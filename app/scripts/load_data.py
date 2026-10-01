import pandas as pd

from app.database import Base, SessionLocal, engine
from app.models.crop import Crop
from app.models.historical_yield import HistoricalYield
from app.models.region import Region


Base.metadata.create_all(bind=engine)

CSV_PATH = "app/data/historical_yield.csv"


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
    df = pd.read_csv(CSV_PATH)

    df = clean_data(df)

    session = SessionLocal()
    inserted = 0

    try:
        for _, row in df.iterrows():

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

            record = HistoricalYield(
                crop_id=crop_obj.id,
                region_id=region_obj.id,
                year=int(row["year"]),
                rainfall=None,
                yield_value=float(
                    row["yield_tons_per_hectare"]
                )
            )

            session.add(record)
            inserted += 1

        session.commit()

        print(
            f"{inserted} historical yield records loaded successfully."
        )

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    load_data()