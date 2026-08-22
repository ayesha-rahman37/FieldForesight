import pandas as pd
from prophet import Prophet
import joblib
import os

# Dummy dataset — replace with real historical data later
data = pd.DataFrame({
    "ds": pd.date_range(start="2016-01-01", periods=9, freq="YE"),
    "y": [4.1, 4.3, 4.0, 4.5, 4.6, 4.2, 4.8, 4.7, 4.9]
})

model = Prophet()
model.fit(data)

output_path = os.path.join("app", "data", "trained_model.pkl")
joblib.dump(model, output_path)
print("Model trained and saved:", output_path)