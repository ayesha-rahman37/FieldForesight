"""
Defines adjustment coefficients for variety-aware prediction and
mixed-cropping support. Supports certified Bangladeshi varieties
(BRRI, BARI, BJRI) as well as broad cultivar categories.
"""

# Variety multipliers calibrated against standard Bangladesh field trials
VARIETY_COEFFICIENTS = {
    # Broad categories
    "HYV": 1.0,
    "HYBRID": 1.12,
    "LOCAL": 0.82,
    "STRESS_TOLERANT": 1.02,

    # Specific Rice varieties
    "BRRI_DHAN_28": 1.02,
    "BRRI_DHAN_29": 1.15,
    "BRRI_DHAN_89": 1.18,
    "BANGABANDHU_100": 1.08,
    "BRRI_DHAN_67": 1.04,
    "BRRI_DHAN_51": 0.98,
    "BRRI_DHAN_56": 0.96,

    # Specific Wheat varieties
    "BARI_GOM_33": 1.12,
    "BARI_GOM_25": 1.05,

    # Specific Potato varieties
    "BARI_ALU_7": 1.0,
    "BARI_ALU_25": 1.08,

    # Specific Maize varieties
    "BARI_BHUTTA_9": 1.10,

    # Specific Mustard varieties
    "BARI_SARISHA_14": 1.0,

    # Specific Jute varieties
    "BJRI_TOSSA_8": 1.0,

    # Specific Lentil varieties
    "BARI_MASUR_8": 1.08,
}

# Mixed-cropping adjustments
MIXED_CROPPING_COEFFICIENTS = {
    "single": 1.0,
    "intercrop": 0.88,
    "rotation": 0.95,
}


def get_variety_coefficient(variety: str) -> float:
    if not variety:
        return 1.0
    normalized = variety.strip().replace(" ", "_").replace("-", "_").upper()
    if normalized in VARIETY_COEFFICIENTS:
        return VARIETY_COEFFICIENTS[normalized]
    # Check if a specific variety key (len >= 4) appears inside normalized input
    for key, val in VARIETY_COEFFICIENTS.items():
        if len(key) >= 4 and key in normalized:
            return val
    if "LOCAL" in normalized or "DESHI" in normalized:
        return 0.82
    if "HYBRID" in normalized:
        return 1.12
    return 1.0


def get_mixed_cropping_coefficient(cropping_type: str) -> float:
    return MIXED_CROPPING_COEFFICIENTS.get(cropping_type.lower() if cropping_type else "single", 1.0)


def apply_adjustments(base_yield: float, variety: str, cropping_type: str) -> float:
    variety_factor = get_variety_coefficient(variety)
    cropping_factor = get_mixed_cropping_coefficient(cropping_type)
    return round(base_yield * variety_factor * cropping_factor, 2)
