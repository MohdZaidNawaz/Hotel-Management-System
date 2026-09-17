"""Input validation shared by API routes."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_stay(
    check_in_value: Any, check_out_value: Any, guests_value: Any
) -> tuple[str, str, int, int]:
    try:
        check_in_date = date.fromisoformat(str(check_in_value))
        check_out_date = date.fromisoformat(str(check_out_value))
    except (TypeError, ValueError):
        raise ValueError("Choose valid check-in and check-out dates.") from None
    try:
        guests = int(guests_value)
    except (TypeError, ValueError):
        raise ValueError("Choose the number of guests.") from None
    if check_in_date < date.today():
        raise ValueError("Check-in cannot be in the past.")
    nights = (check_out_date - check_in_date).days
    if nights < 1:
        raise ValueError("Check-out must be after check-in.")
    if nights > 30:
        raise ValueError("Online stays are limited to 30 nights.")
    if not 1 <= guests <= 4:
        raise ValueError("Online reservations support 1 to 4 guests.")
    return check_in_date.isoformat(), check_out_date.isoformat(), guests, nights


def clean_text(value: Any, label: str, max_length: int) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} is required.")
    if len(text) > max_length:
        raise ValueError(f"{label} is too long.")
    return text
