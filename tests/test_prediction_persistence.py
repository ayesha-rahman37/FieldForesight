
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

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


class TestPredictionPersistence(unittest.TestCase):
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

        self.user = User(
            username="prediction_user",
            email="prediction@example.com",
            password_hash="test-hash",
            role_id=role.id,
            is_active=True,
        )
        self.db.add(self.user)
        self.db.commit()

        self.token = "prediction-test-token"
        self.db.add(
            UserSession(
                user_id=self.user.id,
                session_token=self.token,
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
        )
        self.db.commit()

        def override_get_db():
            yield self.db

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()

    def test_prediction_is_saved_for_authenticated_user(self):
        mock_result = {
            "predicted_yield": 5.5,
            "lower_bound": 4.5,
            "upper_bound": 6.5,
            "message": "Test prediction",
            "model_version": "test-version",
            "cache_hit": False,
        }

        with patch(
            "app.routes.prediction.get_prediction",
            return_value=mock_result,
        ) as mocked_prediction:
            response = self.client.post(
                "/api/predict",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "crop": "Rice",
                    "region": "Rangpur",
                    "variety": "HYV",
                    "cropping_type": "single",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["predicted_yield"], 5.5)
        self.assertEqual(response.json()["lower_bound"], 4.5)
        self.assertEqual(response.json()["upper_bound"], 6.5)
        mocked_prediction.assert_called_once()

        history = (
            self.db.query(PredictionHistory)
            .filter_by(user_id=self.user.id)
            .all()
        )
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].crop, "Rice")
        self.assertEqual(history[0].region, "Rangpur")
        self.assertEqual(history[0].predicted_yield, 5.5)
        self.assertEqual(history[0].lower_bound, 4.5)
        self.assertEqual(history[0].upper_bound, 6.5)

    def test_prediction_requires_authentication(self):
        response = self.client.post(
            "/api/predict",
            json={
                "crop": "Rice",
                "region": "Rangpur",
                "variety": "HYV",
                "cropping_type": "single",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            self.db.query(PredictionHistory).count(),
            0,
        )


if __name__ == "__main__":
    unittest.main()
