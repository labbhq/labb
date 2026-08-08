"""Capture a thumbnail for every block in the collection.

    poetry run python scripts/capture_thumbnails.py

Starts the block dev renderer, drives each block's preview URL in a headless
browser, and writes {category}/{slug}/thumbnails/{slug}.{light,dark}.png — the path each
block.yaml already declares, in both labb themes.
"""

import argparse
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests
import yaml
from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BLOCKS = ROOT / (
    yaml.safe_load((ROOT / "blocks.yaml").read_text()).get("blocks_dir") or "."
)
# One viewport for every block, so the gallery grid reads as a set rather than
# 40 unrelated screenshots. Both themes are captured — the gallery serves the one
# matching the reader's theme.
VIEWPORT = {"width": 1280, "height": 800}
THEMES = {"light": "labb-light", "dark": "labb-dark"}
SETTLE_MS = 700  # charts and fonts
MAX_MEAN_DELTA = 1.5


def blocks():
    index = yaml.safe_load((ROOT / "index.yaml").read_text())
    for entry in index.get("blocks", []):
        _vendor, category, slug = entry["ref"].split("/")
        yield category, slug


def available_port():
    """Choose an isolated port so a previous preview never supplies stale images."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_server(base, timeout=40):
    for _ in range(timeout * 2):
        try:
            if requests.get(base, timeout=1).status_code < 500:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.5)
    return False


def images_match(reference, candidate):
    """Accept tiny browser raster differences, reject visible regressions."""
    with (
        Image.open(reference).convert("RGB") as expected,
        Image.open(candidate).convert("RGB") as actual,
    ):
        if expected.size != actual.size:
            return False, f"size changed from {expected.size} to {actual.size}"
        difference = ImageChops.difference(expected, actual)
        mean_delta = max(ImageStat.Stat(difference).mean)
        if mean_delta > MAX_MEAN_DELTA:
            return False, f"mean pixel delta {mean_delta:.2f} exceeds {MAX_MEAN_DELTA}"
    return True, ""


def main(check=False):
    port = available_port()
    base = f"http://127.0.0.1:{port}"
    server = subprocess.Popen(
        ["labb", "block", "dev", "serve", "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_for_server(base):
            print("✗ block dev serve did not come up")
            return 1

        captured, failed = 0, []
        with tempfile.TemporaryDirectory() as temp_dir:
            temporary_root = Path(temp_dir)
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport=VIEWPORT)

                for category, slug in blocks():
                    url = f"{base}/lb/{category}/{slug}/preview/"
                    out_dir = BLOCKS / category / slug / "thumbnails"
                    capture_dir = temporary_root / category / slug if check else out_dir
                    capture_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        resp = page.goto(url, wait_until="networkidle")
                        if resp is None or resp.status >= 400:
                            failed.append(
                                f"{category}/{slug} (HTTP {resp.status if resp else '?'})"
                            )
                            continue
                        for mode, theme in THEMES.items():
                            page.evaluate(
                                "theme => document.documentElement.setAttribute('data-theme', theme)",
                                theme,
                            )
                            page.wait_for_timeout(SETTLE_MS)
                            screenshot = capture_dir / f"{slug}.{mode}.png"
                            page.screenshot(path=str(screenshot))
                            if check:
                                baseline = out_dir / screenshot.name
                                if not baseline.exists():
                                    failed.append(
                                        f"{category}/{slug} ({mode} baseline is missing)"
                                    )
                                else:
                                    matches, detail = images_match(baseline, screenshot)
                                    if not matches:
                                        failed.append(
                                            f"{category}/{slug} ({mode}: {detail})"
                                        )
                        captured += 1
                        print(f"✓ {category}/{slug}")
                    except Exception as e:  # noqa: BLE001 — report and keep going
                        failed.append(f"{category}/{slug} ({type(e).__name__}: {e})")

                browser.close()

        print(f"\n{captured} captured", end="")
        if failed:
            print(f", {len(failed)} failed:")
            for f in failed:
                print(f"  ✗ {f}")
            return 1
        print(".")
        return 0
    finally:
        server.terminate()
        server.wait(timeout=10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare fresh screenshots to committed light and dark baselines",
    )
    sys.exit(main(check=parser.parse_args().check))
