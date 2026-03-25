"""aline_search の日付パースロジックおよび方向別ステータス抽出のテスト"""
import pytest
from aline_search import _parse_datetime, _parse_operation_date, _extract_direction_status


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


# ──────────────────────────────────────────
# _extract_direction_status
# ──────────────────────────────────────────

class TestExtractDirectionStatus:
    _MIXED_EXCERPT = "3月24日（火）下り便…運航遅延\n3月26日（木）上り便…通常運航"

    def test_matches_kudari(self):
        classes, texts, line = _extract_direction_status(self._MIXED_EXCERPT, "下り")
        assert classes == ["tag-delay"]
        assert texts == ["運航遅延"]
        assert "下り便" in line

    def test_matches_nobori(self):
        classes, texts, line = _extract_direction_status(self._MIXED_EXCERPT, "上り")
        assert classes == ["tag-normal"]
        assert texts == ["通常運航"]
        assert "上り便" in line

    def test_returns_none_when_no_excerpt(self):
        assert _extract_direction_status(None, "上り") == (None, None, None)

    def test_returns_none_when_no_direction_info(self):
        """方向別情報がない単純なテキスト（通常運航時など）"""
        assert _extract_direction_status("通常運航致しております。", "上り") == (None, None, None)

    def test_returns_none_when_unknown_status_text(self):
        """マッピングにないステータステキストはNoneを返す"""
        excerpt = "3月26日（木）上り便…点検中"
        assert _extract_direction_status(excerpt, "上り") == (None, None, None)
