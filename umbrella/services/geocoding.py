from __future__ import annotations

from dataclasses import dataclass

from umbrella.services.http import get_json


@dataclass(frozen=True)
class CityHit:
    name: str
    country: str | None
    admin1: str | None
    lat: float
    lon: float

    @property
    def display_name(self) -> str:
        parts = [self.name]
        if self.admin1:
            parts.append(self.admin1)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


class OpenMeteoGeocoding:
    BASE = "https://geocoding-api.open-meteo.com/v1/search"

    def search(self, name: str, lang: str = "ru", count: int = 8) -> list[CityHit]:
        name = (name or "").strip()
        if len(name) < 2:
            return []
        data = get_json(
            self.BASE,
            params={"name": name, "count": count, "language": lang, "format": "json"},
        )
        results = data.get("results") or []
        hits: list[CityHit] = []
        for r in results:
            try:
                hits.append(
                    CityHit(
                        name=str(r.get("name", "")),
                        country=r.get("country", None),
                        admin1=r.get("admin1", None),
                        lat=float(r["latitude"]),
                        lon=float(r["longitude"]),
                    )
                )
            except Exception:
                continue
        return hits

