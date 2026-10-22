import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.scenario_planner import ScenarioRequest, ScenarioResponse
from app.services.auth_service import get_current_user
from app.services.scenario_service import compute

router = APIRouter()


@router.post("/", response_model=ScenarioResponse)
@router.post("", response_model=ScenarioResponse, include_in_schema=False)
def scenario(request: ScenarioRequest, db: Session = Depends(get_db)):
    """Standard REST endpoint for scenario yield recalculation."""
    try:
        return compute(
            crop=request.crop,
            region=request.region,
            variety=request.variety,
            cropping_type=request.cropping_type,
            rainfall_pct=request.rainfall_adjustment_percent,
            temperature_pct=request.temperature_adjustment_percent,
            db=db,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"সার্ভিস সাময়িকভাবে অনুপলব্ধ: {str(exc)}") from exc


@router.post("/stream")
@router.post("/stream/", include_in_schema=False)
def scenario_stream(
    request: ScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Short-lived SSE endpoint for live scenario recalculation.
    Accepts the slider state and yields one result event, followed by done event.
    Errors before stream start return standard HTTP status codes (401, 422, 503).
    """
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ডাটাবেজ সংযোগ পাওয়া যায়নি",
        )

    def event_generator():
        try:
            res = compute(
                crop=request.crop,
                region=request.region,
                variety=request.variety,
                cropping_type=request.cropping_type,
                rainfall_pct=request.rainfall_adjustment_percent,
                temperature_pct=request.temperature_adjustment_percent,
                db=db,
            )
            data = {
                "type": "result",
                "original_yield": res.original_yield,
                "adjusted_yield": res.adjusted_yield,
                "lower_bound": res.lower_bound,
                "upper_bound": res.upper_bound,
                "adjustment_applied": res.adjustment_applied,
                "message": res.message,
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
        except Exception as exc:
            err_data = {
                "type": "error",
                "message": f"সিনারিও পুনঃগণনা ব্যর্থ হয়েছে: {str(exc)}",
            }
            yield f"data: {json.dumps(err_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
