"""Tests for the guided-tour renderer (c-lbb.renderer.tour).

The tour is a Datastar-driven step list: each step is a <button> that on click
sets the `$tourStep_{idsafe}` signal, switches to the code view, sets the active
file, and calls lbbTourHighlight(). Keyboard nav (added in 0020) drives the same
behaviour from the <ol> container: arrows move between steps and wrap at the ends,
Home/End jump to first/last, and each key change reuses the per-step click handler.
"""

from .test_base import ComponentTestBase


class TestTourKeyboardNav(ComponentTestBase):
    """Keyboard navigation, roving tabindex, and the a11y contract."""

    def render_tour(self, steps=3):
        tour = [
            {
                "n": i,
                "title": f"Step {i}",
                "file": "views.py",
                "start_line": i * 10,
                "end_line": i * 10 + 5,
            }
            for i in range(1, steps + 1)
        ]
        return self.render_template_string(
            """
{% load lb_tags %}
<c-lbb.renderer.tour id="hero" idsafe="hero" :tour=tour />
""",
            {"tour": tour},
        )

    # --- keydown handler lives on the list container -----------------------

    def test_keydown_handler_on_list(self):
        html = self.render_tour()
        assert "data-on:keydown" in html
        # Only these keys are handled; everything else returns early so Tab
        # leaves the list normally (focus is not trapped).
        assert "'ArrowDown'" in html
        assert "'ArrowUp'" in html
        assert "'Home'" in html
        assert "'End'" in html

    def test_wrap_arithmetic_uses_step_count(self):
        # 3 steps → len is baked from `tour|length`.
        assert "const len = 3;" in self.render_tour(steps=3)
        assert "const len = 5;" in self.render_tour(steps=5)

    def test_down_wraps_at_end(self):
        # At the last step ArrowDown returns to the first (modulo wrap).
        html = self.render_tour()
        assert "cur >= len ? 1 : cur + 1" in html

    def test_up_wraps_at_start(self):
        # At the first step ArrowUp jumps to the last.
        html = self.render_tour()
        assert "cur <= 1 ? len : cur - 1" in html

    def test_home_and_end_jump_to_first_and_last(self):
        html = self.render_tour()
        assert "'Home' ? 1 : len" in html

    def test_key_change_reuses_click(self):
        # Each key change mirrors a click exactly by dispatching one on the
        # target step button, then moving focus to it (roving tabindex).
        html = self.render_tour()
        assert "el.querySelector('[data-tour-step=' + t + ']')" in html
        assert "btn.click(); btn.focus();" in html

    # --- active-step signal ------------------------------------------------

    def test_active_step_signal_updates_per_step(self):
        # The click handler each keypress fires sets the active-step signal to
        # that step's number; every step button carries its own assignment.
        html = self.render_tour()
        assert "$tourStep_hero = 1;" in html
        assert "$tourStep_hero = 2;" in html
        assert "$tourStep_hero = 3;" in html

    def test_arrow_reads_active_step_signal(self):
        html = self.render_tour()
        assert "const cur = $tourStep_hero;" in html

    # --- roving tabindex + a11y -------------------------------------------

    def test_each_step_has_stable_selector(self):
        html = self.render_tour()
        assert 'data-tour-step="1"' in html
        assert 'data-tour-step="2"' in html
        assert 'data-tour-step="3"' in html

    def test_roving_tabindex(self):
        html = self.render_tour()
        # Active step is tabindex 0, the rest -1.
        assert "data-attr:tabindex" in html
        assert "$tourStep_hero === 1 || $tourStep_hero === 0 ? 0 : -1" in html
        assert "$tourStep_hero === 2 ? 0 : -1" in html

    def test_active_step_marked_aria_current(self):
        html = self.render_tour()
        assert "data-attr:aria-current" in html
        assert "$tourStep_hero === 2 ? 'step' : null" in html
