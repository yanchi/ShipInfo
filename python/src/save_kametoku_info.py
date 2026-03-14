import logging
from scrape_operation_details import scrape_data

_STATUS_CLASS_MAP = {
    "通常運航": "normal",
    "欠航": "cancelled",
    "条件付運航": "tag-conditionally",
    "遅延": "delayed",
}
from datetime import datetime
from db import get_connection, get_company_id, get_route_id, upsert_operation

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def _resolve_year(year, month):
    """現在月より6ヶ月以上先の月は前年と判断して返す。"""
    now = datetime.now()
    return year - 1 if month - now.month > 6 else year


def _parse_operation_date(year, date_str):
    """'MM月DD日' を '%Y-%m-%d' に変換。年をまたぐ場合を考慮する。"""
    dt = datetime.strptime(f"{year}年{date_str}", "%Y年%m月%d日")
    dt = dt.replace(year=_resolve_year(year, dt.month))
    return dt.strftime("%Y-%m-%d")


def _parse_time(year, date_str, time_str):
    if not time_str:
        return None
    dt = datetime.strptime(f"{year}年{date_str}", "%Y年%m月%d日")
    dt = dt.replace(year=_resolve_year(year, dt.month))
    return f"{dt.strftime('%Y-%m-%d')} {time_str}:00"


def save_kametoku_info():
    logging.info("スクレイピングを実行中...")
    kametoku_data = scrape_data()
    logging.info("スクレイピングが完了しました。")

    company_name = "マリックスライン"
    now = datetime.now()
    year = now.year

    with get_connection() as connection:
        with connection.cursor(buffered=True) as cursor:
            company_id = get_company_id(cursor, company_name)
            if not company_id:
                raise ValueError(f"Company '{company_name}' not found.")

            for entry in kametoku_data:
                route_id = get_route_id(cursor, entry['方向'], company_id)
                if not route_id:
                    logging.error(f"Route '{entry['方向']}' not found for company ID {company_id}.")
                    continue

                try:
                    operation_date = _parse_operation_date(year, entry["運航日"])
                    arrival_time = _parse_time(year, entry["運航日"], entry["到着時刻"])
                    departure_time = _parse_time(year, entry["運航日"], entry["出発時刻"])

                    status_texts = entry["状況詳細"]
                    status_classes = [_STATUS_CLASS_MAP.get(t, "normal") for t in status_texts]
                    upsert_operation(
                        cursor, route_id, operation_date,
                        status_classes, status_texts,
                        arrival_time, departure_time, entry["備考"], now
                    )
                except Exception as e:
                    logging.error(f"Error inserting operation: {e}")

    logging.info("データが正常に保存されました。")


if __name__ == "__main__":
    save_kametoku_info()
