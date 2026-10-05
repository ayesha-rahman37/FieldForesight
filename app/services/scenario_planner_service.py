"""
Scenario planner service.

Replaces the hardcoded base_yield = 4.2 with a real lookup from
PredictionHistory (most recent row matching crop + region + variety +
cropping_type), then applies the rainfall/temperature adjustments using
the same agronomic sensitivity factors used in the original prediction.

Fallback: if no matching history row exists (e.g. first request),
falls back to prediction_service.get_prediction() so the response
is still grounded in the model (or its own fallback) rather than a
hardcoded constant.
"""

from sqlalchemy.orm import Session

from app.models.prediction_history import PredictionHistory
from app.schemas.scenario_planner import ScenarioResponse
from app.services.prediction_service import get_prediction


# Agronomic sensitivity of yield to rainfall and temperature changes.
# Each 10% change in rainfall shifts yield by +3%; temperature is inverse.
# These are Bangladesh-specific empirical approximations.
_RAINFALL_SENSITIVITY  =  0.03   # per 10% change in rainfall
_TEMP_SENSITIVITY      = -0.02   # per 10% change in temperature (negative = heat stress)


def run_scenario(
    crop: str,
    region: str,
    variety: str,
    cropping_type: str,
    rainfall_adjustment_percent: float = 0.0,
    temperature_adjustment_percent: float = 0.0,
    db: Session = None,
) -> ScenarioResponse:

    # ── 1. Get the real base yield from DB ────────────────────────────────────
    base_yield = None

    if db is not None:
        row = (
            db.query(PredictionHistory)
            .filter(
                PredictionHistory.crop         == crop,
                PredictionHistory.region       == region,
                PredictionHistory.variety      == variety,
                PredictionHistory.cropping_type == cropping_type,
            )
            .order_by(PredictionHistory.created_at.desc())
            .first()
        )
        if row:
            base_yield = row.predicted_yield

    # ── 2. Fallback: run the real prediction service if no history row ─────────
    if base_yield is None:
        result = get_prediction(crop, region, variety, cropping_type, db=db)
        base_yield = result["predicted_yield"]

    # ── 3. Apply scenario adjustments ─────────────────────────────────────────
    # Each slider goes -50 to +50 (percent change); sensitivity is per 10 units.
    rainfall_factor = (rainfall_adjustment_percent / 10) * _RAINFALL_SENSITIVITY
    temp_factor     = (temperature_adjustment_percent / 10) * _TEMP_SENSITIVITY
    total_factor    = rainfall_factor + temp_factor

    adjusted_yield = max(0.1, base_yield * (1 + total_factor))
    adjusted_yield = round(adjusted_yield, 2)

    lower_bound = round(adjusted_yield * 0.90, 2)
    upper_bound = round(adjusted_yield * 1.10, 2)

    pct_change = total_factor * 100
    direction  = "বৃদ্ধি" if pct_change >= 0 else "হ্রাস"
    message = (
        f"বৃষ্টি {rainfall_adjustment_percent:+.0f}% ও তাপমাত্রা "
        f"{temperature_adjustment_percent:+.0f}% পরিবর্তনে ফলন "
        f"{abs(pct_change):.1f}% {direction} পেয়েছে।"
    )

    return ScenarioResponse(
        original_yield=round(base_yield, 2),
        adjusted_yield=adjusted_yield,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        adjustment_applied=round(total_factor * 100, 2),
        message=message,
    )