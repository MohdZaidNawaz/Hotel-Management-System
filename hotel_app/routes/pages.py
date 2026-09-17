"""HTML page and health-check routes."""

from datetime import date

from flask import Blueprint, jsonify, render_template, session

from ..rooms import query_rooms

pages = Blueprint("pages", __name__)


@pages.get("/")
def home():
    return render_template(
        "index.html",
        rooms=query_rooms(),
        csrf_token=session["csrf_token"],
        today=date.today().isoformat(),
    )


@pages.get("/health")
def health():
    return jsonify({"status": "ok"})
