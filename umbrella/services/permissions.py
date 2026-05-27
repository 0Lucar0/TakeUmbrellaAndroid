from __future__ import annotations

from umbrella.platform import is_android


def request_android_permissions(callback=None) -> None:
    if not is_android():
        if callback:
            callback(True)
        return

    try:
        from android.permissions import Permission, request_permissions  # type: ignore

        perms = [
            Permission.POST_NOTIFICATIONS,  # Android 13+
            Permission.ACCESS_COARSE_LOCATION,
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_BACKGROUND_LOCATION,
        ]

        def _cb(permissions, grants):
            ok = all(bool(g) for g in grants)
            if callback:
                callback(ok)

        request_permissions(perms, _cb)
    except Exception:
        if callback:
            callback(False)

