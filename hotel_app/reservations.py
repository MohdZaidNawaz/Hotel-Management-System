"""Reservation helpers shared by reservation routes."""

from __future__ import annotations

import secrets
import sqlite3
import string
from typing import Any


def create_confirmation_code(database: sqlite3.Connection) -> str:
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "SOL-" + "".join(secrets.choice(alphabet) for _ in range(6))
        exists = database.execute(
            "SELECT 1 FROM reservations WHERE confirmation_code = ?", (code,)
        ).fetchone()
        if exists is None:
            return code


def serialize_reservation(reservation: sqlite3.Row) -> dict[str, Any]:
    return {
        "confirmation_code": reservation["confirmation_code"],
        "guest_name": f"{reservation['first_name']} {reservation['last_name']}",
        "email": reservation["email"],
        "room_name": reservation["room_name"],
        "check_in": reservation["check_in"],
        "check_out": reservation["check_out"],
        "nights": reservation["nights"],
        "guests": reservation["guests"],
        "total": reservation["total"],
        "status": reservation["status"],
    }
