"""Guide-only examples live under lb-examples/guide/ and are not components.

Before this split, lb-examples/reactivity/ sat at the top level and showed up in
`labb components ex --tree` as if it were a component, alongside the 68 real
ones. The guide is meant to be generous with live examples, so that would only
have got worse.
"""

from unittest.mock import Mock, patch

from labb.cli.handlers.components_handler import (
    _list_all_examples,
    _show_examples_tree,
    _show_multiple_examples,
)
from labb.components.registry import GUIDE_EXAMPLES_DIR, ComponentRegistry


class TestRegistry:
    def test_guide_dir_is_not_listed_as_a_component(self):
        components = ComponentRegistry().get_available_components_with_examples()
        assert GUIDE_EXAMPLES_DIR not in components
        assert "reactivity" not in components, "the old top-level dir is gone"
        assert "button" in components

    def test_guide_topics_are_grouped_by_topic(self):
        topics = ComponentRegistry().get_guide_example_topics()
        assert "reactivity" in topics
        # a subset, not an exact list: guide pages add examples over time
        assert {"counter", "object-signal", "toggle"} <= set(topics["reactivity"])

    def test_guide_examples_resolve_by_their_full_path(self):
        registry = ComponentRegistry()
        assert registry.get_example_raw_content("guide/reactivity/toggle") is not None
        assert registry.get_example_raw_content("reactivity/toggle") is None


@patch("labb.cli.handlers.components_handler.console")
class TestCliOutput:
    def _registry(self, topics=None):
        registry = Mock()
        registry.get_available_components_with_examples.return_value = ["button"]
        registry.get_component_example_names.return_value = ["basic"]
        registry.get_guide_example_topics.return_value = (
            {"reactivity": ["counter", "toggle"]} if topics is None else topics
        )
        registry.get_example_title_from_name.side_effect = lambda n: n.title()
        return registry

    def _output(self, mock_console):
        return " ".join(str(c) for c in mock_console.print.call_args_list)

    def test_tree_shows_guide_as_its_own_branch(self, mock_console):
        from rich.tree import Tree

        _show_examples_tree(self._registry())

        tree = next(
            c.args[0]
            for c in mock_console.print.call_args_list
            if c.args and isinstance(c.args[0], Tree)
        )
        labels = [str(branch.label) for branch in tree.children]
        assert any("not components" in label for label in labels)
        # the topic sits under guide, not at the top level
        guide = next(b for b in tree.children if "guide" in str(b.label))
        assert [str(t.label) for t in guide.children] == [
            "[magenta]reactivity[/magenta]"
        ]

    def test_tree_counts_guide_separately_from_components(self, mock_console):
        _show_examples_tree(self._registry())
        output = self._output(mock_console)
        assert "across 1 components" in output
        assert "plus 2 guide examples" in output

    def test_listing_shows_the_reference_form(self, mock_console):
        _list_all_examples(self._registry())
        assert "guide/<topic>/<name>" in self._output(mock_console)

    def test_no_guide_section_when_there_are_none(self, mock_console):
        _list_all_examples(self._registry(topics={}))
        assert "Guide examples" not in self._output(mock_console)

    def test_a_guide_topic_is_accepted_as_a_target(self, mock_console):
        """`labb components ex guide/reactivity toggle` must not be rejected."""
        registry = self._registry()
        registry.get_component_example_names.return_value = ["counter", "toggle"]
        registry.get_example_raw_content.return_value = "<div></div>"

        _show_multiple_examples(registry, "guide/reactivity", ["toggle"])

        assert "has no examples" not in self._output(mock_console)
