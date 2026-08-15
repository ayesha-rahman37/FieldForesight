import json
import logging
from typing import List
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from database import get_db
from models import Variety
from schemas import WeatherScenario
from services.risk_engine import evaluate_risk

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSockets"])


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


@router.websocket("/ws/scenario")
async def websocket_scenario_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_json({"error": "Invalid JSON format"}, websocket)
                continue

            variety_id = payload.get("variety_id", 1)
            scenario_dict = payload.get("scenario", {})

            try:
                scenario = WeatherScenario(**scenario_dict)
            except Exception as val_err:
                await manager.send_json({"error": f"Invalid scenario payload: {val_err}"}, websocket)
                continue

            v = db.query(Variety).filter(Variety.id == variety_id).first()
            if v:
                eval_result = evaluate_risk(v, scenario)
                await manager.send_json({
                    "type": "RISK_UPDATE",
                    "result": eval_result.model_dump()
                }, websocket)
            else:
                await manager.send_json({"error": f"Variety with ID {variety_id} not found"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as err:
        logger.error("Unexpected WebSocket error: %s", err)
        manager.disconnect(websocket)
