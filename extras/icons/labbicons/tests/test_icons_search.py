"""`labb icons search` accepts several comma-separated terms.

Hunting icons for a page means picking one per slot, so searching several at
once should be one command. Each term reports its own section: a merged table
would lose which term matched, which is the thing you are choosing on.
"""

import pytest

from labbicons.cli.handlers.icons_handler import (
    _match_icons,
    parse_search_terms,
    search_icons,
)

ICONS = [
    {
        "name": "arrow-right",
        "pack": "rmx",
        "category": "Arrows",
        "variants": ["line", "fill"],
        "component_name": "rmx.arrow-right",
    },
    {
        "name": "arrow-left",
        "pack": "rmx",
        "category": "Arrows",
        "variants": ["line"],
        "component_name": "rmx.arrow-left",
    },
    {
        "name": "heart",
        "pack": "rmx",
        "category": "Health",
        "variants": ["line", "fill"],
        "component_name": "rmx.heart",
    },
    {
        "name": "user-heart",
        "pack": "rmx",
        "category": "Users",
        "variants": ["fill"],
        "component_name": "rmx.user-heart",
    },
]


class TestParseSearchTerms:
    @pytest.mark.parametrize(
        "query,expected",
        [
            ("arrow", ["arrow"]),
            ("arrow,heart", ["arrow", "heart"]),
            ("arrow, heart", ["arrow", "heart"]),
            ("  arrow ,  heart  ", ["arrow", "heart"]),
            ("arrow,,heart", ["arrow", "heart"]),
            ("arrow,", ["arrow"]),
            (",", []),
            ("", []),
        ],
    )
    def test_splits_trims_and_drops_blanks(self, query, expected):
        assert parse_search_terms(query) == expected

    def test_order_is_preserved(self):
        assert parse_search_terms("c,a,b") == ["c", "a", "b"]

    def test_a_term_may_contain_hyphens(self):
        assert parse_search_terms("arrow-right,user-heart") == [
            "arrow-right",
            "user-heart",
        ]


class TestMatchIcons:
    def test_matches_on_substring_of_the_name(self):
        names = [i["name"] for i in _match_icons(ICONS, "arrow", None, None)]
        assert names == ["arrow-right", "arrow-left"]

    def test_category_filter_still_applies(self):
        names = [i["name"] for i in _match_icons(ICONS, "heart", "Users", None)]
        assert names == ["user-heart"]

    def test_variant_filter_still_applies(self):
        names = [i["name"] for i in _match_icons(ICONS, "heart", None, "fill")]
        assert names == ["heart", "user-heart"]

    def test_variant_filter_excludes_non_matching(self):
        names = [i["name"] for i in _match_icons(ICONS, "arrow", None, "fill")]
        assert names == ["arrow-right"]

    def test_no_match_returns_empty(self):
        assert _match_icons(ICONS, "nothing-like-this", None, None) == []


@pytest.fixture
def all_icons(monkeypatch):
    monkeypatch.setattr(
        "labbicons.cli.handlers.icons_handler.load_all_packs_metadata",
        lambda: {"remix": {"icons": ICONS}},
    )


class TestSearchOutput:
    def test_single_term_has_no_per_term_header(self, all_icons, capsys):
        search_icons("arrow")
        out = capsys.readouterr().out
        assert "Searching icons for: 'arrow'" in out
        assert "Found 2 icon(s) matching 'arrow'" in out

    def test_each_term_reports_its_own_section(self, all_icons, capsys):
        search_icons("arrow,heart")
        out = capsys.readouterr().out
        assert "Found 2 icon(s) matching 'arrow'" in out
        assert "Found 2 icon(s) matching 'heart'" in out

    def test_whitespace_around_commas_is_ignored(self, all_icons, capsys):
        search_icons("  arrow ,  heart ")
        out = capsys.readouterr().out
        assert "Found 2 icon(s) matching 'arrow'" in out
        assert "Found 2 icon(s) matching 'heart'" in out

    def test_a_term_with_no_matches_does_not_stop_the_others(self, all_icons, capsys):
        search_icons("nothing-like-this,heart")
        out = capsys.readouterr().out
        assert "No icons found matching 'nothing-like-this'" in out
        assert "Found 2 icon(s) matching 'heart'" in out

    def test_limit_applies_per_term_not_across_the_whole_result(
        self, all_icons, capsys
    ):
        # 2 arrows + 2 hearts; limit=1 must not let arrows starve hearts
        search_icons("arrow,heart", limit=1)
        out = capsys.readouterr().out
        assert "Found 1 icon(s) matching 'arrow'" in out
        assert "Found 1 icon(s) matching 'heart'" in out

    def test_truncation_reports_the_real_total(self, all_icons, capsys):
        search_icons("arrow", limit=1)
        out = capsys.readouterr().out
        # regression: the total used to be read after truncating, so it
        # always equalled the limit
        assert "total: 2" in out

    def test_an_empty_query_says_so(self, all_icons, capsys):
        search_icons(" , ")
        assert "No search terms given" in capsys.readouterr().out
