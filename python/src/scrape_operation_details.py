import logging
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from get_latest_status_urls import get_latest_status_urls  # URL取得用の関数をインポート

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# 亀徳港の情報を抽出する関数（解析処理）
def get_kametoku_info(soup, direction):
    services = soup.find_all("div", class_="single")
    kametoku_info = []

    for service in services:
        port_name_tag = service.find("span", class_="port_name")
        if not (port_name_tag and "亀徳港" in port_name_tag.get_text(strip=True)):
            continue

        # 各データを一度だけ抽出（要素が存在しない場合はスキップ）
        date_tag = service.select_one("div.departure span.date")
        if not date_tag:
            logging.warning("div.departure span.date が見つかりません。スキップします。")
            continue
        departure_date = date_tag.get_text(strip=True)

        status_detail = [div.get_text(strip=True) for div in service.select("div.status")]

        if not status_detail:
            logging.warning("div.status が見つかりません。スキップします。")
            continue

        # 「―」のみの場合は寄港なしのためスキップ
        if status_detail == ["―"]:
            continue

        departure_time_tag = service.select_one("div.departure span.time")
        arrival_time_tag = service.select_one("div.entry span.time")
        departure_time = departure_time_tag.get_text(strip=True) if departure_time_tag else None
        arrival_time = arrival_time_tag.get_text(strip=True) if arrival_time_tag else None

        exp = service.select_one("div.exp")
        memo = exp.get_text(strip=True) if exp else "N/A"

        kametoku_info.append({
            "運航日": departure_date,
            "方向": direction,
            "状況詳細": status_detail,
            "出発時刻": departure_time,
            "到着時刻": arrival_time,
            "備考": memo
        })

    return kametoku_info

# サイトからHTMLデータを取得
def fetch_html(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # ステータスコードがエラーの場合、例外を発生
    return response.text

# h1タグから方向を取得
def parse_direction_from_h1(soup):
    h1_tag = soup.find("h1")
    if h1_tag:
        h1_text = h1_tag.get_text(strip=True)
        if "下り便" in h1_text:
            return "下り"
        if "上り便" in h1_text:
            return "上り"
    return "N/A"

# 全スクレイピング処理の実行
def scrape_data():
    urls = get_latest_status_urls()

    all_kametoku_data = []
    for url in urls:
        logging.info(f"Fetching data from: {url}")
        try:
            html_content = fetch_html(url)
            soup = BeautifulSoup(html_content, "html.parser")
            direction = parse_direction_from_h1(soup)
            if direction == "N/A":
                logging.warning(f"h1 から方向を特定できませんでした。スキップします: {url}")
                continue
            kametoku_data = get_kametoku_info(soup, direction)

            if kametoku_data:
                all_kametoku_data.extend(kametoku_data)
            else:
                logging.warning("亀徳港のデータは見つかりませんでした。")
        except requests.RequestException as e:
            logging.error(f"HTTP エラーが発生しました: {e}")
        except Exception as e:
            logging.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
    return all_kametoku_data
