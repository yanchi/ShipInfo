import logging
from datetime import datetime

from db import get_connection, get_company_id, get_route_id, upsert_operation
from scrape_operation_details import scrape_data

_STATUS_CLASS_MAP = {
    "通常運航": "normal",
    "欠航": "cancelled",
    "条件付運航": "tag-conditionally",
    "遅延": "delayed",
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def _resolve_year(year, month):
    """年をまたぐ場合の年を補正する。
    スクレイプ月と現在月の差が 6 ヶ月超の場合、年境界をまたいでいると判断する。
    例: 現在 1月・スクレイプ 12月 → 差 +11 → 前年12月 (year - 1)
    例: 現在 12月・スクレイプ 1月 → 差 -11 → 翌年1月 (year + 1)
    """
    now = datetime.now()
    diff = month - now.month
    if diff > 6:
        return year - 1
    if diff < -6:
        return year + 1
    return year


def _parse_date_object(year, date_str):
    """'MM月DD日' を datetime オブジェクトに変換。年またぎを補正する。"""
    dt = datetime.strptime(f"{year}年{date_str}", "%Y年%m月%d日")
    return dt.replace(year=_resolve_year(year, dt.month))


def _parse_operation_date(year, date_str):
    """'MM月DD日' を '%Y-%m-%d' に変換。年をまたぐ場合を考慮する。"""
    return _parse_date_object(year, date_str).strftime("%Y-%m-%d")


def _parse_time(year, date_str, time_str):
    """'HH:MM' 形式の time_str を '%Y-%m-%d %H:%M:%S' に変換。None または空文字は None を返す。"""
    if not time_str:
        return None
    dt = _parse_date_object(year, date_str)
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
                    status_classes = []
                    for t in status_texts:
                        css_class = _STATUS_CLASS_MAP.get(t)
                        if css_class is None:
                            logging.warning(f"未知のステータス文字列: '{t}' → 'normal' にフォールバック")
                            css_class = "normal"
                        status_classes.append(css_class)
                    upsert_operation(
                        cursor, route_id, operation_date,
                        status_classes, status_texts,
                        arrival_time, departure_time, entry["備考"], now
                    )
                except Exception as e:
                    logging.error(f"Error inserting operation: {e}", exc_info=True)

    logging.info("データが正常に保存されました。")


if __name__ == "__main__":
    save_kametoku_info()
