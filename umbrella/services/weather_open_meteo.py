from __future__ import annotations

from dataclasses import dataclass

from umbrella.services.http import get_json


@dataclass(frozen=True)
class TodayForecast:
    precip_probability_pct: int
    description: str


class OpenMeteoWeather:
    BASE = "https://api.open-meteo.com/v1/forecast"

    def get_today(self, lat: float, lon: float, lang: str = "ru") -> TodayForecast:
        data = get_json(
            self.BASE,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "precipitation_probability_max,weathercode",
                "timezone": "auto",
            },
        )
        daily = data.get("daily") or {}
        p = (daily.get("precipitation_probability_max") or [0])[0] or 0
        code = (daily.get("weathercode") or [0])[0] or 0
        return TodayForecast(
            precip_probability_pct=int(p),
            description=_weathercode_to_text(int(code), lang=lang),
        )


def _weathercode_to_text(code: int, lang: str) -> str:
    ru = {
        0: "Ясно",
        1: "В основном ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Изморозь / туман",
        51: "Морось (слабая)",
        53: "Морось (умеренная)",
        55: "Морось (сильная)",
        61: "Дождь (слабый)",
        63: "Дождь (умеренный)",
        65: "Дождь (сильный)",
        71: "Снег (слабый)",
        73: "Снег (умеренный)",
        75: "Снег (сильный)",
        80: "Ливни (слабые)",
        81: "Ливни (умеренные)",
        82: "Ливни (сильные)",
        95: "Гроза",
    }
    en = {
        0: "Clear",
        1: "Mostly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Drizzle (light)",
        53: "Drizzle (moderate)",
        55: "Drizzle (dense)",
        61: "Rain (slight)",
        63: "Rain (moderate)",
        65: "Rain (heavy)",
        71: "Snow (slight)",
        73: "Snow (moderate)",
        75: "Snow (heavy)",
        80: "Rain showers (slight)",
        81: "Rain showers (moderate)",
        82: "Rain showers (violent)",
        95: "Thunderstorm",
    }
    table = ru if lang == "ru" else en
    return table.get(code, table.get(3, ""))

