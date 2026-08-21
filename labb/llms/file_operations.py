"""
File operations for LLM documentation.

This module handles reading and writing of llms.txt files.
"""

from pathlib import Path
from typing import Optional

from labb.llms.generator import generate_llms_txt


def get_llms_txt() -> str:
    """Get the llms.txt content as a string by reading from file."""
    file_path = Path(__file__).parent / "llms.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_llms_txt(output_path: Optional[str] = None) -> str:
    """Generate and write llms.txt file to specified path or default location."""

    if output_path is None:
        # Default to the llms module directory
        output_path = Path(__file__).parent / "llms.txt"
    else:
        output_path = Path(output_path)

    # Generate content
    content = generate_llms_txt()

    # Exactly one trailing newline. The generated body ends with a blank line,
    # which end-of-file-fixer strips on commit; regenerating then put it back,
    # so the two hooks fought each other every run.
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.rstrip("\n") + "\n")

    return str(output_path)
