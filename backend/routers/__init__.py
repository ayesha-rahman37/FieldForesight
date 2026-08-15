from routers.variety_router import router as variety_router
from routers.risk_router import router as risk_router
from routers.advisory_router import router as advisory_router
from routers.forecast_router import router as forecast_router
from routers.websocket_router import router as websocket_router

__all__ = [
    "variety_router",
    "risk_router",
    "advisory_router",
    "forecast_router",
    "websocket_router",
]
