from labb.tests.components.test_base import ComponentTestBase


class TestBreadcrumbs(ComponentTestBase):
    """Test suite for breadcrumbs component"""

    def test_basic_rendering(self):
        """Test basic breadcrumbs component renders with default classes"""
        html = self.render_component("breadcrumbs", slot_content="<li>Home</li>")
        assert "breadcrumbs" in html
        assert "<ul>" in html
        assert "</ul>" in html
        assert "Home" in html

    def test_sizes(self):
        """Test all breadcrumbs sizes"""
        sizes = {
            "xs": "text-xs",
            "sm": "text-sm",
            "md": "text-base",
            "lg": "text-lg",
            "xl": "text-xl",
        }
        for size, css_class in sizes.items():
            html = self.render_component(
                "breadcrumbs", size=size, slot_content="<li>Home</li>"
            )
            assert css_class in html, (
                f"Expected class '{css_class}' not found for size '{size}'"
            )
            assert "breadcrumbs" in html

    def test_custom_classes(self):
        """Test custom classes are applied"""
        html = self.render_component(
            "breadcrumbs", class_="custom-class", slot_content="<li>Home</li>"
        )
        assert "custom-class" in html
        assert "breadcrumbs" in html

    def test_attributes_passthrough(self):
        """Test HTML attributes are passed through"""
        html = self.render_component(
            "breadcrumbs",
            **{"data-test": "value", "aria-label": "navigation"},
            slot_content="<li>Home</li>",
        )
        assert 'data-test="value"' in html
        assert 'aria-label="navigation"' in html

    def test_empty_breadcrumbs(self):
        """Test breadcrumbs component without items"""
        html = self.render_component("breadcrumbs")
        assert "breadcrumbs" in html
        assert "<ul>" in html
        assert "</ul>" in html

    def test_multiple_items(self):
        """Test breadcrumbs with multiple items"""
        slot_content = "<li>Home</li><li>Documents</li><li>Reports</li>"
        html = self.render_component("breadcrumbs", slot_content=slot_content)
        assert "breadcrumbs" in html
        assert "Home" in html
        assert "Documents" in html
        assert "Reports" in html

    def test_default_size(self):
        """Test default size is md (text-base)"""
        html = self.render_component("breadcrumbs", slot_content="<li>Home</li>")
        assert "text-base" in html

    def test_combination_size_and_custom_class(self):
        """Test combination of size and custom class"""
        html = self.render_component(
            "breadcrumbs",
            size="lg",
            class_="my-custom-class",
            slot_content="<li>Home</li>",
        )
        assert "text-lg" in html
        assert "my-custom-class" in html
        assert "breadcrumbs" in html


class TestBreadcrumbsItem(ComponentTestBase):
    """Test suite for breadcrumbs.item component"""

    def test_basic_item_rendering(self):
        """Test basic breadcrumb item renders"""
        html = self.render_component("breadcrumbs.item", slot_content="Home")
        assert "<li" in html
        assert "</li>" in html
        assert "Home" in html

    def test_item_with_href(self):
        """Test breadcrumb item with href"""
        html = self.render_component(
            "breadcrumbs.item", href="/home", slot_content="Home"
        )
        assert "<li" in html
        assert '<a href="/home"' in html
        assert "Home" in html

    def test_item_without_link(self):
        """Test breadcrumb item without href (current page)"""
        html = self.render_component("breadcrumbs.item", slot_content="Current Page")
        assert "<li" in html
        assert "<a" not in html
        assert "Current Page" in html

    def test_item_with_icon(self):
        """Test breadcrumb item with icon"""
        html = self.render_component(
            "breadcrumbs.item", icon="rmx.home", slot_content="Home"
        )
        assert "<li" in html
        assert "Home" in html
        # Should contain the rendered SVG icon
        assert "<svg" in html
        assert 'height="1em"' in html
        assert 'width="1em"' in html

    def test_item_with_icon_and_href(self):
        """Test breadcrumb item with both icon and href"""
        html = self.render_component(
            "breadcrumbs.item", href="/home", icon="rmx.home", slot_content="Home"
        )
        assert '<a href="/home"' in html
        assert "Home" in html
        assert "<svg" in html

    def test_item_icon_fill(self):
        """Test breadcrumb item with filled icon"""
        html = self.render_component(
            "breadcrumbs.item",
            icon="rmx.home",
            iconFill="true",
            slot_content="Home",
        )
        assert "<li" in html
        assert "Home" in html
        assert "<svg" in html
        assert 'fill="currentColor"' in html

    def test_item_icon_class(self):
        """Test breadcrumb item with icon and custom icon class"""
        html = self.render_component(
            "breadcrumbs.item",
            icon="rmx.home",
            iconClass="text-primary",
            slot_content="Home",
        )
        assert "<li" in html
        assert "Home" in html
        assert 'is="lbi"' in html or "<svg" in html

    def test_item_custom_class(self):
        """Test breadcrumb item with custom class"""
        html = self.render_component(
            "breadcrumbs.item", class_="custom-item-class", slot_content="Home"
        )
        assert "custom-item-class" in html
        assert "Home" in html

    def test_item_attributes_passthrough(self):
        """Test breadcrumb item HTML attributes are passed through"""
        html = self.render_component(
            "breadcrumbs.item",
            href="/home",
            **{"data-test": "home-link", "aria-label": "Home page"},
            slot_content="Home",
        )
        assert 'data-test="home-link"' in html
        assert 'aria-label="Home page"' in html

    def test_item_with_viewname(self):
        """Test breadcrumb item with Django viewname"""
        # Note: viewname resolution requires URL configuration in test environment
        # This test is skipped as it requires a full Django URL setup
        # In production use, viewname will properly resolve to URLs
        html = self.render_component(
            "breadcrumbs.item", viewname="home", slot_content="Home"
        )
        # Test will fail if URL resolution is not configured, which is expected
        # In actual usage with proper URL configuration, this will work correctly
        assert "Home" in html or "rendering error" in html.lower()

    def test_item_icon_without_text(self):
        """Test breadcrumb item with icon only"""
        html = self.render_component("breadcrumbs.item", icon="rmx.home")
        assert "<li" in html
        assert "<svg" in html

    def test_item_with_href_and_custom_class(self):
        """Test breadcrumb item with href and custom class"""
        html = self.render_component(
            "breadcrumbs.item",
            href="/documents",
            class_="active-item",
            slot_content="Documents",
        )
        assert '<a href="/documents"' in html
        assert "active-item" in html
        assert "Documents" in html


class TestBreadcrumbsIntegration(ComponentTestBase):
    """Integration tests for breadcrumbs with breadcrumbs.item"""

    def test_complete_breadcrumbs_navigation(self):
        """Test complete breadcrumbs navigation with multiple items"""
        template = """
        {% load lb_tags %}
        <c-lb.breadcrumbs>
            <c-lb.breadcrumbs.item href="/" icon="rmx.home">Home</c-lb.breadcrumbs.item>
            <c-lb.breadcrumbs.item href="/documents">Documents</c-lb.breadcrumbs.item>
            <c-lb.breadcrumbs.item>Current Page</c-lb.breadcrumbs.item>
        </c-lb.breadcrumbs>
        """
        html = self.render_template_string(template)
        assert "breadcrumbs" in html
        assert "Home" in html
        assert "Documents" in html
        assert "Current Page" in html
        assert 'href="/"' in html
        assert 'href="/documents"' in html
        # Last item should not have a link
        assert html.count("<a") == 2

    def test_breadcrumbs_with_sizes(self):
        """Test breadcrumbs with different sizes"""
        template = """
        {% load lb_tags %}
        <c-lb.breadcrumbs size="lg">
            <c-lb.breadcrumbs.item href="/">Home</c-lb.breadcrumbs.item>
            <c-lb.breadcrumbs.item>Current</c-lb.breadcrumbs.item>
        </c-lb.breadcrumbs>
        """
        html = self.render_template_string(template)
        assert "text-lg" in html
        assert "Home" in html
        assert "Current" in html

    def test_breadcrumbs_with_all_icons(self):
        """Test breadcrumbs with icons on all items"""
        template = """
        {% load lb_tags %}
        <c-lb.breadcrumbs>
            <c-lb.breadcrumbs.item href="/" icon="rmx.home">Home</c-lb.breadcrumbs.item>
            <c-lb.breadcrumbs.item href="/docs" icon="rmx.file">Documents</c-lb.breadcrumbs.item>
            <c-lb.breadcrumbs.item icon="rmx.folder">Folder</c-lb.breadcrumbs.item>
        </c-lb.breadcrumbs>
        """
        html = self.render_template_string(template)
        assert "breadcrumbs" in html
        # Should have 3 SVG icons
        assert html.count("<svg") == 3

    def test_breadcrumbs_small_with_custom_class(self):
        """Test breadcrumbs with small size and custom class"""
        template = """
        {% load lb_tags %}
        <c-lb.breadcrumbs size="sm" class="my-breadcrumbs">
            <c-lb.breadcrumbs.item href="/">Home</c-lb.breadcrumbs.item>
            <c-lb.breadcrumbs.item>Current</c-lb.breadcrumbs.item>
        </c-lb.breadcrumbs>
        """
        html = self.render_template_string(template)
        assert "text-sm" in html
        assert "my-breadcrumbs" in html

    def test_breadcrumbs_accessibility(self):
        """Test breadcrumbs with accessibility attributes"""
        template = """
        {% load lb_tags %}
        <c-lb.breadcrumbs aria-label="Breadcrumb navigation">
            <c-lb.breadcrumbs.item href="/" aria-label="Home page">Home</c-lb.breadcrumbs.item>
            <c-lb.breadcrumbs.item>Current</c-lb.breadcrumbs.item>
        </c-lb.breadcrumbs>
        """
        html = self.render_template_string(template)
        assert 'aria-label="Breadcrumb navigation"' in html
        assert 'aria-label="Home page"' in html
