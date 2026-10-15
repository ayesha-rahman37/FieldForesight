
from datetime import datetime
from app.data.district_coordinates import DISTRICT_COORDINATES
from app.database import SessionLocal, Base, engine
from app.models.ndvi_cache import NDVICache
from app.services.helper import fetch_ndvi_for_region,classify_vegetation


def run_batch():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()


    for region_name in DISTRICT_COORDINATES:
        try:
          print(f"Fetching NDVI for {region_name}...")
          ndvi = fetch_ndvi_for_region(region_name)
          status = classify_vegetation(ndvi)
          record = db.query(NDVICache).filter(NDVICache.region_name == region_name).first()
          lat,lon = DISTRICT_COORDINATES[region_name]

          if record:
              record.ndvi_value = ndvi
              record.vegetation_status = status
              record.computed_at = datetime.now()
          else:
              record = NDVICache(
                  region_name=region_name,
                  latitude=lat,
                  longitude=lon,
                  ndvi_value=ndvi,
                  vegetation_status=status,
                  computed_at=datetime.now()
              )
              db.add(record)
          db.commit()
          print(f"  → {region_name}: NDVI={ndvi} ({status})")

        except Exception as e:
            print(f"  ✗ Failed for {region_name}: {e}")
            continue

    db.close()
    print("Batch NDVI update completed.")

if __name__ == "__main__":
    run_batch()

