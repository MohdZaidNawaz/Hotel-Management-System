"""Consistent API response helpers."""

from flask import jsonify


def api_error(message: str, status: int):
    return jsonify({"error": message}), status
