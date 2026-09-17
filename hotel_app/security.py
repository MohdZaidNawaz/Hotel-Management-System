"""Session and CSRF protection helpers."""

import secrets

from flask import request, session

from .responses import api_error


def ensure_csrf_token() -> None:
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(24)


def validate_csrf():
    supplied = request.headers.get("X-CSRF-Token", "")
    expected = session.get("csrf_token", "")
    if not supplied or not expected or not secrets.compare_digest(supplied, expected):
        return api_error("Your session expired. Refresh the page and try again.", 403)
    return None
