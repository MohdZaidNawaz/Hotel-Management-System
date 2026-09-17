"""Route registration for the application factory."""

from flask import Flask

from .availability import availability_api
from .pages import pages
from .reservations import reservations_api


def register_routes(app: Flask) -> None:
    app.register_blueprint(pages)
    app.register_blueprint(availability_api)
    app.register_blueprint(reservations_api)
