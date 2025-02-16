import mysql.connector # type: ignore
from scrape_operation_details import scrape_data  # スクレイピング処理を呼び出し
from datetime import datetime
import os

# MySQLデータベース接続設定
DB_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': os.getenv("MYSQL_DATABASE"),
}

def save_kametoku_info():
    print("スクレイピングを実行中...")
    kametoku_data = scrape_data()
    print("スクレイピングが完了しました。")

    connection = mysql.connector.connect(**DB_CONFIG)
    try:
        cursor = connection.cursor(buffered=True)

        for entry in kametoku_data:
            # company_idを取得
            company_name = "マリックスライン"
            cursor.execute("SELECT id FROM companies WHERE name = %s", (company_name,))
            company_id_result = cursor.fetchone()
            company_id = company_id_result[0] if company_id_result else None

            if not company_id:
                print(f"Error: Company '{company_name}' not found.")
                continue

            # route_idを取得
            route_name = entry['方向']
            cursor.execute("SELECT id FROM routes WHERE direction = %s AND company_id = %s", (route_name, company_id))
            route_id_result = cursor.fetchone()
            route_id = route_id_result[0] if route_id_result else None

            if not route_id:
                print(f"Error: Route '{route_name}' not found for company ID {company_id}.")
                continue

            # operationsテーブルにデータを追加
            try:
                cursor.execute("""
                    INSERT INTO operations (
                        route_id, operation_date, status, status_text, arrival_time, departure_time, memo, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at), status = VALUES(status), status_text = VALUES(status_text)
                """, (
                    route_id,
                    datetime.strptime(f"{datetime.now().year}年" + entry["運航日"], "%Y年%m月%d日").strftime("%Y-%m-%d"),
                    None,
                    entry["状況詳細"],
                    f"{datetime.strptime(entry['運航日'], '%m月%d日').strftime('%Y-%m-%d')} {entry['到着時刻']}:00" if entry["到着時刻"] else None,
                    f"{datetime.strptime(entry['運航日'], '%m月%d日').strftime('%Y-%m-%d')} {entry['出発時刻']}:00" if entry["出発時刻"] else None,
                    entry["備考"],
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
    save_kametoku_info()
