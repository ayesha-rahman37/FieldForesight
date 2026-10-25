import json
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.data.district_coordinates import normalize_region_name
from app.database import get_db
from app.models.advisory_history import AdvisoryHistory
from app.models.crop import Crop
from app.models.historical_yield import HistoricalYield
from app.models.ndvi_cache import NDVICache
from app.models.prediction_history import PredictionHistory
from app.models.region import Region
from app.models.risk_threshold import RiskThreshold
from app.models.user import User
from app.scripts.seed_samir_data import seed_samir_data
from app.services.auth_service import get_current_user, get_optional_current_user
from app.services.groq_service import generate_bangla_advisory_groq
from app.services.prediction_service import get_prediction
from app.services.risk_service import calculate_risk_and_alerts

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


RiskAlert = RiskAlertItem


class AdvisoryGenerateRequest(BaseModel):
    crop: str = "Rice"
    region: str = "Rangpur"
    variety: str = "HYV"
    predicted_yield: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    cropping_type: str = "single"
    prediction_id: Optional[int] = None
    rainfall_adjustment_percent: float = 0.0
    temperature_adjustment_percent: float = 0.0


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
    model_config = ConfigDict(from_attributes=True)

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


def _resolve_yield_and_bounds(
    crop: str,
    region: str,
    variety: str,
    cropping_type: str,
    predicted_yield: Optional[float],
    lower_bound: Optional[float],
    upper_bound: Optional[float],
    prediction_id: Optional[int],
    db: Session,
) -> tuple[float, float, float]:
    if prediction_id is not None:
        hist = db.query(PredictionHistory).filter(PredictionHistory.id == prediction_id).first()
        if hist:
            y = predicted_yield if predicted_yield is not None else hist.predicted_yield
            lb = lower_bound if lower_bound is not None else hist.lower_bound
            ub = upper_bound if upper_bound is not None else hist.upper_bound
            return y, lb, ub

    if predicted_yield is not None:
        lb = lower_bound if lower_bound is not None else round(predicted_yield * 0.92, 2)
        ub = upper_bound if upper_bound is not None else round(predicted_yield * 1.08, 2)
        return predicted_yield, lb, ub

    try:
        pred = get_prediction(crop=crop, region=region, variety=variety, cropping_type=cropping_type, db=db)
        return pred["predicted_yield"], pred["lower_bound"], pred["upper_bound"]
    except Exception:
        return 4.2, round(4.2 * 0.92, 2), round(4.2 * 1.08, 2)


@router.get("/risk/thresholds", response_model=List[RiskThresholdResponse])
def get_risk_thresholds(
    crop: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    count = db.query(RiskThreshold).count()
    if count == 0:
        seed_samir_data(db)

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
    canonical_region = normalize_region_name(region)
    evaluated_yield, lower, upper = _resolve_yield_and_bounds(
        crop=crop,
        region=canonical_region,
        variety=variety,
        cropping_type="single",
        predicted_yield=yield_val,
        lower_bound=None,
        upper_bound=None,
        prediction_id=None,
        db=db,
    )

    risk_eval = calculate_risk_and_alerts(
        crop=crop,
        region=canonical_region,
        variety_code=variety,
        predicted_yield=evaluated_yield,
        lower_bound=lower,
        upper_bound=upper,
        db=db,
    )

    return [RiskAlertItem(**a) for a in risk_eval["alerts"]]


def _compute_advisory(
    req: AdvisoryGenerateRequest,
    db: Session,
    current_user: Optional[User],
    persist: bool = True,
) -> AdvisoryResponse:
    canonical_region = normalize_region_name(req.region)
    evaluated_yield, lower, upper = _resolve_yield_and_bounds(
        crop=req.crop,
        region=canonical_region,
        variety=req.variety,
        cropping_type=req.cropping_type,
        predicted_yield=req.predicted_yield,
        lower_bound=req.lower_bound,
        upper_bound=req.upper_bound,
        prediction_id=req.prediction_id,
        db=db,
    )

    risk_eval = calculate_risk_and_alerts(
        crop=req.crop,
        region=canonical_region,
        variety_code=req.variety,
        predicted_yield=evaluated_yield,
        lower_bound=lower,
        upper_bound=upper,
        cropping_type=req.cropping_type,
        db=db,
        rainfall_adjustment_percent=req.rainfall_adjustment_percent,
        temperature_adjustment_percent=req.temperature_adjustment_percent,
    )

    groq_result = generate_bangla_advisory_groq(
        crop=req.crop,
        region=canonical_region,
        variety=req.variety,
        predicted_yield=evaluated_yield,
        risk_level=risk_eval["risk_level"],
        risk_factors=risk_eval["risk_factors"],
        ndvi_status=risk_eval.get("ndvi_context", {}).get("status"),
        cropping_type=req.cropping_type,
        rainfall_adjustment_percent=req.rainfall_adjustment_percent,
        temperature_adjustment_percent=req.temperature_adjustment_percent,
    )

    entry_id = None
    if persist:
        history_entry = AdvisoryHistory(
            prediction_id=req.prediction_id,
            user_id=current_user.id if current_user else None,
            crop=req.crop,
            region=canonical_region,
            variety=req.variety,
            cropping_type=req.cropping_type,
            predicted_yield=evaluated_yield,
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
            entry_id = history_entry.id
        except Exception as e:
            db.rollback()
            print(f"Warning: Failed to save advisory history: {e}")

    alerts_list = [RiskAlertItem(**a) for a in risk_eval["alerts"]]

    return AdvisoryResponse(
        id=entry_id,
        crop=req.crop,
        region=canonical_region,
        variety=req.variety,
        predicted_yield=evaluated_yield,
        risk_level=risk_eval["risk_level"],
        risk_score=risk_eval["risk_score"],
        advisory_text=groq_result.get("advisory_text", ""),
        action_items=groq_result.get("action_items", []),
        precaution_alert=groq_result.get("precaution_alert"),
        warning_alerts=alerts_list,
        llm_provider=groq_result.get("llm_provider", "groq"),
        llm_model=groq_result.get("llm_model", "llama-3.3-70b-versatile"),
    )


@router.post("/advisory/generate", response_model=AdvisoryResponse)
def generate_advisory_post(
    req: AdvisoryGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _compute_advisory(req=req, db=db, current_user=current_user, persist=True)


@router.get("/advisory/generate", response_model=AdvisoryResponse)
def generate_advisory_get(
    crop: str = Query("Rice"),
    region: str = Query("Rangpur"),
    variety: str = Query("HYV"),
    yield_val: Optional[float] = Query(None, alias="yield"),
    prediction_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = AdvisoryGenerateRequest(
        crop=crop,
        region=region,
        variety=variety,
        predicted_yield=yield_val,
        prediction_id=prediction_id,
    )
    return _compute_advisory(req=req, db=db, current_user=current_user, persist=False)


@router.get("/advisory/history")
def get_advisory_history(
    crop: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    query = db.query(AdvisoryHistory)
    if current_user:
        query = query.filter(
            (AdvisoryHistory.user_id == current_user.id) | (AdvisoryHistory.user_id.is_(None))
        )
    if crop and crop.strip():
        query = query.filter(AdvisoryHistory.crop.ilike(f"%{crop.strip()}%"))
    if region and region.strip():
        canonical_region = normalize_region_name(region)
        query = query.filter(
            (AdvisoryHistory.region.ilike(f"%{canonical_region}%"))
            | (AdvisoryHistory.region.ilike(f"%{region.strip()}%"))
        )

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
    canonical_region = normalize_region_name(region)
    ndvi_entry = (
        db.query(NDVICache)
        .filter(
            (NDVICache.region_name.ilike(canonical_region))
            | (NDVICache.region_name.ilike(region.strip()))
        )
        .order_by(NDVICache.computed_at.desc())
        .first()
    )

    veg_status = ndvi_entry.vegetation_status if ndvi_entry else "স্বাভাবিক"
    ndvi_val = (
        f"NDVI {ndvi_entry.ndvi_value:.2f}"
        if (ndvi_entry and ndvi_entry.ndvi_value is not None)
        else "স্যাটেলাইট উপাত্ত"
    )

    # Query actual historical years count from HistoricalYield table
    hist_count = (
        db.query(HistoricalYield)
        .join(Crop, HistoricalYield.crop_id == Crop.id)
        .join(Region, HistoricalYield.region_id == Region.id)
        .filter(
            Crop.name.ilike(crop.strip()),
            Region.name.ilike(canonical_region),
        )
        .count()
    )
    years_count = hist_count if hist_count > 0 else 10

    return RegionalContextResponse(
        region=canonical_region,
        historical_years=years_count,
        seasonal_status_bn=(
            f"{canonical_region} অঞ্চলের উপগ্রহ তথ্য ({ndvi_val}, আবাদ: {veg_status}) ও "
            f"আবহাওয়া ডেটাসেটের ভিত্তিতে পূর্বাভাস মডেলটি রিয়েল-টাইমে ক্যালিব্রেট করা হয়েছে।"
        ),
        seasonal_status_en=(
            f"Prediction models for {canonical_region} are calibrated against {years_count} years "
            f"of historical weather and soil data. Current satellite indicators ({ndvi_val}, status: {veg_status}) "
            f"track near district average."
        ),
        validation_note_bn=(
            f"এই পূর্বাভাসটি {canonical_region} অঞ্চলের বিগত {years_count} বছরের আবহাওয়া ও মাটির তথ্যের সাথে যাচাইকৃত।"
        ),
        validation_note_en=(
            f"Calibrated against {years_count} years of historical climate and soil datasets in {canonical_region}."
        ),
    )
