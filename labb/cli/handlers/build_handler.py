import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from labb.cli.handlers.commons import confirm_load_config

console = Console()


def build_css(
    watch: bool = False,
    scan: bool = False,
    minify: Optional[bool] = None,
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
):
    console.print("[bold blue]🔨 Building CSS...[/bold blue]")
    config = confirm_load_config(console)

    input_path = input_file or config.input_file
    output_path = output_file or config.output_file
    should_minify = minify if minify is not None else config.minify

    input_path_obj = Path(input_path)
    output_path_obj = Path(output_path)

    if not input_path_obj.exists():
        console.print(f"[red]❌ Input CSS file not found: {input_path}[/red]")
        console.print(
            "[yellow]💡 Run 'labb setup' to create the required files[/yellow]"
        )
        sys.exit(1)

    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Handle different scan/build combinations
    if scan and not watch:
        # Scan before building (one-time scan, then build)
        console.print("[blue]🔍 Scanning templates...[/blue]")
        from .scan_handler import scan_templates

        scan_templates(
            watch=False,
            output=config.classes_output,
            patterns=",".join(config.template_patterns),
            verbose=False,
        )
        console.print("[green]✅ Scan complete[/green]")
        _run_build_process(input_path, output_path, should_minify, watch=False)
    elif watch:
        # Run watch mode (with or without scan thread)
        _run_concurrent_build_and_scan(
            input_path, output_path, should_minify, config, scan=scan
        )
    else:
        # Just build (no watch, no scan)
        _run_build_process(input_path, output_path, should_minify, watch=False)


def _run_concurrent_build_and_scan(
    input_path: str, output_path: str, should_minify: bool, config, scan: bool = True
):
    mode = "CSS + scan" if scan else "CSS only"
    console.print(f"[green]🚀 Watch mode ({mode})[/green]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")

    # Create stop event for coordinating threads
    stop_event = threading.Event()

    # Start CSS build watcher in a thread
    build_thread = threading.Thread(
        target=_run_build_watcher,
        args=(input_path, output_path, should_minify, stop_event),
        daemon=True,
    )

    # Start template scanner in a thread (only if scan is True)
    scan_thread = None
    if scan:
        scan_thread = threading.Thread(
            target=_run_scan_watcher,
            args=(
                config.template_patterns,
                config.classes_output,
                stop_event,
                config.scan_apps,
            ),
            daemon=True,
        )

    try:
        build_thread.start()
        if scan_thread:
            time.sleep(0.5)  # Small delay to let build start first
            scan_thread.start()

        # Keep main thread alive and handle Ctrl+C
        while build_thread.is_alive() or (scan_thread and scan_thread.is_alive()):
            time.sleep(0.1)

    except KeyboardInterrupt:
        console.print("[yellow]⏹️  Stopping...[/yellow]")
        stop_event.set()

        # Wait for threads to finish
        if build_thread.is_alive():
            build_thread.join(timeout=2)
        if scan_thread and scan_thread.is_alive():
            scan_thread.join(timeout=2)

        console.print("[yellow]👋 Stopped[/yellow]")
        sys.exit(0)


def _run_build_watcher(
    input_path: str, output_path: str, should_minify: bool, stop_event: threading.Event
):
    """Run CSS build watcher in a thread"""
    cmd = ["npx", "@tailwindcss/cli", "-i", input_path, "-o", output_path, "--watch"]

    if should_minify:
        cmd.append("--minify")

    try:
        console.print("[cyan]🎨 CSS watcher started[/cyan]")
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        while not stop_event.is_set() and process.poll() is None:
            time.sleep(0.1)

        if process.poll() is None:
            process.terminate()
            process.wait()

    except Exception as e:
        if not stop_event.is_set():
            console.print(f"[red]❌ CSS watcher error: {e}[/red]")


def _run_scan_watcher(
    template_patterns: list,
    output_path: str,
    stop_event: threading.Event,
    scan_apps: dict = None,
):
    """Run template scanner watcher in a thread"""
    try:
        from .scan_handler import _watch_and_scan_with_stop_event_live

        console.print("[magenta]🔍 Template Scanner started[/magenta]")
        _watch_and_scan_with_stop_event_live(
            template_patterns, output_path, False, stop_event, scan_apps=scan_apps
        )
    except Exception as e:
        if not stop_event.is_set():
            console.print(f"[red]❌ Template scanner error: {e}[/red]")


def _run_build_process(
    input_path: str, output_path: str, should_minify: bool, watch: bool
):
    """Run the regular build process"""

    # Build Tailwind command
    cmd = [
        "npx",
        "@tailwindcss/cli",
        "-i",
        input_path,
        "-o",
        output_path,
    ]

    # Add flags
    if should_minify:
        cmd.append("--minify")

    if watch:
        cmd.append("--watch")
        console.print("[green]👀 Watching for changes...[/green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")

    # Display build info
    info_text = Text()
    info_text.append("Build Configuration:\n", style="bold")
    info_text.append(f"Input:  {input_path}\n", style="cyan")
    info_text.append(f"Output: {output_path}\n", style="green")
    info_text.append(f"Minify: {'Yes' if should_minify else 'No'}\n", style="yellow")
    info_text.append(f"Watch:  {'Yes' if watch else 'No'}", style="magenta")

    console.print(Panel(info_text, title="CSS Build", border_style="blue"))

    try:
        # Check if npx is available
        subprocess.run(["npx", "--version"], check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print(
            "[red]❌ npx is not available. Please install Node.js and npm[/red]"
        )
        console.print(
            "[yellow]💡 Visit https://nodejs.org/ to install Node.js[/yellow]"
        )
        sys.exit(1)

    try:
        # Execute the build command
        console.print(f"\n[dim]Running: {' '.join(cmd)}[/dim]")

        if watch:
            # For watch mode, run in foreground and handle Ctrl+C
            try:
                subprocess.run(cmd, check=True)
            except KeyboardInterrupt:
                console.print("\n[yellow]⏹️  Build watch stopped[/yellow]")
                sys.exit(0)
        else:
            # For one-time build, capture output
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            if result.returncode == 0:
                console.print("[green]✅ CSS built successfully![/green]")
                console.print(f"[green]📁 Output: {output_path}[/green]")

                # Show file size if possible
                try:
                    output_path_obj = Path(output_path)
                    size = output_path_obj.stat().st_size
                    size_kb = size / 1024
                    console.print(f"[dim]📊 File size: {size_kb:.1f} KB[/dim]")
                except Exception:
                    pass
            else:
                console.print("[yellow]⚠️  Build completed with warnings[/yellow]")
                if result.stderr:
                    console.print(f"[yellow]{result.stderr}[/yellow]")

    except subprocess.CalledProcessError as e:
        console.print("[red]❌ Build failed![/red]")
        if e.stderr:
            console.print(f"[red]{e.stderr}[/red]")
        if e.stdout:
            console.print(f"[yellow]{e.stdout}[/yellow]")

        # Provide helpful error messages
        if "tailwindcss" in str(e):
            console.print("\n[yellow]💡 Troubleshooting:[/yellow]")
            console.print(
                "[yellow]   • Make sure Tailwind CSS is installed: npm install -D tailwindcss @tailwindcss/cli[/yellow]"
            )
            console.print(
                "[yellow]   • Run 'labb setup' to install dependencies[/yellow]"
            )

        sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)
