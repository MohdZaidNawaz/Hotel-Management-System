"""SQLite connection and schema setup."""

from __future__ import annotations

import sqlite3

from flask import current_app, g

from .seed import ROOM_SEED


def get_db() -> sqlite3.Connection:
    if "database" not in g:
        g.database = sqlite3.connect(current_app.config["DATABASE"])
        g.database.row_factory = sqlite3.Row
        g.database.execute("PRAGMA foreign_keys = ON")
        g.database.execute("PRAGMA busy_timeout = 5000")
    return g.database


def close_database(_error: BaseException | None = None) -> None:
    database = g.pop("database", None)
    if database is not None:
        database.close()


def init_database() -> None:
    database = get_db()
    database.executescript(
        """
        CREATE TABLE IF NOT EXISTS room_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            nightly_rate INTEGER NOT NULL CHECK (nightly_rate > 0),
            capacity INTEGER NOT NULL CHECK (capacity > 0),
            beds INTEGER NOT NULL CHECK (beds > 0),
            inventory INTEGER NOT NULL CHECK (inventory > 0),
            amenities TEXT NOT NULL,
            image_variant TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            confirmation_code TEXT NOT NULL UNIQUE,
            room_type_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            guests INTEGER NOT NULL,
            nights INTEGER NOT NULL,
            nightly_rate INTEGER NOT NULL,
            subtotal INTEGER NOT NULL,
            taxes INTEGER NOT NULL,
            total INTEGER NOT NULL,
            special_requests TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled')),
            created_at TEXT NOT NULL,
            cancelled_at TEXT,
            FOREIGN KEY (room_type_id) REFERENCES room_types(id)
        );

        CREATE INDEX IF NOT EXISTS idx_reservation_dates
        ON reservations(room_type_id, check_in, check_out, status);
        """
    )
    database.executemany(
        """
        INSERT OR IGNORE INTO room_types
        (code, name, description, nightly_rate, capacity, beds, inventory, amenities, image_variant)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ROOM_SEED,
    )
    database.commit()
