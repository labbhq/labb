import json
import re

from labbdocs.templatetags.docs_tags import generate_structured_data

BREAKOUT = "Todo </script><img src=x onerror=alert(1)>"


def _render(title):
    doc_info = {
        "url_path": "ui/components/todo",
        "frontmatter": {"title": title, "description": title, "component": "c-lb.todo"},
        "title": title,
    }
    return generate_structured_data({"request": None}, doc_info)


def test_a_closing_script_tag_in_frontmatter_cannot_break_out():
    html = _render(BREAKOUT)

    assert "</script><img" not in html
    assert html.count("</script>") == 1


def test_the_payload_is_still_valid_json_ld():
    html = _render(BREAKOUT)

    body = re.search(
        r'<script type="application/ld\+json">\n(.*)\n</script>', html, re.S
    )
    assert body, "script block not found"

    data = json.loads(body.group(1))
    assert any(BREAKOUT in json.dumps(entry) for entry in data)
