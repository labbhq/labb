"""Capture a thumbnail for every block in the collection.

    poetry run python scripts/capture_thumbnails.py

Starts the block dev renderer, drives each block's preview URL in a headless
browser, and writes {category}/{slug}/thumbnails/{slug}.{light,dark}.png — the path each
block.yaml already declares, in both labb themes.
"""

import subprocess
import sys
import time
from pathlib import Path

import requests
import yaml
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BLOCKS = ROOT / (yaml.safe_load((ROOT / "blocks.yaml").read_text()).get("blocks_dir") or ".")
PORT = 8791
BASE = f"http://127.0.0.1:{PORT}"

# One viewport for every block, so the gallery grid reads as a set rather than
# 40 unrelated screenshots. Both themes are captured — the gallery serves the one
# matching the reader's theme.
VIEWPORT = {"width": 1280, "height": 800}
THEMES = {"light": "labb-light", "dark": "labb-dark"}
SETTLE_MS = 700  # charts and fonts


def blocks():
    index = yaml.safe_load((ROOT / "index.yaml").read_text())
    for entry in index.get("blocks", []):
        _vendor, category, slug = entry["ref"].split("/")
        yield category, slug


def wait_for_server(timeout=40):
    for _ in range(timeout * 2):
        try:
            if requests.get(BASE, timeout=1).status_code < 500:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.5)
    return False


def main():
    server = subprocess.Popen(
        ["labb", "block", "dev", "serve", "--port", str(PORT)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_for_server():
            print("✗ block dev serve did not come up")
            return 1

        captured, failed = 0, []
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport=VIEWPORT)

            for category, slug in blocks():
                url = f"{BASE}/lb/{category}/{slug}/preview/"
                out_dir = BLOCKS / category / slug / "thumbnails"
                out_dir.mkdir(parents=True, exist_ok=True)
                try:
                    resp = page.goto(url, wait_until="networkidle")
                    if resp is None or resp.status >= 400:
                        failed.append(f"{category}/{slug} (HTTP {resp.status if resp else '?'})")
                        continue
                    for mode, theme in THEMES.items():
                        page.evaluate(
                            "theme => document.documentElement.setAttribute('data-theme', theme)",
                            theme,
                        )
                        page.wait_for_timeout(SETTLE_MS)
                        page.screenshot(path=str(out_dir / f"{slug}.{mode}.png"))
                    captured += 1
                    print(f"✓ {category}/{slug}")
                except Exception as e:  # noqa: BLE001 — report and keep going
                    failed.append(f"{category}/{slug} ({type(e).__name__})")

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
    sys.exit(main())
