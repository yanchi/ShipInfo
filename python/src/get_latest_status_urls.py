import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
import os

# 環境変数から値を取得
MARIXLINE_SERVICE_URL = os.getenv("MARIXLINE_SERVICE_URL")

if not MARIXLINE_SERVICE_URL:
    raise ValueError("MARIXLINE_SERVICE_URL is not defined in the .env file.")


def get_latest_status_urls():
    url = MARIXLINE_SERVICE_URL
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # ステータスコードがエラーの場合、例外を発生
        soup = BeautifulSoup(response.text, "html.parser")
        latest_status_section = soup.select_one("section.section__latest_status")
        if latest_status_section:
            return [link["href"] for link in latest_status_section.select("a.status_single")]
        else:
            print("Error: No latest status section found.")
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    return []

if __name__ == "__main__":
    urls = get_latest_status_urls()
    print(urls)
