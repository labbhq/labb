from labb.tests.components.test_base import ComponentTestBase


class TestMockupCode(ComponentTestBase):
    """Test mockup-code component"""

    def test_basic_mockup_code(self):
        """Test basic code mockup rendering"""
        html = self.render_component(
            "mockup-code",
            slot_content='<pre data-prefix="$"><code>npm i daisyui</code></pre>',
        )
        assert "mockup-code" in html
        assert "npm i daisyui" in html

    def test_mockup_code_custom_class(self):
        """Test code mockup with custom CSS class"""
        html = self.render_component(
            "mockup-code",
            slot_content="<pre><code>test</code></pre>",
            **{"class": "bg-primary text-primary-content"},
        )
        assert "bg-primary" in html
        assert "text-primary-content" in html

    def test_mockup_code_multiple_lines(self):
        """Test code mockup with multiple lines"""
        html = self.render_component(
            "mockup-code",
            slot_content=(
                '<pre data-prefix="$"><code>npm i daisyui</code></pre>'
                '<pre data-prefix=">" class="text-success"><code>Done!</code></pre>'
            ),
        )
        assert "mockup-code" in html
        assert "npm i daisyui" in html
        assert "Done!" in html
