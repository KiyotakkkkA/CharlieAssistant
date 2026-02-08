from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CacheStore:
    def __init__(self, cache_path: str | None = None) -> None:
        base = Path(__file__).resolve().parents[2]
        self._path = Path(cache_path) if cache_path else base / "data" / "cache" / "cache.json"
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        try:
            if not self._path.exists():
                self._data = {}
                return
            raw = self._path.read_text(encoding="utf-8")
            obj = json.loads(raw) if raw.strip() else {}
            self._data = obj if isinstance(obj, dict) else {}
        except Exception:
            self._data = {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False)

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save()

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
            self._save()

    def all(self) -> dict[str, Any]:
        return dict(self._data)
