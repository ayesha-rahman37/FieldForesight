from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Variety, AdvisoryHistory
from schemas import AdvisoryRequest, AdvisoryResponse
from services.risk_engine import evaluate_risk
from services.groq_advisory import generate_bangla_advisory

router = APIRouter(prefix="/api/advisory", tags=["Advisory Generator"])


@router.post("/generate", response_model=AdvisoryResponse)
def generate_advisory_endpoint(request: AdvisoryRequest, db: Session = Depends(get_db)):
    v = db.query(Variety).filter(Variety.id == request.variety_id).first()
    if not v:
        raise HTTPException(status_code=404, detail=f"Variety with ID {request.variety_id} not found")

    eval_result = evaluate_risk(v, request.scenario)
    advisory_content = generate_bangla_advisory(v, eval_result)

    advisory_text = advisory_content.get("advisory_text_bn", "পরামর্শ পাওয়া যায়নি।")
    action_items = advisory_content.get("action_items_bn", [])
    provider = advisory_content.get("llm_provider", "Rule Engine Fallback")

    history_entry = AdvisoryHistory(
        variety_id=v.id,
        risk_level=eval_result.risk_level,
        weather_scenario_json=request.scenario.model_dump(),
        advisory_text_bn=advisory_text,
        action_items_json=action_items,
        llm_provider=provider
    )
    try:
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
    except Exception:
        db.rollback()

    return AdvisoryResponse(
        id=history_entry.id,
        variety_id=v.id,
        variety_name=v.name,
        variety_name_bangla=v.name_bangla,
        risk_level=eval_result.risk_level,
        advisory_text_bn=advisory_text,
        action_items_bn=action_items,
        irrigation_advice_bn=advisory_content.get("irrigation_advice_bn", ""),
        pest_advice_bn=advisory_content.get("pest_advice_bn", ""),
        llm_provider=provider,
        created_at=history_entry.created_at
    )


@router.get("/history", response_model=List[AdvisoryResponse])
def get_advisory_history(variety_id: Optional[int] = None, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(AdvisoryHistory)
    if variety_id is not None:
        query = query.filter(AdvisoryHistory.variety_id == variety_id)
    records = query.order_by(AdvisoryHistory.created_at.desc()).limit(limit).all()

    results = []
    for r in records:
        v = r.variety
        results.append(
            AdvisoryResponse(
                id=r.id,
                variety_id=r.variety_id,
                variety_name=v.name if v else "Unknown",
                variety_name_bangla=v.name_bangla if v else "অজানা জাত",
                risk_level=r.risk_level,
                advisory_text_bn=r.advisory_text_bn,
                action_items_bn=r.action_items_json or [],
                irrigation_advice_bn="",
                pest_advice_bn="",
                llm_provider=r.llm_provider,
                created_at=r.created_at
            )
        )
    return results
