from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_bundle_root() -> Path:
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[2]


def get_app_root() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def ensure_app_directories() -> dict[str, Path]:
    app_root = get_app_root()
    music_dir = app_root / "music"
    cache_dir = app_root / "model-cache"
    music_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return {
        "app_root": app_root,
        "bundle_root": get_bundle_root(),
        "music_dir": music_dir,
        "cache_dir": cache_dir,
    }
