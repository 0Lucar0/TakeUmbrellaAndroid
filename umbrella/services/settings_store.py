from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class City:
    name: str = ""
    lat: float | None = None
    lon: float | None = None


@dataclass
class Settings:
    onboarding_done: bool = False
    lang: str = "ru"  # "ru" | "en" | "auto" handled by app on first run

    notifications_enabled: bool = True
    notify_hour: int = 7
    notify_minute: int = 0
    rain_threshold_pct: int = 30

    theme: str = "auto"  # "auto" | "light" | "dark"
    city: City = field(default_factory=City)


class SettingsStore:
    def __init__(self, path: Path):
        self._path = path
        self._settings = Settings()

    @property
    def settings(self) -> Settings:
        return self._settings

    def load(self) -> Settings:
        if not self._path.exists():
            self._settings = Settings()
            return self._settings
        data = json.loads(self._path.read_text(encoding="utf-8"))
        self._settings = _from_json(data)
        return self._settings

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = _to_json(self._settings)
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _to_json(s: Settings) -> dict[str, Any]:
    d = asdict(s)
    return d


def _from_json(d: dict[str, Any]) -> Settings:
    city_d = d.get("city") or {}
    city = City(
        name=str(city_d.get("name", "")),
        lat=city_d.get("lat", None),
        lon=city_d.get("lon", None),
    )
    return Settings(
        onboarding_done=bool(d.get("onboarding_done", False)),
        lang=str(d.get("lang", "ru")),
        notifications_enabled=bool(d.get("notifications_enabled", True)),
        notify_hour=int(d.get("notify_hour", 7)),
        notify_minute=int(d.get("notify_minute", 0)),
        rain_threshold_pct=30,
        theme=str(d.get("theme", "auto")),
        city=city,
    )

