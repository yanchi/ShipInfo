import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore

def get_latest_status_urls():
    url = "https://marixline.com/service/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        latest_status_section = soup.select_one("section.section__latest_status")
        if latest_status_section:
            return [link["href"] for link in latest_status_section.select("a.status_single")]
    return []

if __name__ == "__main__":
    urls = get_latest_status_urls()
    print(urls)
