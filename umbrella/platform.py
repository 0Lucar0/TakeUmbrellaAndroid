def is_android() -> bool:
    try:
        import android  # noqa: F401

        return True
    except Exception:
        return False


def is_desktop() -> bool:
    return not is_android()

