"""
Scenario planner service.

Re-runs the Prophet / regional prediction pipeline with the simulated rainfall
and temperature adjustments to compute the updated yield forecast and confidence
interval bounds.
"""

from sqlalchemy.orm import Session

from app.data.district_coordinates import normalize_region_name
from app.schemas.scenario_planner import ScenarioResponse
from app.services.prediction_service import get_prediction


def compute(
    crop: str,
    region: str,
    variety: str = "HYV",
    cropping_type: str = "single",
    rainfall_pct: float = 0.0,
    temperature_pct: float = 0.0,
    db: Session | None = None,
) -> ScenarioResponse:
    """
    Core shared calculation for scenario planning.
    Used by both REST (POST /api/scenario/) and streaming (POST /api/scenario/stream).
    """
    clean_crop = (crop or "Rice").strip().title()
    canonical_region = normalize_region_name(region or "Rangpur")
    clean_variety = (variety or "HYV").strip()
    clean_cropping = (cropping_type or "single").strip()

    baseline_res = get_prediction(
        crop=clean_crop,
        region=canonical_region,
        variety=clean_variety,
        cropping_type=clean_cropping,
        db=db,
        rainfall_adjustment_percent=0.0,
        temperature_adjustment_percent=0.0,
    )
    base_yield = float(baseline_res["predicted_yield"])

    sim_res = get_prediction(
        crop=clean_crop,
        region=canonical_region,
        variety=clean_variety,
        cropping_type=clean_cropping,
        db=db,
        rainfall_adjustment_percent=rainfall_pct,
        temperature_adjustment_percent=temperature_pct,
    )

    adjusted_yield = float(sim_res["predicted_yield"])
    lower_bound = float(sim_res["lower_bound"])
    upper_bound = float(sim_res["upper_bound"])

    pct_change = ((adjusted_yield - base_yield) / base_yield * 100.0) if base_yield > 0 else 0.0
    temp_shift_c = temperature_pct / 10.0
    direction = "বৃদ্ধি" if pct_change >= 0 else "হ্রাস"
    message = (
        f"বৃষ্টি {rainfall_pct:+.0f}% ও তাপমাত্রা "
        f"{temp_shift_c:+.1f}°সে পরিবর্তনে পূর্বাভাসকৃত ফলন "
        f"{abs(pct_change):.1f}% {direction} পেয়েছে ({adjusted_yield:.2f} টন/হেক্টর)।"
    )

    return ScenarioResponse(
        original_yield=round(base_yield, 2),
        adjusted_yield=round(adjusted_yield, 2),
        lower_bound=round(lower_bound, 2),
        upper_bound=round(upper_bound, 2),
        adjustment_applied=round(pct_change, 2),
        message=message,
    )


def run_scenario(
    crop: str,
    region: str,
    variety: str,
    cropping_type: str,
    rainfall_adjustment_percent: float = 0.0,
    temperature_adjustment_percent: float = 0.0,
    db: Session | None = None,
) -> ScenarioResponse:
    """Backward compatibility wrapper delegating to compute()."""
    return compute(
        crop=crop,
        region=region,
        variety=variety,
        cropping_type=cropping_type,
        rainfall_pct=rainfall_adjustment_percent,
        temperature_pct=temperature_adjustment_percent,
        db=db,
    )
