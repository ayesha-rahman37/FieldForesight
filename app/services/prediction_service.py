import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trained_model.pkl")
model = joblib.load(MODEL_PATH)

def get_prediction(crop: str, region: str, variety: str):
    future = model.make_future_dataframe(periods=1, freq="YE")
    forecast = model.predict(future)
    latest = forecast.iloc[-1]

    return {
        "predicted_yield": round(latest["yhat"], 2),
        "lower_bound": round(latest["yhat_lower"], 2),
        "upper_bound": round(latest["yhat_upper"], 2),
        "message": f"Forecast ready for {crop} in {region}"
    }