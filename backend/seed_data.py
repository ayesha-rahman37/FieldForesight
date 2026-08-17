from database import SessionLocal, engine, Base
from models import Variety, RiskThreshold


def seed(force_update: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        varieties_data = [
            {
                "name": "BRRI Dhan 28",
                "name_bangla": "BRRI Dhan 28",
                "crop_type": "Boro Rice",
                "optimal_temp_min": 20.0,
                "optimal_temp_max": 30.0,
                "max_temp_threshold": 35.0,
                "rainfall_min_mm": 120.0,
                "rainfall_max_mm": 250.0,
                "pest_susceptibility": "High",
                "growth_duration_days": 140,
                "yield_potential_ton_ha": 6.0,
                "description_bn": "Bangladesh's most popular high-yielding Boro rice variety. Moderately susceptible to neck blast disease."
            },
            {
                "name": "BRRI Dhan 29",
                "name_bangla": "BRRI Dhan 29",
                "crop_type": "Boro Rice",
                "optimal_temp_min": 22.0,
                "optimal_temp_max": 32.0,
                "max_temp_threshold": 36.0,
                "rainfall_min_mm": 130.0,
                "rainfall_max_mm": 280.0,
                "pest_susceptibility": "Medium",
                "growth_duration_days": 160,
                "yield_potential_ton_ha": 7.5,
                "description_bn": "Long duration and highest-yielding Boro rice variety. Sensitive to heatwaves and drought during late maturity stages."
            },
            {
                "name": "BRRI Dhan 89",
                "name_bangla": "BRRI Dhan 89",
                "crop_type": "Boro Rice",
                "optimal_temp_min": 21.0,
                "optimal_temp_max": 31.0,
                "max_temp_threshold": 36.5,
                "rainfall_min_mm": 110.0,
                "rainfall_max_mm": 260.0,
                "pest_susceptibility": "Low",
                "growth_duration_days": 155,
                "yield_potential_ton_ha": 8.0,
                "description_bn": "Modern mega variety. High-yielding and disease-resistant alternative to BRRI Dhan 29."
            },
            {
                "name": "BARI Gom 33",
                "name_bangla": "BARI Gom 33",
                "crop_type": "Wheat",
                "optimal_temp_min": 15.0,
                "optimal_temp_max": 25.0,
                "max_temp_threshold": 30.0,
                "rainfall_min_mm": 50.0,
                "rainfall_max_mm": 150.0,
                "pest_susceptibility": "Low",
                "growth_duration_days": 110,
                "yield_potential_ton_ha": 4.5,
                "description_bn": "Modern wheat blast resistant variety bio-fortified with Zinc."
            },
            {
                "name": "BINA Dhan 10",
                "name_bangla": "BINA Dhan 10",
                "crop_type": "Aman Rice",
                "optimal_temp_min": 22.0,
                "optimal_temp_max": 33.0,
                "max_temp_threshold": 37.0,
                "rainfall_min_mm": 140.0,
                "rainfall_max_mm": 300.0,
                "pest_susceptibility": "Medium",
                "growth_duration_days": 130,
                "yield_potential_ton_ha": 5.5,
                "description_bn": "Modern salinity-tolerant Aman rice variety (8-10 dS/m) adapted for coastal regions."
            }
        ]

        existing = db.query(Variety).all()
        if existing:
            # Update existing records to English
            for var in existing:
                match = next((item for item in varieties_data if item["name"] == var.name), None)
                if match:
                    var.name_bangla = match["name_bangla"]
                    var.description_bn = match["description_bn"]
            db.commit()
            return

        varieties = [Variety(**item) for item in varieties_data]
        db.add_all(varieties)
        db.commit()

        for v in varieties:
            db.refresh(v)
            thresholds = [
                RiskThreshold(
                    variety_id=v.id,
                    metric_name="temperature",
                    low_max=v.optimal_temp_min,
                    medium_max=v.optimal_temp_max,
                    high_max=v.max_temp_threshold,
                    critical_min=v.max_temp_threshold + 0.1,
                    advisory_note_bn=f"For {v.name}, temperatures exceeding {v.max_temp_threshold}°C may impair pollination and spikelet fertility."
                ),
                RiskThreshold(
                    variety_id=v.id,
                    metric_name="rainfall",
                    low_max=v.rainfall_min_mm,
                    medium_max=(v.rainfall_min_mm + v.rainfall_max_mm) / 2,
                    high_max=v.rainfall_max_mm,
                    critical_min=v.rainfall_max_mm + 0.1,
                    advisory_note_bn=f"For {v.name}, prolonged drought or severe waterlogging may cause major yield deficits."
                )
            ]
            db.add_all(thresholds)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed(force_update=True)
