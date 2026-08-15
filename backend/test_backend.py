import os
import sys
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_list_varieties():
    response = client.get("/api/varieties")
    assert response.status_code == 200
    varieties = response.json()
    assert len(varieties) >= 5


def test_evaluate_risk():
    payload = {
        "variety_id": 1,
        "scenario": {
            "temperature": 37.5,
            "humidity": 85.0,
            "rainfall": 30.0,
            "wind_speed": 15.0,
            "pest_density": 35.0
        }
    }
    response = client.post("/api/risk/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["HIGH", "CRITICAL"]
    assert data["overall_risk_score"] > 50.0


def test_generate_advisory():
    payload = {
        "variety_id": 1,
        "scenario": {
            "temperature": 32.0,
            "humidity": 75.0,
            "rainfall": 100.0,
            "wind_speed": 10.0,
            "pest_density": 10.0
        }
    }
    response = client.post("/api/advisory/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "advisory_text_bn" in data
    assert "action_items_bn" in data


def test_forecast():
    response = client.get("/api/forecast?variety_id=1&days=15")
    assert response.status_code == 200
    data = response.json()
    assert len(data["points"]) == 15


if __name__ == "__main__":
    test_health_check()
    test_list_varieties()
    test_evaluate_risk()
    test_generate_advisory()
    test_forecast()
