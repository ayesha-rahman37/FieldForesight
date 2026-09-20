import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI
from app.database import Base, engine
from app.models.user_preference import UserPreference
from app.models.user import User
from app.models.role import Role
from app.models.session import UserSession
from app.routes.community import router as community_router
from app.routes.data_ownership import router as data_ownership_router
from app.routes.explainability import router as explainability_router
from app.routes.scenario_planner import router as scenario_planner_router
from app.routes.personalization import router as personalization_router
from app.routes.ndvi import router as ndvi_router
from app.routes import prediction
from app.models.prediction_history import PredictionHistory
from app.routes import history
from app.routes import auth
from app.routes import historical_data


Base.metadata.create_all(bind=engine)
from app.routes import crops, regions  # prediction আপাতত বাদ
app = FastAPI(title="FieldForesight API", version="1.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

app.include_router(history.router, prefix="/api", tags=["Prediction History"])
app.include_router(community_router, prefix="/api/community", tags=["Community"])
app.include_router(data_ownership_router, prefix="/api/data-ownership", tags=["Data Ownership"])
app.include_router(explainability_router, prefix="/api/explain", tags=["Explainability"])
app.include_router(scenario_planner_router, prefix="/api/scenario", tags=["Scenario Planner"])
app.include_router(personalization_router, prefix="/api/personalization", tags=["Personalization"])
app.include_router(ndvi_router, prefix="/api/ndvi", tags=["NDVI"])
app.include_router(prediction.router, prefix="/api", tags=["Prediction"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(crops.router, prefix="/api", tags=["Crops"])
app.include_router(regions.router, prefix="/api", tags=["Regions"])
app.include_router(historical_data.router, prefix="/api", tags=["Historical Data"])


@app.get("/")
def root():
    return FileResponse(
        os.path.join(BASE_DIR, "templates", "index.html")
    )