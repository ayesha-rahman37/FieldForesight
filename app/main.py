from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models as models_module  # noqa: F401
from app.models.advisory_history import AdvisoryHistory
from app.models.crop import Crop
from app.models.crop_variety import CropVariety
from app.models.explainability_cache import ExplainabilityCache
from app.models.forecast_cache import ForecastCache
from app.models.historical_yield import HistoricalYield
from app.models.mixed_cropping import MixedCroppingMapping
from app.models.model_metadata import ModelMetadata
from app.models.ndvi_cache import NDVICache
from app.models.prediction_history import PredictionHistory
from app.models.processed_dataset import ProcessedDataset
from app.models.region import Region
from app.models.risk_threshold import RiskThreshold
from app.models.role import Role
from app.models.session import UserSession
from app.models.user import User
from app.models.user_preference import UserPreference
from app.routes import (
    admin,
    auth,
    crops,
    data_sources,
    environmental_data,
    historical_data,
    history,
    mixed_crop,
    prediction,
    regions,
)
from app.routes.advisory_risk import router as advisory_risk_router
from app.routes.chat import router as chat_router
from app.routes.community import router as community_router
from app.routes.data_ownership import router as data_ownership_router
from app.routes.explainability import router as explainability_router
from app.routes.ndvi import router as ndvi_router
from app.routes.personalization import router as personalization_router
from app.routes.scenario_planner import router as scenario_planner_router
from app.routes.varieties import router as varieties_router
from app.routes.webhook_news import router as webhook_news_router
from app.scripts.load_data import load_data
from app.scripts.seed_samir_data import seed_samir_data


def initialize_database():
    Base.metadata.create_all(bind=engine)
    try:
        seed_samir_data()
    except Exception as exc:
        print(f"Warning: seed_samir_data failed: {exc}")
    try:
        load_data()
    except Exception as exc:
        print(f"Warning: load_data failed: {exc}")
    try:
        from app.services.graph_service import seed_agricultural_knowledge_graph
        seed_agricultural_knowledge_graph()
    except Exception as exc:
        print(f"Warning: seed_agricultural_knowledge_graph failed: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="FieldForesight API", version="1.0", lifespan=lifespan)

# Mount SQLAdmin interface at /admin when sqladmin is installed
try:
    import sys
    import types

    try:
        import greenlet  # noqa: F401
    except ImportError:
        _greenlet_shim = types.ModuleType("greenlet")
        _greenlet_shim.getcurrent = lambda: None  # type: ignore[attr-defined]
        _greenlet_shim.greenlet = object  # type: ignore[attr-defined]
        sys.modules["greenlet"] = _greenlet_shim

    from sqladmin import Admin, ModelView

    class UserAdmin(ModelView, model=User):
        column_list = [User.id, User.username, User.email, User.role_id, User.is_active, User.created_at]

    class RoleAdmin(ModelView, model=Role):
        column_list = [Role.id, Role.name]

    class CropAdmin(ModelView, model=Crop):
        column_list = [Crop.id, Crop.name, Crop.type]

    class RegionAdmin(ModelView, model=Region):
        column_list = [Region.id, Region.name]

    class CropVarietyAdmin(ModelView, model=CropVariety):
        column_list = [CropVariety.id, CropVariety.crop, CropVariety.variety_code, CropVariety.name_en, CropVariety.yield_coefficient]

    class HistoricalYieldAdmin(ModelView, model=HistoricalYield):
        column_list = [HistoricalYield.id, HistoricalYield.crop_id, HistoricalYield.region_id, HistoricalYield.year, HistoricalYield.rainfall, HistoricalYield.yield_value]

    class PredictionHistoryAdmin(ModelView, model=PredictionHistory):
        column_list = [PredictionHistory.id, PredictionHistory.user_id, PredictionHistory.crop, PredictionHistory.region, PredictionHistory.predicted_yield, PredictionHistory.created_at]

    class ModelMetadataAdmin(ModelView, model=ModelMetadata):
        column_list = [ModelMetadata.id, ModelMetadata.crop, ModelMetadata.region, ModelMetadata.model_version, ModelMetadata.mae, ModelMetadata.rmse, ModelMetadata.mape]

    class NDVICacheAdmin(ModelView, model=NDVICache):
        column_list = [NDVICache.id, NDVICache.region_name, NDVICache.ndvi_value, NDVICache.vegetation_status, NDVICache.computed_at]

    class RiskThresholdAdmin(ModelView, model=RiskThreshold):
        column_list = [RiskThreshold.id, RiskThreshold.crop, RiskThreshold.metric, RiskThreshold.low_threshold, RiskThreshold.medium_threshold, RiskThreshold.high_threshold]

    sql_admin = Admin(app, engine, title="FieldForesight Admin")
    for view in (
        UserAdmin,
        RoleAdmin,
        CropAdmin,
        RegionAdmin,
        CropVarietyAdmin,
        HistoricalYieldAdmin,
        PredictionHistoryAdmin,
        ModelMetadataAdmin,
        NDVICacheAdmin,
        RiskThresholdAdmin,
    ):
        sql_admin.add_view(view)
except Exception as exc:
    print(f"SQLAdmin setup skipped: {exc}")

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
origins = list(
    dict.fromkeys(
        [
            frontend_origin,
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ]
    )
)

from app.middleware.rate_limiter import SlidingWindowRateLimiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlidingWindowRateLimiter)

app.include_router(history.router, prefix="/api", tags=["Prediction History"])
app.include_router(community_router, prefix="/api/community", tags=["Community"])
app.include_router(data_ownership_router, prefix="/api/data-ownership", tags=["Data Ownership"])
app.include_router(explainability_router, prefix="/api/explain", tags=["Explainability"])
app.include_router(scenario_planner_router, prefix="/api/scenario", tags=["Scenario Planner"])
app.include_router(personalization_router, prefix="/api/personalization", tags=["Personalization"])
app.include_router(ndvi_router, prefix="/api/ndvi", tags=["NDVI"])
app.include_router(prediction.router, prefix="/api", tags=["Prediction"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(crops.router, prefix="/api", tags=["Crops"])
app.include_router(regions.router, prefix="/api", tags=["Regions"])
app.include_router(historical_data.router, prefix="/api", tags=["Historical Data"])
app.include_router(mixed_crop.router, prefix="/api", tags=["Mixed Cropping"])
app.include_router(advisory_risk_router, prefix="/api", tags=["Advisory & Risk"])
app.include_router(varieties_router, prefix="/api", tags=["Varieties"])
app.include_router(data_sources.router, prefix="/api/data-sources", tags=["Data Sources"])
app.include_router(environmental_data.router, prefix="/api/environmental-data", tags=["Environmental Data"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(webhook_news_router)


from starlette.requests import Request
from starlette.responses import JSONResponse
from app.mcp_server import mcp

class MCPAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            req = Request(scope, receive)
            expected_key = os.getenv("MCP_API_KEY", "fieldforesight-mcp-secret").strip()
            client_key = req.headers.get("x-api-key")
            auth_header = req.headers.get("authorization", "")
            if not client_key and auth_header.startswith("Bearer "):
                client_key = auth_header[7:].strip()
            if not client_key:
                client_key = req.query_params.get("api_key")

            if not expected_key or client_key != expected_key:
                response = JSONResponse(
                    {"detail": "Unauthorized: Invalid or missing MCP API key header ('x-api-key')"},
                    status_code=401,
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)

mcp_sse_app = mcp.sse_app()
app.mount("/api/mcp", MCPAuthMiddleware(mcp_sse_app))


@app.get("/")
def root():
    return {
        "message": "FieldForesight API is running",
        "version": "1.0",
        "docs": "/docs",
        "admin": "/admin",
        "mcp_sse": "/api/mcp/sse",
    }
