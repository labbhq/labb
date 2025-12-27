import os
from pathlib import Path
from typing import Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from labb.config import LabbConfig, LabbConfigNotFound, find_config_file, load_config

console = Console()


def show_config(
    show_metadata: bool = False,
    config_path: Optional[str] = None,
):
    """Display current labb configuration in YAML format"""

    console.print("\n[bold blue]🔧 Labb Configuration[/bold blue]")

    # Try to load config and get metadata
    config, metadata = _load_config_with_metadata(config_path)

    # Show raw YAML configuration
    _show_raw_config(metadata.get("config_path"), config)

    # Show metadata below config if requested or if there are important details
    if show_metadata or metadata.get("from_env") or metadata.get("warnings"):
        _show_config_metadata(metadata)


def _load_config_with_metadata(config_path: Optional[str] = None):
    """Load config and gather metadata about the configuration source"""
    metadata = {
        "config_path": None,
        "config_exists": False,
        "from_env": False,
        "warnings": [],
        "env_vars_used": [],
    }

    # Check for environment variable override
    if "LABB_CONFIG_PATH" in os.environ:
        metadata["from_env"] = True
        metadata["env_vars_used"].append("LABB_CONFIG_PATH")

    # Find config file
    if config_path:
        config_file_path = Path(config_path)
    else:
        config_file_path = find_config_file()

    if config_file_path and config_file_path.exists():
        metadata["config_path"] = str(config_file_path)
        metadata["config_exists"] = True
    else:
        metadata["warnings"].append("No configuration file found - using defaults")

    # Load the actual config
    try:
        if config_path:
            config = load_config(Path(config_path), raise_not_found=True)
        else:
            config = load_config(raise_not_found=False)
    except LabbConfigNotFound:
        config = LabbConfig()
        metadata["warnings"].append("Configuration file not found - using defaults")
    except Exception as e:
        config = LabbConfig()
        metadata["warnings"].append(f"Error loading configuration: {e}")

    return config, metadata


def _show_config_metadata(metadata):
    """Display configuration metadata"""

    # Create metadata info
    info_text = Text()
    info_text.append("Configuration Source:\n", style="bold")

    if metadata.get("config_path"):
        info_text.append(f"📁 File: {metadata['config_path']}\n", style="green")
    else:
        info_text.append("📁 File: Not found (using defaults)\n", style="yellow")

    if metadata.get("from_env"):
        info_text.append(
            "🌍 Path set via LABB_CONFIG_PATH environment variable\n", style="cyan"
        )

    if metadata.get("env_vars_used"):
        info_text.append("🔧 Environment variables affecting config:\n", style="blue")
        for env_var in metadata["env_vars_used"]:
            value = os.environ.get(env_var, "")
            info_text.append(f"   • {env_var}={value}\n", style="dim")

    if metadata.get("warnings"):
        info_text.append("\n⚠️  Warnings:\n", style="yellow")
        for warning in metadata["warnings"]:
            info_text.append(f"   • {warning}\n", style="yellow")

    console.print(Panel(info_text, title="Configuration Metadata", border_style="blue"))


def _show_raw_config(config_path: Optional[str], config: LabbConfig):
    """Display raw YAML configuration file or effective configuration"""

    if config_path and Path(config_path).exists():
        # Show actual config file
        try:
            with open(config_path, "r") as f:
                yaml_content = f.read()

            syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
            console.print(
                Panel(
                    syntax,
                    title=f"Configuration File: {config_path}",
                    border_style="green",
                )
            )

        except Exception as e:
            console.print(f"[red]❌ Error reading configuration file: {e}[/red]")
            _show_effective_config(config)
    else:
        # Show effective configuration (defaults)
        console.print(
            "\n[yellow]⚠️  No configuration file found - showing effective configuration (defaults)[/yellow]"
        )
        _show_effective_config(config)


def _show_effective_config(config: LabbConfig):
    """Display the effective configuration as YAML"""

    # Convert config to dict for YAML display
    config_dict = {
        "css": {
            "build": {
                "input": config.input_file,
                "output": config.output_file,
                "minify": config.minify,
            },
            "scan": {
                "classes_output": config.classes_output,
                "template_patterns": config.template_patterns,
            },
        }
    }

    try:
        yaml_content = yaml.dump(config_dict, default_flow_style=False, indent=2)
        syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
        console.print(
            Panel(syntax, title="Effective Configuration", border_style="blue")
        )

    except Exception as e:
        console.print(f"[red]❌ Error generating configuration YAML: {e}[/red]")


def validate_config(config_path: Optional[str] = None):
    """Validate the current configuration and report any issues"""

    console.print("\n[bold blue]🔍 Validating Configuration[/bold blue]")

    config, metadata = _load_config_with_metadata(config_path)
    issues = []

    # Check if files exist
    input_path = Path(config.input_file)
    if not input_path.exists():
        issues.append(f"❌ Input CSS file does not exist: {config.input_file}")
    else:
        console.print(f"[green]✅ Input CSS file found: {config.input_file}[/green]")

    # Check if output directory exists
    output_path = Path(config.output_file)
    if not output_path.parent.exists():
        issues.append(f"⚠️  Output directory does not exist: {output_path.parent}")
    else:
        console.print(
            f"[green]✅ Output directory exists: {output_path.parent}[/green]"
        )

    # Check if classes output directory exists
    classes_path = Path(config.classes_output)
    if not classes_path.parent.exists():
        issues.append(
            f"⚠️  Classes output directory does not exist: {classes_path.parent}"
        )
    else:
        console.print(
            f"[green]✅ Classes output directory exists: {classes_path.parent}[/green]"
        )

    # Check template patterns
    template_files_found = 0
    for pattern in config.template_patterns:
        import glob

        files = glob.glob(pattern, recursive=True)
        html_files = [f for f in files if f.endswith(".html")]
        template_files_found += len(html_files)

    if template_files_found == 0:
        issues.append(
            "⚠️  No HTML template files found matching the configured patterns"
        )
    else:
        console.print(f"[green]✅ Found {template_files_found} template files[/green]")

    # Report issues
    if issues:
        console.print("\n[yellow]Issues found:[/yellow]")
        for issue in issues:
            console.print(f"  {issue}")
    else:
        console.print("\n[green]🎉 Configuration looks good![/green]")

    # Show next steps
    if issues:
        console.print("\n[bold blue]💡 Suggested actions:[/bold blue]")
        console.print("  • Run 'labb setup' to create missing files and directories")
        console.print("  • Run 'labb init' to create a new configuration file")


def edit_config(config_path: Optional[str] = None):
    """Open configuration file in default editor"""

    # Find config file
    if config_path:
        config_file_path = Path(config_path)
    else:
        config_file_path = find_config_file()

    if not config_file_path or not config_file_path.exists():
        console.print("[yellow]⚠️  No configuration file found[/yellow]")
        console.print("[dim]Run 'labb init' to create a configuration file[/dim]")
        return

    # Try to open in editor
    import subprocess
    import sys

    try:
        if sys.platform.startswith("darwin"):  # macOS
            subprocess.run(["open", str(config_file_path)])
        elif sys.platform.startswith("win"):  # Windows
            subprocess.run(["notepad", str(config_file_path)])
        else:  # Linux and others
            # Try common editors
            editors = ["code", "nano", "vim", "gedit"]
            for editor in editors:
                try:
                    subprocess.run([editor, str(config_file_path)])
                    break
                except FileNotFoundError:
                    continue
            else:
                console.print(
                    f"[yellow]Please manually edit: {config_file_path}[/yellow]"
                )
                return

        console.print(f"[green]✅ Opened {config_file_path} in editor[/green]")

    except Exception as e:
        console.print(f"[red]❌ Error opening editor: {e}[/red]")
        console.print(f"[yellow]Please manually edit: {config_file_path}[/yellow]")
