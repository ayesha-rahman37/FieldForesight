import unittest
import json
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.session import UserSession
from datetime import datetime, timedelta, timezone


class TestScenarioStreamEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

        self.user = self.db.query(User).filter(User.username == "test_scenario_stream_user").first()
        if not self.user:
            self.user = User(
                username="test_scenario_stream_user",
                email="scenariostream@fieldforesight.org",
                password_hash="fakehash",
                role_id=1,
            )
            self.db.add(self.user)
            self.db.commit()
            self.db.refresh(self.user)

        self.token = "test_scenario_token_abc"
        self.session = self.db.query(UserSession).filter(UserSession.session_token == self.token).first()
        if not self.session:
            self.session = UserSession(
                user_id=self.user.id,
                session_token=self.token,
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            )
            self.db.add(self.session)
            self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_unauthorized_returns_401(self):
        resp = self.client.post("/api/scenario/stream", json={"crop": "Rice", "region": "Rangpur"})
        self.assertEqual(resp.status_code, 401)

    def test_invalid_input_returns_422(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = self.client.post("/api/scenario/stream", json={"crop": "Rice", "rainfall_adjustment_percent": "abc"}, headers=headers)
        self.assertEqual(resp.status_code, 422)

    def test_successful_stream(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.stream(
            "POST",
            "/api/scenario/stream",
            json={
                "crop": "Rice",
                "region": "Rangpur",
                "variety": "HYV",
                "cropping_type": "single",
                "rainfall_adjustment_percent": 10.0,
                "temperature_adjustment_percent": -5.0,
            },
            headers=headers,
        ) as response:
            self.assertEqual(response.status_code, 200)
            events = []
            buffer = ""
            for chunk in response.iter_text():
                buffer += chunk
                while "\n\n" in buffer:
                    part, buffer = buffer.split("\n\n", 1)
                    for line in part.split("\n"):
                        line = line.strip()
                        if line.startswith("data:"):
                            events.append(json.loads(line[5:].strip()))

            self.assertEqual(len(events), 2)
            self.assertEqual(events[0]["type"], "result")
            self.assertIn("adjusted_yield", events[0])
            self.assertEqual(events[1]["type"], "done")


if __name__ == "__main__":
    unittest.main()
