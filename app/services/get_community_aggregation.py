"""
Community aggregation service.

Queries HistoricalYield (joined to Crop + Region ORM tables) for the
given region and crop, groups results by year, and returns the real
yield trend. Falls back to an empty list if no data exists yet.
"""

from typing import List

from sqlalchemy.orm import Session

from app.models.historical_yield import HistoricalYield
from app.models.crop import Crop
from app.models.region import Region
from app.schemas.community import RegionYieldPoint, CommunityYieldAggregationResponse


from app.services.llm_service import generate_llm_text


def get_community_aggregation(
    region: str,
    crop: str,
    llm_prediction: float,
    db: Session,
) -> CommunityYieldAggregationResponse:
    """
    Returns real historical yield data for `region` + `crop` from the DB,
    ordered by year ascending.  Falls back gracefully when no rows exist.
    """
    rows = (
        db.query(HistoricalYield.year, HistoricalYield.yield_value)
        .join(Crop,   HistoricalYield.crop_id   == Crop.id)
        .join(Region, HistoricalYield.region_id == Region.id)
        .filter(
            Crop.name.ilike(crop.strip()),
            Region.name.ilike(region.strip()),
        )
        .order_by(HistoricalYield.year.asc())
        .all()
    )

    historical_trend: List[RegionYieldPoint] = [
        RegionYieldPoint(year=r.year, yield_value=round(r.yield_value, 2))
        for r in rows
    ]

    if historical_trend:
        avg_yield = sum(p.yield_value for p in historical_trend) / len(historical_trend)
    else:
        # No data seeded yet — use the model prediction itself as reference
        avg_yield = llm_prediction

    avg_yield = round(avg_yield, 2)

    if llm_prediction > avg_yield:
        fallback_note = (
            f"তোমার পূর্বাভাসের ফলন ({llm_prediction:.2f} টন/হেক্টর) "
            f"{region} এলাকার গড় ফলনের ({avg_yield:.2f} টন/হেক্টর) চেয়ে বেশি।"
        )
    elif llm_prediction < avg_yield:
        fallback_note = (
            f"তোমার পূর্বাভাসের ফলন ({llm_prediction:.2f} টন/হেক্টর) "
            f"{region} এলাকার গড় ফলনের ({avg_yield:.2f} টন/হেক্টর) চেয়ে কম।"
        )
    else:
        fallback_note = (
            f"তোমার পূর্বাভাসের ফলন ({llm_prediction:.2f} টন/হেক্টর) "
            f"{region} এলাকার গড় ফলনের ({avg_yield:.2f} টন/হেক্টর) সমান।"
        )

    prompt = (
        f"তুমি একজন অভিজ্ঞ কৃষি সম্প্রসারণ কর্মকর্তা। {region} অঞ্চলে {crop} ফসলে একজন কৃষকের পূর্বাভাসিত ফলন "
        f"{llm_prediction:.2f} টন/হেক্টর, আর এলাকার ঐতিহাসিক গড় ফলন {avg_yield:.2f} টন/হেক্টর। "
        f"এলাকার গড়ের তুলনায় কৃষককে ১-২ বাক্যে উৎসাহমূলক এবং বাস্তবমুখী বাংলা পরামর্শ দাও। Markdown বা bullet ব্যবহার কোরো না।"
    )

    note = generate_llm_text(prompt, fallback_text=fallback_note)

    return CommunityYieldAggregationResponse(
        region=region,
        crop=crop,
        district_avg_value=avg_yield,
        historical_trend=historical_trend,
        llm_prediction=llm_prediction,
        comparison_note_bn=note,
    )