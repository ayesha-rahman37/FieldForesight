from fastapi import FastAPI
from app.routes import crops, regions  # prediction আপাতত বাদ
# from app.routes import prediction

app = FastAPI(title="FieldForesight API", version="1.0")

# app.include_router(prediction.router, prefix="/api", tags=["Prediction"])
app.include_router(crops.router, prefix="/api", tags=["Crops"])
app.include_router(regions.router, prefix="/api", tags=["Regions"])

@app.get("/")
def root():
    return {"message": "FieldForesight API is running"}