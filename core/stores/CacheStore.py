import json
from datetime import datetime, timedelta, timezone
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
            self._purge_expired()
        except Exception:
            self._data = {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False)

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def get_valid(self, key: str, ttl_seconds: int) -> Any:
        cached = self._data.get(key)
        if self._is_entry_valid(cached, ttl_seconds):
            return cached.get("data") if isinstance(cached, dict) else cached
        if cached is not None:
            self.delete(key)
        return None

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save()

    def set_with_ttl(self, key: str, data: Any, ttl_seconds: int) -> None:
        entry = self._build_entry(data, ttl_seconds)
        self.set(key, entry)

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
            self._save()

    def all(self) -> dict[str, Any]:
        return dict(self._data)

    def _build_entry(self, data: Any, ttl_seconds: int) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=int(ttl_seconds))
        return {
            "collected_at": int(now.timestamp()),
            "ttl_seconds": int(ttl_seconds),
            "expires_at": int(expires_at.timestamp()),
            "data": data,
        }

    def _is_entry_valid(self, cached: Any, ttl_seconds: int) -> bool:
        if not isinstance(cached, dict):
            return False
        if int(cached.get("ttl_seconds") or 0) != int(ttl_seconds):
            return False
        expires_at = cached.get("expires_at")
        if not isinstance(expires_at, (int, float)):
            return False
        return datetime.now(timezone.utc).timestamp() < float(expires_at)

    def _purge_expired(self) -> None:
        now_ts = datetime.now(timezone.utc).timestamp()
        expired_keys = []
        for key, value in self._data.items():
            if not isinstance(value, dict):
                continue
            expires_at = value.get("expires_at")
            if isinstance(expires_at, (int, float)) and now_ts >= float(expires_at):
                expired_keys.append(key)
        if not expired_keys:
            return
        for key in expired_keys:
            del self._data[key]
        self._save()
