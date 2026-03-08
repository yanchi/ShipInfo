"""save_kametoku_info の日付パースロジックのテスト"""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from save_kametoku_info import _parse_operation_date, _parse_time, _resolve_year

# datetime.now() のモックを固定するヘルパー
# save_kametoku_info は `from datetime import datetime` しているため
# モジュール内の datetime クラスをパッチする
PATCH_TARGET = "save_kametoku_info.datetime"


def _mock_now(month: int):
    """指定月を返す datetime.now() モックを返す"""
    m = MagicMock()
    m.now.return_value = MagicMock(month=month)
    m.strptime.side_effect = datetime.strptime  # strptime は本物を使う
    return m


# ──────────────────────────────────────────
# _resolve_year
# ──────────────────────────────────────────

class TestResolveYear:
    def test_same_year_when_month_is_ahead_within_6(self):
        """現在6月 → 8月 (+2) は同年"""
        with patch(PATCH_TARGET, _mock_now(6)):
            assert _resolve_year(2025, 8) == 2025

    def test_same_year_when_month_is_exactly_6_ahead(self):
        """現在6月 → 12月 (+6) は境界値、同年"""
        with patch(PATCH_TARGET, _mock_now(6)):
            assert _resolve_year(2025, 12) == 2025

    def test_previous_year_when_month_is_more_than_6_ahead(self):
        """現在6月 → 1月 (差 = -5, month - now.month = 1-6 = -5 ≤ 6) → 同年。
        現在11月 → 6月 (差 = -5) だと… いや month=6, now.month=11 → 6-11 = -5 ≤ 6 → 同年。
        前年になるのは month - now.month > 6、例: 現在1月(now.month=1)、month=8 → 8-1=7 > 6 → 前年"""
        with patch(PATCH_TARGET, _mock_now(1)):
            assert _resolve_year(2025, 8) == 2024

    def test_same_year_in_december_to_january_transition(self):
        """現在12月 → 翌1月 (差=-11) は同年扱い"""
        with patch(PATCH_TARGET, _mock_now(12)):
            assert _resolve_year(2025, 1) == 2025

    def test_boundary_exact_7_months_ahead_is_previous_year(self):
        """現在1月 → 8月 (差=7 > 6) → 前年"""
        with patch(PATCH_TARGET, _mock_now(1)):
            assert _resolve_year(2026, 8) == 2025


# ──────────────────────────────────────────
# _parse_operation_date
# ──────────────────────────────────────────

class TestParseOperationDate:
    def test_normal_case(self):
        """通常: 現在3月 → '2月14日' は同年"""
        with patch(PATCH_TARGET, _mock_now(3)):
            assert _parse_operation_date(2025, "2月14日") == "2025-02-14"

    def test_year_rollover(self):
        """現在1月 → '8月20日' は前年扱い"""
        with patch(PATCH_TARGET, _mock_now(1)):
            assert _parse_operation_date(2025, "8月20日") == "2024-08-20"

    def test_zero_padded_day(self):
        """1桁日付も正しく変換"""
        with patch(PATCH_TARGET, _mock_now(6)):
            assert _parse_operation_date(2025, "6月5日") == "2025-06-05"


# ──────────────────────────────────────────
# _parse_time
# ──────────────────────────────────────────

class TestParseTime:
    def test_normal_case(self):
        with patch(PATCH_TARGET, _mock_now(3)):
            result = _parse_time(2025, "2月14日", "10:30")
            assert result == "2025-02-14 10:30:00"

    def test_returns_none_when_time_str_is_empty(self):
        with patch(PATCH_TARGET, _mock_now(3)):
            assert _parse_time(2025, "2月14日", "") is None

    def test_returns_none_when_time_str_is_none(self):
        with patch(PATCH_TARGET, _mock_now(3)):
            assert _parse_time(2025, "2月14日", None) is None

    def test_year_rollover_in_time(self):
        """日付がまたぐ場合、時刻でも前年が適用される"""
        with patch(PATCH_TARGET, _mock_now(1)):
            result = _parse_time(2025, "8月20日", "14:00")
            assert result == "2024-08-20 14:00:00"
