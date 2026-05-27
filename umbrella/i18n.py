from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class I18n:
    lang: str  # "ru" | "en"

    def t(self, key: str, **kwargs) -> str:
        table = STRINGS.get(self.lang, STRINGS["ru"])
        s = table.get(key, STRINGS["ru"].get(key, key))
        return s.format(**kwargs)


STRINGS = {
    "ru": {
        "app_title": "Возьми зонтик",
        "onboarding_title": "Доброе утро без сюрпризов",
        "onboarding_body": "Разрешите уведомления и геолокацию или выберите город вручную.",
        "allow_notifications": "Разрешить уведомления",
        "allow_location": "Разрешить геолокацию",
        "enter_city": "Ввести город",
        "continue": "Продолжить",
        "today_need_umbrella": "Сегодня зонтик нужен",
        "today_no_umbrella": "Сегодня зонтик не нужен",
        "rain_chance": "Вероятность осадков: {pct}%",
        "weather_desc": "Погода: {desc}",
        "city": "Город: {name}",
        "change_city": "Сменить город",
        "settings": "Настройки",
        "notify_enabled": "Уведомления",
        "notify_time": "Время уведомления",
        "rain_threshold": "Порог дождя",
        "theme": "Тема",
        "theme_auto": "Авто",
        "theme_light": "Светлая",
        "theme_dark": "Тёмная",
        "notif_rain": "Возьми зонтик! Сегодня ожидается дождь ({pct}%)",
        "notif_no_rain": "Дождя не ожидается. Хорошего дня! ☀️",
        "search_city_hint": "Начните вводить город…",
    },
    "en": {
        "app_title": "Take Umbrella",
        "onboarding_title": "Good mornings, no surprises",
        "onboarding_body": "Allow notifications and location, or pick a city manually.",
        "allow_notifications": "Allow notifications",
        "allow_location": "Allow location",
        "enter_city": "Enter city",
        "continue": "Continue",
        "today_need_umbrella": "Umbrella needed today",
        "today_no_umbrella": "No umbrella needed today",
        "rain_chance": "Precipitation chance: {pct}%",
        "weather_desc": "Weather: {desc}",
        "city": "City: {name}",
        "change_city": "Change city",
        "settings": "Settings",
        "notify_enabled": "Notifications",
        "notify_time": "Notification time",
        "rain_threshold": "Rain threshold",
        "theme": "Theme",
        "theme_auto": "Auto",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "notif_rain": "Take an umbrella! Rain expected today ({pct}%)",
        "notif_no_rain": "No rain expected. Have a great day! ☀️",
        "search_city_hint": "Type a city…",
    },
}

