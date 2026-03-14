"""非通常運航ステータス検出時のメール通知モジュール"""
import logging
import os
import smtplib
from email.mime.text import MIMEText


def send_alert(abnormal_entries: list[dict]) -> None:
    """非通常運航のエントリが1件以上ある場合にメールを送信する。

    Args:
        abnormal_entries: 通常運航以外のエントリのリスト。各要素は以下のキーを持つ:
            - 運航日: str
            - 方向: str
            - 状況詳細: list[str]
            - 備考: str
    """
    if not abnormal_entries:
        return

    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port_str = os.environ.get("SMTP_PORT") or "587"
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    notify_from = os.environ.get("NOTIFY_FROM", smtp_user)
    notify_to = os.environ.get("NOTIFY_TO", "")

    if not smtp_host or not notify_to:
        logging.warning("SMTP_HOST または NOTIFY_TO が未設定のためメール通知をスキップします。")
        return

    try:
        smtp_port = int(smtp_port_str)
    except ValueError:
        logging.warning(f"SMTP_PORT の値が不正です: '{smtp_port_str}' → 通知をスキップします。")
        return

    subject = f"【ShipInfo】非通常運航ステータスを検出 ({len(abnormal_entries)}件)"
    body = _build_body(abnormal_entries)

    recipients = [addr.strip() for addr in notify_to.split(",") if addr.strip()]
    if not recipients:
        logging.warning("有効な宛先アドレスがないためメール通知をスキップします。")
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = notify_from
    msg["To"] = ", ".join(recipients)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(notify_from, recipients, msg.as_string())
        logging.info(f"メール通知を送信しました: {subject}")
    except Exception as e:
        logging.error(f"メール通知の送信に失敗しました: {e}", exc_info=True)


def _build_body(abnormal_entries: list[dict]) -> str:
    lines = [
        "以下の運航情報で通常運航以外のステータスが検出されました。",
        "",
    ]
    for entry in abnormal_entries:
        statuses = "、".join(entry["状況詳細"])
        lines.append(f"  会社名: {entry.get('会社名', '不明')}")
        lines.append(f"  運航日: {entry['運航日']}")
        lines.append(f"  方向　: {entry['方向']}")
        lines.append(f"  状況　: {statuses}")
        if entry.get("備考") and entry["備考"] != "N/A":
            lines.append(f"  備考　: {entry['備考']}")
        lines.append("")
    return "\n".join(lines)
