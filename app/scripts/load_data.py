import pandas as pd
from app.database import SessionLocal, engine, Base
from app.models.crop import Crop
from app.models.region import Region
from app.models.historical_yield import HistoricalYield

# টেবিলগুলো এখনো তৈরি না হলে তৈরি করবে
Base.metadata.create_all(bind=engine)

CSV_PATH = "app/data/raw_yield_data.csv"  # আপনার আসল CSV path বসান

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # কলামের নাম normalize (স্পেস, বড়হাতের অক্ষর সরানো)
    df.columns = [c.strip().lower() for c in df.columns]

    # প্রয়োজনীয় কলাম আছে কিনা check
    required = {"crop", "region", "year", "rainfall", "yield"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV-তে এই কলামগুলো নেই: {missing}")

    # খালি/ভুল row বাদ দেওয়া
    df = df.dropna(subset=["crop", "region", "year", "yield"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["yield"] = pd.to_numeric(df["yield"], errors="coerce")
    df["rainfall"] = pd.to_numeric(df["rainfall"], errors="coerce")
    df = df.dropna(subset=["year", "yield"])

    # crop/region নামের extra space/case বাদ
    df["crop"] = df["crop"].str.strip()
    df["region"] = df["region"].str.strip()

    return df

def get_or_create(session, model, name):
    obj = session.query(model).filter_by(name=name).first()
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

    for _, row in df.iterrows():
        crop_obj = get_or_create(session, Crop, row["crop"])
        region_obj = get_or_create(session, Region, row["region"])

        record = HistoricalYield(
            crop_id=crop_obj.id,
            region_id=region_obj.id,
            year=int(row["year"]),
            rainfall=row["rainfall"] if not pd.isna(row["rainfall"]) else None,
            yield_value=row["yield"],
        )
        session.add(record)
        inserted += 1

    session.commit()
    session.close()
    print(f"{inserted}টা row database-এ লোড হয়েছে।")

if __name__ == "__main__":
    load_data()