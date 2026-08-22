"""
Defines adjustment coefficients for variety-aware prediction and
mixed-cropping support. Other modules (risk alerts, advisory, etc.)
should import and use these functions rather than duplicating logic.
"""

# Variety multiplier: local varieties tend to yield less than
# High Yielding Varieties (HYV) under the same conditions, based on
# general agronomic patterns for Bangladesh.
VARIETY_COEFFICIENTS = {
    "HYV": 1.0,
    "Local": 0.82,
}

# Mixed-cropping adjustment: if a farmer grows more than one crop on
# the same plot (intercropping/rotation), the effective yield of the
# primary crop is typically reduced due to shared resources.
MIXED_CROPPING_COEFFICIENTS = {
    "single": 1.0,
    "intercrop": 0.88,
    "rotation": 0.95,
}


def get_variety_coefficient(variety: str) -> float:
    return VARIETY_COEFFICIENTS.get(variety, 1.0)


def get_mixed_cropping_coefficient(cropping_type: str) -> float:
    return MIXED_CROPPING_COEFFICIENTS.get(cropping_type, 1.0)


def apply_adjustments(base_yield: float, variety: str, cropping_type: str) -> float:
    variety_factor = get_variety_coefficient(variety)
    cropping_factor = get_mixed_cropping_coefficient(cropping_type)
    return round(base_yield * variety_factor * cropping_factor, 2)
