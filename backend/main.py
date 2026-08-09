import json
import asyncio
from typing import List
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqladmin import Admin

from database import engine, Base, get_db
from models import Variety, RiskThreshold, AdvisoryHistory, ForecastData
from schemas import (
    VarietyResponse, VarietyCreate, RiskThresholdResponse,
    WeatherScenario, RiskEvaluationResult, AdvisoryRequest, AdvisoryResponse, ForecastResponse
)
from services.risk_engine import evaluate_risk
from services.groq_advisory import generate_bangla_advisory
from services.forecaster import run_prophet_or_fallback_forecast
from admin import register_admin
from seed_data import seed

# Auto create tables and seed DB
Base.metadata.create_all(bind=engine)
try:
    seed()
except Exception as e:
    print(f"Seed warning: {e}")

app = FastAPI(
    title="FieldForesight API — Risk Alert & Bangla Advisory Service",
    description="Group 3 (Samir) — Risk Alert Logic, Groq Advisory Generator, Variety Parameter Dataset, Prophet Forecaster, & WebSockets",
    version="1.0.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAdmin Integration
admin = Admin(app, engine)
register_admin(admin)


# --- REST API Endpoints ---

@app.get("/")
def root():
    return {
        "status": "online",
        "app": "FieldForesight Risk Engine & Advisory Generator",
        "group": "Group 3 — Samir",
        "docs": "/docs",
        "admin": "/admin"
    }

@app.get("/api/varieties", response_model=List[VarietyResponse])
def list_varieties(db: Session = Depends(get_db)):
    return db.query(Variety).all()

@app.get("/api/varieties/{variety_id}", response_model=VarietyResponse)
def get_variety(variety_id: int, db: Session = Depends(get_db)):
    v = db.query(Variety).filter(Variety.id == variety_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Variety not found")
    return v

@app.post("/api/varieties", response_model=VarietyResponse)
def create_variety(variety_in: VarietyCreate, db: Session = Depends(get_db)):
    v = Variety(**variety_in.model_dump())
    db.add(v)
    db.commit()
    db.refresh(v)
    return v

@app.get("/api/thresholds", response_model=List[RiskThresholdResponse])
def list_thresholds(variety_id: int = None, db: Session = Depends(get_db)):
    query = db.query(RiskThreshold)
    if variety_id:
        query = query.filter(RiskThreshold.variety_id == variety_id)
    return query.all()

@app.post("/api/risk/evaluate", response_model=RiskEvaluationResult)
def evaluate_risk_endpoint(request: AdvisoryRequest, db: Session = Depends(get_db)):
    v = db.query(Variety).filter(Variety.id == request.variety_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Variety not found")
    return evaluate_risk(v, request.scenario)

@app.post("/api/advisory/generate", response_model=AdvisoryResponse)
def generate_advisory_endpoint(request: AdvisoryRequest, db: Session = Depends(get_db)):
    v = db.query(Variety).filter(Variety.id == request.variety_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Variety not found")

    eval_result = evaluate_risk(v, request.scenario)
    advisory_content = generate_bangla_advisory(v, eval_result)

    # Store history entry in DB
    history_entry = AdvisoryHistory(
        variety_id=v.id,
        risk_level=eval_result.risk_level,
        weather_scenario_json=request.scenario.model_dump(),
        advisory_text_bn=advisory_content["advisory_text_bn"],
        action_items_json=advisory_content.get("action_items_bn", []),
        llm_provider=advisory_content.get("llm_provider", "Rule-Engine Fallback")
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)

    return AdvisoryResponse(
        id=history_entry.id,
        variety_id=v.id,
        variety_name=v.name,
        variety_name_bangla=v.name_bangla,
        risk_level=eval_result.risk_level,
        advisory_text_bn=advisory_content["advisory_text_bn"],
        action_items_bn=advisory_content.get("action_items_bn", []),
        irrigation_advice_bn=advisory_content.get("irrigation_advice_bn", ""),
        pest_advice_bn=advisory_content.get("pest_advice_bn", ""),
        llm_provider=advisory_content.get("llm_provider", "Rule-Engine Fallback"),
        created_at=history_entry.created_at
    )

@app.get("/api/advisory/history", response_model=List[AdvisoryResponse])
def get_advisory_history(variety_id: int = None, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(AdvisoryHistory)
    if variety_id:
        query = query.filter(AdvisoryHistory.variety_id == variety_id)
    records = query.order_by(AdvisoryHistory.created_at.desc()).limit(limit).all()

    results = []
    for r in records:
        v = r.variety
        results.append(
            AdvisoryResponse(
                id=r.id,
                variety_id=r.variety_id,
                variety_name=v.name if v else "Unknown",
                variety_name_bangla=v.name_bangla if v else "অজানা জাত",
                risk_level=r.risk_level,
                advisory_text_bn=r.advisory_text_bn,
                action_items_bn=r.action_items_json or [],
                irrigation_advice_bn="",
                pest_advice_bn="",
                llm_provider=r.llm_provider,
                created_at=r.created_at
            )
        )
    return results

@app.get("/api/forecast", response_model=ForecastResponse)
def get_forecast(variety_id: int, metric_type: str = "yield_index", days: int = 30, db: Session = Depends(get_db)):
    v = db.query(Variety).filter(Variety.id == variety_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Variety not found")

    return run_prophet_or_fallback_forecast(v, metric_type=metric_type, days=days)


# --- WebSocket Endpoint for Real-time Scenario Slider ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/scenario")
async def websocket_scenario_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            # Expecting payload: {"variety_id": 1, "scenario": {"temperature": 32, "humidity": 70, "rainfall": 150, "wind_speed": 12, "pest_density": 10}}
            variety_id = payload.get("variety_id", 1)
            scenario_dict = payload.get("scenario", {})

            scenario = WeatherScenario(**scenario_dict)
            v = db.query(Variety).filter(Variety.id == variety_id).first()
            if v:
                eval_result = evaluate_risk(v, scenario)
                await manager.send_json({
                    "type": "RISK_UPDATE",
                    "result": eval_result.model_dump()
                }, websocket)
            else:
                await manager.send_json({"error": "Variety not found"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
