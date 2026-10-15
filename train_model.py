import os
from datetime import datetime

import joblib
import pandas as pd
from prophet import Prophet

from app.database import Base, SessionLocal, engine
from app.models.crop import Crop
from app.models.historical_yield import HistoricalYield
from app.models.model_metadata import ModelMetadata
from app.models.processed_dataset import ProcessedDataset
from app.models.region import Region
from app.services.feature_engineering import prepare_yield_features
from app.services.model_evaluation import evaluate_prophet_model


DATA_DIR = os.path.join(
    "app",
    "data"
)

MODEL_DIR = os.path.join(
    DATA_DIR,
    "models"
)

RECENT_YEARS_COUNT = 3
RECENT_YEAR_WEIGHT_MULTIPLIER = 3


def apply_recent_anomaly_weighting(
    df: pd.DataFrame
) -> pd.DataFrame:

    if df.empty:
        return df.copy()

    max_year = int(
        df["year"].max()
    )

    cutoff_year = (
        max_year
        - RECENT_YEARS_COUNT
        + 1
    )

    recent_rows = df[
        df["year"] >= cutoff_year
    ]

    older_rows = df[
        df["year"] < cutoff_year
    ]

    if recent_rows.empty:
        return df.sort_values(
            "ds"
        ).reset_index(
            drop=True
        )

    duplicated_recent = pd.concat(
        [recent_rows]
        * RECENT_YEAR_WEIGHT_MULTIPLIER,
        ignore_index=True
    )

    weighted_df = pd.concat(
        [
            older_rows,
            duplicated_recent
        ],
        ignore_index=True
    )

    return (
        weighted_df
        .sort_values("ds")
        .reset_index(drop=True)
    )


def make_model_filename(
    crop: str,
    region: str
) -> str:

    crop_part = (
        crop.strip()
        .lower()
        .replace(" ", "_")
    )

    region_part = (
        region.strip()
        .lower()
        .replace(" ", "_")
    )

    return (
        f"{crop_part}__{region_part}.pkl"
    )


def load_database_data(
    db
) -> pd.DataFrame:

    records = (
        db.query(
            HistoricalYield,
            Crop.name,
            Region.name
        )
        .join(
            Crop,
            HistoricalYield.crop_id == Crop.id
        )
        .join(
            Region,
            HistoricalYield.region_id == Region.id
        )
        .all()
    )

    rows = []

    for record, crop_name, region_name in records:
        rows.append(
            {
                "crop": crop_name,
                "region": region_name,
                "year": record.year,
                "rainfall": record.rainfall,
                "yield": record.yield_value
            }
        )

    return pd.DataFrame(rows)


def save_processed_dataset(
    db,
    crop: str,
    region: str,
    data: pd.DataFrame
) -> None:

    (
        db.query(ProcessedDataset)
        .filter(
            ProcessedDataset.crop == crop,
            ProcessedDataset.region == region
        )
        .delete(
            synchronize_session=False
        )
    )

    for _, row in data.iterrows():

        record = ProcessedDataset(
            crop=crop,
            region=region,
            year=int(row["year"]),
            rainfall=float(row["rainfall"]),
            yield_value=float(row["y"]),
            year_index=float(
                row["year_index"]
            ),
            lag_yield=float(
                row["lag_yield"]
            ),
            yield_change=float(
                row["yield_change"]
            ),
            rolling_yield_mean=float(
                row["rolling_yield_mean"]
            ),
            yield_anomaly=float(
                row["yield_anomaly"]
            ),
            anomaly_score=float(
                row["anomaly_score"]
            ),
            is_recent=int(
                row["is_recent"]
            )
        )

        db.add(record)


def train_models() -> None:

    Base.metadata.create_all(
        bind=engine
    )

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    db = SessionLocal()

    try:

        raw_data = load_database_data(db)

        if raw_data.empty:
            raise ValueError(
                "No historical yield data found in the database. "
                "Run app/scripts/load_data.py first."
            )

        model_version = (
            "prophet-"
            + datetime.utcnow().strftime(
                "%Y%m%d%H%M%S"
            )
        )

        grouped = raw_data.groupby(
            ["crop", "region"]
        )

        trained_count = 0

        for (crop, region), group in grouped:

            features = prepare_yield_features(
                group[
                    [
                        "year",
                        "rainfall",
                        "yield"
                    ]
                ]
            )

            if len(features) < 2:
                print(
                    f"Skipped {crop} / {region}: "
                    "not enough historical records."
                )
                continue

            save_processed_dataset(
                db,
                crop,
                region,
                features
            )

            evaluation = evaluate_prophet_model(
                features,
                apply_recent_anomaly_weighting
            )

            weighted_data = (
                apply_recent_anomaly_weighting(
                    features
                )
            )

            model = Prophet(
                yearly_seasonality=False
            )

            model.fit(
                weighted_data[
                    ["ds", "y"]
                ]
            )

            filename = make_model_filename(
                crop,
                region
            )

            model_path = os.path.join(
                MODEL_DIR,
                filename
            )

            joblib.dump(
                model,
                model_path
            )

            relative_model_path = os.path.relpath(
                model_path
            )

            metadata = ModelMetadata(
                model_name="Prophet Yield Forecast",
                model_version=model_version,
                crop=crop,
                region=region,
                model_path=relative_model_path,
                training_records=len(features),
                mae=evaluation["mae"],
                rmse=evaluation["rmse"],
                mape=evaluation["mape"],
                recent_weighting_enabled=True
            )

            db.add(metadata)

            trained_count += 1

            print(
                f"Trained model for {crop} / {region}"
            )

        db.commit()

        print(
            f"Training completed for {trained_count} crop-region models."
        )

    finally:
        db.close()


if __name__ == "__main__":
    train_models()