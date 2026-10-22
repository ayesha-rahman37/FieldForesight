import os
import sys
import logging
import warnings
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

# Suppress unwanted stdout/stderr warnings from underlying libraries in stdio mode
warnings.filterwarnings("ignore")

from mcp.server.fastmcp import FastMCP
from app.database import SessionLocal
from app.services.prediction_service import get_prediction
from app.services.ndvi_service import get_ndvi_for_region
from app.services.rag_service import retrieve
from app.services.llm_service import generate_llm_text

# Configure logger to output only to stderr
logger = logging.getLogger("FieldForesightMCP")
logger.setLevel(logging.INFO)
if not logger.handlers:
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(stderr_handler)

mcp = FastMCP("FieldForesight", log_level="INFO")


@mcp.tool()
def predict_crop_yield(
    crop: str,
    region: str,
    variety: str = "HYV",
    cropping_type: str = "single",
) -> Dict[str, Any]:
    """Predict crop yield (metric tons per hectare) using historical ML models and regional environmental data.

    Args:
        crop: Target crop name (e.g. 'Rice', 'Wheat', 'Potato', 'Maize', 'Mustard', 'Lentil').
        region: Bangladesh district/region name (e.g. 'Rangpur', 'Dinajpur', 'Dhaka').
        variety: Seed variety code or type (e.g. 'HYV', 'Local', 'Hybrid').
        cropping_type: Cropping pattern ('single', 'intercrop', 'mixed').
    """
    db = SessionLocal()
    try:
        prediction = get_prediction(
            crop=crop,
            region=region,
            variety=variety,
            cropping_type=cropping_type,
            db=db,
        )
        return prediction
    except Exception as exc:
        logger.error(f"predict_crop_yield error: {exc}")
        return {"error": f"Crop yield prediction failed: {str(exc)}"}
    finally:
        db.close()


@mcp.tool()
def get_district_ndvi(region: str) -> Dict[str, Any]:
    """Retrieve the latest satellite NDVI (vegetation index) and canopy health status for a district.

    Args:
        region: Bangladesh district name (e.g. 'Rangpur', 'Dinajpur', 'Dhaka').
    """
    db = SessionLocal()
    try:
        ndvi_res = get_ndvi_for_region(region, db)
        if hasattr(ndvi_res, "model_dump"):
            return ndvi_res.model_dump(mode="json")
        return ndvi_res.dict()
    except Exception as exc:
        logger.error(f"get_district_ndvi error: {exc}")
        return {"error": f"Failed to retrieve NDVI for '{region}': {str(exc)}"}
    finally:
        db.close()


@mcp.tool()
def get_bangla_advisory(
    crop: str,
    region: str,
    risk_context: str,
) -> Dict[str, Any]:
    """Generate grounded agricultural advisory in Bangla for farmers using RAG guidelines and Groq LLM.

    Args:
        crop: Target crop name (e.g. 'Rice', 'Wheat').
        region: Bangladesh district or region (e.g. 'Rangpur').
        risk_context: Observed risk condition or topic (e.g. 'ব্লাস্ট রোগ', 'খরা পরিস্থিতি', 'কীটপতঙ্গ আক্রমণ').
    """
    db = SessionLocal()
    try:
        # 1. RAG retrieval
        guidelines_text = ""
        source_labels: List[str] = []
        try:
            chunks = retrieve(query=f"{crop} {risk_context}", crop=crop, k=3)
            if chunks:
                guideline_parts = []
                for c in chunks:
                    title = c.get("title", "")
                    sec = c.get("section", "")
                    label = f"{title} ({sec})" if sec else title
                    if label and label not in source_labels:
                        source_labels.append(label)
                    guideline_parts.append(f"[{label}]:\n{c.get('text', '')}")
                guidelines_text = "\n\n".join(guideline_parts)
        except Exception as rag_err:
            logger.warning(f"RAG retrieval unavailable: {rag_err}")
            return {"error": f"RAG knowledge base service is not available: {str(rag_err)}"}

        if not guidelines_text:
            guidelines_text = "কোনো সরাসরি সরকারি নির্দেশিকা চাঙ্ক পাওয়া যায়নি।"

        # 2. Check Groq API configuration
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            return {"error": "Groq LLM service is not available: GROQ_API_KEY is not configured"}

        # 3. Call Groq service
        prompt = (
            f"তুমি বাংলাদেশ কৃষি গবেষণা কাউন্সিল (BARC) ও ডিএই (DAE)-এর একজন কৃষি বিশেষজ্ঞ।\n"
            f"ফসল: {crop}\n"
            f"অঞ্চল: {region}\n"
            f"ঝুঁকি/পরিস্থিতি: {risk_context}\n\n"
            f"সরকারি কৃষি গবেষণা নির্দেশিকা (Verified Knowledge Base):\n{guidelines_text}\n\n"
            f"উপরের নির্দেশিকার ভিত্তিতে কৃষকের জন্য খাঁটি বাংলায় ৩-৪ বাক্যে বাস্তবসম্মত ও সুস্পষ্ট করণীয় পরামর্শ দাও।"
        )

        marker = "__GROQ_UNAVAILABLE__"
        advisory_text = generate_llm_text(prompt=prompt, fallback_text=marker)

        if advisory_text == marker or not advisory_text:
            return {"error": "Groq LLM service is not available or failed to respond"}

        return {
            "crop": crop,
            "region": region,
            "risk_context": risk_context,
            "advisory_bangla": advisory_text,
            "sources": source_labels,
        }
    except Exception as exc:
        logger.error(f"get_bangla_advisory error: {exc}")
        return {"error": f"Advisory generation failed: {str(exc)}"}
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")
