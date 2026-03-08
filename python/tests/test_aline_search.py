"""aline_search の日付パースロジックのテスト"""
import pytest
from aline_search import _parse_datetime, _parse_operation_date


# ──────────────────────────────────────────
# _parse_operation_date
# ──────────────────────────────────────────

class TestParseOperationDate:
    def test_normal_date(self):
        assert _parse_operation_date("2025年2月14日(金)") == "2025-02-14"

    def test_strips_day_of_week(self):
        """曜日部分が除去されて正しく変換される"""
        assert _parse_operation_date("2025年12月31日(水)") == "2025-12-31"

    def test_without_day_of_week(self):
        """曜日なしでも動作する"""
        assert _parse_operation_date("2025年3月1日") == "2025-03-01"

    def test_single_digit_month_and_day(self):
        assert _parse_operation_date("2025年1月5日(月)") == "2025-01-05"


# ──────────────────────────────────────────
# _parse_datetime
# ──────────────────────────────────────────

class TestParseDatetime:
    def test_normal_datetime(self):
        assert _parse_datetime("2025年2月14日 10:30") == "2025-02-14 10:30:00"

    def test_returns_none_when_empty_string(self):
        assert _parse_datetime("") is None

    def test_returns_none_when_none(self):
        assert _parse_datetime(None) is None

    def test_midnight(self):
        assert _parse_datetime("2025年12月31日 00:00") == "2025-12-31 00:00:00"

    def test_end_of_day(self):
        assert _parse_datetime("2025年1月1日 23:59") == "2025-01-01 23:59:00"
