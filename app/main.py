from fastapi import FastAPI
<<<<<<< HEAD

from app.database import Base, engine
#from app.routes import prediction
from app.models.user_preference import UserPreference
from app.routes.community import router as community_router
from app.routes.data_ownership import router as data_ownership_router
from app.routes.explainability import router as explainability_router
from app.routes.scenario_planner import router as scenario_planner_router
from app.routes.personalization import router as personalization_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FieldForesight API", version="1.0")
#app.include_router(prediction.router, prefix="/api", tags=["Prediction"])
app.include_router(community_router, prefix="/api/community", tags=["Community"])
app.include_router(data_ownership_router, prefix="/api/data-ownership", tags=["Data Ownership"])
app.include_router(explainability_router, prefix="/api/explain", tags=["Explainability"])
app.include_router(scenario_planner_router, prefix="/api/scenario", tags=["Scenario Planner"])
app.include_router(personalization_router, prefix="/api/personalization", tags=["Personalization"])
=======
from app.routes import crops, regions  # prediction আপাতত বাদ
# from app.routes import prediction

app = FastAPI(title="FieldForesight API", version="1.0")

# app.include_router(prediction.router, prefix="/api", tags=["Prediction"])
app.include_router(crops.router, prefix="/api", tags=["Crops"])
app.include_router(regions.router, prefix="/api", tags=["Regions"])
>>>>>>> 0698a029aa38a8e6089f9dda431acff85e4b9337

@app.get("/")
def root():
    return {"message": "FieldForesight API is running"}