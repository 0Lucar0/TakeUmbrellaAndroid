from __future__ import annotations

import datetime as _dt

from kivy.clock import Clock

from umbrella.platform import is_android


class DailyScheduler:
    """
    Schedules a daily background check.

    Android: intended to be wired to AlarmManager + PythonService.
    Desktop/dev: uses a best-effort Clock timer while the app is running.
    """

    def __init__(self, on_trigger):
        self._on_trigger = on_trigger
        self._event = None

    def schedule(self, hour: int, minute: int) -> None:
        if is_android():
            _schedule_android_alarm(hour, minute)
            return
        self._schedule_clock(hour, minute)

    def cancel(self) -> None:
        if self._event is not None:
            try:
                self._event.cancel()
            except Exception:
                pass
            self._event = None
        if is_android():
            _cancel_android_alarm()

    def _schedule_clock(self, hour: int, minute: int) -> None:
        if self._event is not None:
            self._event.cancel()
            self._event = None

        now = _dt.datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target = target + _dt.timedelta(days=1)
        delay = (target - now).total_seconds()

        def _fire(_dt_):
            self._on_trigger()
            self._schedule_clock(hour, minute)

        self._event = Clock.schedule_once(_fire, delay)


def _schedule_android_alarm(hour: int, minute: int) -> None:
    # Kept minimal here; actual wiring is done in service entrypoint and build config.
    # App still functions on desktop/dev without this.
    try:
        from jnius import autoclass  # type: ignore

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")
        Intent = autoclass("android.content.Intent")
        PendingIntent = autoclass("android.app.PendingIntent")
        AlarmManager = autoclass("android.app.AlarmManager")
        Calendar = autoclass("java.util.Calendar")

        activity = PythonActivity.mActivity
        ctx = activity.getApplicationContext()

        intent = Intent(ctx, autoclass("org.kivy.android.PythonService"))
        intent.putExtra("serviceTitle", "Take Umbrella")
        intent.putExtra("serviceDescription", "Daily weather check")
        intent.putExtra("serviceArgument", "daily_check")

        req_code = 1001
        flags = PendingIntent.FLAG_UPDATE_CURRENT
        if hasattr(PendingIntent, "FLAG_IMMUTABLE"):
            flags |= PendingIntent.FLAG_IMMUTABLE
        pi = PendingIntent.getService(ctx, req_code, intent, flags)

        cal = Calendar.getInstance()
        cal.set(Calendar.HOUR_OF_DAY, int(hour))
        cal.set(Calendar.MINUTE, int(minute))
        cal.set(Calendar.SECOND, 0)
        cal.set(Calendar.MILLISECOND, 0)
        if cal.getTimeInMillis() <= Calendar.getInstance().getTimeInMillis():
            cal.add(Calendar.DAY_OF_YEAR, 1)

        am = ctx.getSystemService(Context.ALARM_SERVICE)
        if hasattr(am, "setExactAndAllowWhileIdle"):
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, cal.getTimeInMillis(), pi)
        else:
            am.setExact(AlarmManager.RTC_WAKEUP, cal.getTimeInMillis(), pi)
    except Exception:
        # Don't crash UI if alarm scheduling fails.
        return


def _cancel_android_alarm() -> None:
    try:
        from jnius import autoclass  # type: ignore

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")
        Intent = autoclass("android.content.Intent")
        PendingIntent = autoclass("android.app.PendingIntent")

        activity = PythonActivity.mActivity
        ctx = activity.getApplicationContext()
        intent = Intent(ctx, autoclass("org.kivy.android.PythonService"))
        req_code = 1001
        flags = PendingIntent.FLAG_UPDATE_CURRENT
        if hasattr(PendingIntent, "FLAG_IMMUTABLE"):
            flags |= PendingIntent.FLAG_IMMUTABLE
        pi = PendingIntent.getService(ctx, req_code, intent, flags)

        am = ctx.getSystemService(Context.ALARM_SERVICE)
        am.cancel(pi)
    except Exception:
        return

