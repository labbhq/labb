from labb.tests.components.test_base import ComponentTestBase, ComponentTestTemplate


class TestTimeline(ComponentTestTemplate):
    """Test suite for the timeline component"""

    component_name = "timeline"

    def test_timeline_renders_with_base_class(self):
        """Test that timeline renders with the timeline base class"""
        html = self.render_component("timeline", slot_content="<li>Event</li>")
        self.assert_classes_present(html, {"timeline"})

    def test_timeline_renders_as_ul(self):
        """Test that timeline renders as a ul element"""
        html = self.render_component("timeline", slot_content="<li>Event</li>")
        assert "<ul" in html
        assert "</ul>" in html

    def test_timeline_horizontal_direction(self):
        """Test timeline with horizontal direction"""
        html = self.render_component(
            "timeline", direction="horizontal", slot_content="<li>Event</li>"
        )
        assert "timeline-horizontal" in html

    def test_timeline_vertical_direction(self):
        """Test timeline with vertical direction"""
        html = self.render_component(
            "timeline", direction="vertical", slot_content="<li>Event</li>"
        )
        assert "timeline-vertical" in html

    def test_timeline_compact(self):
        """Test timeline with compact layout"""
        html = self.render_component(
            "timeline", compact="true", slot_content="<li>Event</li>"
        )
        assert "timeline-compact" in html

    def test_timeline_snap(self):
        """Test timeline with snap-icon"""
        html = self.render_component(
            "timeline", snap="true", slot_content="<li>Event</li>"
        )
        assert "timeline-snap-icon" in html

    def test_timeline_custom_class(self):
        """Test timeline with custom CSS class"""
        html = self.render_component(
            "timeline",
            slot_content="<li>Event</li>",
            **{"class": "my-custom"},
        )
        assert "my-custom" in html


class TestTimelineItem(ComponentTestBase):
    """Test suite for the timeline.item component"""

    def test_timeline_item_renders_as_li(self):
        """Test that timeline.item renders as a li element"""
        html = self.render_component("timeline.item", slot_content="<div>Content</div>")
        assert "<li" in html
        assert "</li>" in html

    def test_timeline_item_renders_slot(self):
        """Test that slot content is rendered"""
        html = self.render_component(
            "timeline.item", slot_content="<div>Event content</div>"
        )
        assert "Event content" in html

    def test_timeline_item_first_no_hr_before(self):
        """Test that first item has no hr before content"""
        html = self.render_component(
            "timeline.item", first="true", end="First event", endBox="true"
        )
        # Should have hr after (not last) but not before (first)
        assert "First event" in html
        # Count hr tags - should be exactly 1 (after only)
        assert html.count("<hr") == 1

    def test_timeline_item_last_no_hr_after(self):
        """Test that last item has no hr after content"""
        html = self.render_component(
            "timeline.item", last="true", end="Last event", endBox="true"
        )
        assert "Last event" in html
        # Should have hr before (not first) but not after (last)
        assert html.count("<hr") == 1

    def test_timeline_item_first_and_last_no_hr(self):
        """Test that an item that is both first and last has no hr"""
        html = self.render_component(
            "timeline.item", first="true", last="true", end="Only event"
        )
        assert "Only event" in html
        assert "<hr" not in html

    def test_timeline_item_middle_has_both_hr(self):
        """Test that a middle item (not first, not last) has hr on both sides"""
        html = self.render_component("timeline.item", end="Middle event", endBox="true")
        assert html.count("<hr") == 2

    def test_timeline_item_icon_prop(self):
        """Test that icon prop renders timeline-middle with icon"""
        html = self.render_component(
            "timeline.item", icon="rmx.check", first="true", last="true"
        )
        assert "timeline-middle" in html
        assert "<svg" in html

    def test_timeline_item_start_prop(self):
        """Test that start prop renders timeline-start section"""
        html = self.render_component(
            "timeline.item", start="2024", first="true", last="true"
        )
        assert "timeline-start" in html
        assert "2024" in html

    def test_timeline_item_end_prop(self):
        """Test that end prop renders timeline-end section"""
        html = self.render_component(
            "timeline.item", end="Event happened", first="true", last="true"
        )
        assert "timeline-end" in html
        assert "Event happened" in html

    def test_timeline_item_end_box(self):
        """Test that endBox applies timeline-box to end section"""
        html = self.render_component(
            "timeline.item",
            end="Boxed",
            endBox="true",
            first="true",
            last="true",
        )
        assert "timeline-box" in html
        assert "timeline-end" in html

    def test_timeline_item_start_box(self):
        """Test that startBox applies timeline-box to start section"""
        html = self.render_component(
            "timeline.item",
            start="Boxed start",
            startBox="true",
            first="true",
            last="true",
        )
        assert "timeline-box" in html
        assert "timeline-start" in html

    def test_timeline_item_all_props(self):
        """Test timeline.item with all convenience props"""
        html = self.render_component(
            "timeline.item",
            first="true",
            start="2024",
            icon="rmx.check",
            end="Major release",
            endBox="true",
        )
        assert "timeline-start" in html
        assert "2024" in html
        assert "timeline-middle" in html
        assert "<svg" in html
        assert "timeline-end" in html
        assert "Major release" in html
        assert "timeline-box" in html
        # first=true, so only 1 hr (after)
        assert html.count("<hr") == 1

    def test_timeline_item_slot_overrides_start_prop(self):
        """Test that startSlot overrides start prop"""
        html = self.render_component(
            "timeline.item",
            start="Ignored",
            first="true",
            last="true",
            slot_content='<c-slot name="startSlot"><div class="timeline-start timeline-box">Custom start</div></c-slot>',
        )
        assert "Custom start" in html
        assert "Ignored" not in html

    def test_timeline_item_slot_overrides_end_prop(self):
        """Test that endSlot overrides end prop"""
        html = self.render_component(
            "timeline.item",
            end="Ignored",
            first="true",
            last="true",
            slot_content='<c-slot name="endSlot"><div class="timeline-end timeline-box">Custom end</div></c-slot>',
        )
        assert "Custom end" in html
        assert "Ignored" not in html

    def test_timeline_item_slot_overrides_icon_prop(self):
        """Test that middleSlot overrides icon prop"""
        html = self.render_component(
            "timeline.item",
            icon="rmx.check",
            first="true",
            last="true",
            slot_content='<c-slot name="middleSlot"><div class="timeline-middle">Custom marker</div></c-slot>',
        )
        assert "Custom marker" in html
        # The icon should not render because middleSlot overrides it
        assert "<svg" not in html

    def test_timeline_item_variant_colors_hr(self):
        """Test that variant prop applies color to hr connectors"""
        html = self.render_component(
            "timeline.item", variant="primary", end="Event", endBox="true"
        )
        assert "bg-primary" in html
        # Both hrs should have the variant class
        assert html.count("bg-primary") == 2

    def test_timeline_item_variant_colors_icon(self):
        """Test that variant prop applies color to the icon"""
        html = self.render_component(
            "timeline.item",
            variant="success",
            icon="rmx.check",
            first="true",
            last="true",
        )
        assert "text-success" in html

    def test_timeline_item_variant_colors_both(self):
        """Test that variant colors both hr and icon together"""
        html = self.render_component(
            "timeline.item",
            variant="info",
            icon="rmx.check",
            end="Event",
            endBox="true",
        )
        assert "bg-info" in html
        assert "text-info" in html

    def test_timeline_item_no_variant_no_color_on_hr(self):
        """Test that without variant, hr has no color class"""
        html = self.render_component("timeline.item", end="Event", endBox="true")
        assert "bg-primary" not in html
        assert "bg-success" not in html

    def test_timeline_item_variant_with_first_last(self):
        """Test variant with first item (only hr after is colored)"""
        html = self.render_component(
            "timeline.item",
            variant="warning",
            first="true",
            end="First",
            endBox="true",
        )
        assert html.count("bg-warning") == 1
        assert html.count("<hr") == 1


class TestTimelineStart(ComponentTestBase):
    """Test suite for the timeline.start component"""

    def test_timeline_start_renders_with_base_class(self):
        """Test that timeline.start renders with timeline-start class"""
        html = self.render_component("timeline.start", slot_content="2024")
        self.assert_classes_present(html, {"timeline-start"})

    def test_timeline_start_with_box(self):
        """Test timeline.start with box styling"""
        html = self.render_component("timeline.start", box="true", slot_content="Event")
        assert "timeline-box" in html
        assert "timeline-start" in html


class TestTimelineMiddle(ComponentTestBase):
    """Test suite for the timeline.middle component"""

    def test_timeline_middle_renders_with_base_class(self):
        """Test that timeline.middle renders with timeline-middle class"""
        html = self.render_component("timeline.middle", slot_content="<span>*</span>")
        self.assert_classes_present(html, {"timeline-middle"})

    def test_timeline_middle_with_icon(self):
        """Test timeline.middle with an icon"""
        html = self.render_component("timeline.middle", icon="rmx.check")
        assert "timeline-middle" in html
        assert "<svg" in html

    def test_timeline_middle_icon_with_custom_class(self):
        """Test timeline.middle icon with custom class"""
        html = self.render_component(
            "timeline.middle", icon="rmx.check", iconClass="text-primary"
        )
        assert "<svg" in html


class TestTimelineEnd(ComponentTestBase):
    """Test suite for the timeline.end component"""

    def test_timeline_end_renders_with_base_class(self):
        """Test that timeline.end renders with timeline-end class"""
        html = self.render_component("timeline.end", slot_content="Details")
        self.assert_classes_present(html, {"timeline-end"})

    def test_timeline_end_with_box(self):
        """Test timeline.end with box styling"""
        html = self.render_component("timeline.end", box="true", slot_content="Event")
        assert "timeline-box" in html
        assert "timeline-end" in html


class TestTimelineHr(ComponentTestBase):
    """Test suite for the timeline.hr component"""

    def test_timeline_hr_renders(self):
        """Test that timeline.hr renders an hr element"""
        html = self.render_component("timeline.hr")
        assert "<hr" in html

    def test_timeline_hr_with_color_class(self):
        """Test timeline.hr with color class"""
        html = self.render_component("timeline.hr", **{"class": "bg-primary"})
        assert "bg-primary" in html
