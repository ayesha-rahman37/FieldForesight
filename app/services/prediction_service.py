import os
import joblib

from app.services.adjustment_rules import apply_adjustments


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "trained_model.pkl"
)


def get_prediction(
    crop: str,
    region: str,
    variety: str = "HYV",
    cropping_type: str = "single"
):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Trained model not found. Please train the model first."
        )

    model = joblib.load(MODEL_PATH)

    future = model.make_future_dataframe(
        periods=1,
        freq="YE"
    )

    forecast = model.predict(future)
    latest = forecast.iloc[-1]

    base_yield = float(latest["yhat"])
    lower = float(latest["yhat_lower"])
    upper = float(latest["yhat_upper"])

    adjusted_yield = apply_adjustments(
        base_yield,
        variety,
        cropping_type
    )

    adjusted_lower = apply_adjustments(
        lower,
        variety,
        cropping_type
    )

    adjusted_upper = apply_adjustments(
        upper,
        variety,
        cropping_type
    )

    return {
        "predicted_yield": round(adjusted_yield, 2),
        "lower_bound": round(adjusted_lower, 2),
        "upper_bound": round(adjusted_upper, 2),
        "message": (
            f"Yield prediction generated for {crop} "
            f"in {region} using {variety} variety "
            f"and {cropping_type} cropping."
        )
    }