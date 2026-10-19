"""
Seed script for Samir module:
1. Prepopulates RiskThreshold table with standard agricultural thresholds for Bangladesh
2. Prepopulates CropVariety table with certified BRRI, BARI & local varieties
"""

from app.database import SessionLocal, engine, Base
from app.models.risk_threshold import RiskThreshold
from app.models.crop_variety import CropVariety

Base.metadata.create_all(bind=engine)

DEFAULT_THRESHOLDS = [
    # Rice thresholds (in ton/ha)
    {
        "crop": "Rice",
        "region": "All",
        "metric": "predicted_yield_min",
        "low_threshold": 4.5,      # >= 4.5 is Low Risk (Good)
        "medium_threshold": 3.5,   # 3.5 - 4.5 is Medium Risk
        "high_threshold": 3.0,     # < 3.5 is High Risk
        "unit": "ton/ha",
        "description_bn": "ধানের স্বাভাবিক ন্যূনতম ফলন থ্রেশহোল্ড (টন/হেক্টর)",
        "description_en": "Standard baseline yield threshold for Rice (ton/ha)",
    },
    {
        "crop": "Rice",
        "region": "All",
        "metric": "lower_bound_deficit_pct",
        "low_threshold": 5.0,      # Deficit < 5% = Low Risk
        "medium_threshold": 15.0,  # Deficit 5-15% = Medium Risk
        "high_threshold": 25.0,    # Deficit > 15% = High Risk
        "unit": "%",
        "description_bn": "পূর্বাভাসকৃত ফলনের নিম্নসীমা ঘাটতি শতকরা হার",
        "description_en": "Lower bound forecast deficit percentage",
    },
    # Wheat thresholds
    {
        "crop": "Wheat",
        "region": "All",
        "metric": "predicted_yield_min",
        "low_threshold": 3.2,
        "medium_threshold": 2.4,
        "high_threshold": 1.8,
        "unit": "ton/ha",
        "description_bn": "গমের স্বাভাবিক ফলন থ্রেশহোল্ড (টন/হেক্টর)",
        "description_en": "Standard baseline yield threshold for Wheat (ton/ha)",
    },
    # Potato thresholds
    {
        "crop": "Potato",
        "region": "All",
        "metric": "predicted_yield_min",
        "low_threshold": 22.0,
        "medium_threshold": 18.0,
        "high_threshold": 14.0,
        "unit": "ton/ha",
        "description_bn": "আলুর স্বাভাবিক ফলন থ্রেশহোল্ড (টন/হেক্টর)",
        "description_en": "Standard baseline yield threshold for Potato (ton/ha)",
    },
    # Maize thresholds
    {
        "crop": "Maize",
        "region": "All",
        "metric": "predicted_yield_min",
        "low_threshold": 8.0,
        "medium_threshold": 6.5,
        "high_threshold": 5.0,
        "unit": "ton/ha",
        "description_bn": "ভুট্টার স্বাভাবিক ফলন থ্রেশহোল্ড (টন/হেক্টর)",
        "description_en": "Standard baseline yield threshold for Maize (ton/ha)",
    },
    # Mustard thresholds
    {
        "crop": "Mustard",
        "region": "All",
        "metric": "predicted_yield_min",
        "low_threshold": 1.6,
        "medium_threshold": 1.2,
        "high_threshold": 0.9,
        "unit": "ton/ha",
        "description_bn": "সরিষার স্বাভাবিক ফলন থ্রেশহোল্ড (টন/হেক্টর)",
        "description_en": "Standard baseline yield threshold for Mustard (ton/ha)",
    },
    # Jute thresholds
    {
        "crop": "Jute",
        "region": "All",
        "metric": "predicted_yield_min",
        "low_threshold": 2.8,
        "medium_threshold": 2.2,
        "high_threshold": 1.6,
        "unit": "ton/ha",
        "description_bn": "পাটের আঁশের স্বাভাবিক ফলন থ্রেশহোল্ড (টন/হেক্টর)",
        "description_en": "Standard baseline yield threshold for Jute (ton/ha)",
    },
    # General NDVI Threshold
    {
        "crop": "All",
        "region": "All",
        "metric": "ndvi_vegetation_index",
        "low_threshold": 0.55,     # > 0.55 vigorous canopy (Low Risk)
        "medium_threshold": 0.38,  # 0.38 - 0.55 average (Medium Risk)
        "high_threshold": 0.25,    # < 0.38 sparse/stressed (High Risk)
        "unit": "index",
        "description_bn": "স্যাটেলাইট এনডিভিআই সূচক থ্রেশহোল্ড",
        "description_en": "Satellite NDVI canopy vegetation index threshold",
    },
]

DEFAULT_VARIETIES = [
    # ---------------- Rice Varieties (BRRI / BINA / Local) ----------------
    {
        "crop": "Rice",
        "variety_code": "HYV",
        "name_en": "High Yielding Variety (HYV Standard)",
        "name_bn": "উচ্চ ফলনশীল জাত (সাধারণ HYV)",
        "variety_type": "HYV",
        "yield_coefficient": 1.0,
        "potential_yield_min": 4.5,
        "potential_yield_max": 6.2,
        "maturity_days": 145,
        "season": "All",
        "stress_tolerance": "Standard",
        "description_bn": "বাংলাদেশ ধান গবেষণা ইনস্টিটিউট কর্তৃক উদ্ভাবিত মানসম্মত উচ্চ ফলনশীল জাত।",
        "description_en": "Certified standard High Yielding Variety developed by BRRI.",
        "is_recommended": True,
    },
    {
        "crop": "Rice",
        "variety_code": "BRRI_DHAN_28",
        "name_en": "BRRI dhan28",
        "name_bn": "ব্রি ধান২৮ (স্বল্পমেয়াদী বোরো)",
        "variety_type": "HYV",
        "yield_coefficient": 1.02,
        "potential_yield_min": 5.0,
        "potential_yield_max": 6.0,
        "maturity_days": 140,
        "season": "Boro",
        "stress_tolerance": "Standard",
        "description_bn": "স্বল্প জীবনকালবিশিষ্ট জনপ্রিয় বোরো জাত। রোগবালাই বিশেষ করে শীথ ব্লাইট ও নেক ব্লাস্ট পর্যবেক্ষণ জরুরি।",
        "description_en": "Early maturing popular Boro rice. Requires alert monitoring against sheath blight and neck blast.",
        "is_recommended": True,
    },
    {
        "crop": "Rice",
        "variety_code": "BRRI_DHAN_29",
        "name_en": "BRRI dhan29",
        "name_bn": "ব্রি ধান২৯ (মেগা ভ্যারাইটি)",
        "variety_type": "HYV",
        "yield_coefficient": 1.15,
        "potential_yield_min": 6.0,
        "potential_yield_max": 7.5,
        "maturity_days": 160,
        "season": "Boro",
        "stress_tolerance": "Standard",
        "description_bn": "বাংলাদেশের সর্বাধিক ফলনশীল দীর্ঘমেয়াদী বোরো জাত। সুষম সার ও নিয়মিত সেচে সর্বোচ্চ ফলন দেয়।",
        "description_en": "Highest yielding mega variety for Boro season in Bangladesh. Requires sustained irrigation.",
        "is_recommended": True,
    },
    {
        "crop": "Rice",
        "variety_code": "BRRI_DHAN_89",
        "name_en": "BRRI dhan89",
        "name_bn": "ব্রি ধান৮৯ (উচ্চ ফলনশীল আধুনিক)",
        "variety_type": "HYV",
        "yield_coefficient": 1.18,
        "potential_yield_min": 6.5,
        "potential_yield_max": 8.0,
        "maturity_days": 155,
        "season": "Boro",
        "stress_tolerance": "Standard",
        "description_bn": "ব্রি ধান২৯ এর বিকল্প আধুনিক জাত, উচ্চ ফলন ও রোগ প্রতিরোধ ক্ষমতা বেশি।",
        "description_en": "Modern successor to BRRI 29 with high yield potential and superior lodging resistance.",
        "is_recommended": True,
    },
    {
        "crop": "Rice",
        "variety_code": "BANGABANDHU_100",
        "name_en": "Bangabandhu dhan100",
        "name_bn": "বঙ্গবন্ধু ধান১০০ (জিঙ্ক সমৃদ্ধ)",
        "variety_type": "HYV",
        "yield_coefficient": 1.08,
        "potential_yield_min": 5.8,
        "potential_yield_max": 7.0,
        "maturity_days": 148,
        "season": "Boro",
        "stress_tolerance": "Standard",
        "description_bn": "জিঙ্ক সমৃদ্ধ উচ্চ পুষ্টিগুণসম্পন্ন বোরো জাত। চাল সরু ও সুস্বাদু।",
        "description_en": "Zinc biofortified high yielding Boro rice with excellent grain quality.",
        "is_recommended": True,
    },
    {
        "crop": "Rice",
        "variety_code": "BRRI_DHAN_67",
        "name_en": "BRRI dhan67 (Salt Tolerant)",
        "name_bn": "ব্রি ধান৬৭ (লবণাক্ততা সহনশীল)",
        "variety_type": "Stress-Tolerant",
        "yield_coefficient": 1.04,
        "potential_yield_min": 5.2,
        "potential_yield_max": 6.5,
        "maturity_days": 145,
        "season": "Boro",
        "stress_tolerance": "Saline",
        "description_bn": "উপকূলীয় অঞ্চলে ৮-১২ ডিএস/মিটার পর্যন্ত লবণাক্ততা সহ্য করতে সক্ষম।",
        "description_en": "Salt tolerant up to 8-12 dS/m, ideal for southern coastal belt (Khulna, Barishal, Satkhira).",
        "is_recommended": True,
    },
    {
        "crop": "Rice",
        "variety_code": "BRRI_DHAN_51",
        "name_en": "BRRI dhan51 (Submergence Tolerant)",
        "name_bn": "ব্রি ধান৫১ (জলমগ্নতা/বন্যা সহনশীল)",
        "variety_type": "Stress-Tolerant",
        "yield_coefficient": 0.98,
        "potential_yield_min": 4.2,
        "potential_yield_max": 5.2,
        "maturity_days": 142,
        "season": "Aman",
        "stress_tolerance": "Submergence",
        "description_bn": "বন্যার পানিতে টানা ২ সপ্তাহ সম্পূর্ণ ডুবে থাকলেও বাঁচে (SUB1 জিনযুক্ত)।",
        "description_en": "Submergence tolerant up to 14 days of complete flash flooding.",
        "is_recommended": True,
    },
    {
        "crop": "Rice",
        "variety_code": "BRRI_DHAN_56",
        "name_en": "BRRI dhan56 (Drought Tolerant)",
        "name_bn": "ব্রি ধান৫৬ (খরা সহনশীল আমন)",
        "variety_type": "Stress-Tolerant",
        "yield_coefficient": 0.96,
        "potential_yield_min": 4.0,
        "potential_yield_max": 5.0,
        "maturity_days": 115,
        "season": "Aman",
        "stress_tolerance": "Drought",
        "description_bn": "বরেন্দ্র ও উত্তরাঞ্চলের খরা প্রবণ এলাকায় দ্রুত পেকে ঘরে তোলা যায়।",
        "description_en": "Drought tolerant short-duration Aman rice for Barind tract (Rajshahi, Rangpur).",
        "is_recommended": True,
    },
    {
        "crop": "Rice",
        "variety_code": "Local",
        "name_en": "Local Traditional Cultivar",
        "name_bn": "স্থানীয় দেশি জাত (নাজিরশাইল/কালিজিরে)",
        "variety_type": "Local",
        "yield_coefficient": 0.82,
        "potential_yield_min": 2.5,
        "potential_yield_max": 3.8,
        "maturity_days": 135,
        "season": "All",
        "stress_tolerance": "Standard",
        "description_bn": "চিরাচরিত দেশীয় জাত। ফলন অপেক্ষাকৃত কম হলেও স্বাদ ও স্থানীয় অভিযোজন ভালো।",
        "description_en": "Traditional indigenous varieties. Lower yield ceiling but adaptable.",
        "is_recommended": False,
    },

    # ---------------- Wheat Varieties (BARI Gom) ----------------
    {
        "crop": "Wheat",
        "variety_code": "HYV",
        "name_en": "BARI Gom (Standard HYV)",
        "name_bn": "বারি গম (উচ্চ ফলনশীল সাধারণ)",
        "variety_type": "HYV",
        "yield_coefficient": 1.0,
        "potential_yield_min": 3.5,
        "potential_yield_max": 4.5,
        "maturity_days": 105,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "বাংলাদেশ কৃষি গবেষণা ইনস্টিটিউট উদ্ভাবিত মানসম্মত গমের জাত।",
        "description_en": "Standard BARI certified high yielding wheat variety.",
        "is_recommended": True,
    },
    {
        "crop": "Wheat",
        "variety_code": "BARI_GOM_33",
        "name_en": "BARI Gom-33 (Blast Resistant & Zinc Rich)",
        "name_bn": "বারি গম-৩৩ (ব্লাস্ট প্রতিরোধী ও জিঙ্ক সমৃদ্ধ)",
        "variety_type": "HYV",
        "yield_coefficient": 1.12,
        "potential_yield_min": 4.0,
        "potential_yield_max": 5.0,
        "maturity_days": 110,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "মারাত্মক গম ব্লাস্ট রোগ প্রতিরোধী ও জিঙ্ক সমৃদ্ধ জনপ্রিয় জাত।",
        "description_en": "Blast-resistant, biofortified with Zinc, highly recommended for Meherpur/Jessore.",
        "is_recommended": True,
    },
    {
        "crop": "Wheat",
        "variety_code": "BARI_GOM_25",
        "name_en": "BARI Gom-25 (Saline Tolerant)",
        "name_bn": "বারি গম-২৫ (লবণাক্ততা সহনশীল)",
        "variety_type": "Stress-Tolerant",
        "yield_coefficient": 1.05,
        "potential_yield_min": 3.6,
        "potential_yield_max": 4.4,
        "maturity_days": 105,
        "season": "Rabi",
        "stress_tolerance": "Saline",
        "description_bn": "দক্ষিণাঞ্চলের মৃদু লবণাক্ত জমিতে ভালো ফলন দিতে সক্ষম।",
        "description_en": "Tolerates moderate soil salinity in southern districts.",
        "is_recommended": True,
    },
    {
        "crop": "Wheat",
        "variety_code": "Local",
        "name_en": "Local Deshi Wheat",
        "name_bn": "স্থানীয় দেশি গম",
        "variety_type": "Local",
        "yield_coefficient": 0.82,
        "potential_yield_min": 2.0,
        "potential_yield_max": 2.8,
        "maturity_days": 100,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "স্থানীয় প্রচলিত গম জাত, ফলন কম।",
        "description_en": "Traditional local wheat seed.",
        "is_recommended": False,
    },

    # ---------------- Potato Varieties (BARI Alu) ----------------
    {
        "crop": "Potato",
        "variety_code": "HYV",
        "name_en": "BARI Alu-7 / Diamant (HYV Standard)",
        "name_bn": "বারি আলু-৭ / ডায়মন্ট (জনপ্রিয় HYV)",
        "variety_type": "HYV",
        "yield_coefficient": 1.0,
        "potential_yield_min": 25.0,
        "potential_yield_max": 32.0,
        "maturity_days": 90,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "বাংলাদেশের সর্বাধিক আবাদকৃত সাদা গোল আলু। বাজারে ব্যাপক চাহিদা।",
        "description_en": "Most popular white table potato (Diamant) in Bangladesh.",
        "is_recommended": True,
    },
    {
        "crop": "Potato",
        "variety_code": "BARI_ALU_25",
        "name_en": "BARI Alu-25 / Asterix (Red Skin)",
        "name_bn": "বারি আলু-২৫ / এস্টারিক্স (লাল আলু)",
        "variety_type": "HYV",
        "yield_coefficient": 1.08,
        "potential_yield_min": 26.0,
        "potential_yield_max": 35.0,
        "maturity_days": 95,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "লাল খোসার দীর্ঘ সংরক্ষণযোগ্য ও লেট ব্লাইট সহনশীল উন্নত জাত।",
        "description_en": "Red skin processing potato with moderate late blight resistance.",
        "is_recommended": True,
    },
    {
        "crop": "Potato",
        "variety_code": "Local",
        "name_en": "Local Indigenous Potato (Sheel/Lal Pakri)",
        "name_bn": "স্থানীয় দেশি লাল শীল আলু",
        "variety_type": "Local",
        "yield_coefficient": 0.78,
        "potential_yield_min": 14.0,
        "potential_yield_max": 18.0,
        "maturity_days": 85,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "দেশি ছোট জাতের আলু। ফলন কম কিন্তু স্বাদ চমৎকার।",
        "description_en": "Indigenous small red potato cultivar.",
        "is_recommended": False,
    },

    # ---------------- Maize Varieties ----------------
    {
        "crop": "Maize",
        "variety_code": "HYV",
        "name_en": "Hybrid Maize (Standard High Yield)",
        "name_bn": "হাইব্রিড ভুট্টা (উচ্চ ফলনশীল)",
        "variety_type": "Hybrid",
        "yield_coefficient": 1.0,
        "potential_yield_min": 8.5,
        "potential_yield_max": 11.0,
        "maturity_days": 135,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "দানার আকার বড় ও পুষ্ট। পোল্ট্রি ও মাছের খাদ্যের জন্য উপযোগী।",
        "description_en": "Certified hybrid maize with high biomass and grain output.",
        "is_recommended": True,
    },
    {
        "crop": "Maize",
        "variety_code": "BARI_BHUTTA_9",
        "name_en": "BARI Hybrid Bhutta-9",
        "name_bn": "বারি হাইব্রিড ভুট্টা-৯",
        "variety_type": "Hybrid",
        "yield_coefficient": 1.10,
        "potential_yield_min": 9.5,
        "potential_yield_max": 12.5,
        "maturity_days": 140,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "বারি উদ্ভাবিত সর্বোচ্চ ফলনশীল হলুদ দানার হাইব্রিড ভুট্টা।",
        "description_en": "BARI release with 10+ ton/ha potential under balanced irrigation.",
        "is_recommended": True,
    },
    {
        "crop": "Maize",
        "variety_code": "Local",
        "name_en": "Composite / Local Maize",
        "name_bn": "স্থানীয় কম্পোজিট ভুট্টা",
        "variety_type": "Local",
        "yield_coefficient": 0.82,
        "potential_yield_min": 5.0,
        "potential_yield_max": 6.8,
        "maturity_days": 120,
        "season": "All",
        "stress_tolerance": "Standard",
        "description_bn": "খোলা পরাগায়িত জাত, ফলন কম।",
        "description_en": "Open pollinated composite variety.",
        "is_recommended": False,
    },

    # ---------------- Mustard Varieties ----------------
    {
        "crop": "Mustard",
        "variety_code": "HYV",
        "name_en": "BARI Sarisha-14 (Early Maturing HYV)",
        "name_bn": "বারি সরিষা-১৪ (স্বল্পমেয়াদী HYV)",
        "variety_type": "HYV",
        "yield_coefficient": 1.0,
        "potential_yield_min": 1.4,
        "potential_yield_max": 1.8,
        "maturity_days": 80,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "মাত্র ৭৫-৮০ দিনে পাকে। আমন ও বোরোর মধ্যবর্তী সময়ে চমৎকার আবাদযোগ্য।",
        "description_en": "Short duration 75-80 days mustard ideal for rice-fallow-rice cropping.",
        "is_recommended": True,
    },
    {
        "crop": "Mustard",
        "variety_code": "Local",
        "name_en": "Tori-7 / Local Mustard",
        "name_bn": "টোরি-৭ / দেশি মাঘী সরিষা",
        "variety_type": "Local",
        "yield_coefficient": 0.80,
        "potential_yield_min": 0.9,
        "potential_yield_max": 1.2,
        "maturity_days": 75,
        "season": "Rabi",
        "stress_tolerance": "Standard",
        "description_bn": "ঐতিহ্যবাহী দেশি জাত। তেল বেশি কিন্তু ফলন কম।",
        "description_en": "Traditional Tori-7 cultivar.",
        "is_recommended": False,
    },

    # ---------------- Jute Varieties ----------------
    {
        "crop": "Jute",
        "variety_code": "HYV",
        "name_en": "BJRI Tossa Pat-8 (Robi-1 HYV)",
        "name_bn": "বিজেআরআই তোষা পাট-৮ (রবি-১)",
        "variety_type": "HYV",
        "yield_coefficient": 1.0,
        "potential_yield_min": 3.0,
        "potential_yield_max": 4.0,
        "maturity_days": 120,
        "season": "Kharif",
        "stress_tolerance": "Standard",
        "description_bn": "উন্নত সোনালী আঁশ ও উচ্চ ফলনশীল তোষা পাটের আধুনিক জাত।",
        "description_en": "Modern certified golden fibre Tossa jute by BJRI.",
        "is_recommended": True,
    },
    {
        "crop": "Jute",
        "variety_code": "Local",
        "name_en": "Deshi White Jute",
        "name_bn": "স্থানীয় দেশি সাদা পাট",
        "variety_type": "Local",
        "yield_coefficient": 0.82,
        "potential_yield_min": 1.8,
        "potential_yield_max": 2.4,
        "maturity_days": 110,
        "season": "Kharif",
        "stress_tolerance": "Standard",
        "description_bn": "স্থানীয় সাদা জাতের তিতা পাট।",
        "description_en": "Indigenous white jute variety.",
        "is_recommended": False,
    },
]


def seed_samir_data():
    db = SessionLocal()
    try:
        # 1. Seed Risk Thresholds
        threshold_count = 0
        for item in DEFAULT_THRESHOLDS:
            existing = (
                db.query(RiskThreshold)
                .filter(
                    RiskThreshold.crop == item["crop"],
                    RiskThreshold.region == item["region"],
                    RiskThreshold.metric == item["metric"],
                )
                .first()
            )
            if not existing:
                threshold = RiskThreshold(**item)
                db.add(threshold)
                threshold_count += 1

        # 2. Seed Crop Varieties
        variety_count = 0
        for item in DEFAULT_VARIETIES:
            existing = (
                db.query(CropVariety)
                .filter(
                    CropVariety.crop == item["crop"],
                    CropVariety.variety_code == item["variety_code"],
                )
                .first()
            )
            if not existing:
                variety = CropVariety(**item)
                db.add(variety)
                variety_count += 1
            else:
                # Update coefficients and Bangla names if already exists
                existing.name_en = item["name_en"]
                existing.name_bn = item["name_bn"]
                existing.yield_coefficient = item["yield_coefficient"]
                existing.potential_yield_min = item["potential_yield_min"]
                existing.potential_yield_max = item["potential_yield_max"]
                existing.maturity_days = item["maturity_days"]
                existing.stress_tolerance = item["stress_tolerance"]
                existing.description_bn = item["description_bn"]

        db.commit()
        print(f"Seeded {threshold_count} risk thresholds and {variety_count} crop varieties successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding Samir data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_samir_data()
