import os
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agri_alert import AgriAlert

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

WEBHOOK_SECRET = os.getenv("N8N_WEBHOOK_SECRET", "super-secret-fieldforesight-key")


class NewsAlertItem(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    district: Optional[str] = "National"
    risk_tag: Optional[str] = "General"


class NewsAlertResponse(BaseModel):
    id: int
    title: str
    source_url: str
    summary: Optional[str]
    district: str
    risk_tag: str
    crawled_at: datetime

    class Config:
        from_attributes = True


@router.post("/agri-news", status_code=status.HTTP_201_CREATED)
def receive_scraped_agri_news(
    payload: List[NewsAlertItem],
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret"),
    db: Session = Depends(get_db),
):
    """
    Webhook endpoint called by n8n scheduled workflow.
    Validates X-Webhook-Secret, deduplicates by URL, and persists agricultural alerts.
    """
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Webhook-Secret header",
        )

    inserted_count = 0
    updated_count = 0

    for item in payload:
        if not item.url or not item.title:
            continue

        clean_url = item.url.strip()
        existing = db.query(AgriAlert).filter(AgriAlert.source_url == clean_url).first()

        if existing:
            # Update summary and risk tag if changed
            existing.summary = item.summary
            existing.risk_tag = item.risk_tag or "General"
            existing.district = item.district or "National"
            updated_count += 1
        else:
            new_alert = AgriAlert(
                title=item.title.strip(),
                source_url=clean_url,
                summary=item.summary,
                district=item.district or "National",
                risk_tag=item.risk_tag or "General",
            )
            db.add(new_alert)
            inserted_count += 1

    db.commit()

    return {
        "status": "success",
        "inserted": inserted_count,
        "updated": updated_count,
        "total_received": len(payload),
    }


@router.get("/alerts", response_model=List[NewsAlertResponse])
def get_latest_alerts(
    district: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Retrieves the latest crawled agricultural and disaster news alerts.
    Optional filtering by district for localized dashboard feeds.
    """
    query = db.query(AgriAlert)
    if district and district.lower() != "national":
        query = query.filter(
            (AgriAlert.district.ilike(district)) | (AgriAlert.district == "National")
        )
    return query.order_by(AgriAlert.crawled_at.desc()).limit(limit).all()

