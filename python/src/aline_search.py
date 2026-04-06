import logging
import re
import requests
from datetime import date, datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from db import get_connection, get_company_id, get_route_id, upsert_operation
from notifier import send_alert

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

BASE_URL = "https://www.aline-ferry.com/search/"

_EXCERPT_STATUS_CLASS_MAP = {
    "通常運航": "tag-normal",
    "運航遅延": "tag-delay",
    "欠航": "tag-cancel",
    "条件付運航": "tag-conditionally",
    "スケジュール変更": "tag-schedule-change",
}

# A'LINE フェリー 検索用ポートコード（サイト内部ID）
_PORT_KAMETOKU = "78"   # 亀徳
_PORT_NAHA = "83"       # 那覇
_PORT_KAGOSHIMA = "50"  # 鹿児島

# 亀徳港からの所要時間（スケジュール基準の固定値）
# 下り（亀徳 → 那覇）: 約 9 時間 20 分
# 上り（亀徳 → 鹿児島）: 約 15 時間 30 分
_TRAVEL_DELTA_KUDARI = timedelta(hours=9, minutes=20)
_TRAVEL_DELTA_NOBORI = timedelta(hours=15, minutes=30)


def _extract_no_port_notice(text):
    """status-detail テキストから「※〜には寄港致しません」の行を抽出する。なければ None を返す。"""
    match = re.search(r'※[^。\n]*には寄港致しません[。]?', text)
    return match.group(0) if match else None


def _extract_direction_status(excerpt, direction):
    """excerptから方向別の1行を抽出し、(classes, texts, line) を返す。マッチしなければ (None, None, None) を返す。"""
    if not excerpt:
        return None, None, None
    for line in excerpt.split('\n'):
        if f"{direction}便" in line and "…" in line:
            status_text = line.split("…", 1)[1].strip()
            status_class = _EXCERPT_STATUS_CLASS_MAP.get(status_text)
            if status_class:
                return [status_class], [status_text], line
    return None, None, None


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
        {"startDate": today, "startPort": _PORT_KAMETOKU, "endPort": _PORT_KAGOSHIMA},
        {"startDate": today, "startPort": _PORT_KAMETOKU, "endPort": _PORT_NAHA},
    ]
    results = []
    detail_cache = {}
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
            logging.info(f"result-box が見つかりませんでした（便なし or サイト構造変更の可能性）: {data}")
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
            detail_link = urljoin(BASE_URL, detail_link_tag['href'])

            if detail_link not in detail_cache:
                try:
                    detail_response = requests.get(detail_link, timeout=10)
                except requests.RequestException as e:
                    logging.error(f"詳細ページの取得に失敗しました: {e} URL: {detail_link}")
                    continue
                if detail_response.status_code != 200:
                    logging.error(f"詳細ページのリクエスト失敗: {detail_response.status_code} URL: {detail_link}")
                    continue
                detail_cache[detail_link] = BeautifulSoup(detail_response.text, 'html.parser')

            detail_soup = detail_cache[detail_link]
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
                excerpt_tag = box.find('div', class_='situation-excerpt')
                excerpt = excerpt_tag.get_text(separator='\n', strip=True) if excerpt_tag else None

                # スケジュール変更のとき詳細ページから status-detail を取得
                has_sche = any('tag-sche' in ' '.join(span.get('class', [])) for span in spans)
                if has_sche:
                    status_box_link = box.find('a')
                    status_detail_url = status_box_link['href'] if status_box_link else None
                    if status_detail_url:
                        try:
                            if status_detail_url not in detail_cache:
                                r = requests.get(status_detail_url, timeout=10)
                                r.raise_for_status()
                                detail_cache[status_detail_url] = BeautifulSoup(r.text, 'html.parser')
                            status_detail_div = detail_cache[status_detail_url].find('div', class_='status-detail')
                            if status_detail_div:
                                detail_text = status_detail_div.get_text(separator='\n', strip=True)
                                notice = _extract_no_port_notice(detail_text)
                                if notice:
                                    excerpt = notice
                        except requests.RequestException as e:
                            logging.warning(f"スケジュール変更詳細ページの取得に失敗しました: {e} URL: {status_detail_url}")

                results.append({
                    '乗船日': ship_date,
                    '乗船港': start_port,
                    '下船港': end_port,
                    '乗船日時': cols[2].text.strip(),
                    '下船日時': cols[3].text.strip(),
                    'Classes': [" ".join(span.get('class', [])) for span in spans],
                    'Texts': [span.text.strip() for span in spans],
                    'Excerpt': excerpt,
                })
    return results


def fetch_and_save_data():
    results = fetch_results()

    if not results:
        logging.info("スクレイピング結果なし、保存をスキップします")
        return

    company_name = "A'LINE"
    now = datetime.now()

    abnormal_entries = []

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
                    departure_time = _parse_datetime(result.get("乗船日時"))
                    if departure_time:
                        delta = _TRAVEL_DELTA_KUDARI if direction == "下り" else _TRAVEL_DELTA_NOBORI
                        arrival_time = (datetime.strptime(departure_time, "%Y-%m-%d %H:%M:%S") + delta).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        arrival_time = None

                    dir_classes, dir_texts, dir_line = _extract_direction_status(result.get('Excerpt'), direction)
                    if dir_classes:
                        classes = dir_classes
                        texts = dir_texts
                        memo = dir_line
                    else:
                        excerpt = result.get('Excerpt') or ''
                        has_direction_info = '上り便' in excerpt or '下り便' in excerpt
                        if has_direction_info:
                            logging.warning(f"方向別excerptが見つかりませんでした: direction={direction}, excerpt={excerpt}")
                        classes = result['Classes']
                        texts = result['Texts']
                        memo = excerpt or None

                    if any(c and "tag-normal" not in c for c in classes):
                        abnormal_entries.append({
                            "運航日": operation_date,
                            "方向": direction,
                            "状況詳細": texts,
                            "備考": memo,
                            "会社名": company_name,
                        })

                    upsert_operation(
                        cursor, route_id, operation_date,
                        classes, texts,
                        arrival_time, departure_time, memo, now
                    )
                except Exception as e:
                    logging.error(f"Error inserting operation: {e}", exc_info=True)

    logging.info("データが正常に保存されました。")
    send_alert(abnormal_entries)


if __name__ == "__main__":
    fetch_and_save_data()
