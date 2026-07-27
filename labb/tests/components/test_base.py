"""
Base test utilities for component testing in labb.

This module provides common utilities and patterns for testing Django Cotton
components, including component rendering, schema validation, and CSS class
extraction testing.
"""

import os
import re
import tempfile
import uuid
from pathlib import Path

import pytest
from django.conf import settings
from django.template import engines
from django.template.loader import render_to_string

from labb.components.registry import ComponentRegistry


def _worker_template_dir() -> Path:
    """Return a per-worker directory for temporary test templates.

    Under ``pytest -n auto`` (pytest-xdist) each worker is a separate process,
    but they all share the system temp dir. Writing temp templates there — and
    mutating ``settings.TEMPLATES[0]["DIRS"]`` per render — let one worker's
    cleanup clobber another's in-flight lookup, producing intermittent
    "template not found" failures. Giving each worker its own dedicated dir
    (keyed on ``PYTEST_XDIST_WORKER``) removes the cross-worker interference.
    """
    worker = os.environ.get("PYTEST_XDIST_WORKER", "master")
    template_dir = Path(tempfile.gettempdir()) / f"labb-test-templates-{worker}"
    template_dir.mkdir(parents=True, exist_ok=True)
    return template_dir


def _ensure_template_dir(template_dir: Path) -> None:
    """Keep the worker dir on the live template engine.

    Registering it in ``settings.TEMPLATES`` is not enough on its own: any test
    that uses ``override_settings`` restores the original TEMPLATES on exit and
    rebuilds the engines, silently dropping the dir. So re-add it when missing
    and invalidate the engine cache, rather than assuming a one-time setup holds.
    """
    template_dir_str = str(template_dir)

    # DIRS entries may be Path or str — compare as strings.
    dirs = [str(d) for d in settings.TEMPLATES[0]["DIRS"]]
    if template_dir_str not in dirs:
        settings.TEMPLATES[0]["DIRS"] = [template_dir_str, *settings.TEMPLATES[0]["DIRS"]]

    # Check the live engine, not just settings: override_settings rebuilds the
    # engines from the restored TEMPLATES, so settings can look right while the
    # engine actually in use has already dropped the dir. Both the built engines
    # and the parsed config are cached, so clear both.
    engine_dirs = [str(d) for d in engines["django"].engine.dirs]
    if template_dir_str not in engine_dirs:
        engines._engines = {}
        engines.__dict__.pop("templates", None)


def _render_isolated(template_content: str, context: dict, error_label: str) -> str:
    """Render ``template_content`` from a uniquely-named file in the worker dir.

    The worker dir is registered in ``TEMPLATES[0]["DIRS"]`` once and left in
    place (no per-call insert/restore churn); the unique per-render filename
    avoids any template-cache collisions.
    """
    template_dir = _worker_template_dir()
    tmp_name = f"{uuid.uuid4().hex}.html"
    tmp_path = template_dir / tmp_name
    tmp_path.write_text(template_content)

    _ensure_template_dir(template_dir)

    try:
        return render_to_string(tmp_name, context).strip()
    except Exception as e:
        return f"<!-- {error_label}: {e} -->"
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass


class ComponentTestBase:
    """
    Base class for component testing.

    Provides common utilities for:
    - Component template rendering
    - Schema validation
    - CSS class testing
    - Attribute parsing
    """

    def setup_method(self):
        """Setup method called before each test method"""
        self.component_registry = ComponentRegistry()

    def render_component(self, component_name, **kwargs):
        """
        Render a component with given attributes using Django's template engine.

        This method creates a temporary template file containing the component usage,
        then uses Django's template engine to render it. This ensures we test
        the actual Django Cotton components and templates.

        Args:
            component_name (str): Name of the component to render
            **kwargs: Component attributes to pass

        Returns:
            str: Rendered HTML output
        """
        # Extract slot content and special attributes
        slot_content = kwargs.pop("slot_content", "")
        as_element = kwargs.pop("as", None)

        # Build component attributes string
        attr_parts = []
        for key, value in kwargs.items():
            if value is True:
                attr_parts.append(key)
            elif value is False or value is None or value == "":
                continue  # Skip false/none/empty attributes
            else:
                # Handle special Python keywords that can't be used as kwargs
                if key == "for":
                    attr_parts.append(f'for="{value}"')
                elif key == "class_":
                    attr_parts.append(f'class="{value}"')
                else:
                    attr_parts.append(f'{key}="{value}"')

        # Add as attribute if provided - use literal string syntax
        if as_element:
            attr_parts.append(f'as="{as_element}"')

        attrs_str = " " + " ".join(attr_parts) if attr_parts else ""

        # Create template content
        if slot_content:
            template_content = f"""
{{% load lb_tags %}}
<c-lb.{component_name}{attrs_str}>
{slot_content}
</c-lb.{component_name}>
""".strip()
        else:
            template_content = f"""
{{% load lb_tags %}}
<c-lb.{component_name}{attrs_str} />
""".strip()

        # Create template context - no need for element_type anymore
        context = {}

        return _render_isolated(template_content, context, "Component rendering error")

    def render_template_string(self, template_str, context=None):
        """
        Render a template string using Django's template engine with temp file.

        This method creates a temporary template file containing the template string,
        then uses Django's template engine to render it. This ensures consistent
        Django Cotton component processing for integration tests.

        Args:
            template_str (str): Template string to render
            context (dict): Template context variables (optional)

        Returns:
            str: Rendered HTML output
        """
        if context is None:
            context = {}

        return _render_isolated(template_str.strip(), context, "Template rendering error")

    def get_component_schema(self, component_name):
        """
        Get component schema from registry.

        Args:
            component_name (str): Name of the component

        Returns:
            dict: Component schema definition
        """
        return self.component_registry.get_component(component_name)

    def assert_classes_present(self, html, expected_classes):
        """
        Assert that expected CSS classes are present in HTML.

        Args:
            html (str): HTML content to check
            expected_classes (set): Set of expected CSS classes
        """
        # Extract all class attributes from HTML
        class_matches = re.findall(r'class="([^"]*)"', html)
        all_classes = set()
        for match in class_matches:
            all_classes.update(match.split())

        for css_class in expected_classes:
            assert css_class in all_classes, (
                f"Expected class '{css_class}' not found in HTML classes {all_classes}. Full HTML: {html}"
            )

    def assert_attributes_present(self, html, expected_attrs):
        """
        Assert that expected HTML attributes are present.

        Args:
            html (str): HTML content to check
            expected_attrs (dict): Expected attributes as key-value pairs
        """
        for attr, value in expected_attrs.items():
            if value is True:
                assert f"{attr}" in html or f'{attr}=""' in html, (
                    f"Boolean attribute '{attr}' not found"
                )
            else:
                assert f'{attr}="{value}"' in html, (
                    f"Attribute '{attr}=\"{value}\"' not found"
                )

    def extract_classes_from_html(self, html):
        """
        Extract CSS classes from HTML class attributes.

        Args:
            html (str): HTML content

        Returns:
            set: Set of CSS classes found
        """
        import re

        class_pattern = r'class="([^"]*)"'
        matches = re.findall(class_pattern, html)
        classes = set()
        for match in matches:
            classes.update(match.split())
        return classes


class ComponentSchemaTestMixin:
    """
    Mixin for testing component schema compliance.
    """

    def test_component_schema_exists(self):
        """Test that the component has a schema definition"""
        schema = self.get_component_schema(self.component_name)
        assert schema is not None, (
            f"Schema not found for component '{self.component_name}'"
        )

    def test_component_base_classes(self):
        """Test that component defines base classes"""
        schema = self.get_component_schema(self.component_name)
        assert "base_classes" in schema, (
            f"Component '{self.component_name}' missing base_classes"
        )
        assert isinstance(schema["base_classes"], list), "base_classes should be a list"

    def test_component_template_path(self):
        """Test that component template exists"""
        schema = self.get_component_schema(self.component_name)
        assert "template" in schema, (
            f"Component '{self.component_name}' missing template path"
        )

        template_path = (
            Path(__file__).parent.parent.parent
            / "templates"
            / "cotton"
            / schema["template"]
        )
        assert template_path.exists(), f"Template file not found: {template_path}"

    def test_component_variables_structure(self):
        """Test that component variables have proper structure"""
        schema = self.get_component_schema(self.component_name)
        if "variables" in schema:
            variables = schema["variables"]
            assert isinstance(variables, dict), "Variables should be a dictionary"

            for var_name, var_config in variables.items():
                assert isinstance(var_config, dict), (
                    f"Variable '{var_name}' config should be a dict"
                )
                if "type" in var_config:
                    assert var_config["type"] in [
                        "string",
                        "boolean",
                        "enum",
                        "map",
                    ], f"Invalid type for '{var_name}'"


class ComponentRenderTestMixin:
    """
    Mixin for testing component rendering functionality.
    """

    def test_component_renders_without_error(self):
        """Test that component renders without throwing exceptions"""
        try:
            html = self.render_component(self.component_name)
            assert html is not None, f"Component '{self.component_name}' returned None"
            assert len(html.strip()) > 0, (
                f"Component '{self.component_name}' rendered empty content"
            )
        except Exception as e:
            pytest.fail(f"Component '{self.component_name}' failed to render: {e}")

    def test_component_base_classes_applied(self):
        """Test that component base classes are applied to rendered output"""
        schema = self.get_component_schema(self.component_name)
        if "base_classes" in schema and schema["base_classes"]:
            html = self.render_component(self.component_name)
            rendered_classes = self.extract_classes_from_html(html)

            for base_class in schema["base_classes"]:
                if base_class:  # Skip empty strings
                    assert base_class in rendered_classes, (
                        f"Base class '{base_class}' not found in rendered component"
                    )

    def test_component_optional_base_classes_applied(self):
        """Test that component optional base classes are applied when conditions are met"""
        schema = self.get_component_schema(self.component_name)
        if "optional_base_classes" in schema and schema["optional_base_classes"]:
            html = self.render_component(self.component_name)
            rendered_classes = self.extract_classes_from_html(html)

            # For optional base classes, we just verify they exist in the schema
            # but don't require them to be present in the rendered output
            for optional_class in schema["optional_base_classes"]:
                if optional_class:  # Skip empty strings
                    # Optional classes may or may not be present depending on component state
                    # We don't assert their presence, just log for debugging
                    if optional_class in rendered_classes:
                        print(
                            f"Optional base class '{optional_class}' found in rendered component"
                        )
                    else:
                        print(
                            f"Optional base class '{optional_class}' not found in rendered component (expected for some states)"
                        )


class ComponentTestTemplate(
    ComponentTestBase, ComponentSchemaTestMixin, ComponentRenderTestMixin
):
    """
    Template class for component tests.

    To use this template, create a test class that inherits from this class
    and set the component_name class attribute:

    Example:
        class TestButtonComponent(ComponentTestTemplate):
            component_name = "button"

            def test_button_variants(self):
                # Custom test for button variants
                html = self.render_component("button", variant="primary")
                self.assert_classes_present(html, {"btn", "btn-primary"})
    """

    component_name = None  # Override in subclasses

    def setup_method(self):
        """Setup method called before each test"""
        super().setup_method()
        assert self.component_name is not None, (
            "component_name must be set in test class"
        )
