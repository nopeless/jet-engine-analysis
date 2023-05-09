import json
import os
import re

from typing import Any

Js = dict[str, Any]


def normalize_filename(filename: str) -> str:
    """
    Replace all [^a-zA-Z0-9_] with _
    """
    return re.sub(r"[^a-zA-Z0-9_]", "_", filename)


def enumerate_files(path: str) -> list[str]:
    """
    Enumerate all files in a directory
    """
    return os.listdir(path)


def get_filename_without_extension(path: str) -> str:
    """
    Get filename without extension
    """
    return os.path.splitext(path)[0]


def load_files(folder: str) -> dict[str, Js]:
    """
    Load all files in a folder
    """
    return {
        normalize_filename(get_filename_without_extension(filename)): json.load(
            open(os.path.join(folder, filename), encoding="utf8")
        )
        for filename in enumerate_files(folder)
    }


if __name__ == "__main__":
    files = load_files("data")
    print(f"Found {len(files)} files")
    print(f"Names: {', '.join(files.keys())}")

__all__ = ["load_files"]
