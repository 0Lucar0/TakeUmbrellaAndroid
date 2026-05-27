from __future__ import annotations

from dataclasses import replace

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen

from umbrella.i18n import I18n
from umbrella.services.geocoding import OpenMeteoGeocoding
from umbrella.services.permissions import request_android_permissions
from umbrella.services.settings_store import SettingsStore
from umbrella.services.weather_open_meteo import OpenMeteoWeather


class OnboardingScreen(Screen):
    def request_perms(self):
        request_android_permissions(callback=lambda _ok: None)

    def finish(self):
        self.manager.app.finish_onboarding()


class HomeScreen(Screen):
    umbrella_needed = BooleanProperty(False)
    rain_pct = NumericProperty(0)
    weather_desc = StringProperty("")
    city_label = StringProperty("")

    def refresh(self):
        self.manager.app.refresh_forecast()

    def open_settings(self):
        self.manager.current = "settings"

    def animate_status(self):
        w = self.ids.get("status_icon")
        if not w:
            return
        w.opacity = 0.2
        Animation(opacity=1.0, duration=0.25).start(w)


class SettingsScreen(Screen):
    notify_enabled = BooleanProperty(True)
    time_label = StringProperty("07:00")
    theme = StringProperty("auto")

    city_query = StringProperty("")
    city_results = StringProperty("")

    def on_pre_enter(self, *args):
        app = self.manager.app
        s = app.settings_store.settings
        self.notify_enabled = s.notifications_enabled
        self.time_label = f"{s.notify_hour:02d}:{s.notify_minute:02d}"
        self.theme = s.theme
        return super().on_pre_enter(*args)

    def toggle_notify(self, enabled: bool):
        app = self.manager.app
        s = app.settings_store.settings
        s.notifications_enabled = bool(enabled)
        app.settings_store.save()
        app.reschedule_notifications()

    def cycle_theme(self):
        app = self.manager.app
        s = app.settings_store.settings
        order = ["auto", "light", "dark"]
        nxt = order[(order.index(s.theme) + 1) % len(order)]
        s.theme = nxt
        app.settings_store.save()
        self.theme = nxt
        app.apply_theme()

    def set_time(self, hhmm: str):
        app = self.manager.app
        s = app.settings_store.settings
        try:
            hh, mm = hhmm.split(":")
            s.notify_hour = max(0, min(23, int(hh)))
            s.notify_minute = max(0, min(59, int(mm)))
        except Exception:
            return
        app.settings_store.save()
        self.time_label = f"{s.notify_hour:02d}:{s.notify_minute:02d}"
        app.reschedule_notifications()

    def back(self):
        self.manager.current = "home"

    def search_city(self, text: str):
        self.city_query = text
        Clock.unschedule(self._do_search)
        Clock.schedule_once(self._do_search, 0.25)

    def _do_search(self, _dt):
        app = self.manager.app
        q = (self.city_query or "").strip()
        if len(q) < 2:
            self.city_results = ""
            self.ids.results_box.clear_widgets()
            return
        hits = app.geocoding.search(q, lang=app.lang, count=8)
        box = self.ids.results_box
        box.clear_widgets()
        from kivy.uix.button import Button

        for h in hits:
            b = Button(
                text=h.display_name,
                size_hint_y=None,
                height="40dp",
                background_normal="",
                background_color=app.colors["surface"],
                color=app.colors["text"],
            )
            b.bind(on_release=lambda _btn, hit=h: self._select_city(hit))
            box.add_widget(b)

    def _select_city(self, hit):
        app = self.manager.app
        s = app.settings_store.settings
        s.city.name = hit.display_name
        s.city.lat = float(hit.lat)
        s.city.lon = float(hit.lon)
        app.settings_store.save()
        self.city_query = ""
        self.ids.city_input.text = ""
        self.ids.results_box.clear_widgets()
        app.refresh_forecast()

