import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.role import Role
from app.models.session import UserSession
from app.models.user_preference import UserPreference
from app.models.prediction_history import PredictionHistory
from app.models.advisory_history import AdvisoryHistory
from app.models.explainability_cache import ExplainabilityCache
from app.schemas.data_ownership_schema import DeleteRequest
from app.services.data_ownership_service import get_user_data, delete_data


class TestDataOwnershipService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Seed role
        role = Role(id=1, name="farmer")
        self.db.add(role)

        # Seed user
        self.user = User(
            id=1,
            username="test_farmer",
            email="farmer@test.com",
            password_hash="fakehash",
            role_id=1,
            is_active=True,
            created_at=datetime(2026, 1, 15, 10, 0),
        )
        self.db.add(self.user)

        # Seed session
        session = UserSession(
            id=1,
            user_id=1,
            session_token="test_token_123",
            expires_at=datetime(2026, 12, 31, 0, 0),
        )
        self.db.add(session)

        # Seed preference
        pref = UserPreference(
            id=1,
            user_id=1,
            last_crop="Wheat",
            last_region="Dhaka",
        )
        self.db.add(pref)

        # Seed prediction history
        pred = PredictionHistory(
            id=101,
            user_id=1,
            crop="Wheat",
            region="Dhaka",
            variety="HYV",
            cropping_type="single",
            predicted_yield=3.25,
            lower_bound=3.10,
            upper_bound=3.40,
        )
        self.db.add(pred)

        # Seed explainability cache linked to prediction
        exp = ExplainabilityCache(
            id=1,
            prediction_id=101,
            crop="Wheat",
            region="Dhaka",
            contributions={"rainfall": 35.0, "soil": 20.0, "temperature": 45.0},
            top_factor="temperature",
            summary_text_bn="টেস্ট বিবরণ",
        )
        self.db.add(exp)

        # Seed advisory linked to prediction
        adv = AdvisoryHistory(
            id=1,
            prediction_id=101,
            user_id=1,
            crop="Wheat",
            region="Dhaka",
            predicted_yield=3.25,
            risk_level="medium",
            advisory_text="টেস্ট পরামর্শ",
        )
        self.db.add(adv)

        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_get_user_data_real_values(self):
        user_data = get_user_data(user_id=1, db=self.db)
        self.assertEqual(user_data.profile.username, "test_farmer")
        self.assertEqual(user_data.profile.email, "farmer@test.com")
        self.assertEqual(user_data.profile.role, "farmer")
        self.assertEqual(user_data.profile.created_at, "2026-01-15")
        self.assertEqual(user_data.prediction_count, 1)
        self.assertEqual(len(user_data.prediction_history), 1)
        self.assertEqual(user_data.prediction_history[0].crop, "Wheat")
        self.assertEqual(user_data.prediction_history[0].region, "Dhaka")
        self.assertEqual(user_data.preferences_count, 1)
        self.assertEqual(user_data.saved_preference.get("last_crop"), "Wheat")

    def test_delete_predictions(self):
        req = DeleteRequest(data_type="prediction_history")
        res = delete_data(req, user_id=1, db=self.db)
        self.assertTrue(res)

        # Confirm PredictionHistory, ExplainabilityCache, and AdvisoryHistory are removed
        self.assertEqual(self.db.query(PredictionHistory).filter(PredictionHistory.user_id == 1).count(), 0)
        self.assertEqual(self.db.query(ExplainabilityCache).filter(ExplainabilityCache.prediction_id == 101).count(), 0)
        self.assertEqual(self.db.query(AdvisoryHistory).filter(AdvisoryHistory.prediction_id == 101).count(), 0)
        # User and preferences still exist
        self.assertEqual(self.db.query(User).filter(User.id == 1).count(), 1)
        self.assertEqual(self.db.query(UserPreference).filter(UserPreference.user_id == 1).count(), 1)

    def test_delete_preferences(self):
        req = DeleteRequest(data_type="preferences")
        res = delete_data(req, user_id=1, db=self.db)
        self.assertTrue(res)
        self.assertEqual(self.db.query(UserPreference).filter(UserPreference.user_id == 1).count(), 0)
        # Prediction and User still exist
        self.assertEqual(self.db.query(PredictionHistory).filter(PredictionHistory.user_id == 1).count(), 1)
        self.assertEqual(self.db.query(User).filter(User.id == 1).count(), 1)

    def test_delete_profile(self):
        req = DeleteRequest(data_type="profile")
        res = delete_data(req, user_id=1, db=self.db)
        self.assertTrue(res)
        # Confirm user and all associated records are completely deleted
        self.assertEqual(self.db.query(User).filter(User.id == 1).count(), 0)
        self.assertEqual(self.db.query(UserSession).filter(UserSession.user_id == 1).count(), 0)
        self.assertEqual(self.db.query(UserPreference).filter(UserPreference.user_id == 1).count(), 0)
        self.assertEqual(self.db.query(PredictionHistory).filter(PredictionHistory.user_id == 1).count(), 0)
        self.assertEqual(self.db.query(ExplainabilityCache).filter(ExplainabilityCache.prediction_id == 101).count(), 0)
        self.assertEqual(self.db.query(AdvisoryHistory).filter(AdvisoryHistory.user_id == 1).count(), 0)


if __name__ == "__main__":
    unittest.main()
