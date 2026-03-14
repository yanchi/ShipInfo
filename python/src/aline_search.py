import logging
import requests
from datetime import date, datetime
from bs4 import BeautifulSoup
from db import get_connection, get_company_id, get_route_id, upsert_operation

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

BASE_URL = "https://www.aline-ferry.com/search/"

# A'LINE フェリー 検索用ポートコード（サイト内部ID）
_PORT_KAKEROMA = "78"   # 加計呂麻島（出発港）
_PORT_KAGOSHIMA = "83"  # 鹿児島
_PORT_NAHA = "50"       # 那覇


def _parse_operation_date(date_str):
    """'YYYY年MM月DD日(曜日)' を '%Y-%m-%d' に変換。"""
    date_str = date_str.split('(')[0]
    return datetime.strptime(date_str, "%Y年%m月%d日").strftime("%Y-%m-%d")


def _parse_datetime(dt_str):
    if not dt_str:
        return None
    dt = datetime.strptime(dt_str, "%Y年%m月%d日 %H:%M")
    current_year = date.today().year
    if not (current_year - 1 <= dt.year <= current_year + 2):
        logging.warning(f"不正な年のdatetimeをスキップします: {dt_str} (year={dt.year})")
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def fetch_results():
    today = date.today().strftime("%Y年%m月%d日")
    search_conditions = [
        {"startDate": today, "startPort": _PORT_KAKEROMA, "endPort": _PORT_KAGOSHIMA},
        {"startDate": today, "startPort": _PORT_KAKEROMA, "endPort": _PORT_NAHA},
    ]
    results = []
    for data in search_conditions:
        try:
            response = requests.post(BASE_URL + "result.php", data=data, timeout=10)
        except requests.RequestException as e:
            logging.error(f"HTTP リクエストに失敗しました: {e} 条件: {data}")
            continue
        if response.status_code != 200:
            logging.error(f"リクエスト失敗: {response.status_code} 条件: {data}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        result_box = soup.find('div', class_='result-box')
        if not result_box:
            continue

        ports = result_box.find_all('dd')
        if len(ports) < 3:
            logging.warning(f"result-box の dd 要素が不足しています (got {len(ports)}): {data}")
            continue
        ship_date = ports[0].text.strip()
        start_port = ports[1].text.strip()
        end_port = ports[2].text.strip()

        for row in soup.select('table.s-result tbody tr'):
            cols = row.find_all('td')
            if not cols or len(cols) < 4:
                continue

            ferry_name_tag = cols[1].find('a')
            detail_link_tag = cols[0].find('a')
            if not ferry_name_tag or not detail_link_tag:
                continue

            ferry_name = ferry_name_tag.get_text(strip=True)
            detail_link = BASE_URL + detail_link_tag['href']

            try:
                detail_response = requests.get(detail_link, timeout=10)
            except requests.RequestException as e:
                logging.error(f"詳細ページの取得に失敗しました: {e} URL: {detail_link}")
                continue
            if detail_response.status_code != 200:
                continue

            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
            for box in detail_soup.find_all('div', class_='status-box'):
                ferry_name_tag_in_box = box.find('div', class_='ferry-name')
                if not (ferry_name_tag_in_box and ferry_name in ferry_name_tag_in_box.text):
                    continue
                tag_list = box.find('div', class_='tag-list')
                if not tag_list:
                    continue
                spans = tag_list.find_all('span')
                if not spans:
                    continue
                results.append({
                    '乗船日': ship_date,
                    '乗船港': start_port,
                    '下船港': end_port,
                    '乗船日時': cols[2].text.strip(),
                    '下船日時': cols[3].text.strip(),
                    'Classes': [" ".join(span.get('class', [])) for span in spans],
                    'Texts': [span.text.strip() for span in spans],
                })
    return results


def fetch_and_save_data():
    results = fetch_results()

    company_name = "A'LINE"
    now = datetime.now()

    with get_connection() as connection:
        with connection.cursor(buffered=True) as cursor:
            company_id = get_company_id(cursor, company_name)
            if not company_id:
                raise ValueError(f"Company '{company_name}' not found.")

            for result in results:
                end_port = result.get("下船港", "")
                if end_port == "鹿児島":
                    direction = "上り"
                elif end_port == "那覇":
                    direction = "下り"
                else:
                    logging.warning(f"不明な下船港のため方向を特定できません: {end_port}")
                    continue
                route_id = get_route_id(cursor, direction, company_id)
                if not route_id:
                    logging.error(f"Route '{direction}' not found for company ID {company_id}.")
                    continue

                try:
                    operation_date = _parse_operation_date(result["乗船日"])
                    arrival_time = _parse_datetime(result.get("下船日時"))
                    departure_time = _parse_datetime(result.get("乗船日時"))

                    upsert_operation(
                        cursor, route_id, operation_date,
                        result['Classes'], result['Texts'],
                        arrival_time, departure_time, None, now
                    )
                except Exception as e:
                    logging.error(f"Error inserting operation: {e}", exc_info=True)

    logging.info("データが正常に保存されました。")


if __name__ == "__main__":
    fetch_and_save_data()
