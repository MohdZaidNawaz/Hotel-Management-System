"""Room inventory queries and API serialization."""

from __future__ import annotations

import sqlite3
from typing import Any

from .database import get_db


def query_rooms() -> list[sqlite3.Row]:
    return get_db().execute(
        "SELECT * FROM room_types WHERE is_active = 1 ORDER BY nightly_rate"
    ).fetchall()


def available_units(
    room_type_id: int,
    check_in: str,
    check_out: str,
    database: sqlite3.Connection | None = None,
) -> int:
    database = database or get_db()
    room = database.execute(
        "SELECT inventory FROM room_types WHERE id = ?", (room_type_id,)
    ).fetchone()
    if room is None:
        return 0
    booked = database.execute(
        """
        SELECT COUNT(*) AS total FROM reservations
        WHERE room_type_id = ? AND status = 'confirmed'
          AND check_in < ? AND check_out > ?
        """,
        (room_type_id, check_out, check_in),
    ).fetchone()["total"]
    return max(room["inventory"] - booked, 0)


def serialize_room(room: sqlite3.Row, nights: int, available: int) -> dict[str, Any]:
    subtotal = room["nightly_rate"] * nights
    taxes = round(subtotal * 0.12)
    return {
        "code": room["code"],
        "name": room["name"],
        "description": room["description"],
        "nightly_rate": room["nightly_rate"],
        "capacity": room["capacity"],
        "beds": room["beds"],
        "amenities": room["amenities"].split("|"),
        "image_variant": room["image_variant"],
        "available": available,
        "subtotal": subtotal,
        "taxes": taxes,
        "total": subtotal + taxes,
    }
