import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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

# Mount static assets
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(CURRENT_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

admin = Admin(app, engine)
register_admin(admin)

app.include_router(variety_router)
app.include_router(risk_router)
app.include_router(advisory_router)
app.include_router(forecast_router)
app.include_router(websocket_router)


@app.get("/")
def root(request: Request):
    accept_header = request.headers.get("accept", "")
    index_path = os.path.join(STATIC_DIR, "index.html")

    # If the request comes from a browser or explicitly asks for HTML
    if "text/html" in accept_header and os.path.exists(index_path):
        return FileResponse(index_path)

    # Return JSON API status for programmatic/testing clients
    return {
        "status": "online",
        "service": "FieldForesight Risk Engine & Advisory Generator",
        "docs": "/docs",
        "admin": "/admin",
        "dashboard": "/"
    }


@app.get("/dashboard")
@app.get("/app")
def dashboard_view():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"error": "Dashboard static files not found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

