import json
import unittest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.session import UserSession
from app.models.chat_message import ChatMessage
from app.routes.chat import _USER_RATE_LIMITS
from app.services.token_optimizer import set_mode


class TestChatStreamEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_mode("replay")
        cls.client = TestClient(app)
        db = SessionLocal()
        # Find or create a test user
        user = db.query(User).filter(User.username == "test_stream_user").first()
        if not user:
            user = User(
                username="test_stream_user",
                email="test_stream@example.com",
                password_hash="fake_hash_123456",
                role_id=1,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        cls.user_id = user.id

        # Create valid session token
        cls.token = "test_stream_session_token_12345"
        session = db.query(UserSession).filter(UserSession.session_token == cls.token).first()
        if not session:
            session = UserSession(
                user_id=cls.user_id,
                session_token=cls.token,
                expires_at=datetime.utcnow() + timedelta(days=1),
            )
            db.add(session)
            db.commit()
        db.close()

    def setUp(self):
        _USER_RATE_LIMITS.clear()

    def test_stream_unauthorized(self):
        """1. Request without auth token must return HTTP 401."""
        response = self.client.post("/api/chat/stream", json={"message": "হ্যালো"})
        self.assertEqual(response.status_code, 401)

    def test_stream_invalid_input_422(self):
        """2. Empty message or message > 500 chars must return HTTP 422."""
        headers = {"Authorization": f"Bearer {self.token}"}

        # Empty message
        res_empty = self.client.post("/api/chat/stream", json={"message": ""}, headers=headers)
        self.assertEqual(res_empty.status_code, 422)

        # Message exceeding 500 characters
        long_msg = "ধান " * 150
        self.assertTrue(len(long_msg) > 500)
        res_long = self.client.post("/api/chat/stream", json={"message": long_msg}, headers=headers)
        self.assertEqual(res_long.status_code, 422)

    def test_stream_successful_run(self):
        """3. Successful stream yields token events, sources, and done event."""
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "message": "বোরো ধানে এডব্লিউডি (AWD) পদ্ধতিতে সেচ কীভাবে দেব?",
            "context": {"crop": "Rice", "region": "Rangpur"},
        }
        response = self.client.post("/api/chat/stream", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers["content-type"])

        events = []
        for line in response.text.split("\n\n"):
            line = line.strip()
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))

        self.assertTrue(len(events) >= 3)
        # Check token events
        token_events = [e for e in events if e.get("type") == "token"]
        self.assertTrue(len(token_events) > 0)
        streamed_text = "".join(e["text"] for e in token_events)
        self.assertIn("AWD", streamed_text)

        # Check sources event
        sources_events = [e for e in events if e.get("type") == "sources"]
        self.assertEqual(len(sources_events), 1)
        self.assertIsInstance(sources_events[0].get("sources"), list)

        # Check done event
        done_events = [e for e in events if e.get("type") == "done"]
        self.assertEqual(len(done_events), 1)

        # Check DB persistence
        db = SessionLocal()
        assistant_record = (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == self.user_id, ChatMessage.role == "assistant")
            .order_by(ChatMessage.id.desc())
            .first()
        )
        self.assertIsNotNone(assistant_record)
        self.assertEqual(assistant_record.status, "success")
        self.assertIn("AWD", assistant_record.content)
        db.close()

    def test_stream_simulated_midstream_failure(self):
        """4. Mid-stream exception sends error event and does NOT persist assistant message."""
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "message": "বোরো ধানে এডব্লিউডি পদ্ধতিতে সেচ?",
            "context": {"crop": "Rice", "region": "Rangpur"},
        }
        response = self.client.post("/api/chat/stream?simulate_failure=true", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)

        events = []
        for line in response.text.split("\n\n"):
            line = line.strip()
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))

        error_events = [e for e in events if e.get("type") == "error"]
        self.assertEqual(len(error_events), 1)
        self.assertEqual(error_events[0].get("message"), "উত্তর সম্পূর্ণ হয়নি")

        # Verify done was NOT sent
        self.assertEqual(len([e for e in events if e.get("type") == "done"]), 0)


if __name__ == "__main__":
    unittest.main()
