"""
Trains the Prophet model using real historical yield data merged with
weather data, and applies recent-anomaly weighting so that recent years
have more influence on the prediction than older years.
"""

import pandas as pd
from prophet import Prophet
import joblib
import os

DATA_DIR = os.path.join("app", "data")
YIELD_FILE = os.path.join(DATA_DIR, "historical_yield.csv")
MODEL_OUTPUT = os.path.join(DATA_DIR, "trained_model.pkl")

# How many of the most recent years should be weighted more heavily
RECENT_YEARS_COUNT = 3
# How many times to duplicate recent-year rows to increase their influence
RECENT_YEAR_WEIGHT_MULTIPLIER = 3


def load_yield_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["ds"] = pd.to_datetime(df["year"], format="%Y")
    df["y"] = df["yield_tons_per_hectare"]
    return df[["ds", "y", "year"]]


def apply_recent_anomaly_weighting(df: pd.DataFrame) -> pd.DataFrame:
    """
    Duplicates rows from the most recent years so Prophet effectively
    treats recent patterns as more important than older historical
    averages. This is a simple, explainable way to reflect
    climate-change-driven pattern shifts without needing a custom
    weighted-regression implementation.
    """
    max_year = df["year"].max()
    cutoff_year = max_year - RECENT_YEARS_COUNT + 1

    recent_rows = df[df["year"] >= cutoff_year]
    older_rows = df[df["year"] < cutoff_year]

    duplicated_recent = pd.concat(
        [recent_rows] * RECENT_YEAR_WEIGHT_MULTIPLIER, ignore_index=True
    )

    weighted_df = pd.concat([older_rows, duplicated_recent], ignore_index=True)
    weighted_df = weighted_df.sort_values("ds").reset_index(drop=True)
    return weighted_df


def train_and_save_model(filepath: str, output_path: str):
    df = load_yield_data(filepath)
    weighted_df = apply_recent_anomaly_weighting(df)

    model = Prophet(yearly_seasonality=False)
    model.fit(weighted_df[["ds", "y"]])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(model, output_path)
    print("Model trained with recent-anomaly weighting and saved to:", output_path)


if __name__ == "__main__":
    if not os.path.exists(YIELD_FILE):
        print("Yield data file not found at:", YIELD_FILE)
        print("Copy historical_yield_template.csv into app/data/ and rename it to historical_yield.csv")
        print("Fill it with real data, then run this script again.")
    else:
        train_and_save_model(YIELD_FILE, MODEL_OUTPUT)