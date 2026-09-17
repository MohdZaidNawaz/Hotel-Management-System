"""Reservation creation, lookup, and cancellation API routes."""

from __future__ import annotations

import re
import sqlite3
from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request

from ..database import get_db
from ..reservations import create_confirmation_code, serialize_reservation
from ..responses import api_error
from ..rooms import available_units
from ..security import validate_csrf
from ..validation import EMAIL_PATTERN, clean_text, validate_stay

reservations_api = Blueprint("reservations_api", __name__)


@reservations_api.post("/api/reservations")
def create_reservation():
    csrf_error = validate_csrf()
    if csrf_error:
        return csrf_error

    payload = request.get_json(silent=True) or {}
    try:
        check_in, check_out, guests, nights = validate_stay(
            payload.get("check_in"), payload.get("check_out"), payload.get("guests")
        )
        room_code = clean_text(payload.get("room_code"), "Room", 80)
        first_name = clean_text(payload.get("first_name"), "First name", 80)
        last_name = clean_text(payload.get("last_name"), "Last name", 80)
        email = clean_text(payload.get("email"), "Email", 180).lower()
        phone = clean_text(payload.get("phone"), "Phone number", 30)
        special_requests = str(payload.get("special_requests") or "").strip()[:1000]
        if not EMAIL_PATTERN.match(email):
            raise ValueError("Enter a valid email address.")
        if len(re.sub(r"\D", "", phone)) < 7:
            raise ValueError("Enter a valid phone number.")
    except ValueError as error:
        return api_error(str(error), 400)

    database = get_db()
    room = database.execute(
        "SELECT * FROM room_types WHERE code = ? AND is_active = 1", (room_code,)
    ).fetchone()
    if room is None:
        return api_error("That room type is no longer available.", 404)
    if guests > room["capacity"]:
        return api_error(f"{room['name']} accommodates up to {room['capacity']} guests.", 400)

    subtotal = room["nightly_rate"] * nights
    taxes = round(subtotal * 0.12)
    total = subtotal + taxes
    confirmation = create_confirmation_code(database)

    try:
        database.execute("BEGIN IMMEDIATE")
        remaining = available_units(room["id"], check_in, check_out, database)
        if remaining <= 0:
            database.rollback()
            return api_error(
                "That room was just reserved for these dates. Please choose another stay.", 409
            )
        database.execute(
            """
            INSERT INTO reservations (
                confirmation_code, room_type_id, first_name, last_name, email, phone,
                check_in, check_out, guests, nights, nightly_rate, subtotal, taxes,
                total, special_requests, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'confirmed', ?)
            """,
            (
                confirmation,
                room["id"],
                first_name,
                last_name,
                email,
                phone,
                check_in,
                check_out,
                guests,
                nights,
                room["nightly_rate"],
                subtotal,
                taxes,
                total,
                special_requests,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        database.commit()
    except sqlite3.Error:
        database.rollback()
        current_app.logger.exception("Reservation creation failed")
        return api_error("We could not complete the reservation. Please try again.", 500)

    return (
        jsonify(
            {
                "message": "Your stay is confirmed.",
                "reservation": {
                    "confirmation_code": confirmation,
                    "guest_name": f"{first_name} {last_name}",
                    "room_name": room["name"],
                    "check_in": check_in,
                    "check_out": check_out,
                    "nights": nights,
                    "guests": guests,
                    "total": total,
                    "status": "confirmed",
                },
            }
        ),
        201,
    )


@reservations_api.get("/api/reservations/lookup")
def lookup_reservation():
    confirmation = str(request.args.get("confirmation") or "").strip().upper()
    email = str(request.args.get("email") or "").strip().lower()
    if not confirmation or not EMAIL_PATTERN.match(email):
        return api_error("Enter your confirmation code and booking email.", 400)

    reservation = get_db().execute(
        """
        SELECT r.*, rt.name AS room_name
        FROM reservations r
        JOIN room_types rt ON rt.id = r.room_type_id
        WHERE r.confirmation_code = ? AND lower(r.email) = ?
        """,
        (confirmation, email),
    ).fetchone()
    if reservation is None:
        return api_error("We couldn't find a booking with those details.", 404)
    return jsonify({"reservation": serialize_reservation(reservation)})


@reservations_api.post("/api/reservations/<confirmation>/cancel")
def cancel_reservation(confirmation: str):
    csrf_error = validate_csrf()
    if csrf_error:
        return csrf_error
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email") or "").strip().lower()
    database = get_db()
    reservation = database.execute(
        "SELECT * FROM reservations WHERE confirmation_code = ? AND lower(email) = ?",
        (confirmation.upper(), email),
    ).fetchone()
    if reservation is None:
        return api_error("We couldn't find a booking with those details.", 404)
    if reservation["status"] == "cancelled":
        return api_error("This reservation has already been cancelled.", 409)
    if date.fromisoformat(reservation["check_in"]) <= date.today():
        return api_error("Online cancellation closes on the day of arrival. Please call us.", 409)
    database.execute(
        "UPDATE reservations SET status = 'cancelled', cancelled_at = ? WHERE id = ?",
        (datetime.now().isoformat(timespec="seconds"), reservation["id"]),
    )
    database.commit()
    return jsonify({"message": "Your reservation has been cancelled."})
