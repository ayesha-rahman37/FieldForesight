"""
FieldForesight Agent Tool Registry:
Wraps internal ML, Remote Sensing, Database, and Neo4j Graph queries
as LangChain structured tools for the LangGraph Agronomic Agent.
Guarantees non-empty JSON string responses for strict Groq API tool-call compliance.
"""

import json
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.prediction_service import get_prediction
from app.services.ndvi_service import get_ndvi_for_region
from app.models.agri_alert import AgriAlert
from app.services.graph_service import (
    query_crop_disease_graph,
    find_disease_by_symptom,
    query_variety_recommendation,
)
from app.services.rag_service import retrieve


def _safe_json(data: Any) -> str:
    """Ensures tool output is always a non-empty string for Groq API."""
    if not data or (isinstance(data, list) and len(data) == 0):
        return json.dumps({"status": "no_matching_records_found", "message": "কোনো রেকর্ড পাওয়া যায়নি"}, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


@tool
def tool_predict_crop_yield(crop: str, region: str, variety: str = "Standard HYV") -> str:
    """
    Calculates the 10-year calibrated statistical Prophet crop yield forecast
    for any of the 64 districts in Bangladesh with 95% confidence intervals.
    
    Args:
        crop: Agricultural crop name in English (Rice, Wheat, Maize, Potato, Mustard, Jute, Lentil).
        region: District name in Bangladesh (e.g., Rangpur, Dinajpur, Bogura, Dhaka, Rajshahi).
        variety: Seed variety name (default 'Standard HYV' or specific certified variety).
    """
    db: Session = SessionLocal()
    try:
        pred = get_prediction(
            crop=crop,
            region=region,
            variety=variety,
            db=db,
        )
        result = {
            "crop": crop,
            "region": region,
            "variety": variety,
            "predicted_yield_tha": round(float(pred["predicted_yield"]), 2),
            "lower_bound_tha": round(float(pred["lower_bound"]), 2),
            "upper_bound_tha": round(float(pred["upper_bound"]), 2),
            "model_version": pred.get("model_version", "v2.4"),
            "unit": "metric tonnes per hectare (t/ha)",
        }
        return _safe_json(result)
    except Exception as exc:
        return _safe_json({"error": f"Failed to calculate yield prediction: {str(exc)}"})
    finally:
        db.close()


@tool
def tool_get_satellite_vegetation_health(region: str) -> str:
    """
    Retrieves Copernicus Sentinel-2 L2A multispectral canopy vegetation health (NDVI)
    for a specific district in Bangladesh.
    
    Args:
        region: District name in Bangladesh (e.g., Rangpur, Dinajpur, Bogura, Dhaka).
    """
    db: Session = SessionLocal()
    try:
        ndvi_res = get_ndvi_for_region(region, db=db)
        result = {
            "region": region,
            "ndvi_score": round(float(ndvi_res.ndvi_value), 3) if ndvi_res.ndvi_value is not None else None,
            "vegetation_status": ndvi_res.vegetation_status,
            "interpretation": (
                "উচ্চ পাতার ঘনত্ব ও সুস্থ ফসল (Dense & Healthy)"
                if (ndvi_res.ndvi_value or 0) >= 0.4
                else "মাঝারি ক্যানোপি অবস্থা (Moderate Canopy)"
                if (ndvi_res.ndvi_value or 0) >= 0.2
                else "পাতলা বা সম্ভাব্য চাপে থাকা গাছপালা (Stressed or Sparse)"
            ),
        }
        return _safe_json(result)
    except Exception as exc:
        return _safe_json({"error": f"Failed to retrieve Sentinel-2 NDVI: {str(exc)}"})
    finally:
        db.close()


@tool
def tool_get_live_disaster_and_market_alerts(district: Optional[str] = None) -> str:
    """
    Queries real-time automated ground news, floods, droughts, fertilizer supply,
    and market price alerts scraped by the n8n orchestrator into PostgreSQL.
    
    Args:
        district: Optional district name to filter ground incidents (e.g. Rangpur, Dinajpur).
    """
    db: Session = SessionLocal()
    try:
        query = db.query(AgriAlert)
        if district and district.lower() != "national":
            query = query.filter(
                (AgriAlert.district.ilike(district.strip())) | (AgriAlert.district == "National")
            )
        alerts = query.order_by(AgriAlert.crawled_at.desc()).limit(5).all()
        result = [
            {
                "title": a.title,
                "summary": a.summary,
                "district": a.district,
                "risk_tag": a.risk_tag,
                "source_url": a.source_url,
                "date": a.crawled_at.strftime("%Y-%m-%d"),
            }
            for a in alerts
        ]
        return _safe_json(result)
    except Exception as exc:
        return _safe_json([{"error": f"Failed to query live ground alerts: {str(exc)}"}])
    finally:
        db.close()


@tool
def tool_query_agricultural_knowledge_graph(crop: str) -> str:
    """
    Performs multi-hop Cypher traversal in the Neo4j Knowledge Graph to find
    diseases, field symptoms, certified IPM management protocols, and chemical safety rules
    for a specific agricultural crop.
    
    Args:
        crop: Crop name in English or Bengali (e.g. 'Rice', 'Potato', 'Wheat', 'Mustard', 'ধান', 'আলু').
    """
    try:
        data = query_crop_disease_graph(crop)
        return _safe_json(data)
    except Exception as exc:
        return _safe_json([{"error": f"Knowledge Graph traversal error: {str(exc)}"}])


@tool
def tool_diagnose_symptom_via_graph(symptom_description: str) -> str:
    """
    Performs reverse Graph traversal in the Neo4j Knowledge Graph to identify
    the disease and crop from a farmer's observed visual field symptoms
    (e.g., 'সাদা শীষ', 'চোখের দাগ', 'গাছ পুড়ে যাওয়া', 'কুয়াশায় ধসা').
    
    Args:
        symptom_description: Visual symptom keyword or phrase in Bangla or English.
    """
    try:
        data = find_disease_by_symptom(symptom_description)
        return _safe_json(data)
    except Exception as exc:
        return _safe_json([{"error": f"Symptom graph diagnosis error: {str(exc)}"}])


@tool
def tool_recommend_crop_varieties(crop: str, district: Optional[str] = None) -> str:
    """
    Queries Neo4j Knowledge Graph for certified high-yielding and resilient crop varieties
    suitable for Bangladesh agro-ecological zones, along with maturity days and disease resistance.
    
    Args:
        crop: Agricultural crop name (Rice, Wheat, Potato, etc.).
        district: Optional district name.
    """
    try:
        data = query_variety_recommendation(crop, district)
        return _safe_json(data)
    except Exception as exc:
        return _safe_json([{"error": f"Variety recommendation graph error: {str(exc)}"}])



@tool
def tool_search_agronomic_documents(
    query: str,
    crop: Optional[str] = None
) -> str:
    """
    Searches indexed agricultural documents in ChromaDB.

    Returns retrieved text together with available document
    title, source, page, section, crop, and relevance score.

    Args:
        query: Specific agricultural question or topic.
        crop: Optional crop name filter.
    """

    try:

        chunks = retrieve(
            query=query,
            crop=crop,
            k=5,
        )

        if not chunks:

            return _safe_json({
                "status": "no_reliable_source_found",
                "message": (
                    "এই প্রশ্নের জন্য indexed documents-এ "
                    "নির্ভরযোগ্য তথ্য পাওয়া যায়নি।"
                ),
                "results": [],
            })

        return _safe_json({
            "status": "retrieved",
            "query": query,
            "results": chunks,
            "instructions": (
                "Use only the retrieved document text for "
                "source-based agricultural recommendations. "
                "Preserve exact numerical values and original units. "
                "Never invent missing page numbers or source details."
            ),
        })

    except Exception as exc:

        return _safe_json({
            "status": "retrieval_error",
            "message": str(exc),
            "results": [],
        })



ALL_AGENT_TOOLS = [
    tool_predict_crop_yield,
    tool_get_satellite_vegetation_health,
    tool_get_live_disaster_and_market_alerts,
    tool_query_agricultural_knowledge_graph,
    tool_diagnose_symptom_via_graph,
    tool_recommend_crop_varieties,
    tool_search_agronomic_documents,
]

