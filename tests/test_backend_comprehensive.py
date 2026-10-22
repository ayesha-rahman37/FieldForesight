import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app import models


class TestBackendComprehensive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_ctx = TestClient(app)
        cls.client = cls.client_ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_ctx.__exit__(None, None, None)

    def test_01_database_tables_and_seeding(self):
        db = SessionLocal()
        try:
            self.assertGreaterEqual(db.query(models.Role).count(), 2)
            self.assertGreaterEqual(db.query(models.User).count(), 2)
            self.assertEqual(db.query(models.Crop).count(), 7)
            self.assertEqual(db.query(models.Region).count(), 64)
            self.assertGreaterEqual(db.query(models.HistoricalYield).count(), 260)
            self.assertEqual(db.query(models.NDVICache).count(), 64)
            self.assertGreaterEqual(db.query(models.ModelMetadata).count(), 26)
            self.assertGreaterEqual(db.query(models.ProcessedDataset).count(), 260)
            self.assertGreaterEqual(db.query(models.RiskThreshold).count(), 9)
            self.assertGreaterEqual(db.query(models.CropVariety).count(), 24)
            self.assertGreaterEqual(db.query(models.UserPreference).count(), 2)
        finally:
            db.close()

    def test_02_root_and_sqladmin(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("message", res.json())

        admin_res = self.client.get("/admin/")
        self.assertEqual(admin_res.status_code, 200)
        self.assertIn("FieldForesight Admin", admin_res.text)

    def test_03_crops_and_regions(self):
        crops_res = self.client.get("/api/crops")
        self.assertEqual(crops_res.status_code, 200)
        crops_data = crops_res.json()
        self.assertEqual(len(crops_data), 7)
        crop_names = [c["name"] for c in crops_data]
        self.assertIn("Lentil", crop_names)
        self.assertIn("Mustard", crop_names)
        self.assertIn("Potato", crop_names)

        regions_res = self.client.get("/api/regions")
        self.assertEqual(regions_res.status_code, 200)
        regions_data = regions_res.json()
        self.assertEqual(len(regions_data), 64)
        region_names = [r["name"] for r in regions_data]
        self.assertIn("Rangpur", region_names)
        self.assertIn("Bogura", region_names)

    def test_04_historical_data_and_mixed_crop(self):
        hist_res = self.client.get("/api/historical-data", params={"crop": "Rice", "region": "Rangpur"})
        self.assertEqual(hist_res.status_code, 200)
        hist_json = hist_res.json()
        self.assertEqual(hist_json["source_type"], "local_historical")
        self.assertGreaterEqual(len(hist_json["years"]), 10)
        self.assertEqual(len(hist_json["rainfall"]), len(hist_json["years"]))
        self.assertEqual(len(hist_json["yield"]), len(hist_json["years"]))
        self.assertIsNotNone(hist_json["rainfall"][0])

        # Test legacy spelling normalization ("Bogra" -> "Bogura")
        hist_alias = self.client.get("/api/historical-data", params={"crop": "Potato", "region": "Bogra"})
        self.assertEqual(hist_alias.status_code, 200)
        self.assertEqual(hist_alias.json()["source_type"], "local_historical")
        self.assertGreaterEqual(len(hist_alias.json()["years"]), 10)

        # Mixed crop endpoint
        mc_post = self.client.post("/api/mixed-crop", json={
            "farm_id": "test_farm_01",
            "relation_type": "intercrop",
            "crops": [
                {"crop": "Rice", "sequence_order": 1},
                {"crop": "Lentil", "sequence_order": 2},
            ]
        })
        self.assertEqual(mc_post.status_code, 200)
        self.assertIn("Rice", mc_post.json()["crops"])
        self.assertIn("Lentil", mc_post.json()["crops"])

        mc_get = self.client.get("/api/mixed-crop/test_farm_01")
        self.assertEqual(mc_get.status_code, 200)
        self.assertGreaterEqual(len(mc_get.json()), 2)

    def test_05_prediction_local_and_fallback_and_explainability(self):
        # 1. Trained local model prediction (Rice in Rangpur)
        pred_res = self.client.post("/api/predict", json={
            "crop": "Rice",
            "region": "Rangpur",
            "variety": "HYV",
            "cropping_type": "mixed"
        })
        self.assertEqual(pred_res.status_code, 200)
        pred_data = pred_res.json()
        self.assertIn("prediction_id", pred_data)
        self.assertIsNotNone(pred_data["prediction_id"])
        self.assertGreater(pred_data["predicted_yield"], 0)
        self.assertLess(pred_data["lower_bound"], pred_data["predicted_yield"])
        self.assertGreater(pred_data["upper_bound"], pred_data["predicted_yield"])
        self.assertIn("model_version", pred_data)

        prediction_id = pred_data["prediction_id"]

        # 2. Untrained district uses regional_fallback seamlessly
        fb_res = self.client.post("/api/predict", json={
            "crop": "Lentil",
            "region": "Bandarban",
            "variety": "BARI_MASUR_8",
            "cropping_type": "single"
        })
        self.assertEqual(fb_res.status_code, 200)
        self.assertEqual(fb_res.json()["model_version"], "fallback-regional-trend-v2")
        self.assertIsNotNone(fb_res.json()["prediction_id"])

        # 3. Explainability for prediction_id
        exp_res = self.client.get(f"/api/explain/{prediction_id}")
        self.assertEqual(exp_res.status_code, 200)
        exp_data = exp_res.json()
        self.assertEqual(exp_data["prediction_id"], prediction_id)
        self.assertIn("contributions", exp_data)
        self.assertIn("rainfall", exp_data["contributions"])
        self.assertIn("soil", exp_data["contributions"])
        self.assertIn("temperature", exp_data["contributions"])
        self.assertAlmostEqual(sum(exp_data["contributions"].values()), 100.0, delta=0.5)
        self.assertTrue(len(exp_data["summary_text_bn"]) > 10)

    def test_06_ndvi_scenario_and_community(self):
        # NDVI endpoint for any of the 64 districts
        ndvi_res = self.client.get("/api/ndvi/Dinajpur")
        self.assertEqual(ndvi_res.status_code, 200)
        ndvi_data = ndvi_res.json()
        self.assertEqual(ndvi_data["region"], "Dinajpur")
        self.assertGreater(ndvi_data["ndvi_value"], 0)
        self.assertIn(ndvi_data["vegetation_status"], ["Healthy", "Moderate", "Poor"])

        # Scenario planner simulation
        scen_res = self.client.post("/api/scenario", json={
            "crop": "Rice",
            "region": "Rangpur",
            "variety": "HYV",
            "cropping_type": "mixed",
            "rainfall_adjustment_percent": 15.0,
            "temperature_adjustment_percent": -5.0
        })
        self.assertEqual(scen_res.status_code, 200)
        scen_data = scen_res.json()
        self.assertGreater(scen_data["original_yield"], 0)
        self.assertGreater(scen_data["adjusted_yield"], 0)
        self.assertNotEqual(scen_data["original_yield"], scen_data["adjusted_yield"])

        # Community summary
        comm_res = self.client.get("/api/community", params={
            "region": "Rangpur",
            "crop": "Rice",
            "llm_prediction": 4.35
        })
        self.assertEqual(comm_res.status_code, 200)
        comm_data = comm_res.json()
        self.assertEqual(comm_data["region"], "Rangpur")
        self.assertGreater(comm_data["district_avg_value"], 0)
        self.assertGreaterEqual(len(comm_data["historical_trend"]), 5)

    def test_07_varieties_risk_and_advisory(self):
        # Varieties
        var_res = self.client.get("/api/varieties", params={"crop": "Rice"})
        self.assertEqual(var_res.status_code, 200)
        self.assertGreaterEqual(len(var_res.json()), 3)

        var_lentil = self.client.get("/api/varieties", params={"crop": "Lentil"})
        self.assertEqual(var_lentil.status_code, 200)
        self.assertGreaterEqual(len(var_lentil.json()), 2)

        # Risk thresholds
        thresh_res = self.client.get("/api/risk/thresholds", params={"crop": "Rice"})
        self.assertEqual(thresh_res.status_code, 200)
        self.assertGreaterEqual(len(thresh_res.json()), 1)

        # Risk alerts
        alerts_res = self.client.get("/api/risk/alerts", params={
            "crop": "Rice",
            "region": "Rangpur",
            "variety": "HYV"
        })
        self.assertEqual(alerts_res.status_code, 200)
        self.assertGreaterEqual(len(alerts_res.json()), 1)

        # Risk & Bangla Advisory generation
        adv_res = self.client.post("/api/advisory/generate", json={
            "crop": "Rice",
            "region": "Rangpur",
            "variety": "BRRI_28",
            "predicted_yield": 3.85,
            "cropping_type": "single"
        })
        self.assertEqual(adv_res.status_code, 200)
        adv_data = adv_res.json()
        self.assertIn(adv_data["risk_level"], ["low", "medium", "high"])
        self.assertGreaterEqual(len(adv_data["warning_alerts"]), 1)
        self.assertTrue(len(adv_data["advisory_text"]) > 10)
        self.assertIsNotNone(adv_data["id"])

        # Advisory history list
        hist_res = self.client.get("/api/advisory/history")
        self.assertEqual(hist_res.status_code, 200)
        self.assertGreaterEqual(len(hist_res.json()), 1)

        # Regional context
        ctx_res = self.client.get("/api/regional-context", params={"region": "Rangpur", "crop": "Rice"})
        self.assertEqual(ctx_res.status_code, 200)
        self.assertEqual(ctx_res.json()["region"], "Rangpur")
        self.assertGreaterEqual(ctx_res.json()["historical_years"], 10)

    def test_08_auth_personalization_ownership_and_admin(self):
        # Login as seeded farmer 'karim'
        login_res = self.client.post("/api/auth/login", json={
            "username": "karim",
            "password": "farmer123"
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # /api/auth/me
        me_res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["username"], "karim")
        user_id = me_res.json()["id"]

        # Personalization GET & POST
        pers_get = self.client.get(f"/api/personalization/{user_id}", headers=headers)
        self.assertEqual(pers_get.status_code, 200)
        self.assertIsNotNone(pers_get.json()["last_crop"])

        pers_post = self.client.post("/api/personalization/save", json={
            "user_id": user_id,
            "crop": "Potato",
            "region": "Bogura"
        }, headers=headers)
        self.assertEqual(pers_post.status_code, 200)
        self.assertTrue(pers_post.json()["success"])

        pers_me = self.client.get("/api/personalization/me", headers=headers)
        self.assertEqual(pers_me.status_code, 200)
        self.assertEqual(pers_me.json()["last_crop"], "Potato")
        self.assertEqual(pers_me.json()["last_region"], "Bogura")

        # Data Ownership: create prediction for user, list, and delete
        pred_res = self.client.post("/api/predict", json={
            "crop": "Potato",
            "region": "Bogura",
            "variety": "HYV",
            "cropping_type": "single"
        }, headers=headers)
        self.assertEqual(pred_res.status_code, 200)
        pred_id = pred_res.json()["prediction_id"]

        my_data_res = self.client.get("/api/data-ownership/my_data", headers=headers)
        self.assertEqual(my_data_res.status_code, 200)
        pred_ids = [r["prediction_id"] for r in my_data_res.json()["prediction_history"]]
        self.assertIn(str(pred_id), pred_ids)

        del_res = self.client.request(
            "DELETE",
            "/api/data-ownership/delete",
            json={"data_type": "predictions"},
            headers=headers,
        )
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(del_res.json()["success"])

        # Verify record is actually deleted in DB
        my_data_after = self.client.get("/api/data-ownership/my_data", headers=headers)
        self.assertEqual(len(my_data_after.json()["prediction_history"]), 0)

        # Login as admin and test /api/admin/users
        admin_login = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        self.assertEqual(admin_login.status_code, 200)
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        users_res = self.client.get("/api/admin/users", headers=admin_headers)
        self.assertEqual(users_res.status_code, 200)
        self.assertGreaterEqual(len(users_res.json()), 2)

    def test_09_data_sources_and_environmental_data(self):
        status_res = self.client.get("/api/data-sources/status")
        self.assertEqual(status_res.status_code, 200)
        status_json = status_res.json()
        self.assertIn("weather", status_json)
        self.assertIn("soil", status_json)
        self.assertIn("satellite", status_json)
        self.assertIn("models", status_json)
        self.assertEqual(status_json["satellite"]["regions_with_ndvi"], 64)
        self.assertGreaterEqual(status_json["models"]["trained_models_count"], 26)

        env_res = self.client.get("/api/environmental-data/Rangpur", params={"start_year": 2023, "end_year": 2024})
        self.assertEqual(env_res.status_code, 200)
        env_data = env_res.json()
        self.assertEqual(env_data["region"], "Rangpur")
        self.assertEqual(env_data["satellite"]["status"], "available")
        self.assertGreater(env_data["satellite"]["ndvi_value"], 0)


if __name__ == "__main__":
    unittest.main()
