from datetime import timedelta
from django.utils import timezone

def boundary_for_posted_days(days: int):
    """
    Return the start boundary for the given 'posted' days window,
    anchored to local midnight.
    - Today (days <= 1): start = today 00:00 local
    - 3 days (days=3): start = midnight today - 2 days (includes today)
    - 7 days (days=7): start = midnight today - 6 days
    - 30 days (days=30): start = midnight today - 29 days
    """
    now = timezone.localtime(timezone.now())
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if days <= 1:
        return midnight
    return midnight - timedelta(days=(days - 1))

def apply_posted_filter(queryset, posted_value):
    try:
        days = int(posted_value) if posted_value is not None else None
    except (TypeError, ValueError):
        days = None
    if days is None:
        return queryset
    if days < 0:
        return queryset
    start = boundary_for_posted_days(days)
    if start:
        return queryset.filter(created_at__gte=start)
    return queryset
