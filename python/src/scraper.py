import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore

def scrape_example():
    url = "https://example.com"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        print("ページタイトル:", soup.title.string)
    else:
        print("ページ取得失敗:", response.status_code)

if __name__ == "__main__":
    scrape_example()
