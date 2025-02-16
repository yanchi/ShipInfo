import mysql.connector # type: ignore
from scrape_operation_details import scrape_data  # スクレイピング処理を呼び出し
from datetime import datetime

# MySQLデータベース接続設定
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'ship_info',
}

def save_kametoku_info():
    # スクレイピング処理を実行
    print("スクレイピングを実行中...")
    kametoku_data = scrape_data()
    print("スクレイピングが完了しました。")

    # データベース接続
    connection = mysql.connector.connect(**DB_CONFIG)

    try:
        for entry in kametoku_data:
            # company_idを取得（マルエーフェリーのID）
            with connection.cursor(buffered=True) as cursor:
                company_name = "マリックスライン"
                cursor.execute("SELECT id FROM companies WHERE name = %s", (company_name,))
                company_id_result = cursor.fetchone()
                company_id = company_id_result[0] if company_id_result else None

            if not company_id:
                raise Exception(f"Company '{company_name}' not found in the database.")

            # entryにデータが有る間、以下の処理を繰り返す
            with connection.cursor(buffered=True) as cursor:
                # routesテーブルからroute_idを取得
                route_name = entry['方向']
                cursor.execute(
                    "SELECT id FROM routes WHERE direction = %s AND company_id = %s",
                    (route_name, company_id)
                )
                route_id_result = cursor.fetchone()
                route_id = route_id_result[0] if route_id_result else None

                if not route_id:
                    raise Exception(f"Route '{route_name}' not found for company ID {company_id}.")

                # operationsテーブルにデータを追加
                cursor.execute(
                    """
                    INSERT INTO operations (
                        route_id, operation_date, status, status_text, arrival_time, departure_time, memo, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at), status = VALUES(status), status_text = VALUES(status_text)
                    """,
                    (
                        route_id,
                        datetime.strptime(f"{datetime.now().year}年" + entry["運航日"], "%Y年%m月%d日").strftime("%Y-%m-%d"),
                        None,
                        entry["状況詳細"],
                        f"{datetime.strptime(entry['運航日'], '%m月%d日').strftime('%Y-%m-%d')} {entry['到着時刻']}:00" if entry["到着時刻"] else None,
                        f"{datetime.strptime(entry['運航日'], '%m月%d日').strftime('%Y-%m-%d')} {entry['出発時刻']}:00" if entry["出発時刻"] else None,
                        entry["備考"],
                        datetime.now(),
                        datetime.now()
                    )
                )

        # コミットして保存
        connection.commit()
        print("データが正常に保存されました。")

    except mysql.connector.Error as err:
        print(f"エラー: {err}")
        connection.rollback()

    finally:
        connection.close()

if __name__ == "__main__":
    save_kametoku_info()
