from sqlalchemy.orm import Session

from app.schemas.explainability import ExplainabilityResponse
from app.models.explainability_cache import ExplainabilityCache


def get_explanation(prediction_id: int, db: Session) -> ExplainabilityResponse:
    cached = db.query(ExplainabilityCache).filter(
        ExplainabilityCache.prediction_id == prediction_id,
    ).first()

    if cached:
        return ExplainabilityResponse(
            prediction_id=cached.prediction_id,
            crop=cached.crop,
            region=cached.region,
            contributions=cached.contributions,
            top_factor=cached.top_factor,
            summary_text_bn=cached.summary_text_bn
        )
    mock_contribution = {"rainfall": 45.0, "soil": 30.0, "temperature": 25.0}
    top_factor = max(mock_contribution, key=mock_contribution.get)
    summary_text = f"এই মৌসুমে {top_factor} প্রধান প্রভাবক হিসেবে কাজ করেছে (প্রভাব {mock_contribution[top_factor]}%)।"
    new_entry = ExplainabilityResponse(
        prediction_id=prediction_id,
        crop="Rice",
        region="Rangpur",
        contributions=mock_contribution,
        top_factor=top_factor,
        summary_text_bn=summary_text
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return ExplainabilityResponse(
        prediction_id=new_entry.prediction_id,
        crop=new_entry.crop,
        region=new_entry.region,
        contributions=new_entry.contributions,
        top_factor=new_entry.top_factor,
        summary_text_bn=new_entry.summary_text_bn
    )
