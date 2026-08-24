# import joblib
# import os
# from app.services.adjustment_rules import apply_adjustments
#
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trained_model.pkl")
# model = joblib.load(MODEL_PATH)
#
#
# def get_prediction(crop: str, region: str, variety: str = "HYV", cropping_type: str = "single"):
#     future = model.make_future_dataframe(periods=1, freq="YE")
#     forecast = model.predict(future)
#     latest = forecast.iloc[-1]
#
#     base_yield = latest["yhat"]
#     lower = latest["yhat_lower"]
#     upper = latest["yhat_upper"]
#
#     adjusted_yield = apply_adjustments(base_yield, variety, cropping_type)
#     adjusted_lower = apply_adjustments(lower, variety, cropping_type)
#     adjusted_upper = apply_adjustments(upper, variety, cropping_type)
#
#     return {
#         "predicted_yield": adjusted_yield,
#         "lower_bound": adjusted_lower,
#         "upper_bound": adjusted_upper,
#         "message": f"Forecast ready for {crop} ({variety}, {cropping_type}) in {region}",
#     }