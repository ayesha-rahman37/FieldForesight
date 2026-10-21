
import unittest
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.role import Role
from app.models.user import User
from app.models.session import UserSession
from app.models.prediction_history import PredictionHistory


class TestPredictionHistoryAuthorization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestSession = sessionmaker(
            bind=cls.engine,
            autoflush=False,
            autocommit=False,
        )
        Base.metadata.create_all(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=cls.engine)
        cls.engine.dispose()

    def setUp(self):
        self.db = self.TestSession()

        self.db.query(PredictionHistory).delete()
        self.db.query(UserSession).delete()
        self.db.query(User).delete()
        self.db.query(Role).delete()
        self.db.commit()

        role = Role(name="farmer")
        self.db.add(role)
        self.db.commit()

        self.user1 = User(
            username="history_user1",
            email="history1@example.com",
            password_hash="test-hash",
            role_id=role.id,
            is_active=True,
        )
        self.user2 = User(
            username="history_user2",
            email="history2@example.com",
            password_hash="test-hash",
            role_id=role.id,
            is_active=True,
        )
        self.db.add_all([self.user1, self.user2])
        self.db.commit()

        self.db.add_all([
            UserSession(
                user_id=self.user1.id,
                session_token="history-token-1",
                expires_at=datetime.utcnow() + timedelta(hours=1),
            ),
            UserSession(
                user_id=self.user2.id,
                session_token="history-token-2",
                expires_at=datetime.utcnow() + timedelta(hours=1),
            ),
            PredictionHistory(
                user_id=self.user1.id,
                crop="Rice",
                region="Rangpur",
                variety="HYV",
                cropping_type="single",
                predicted_yield=5.0,
                lower_bound=4.0,
                upper_bound=6.0,
            ),
            PredictionHistory(
                user_id=self.user2.id,
                crop="Wheat",
                region="Dhaka",
                variety="Local",
                cropping_type="rotation",
                predicted_yield=3.0,
                lower_bound=2.0,
                upper_bound=4.0,
            ),
        ])
        self.db.commit()

        def override_get_db():
            yield self.db

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()

    def test_history_requires_authentication(self):
        response = self.client.get("/api/predictions/history")
        self.assertEqual(response.status_code, 401)

    def test_user_sees_only_their_own_history(self):
        response = self.client.get(
            "/api/predictions/history",
            headers={"Authorization": "Bearer history-token-1"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["crop"], "Rice")
        self.assertEqual(data[0]["region"], "Rangpur")

    def test_other_users_history_is_not_exposed(self):
        response = self.client.get(
            "/api/predictions/history",
            headers={"Authorization": "Bearer history-token-2"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["crop"], "Wheat")
        self.assertEqual(data[0]["region"], "Dhaka")


if __name__ == "__main__":
    unittest.main()
