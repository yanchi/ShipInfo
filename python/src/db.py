import json
import mysql.connector  # type: ignore
import os
from contextlib import contextmanager


def get_db_config():
    required = {"MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"}
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"必須の環境変数が設定されていません: {', '.join(missing)}")
    return {
        'host': os.getenv("MYSQL_HOST"),
        'user': os.getenv("MYSQL_USER"),
        'password': os.getenv("MYSQL_PASSWORD"),
        'database': os.getenv("MYSQL_DATABASE"),
    }


@contextmanager
def get_connection():
    connection = mysql.connector.connect(**get_db_config())
    try:
        yield connection
        connection.commit()
    except Exception as err:
        connection.rollback()
        raise err
    finally:
        connection.close()


def get_company_id(cursor, company_name):
    cursor.execute("SELECT id FROM companies WHERE name = %s", (company_name,))
    result = cursor.fetchone()
    return result[0] if result else None


def get_route_id(cursor, direction, company_id):
    cursor.execute(
        "SELECT id FROM routes WHERE direction = %s AND company_id = %s",
        (direction, company_id)
    )
    result = cursor.fetchone()
    return result[0] if result else None


def upsert_operation(cursor, route_id, operation_date, status, status_text,
                     arrival_time, departure_time, memo, now):
    if isinstance(status, list):
        status = json.dumps(status, ensure_ascii=False)
    if isinstance(status_text, list):
        status_text = json.dumps(status_text, ensure_ascii=False)
    cursor.execute("""
        INSERT INTO operations (
            route_id, operation_date, status, status_text, arrival_time, departure_time, memo, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE status = VALUES(status), status_text = VALUES(status_text), updated_at = VALUES(updated_at)
    """, (route_id, operation_date, status, status_text, arrival_time, departure_time, memo, now, now))
