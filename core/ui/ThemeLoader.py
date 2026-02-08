from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from core.ui.css import CSSTemplate


_REQUIRED_KEYS = [
    "WACCENT",
    "WTEXT",
    "WTEXT_WEAK",
    "WTEXT_MUTED",
    "WSECONDARY",
    "WPRIMARY",
    "WPRIMARY_DARK",
    "WPRIMARY_DARKER",
    "WPRIMARY_DARKEST",
]


def _themes_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "data" / "themes"


def list_theme_ids() -> List[str]:
    d = _themes_dir()
    if not d.exists():
        return []
    return sorted([p.stem for p in d.glob("*.json") if p.is_file()])


def load_theme(theme_id: str) -> CSSTemplate:
    d = _themes_dir()
    path = d / f"{theme_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Theme not found: {theme_id}")

    data: Dict[str, str]
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
        data = obj if isinstance(obj, dict) else {}

    missing = [k for k in _REQUIRED_KEYS if not isinstance(data.get(k), str) or not str(data.get(k)).strip()]
    if missing:
        raise ValueError(f"Theme '{theme_id}' missing keys: {', '.join(missing)}")

    return CSSTemplate(
        WACCENT=str(data["WACCENT"]),
        WTEXT=str(data["WTEXT"]),
        WTEXT_WEAK=str(data["WTEXT_WEAK"]),
        WTEXT_MUTED=str(data["WTEXT_MUTED"]),
        WSECONDARY=str(data["WSECONDARY"]),
        WPRIMARY=str(data["WPRIMARY"]),
        WPRIMARY_DARK=str(data["WPRIMARY_DARK"]),
        WPRIMARY_DARKER=str(data["WPRIMARY_DARKER"]),
        WPRIMARY_DARKEST=str(data["WPRIMARY_DARKEST"]),
    )
