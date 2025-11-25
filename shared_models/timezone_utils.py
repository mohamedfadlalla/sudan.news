"""
Timezone utilities for Sudan News application.

Provides consistent timezone handling across all components.
Uses configurable timezone from APP_TIMEZONE environment variable.
"""

import os
from datetime import datetime, timezone
from typing import Optional

try:
    # Python 3.9+
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for older Python versions
    import pytz
    ZoneInfo = pytz.timezone

# Default timezone
DEFAULT_TIMEZONE = "Africa/Khartoum"

def get_app_timezone() -> ZoneInfo:
    """
    Get the configured application timezone.

    Returns:
        ZoneInfo: The configured timezone object
    """
    tz_name = os.getenv('APP_TIMEZONE', DEFAULT_TIMEZONE)
    try:
        return ZoneInfo(tz_name)
    except Exception as e:
        # Fallback to default if timezone is invalid
        print(f"Warning: Invalid timezone '{tz_name}', using default '{DEFAULT_TIMEZONE}'")
        return ZoneInfo(DEFAULT_TIMEZONE)

def now() -> datetime:
    """
    Get current datetime in application timezone.

    Returns:
        datetime: Current datetime with application timezone
    """
    return datetime.now(get_app_timezone())

def utc_now() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        datetime: Current UTC datetime
    """
    return datetime.now(timezone.utc)

def to_app_timezone(dt: datetime) -> datetime:
    """
    Convert a datetime to application timezone.

    Args:
        dt: Datetime to convert (naive or timezone-aware)

    Returns:
        datetime: Datetime in application timezone
    """
    app_tz = get_app_timezone()
    if dt.tzinfo is None:
        # Assume naive datetime is in app timezone
        return dt.replace(tzinfo=app_tz)
    else:
        # Convert to app timezone
        return dt.astimezone(app_tz)

def to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC.

    Args:
        dt: Datetime to convert (naive or timezone-aware)

    Returns:
        datetime: Datetime in UTC
    """
    if dt.tzinfo is None:
        # Assume naive datetime is in app timezone
        app_tz = get_app_timezone()
        dt = dt.replace(tzinfo=app_tz)
    return dt.astimezone(timezone.utc)

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string in application timezone.

    Args:
        dt: Datetime to format
        format_str: Format string (default: ISO-like format)

    Returns:
        str: Formatted datetime string
    """
    dt_app = to_app_timezone(dt)
    return dt_app.strftime(format_str)

def parse_datetime(date_str: str) -> Optional[datetime]:
    """
    Parse datetime string, assuming it's in application timezone if naive.

    Args:
        date_str: Date string to parse

    Returns:
        datetime: Parsed datetime in application timezone, or None if parsing fails
    """
    from dateutil import parser
    try:
        dt = parser.parse(date_str)
        return to_app_timezone(dt)
    except Exception:
        return None
