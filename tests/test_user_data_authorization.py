
import unittest
from datetime import datetime, timedelta

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.role import Role
from app.models.user import User
from app.models.session import UserSession
from app.models.user_preference import UserPreference
from app.models.prediction_history import PredictionHistory


class TestUserDataAuthorization(unittest.TestCase):
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
        self.db.query(UserSession).delete()
        self.db.query(PredictionHistory).delete()
        self.db.query(UserPreference).delete()
        self.db.query(User).delete()
        self.db.query(Role).delete()
        self.db.commit()

        role = Role(name="farmer")
        self.db.add(role)
        self.db.commit()

        self.user1 = User(
            username="farmer1",
            email="farmer1@example.com",
            password_hash="test-hash",
            role_id=role.id,
            is_active=True,
        )
        self.user2 = User(
            username="farmer2",
            email="farmer2@example.com",
            password_hash="test-hash",
            role_id=role.id,
            is_active=True,
        )
        self.db.add_all([self.user1, self.user2])
        self.db.commit()

        self.db.add_all([
            UserSession(
                user_id=self.user1.id,
                session_token="test-token-1",
                expires_at=datetime.utcnow() + timedelta(hours=1),
            ),
            UserSession(
                user_id=self.user2.id,
                session_token="test-token-2",
                expires_at=datetime.utcnow() + timedelta(hours=1),
            ),
            UserPreference(
                user_id=self.user1.id,
                last_crop="Rice",
                last_region="Rangpur",
            ),
            UserPreference(
                user_id=self.user2.id,
                last_crop="Wheat",
                last_region="Dhaka",
            ),
        ])
        self.db.commit()

        def override_get_db():
            try:
                yield self.db
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()

    def test_my_data_requires_authentication(self):
        response = self.client.get("/api/data-ownership/my_data")
        self.assertEqual(response.status_code, 401)


    def test_logout_deletes_current_server_session(self):
        response = self.client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer test-token-1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"],
            "Logged out successfully",
        )
        self.assertIsNone(
            self.db.query(UserSession)
            .filter_by(session_token="test-token-1")
            .first()
        )

        # The revoked token must no longer authenticate requests.
        protected_response = self.client.get(
            "/api/data-ownership/my_data",
            headers={"Authorization": "Bearer test-token-1"},
        )
        self.assertEqual(protected_response.status_code, 401)

        # Logging out one user must not revoke another user's session.
        other_response = self.client.get(
            "/api/data-ownership/my_data",
            headers={"Authorization": "Bearer test-token-2"},
        )
        self.assertEqual(other_response.status_code, 200)

    def test_logout_requires_authentication(self):
        response = self.client.post("/api/auth/logout")
        self.assertEqual(response.status_code, 401)


    def test_my_data_returns_authenticated_user(self):
        response = self.client.get(
            "/api/data-ownership/my_data",
            headers={"Authorization": "Bearer test-token-1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["profile"]["username"], "farmer1")
        self.assertEqual(
            response.json()["saved_preference"]["last_crop"], "Rice"
        )

    def test_preferences_require_authentication(self):
        response = self.client.get(f"/api/personalization/{self.user1.id}")
        self.assertEqual(response.status_code, 401)

    def test_user_cannot_read_another_users_preferences(self):
        response = self.client.get(
            f"/api/personalization/{self.user2.id}",
            headers={"Authorization": "Bearer test-token-1"},
        )
        self.assertEqual(response.status_code, 403)

    def test_save_preferences_uses_authenticated_user(self):
        response = self.client.post(
            "/api/personalization/save",
            headers={"Authorization": "Bearer test-token-1"},
            json={"crop": "Maize", "region": "Dhaka"},
        )
        self.assertEqual(response.status_code, 200)

        self.db.expire_all()
        pref1 = (
            self.db.query(UserPreference)
            .filter_by(user_id=self.user1.id)
            .first()
        )
        pref2 = (
            self.db.query(UserPreference)
            .filter_by(user_id=self.user2.id)
            .first()
        )
        self.assertEqual(pref1.last_crop, "Maize")
        self.assertEqual(pref2.last_crop, "Wheat")

    def test_delete_requires_authentication(self):
        response = self.client.request(
            "DELETE",
            "/api/data-ownership/delete",
            json={"data_type": "preferences"},
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_only_authenticated_users_preferences(self):
        response = self.client.request(
            "DELETE",
            "/api/data-ownership/delete",
            headers={"Authorization": "Bearer test-token-1"},
            json={"data_type": "preferences"},
        )
        self.assertEqual(response.status_code, 200)

        self.assertIsNone(
            self.db.query(UserPreference)
            .filter_by(user_id=self.user1.id)
            .first()
        )
        self.assertIsNotNone(
            self.db.query(UserPreference)
            .filter_by(user_id=self.user2.id)
            .first()
        )

    def test_unsupported_delete_type_is_rejected(self):
        response = self.client.request(
            "DELETE",
            "/api/data-ownership/delete",
            headers={"Authorization": "Bearer test-token-1"},
            json={"data_type": "everything"},
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
