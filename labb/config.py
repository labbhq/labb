import os
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class LabbConfigNotFound(Exception):
    pass


@dataclass
class LabbConfig:
    """Configuration class for labb"""

    # CSS Build settings
    input_file: str = "static_src/input.css"
    output_file: str = "static/css/output.css"
    minify: bool = True

    # CSS Scan settings
    classes_output: str = "static_src/labb-classes.txt"
    template_patterns: List[str] = field(
        default_factory=lambda: [
            "templates/**/*.html",
            "*/templates/**/*.html",
            "**/templates/**/*.html",
        ]
    )
    scan_apps: Dict[str, List[str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LabbConfig":
        """Create LabbConfig from dictionary data"""
        config = cls()

        if "css" in data:
            css = data["css"]

            # CSS Build settings
            if "build" in css:
                build = css["build"]
                config.input_file = build.get("input", config.input_file)
                config.output_file = build.get("output", config.output_file)
                config.minify = build.get("minify", config.minify)

            # CSS Scan settings
            if "scan" in css:
                scan = css["scan"]
                config.classes_output = scan.get("output", config.classes_output)
                config.template_patterns = scan.get(
                    "templates", config.template_patterns
                )
                config.scan_apps = scan.get("apps", config.scan_apps)

        return config

    def to_dict(self) -> Dict[str, Any]:
        return {
            "css": {
                "build": {
                    "input": self.input_file,
                    "output": self.output_file,
                    "minify": self.minify,
                },
                "scan": {
                    "output": self.classes_output,
                    "templates": self.template_patterns,
                    "apps": self.scan_apps,
                },
            },
        }


def find_config_file(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Find labb configuration file using LABB_CONFIG_PATH or current directory"""
    # Check for LABB_CONFIG_PATH environment variable first
    if "LABB_CONFIG_PATH" in os.environ:
        config_path = Path(os.environ["LABB_CONFIG_PATH"])
        if config_path.exists():
            return config_path

    # Fallback to current directory search
    if start_dir is None:
        start_dir = Path.cwd()

    config_names = ["labb.yaml", "labb.yml"]

    # Search only in current directory
    for config_name in config_names:
        config_path = start_dir / config_name
        if config_path.exists():
            return config_path

    return None


_cached_config: Optional[LabbConfig] = None


def clear_config_cache():
    """Clear the cached config (for testing or reload)."""
    global _cached_config
    _cached_config = None


def load_config(
    config_path: Optional[Path] = None, raise_not_found: bool = True
) -> LabbConfig:
    """Load configuration from file or return defaults. Uses a module-level cache."""
    global _cached_config
    if _cached_config is not None:
        return _cached_config

    if config_path is None:
        config_path = find_config_file()

    if config_path is None or not config_path.exists():
        message = (
            "Could not resolve labb config file path. Please run"
            " 'labb init' to create a new configuration file."
        )
        if raise_not_found:
            raise LabbConfigNotFound(message)
        warnings.warn(message)
        _cached_config = LabbConfig()
        return _cached_config

    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}

    _cached_config = LabbConfig.from_dict(data)
    return _cached_config


def save_config(config: LabbConfig, config_path: Optional[Path] = None) -> Path:
    """Save configuration to file"""
    if config_path is None:
        config_path = Path.cwd() / "labb.yaml"

    with open(config_path, "w") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False, indent=2)

    return config_path
