import requests
import mysql.connector
from datetime import date, datetime
import os
from bs4 import BeautifulSoup

# MySQLデータベース接続設定
DB_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': os.getenv("MYSQL_DATABASE"),
}

# 検索条件をリストとして定義
today = date.today().strftime("%Y年%m月%d日")

search_conditions = [
    {
        "startDate": today,  # 乗船日
        "startPort": "78",  # 乗船港ID
        "endPort": "83"     # 下船港ID
    },
    {
        "startDate": today,  # 乗船日
        "startPort": "78",  # 乗船港ID
        "endPort": "50"     # 下船港ID
    }
]

# ベースURL
url = "https://www.aline-ferry.com/search/"
results = []

def fetch_and_save_data():
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

    # データベース接続
    connection = mysql.connector.connect(**DB_CONFIG)
    try:
        cursor = connection.cursor(buffered=True)

        for result in results:
            print(result)
            # company_idを取得
            company_name = "A'LINE"
            cursor.execute("SELECT id FROM companies WHERE name = %s", (company_name,))
            company_id_result = cursor.fetchone()
            company_id = company_id_result[0] if company_id_result else None

            if not company_id:
                print(f"Error: Company '{company_name}' not found.")
                continue

            # route_idを取得
            route_name = "上り" if result.get("下船港") == "鹿児島" else "下り"
            cursor.execute("SELECT id FROM routes WHERE direction = %s AND company_id = %s", (route_name, company_id))
            route_id_result = cursor.fetchone()
            route_id = route_id_result[0] if route_id_result else None

            if not route_id:
                print(f"Error: Route '{route_name}' not found for company ID {company_id}.")
                continue

            # operationsテーブルにデータを追加
            try:
                # 日本語の日付を正しいフォーマットに変換
                operation_date = result["乗船日"].split('(')[0]  # 曜日を削除
                operation_date = datetime.strptime(operation_date, "%Y年%m月%d日").strftime("%Y-%m-%d")

                # "Class" と "Text" を文字列型に変換
                status = ", ".join(result.get("Class", []))  # リストをカンマ区切りの文字列に変換
                status_text = str(result.get("Text", ""))    # 値を文字列に変換

                # 下船日時と乗船日時を正しいフォーマットに変換
                arrival_time = result.get("下船日時")
                if arrival_time:
                    arrival_time = datetime.strptime(arrival_time, "%Y年%m月%d日 %H:%M").strftime("%Y-%m-%d %H:%M:%S")

                departure_time = result.get("乗船日時")
                if departure_time:
                    departure_time = datetime.strptime(departure_time, "%Y年%m月%d日 %H:%M").strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute("""
                    INSERT INTO operations (
                        route_id, operation_date, status, status_text, arrival_time, departure_time, memo, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status), status_text = VALUES(status_text)
                """, (
                    route_id,
                    operation_date,
                    status,
                    status_text,
                    arrival_time,
                    departure_time,
                    None,
                    datetime.now(),
                    datetime.now()
                ))
            except Exception as e:
                print(f"Error inserting operation: {e}")

        connection.commit()
        print("データが正常に保存されました。")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    fetch_and_save_data()
