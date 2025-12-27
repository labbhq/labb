"""Tests for icon components."""

import os
import tempfile

import pytest
from django.conf import settings
from django.template.loader import render_to_string
from django.test import TestCase


@pytest.mark.django_db
class IconComponentTest(TestCase):
    """Test icon components rendering."""

    def render_component(self, component_name, **kwargs):
        """
        Render a component with given attributes using Django's template engine.

        This method creates a temporary template file containing the component usage,
        then uses Django's template engine to render it. This ensures we test
        the actual Django Cotton components and templates.
        """
        attr_parts = []
        for key, value in kwargs.items():
            if value is True:
                attr_parts.append(key)
            elif value is False or value is None or value == "":
                continue
            else:
                if key == "class_":  # Handle Python reserved keyword
                    attr_parts.append(f'class="{value}"')
                else:
                    attr_parts.append(f'{key}="{value}"')

        attrs_str = " " + " ".join(attr_parts) if attr_parts else ""

        template_content = f"""
        {{% load cotton %}}
        <c-lbi.{component_name}{attrs_str} />
        """.strip()

        context = {}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False
        ) as tmp_file:
            tmp_file.write(template_content)
            tmp_file_path = tmp_file.name

        try:
            tmp_filename = os.path.basename(tmp_file_path)
            temp_dir = os.path.dirname(tmp_file_path)
            current_template_dirs = list(settings.TEMPLATES[0]["DIRS"])
            settings.TEMPLATES[0]["DIRS"].insert(0, temp_dir)

            try:
                html = render_to_string(tmp_filename, context)
                return html.strip()
            finally:
                settings.TEMPLATES[0]["DIRS"] = current_template_dirs

        except Exception as e:
            return f"<!-- Component rendering error: {e} -->"
        finally:
            try:
                os.unlink(tmp_file_path)
            except OSError:
                pass

    def test_heart_icon_default_rendering(self):
        """Test heart icon renders line variant by default."""
        html = self.render_component("rmx.heart", w="32", h="32", class_="text-red-500")
        self.assertIn("<svg", html)
        self.assertIn('width="32"', html)
        self.assertIn('height="32"', html)
        self.assertIn('class="text-red-500"', html)
        self.assertIn('viewbox="0 0 24 24"', html)
        # Should render line variant by default (outlined heart)
        self.assertIn("ZM18.827 6.1701", html)  # Line variant path

    def test_heart_icon_fill_rendering(self):
        """Test heart icon renders fill variant when fill is specified."""
        html = self.render_component(
            "rmx.heart", w="32", h="32", class_="text-red-500", fill=True
        )
        self.assertIn("<svg", html)
        self.assertIn('width="32"', html)
        self.assertIn('height="32"', html)
        self.assertIn('class="text-red-500"', html)
        self.assertIn('viewbox="0 0 24 24"', html)
        # Should render fill variant (solid heart)
        self.assertIn('Z"></path>', html)  # Fill variant path (shorter)

    def test_heart_icon_line_rendering(self):
        """Test heart icon renders line variant when line is specified."""
        html = self.render_component(
            "rmx.heart", w="32", h="32", class_="text-red-500", line=True
        )
        self.assertIn("<svg", html)
        self.assertIn('width="32"', html)
        self.assertIn('height="32"', html)
        self.assertIn('class="text-red-500"', html)
        self.assertIn('viewbox="0 0 24 24"', html)
        # Should render line variant (outlined heart)
        self.assertIn("ZM18.827 6.1701", html)  # Line variant path

    def test_camera_icon_default_rendering(self):
        """Test camera icon renders line variant by default."""
        html = self.render_component(
            "rmx.camera", w="28", h="28", class_="text-blue-500"
        )
        self.assertIn("<svg", html)
        self.assertIn('width="28"', html)
        self.assertIn('height="28"', html)
        self.assertIn('class="text-blue-500"', html)
        self.assertIn('viewbox="0 0 24 24"', html)
        # Should render line variant by default
        self.assertIn(
            "9.82843 5L7.82843 7H4V19H20V7H16.1716L14.1716 5H9.82843Z", html
        )  # Line variant path

    def test_camera_icon_fill_rendering(self):
        """Test camera icon renders fill variant when fill is specified."""
        html = self.render_component(
            "rmx.camera", w="28", h="28", class_="text-blue-500", fill=True
        )
        self.assertIn("<svg", html)
        self.assertIn('width="28"', html)
        self.assertIn('height="28"', html)
        self.assertIn('class="text-blue-500"', html)
        self.assertIn('viewbox="0 0 24 24"', html)
        # Should render fill variant
        self.assertIn(
            "12 19C15.3137 19 18 16.3137 18 13C18 9.68629 15.3137 7 12 7C8.68629 7 6 9.68629 6 13C6 16.3137 8.68629 19 12 19Z",
            html,
        )  # Fill variant path

    def test_icon_default_values(self):
        """Test icon uses default values when not specified."""
        html = self.render_component("rmx.heart")
        self.assertIn('width="24"', html)  # Default width
        self.assertIn('height="24"', html)  # Default height
        self.assertIn('class=""', html)  # Default empty class

    def test_icon_with_custom_class(self):
        """Test icon with custom CSS class."""
        html = self.render_component("rmx.heart", class_="text-red-500 my-custom-class")
        self.assertIn('class="text-red-500 my-custom-class"', html)

    def test_icon_with_different_sizes(self):
        """Test icon with different width and height."""
        html = self.render_component("rmx.heart", w="16", h="20")
        self.assertIn('width="16"', html)
        self.assertIn('height="20"', html)
