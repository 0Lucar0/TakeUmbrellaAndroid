from __future__ import annotations

from pathlib import Path

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import DictProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import get_color_from_hex

from kivy.app import App

from umbrella.i18n import I18n
from umbrella.services.geocoding import OpenMeteoGeocoding
from umbrella.services.notifications import Notifier
from umbrella.services.scheduler import DailyScheduler
from umbrella.services.settings_store import SettingsStore
from umbrella.services.weather_open_meteo import OpenMeteoWeather
from umbrella.ui.screens import HomeScreen, OnboardingScreen, SettingsScreen


class TakeUmbrellaApp(App):
    lang = StringProperty("ru")
    colors = DictProperty({})
    emoji_font = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_store: SettingsStore | None = None
        self.i18n: I18n | None = None
        self.weather = OpenMeteoWeather()
        self.geocoding = OpenMeteoGeocoding()
        self.notifier = Notifier()
        self.scheduler: DailyScheduler | None = None

    def build(self):
        Builder.load_file(str(Path("kv") / "app.kv"))
        self.settings_store = SettingsStore(Path(self.user_data_dir) / "settings.json")
        s = self.settings_store.load()

        self.lang = "ru" if s.lang in ("ru", "en") else "ru"
        self.i18n = I18n(self.lang)

        self.apply_theme()
        self._resolve_fonts()

        sm = ScreenManager()
        sm.app = self  # small convenience for screens
        sm.add_widget(OnboardingScreen(name="onboarding"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(SettingsScreen(name="settings"))

        sm.current = "home" if s.onboarding_done else "onboarding"

        self.scheduler = DailyScheduler(on_trigger=self._daily_trigger_foreground)
        self.reschedule_notifications()
        if s.onboarding_done:
            Clock.schedule_once(lambda _dt: self.refresh_forecast(), 0)
        return sm

    def _resolve_fonts(self) -> None:
        # Optional: if present, used to render umbrella emoji reliably on Windows.
        # We keep it bundled with the project (and included by buildozer).
        p = Path("assets") / "fonts" / "NotoEmoji-Regular.ttf"
        self.emoji_font = str(p) if p.exists() else ""

    def t(self, key: str, **kwargs) -> str:
        return (self.i18n or I18n("ru")).t(key, **kwargs)

    def apply_theme(self):
        s = self.settings_store.settings if self.settings_store else None
        theme = (s.theme if s else "auto") or "auto"

        # Minimal palette (RGBA floats).
        # "auto" is treated as dark by default for now; can be extended via Android night mode later.
        dark = theme in ("auto", "dark")
        if dark:
            self.colors = {
                "bg": (0.07, 0.08, 0.10, 1),
                "surface": (0.12, 0.13, 0.16, 1),
                "text": (0.95, 0.95, 0.97, 1),
                "muted": (0.70, 0.72, 0.75, 1),
                "accent": (0.35, 0.70, 0.98, 1),
                "good": (0.38, 0.85, 0.60, 1),
                "bad": (0.98, 0.45, 0.45, 1),
            }
        else:
            self.colors = {
                "bg": (0.97, 0.97, 0.98, 1),
                "surface": (1.0, 1.0, 1.0, 1),
                "text": (0.10, 0.11, 0.12, 1),
                "muted": (0.35, 0.38, 0.42, 1),
                "accent": (0.12, 0.45, 0.95, 1),
                "good": (0.10, 0.60, 0.35, 1),
                "bad": (0.85, 0.20, 0.20, 1),
            }

        from kivy.core.window import Window

        Window.clearcolor = self.colors["bg"]

    def finish_onboarding(self):
        s = self.settings_store.settings
        s.onboarding_done = True
        self.settings_store.save()
        self.root.current = "home"
        self.refresh_forecast()
        self.reschedule_notifications()

    def refresh_forecast(self):
        s = self.settings_store.settings
        home: HomeScreen = self.root.get_screen("home")
        if not s.city.lat or not s.city.lon:
            home.city_label = self.t("city", name="—")
            home.rain_pct = 0
            home.weather_desc = ""
            home.umbrella_needed = False
            return

        fc = self.weather.get_today(s.city.lat, s.city.lon, lang=self.lang)
        home.city_label = self.t("city", name=s.city.name or "—")
        home.rain_pct = fc.precip_probability_pct
        home.weather_desc = fc.description
        home.umbrella_needed = fc.precip_probability_pct >= int(s.rain_threshold_pct)
        home.animate_status()

    def reschedule_notifications(self):
        s = self.settings_store.settings
        if not self.scheduler:
            return
        if not s.notifications_enabled:
            self.scheduler.cancel()
            return
        self.scheduler.schedule(s.notify_hour, s.notify_minute)

    def _daily_trigger_foreground(self):
        # Dev/desktop fallback: when timer fires while app is open.
        self._send_today_notification()

    def _send_today_notification(self):
        s = self.settings_store.settings
        if not s.notifications_enabled:
            return
        if not s.city.lat or not s.city.lon:
            return
        fc = self.weather.get_today(s.city.lat, s.city.lon, lang=self.lang)
        if fc.precip_probability_pct >= int(s.rain_threshold_pct):
            msg = self.t("notif_rain", pct=fc.precip_probability_pct)
        else:
            msg = self.t("notif_no_rain")
        self.notifier.notify(self.t("app_title"), msg)

