import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.services.scenario_service import compute
from app.database import SessionLocal


class TestScenarioSharedService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_identical_numbers_both_paths(self):
        """Confirms REST /api/scenario/ and scenario_service.compute return identical numbers."""
        test_cases = [
            {"crop": "Rice", "region": "Rangpur", "variety": "HYV", "cropping_type": "single", "rainfall_adj": -20.0, "temp_adj": 10.0},
            {"crop": "Potato", "region": "Bogra", "variety": "HYV", "cropping_type": "single", "rainfall_adj": 30.0, "temp_adj": -10.0},
            {"crop": "Wheat", "region": "Dinajpur", "variety": "HYV", "cropping_type": "single", "rainfall_adj": 0.0, "temp_adj": 0.0},
        ]

        for tc in test_cases:
            # Direct service call
            direct_res = compute(
                crop=tc["crop"],
                region=tc["region"],
                variety=tc["variety"],
                cropping_type=tc["cropping_type"],
                rainfall_pct=tc["rainfall_adj"],
                temperature_pct=tc["temp_adj"],
                db=self.db,
            )

            # REST endpoint call
            rest_resp = self.client.post("/api/scenario/", json={
                "crop": tc["crop"],
                "region": tc["region"],
                "variety": tc["variety"],
                "cropping_type": tc["cropping_type"],
                "rainfall_adjustment_percent": tc["rainfall_adj"],
                "temperature_adjustment_percent": tc["temp_adj"],
            })
            self.assertEqual(rest_resp.status_code, 200)
            rest_data = rest_resp.json()

            # Verify identical figures
            self.assertEqual(direct_res.original_yield, rest_data["original_yield"])
            self.assertEqual(direct_res.adjusted_yield, rest_data["adjusted_yield"])
            self.assertEqual(direct_res.lower_bound, rest_data["lower_bound"])
            self.assertEqual(direct_res.upper_bound, rest_data["upper_bound"])
            self.assertEqual(direct_res.adjustment_applied, rest_data["adjustment_applied"])
            self.assertEqual(direct_res.message, rest_data["message"])


if __name__ == "__main__":
    unittest.main()

