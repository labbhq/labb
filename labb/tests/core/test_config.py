import warnings
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml

from labb.config import (
    BlockSource,
    LabbConfig,
    LabbConfigError,
    find_config_file,
    load_config,
    save_config,
)


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
    config_file = temp_dir / "labb.yaml"

    # chmod 0o444 on a directory doesn't block writes on Windows; mock instead.
    with patch("builtins.open", side_effect=OSError("write failed")):
        with pytest.raises(Exception):
            save_config(mock_config, config_file)


# ---------------------------------------------------------------------------
# blocks: section tests
# ---------------------------------------------------------------------------


def test_blocks_config_absent():
    """Config without blocks: key parses fine; config.blocks is None."""
    config = LabbConfig.from_dict({"css": {}})
    assert config.blocks is None


def test_blocks_config_with_collections_and_sources(temp_dir):
    """Full parse populates collections and sources correctly."""
    data = {
        "blocks": {
            "collections": [
                {"name": "blocks", "path": "./blocks", "default": True},
                {"name": "premium", "path": "./premium-blocks", "default": False},
            ],
            "sources": [
                {"name": "labbhq", "url": "https://github.com/labbhq/blocks"},
                {"name": "local", "path": "./my-custom-blocks"},
            ],
        }
    }
    config = LabbConfig.from_dict(data, config_dir=temp_dir)

    assert config.blocks is not None
    assert len(config.blocks.collections) == 2
    assert len(config.blocks.sources) == 2

    blocks_col = config.blocks.get_collection("blocks")
    assert blocks_col is not None
    assert blocks_col.default is True
    assert blocks_col.path == str((temp_dir / "./blocks").resolve())

    premium_col = config.blocks.get_collection("premium")
    assert premium_col is not None
    assert premium_col.default is False

    labbhq = config.blocks.sources[0]
    assert labbhq.name == "labbhq"
    assert labbhq.url == "https://github.com/labbhq/blocks"
    assert labbhq.path is None

    local = config.blocks.sources[1]
    assert local.name == "local"
    assert local.path == "./my-custom-blocks"
    assert local.url is None


def test_blocks_config_get_default_collection(temp_dir):
    """get_default_collection returns the collection marked default=True."""
    data = {
        "blocks": {
            "collections": [
                {"name": "blocks", "path": "./blocks", "default": True},
                {"name": "premium", "path": "./premium-blocks", "default": False},
            ],
            "sources": [],
        }
    }
    config = LabbConfig.from_dict(data, config_dir=temp_dir)
    default = config.blocks.get_default_collection()
    assert default is not None
    assert default.name == "blocks"


def test_blocks_config_single_collection_is_default(temp_dir):
    """A single collection without default=True is still returned by get_default_collection."""
    data = {
        "blocks": {
            "collections": [
                {"name": "only", "path": "./blocks"},
            ],
            "sources": [],
        }
    }
    config = LabbConfig.from_dict(data, config_dir=temp_dir)
    default = config.blocks.get_default_collection()
    assert default is not None
    assert default.name == "only"


def test_blocks_config_multiple_defaults_raises(temp_dir):
    """Two collections both default=True raises LabbConfigError."""
    data = {
        "blocks": {
            "collections": [
                {"name": "a", "path": "./a", "default": True},
                {"name": "b", "path": "./b", "default": True},
            ],
            "sources": [],
        }
    }
    with pytest.raises(LabbConfigError):
        LabbConfig.from_dict(data, config_dir=temp_dir)


def test_blocks_source_remote_vs_local():
    """Source with url is_remote=True; source with path is_local=True."""
    remote = BlockSource(name="remote", url="https://github.com/example/blocks")
    local = BlockSource(name="local", path="./my-blocks")

    assert remote.is_remote is True
    assert remote.is_local is False

    assert local.is_local is True
    assert local.is_remote is False


def test_blocks_config_round_trip(temp_dir):
    """from_dict → to_dict produces equivalent structure."""
    data = {
        "blocks": {
            "collections": [
                {"name": "blocks", "path": "./blocks", "default": True},
            ],
            "sources": [
                {"name": "labbhq", "url": "https://github.com/labbhq/blocks"},
            ],
        }
    }
    config = LabbConfig.from_dict(data, config_dir=temp_dir)
    result = config.to_dict()

    assert "blocks" in result
    assert len(result["blocks"]["collections"]) == 1
    assert result["blocks"]["collections"][0]["name"] == "blocks"
    assert result["blocks"]["collections"][0]["default"] is True

    assert len(result["blocks"]["sources"]) == 1
    assert result["blocks"]["sources"][0]["name"] == "labbhq"
    assert result["blocks"]["sources"][0]["url"] == "https://github.com/labbhq/blocks"
    assert "path" not in result["blocks"]["sources"][0]
