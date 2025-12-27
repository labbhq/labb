#!/usr/bin/env python3
"""
Simple version management script for the labb project.
Updates version in all pyproject.toml files and __init__.py files.
"""

import argparse
import re
from pathlib import Path


def update_pyproject_version(file_path: Path, new_version: str) -> bool:
    """Update version in a pyproject.toml file."""
    try:
        content = file_path.read_text()

        # Pattern to match version line in pyproject.toml
        version_pattern = r'^version\s*=\s*["\']([^"\']+)["\']'

        def replace_version(match):
            return f'version = "{new_version}"'

        new_content = re.sub(
            version_pattern, replace_version, content, flags=re.MULTILINE
        )

        if new_content != content:
            file_path.write_text(new_content)
            print(f"✅ Updated {file_path} to version {new_version}")
            return True
        else:
            print(f"⚠️  No version found in {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def update_init_version(file_path: Path, new_version: str) -> bool:
    """Update version in an __init__.py file."""
    try:
        content = file_path.read_text()

        # Pattern to match __version__ line
        version_pattern = r'^__version__\s*=\s*["\']([^"\']+)["\']'

        def replace_version(match):
            return f'__version__ = "{new_version}"'

        new_content = re.sub(
            version_pattern, replace_version, content, flags=re.MULTILINE
        )

        if new_content != content:
            file_path.write_text(new_content)
            print(f"✅ Updated {file_path} to version {new_version}")
            return True
        else:
            # If no __version__ found, add it
            if content.strip():
                new_content = content.rstrip() + f'\n\n__version__ = "{new_version}"\n'
            else:
                new_content = f'__version__ = "{new_version}"\n'

            file_path.write_text(new_content)
            print(f"✅ Added version {new_version} to {file_path}")
            return True

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def get_current_version(pyproject_path: Path) -> str:
    """Get current version from main pyproject.toml."""
    try:
        content = pyproject_path.read_text()
        match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        return match.group(1) if match else "unknown"
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(description="Manage version across labb project")
    parser.add_argument("version", help="New version (e.g., 0.1.1, 0.2.0a1)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )

    args = parser.parse_args()

    # Get project root (assuming script is in scripts/ directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Define all files to update
    files_to_update = [
        # Main project
        project_root / "pyproject.toml",
        project_root / "labb" / "__init__.py",
        # Docs package
        project_root / "docs" / "pyproject.toml",
        project_root / "docs" / "labbdocs" / "__init__.py",
        # Icons package
        project_root / "extras" / "icons" / "pyproject.toml",
        project_root / "extras" / "icons" / "labbicons" / "__init__.py",
    ]

    # Get current version
    current_version = get_current_version(project_root / "pyproject.toml")

    print(f"🔄 Updating version from {current_version} to {args.version}")
    print(f"📁 Project root: {project_root}")

    if args.dry_run:
        print("\n🔍 DRY RUN - No files will be modified")
        for file_path in files_to_update:
            if file_path.exists():
                print(f"  Would update: {file_path}")
            else:
                print(f"  Missing: {file_path}")
        return

    # Update files
    updated_count = 0
    for file_path in files_to_update:
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        if file_path.name == "pyproject.toml":
            if update_pyproject_version(file_path, args.version):
                updated_count += 1
        elif file_path.name == "__init__.py":
            if update_init_version(file_path, args.version):
                updated_count += 1

    print(f"\n🎉 Successfully updated {updated_count} files to version {args.version}")

    print("\n💡 Next steps:")
    print("  1. Review the changes: git diff")
    print(
        f"  2. Commit the changes: git add . && git commit -m 'Bump version to {args.version}'"
    )
    print("  3. Push to main branch to trigger release")


if __name__ == "__main__":
    main()
