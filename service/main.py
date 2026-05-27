from __future__ import annotations

import json
from pathlib import Path

from umbrella.i18n import I18n
from umbrella.services.notifications import Notifier
from umbrella.services.settings_store import SettingsStore
from umbrella.services.weather_open_meteo import OpenMeteoWeather


def main():
    # PythonService working dir differs; read settings from the same user_data_dir path by env.
    # In python-for-android, the app's private storage is accessible; we keep the path stable.
    # If the environment doesn't provide it (desktop/dev), this still works if run from project.
    user_data = Path(_guess_user_data_dir())
    store = SettingsStore(user_data / "settings.json")
    s = store.load()

    if not s.notifications_enabled:
        return
    if not s.city.lat or not s.city.lon:
        return

    lang = "ru" if s.lang not in ("ru", "en") else s.lang
    i18n = I18n(lang)

    weather = OpenMeteoWeather()
    fc = weather.get_today(s.city.lat, s.city.lon, lang=lang)

    if fc.precip_probability_pct >= int(s.rain_threshold_pct):
        msg = i18n.t("notif_rain", pct=fc.precip_probability_pct)
    else:
        msg = i18n.t("notif_no_rain")

    Notifier().notify(i18n.t("app_title"), msg)


def _guess_user_data_dir() -> str:
    # Best-effort: python-for-android sets ANDROID_PRIVATE or uses app files dir.
    import os

    p = os.environ.get("ANDROID_PRIVATE")
    if p:
        return p
    # Fallback for dev
    return str(Path.home() / ".take-umbrella")


if __name__ == "__main__":
    main()

