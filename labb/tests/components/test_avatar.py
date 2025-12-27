from labb.tests.components.test_base import ComponentTestBase


class TestAvatar(ComponentTestBase):
    """Test avatar component"""

    def test_basic_avatar(self):
        """Test basic avatar rendering"""
        html = self.render_component("avatar")
        assert "avatar" in html
        assert 'class="avatar' in html

    def test_avatar_with_image(self):
        """Test avatar with image source"""
        html = self.render_component(
            "avatar", src="https://example.com/avatar.jpg", alt="User avatar"
        )
        assert "avatar" in html
        assert 'src="https://example.com/avatar.jpg"' in html
        assert 'alt="User avatar"' in html

    def test_avatar_sizes(self):
        """Test avatar sizes"""
        sizes = ["xs", "sm", "md", "lg", "xl"]
        size_classes = [
            "w-8 text-xs",
            "w-12 text-md",
            "w-16 text-lg",
            "w-24 text-xl",
            "w-32 text-2xl",
        ]

        for size, expected_class in zip(sizes, size_classes):
            html = self.render_component("avatar", size=size)
            assert expected_class in html

    def test_avatar_rounded(self):
        """Test avatar rounded size variants"""
        rounded_options = {
            "xs": "rounded-xs",
            "sm": "rounded-sm",
            "md": "rounded-md",
            "lg": "rounded-lg",
            "xl": "rounded-xl",
            "full": "rounded-full",
        }

        for rounded, expected_class in rounded_options.items():
            html = self.render_component("avatar", rounded=rounded)
            assert expected_class in html

    def test_avatar_masks(self):
        """Test avatar mask shapes"""
        masks = {
            "heart": "mask mask-heart",
            "squircle": "mask mask-squircle",
            "hexagon-2": "mask mask-hexagon-2",
            "triangle": "mask mask-triangle",
            "pentagon": "mask mask-pentagon",
            "diamond": "mask mask-diamond",
            "star": "mask mask-star",
        }

        for mask, expected_classes in masks.items():
            html = self.render_component("avatar", mask=mask)
            for class_name in expected_classes.split():
                assert class_name in html

    def test_avatar_status(self):
        """Test avatar status indicators"""
        statuses = {"online": "avatar-online", "offline": "avatar-offline"}

        for status, expected_class in statuses.items():
            html = self.render_component("avatar", status=status)
            assert expected_class in html

    def test_avatar_placeholder(self):
        """Test avatar placeholder mode"""
        html = self.render_component("avatar", placeholder="true")
        assert "avatar-placeholder" in html

    def test_avatar_placeholder_with_initials(self):
        """Test avatar placeholder with initials"""
        html = self.render_component("avatar", placeholder="true", initials="JD")
        assert "avatar-placeholder" in html
        assert ">JD<" in html

    def test_avatar_placeholder_with_icon(self):
        """Test avatar placeholder with icon"""
        html = self.render_component("avatar", placeholder="true", icon="rmx.user")
        assert "avatar-placeholder" in html
        # Should contain SVG icon (rendered by labbicons)
        assert "<svg" in html
        assert "currentColor" in html

    def test_avatar_background_colors(self):
        """Test avatar placeholder background colors"""
        bg_colors = {
            "neutral": "bg-neutral text-neutral-content",
            "primary": "bg-primary text-primary-content",
            "secondary": "bg-secondary text-secondary-content",
            "accent": "bg-accent text-accent-content",
            "info": "bg-info text-info-content",
            "success": "bg-success text-success-content",
            "warning": "bg-warning text-warning-content",
            "error": "bg-error text-error-content",
        }

        for color, expected_classes in bg_colors.items():
            html = self.render_component(
                "avatar", placeholder="true", bgColor=color, initials="AB"
            )
            for class_name in expected_classes.split():
                assert class_name in html

    def test_avatar_ring(self):
        """Test avatar with ring"""
        html = self.render_component("avatar", ring="true")
        assert "ring-2" in html
        assert "ring-offset-2" in html

    def test_avatar_ring_colors(self):
        """Test avatar ring colors"""
        ring_colors = {
            "primary": "ring-primary ring-offset-base-100",
            "secondary": "ring-secondary ring-offset-base-100",
            "accent": "ring-accent ring-offset-base-100",
            "neutral": "ring-neutral ring-offset-base-100",
            "info": "ring-info ring-offset-base-100",
            "success": "ring-success ring-offset-base-100",
            "warning": "ring-warning ring-offset-base-100",
            "error": "ring-error ring-offset-base-100",
        }

        for color, expected_classes in ring_colors.items():
            html = self.render_component("avatar", ring="true", ringColor=color)
            for class_name in expected_classes.split():
                assert class_name in html

    def test_avatar_custom_class(self):
        """Test avatar with custom CSS classes"""
        html = self.render_component("avatar", **{"class": "custom-avatar"})
        assert "custom-avatar" in html
        assert "avatar" in html

    def test_avatar_custom_content_slot(self):
        """Test avatar with custom content slot"""
        html = self.render_component(
            "avatar", slot_content='<div class="custom-content">Custom</div>'
        )
        assert "avatar" in html
        assert "custom-content" in html
        assert "Custom" in html

    def test_avatar_icon_fill(self):
        """Test avatar placeholder icon with fill"""
        html = self.render_component(
            "avatar", placeholder="true", icon="rmx.star", iconFill="true"
        )
        assert "avatar-placeholder" in html
        # Should contain SVG icon (rendered by labbicons)
        assert "<svg" in html
        assert "currentColor" in html


class TestAvatarGroup(ComponentTestBase):
    """Test avatar group component"""

    def test_basic_avatar_group(self):
        """Test basic avatar group rendering"""
        html = self.render_component("avatar.group")
        assert "avatar-group" in html
        assert '<div class="avatar-group' in html

    def test_avatar_group_spacing(self):
        """Test avatar group spacing options"""
        spacings = {
            "wide": "",  # No negative space class
            "normal": "-space-x-2",
            "tight": "-space-x-6",
            "tighter": "-space-x-8",
            "tightest": "-space-x-12",
        }

        for spacing, expected_class in spacings.items():
            html = self.render_component("avatar.group", spacing=spacing)
            assert "avatar-group" in html
            if expected_class:  # Only check if there's an expected class
                assert expected_class in html

    def test_avatar_group_with_custom_class(self):
        """Test avatar group with custom CSS classes"""
        html = self.render_component("avatar.group", **{"class": "custom-group"})
        assert "custom-group" in html
        assert "avatar-group" in html

    def test_avatar_group_with_content(self):
        """Test avatar group with avatar content"""
        content = '<c-lb.avatar size="sm" /><c-lb.avatar size="sm" />'
        html = self.render_component("avatar.group", slot_content=content)
        assert "avatar-group" in html
        # Should contain rendered avatars (the components get processed)
        assert "w-12" in html  # sm size class
