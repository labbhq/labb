from labb.tests.components.test_base import ComponentTestBase


class TestValidateOnInput(ComponentTestBase):
    """Test validate prop on input components"""

    def test_input_validate(self):
        """Test input with validate prop"""
        html = self.render_component(
            "input", validate="true", type="email", required="true"
        )
        assert "validator" in html
        assert "input" in html

    def test_input_no_validate_by_default(self):
        """Test input does not have validator class by default"""
        html = self.render_component("input")
        assert "validator" not in html

    def test_textarea_validate(self):
        """Test textarea with validate prop"""
        html = self.render_component("textarea", validate="true", required="true")
        assert "validator" in html

    def test_select_validate(self):
        """Test select with validate prop"""
        html = self.render_component(
            "select",
            validate="true",
            required="true",
            slot_content="<option>Pick one</option>",
        )
        assert "validator" in html

    def test_checkbox_validate(self):
        """Test checkbox with validate prop"""
        html = self.render_component("checkbox", validate="true", required="true")
        assert "validator" in html

    def test_toggle_validate(self):
        """Test toggle with validate prop"""
        html = self.render_component("toggle", validate="true")
        assert "validator" in html

    def test_radio_validate(self):
        """Test radio with validate prop"""
        html = self.render_component("radio", validate="true")
        assert "validator" in html

    def test_file_input_validate(self):
        """Test file-input with validate prop"""
        html = self.render_component("file-input", validate="true", required="true")
        assert "validator" in html

    def test_range_validate(self):
        """Test range with validate prop"""
        html = self.render_component("range", validate="true")
        assert "validator" in html


class TestValidatorHint(ComponentTestBase):
    """Test validator.hint sub-component"""

    def test_basic_hint(self):
        """Test basic validator hint rendering"""
        html = self.render_component(
            "validator.hint", slot_content="This field is required"
        )
        assert "validator-hint" in html
        assert "This field is required" in html

    def test_hint_custom_class(self):
        """Test validator hint with custom class"""
        html = self.render_component(
            "validator.hint",
            slot_content="Error message",
            **{"class": "text-error"},
        )
        assert "validator-hint" in html
        assert "text-error" in html

    def test_hint_hidden(self):
        """Test validator hint with hidden flag"""
        html = self.render_component(
            "validator.hint", hidden="true", slot_content="Error message"
        )
        assert "validator-hint" in html
        assert "hidden" in html

    def test_hint_not_hidden_by_default(self):
        """Test validator hint is not hidden by default"""
        html = self.render_component("validator.hint", slot_content="Error message")
        assert "hidden" not in html

    def test_validate_with_hint(self):
        """Test input with validate prop alongside validator.hint"""
        html = self.render_template_string(
            """
            {% load lb_tags %}
            <c-lb.input validate type="email" required placeholder="mail@site.com" />
            <c-lb.validator.hint>Enter a valid email address</c-lb.validator.hint>
            """
        )
        assert "validator" in html
        assert "validator-hint" in html
        assert "Enter a valid email address" in html
