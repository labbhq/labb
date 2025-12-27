from unittest.mock import Mock, patch

from django.contrib.sessions.middleware import SessionMiddleware
from django.template import Context, Template
from django.test import RequestFactory

from labb.shortcuts import DEFAULT_THEME, set_labb_theme
from labb.templatetags.lb_tags import labb_theme, lb_css_path


class TestLbCssPath:
    """Test the lb_css_path template tag"""

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_static_prefix(self, mock_load_config, temp_dir):
        """Test when output path starts with 'static/'"""
        mock_config = Mock()
        # Use a path that starts with "static/" to test the prefix stripping
        mock_config.output_file = "static/css/output.css"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "css/output.css"

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_no_static_prefix(self, mock_load_config):
        """Test when output path doesn't start with 'static/'"""
        mock_config = Mock()
        mock_config.output_file = "assets/css/output.css"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "assets/css/output.css"

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_relative_path(self, mock_load_config):
        """Test with relative path"""
        mock_config = Mock()
        mock_config.output_file = "css/output.css"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "css/output.css"

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_absolute_path(self, mock_load_config):
        """Test with absolute path"""
        mock_config = Mock()
        mock_config.output_file = "/absolute/path/to/css/output.css"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "/absolute/path/to/css/output.css"

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_exception_handling(self, mock_load_config):
        """Test exception handling returns default path"""
        mock_config = Mock()
        mock_config.output_file = None  # This will cause an exception
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "css/output.css"

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_attribute_error(self, mock_load_config):
        """Test handling of AttributeError"""
        mock_config = Mock()
        mock_config.output_file = (
            None  # This will cause an exception when Path() is called
        )
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "css/output.css"

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_path_construction_error(self, mock_load_config, temp_dir):
        """Test handling of Path construction errors"""
        mock_config = Mock()
        # Use a path that starts with "static/" to test the prefix stripping
        mock_config.output_file = "static/css/output.css"
        mock_load_config.return_value = mock_config
        with patch(
            "labb.templatetags.lb_tags.Path", side_effect=Exception("Path error")
        ):
            result = lb_css_path()
            assert result == "css/output.css"

    def test_lb_css_path_in_template(self, temp_dir):
        """Test the template tag in a Django template context"""
        template_string = "{% load lb_tags %}{% lb_css_path %}"
        template = Template(template_string)
        with patch("labb.templatetags.lb_tags.load_config") as mock_load_config:
            mock_config = Mock()
            # Use a path that starts with "static/" to test the prefix stripping
            mock_config.output_file = "static/css/output.css"
            mock_load_config.return_value = mock_config
            context = Context({})
            result = template.render(context)
            assert result == "css/output.css"

    def test_lb_css_path_in_template_with_exception(self):
        """Test the template tag in Django template when exception occurs"""
        template_string = "{% load lb_tags %}{% lb_css_path %}"
        template = Template(template_string)
        with patch("labb.templatetags.lb_tags.load_config") as mock_load_config:
            mock_config = Mock()
            mock_config.output_file = None
            mock_load_config.return_value = mock_config
            context = Context({})
            result = template.render(context)
            assert result == "css/output.css"

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_edge_cases(self, mock_load_config, temp_dir):
        """Test various edge cases for the template tag"""
        mock_config = Mock()
        # Test empty string
        mock_config.output_file = ""
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "."
        # Test just "static"
        mock_config.output_file = "static"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "static"
        # Test "static/" (just the prefix)
        mock_config.output_file = "static/"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "static"
        # Test with multiple static prefixes - use a path that starts with "static/"
        mock_config.output_file = "static/static/css/output.css"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "static/css/output.css"
        # Test with different case - use a path that starts with "Static/"
        mock_config.output_file = "Static/css/output.css"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "Static/css/output.css"

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_with_spaces(self, mock_load_config, temp_dir):
        """Test handling of paths with spaces"""
        mock_config = Mock()
        # Use a path that starts with "static/" to test the prefix stripping
        mock_config.output_file = "static/css/my output.css"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "css/my output.css"

    @patch("labb.templatetags.lb_tags.load_config")
    def test_lb_css_path_with_special_characters(self, mock_load_config, temp_dir):
        """Test handling of paths with special characters"""
        mock_config = Mock()
        # Use a path that starts with "static/" to test the prefix stripping
        mock_config.output_file = "static/css/output-v1.2.3.css"
        mock_load_config.return_value = mock_config
        result = lb_css_path()
        assert result == "css/output-v1.2.3.css"


class TestLbTags:
    """Test labb template tags."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()

    def _get_request_with_session(self):
        """Helper to create a request with session middleware."""
        request = self.factory.get("/")
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_labb_theme_tag_with_request(self):
        """Test labb_theme tag with request context."""
        request = self._get_request_with_session()
        context = {"request": request}

        # Test default theme
        theme = labb_theme(context)
        assert theme == f'data-theme="{DEFAULT_THEME}"'

        # Test custom theme
        set_labb_theme(request, "labb-dark")
        theme = labb_theme(context)
        assert theme == 'data-theme="labb-dark"'

    def test_labb_theme_tag_without_request(self):
        """Test labb_theme tag without request context."""
        context = {}

        theme = labb_theme(context)
        assert theme == 'data-theme="labb-light"'  # fallback default

    def test_labb_theme_tag_in_template(self):
        """Test labb_theme tag in a template."""
        request = self._get_request_with_session()
        set_labb_theme(request, "labb-dark")

        template = Template("{% load lb_tags %}{% labb_theme as theme %}{{ theme }}")
        context = Context({"request": request})

        result = template.render(context)
        assert result == "data-theme=&quot;labb-dark&quot;"

    def test_labb_theme_tag_fallback(self):
        """Test labb_theme tag fallback when no request."""
        template = Template("{% load lb_tags %}{% labb_theme as theme %}{{ theme }}")
        context = Context({})

        result = template.render(context)
        assert result == "data-theme=&quot;labb-light&quot;"
