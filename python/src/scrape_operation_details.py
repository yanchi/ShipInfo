import requests
from bs4 import BeautifulSoup
from get_latest_status_urls import get_latest_status_urls  # URL取得用の関数をインポート

# 亀徳港の情報を抽出する関数（解析処理）
def get_kametoku_info(soup, direction):
    # "single" を含むクラスのサービス情報を取得
    services = soup.find_all("div", class_="single")
    kametoku_info = []

    for service in services:
        # 港名の要素を取得
        port_name_tag = service.find("span", class_="port_name")
        if port_name_tag and "亀徳港" in port_name_tag.get_text(strip=True):
            # 必要な情報を取得
            departure_date = service.find("div", class_="departure").find("span", class_="date").get_text(strip=True)
            status_detail = service.find("div", class_="status").get_text(strip=True)
            departure_time = service.find("div", class_="departure").find("span", class_="time").get_text(strip=True)
            arrival_time = service.find("div", class_="entry").find("span", class_="time").get_text(strip=True)
            memo = service.find("div", class_="exp").get_text(strip=True) if service.find("div", class_="exp") else "N/A"

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
    response = requests.get(url)
    response.raise_for_status()  # ステータスコードがエラーの場合、例外を発生
    return response.text

# h1タグから方向を取得
def parse_direction_from_h1(soup):
    h1_tag = soup.find("h1")
    if h1_tag:
        h1_text = h1_tag.get_text(strip=True)
        # 方向を抽出（例: "下り便" or "上り便"）
        return "下り" if "下り便" in h1_text else "上り"
    return "N/A"

if __name__ == "__main__":
    # 最新の運行状況URLを取得
    urls = get_latest_status_urls()

    for url in urls:
        print(f"Fetching data from: {url}")
        try:
            html_content = fetch_html(url)  # サイトからHTMLを取得
            soup = BeautifulSoup(html_content, "html.parser")  # HTMLを解析

            # h1タグから方向を解析
            direction = parse_direction_from_h1(soup)

            # 亀徳港のデータを解析
            kametoku_data = get_kametoku_info(soup, direction)

            if kametoku_data:
                print("亀徳港のデータ:")
                for entry in kametoku_data:
                    print(entry)
            else:
                print("亀徳港のデータは見つかりませんでした。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
