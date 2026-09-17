"""Development entry point for the Solara House application."""

from __future__ import annotations

import os

from hotel_app import create_app
from hotel_app.database import get_db

__all__ = ["app", "create_app", "get_db"]

app = create_app()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=5000)
