import warnings
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml

from labb.config import LabbConfig, find_config_file, load_config, save_config


def test_labb_config_defaults():
    config = LabbConfig()
    assert config.input_file == "static_src/input.css"
    assert config.output_file == "static/css/output.css"
    assert config.minify is True
    assert config.classes_output == "static_src/labb-classes.txt"
    assert "templates/**/*.html" in config.template_patterns


def test_labb_config_from_dict_new_structure(config_data, temp_dir):
    config = LabbConfig.from_dict(config_data)
    assert config.input_file == str(temp_dir / "static_src" / "input.css")
    assert config.output_file == str(temp_dir / "static" / "css" / "output.css")
    assert config.minify is True
    assert config.classes_output == str(temp_dir / "static_src" / "labb-classes.txt")
    assert config.template_patterns == ["templates/**/*.html", "*/templates/**/*.html"]


def test_labb_config_to_dict():
    config = LabbConfig()
    config.input_file = "test/input.css"
    config.output_file = "test/output.css"

    result = config.to_dict()
    expected = {
        "css": {
            "build": {
                "input": "test/input.css",
                "output": "test/output.css",
                "minify": True,
            },
            "scan": {
                "output": "static_src/labb-classes.txt",
                "templates": [
                    "templates/**/*.html",
                    "*/templates/**/*.html",
                    "**/templates/**/*.html",
                ],
                "apps": {},
            },
        }
    }
    assert result == expected


def test_find_config_file_with_env_var(temp_dir):
    config_file = temp_dir / "custom.yaml"
    config_file.write_text("test: true")

    with patch.dict("os.environ", {"LABB_CONFIG_PATH": str(config_file)}):
        result = find_config_file()
        assert result == config_file


def test_find_config_file_env_var_nonexistent(temp_dir):
    nonexistent = temp_dir / "nonexistent.yaml"

    with patch.dict("os.environ", {"LABB_CONFIG_PATH": str(nonexistent)}):
        result = find_config_file()
        assert result is None


def test_find_config_file_in_directory(temp_dir):
    config_file = temp_dir / "labb.yaml"
    config_file.write_text("test: true")

    result = find_config_file(temp_dir)
    assert result == config_file


def test_find_config_file_yml_extension(temp_dir):
    config_file = temp_dir / "labb.yml"
    config_file.write_text("test: true")

    result = find_config_file(temp_dir)
    assert result == config_file


def test_find_config_file_not_found(temp_dir):
    result = find_config_file(temp_dir)
    assert result is None


def test_load_config_from_file(config_file, temp_dir):
    with patch("labb.config.find_config_file", return_value=config_file):
        config = load_config()
        assert config.input_file == str(temp_dir / "static_src" / "input.css")
        assert config.output_file == str(temp_dir / "static" / "css" / "output.css")


@pytest.mark.filterwarnings("ignore:Could not resolve labb config file path")
def test_load_config_file_not_found():
    with patch("labb.config.find_config_file", return_value=None):
        config = load_config(raise_not_found=False)
        assert isinstance(config, LabbConfig)


def test_load_config_file_not_found_with_warning():
    """Test load_config when file not found and raise_not_found=False"""
    with patch("labb.config.find_config_file", return_value=None):
        with warnings.catch_warnings(record=True) as w:
            config = load_config(raise_not_found=False)

            # Should return default config
            assert isinstance(config, LabbConfig)

            # Should issue a warning
            assert len(w) == 1
            assert "Could not resolve labb config file path" in str(w[0].message)
            assert "Please run 'labb init'" in str(w[0].message)


def test_load_config_yaml_error(temp_dir):
    config_file = temp_dir / "labb.yaml"
    config_file.write_text("invalid: yaml: content:")

    with patch("labb.config.find_config_file", return_value=config_file):
        with pytest.raises(yaml.YAMLError):
            load_config()


def test_save_config(temp_dir, mock_config):
    config_path = temp_dir / "test.yaml"

    result = save_config(mock_config, config_path)
    assert result == config_path
    assert config_path.exists()


def test_save_config_default_path(mock_config):
    with patch("pathlib.Path.cwd", return_value=Path("/test")):
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("yaml.dump") as mock_dump:
                result = save_config(mock_config)
                assert result == Path("/test/labb.yaml")
                mock_file.assert_called_once()
                mock_dump.assert_called_once()


def test_save_config_error(temp_dir, mock_config):
    config_path = temp_dir / "readonly"
    config_path.mkdir()
    config_file = config_path / "labb.yaml"

    # Make the parent directory read-only to trigger an exception
    import os

    os.chmod(config_path, 0o444)  # Read-only directory

    try:
        with pytest.raises(Exception):
            save_config(mock_config, config_file)
    finally:
        # Restore permissions for cleanup
        os.chmod(config_path, 0o755)
