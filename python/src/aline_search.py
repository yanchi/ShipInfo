import requests
from bs4 import BeautifulSoup

# 検索条件をリストとして定義
search_conditions = [
    {
        "startDate": "2025年02月18日",  # 乗船日
        "startPort": "78",  # 乗船港ID
        "endPort": "83"     # 下船港ID
    },
    {
        "startDate": "2025年02月18日",  # 乗船日
        "startPort": "78",  # 乗船港ID
        "endPort": "50"     # 下船港ID
    }
]

# ベースURL
url = "https://www.aline-ferry.com/search/"
results = []

# 各条件に対してリクエストを送信
for data in search_conditions:
    response = requests.post(url + "result.php", data=data)

    # 検索結果が取得できた場合
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # 乗船日、乗船港、下船港の取得
        result_box = soup.find('div', class_='result-box')
        if result_box:
            ship_date = result_box.find('dd').text.strip()  # 乗船日
            ports = result_box.find_all('dd')
            start_port = ports[1].text.strip()  # 乗船港
            end_port = ports[2].text.strip()  # 下船港

        # テーブルデータの取得
        table_rows = soup.select('table.s-result tbody tr')
        for row in table_rows:
            cols = row.find_all('td')
            if not cols or len(cols) < 2:
                continue  # cols が存在しない、または列が不足している場合スキップ

            # フェリー名（cols[1].find('a')が存在しない場合スキップ）
            ferry_name_tag = cols[1].find('a')
            if not ferry_name_tag:
                continue  # フェリー名が存在しない場合スキップ
            ferry_name = ferry_name_tag.get_text(strip=True)

            # 詳細ページへのリンク
            detail_link_tag = cols[0].find('a')
            if not detail_link_tag:
                continue  # 詳細ページリンクが存在しない場合スキップ
            detail_link = url + detail_link_tag['href']

            # 詳細ページにアクセスしてtag-listを取得
            detail_response = requests.get(detail_link)
            if detail_response.status_code == 200:
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

                # 該当のtag-list内のspanタグを取得
                tag_list_data = []
                status_boxes = detail_soup.find_all('div', class_='status-box')
                for box in status_boxes:
                    ferry_name_tag_in_box = box.find('div', class_='ferry-name')
                    if ferry_name_tag_in_box and ferry_name in ferry_name_tag_in_box.text:
                        tag_list = box.find('div', class_='tag-list')
                        if tag_list:
                            spans = tag_list.find_all('span')
                            for span in spans:
                                tag_list_data.append({
                                    'class': span.get('class', []),  # spanタグのクラス名を取得
                                    'text': span.text.strip()        # spanタグのテキストを取得
                                })

                # 結果を辞書に追加
                for tag in tag_list_data:
                    results.append({
                        '乗船日': ship_date,
                        '乗船港': start_port,
                        '下船港': end_port,
                        '乗船日時': cols[2].text.strip(),  # 乗船日時
                        '下船日時': cols[3].text.strip(),  # 下船日時
                        'Class': tag['class'],
                        'Text': tag['text']
                    })
    else:
        print(f"リクエスト失敗: {response.status_code} 条件: {data}")

# 結果を表示
for result in results:
    print(result)
