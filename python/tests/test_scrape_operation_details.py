"""scrape_operation_details の HTML パースロジックのテスト"""
import pytest
from bs4 import BeautifulSoup

from scrape_operation_details import get_kametoku_info, parse_direction_from_h1


def _make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


# ──────────────────────────────────────────
# parse_direction_from_h1
# ──────────────────────────────────────────

class TestParseDirectionFromH1:
    def test_returns_kudari_when_h1_contains_kudari_bin(self):
        soup = _make_soup("<h1>鹿児島 → 亀徳港 下り便</h1>")
        assert parse_direction_from_h1(soup) == "下り"

    def test_returns_nobori_when_h1_does_not_contain_kudari_bin(self):
        soup = _make_soup("<h1>亀徳港 → 鹿児島 上り便</h1>")
        assert parse_direction_from_h1(soup) == "上り"

    def test_returns_na_when_no_h1(self):
        soup = _make_soup("<div>見出しなし</div>")
        assert parse_direction_from_h1(soup) == "N/A"

    def test_strips_whitespace(self):
        soup = _make_soup("<h1>  下り便  </h1>")
        assert parse_direction_from_h1(soup) == "下り"


# ──────────────────────────────────────────
# get_kametoku_info
# ──────────────────────────────────────────

KAMETOKU_HTML = """
<div class="single">
    <span class="port_name">亀徳港</span>
    <div class="departure">
        <span class="date">2月14日</span>
        <span class="time">10:30</span>
    </div>
    <div class="entry">
        <span class="time">16:00</span>
    </div>
    <div class="status">通常運航</div>
    <div class="exp">天候良好</div>
</div>
"""

OTHER_PORT_HTML = """
<div class="single">
    <span class="port_name">那覇港</span>
    <div class="departure">
        <span class="date">2月14日</span>
        <span class="time">09:00</span>
    </div>
    <div class="entry">
        <span class="time">15:00</span>
    </div>
    <div class="status">通常運航</div>
</div>
"""


class TestGetKametokuInfo:
    def test_extracts_kametoku_entry(self):
        soup = _make_soup(KAMETOKU_HTML)
        result = get_kametoku_info(soup, "上り")
        assert len(result) == 1
        entry = result[0]
        assert entry["運航日"] == "2月14日"
        assert entry["方向"] == "上り"
        assert entry["状況詳細"] == ["通常運航"]
        assert entry["出発時刻"] == "10:30"
        assert entry["到着時刻"] == "16:00"
        assert entry["備考"] == "天候良好"

    def test_skips_non_kametoku_port(self):
        soup = _make_soup(OTHER_PORT_HTML)
        result = get_kametoku_info(soup, "下り")
        assert result == []

    def test_returns_only_kametoku_when_mixed(self):
        soup = _make_soup(KAMETOKU_HTML + OTHER_PORT_HTML)
        result = get_kametoku_info(soup, "上り")
        assert len(result) == 1
        assert result[0]["運航日"] == "2月14日"

    def test_memo_is_na_when_exp_missing(self):
        html = KAMETOKU_HTML.replace('<div class="exp">天候良好</div>', "")
        soup = _make_soup(html)
        result = get_kametoku_info(soup, "上り")
        assert result[0]["備考"] == "N/A"

    def test_empty_html_returns_empty_list(self):
        soup = _make_soup("<div></div>")
        result = get_kametoku_info(soup, "上り")
        assert result == []

    def test_dashi_converted_to_nukko_using_last_date(self):
        """「―」は直前の港の日付を使って「抜港」として保存される"""
        html = """
        <div class="single">
            <span class="port_name">名瀬港</span>
            <div class="departure"><span class="date">04月07日</span></div>
            <div class="status">航行経路変更</div>
        </div>
        <div class="single no_status">
            <span class="port_name">亀徳港</span>
            <div class="service_single_inner">
                <div class="status sub">―</div>
                <div class="exp sub">寄港しません</div>
            </div>
        </div>
        """
        soup = _make_soup(html)
        result = get_kametoku_info(soup, "下り")
        assert len(result) == 1
        assert result[0]["状況詳細"] == ["抜港"]
        assert result[0]["運航日"] == "04月07日"

    def test_dashi_skipped_when_no_last_date(self):
        """直前の港の日付がない場合は抜港をスキップ"""
        html = """
        <div class="single no_status">
            <span class="port_name">亀徳港</span>
            <div class="service_single_inner">
                <div class="status sub">―</div>
            </div>
        </div>
        """
        soup = _make_soup(html)
        result = get_kametoku_info(soup, "下り")
        assert result == []

    def test_memo_replaced_by_h2_when_placeholder(self):
        """備考が「下記の詳細条件を確認してください」のときh2内容に置換"""
        html = """
        <h2 class="has-vivid-red-color">強風のため条件付運航</h2>
        <div class="single">
            <span class="port_name">亀徳港</span>
            <div class="departure"><span class="date">04月07日</span></div>
            <div class="status">条件付運航</div>
            <div class="exp">下記の詳細条件を確認してください</div>
        </div>
        """
        soup = _make_soup(html)
        result = get_kametoku_info(soup, "上り")
        assert result[0]["備考"] == "強風のため条件付運航"

    def test_nukko_memo_replaced_by_h2(self):
        """抜港で備考が「寄港しません」のときh2内容に置換"""
        html = """
        <h2 class="has-vivid-red-color">航行経路変更のため亀徳港に寄港しません</h2>
        <div class="single">
            <span class="port_name">名瀬港</span>
            <div class="departure"><span class="date">04月07日</span></div>
            <div class="status">航行経路変更</div>
        </div>
        <div class="single no_status">
            <span class="port_name">亀徳港</span>
            <div class="service_single_inner">
                <div class="status sub">―</div>
                <div class="exp sub">寄港しません</div>
            </div>
        </div>
        """
        soup = _make_soup(html)
        result = get_kametoku_info(soup, "下り")
        assert result[0]["備考"] == "航行経路変更のため亀徳港に寄港しません"

    def test_nukko_memo_stays_when_no_h2(self):
        """抜港でh2がなければ備考は「寄港しません」のまま"""
        html = """
        <div class="single">
            <span class="port_name">名瀬港</span>
            <div class="departure"><span class="date">04月07日</span></div>
            <div class="status">航行経路変更</div>
        </div>
        <div class="single no_status">
            <span class="port_name">亀徳港</span>
            <div class="service_single_inner">
                <div class="status sub">―</div>
                <div class="exp sub">寄港しません</div>
            </div>
        </div>
        """
        soup = _make_soup(html)
        result = get_kametoku_info(soup, "下り")
        assert result[0]["備考"] == "寄港しません"
