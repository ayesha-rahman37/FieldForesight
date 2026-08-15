import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from database import engine, Base
from admin import register_admin
from seed_data import seed
from routers import (
    variety_router,
    risk_router,
    advisory_router,
    forecast_router,
    websocket_router
)

logger = logging.getLogger("fieldforesight")

Base.metadata.create_all(bind=engine)
try:
    seed()
except Exception as err:
    logger.warning("Database seeding skipped or encountered issue: %s", err)

app = FastAPI(
    title="FieldForesight API",
    description="Agricultural risk evaluation, forecaster, and Bangla advisory service.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin = Admin(app, engine)
register_admin(admin)

app.include_router(variety_router)
app.include_router(risk_router)
app.include_router(advisory_router)
app.include_router(forecast_router)
app.include_router(websocket_router)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "FieldForesight Risk Engine & Advisory Generator",
        "docs": "/docs",
        "admin": "/admin"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
