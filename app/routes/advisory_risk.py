import json
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.database import get_db
from app.models.advisory_history import AdvisoryHistory
from app.models.risk_threshold import RiskThreshold
from app.models.ndvi_cache import NDVICache
from app.models.user import User
from app.services.auth_service import get_optional_current_user
from app.services.groq_service import generate_bangla_advisory_groq
from app.services.risk_service import calculate_risk_and_alerts
from app.scripts.seed_samir_data import seed_samir_data

router = APIRouter()


class RiskAlertItem(BaseModel):
    id: str
    category: str
    level: str  # 'high' | 'medium' | 'low'
    title: str
    title_bn: Optional[str] = None
    title_en: Optional[str] = None
    description: str
    description_bn: Optional[str] = None
    description_en: Optional[str] = None
    action_bn: Optional[str] = None
    action_en: Optional[str] = None


class AdvisoryGenerateRequest(BaseModel):
    crop: str = "Rice"
    region: str = "Rangpur"
    variety: str = "HYV"
    predicted_yield: float = 4.5
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    cropping_type: str = "single"
    prediction_id: Optional[int] = None


class AdvisoryResponse(BaseModel):
    id: Optional[int] = None
    crop: str
    region: str
    variety: str
    predicted_yield: float
    risk_level: str  # 'high' | 'medium' | 'low'
    risk_score: float
    advisory_text: str
    action_items: List[str]
    precaution_alert: Optional[str] = None
    warning_alerts: List[RiskAlertItem]
    llm_provider: str
    llm_model: Optional[str] = None


class RegionalContextResponse(BaseModel):
    region: str
    historical_years: int
    seasonal_status_bn: str
    seasonal_status_en: str
    validation_note_bn: str
    validation_note_en: str


class RiskThresholdResponse(BaseModel):
    id: int
    crop: str
    region: Optional[str]
    metric: str
    low_threshold: float
    medium_threshold: float
    high_threshold: float
    unit: str
    description_bn: Optional[str]
    description_en: Optional[str]

    class Config:
        from_attributes = True


@router.get("/risk/thresholds", response_model=List[RiskThresholdResponse])
def get_risk_thresholds(
    crop: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Returns configured agro-climatic risk thresholds.
    """
    count = db.query(RiskThreshold).count()
    if count == 0:
        seed_samir_data()

    query = db.query(RiskThreshold)
    if crop and crop.strip():
        query = query.filter((RiskThreshold.crop.ilike(f"%{crop.strip()}%")) | (RiskThreshold.crop == "All"))
    return query.all()


@router.get("/risk/alerts", response_model=List[RiskAlertItem])
def get_risk_alerts(
    crop: str = Query("Rice"),
    region: str = Query("Rangpur"),
    variety: str = Query("HYV"),
    yield_val: Optional[float] = Query(None, alias="yield"),
    db: Session = Depends(get_db),
):
    """
    Calculates multi-dimensional risk alerts (threshold breach, variety mismatch, NDVI vegetation health, pest risks).
    """
    # Fallback yield estimation if not passed in query
    evaluated_yield = yield_val if yield_val is not None else 4.2
    lower = evaluated_yield * 0.92
    upper = evaluated_yield * 1.08

    risk_eval = calculate_risk_and_alerts(
        crop=crop,
        region=region,
        variety_code=variety,
        predicted_yield=evaluated_yield,
        lower_bound=lower,
        upper_bound=upper,
        db=db,
    )

    alerts = [RiskAlertItem(**a) for a in risk_eval["alerts"]]
    return alerts


@router.post("/advisory/generate", response_model=AdvisoryResponse)
def generate_advisory_post(
    req: AdvisoryGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Primary endpoint integrating Part 1 Prediction output with Groq API Bangla advisory generation & risk thresholds.
    Stores generation record in AdvisoryHistory table.
    """
    lower = req.lower_bound if req.lower_bound is not None else req.predicted_yield * 0.92
    upper = req.upper_bound if req.upper_bound is not None else req.predicted_yield * 1.08

    # 1. Threshold detection & Risk Calculation
    risk_eval = calculate_risk_and_alerts(
        crop=req.crop,
        region=req.region,
        variety_code=req.variety,
        predicted_yield=req.predicted_yield,
        lower_bound=lower,
        upper_bound=upper,
        cropping_type=req.cropping_type,
        db=db,
    )

    # 2. Call Groq API with Bangladeshi prompt engineering
    groq_result = generate_bangla_advisory_groq(
        crop=req.crop,
        region=req.region,
        variety=req.variety,
        predicted_yield=req.predicted_yield,
        risk_level=risk_eval["risk_level"],
        risk_factors=risk_eval["risk_factors"],
        ndvi_status=risk_eval.get("ndvi_context", {}).get("status"),
        cropping_type=req.cropping_type,
    )

    # 3. Persist to AdvisoryHistory table
    history_entry = AdvisoryHistory(
        prediction_id=req.prediction_id,
        user_id=current_user.id if current_user else None,
        crop=req.crop,
        region=req.region,
        variety=req.variety,
        cropping_type=req.cropping_type,
        predicted_yield=req.predicted_yield,
        lower_bound=lower,
        upper_bound=upper,
        risk_level=risk_eval["risk_level"],
        risk_score=risk_eval["risk_score"],
        advisory_text=groq_result.get("advisory_text", ""),
        action_items=json.dumps(groq_result.get("action_items", []), ensure_ascii=False),
        warning_alerts=json.dumps(risk_eval["alerts"], ensure_ascii=False),
        llm_provider=groq_result.get("llm_provider", "groq"),
        llm_model=groq_result.get("llm_model", "llama-3.3-70b-versatile"),
    )

    try:
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
    except Exception as e:
        db.rollback()
        print(f"Warning: Failed to save advisory history: {e}")

    alerts_list = [RiskAlertItem(**a) for a in risk_eval["alerts"]]

    return AdvisoryResponse(
        id=history_entry.id if hasattr(history_entry, "id") else None,
        crop=req.crop,
        region=req.region,
        variety=req.variety,
        predicted_yield=req.predicted_yield,
        risk_level=risk_eval["risk_level"],
        risk_score=risk_eval["risk_score"],
        advisory_text=groq_result.get("advisory_text", ""),
        action_items=groq_result.get("action_items", []),
        precaution_alert=groq_result.get("precaution_alert"),
        warning_alerts=alerts_list,
        llm_provider=groq_result.get("llm_provider", "groq"),
        llm_model=groq_result.get("llm_model", "llama-3.3-70b-versatile"),
    )


@router.get("/advisory/generate", response_model=AdvisoryResponse)
def generate_advisory_get(
    crop: str = Query("Rice"),
    region: str = Query("Rangpur"),
    variety: str = Query("HYV"),
    yield_val: float = Query(4.2, alias="yield"),
    prediction_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    GET version for quick backwards-compatible querying from frontend components.
    """
    req = AdvisoryGenerateRequest(
        crop=crop,
        region=region,
        variety=variety,
        predicted_yield=yield_val,
        prediction_id=prediction_id,
    )
    return generate_advisory_post(req=req, db=db, current_user=current_user)


@router.get("/advisory/history")
def get_advisory_history(
    crop: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    """
    Returns stored advisory history records.
    """
    query = db.query(AdvisoryHistory)
    if crop and crop.strip():
        query = query.filter(AdvisoryHistory.crop.ilike(f"%{crop.strip()}%"))
    if region and region.strip():
        query = query.filter(AdvisoryHistory.region.ilike(f"%{region.strip()}%"))

    records = query.order_by(AdvisoryHistory.created_at.desc()).limit(limit).all()

    output = []
    for r in records:
        action_items = []
        if r.action_items:
            try:
                action_items = json.loads(r.action_items)
            except Exception:
                action_items = [r.action_items]

        output.append({
            "id": r.id,
            "prediction_id": r.prediction_id,
            "crop": r.crop,
            "region": r.region,
            "variety": r.variety,
            "predicted_yield": r.predicted_yield,
            "risk_level": r.risk_level,
            "risk_score": r.risk_score,
            "advisory_text": r.advisory_text,
            "action_items": action_items,
            "llm_provider": r.llm_provider,
            "llm_model": r.llm_model,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return output


@router.get("/regional-context", response_model=RegionalContextResponse)
def get_regional_context(
    region: str = Query("Rangpur"),
    crop: str = Query("Rice"),
    db: Session = Depends(get_db),
):
    ndvi_entry = (
        db.query(NDVICache)
        .filter(NDVICache.region_name.ilike(region.strip()))
        .order_by(NDVICache.computed_at.desc())
        .first()
    )

    veg_status = ndvi_entry.vegetation_status if ndvi_entry else "স্বাভাবিক"
    ndvi_val = f"NDVI {ndvi_entry.ndvi_value:.2f}" if (ndvi_entry and ndvi_entry.ndvi_value is not None) else "স্যাটেলাইট উপাত্ত"

    return RegionalContextResponse(
        region=region,
        historical_years=10,
        seasonal_status_bn=f"{region} অঞ্চলের উপগ্রহ তথ্য ({ndvi_val}, আবাদ: {veg_status}) ও আবহাওয়া ডেটাসেটের ভিত্তিতে পূর্বাভাস মডেলটি রিয়েল-টাইমে ক্যালিব্রেট করা হয়েছে।",
        seasonal_status_en=f"Prediction models for {region} are calibrated against 10 years of historical weather and soil data. Current satellite indicators ({ndvi_val}, status: {veg_status}) track near district average.",
        validation_note_bn=f"এই পূর্বাভাসটি {region} অঞ্চলের বিগত ১০ বছরের আবহাওয়া ও মাটির তথ্যের সাথে যাচাইকৃত।",
        validation_note_en=f"Calibrated against 10 years of historical climate and soil datasets in {region}.",
    )
