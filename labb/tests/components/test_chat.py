"""
Tests for the chat component and its sub-components.

This module tests the chat container, chat.bubble, chat.image,
chat.header, and chat.footer components including all variants,
attributes, and slot rendering.
"""

from labb.tests.components.test_base import ComponentTestBase, ComponentTestTemplate


class TestChat(ComponentTestTemplate):
    """Test the chat container component"""

    component_name = "chat"

    def test_chat_default_rendering(self):
        """Test chat renders with default placement (start)"""
        html = self.render_component("chat", slot_content="<p>Hello</p>")
        self.assert_classes_present(html, {"chat", "chat-start"})
        assert "Hello" in html

    def test_chat_placement_start(self):
        """Test chat with explicit start placement"""
        html = self.render_component("chat", placement="start", slot_content="Message")
        self.assert_classes_present(html, {"chat", "chat-start"})

    def test_chat_placement_end(self):
        """Test chat with end placement"""
        html = self.render_component("chat", placement="end", slot_content="Message")
        self.assert_classes_present(html, {"chat", "chat-end"})

    def test_chat_custom_class(self):
        """Test chat with custom CSS class"""
        html = self.render_component("chat", **{"class": "my-chat"})
        assert "my-chat" in html
        self.assert_classes_present(html, {"chat"})

    def test_chat_attributes_passthrough(self):
        """Test HTML attributes are passed through to the container"""
        html = self.render_component("chat", id="msg-1", **{"data-role": "message"})
        assert 'id="msg-1"' in html
        assert 'data-role="message"' in html

    def test_chat_renders_as_div(self):
        """Test chat container renders as a div element"""
        html = self.render_component("chat", slot_content="Content")
        assert "<div" in html


class TestChatBubble(ComponentTestTemplate):
    """Test the chat.bubble sub-component"""

    component_name = "chat.bubble"

    def test_bubble_default_rendering(self):
        """Test bubble renders with base class and no variant"""
        html = self.render_component("chat.bubble", slot_content="Hello there")
        self.assert_classes_present(html, {"chat-bubble"})
        assert "Hello there" in html

    def test_bubble_all_variants(self):
        """Test all color variants produce correct classes"""
        variants = {
            "primary": "chat-bubble-primary",
            "secondary": "chat-bubble-secondary",
            "accent": "chat-bubble-accent",
            "neutral": "chat-bubble-neutral",
            "info": "chat-bubble-info",
            "success": "chat-bubble-success",
            "warning": "chat-bubble-warning",
            "error": "chat-bubble-error",
        }
        for variant, expected_class in variants.items():
            html = self.render_component(
                "chat.bubble", variant=variant, slot_content="Test"
            )
            self.assert_classes_present(html, {"chat-bubble", expected_class})

    def test_bubble_no_variant_class_when_empty(self):
        """Test that no variant class is added when variant is empty"""
        html = self.render_component("chat.bubble", slot_content="Plain")
        classes = self.extract_classes_from_html(html)
        assert "chat-bubble" in classes
        # No chat-bubble-* variant class should be present
        variant_classes = {c for c in classes if c.startswith("chat-bubble-")}
        assert len(variant_classes) == 0

    def test_bubble_custom_class(self):
        """Test bubble with additional custom CSS class"""
        html = self.render_component(
            "chat.bubble", **{"class": "custom-bubble"}, slot_content="Hi"
        )
        assert "custom-bubble" in html
        self.assert_classes_present(html, {"chat-bubble"})

    def test_bubble_attributes_passthrough(self):
        """Test HTML attributes are passed through"""
        html = self.render_component(
            "chat.bubble", **{"data-message-id": "42"}, slot_content="Hi"
        )
        assert 'data-message-id="42"' in html

    def test_bubble_with_html_content(self):
        """Test bubble accepts rich HTML content in slot"""
        html = self.render_component(
            "chat.bubble",
            slot_content="<p>Line one</p><p>Line two</p>",
        )
        assert "Line one" in html
        assert "Line two" in html


class TestChatImage(ComponentTestTemplate):
    """Test the chat.image sub-component"""

    component_name = "chat.image"

    def test_image_default_rendering(self):
        """Test image renders with base classes and default size"""
        html = self.render_component("chat.image", src="/avatar.png")
        self.assert_classes_present(html, {"chat-image", "avatar"})
        assert 'src="/avatar.png"' in html
        assert 'alt="Avatar"' in html
        # Default size is md -> w-10
        assert "w-10" in html

    def test_image_custom_alt(self):
        """Test image with custom alt text"""
        html = self.render_component("chat.image", src="/pic.png", alt="John Doe")
        assert 'alt="John Doe"' in html

    def test_image_size_small(self):
        """Test image with small size"""
        html = self.render_component("chat.image", src="/pic.png", size="sm")
        assert "w-8" in html

    def test_image_size_medium(self):
        """Test image with medium size (default)"""
        html = self.render_component("chat.image", src="/pic.png", size="md")
        assert "w-10" in html

    def test_image_size_large(self):
        """Test image with large size"""
        html = self.render_component("chat.image", src="/pic.png", size="lg")
        assert "w-12" in html

    def test_image_without_src_uses_slot(self):
        """Test that when src is empty, the slot content is rendered instead"""
        html = self.render_component(
            "chat.image", slot_content='<span class="placeholder">JD</span>'
        )
        assert "placeholder" in html
        # Should not have an img tag when no src
        assert "<img" not in html

    def test_image_with_src_renders_img_tag(self):
        """Test that providing src renders an img element"""
        html = self.render_component("chat.image", src="/user.jpg")
        assert "<img" in html
        assert 'src="/user.jpg"' in html

    def test_image_custom_class(self):
        """Test image with additional custom CSS class"""
        html = self.render_component(
            "chat.image", src="/pic.png", **{"class": "extra-class"}
        )
        assert "extra-class" in html
        self.assert_classes_present(html, {"chat-image", "avatar"})

    def test_image_rounded_full_applied(self):
        """Test that the inner div always has rounded-full"""
        html = self.render_component("chat.image", src="/pic.png")
        assert "rounded-full" in html


class TestChatHeader(ComponentTestTemplate):
    """Test the chat.header sub-component"""

    component_name = "chat.header"

    def test_header_default_rendering(self):
        """Test header renders with base class"""
        html = self.render_component("chat.header", slot_content="Alice")
        self.assert_classes_present(html, {"chat-header"})
        assert "Alice" in html

    def test_header_with_time_element(self):
        """Test header with name and time content"""
        html = self.render_component(
            "chat.header",
            slot_content='Bob <time datetime="2024-01-01">12:45 PM</time>',
        )
        assert "Bob" in html
        assert "<time" in html
        assert "12:45 PM" in html

    def test_header_custom_class(self):
        """Test header with additional custom CSS class"""
        html = self.render_component(
            "chat.header", **{"class": "font-bold"}, slot_content="Name"
        )
        assert "font-bold" in html
        self.assert_classes_present(html, {"chat-header"})

    def test_header_attributes_passthrough(self):
        """Test HTML attributes are passed through"""
        html = self.render_component(
            "chat.header", **{"data-sender": "alice"}, slot_content="Alice"
        )
        assert 'data-sender="alice"' in html


class TestChatFooter(ComponentTestTemplate):
    """Test the chat.footer sub-component"""

    component_name = "chat.footer"

    def test_footer_default_rendering(self):
        """Test footer renders with base class"""
        html = self.render_component("chat.footer", slot_content="Delivered")
        self.assert_classes_present(html, {"chat-footer"})
        assert "Delivered" in html

    def test_footer_with_opacity(self):
        """Test footer with opacity class for typical status styling"""
        html = self.render_component(
            "chat.footer",
            **{"class": "opacity-50"},
            slot_content="Seen",
        )
        assert "opacity-50" in html
        self.assert_classes_present(html, {"chat-footer"})
        assert "Seen" in html

    def test_footer_custom_class(self):
        """Test footer with additional custom CSS class"""
        html = self.render_component(
            "chat.footer", **{"class": "text-xs"}, slot_content="Status"
        )
        assert "text-xs" in html
        self.assert_classes_present(html, {"chat-footer"})

    def test_footer_attributes_passthrough(self):
        """Test HTML attributes are passed through"""
        html = self.render_component(
            "chat.footer", **{"data-status": "read"}, slot_content="Read"
        )
        assert 'data-status="read"' in html


class TestChatIntegration(ComponentTestBase):
    """Integration tests composing multiple chat sub-components together"""

    def test_full_chat_message_start(self):
        """Test a complete start-aligned chat message with all sub-components"""
        slot = (
            '<c-lb.chat.image src="/avatar.png" alt="Alice" />'
            "<c-lb.chat.header>Alice <time>10:00 AM</time></c-lb.chat.header>"
            '<c-lb.chat.bubble variant="primary">Good morning!</c-lb.chat.bubble>'
            '<c-lb.chat.footer class="opacity-50">Delivered</c-lb.chat.footer>'
        )
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.chat placement="start">' + slot + "</c-lb.chat>"
        )
        assert "chat-start" in html
        assert "chat-image" in html
        assert "chat-header" in html
        assert "chat-bubble" in html
        assert "chat-bubble-primary" in html
        assert "chat-footer" in html
        assert "Good morning!" in html
        assert "Alice" in html
        assert "Delivered" in html

    def test_full_chat_message_end(self):
        """Test a complete end-aligned chat message"""
        slot = (
            '<c-lb.chat.bubble variant="accent">See you later!</c-lb.chat.bubble>'
            '<c-lb.chat.footer class="opacity-50">Sent</c-lb.chat.footer>'
        )
        html = self.render_template_string(
            '{% load lb_tags %}<c-lb.chat placement="end">' + slot + "</c-lb.chat>"
        )
        assert "chat-end" in html
        assert "chat-bubble-accent" in html
        assert "See you later!" in html
        assert "Sent" in html

    def test_chat_conversation_thread(self):
        """Test rendering multiple chat messages as a conversation"""
        template = (
            "{% load lb_tags %}"
            '<div class="chat-thread">'
            '<c-lb.chat placement="start">'
            "<c-lb.chat.bubble>Hello!</c-lb.chat.bubble>"
            "</c-lb.chat>"
            '<c-lb.chat placement="end">'
            '<c-lb.chat.bubble variant="primary">Hi there!</c-lb.chat.bubble>'
            "</c-lb.chat>"
            "</div>"
        )
        html = self.render_template_string(template)
        assert "chat-start" in html
        assert "chat-end" in html
        assert "Hello!" in html
        assert "Hi there!" in html
        assert "chat-bubble-primary" in html
        assert "chat-thread" in html
