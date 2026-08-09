from database import SessionLocal, engine, Base
from models import Variety, RiskThreshold, AdvisoryHistory, ForecastData

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Variety).first():
        print("Database already seeded.")
        db.close()
        return

    print("Seeding Bangladeshi Variety Dataset & Risk Thresholds...")

    varieties = [
        Variety(
            name="BRRI Dhan 28",
            name_bangla="বিআরআরআই ধান ২৮",
            crop_type="Boro Rice",
            optimal_temp_min=20.0,
            optimal_temp_max=30.0,
            max_temp_threshold=35.0,
            rainfall_min_mm=120.0,
            rainfall_max_mm=250.0,
            pest_susceptibility="High",
            growth_duration_days=140,
            yield_potential_ton_ha=6.0,
            description_bn="বাংলাদেশের সবচেয়ে জনপ্রিয় উচ্চ ফলনশীল বোরো ধানের জাত। ব্লাস্ট রোগের প্রতি সামান্য সংবেদনশীল।"
        ),
        Variety(
            name="BRRI Dhan 29",
            name_bangla="বিআরআরআই ধান ২৯",
            crop_type="Boro Rice",
            optimal_temp_min=22.0,
            optimal_temp_max=32.0,
            max_temp_threshold=36.0,
            rainfall_min_mm=130.0,
            rainfall_max_mm=280.0,
            pest_susceptibility="Medium",
            growth_duration_days=160,
            yield_potential_ton_ha=7.5,
            description_bn="দীর্ঘ মেয়াদী ও সর্বোচ্চ ফলনশীল বোরো ধান। শেষ পর্যায়ে তাপপ্রবাহ ও খরা সংবেদনশীল।"
        ),
        Variety(
            name="BRRI Dhan 89",
            name_bangla="বিআরআরআই ধান ৮৯",
            crop_type="Boro Rice",
            optimal_temp_min=21.0,
            optimal_temp_max=31.0,
            max_temp_threshold=36.5,
            rainfall_min_mm=110.0,
            rainfall_max_mm=260.0,
            pest_susceptibility="Low",
            growth_duration_days=155,
            yield_potential_ton_ha=8.0,
            description_bn="আধুনিক মেগা ভ্যারাইটি। বিআর২৯ এর বিকল্প হিসেবে উচ্চ ফলনশীল ও রোগ প্রতিরোধী।"
        ),
        Variety(
            name="BARI Gom 33",
            name_bangla="বারি গম ৩৩",
            crop_type="Wheat",
            optimal_temp_min=15.0,
            optimal_temp_max=25.0,
            max_temp_threshold=30.0,
            rainfall_min_mm=50.0,
            rainfall_max_mm=150.0,
            pest_susceptibility="Low",
            growth_duration_days=110,
            yield_potential_ton_ha=4.5,
            description_bn="গম ব্লাস্ট রোগ প্রতিরোধী ও দস্তা (Zinc) সমৃদ্ধ আধুনিক গমের জাত।"
        ),
        Variety(
            name="BINA Dhan 10",
            name_bangla="বিনা ধান ১০",
            crop_type="Aman Rice",
            optimal_temp_min=22.0,
            optimal_temp_max=33.0,
            max_temp_threshold=37.0,
            rainfall_min_mm=140.0,
            rainfall_max_mm=300.0,
            pest_susceptibility="Medium",
            growth_duration_days=130,
            yield_potential_ton_ha=5.5,
            description_bn="উপকূলীয় অঞ্চলে লবণাক্ততা সহনশীল আধুনিক আমন ধানের জাত (৮-১০ ডিএস/মি)।"
        )
    ]

    db.add_all(varieties)
    db.commit()

    # Refresh items to get IDs
    for v in varieties:
        db.refresh(v)

        # Add Threshold entries for each variety
        thresholds = [
            RiskThreshold(
                variety_id=v.id,
                metric_name="temperature",
                low_max=v.optimal_temp_min,
                medium_max=v.optimal_temp_max,
                high_max=v.max_temp_threshold,
                critical_min=v.max_temp_threshold + 0.1,
                advisory_note_bn=f"{v.name_bangla} জাতের জন্য তাপমাত্রা {v.max_temp_threshold}°C এর উপরে উঠলে পরাগায়ন ব্যাহত হতে পারে।"
            ),
            RiskThreshold(
                variety_id=v.id,
                metric_name="rainfall",
                low_max=v.rainfall_min_mm,
                medium_max=(v.rainfall_min_mm + v.rainfall_max_mm) / 2,
                high_max=v.rainfall_max_mm,
                critical_min=v.rainfall_max_mm + 0.1,
                advisory_note_bn=f"{v.name_bangla} জাতে খরা বা জলাবদ্ধতা সৃষ্টি হলে ফলন ঘাটতি ঘটতে পারে।"
            )
        ]
        db.add_all(thresholds)

    db.commit()
    print("Database seeding completed successfully.")
    db.close()

if __name__ == "__main__":
    seed()
