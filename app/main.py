from fastapi import FastAPI
from app.routes import prediction

app = FastAPI(title="FieldForesight API", version="1.0")

app.include_router(prediction.router, prefix="/api", tags=["Prediction"])

@app.get("/")
def root():
    return {"message": "FieldForesight API is running"}