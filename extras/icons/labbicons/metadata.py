import json
from pathlib import Path
from typing import Any, Dict, List


def get_available_packs() -> List[str]:
    """
    Get list of available icon packs by scanning the metadata directory.

    Returns:
        List of pack names (e.g., ['rmx'])
    """
    metadata_dir = Path(__file__).parent / "metadata"
    packs = []

    if metadata_dir.exists():
        for json_file in metadata_dir.glob("*.json"):
            pack_name = json_file.stem
            packs.append(pack_name)

    return sorted(packs)


def load_pack_metadata(pack_name: str) -> Dict[str, Any]:
    """
    Load icon pack metadata from the JSON file and return as a dictionary.

    Args:
        pack_name: Name of the pack (e.g., 'remix' for remix.json)

    Returns:
        Dictionary containing:
        - icons: List of all icons with category info
        - categories: List of category names
        - metadata: General metadata about the icon pack
        - pack_name: Name of the pack
    """
    try:
        # Get the path to the pack's JSON file
        json_path = Path(__file__).parent / "metadata" / f"{pack_name}.json"

        if not json_path.exists():
            return {
                "icons": [],
                "categories": [],
                "metadata": {},
                "pack_name": pack_name,
            }

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Flatten all icons into a single array with category info
        icons = []
        categories = list(data["categories"].keys())

        # Get the pack name from metadata
        pack_name_from_metadata = data["metadata"].get("pack", pack_name)

        for category, category_data in data["categories"].items():
            for icon in category_data["icons"]:
                icons.append(
                    {**icon, "category": category, "pack": pack_name_from_metadata}
                )

        return {
            "icons": icons,
            "categories": categories,
            "metadata": data["metadata"],
            "pack_name": pack_name,
        }

    except Exception as e:
        print(f"Error loading {pack_name} metadata: {e}")
        return {"icons": [], "categories": [], "metadata": {}, "pack_name": pack_name}


def load_all_packs_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Load metadata for all available icon packs.

    Returns:
        Dictionary with pack names as keys and their metadata as values
    """
    packs = get_available_packs()
    all_metadata = {}

    for pack in packs:
        all_metadata[pack] = load_pack_metadata(pack)

    return all_metadata


def load_remix_metadata() -> Dict[str, Any]:
    """
    Load Remix Icons metadata from the JSON file and return as a dictionary.
    This is kept for backward compatibility.

    Returns:
        Dictionary containing:
        - icons: List of all icons with category info
        - categories: List of category names
        - metadata: General metadata about the icon pack
    """
    return load_pack_metadata("remix")


# Convenience function for direct import
def remix() -> Dict[str, Any]:
    """
    Convenience function to get Remix Icons metadata.
    Usage: from labbicons.metadata import remix
    """
    return load_remix_metadata()
