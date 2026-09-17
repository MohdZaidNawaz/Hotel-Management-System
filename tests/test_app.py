import unittest
import uuid
from datetime import date, timedelta
from pathlib import Path

from app import create_app, get_db


class SolaraAppTestCase(unittest.TestCase):
    def setUp(self):
        self.database_path = Path.cwd() / f".solara-test-{uuid.uuid4().hex}.db"
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "DATABASE": str(self.database_path),
            }
        )
        self.client = self.app.test_client()
        self.check_in = (date.today() + timedelta(days=10)).isoformat()
        self.check_out = (date.today() + timedelta(days=13)).isoformat()
        self.client.get("/")
        with self.client.session_transaction() as session:
            self.csrf = session["csrf_token"]

    def tearDown(self):
        self.database_path.unlink(missing_ok=True)

    def booking_payload(self, **updates):
        payload = {
            "room_code": "garden-studio",
            "first_name": "Asha",
            "last_name": "Nair",
            "email": "asha@example.com",
            "phone": "+91 98765 43210",
            "check_in": self.check_in,
            "check_out": self.check_out,
            "guests": 2,
            "special_requests": "Late arrival",
        }
        payload.update(updates)
        return payload

    def create_booking(self, **updates):
        return self.client.post(
            "/api/reservations",
            json=self.booking_payload(**updates),
            headers={"X-CSRF-Token": self.csrf},
        )

    def test_home_and_health_are_available(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn(b"Solara House", home.data)
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})

    def test_availability_filters_by_guest_capacity(self):
        response = self.client.get(
            "/api/availability",
            query_string={
                "check_in": self.check_in,
                "check_out": self.check_out,
                "guests": 4,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["nights"], 3)
        self.assertEqual([room["code"] for room in response.json["rooms"]], ["horizon-villa"])

    def test_reservation_requires_csrf_token(self):
        response = self.client.post("/api/reservations", json=self.booking_payload())
        self.assertEqual(response.status_code, 403)

    def test_full_reservation_lookup_and_cancel_flow(self):
        created = self.create_booking()
        self.assertEqual(created.status_code, 201)
        reservation = created.json["reservation"]
        self.assertTrue(reservation["confirmation_code"].startswith("SOL-"))
        self.assertEqual(reservation["total"], 42000)

        found = self.client.get(
            "/api/reservations/lookup",
            query_string={
                "confirmation": reservation["confirmation_code"],
                "email": "ASHA@example.com",
            },
        )
        self.assertEqual(found.status_code, 200)
        self.assertEqual(found.json["reservation"]["status"], "confirmed")

        cancelled = self.client.post(
            f"/api/reservations/{reservation['confirmation_code']}/cancel",
            json={"email": "asha@example.com"},
            headers={"X-CSRF-Token": self.csrf},
        )
        self.assertEqual(cancelled.status_code, 200)

        found_again = self.client.get(
            "/api/reservations/lookup",
            query_string={
                "confirmation": reservation["confirmation_code"],
                "email": "asha@example.com",
            },
        )
        self.assertEqual(found_again.json["reservation"]["status"], "cancelled")

    def test_inventory_cannot_be_oversold(self):
        with self.app.app_context():
            database = get_db()
            database.execute("UPDATE room_types SET inventory = 1 WHERE code = 'garden-studio'")
            database.commit()

        first = self.create_booking()
        second = self.create_booking(email="another@example.com")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)

    def test_invalid_stay_is_rejected(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        response = self.client.get(
            "/api/availability",
            query_string={"check_in": yesterday, "check_out": self.check_out, "guests": 2},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("past", response.json["error"])


if __name__ == "__main__":
    unittest.main()
