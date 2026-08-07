import os
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class LabbConfigNotFound(Exception):
    pass


class LabbConfigError(Exception):
    pass


@dataclass
class BlockCollection:
    name: str
    path: str  # resolved to absolute path relative to config file location
    default: bool = False


@dataclass
class BlockSource:
    name: str
    url: Optional[str] = None  # remote git source
    path: Optional[str] = None  # local filesystem source

    subdir: Optional[str] = None

    @property
    def is_remote(self) -> bool:
        return self.url is not None

    @property
    def is_local(self) -> bool:
        return self.path is not None


def _uniq(seq: List[str]) -> List[str]:
    """Order-preserving de-duplication."""
    seen = set()
    out = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


@dataclass
class PackageCss:
    """A package's resolved CSS contributions to a consumer's build.

    Three orthogonal kinds (see the css-pipeline design): `components` are
    scanned for `<c-lb.*>` usage (→ safelist), `literals` are handed to Tailwind
    as `@source` globs, `imports` are package-shipped CSS `@import`ed in.
    """

    components: List[str] = field(default_factory=list)
    literals: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)

    def merged_with(self, other: "PackageCss") -> "PackageCss":
        # De-dup on merge: two selected groups may share an import (e.g. themes)
        # or an overlapping glob; a duplicate import would inline the same CSS
        # (and its @plugin blocks) twice.
        return PackageCss(
            components=_uniq(self.components + other.components),
            literals=_uniq(self.literals + other.literals),
            imports=_uniq(self.imports + other.imports),
        )

    def is_empty(self) -> bool:
        return not (self.components or self.literals or self.imports)


@dataclass
class PackageSpec:
    """A consumer's raw request for a package's CSS, before group resolution.

    One of three forms: named `groups`, `all_groups` (the `all`/blank form), or
    an `explicit` raw dict. Group resolution (importing the package and reading
    its `labb-provides.yaml`) happens in the build/scan layer, not here.
    """

    groups: Optional[List[str]] = None
    all_groups: bool = False
    explicit: Optional[PackageCss] = None


def _parse_package_css(val: Optional[Dict[str, Any]]) -> PackageCss:
    val = val or {}
    return PackageCss(
        components=list(val.get("components") or []),
        literals=list(val.get("literals") or []),
        imports=list(val.get("imports") or []),
    )


def _package_css_to_dict(pc: PackageCss) -> Dict[str, List[str]]:
    d: Dict[str, List[str]] = {}
    if pc.components:
        d["components"] = pc.components
    if pc.literals:
        d["literals"] = pc.literals
    if pc.imports:
        d["imports"] = pc.imports
    return d


def _package_spec_to_yaml(spec: "PackageSpec"):
    """Serialize a PackageSpec back to its labb.yaml form (list / '*' / dict)."""
    if spec.explicit is not None:
        return _package_css_to_dict(spec.explicit)
    if spec.all_groups:
        return "*"
    return list(spec.groups or [])


def _parse_package_spec(val: Any) -> PackageSpec:
    """Parse one `css.packages.{pkg}` value into a PackageSpec.

    Forms: `[group, ...]` (named groups); `"*"` (or the `all` alias, or
    null/empty) for every group; `{components/literals/imports: [...]}` (explicit
    raw dict).
    """
    if val is None:
        return PackageSpec(all_groups=True)
    if isinstance(val, str):
        if val.strip() == "*" or val.strip().lower() == "all":
            return PackageSpec(all_groups=True)
        return PackageSpec(groups=[val])
    if isinstance(val, list):
        return PackageSpec(groups=[str(g) for g in val])
    if isinstance(val, dict):
        return PackageSpec(explicit=_parse_package_css(val))
    raise LabbConfigError(
        f"Invalid css.packages entry: expected a group list, 'all', or a "
        f"components/literals/imports mapping, got {type(val).__name__}"
    )


@dataclass
class BlocksConfig:
    collections: List[BlockCollection] = field(default_factory=list)
    sources: List[BlockSource] = field(default_factory=list)

    def get_default_collection(self) -> Optional[BlockCollection]:
        """Return collection marked default=True, or the only collection if one exists."""
        defaults = [c for c in self.collections if c.default]
        if defaults:
            return defaults[0]
        if len(self.collections) == 1:
            return self.collections[0]
        return None

    def get_collection(self, name: str) -> Optional[BlockCollection]:
        for c in self.collections:
            if c.name == name:
                return c
        return None

    def get_sources(self) -> List[BlockSource]:
        return self.sources


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

    # CSS package contributions (new schema; replaces scan_apps).
    # consumer side: which packages' CSS this project pulls in, pre-resolution.
    packages: Dict[str, PackageSpec] = field(default_factory=dict)
    # package side: named groups THIS package publishes (rare in a consumer config;
    # normally shipped as labb-provides.yaml inside the package).
    provides: Dict[str, PackageCss] = field(default_factory=dict)

    # Blocks settings
    blocks: Optional[BlocksConfig] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], config_dir: Optional[Path] = None
    ) -> "LabbConfig":
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
                # Legacy css.scan.apps — still honoured during the deprecation
                # window (scanner reads config.scan_apps unchanged), warned.
                if scan.get("apps"):
                    config.scan_apps = scan["apps"]
                    warnings.warn(
                        "css.scan.apps is deprecated; migrate to css.packages "
                        "(run a labb build/scan for the guided migration).",
                        DeprecationWarning,
                        stacklevel=2,
                    )

            # CSS package contributions (new schema).
            if "packages" in css:
                for pkg, val in (css["packages"] or {}).items():
                    config.packages[pkg] = _parse_package_spec(val)

            # Package-published groups (this package's own labb-provides.yaml
            # is read separately; this handles an inline `css.provides`).
            if "provides" in css:
                for group, val in (css["provides"] or {}).items():
                    config.provides[group] = _parse_package_css(val)

        if "blocks" in data:
            blocks_data = data["blocks"]
            collections = []
            sources = []

            for entry in blocks_data.get("collections", []):
                raw_path = entry["path"]
                if config_dir is not None:
                    resolved = str((config_dir / raw_path).resolve())
                else:
                    resolved = raw_path
                collections.append(
                    BlockCollection(
                        name=entry["name"],
                        path=resolved,
                        default=entry.get("default", False),
                    )
                )

            defaults = [c for c in collections if c.default]
            if len(defaults) > 1:
                raise LabbConfigError(
                    "Only one block collection may be marked as default=true, "
                    f"but found {len(defaults)}: {[c.name for c in defaults]}"
                )

            for entry in blocks_data.get("sources", []):
                sources.append(
                    BlockSource(
                        name=entry["name"],
                        url=entry.get("url"),
                        path=entry.get("path"),
                        subdir=entry.get("subdir"),
                    )
                )

            config.blocks = BlocksConfig(collections=collections, sources=sources)

        return config

    def to_dict(self) -> Dict[str, Any]:
        css: Dict[str, Any] = {
            "build": {
                "input": self.input_file,
                "output": self.output_file,
                "minify": self.minify,
            },
        }
        if self.packages:
            # New schema: css.packages + a slim scan (templates only; output/apps
            # are legacy and obsolete under the new pipeline).
            css["packages"] = {
                pkg: _package_spec_to_yaml(spec) for pkg, spec in self.packages.items()
            }
            if self.provides:
                css["provides"] = {
                    g: _package_css_to_dict(pc) for g, pc in self.provides.items()
                }
            css["scan"] = {"templates": self.template_patterns}
        else:
            # Legacy shape (no css.packages configured).
            css["scan"] = {
                "output": self.classes_output,
                "templates": self.template_patterns,
                "apps": self.scan_apps,
            }
        result: Dict[str, Any] = {"css": css}

        if self.blocks is not None:
            result["blocks"] = {
                "collections": [
                    {"name": c.name, "path": c.path, "default": c.default}
                    for c in self.blocks.collections
                ],
                "sources": [
                    {
                        k: v
                        for k, v in {
                            "name": s.name,
                            "url": s.url,
                            "path": s.path,
                            "subdir": s.subdir,
                        }.items()
                        if v is not None
                    }
                    for s in self.blocks.sources
                ],
            }

        return result


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
    config_path: Optional[Path] = None,
    raise_not_found: bool = True,
    warn: bool = True,
) -> LabbConfig:
    """Load configuration from file or return defaults. Uses a module-level cache.

    ``warn=False`` silences the fallback warning where a missing config is
    normal (e.g. rendering a component). Ignored when ``raise_not_found=True``.
    """
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
        if warn:
            warnings.warn(message)
        _cached_config = LabbConfig()
        return _cached_config

    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}

    _cached_config = LabbConfig.from_dict(data, config_dir=config_path.parent)
    return _cached_config


def save_config(config: LabbConfig, config_path: Optional[Path] = None) -> Path:
    """Save configuration to file"""
    if config_path is None:
        config_path = Path.cwd() / "labb.yaml"

    with open(config_path, "w") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False, indent=2)

    return config_path
