"""Application factory for Solara House."""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Any

from flask import Flask

from .database import close_database, init_database
from .routes import register_routes
from .security import ensure_csrf_token

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / "static"),
        template_folder=str(BASE_DIR / "templates"),
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SOLARA_SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get("SOLARA_DATABASE") or str(BASE_DIR / "solara.db"),
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    app.before_request(ensure_csrf_token)
    app.teardown_appcontext(close_database)
    register_routes(app)

    with app.app_context():
        init_database()

    return app
