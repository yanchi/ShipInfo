"""notifier モジュールのテスト"""
import email
import email.header
import os
from unittest.mock import MagicMock, patch

import pytest

from notifier import _build_body, send_alert

_SAMPLE_ENTRIES = [
    {
        "運航日": "2026-03-14",
        "方向": "下り",
        "状況詳細": ["欠航"],
        "備考": "悪天候のため",
        "会社名": "マリックスライン",
    }
]

_SMTP_ENV = {
    "SMTP_HOST": "smtp.example.com",
    "SMTP_PORT": "587",
    "SMTP_USER": "user@example.com",
    "SMTP_PASSWORD": "pass",
    "NOTIFY_FROM": "user@example.com",
    "NOTIFY_TO": "to@example.com",
}


# ──────────────────────────────────────────
# _build_body
# ──────────────────────────────────────────

class TestBuildBody:
    def test_contains_required_fields(self):
        body = _build_body(_SAMPLE_ENTRIES)
        assert "マリックスライン" in body
        assert "2026-03-14" in body
        assert "下り" in body
        assert "欠航" in body
        assert "悪天候のため" in body

    def test_備考_na_is_omitted(self):
        entries = [{**_SAMPLE_ENTRIES[0], "備考": "N/A"}]
        body = _build_body(entries)
        assert "備考" not in body

    def test_備考_none_is_omitted(self):
        entries = [{**_SAMPLE_ENTRIES[0], "備考": None}]
        body = _build_body(entries)
        assert "備考" not in body

    def test_multiple_entries(self):
        entries = [
            {**_SAMPLE_ENTRIES[0], "運航日": "2026-03-14"},
            {**_SAMPLE_ENTRIES[0], "運航日": "2026-03-15", "状況詳細": ["遅延"]},
        ]
        body = _build_body(entries)
        assert "2026-03-14" in body
        assert "2026-03-15" in body
        assert "遅延" in body


# ──────────────────────────────────────────
# send_alert
# ──────────────────────────────────────────

class TestSendAlert:
    def test_does_nothing_when_entries_empty(self):
        with patch("notifier.smtplib.SMTP") as mock_smtp:
            send_alert([])
        mock_smtp.assert_not_called()

    def test_skips_when_smtp_host_missing(self, caplog):
        env = {**_SMTP_ENV, "SMTP_HOST": ""}
        with patch.dict(os.environ, env, clear=False):
            with patch("notifier.smtplib.SMTP") as mock_smtp:
                send_alert(_SAMPLE_ENTRIES)
        mock_smtp.assert_not_called()
        assert "スキップ" in caplog.text

    def test_skips_when_notify_from_missing(self, caplog):
        env = {**_SMTP_ENV, "NOTIFY_FROM": "", "SMTP_USER": ""}
        with patch.dict(os.environ, env, clear=False):
            with patch("notifier.smtplib.SMTP") as mock_smtp:
                send_alert(_SAMPLE_ENTRIES)
        mock_smtp.assert_not_called()
        assert "スキップ" in caplog.text

    def test_skips_when_notify_to_missing(self, caplog):
        env = {**_SMTP_ENV, "NOTIFY_TO": ""}
        with patch.dict(os.environ, env, clear=False):
            with patch("notifier.smtplib.SMTP") as mock_smtp:
                send_alert(_SAMPLE_ENTRIES)
        mock_smtp.assert_not_called()
        assert "スキップ" in caplog.text

    def test_sends_mail_with_correct_settings(self):
        mock_server = MagicMock()
        with patch.dict(os.environ, _SMTP_ENV, clear=False):
            with patch("notifier.smtplib.SMTP") as mock_smtp:
                mock_smtp.return_value.__enter__.return_value = mock_server
                send_alert(_SAMPLE_ENTRIES)

        mock_smtp.assert_called_once_with("smtp.example.com", 587, timeout=10)
        mock_server.starttls.assert_called_once()
        starttls_kwargs = mock_server.starttls.call_args[1]
        assert "context" in starttls_kwargs
        mock_server.login.assert_called_once_with("user@example.com", "pass")
        mock_server.sendmail.assert_called_once()
        mock_server.ehlo.assert_not_called()

    def test_notify_to_recipients_are_stripped(self):
        mock_server = MagicMock()
        env = {**_SMTP_ENV, "NOTIFY_TO": "a@example.com, b@example.com"}
        with patch.dict(os.environ, env, clear=False):
            with patch("notifier.smtplib.SMTP") as mock_smtp:
                mock_smtp.return_value.__enter__.return_value = mock_server
                send_alert(_SAMPLE_ENTRIES)

        recipients = mock_server.sendmail.call_args[0][1]
        assert recipients == ["a@example.com", "b@example.com"]

    def test_sendmail_contains_subject_with_count(self):
        mock_server = MagicMock()
        with patch.dict(os.environ, _SMTP_ENV, clear=False):
            with patch("notifier.smtplib.SMTP") as mock_smtp:
                mock_smtp.return_value.__enter__.return_value = mock_server
                send_alert(_SAMPLE_ENTRIES)

        args = mock_server.sendmail.call_args
        msg = email.message_from_string(args[0][2])
        subject = email.header.decode_header(msg["Subject"])[0]
        decoded_subject = subject[0].decode(subject[1])
        assert "1件" in decoded_subject

    def test_skips_when_smtp_port_invalid(self, caplog):
        env = {**_SMTP_ENV, "SMTP_PORT": "invalid"}
        with patch.dict(os.environ, env, clear=False):
            with patch("notifier.smtplib.SMTP") as mock_smtp:
                send_alert(_SAMPLE_ENTRIES)
        mock_smtp.assert_not_called()
        assert "スキップ" in caplog.text

    def test_skips_when_notify_to_only_commas(self, caplog):
        env = {**_SMTP_ENV, "NOTIFY_TO": ",, ,"}
        with patch.dict(os.environ, env, clear=False):
            with patch("notifier.smtplib.SMTP") as mock_smtp:
                send_alert(_SAMPLE_ENTRIES)
        mock_smtp.assert_not_called()
        assert "スキップ" in caplog.text

    def test_smtp_error_is_caught_and_logged(self, caplog):
        mock_server = MagicMock()
        mock_server.sendmail.side_effect = Exception("connection error")
        with patch.dict(os.environ, _SMTP_ENV, clear=False):
            with patch("notifier.smtplib.SMTP") as mock_smtp:
                mock_smtp.return_value.__enter__.return_value = mock_server
                send_alert(_SAMPLE_ENTRIES)  # 例外が外に出ないこと

        assert "失敗" in caplog.text
