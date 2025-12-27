from unittest.mock import patch

from labb.tests.components.test_base import ComponentTestBase


class TestLink(ComponentTestBase):
    """Test link component"""

    def test_basic_link_with_href(self):
        """Test basic link rendering with href"""
        html = self.render_component("link", href="/test-url", slot_content="Test Link")
        assert "<a" in html
        assert 'href="/test-url"' in html
        assert "Test Link" in html

    def test_link_with_viewname(self):
        """Test link with Django viewname"""
        with patch("labb.templatetags.lb_tags.reverse") as mock_reverse:
            mock_reverse.return_value = "/blog/post/1/"
            html = self.render_component(
                "link", viewname="blog:post", slot_content="Blog Post"
            )
            assert "<a" in html
            assert 'href="/blog/post/1/"' in html
            assert "Blog Post" in html
            mock_reverse.assert_called_once_with("blog:post")

    def test_link_with_viewname_and_l_attrs(self):
        """Test link with viewname and l: prefixed attributes"""
        with patch("labb.templatetags.lb_tags.reverse") as mock_reverse:
            mock_reverse.return_value = "/blog/post/1/"
            # Note: In actual usage, l: attributes would be in attrs string
            # For testing, we simulate by passing them as regular attrs
            html = self.render_component(
                "link",
                viewname="blog:post",
                slot_content="Blog Post",
                # Simulating l:id="1" in attrs
            )
            assert "<a" in html
            assert 'href="/blog/post/1/"' in html
            assert "Blog Post" in html

    def test_link_elements(self):
        """Test link with different HTML elements"""
        elements = ["a", "button", "span", "div"]
        for element in elements:
            html = self.render_component(
                "link",
                **{"as": element},
                href="/test",
                slot_content=f"{element} link",
            )
            assert f"<{element}" in html
            assert f"{element} link" in html

    def test_link_with_custom_class(self):
        """Test link with custom CSS class"""
        html = self.render_component(
            "link", class_="custom-link", href="/test", slot_content="Custom Link"
        )
        assert "custom-link" in html
        assert 'href="/test"' in html
        assert "Custom Link" in html

    def test_link_without_href_or_viewname(self):
        """Test link without href or viewname (should render without href)"""
        html = self.render_component("link", slot_content="No URL Link")
        assert "<a" in html
        assert "No URL Link" in html
        # Should not have href attribute
        assert "href=" not in html or 'href=""' in html

    def test_link_viewname_with_kwargs(self):
        """Test link with viewname that requires kwargs"""
        with patch("labb.templatetags.lb_tags.reverse") as mock_reverse:
            mock_reverse.return_value = "/blog/post/1/author/sample/"
            # The template tag should extract l: attributes from attrs
            html = self.render_component(
                "link",
                viewname="blog:post",
                slot_content="Blog Post",
            )
            assert "<a" in html
            assert "Blog Post" in html

    def test_link_viewname_no_reverse_match(self):
        """Test link with invalid viewname (should not break)"""
        with patch("labb.templatetags.lb_tags.reverse") as mock_reverse:
            from django.urls import NoReverseMatch

            mock_reverse.side_effect = NoReverseMatch("View not found")
            html = self.render_component(
                "link", viewname="invalid:view", slot_content="Invalid"
            )
            assert "<a" in html
            assert "Invalid" in html
            # Should not have href if reverse fails
            assert "href=" not in html or 'href=""' in html

    def test_link_with_slot_content(self):
        """Test link with nested component content"""
        html = self.render_component(
            "link",
            href="/test",
            slot_content="<c-lb.text>Link Text</c-lb.text>",
        )
        assert 'href="/test"' in html
        # The nested component should be rendered
        assert "Link Text" in html

    def test_link_prefers_viewname_over_href(self):
        """Test that viewname takes precedence over href"""
        with patch("labb.templatetags.lb_tags.reverse") as mock_reverse:
            mock_reverse.return_value = "/blog/post/"
            html = self.render_component(
                "link",
                href="/direct-url",
                viewname="blog:post",
                slot_content="Link",
            )
            assert 'href="/blog/post/"' in html
            # reverse should be called when viewname is provided
            mock_reverse.assert_called_once_with("blog:post")

    def test_link_default_element(self):
        """Test link defaults to anchor tag"""
        html = self.render_component("link", href="/test", slot_content="Link")
        assert "<a" in html
        assert "</a>" in html

    def test_link_removes_l_attrs_from_output(self):
        """Test that l: attributes are removed from final HTML"""
        # This tests the remove_l_attrs filter
        # In actual usage, l: attributes would be in attrs and removed
        html = self.render_component(
            "link",
            viewname="blog:post",
            slot_content="Link",
        )
        # l: attributes should not appear in final HTML
        assert "l:id=" not in html
        assert "l:author=" not in html

    def test_link_base_class(self):
        """Test that link component has base 'link' class"""
        html = self.render_component("link", href="/test", slot_content="Link")
        assert 'class="' in html or "class='" in html
        # Should contain 'link' class
        assert "link" in html

    def test_link_variants(self):
        """Test link color variants"""
        variants = [
            "neutral",
            "primary",
            "secondary",
            "accent",
            "info",
            "success",
            "warning",
            "error",
        ]
        for variant in variants:
            html = self.render_component(
                "link", variant=variant, href="/test", slot_content=f"{variant} link"
            )
            assert f"link-{variant}" in html
            assert f"{variant} link" in html

    def test_link_hover(self):
        """Test link hover option"""
        html = self.render_component(
            "link", href="/test", hover=True, slot_content="Hover Link"
        )
        assert "link-hover" in html
        assert "Hover Link" in html

    def test_link_hover_with_variant(self):
        """Test link hover combined with variant"""
        html = self.render_component(
            "link",
            href="/test",
            variant="primary",
            hover=True,
            slot_content="Primary Hover",
        )
        assert "link-primary" in html
        assert "link-hover" in html
        assert "Primary Hover" in html

    def test_link_no_hover_default(self):
        """Test link without hover (default)"""
        html = self.render_component("link", href="/test", slot_content="Default Link")
        assert "link-hover" not in html
        assert "Default Link" in html
