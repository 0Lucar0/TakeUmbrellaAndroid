from __future__ import annotations

from umbrella.platform import is_android


class Notifier:
    def notify(self, title: str, message: str) -> None:
        try:
            from plyer import notification

            notification.notify(title=title, message=message, app_name=title)
            return
        except Exception:
            pass

        if is_android():
            # Last-resort: even if plyer fails, avoid crashing the background flow.
            return

