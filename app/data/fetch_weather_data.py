"""
Fetches historical rainfall and temperature data from NASA POWER API
for a given region (latitude/longitude) in Bangladesh.
No API key required - this is a free public API.
"""

import requests
import pandas as pd
import os

# Example coordinates - Rangpur, Bangladesh
# Replace with the region you want to collect data for
LATITUDE = 25.7439
LONGITUDE = 89.2752

START_YEAR = 2015
END_YEAR = 2025

def fetch_weather_data(lat: float, lon: float, start_year: int, end_year: int):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"

    params = {
        "parameters": "T2M,PRECTOTCORR",  # Temperature and Precipitation
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": f"{start_year}0101",
        "end": f"{end_year}1231",
        "format": "JSON"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    records = data["properties"]["parameter"]
    dates = list(records["T2M"].keys())

    df = pd.DataFrame({
        "date": dates,
        "temperature": [records["T2M"][d] for d in dates],
        "rainfall": [records["PRECTOTCORR"][d] for d in dates],
    })

    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    return df


def aggregate_to_yearly(df: pd.DataFrame):
    df["year"] = df["date"].dt.year
    yearly = df.groupby("year").agg(
        avg_temperature=("temperature", "mean"),
        total_rainfall=("rainfall", "sum"),
    ).reset_index()
    return yearly


if __name__ == "__main__":
    print("Fetching weather data from NASA POWER API...")
    daily_df = fetch_weather_data(LATITUDE, LONGITUDE, START_YEAR, END_YEAR)

    output_dir = os.path.join("app", "data")
    os.makedirs(output_dir, exist_ok=True)

    daily_path = os.path.join(output_dir, "weather_daily.csv")
    daily_df.to_csv(daily_path, index=False)
    print("Daily weather data saved to:", daily_path)

    yearly_df = aggregate_to_yearly(daily_df)
    yearly_path = os.path.join(output_dir, "weather_yearly.csv")
    yearly_df.to_csv(yearly_path, index=False)
    print("Yearly aggregated data saved to:", yearly_path)
    print(yearly_df)

