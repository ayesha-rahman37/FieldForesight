import os

import pandas as pd

from app.database import Base, SessionLocal, engine
from app.models.crop import Crop
from app.models.historical_yield import HistoricalYield
from app.models.region import Region


Base.metadata.create_all(bind=engine)

CSV_PATH = "app/data/historical_yield.csv"
WEATHER_PATH = "app/data/weather_yearly.csv"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        column.strip().lower()
        for column in df.columns
    ]

    required_columns = {
        "year",
        "crop",
        "region",
        "yield_tons_per_hectare"
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    df["year"] = pd.to_numeric(
        df["year"],
        errors="coerce"
    )

    df["yield_tons_per_hectare"] = pd.to_numeric(
        df["yield_tons_per_hectare"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "year",
            "crop",
            "region",
            "yield_tons_per_hectare"
        ]
    )

    df["crop"] = (
        df["crop"]
        .astype(str)
        .str.strip()
    )

    df["region"] = (
        df["region"]
        .astype(str)
        .str.strip()
    )

    return df


def load_weather_data() -> pd.DataFrame:
    if not os.path.exists(WEATHER_PATH):
        raise FileNotFoundError(
            f"Weather data file not found: {WEATHER_PATH}"
        )

    weather = pd.read_csv(
        WEATHER_PATH
    )

    required_columns = {
        "year",
        "total_rainfall"
    }

    missing_columns = (
        required_columns - set(weather.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing weather columns: "
            + ", ".join(sorted(missing_columns))
        )

    weather["year"] = pd.to_numeric(
        weather["year"],
        errors="coerce"
    )

    weather["total_rainfall"] = pd.to_numeric(
        weather["total_rainfall"],
        errors="coerce"
    )

    weather = weather.dropna(
        subset=[
            "year",
            "total_rainfall"
        ]
    )

    return weather[
        [
            "year",
            "total_rainfall"
        ]
    ]


def get_or_create(
    session,
    model,
    name
):
    obj = (
        session.query(model)
        .filter_by(name=name)
        .first()
    )

    if not obj:
        obj = model(name=name)
        session.add(obj)
        session.commit()
        session.refresh(obj)

    return obj


def load_data():
    yield_df = pd.read_csv(
        CSV_PATH
    )

    yield_df = clean_data(
        yield_df
    )

    weather_df = load_weather_data()

    merged_df = yield_df.merge(
        weather_df,
        on="year",
        how="left"
    )

    session = SessionLocal()

    inserted = 0
    updated = 0

    try:
        for _, row in merged_df.iterrows():

            crop_obj = get_or_create(
                session,
                Crop,
                row["crop"]
            )

            region_obj = get_or_create(
                session,
                Region,
                row["region"]
            )

            existing = (
                session.query(HistoricalYield)
                .filter(
                    HistoricalYield.crop_id == crop_obj.id,
                    HistoricalYield.region_id == region_obj.id,
                    HistoricalYield.year == int(row["year"])
                )
                .first()
            )

            rainfall = (
                float(row["total_rainfall"])
                if not pd.isna(row["total_rainfall"])
                else None
            )

            if existing:
                existing.rainfall = rainfall
                existing.yield_value = float(
                    row["yield_tons_per_hectare"]
                )
                updated += 1

            else:
                record = HistoricalYield(
                    crop_id=crop_obj.id,
                    region_id=region_obj.id,
                    year=int(row["year"]),
                    rainfall=rainfall,
                    yield_value=float(
                        row["yield_tons_per_hectare"]
                    )
                )

                session.add(record)
                inserted += 1

        session.commit()

        print(
            f"{inserted} new records inserted."
        )

        print(
            f"{updated} existing records updated."
        )

        print(
            "Historical yield and rainfall data loaded successfully."
        )

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    load_data()