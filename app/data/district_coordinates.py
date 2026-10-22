# Canonical 64 districts of Bangladesh with coordinates (latitude, longitude)
CANONICAL_DISTRICT_COORDINATES = {
    "Dhaka": (23.8103, 90.4125),
    "Faridpur": (23.6070, 89.8429),
    "Gazipur": (23.9999, 90.4203),
    "Gopalganj": (23.0050, 89.8266),
    "Jamalpur": (24.9375, 89.9370),
    "Kishoreganj": (24.4262, 90.9848),
    "Madaripur": (23.1641, 90.1897),
    "Manikganj": (23.8644, 90.0047),
    "Munshiganj": (23.5422, 90.5305),
    "Mymensingh": (24.7471, 90.4203),
    "Narayanganj": (23.6238, 90.5000),
    "Narsingdi": (23.9322, 90.7150),
    "Netrokona": (24.8829, 90.7280),
    "Rajbari": (23.7574, 89.6444),
    "Shariatpur": (23.2423, 90.4348),
    "Sherpur": (25.0197, 90.0155),
    "Tangail": (24.2513, 89.9167),
    "Bogura": (24.8465, 89.3773),
    "Joypurhat": (25.0968, 89.0227),
    "Naogaon": (24.7936, 88.9318),
    "Natore": (24.4206, 88.9873),
    "Chapainawabganj": (24.5965, 88.2775),
    "Pabna": (24.0064, 89.2372),
    "Rajshahi": (24.3745, 88.6042),
    "Sirajganj": (24.4534, 89.7000),
    "Dinajpur": (25.6217, 88.6354),
    "Gaibandha": (25.3288, 89.5286),
    "Kurigram": (25.8054, 89.6362),
    "Lalmonirhat": (25.9923, 89.2847),
    "Nilphamari": (25.9317, 88.8560),
    "Panchagarh": (26.3411, 88.5541),
    "Rangpur": (25.7439, 89.2752),
    "Thakurgaon": (26.0336, 88.4616),
    "Barguna": (22.1591, 90.1264),
    "Barishal": (22.7010, 90.3535),
    "Bhola": (22.6859, 90.6482),
    "Jhalokathi": (22.6406, 90.1987),
    "Patuakhali": (22.3596, 90.3298),
    "Pirojpur": (22.5841, 89.9720),
    "Bandarban": (22.1953, 92.2184),
    "Brahmanbaria": (23.9571, 91.1119),
    "Chandpur": (23.2513, 90.8563),
    "Chattogram": (22.3569, 91.7832),
    "Cumilla": (23.4607, 91.1809),
    "Cox's Bazar": (21.4272, 92.0058),
    "Feni": (23.0159, 91.3976),
    "Khagrachhari": (23.1193, 91.9847),
    "Lakshmipur": (22.9447, 90.8282),
    "Noakhali": (22.8696, 91.0995),
    "Rangamati": (22.6533, 92.1789),
    "Habiganj": (24.3745, 91.4155),
    "Moulvibazar": (24.4829, 91.7774),
    "Sunamganj": (25.0658, 91.3950),
    "Sylhet": (24.8949, 91.8687),
    "Bagerhat": (22.6602, 89.7895),
    "Chuadanga": (23.6402, 88.8410),
    "Jessore": (23.1667, 89.2167),
    "Jhenaidah": (23.5450, 89.1539),
    "Khulna": (22.8456, 89.5403),
    "Kushtia": (23.9013, 89.1206),
    "Magura": (23.4873, 89.4198),
    "Meherpur": (23.7622, 88.6318),
    "Narail": (23.1725, 89.5126),
    "Satkhira": (22.7185, 89.0705),
}

# Legacy and alternate spellings + Bangla names mapped to canonical English district names
DISTRICT_ALIASES = {
    "bogra": "Bogura",
    "bogura": "Bogura",
    "barisal": "Barishal",
    "barishal": "Barishal",
    "chittagong": "Chattogram",
    "chattogram": "Chattogram",
    "comilla": "Cumilla",
    "cumilla": "Cumilla",
    "jhalokati": "Jhalokathi",
    "jhalokathi": "Jhalokathi",
    "khagrachari": "Khagrachhari",
    "khagrachhari": "Khagrachhari",
    "kishorganj": "Kishoreganj",
    "kishoreganj": "Kishoreganj",
    "maulvibazar": "Moulvibazar",
    "moulvibazar": "Moulvibazar",
    "nawabganj": "Chapainawabganj",
    "chapainawabganj": "Chapainawabganj",
    "sirajgonj": "Sirajganj",
    "sirajganj": "Sirajganj",
    "jashore": "Jessore",
    "jessore": "Jessore",
    # Bangla names used in SignupPage.tsx
    "রাজশাহী": "Rajshahi",
    "রংপুর": "Rangpur",
    "বগুড়া": "Bogura",
    "দিনাজপুর": "Dinajpur",
    "ময়মনসিংহ": "Mymensingh",
    "সিলেট": "Sylhet",
    "খুলনা": "Khulna",
    "বরিশাল": "Barishal",
    "কুমিল্লা": "Cumilla",
    "ঢাকা": "Dhaka",
    "চট্টগ্রাম": "Chattogram",
}

# Combined lookup table supporting both canonical and legacy district names
DISTRICT_COORDINATES = dict(CANONICAL_DISTRICT_COORDINATES)
for _alias, _canonical in [
    ("Bogra", "Bogura"),
    ("Barisal", "Barishal"),
    ("Chittagong", "Chattogram"),
    ("Comilla", "Cumilla"),
    ("Jhalokati", "Jhalokathi"),
    ("Khagrachari", "Khagrachhari"),
    ("Kishorganj", "Kishoreganj"),
    ("Maulvibazar", "Moulvibazar"),
    ("Nawabganj", "Chapainawabganj"),
    ("Sirajgonj", "Sirajganj"),
]:
    DISTRICT_COORDINATES[_alias] = CANONICAL_DISTRICT_COORDINATES[_canonical]


def normalize_region_name(region: str) -> str:
    """Normalizes any district spelling or case to its canonical district name."""
    if not region:
        return "Rangpur"
    cleaned = region.strip()
    lower = cleaned.lower()
    if lower in DISTRICT_ALIASES:
        return DISTRICT_ALIASES[lower]
    if cleaned in DISTRICT_ALIASES:
        return DISTRICT_ALIASES[cleaned]
    for canonical in CANONICAL_DISTRICT_COORDINATES:
        if canonical.lower() == lower:
            return canonical
    return cleaned.title()
