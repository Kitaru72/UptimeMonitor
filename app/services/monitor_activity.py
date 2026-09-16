from datetime import datetime, timedelta


def should_pause_monitor(monitor, current_time: datetime) -> bool:
    if not monitor.is_active:
        return False

    if monitor.last_checked_at is not None:
        reference_time = monitor.last_checked_at
    else:
        reference_time = monitor.created_at

    delta = current_time - reference_time

    return delta >= timedelta(days=1)
