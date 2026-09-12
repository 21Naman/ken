from datetime import date


def expiry_status(expiry_date: date | None, today: date | None = None) -> str:
    """Pure display state. It neither consumes inventory nor recommends a meal."""
    if expiry_date is None:
        return "unknown"
    today = today or date.today()
    if expiry_date < today:
        return "expired"
    if expiry_date == today:
        return "expires_today"
    if (expiry_date - today).days <= 2:
        return "expiring_soon"
    return "fresh"
