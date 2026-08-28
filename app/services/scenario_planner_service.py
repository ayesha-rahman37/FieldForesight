from app.schemas.scenario_planner import ScenarioResponse

def run_scenario(crop: str, region: str, variety: str, cropping_type: str, rainfall_adjustment_percent: float) -> ScenarioResponse:

    base_yield = 4.2
    adjustment_factor = (rainfall_adjustment_percent / 10) * 0.03
    adjusted_yield = base_yield * (1 + adjustment_factor)

    return ScenarioResponse(
        original_yield=base_yield,
        adjusted_yield=round(adjusted_yield, 2),
        lower_bound=round(adjusted_yield * 0.9, 2),
        upper_bound=round(adjusted_yield * 1.1, 2),
        adjustment_applied=rainfall_adjustment_percent,
        message=f"বৃষ্টি {rainfall_adjustment_percent}% পরিবর্তনে yield {adjustment_factor*100:.1f}% পরিবর্তিত হয়েছে"
    )