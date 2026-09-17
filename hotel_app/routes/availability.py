"""Room availability API route."""

from flask import Blueprint, jsonify, request

from ..responses import api_error
from ..rooms import available_units, query_rooms, serialize_room
from ..validation import validate_stay

availability_api = Blueprint("availability_api", __name__)


@availability_api.get("/api/availability")
def availability():
    try:
        check_in, check_out, guests, nights = validate_stay(
            request.args.get("check_in"),
            request.args.get("check_out"),
            request.args.get("guests"),
        )
    except ValueError as error:
        return api_error(str(error), 400)

    rooms = []
    for room in query_rooms():
        if room["capacity"] < guests:
            continue
        available = available_units(room["id"], check_in, check_out)
        if available <= 0:
            continue
        rooms.append(serialize_room(room, nights, available))

    return jsonify(
        {
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "nights": nights,
            "rooms": rooms,
        }
    )
