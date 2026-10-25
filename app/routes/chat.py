import json
import time
import uuid
from collections import defaultdict
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatStreamRequest
from app.services.auth_service import get_current_user
from app.services.chat_service import generate_chat_response, prepare_context
from app.services.groq_service import stream_completion
from app.services.langgraph_agent import run_agent_turn
from app.services.graph_service import check_graph_connection

router = APIRouter()

# Rate limiting: 20 requests per hour per user
_USER_RATE_LIMITS: Dict[int, List[float]] = defaultdict(list)
RATE_LIMIT_MAX_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 3600.0


def check_chat_rate_limit(user_id: int) -> None:
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    timestamps = [t for t in _USER_RATE_LIMITS[user_id] if t > cutoff]
    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="ঘণ্টায় সর্বোচ্চ ২০টি প্রশ্ন করা যাবে। অনুগ্রহ করে পরে চেষ্টা করুন।",
        )
    timestamps.append(now)
    _USER_RATE_LIMITS[user_id] = timestamps


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse, include_in_schema=False)
def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    Agricultural AI Chatbot endpoint: autonomously managed by the
    LangGraph Agronomic Orchestrator with dynamic tool decision-making.
    """
    return chat_agent_endpoint(request, current_user=current_user)


@router.post("/agent", response_model=ChatResponse)
def chat_agent_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    LangGraph Autonomous Agronomic Agent with Neo4j GraphRAG and ML Tool Execution.
    """
    check_chat_rate_limit(current_user.id)
    conv_id = request.conversation_id or str(uuid.uuid4())
    history = [h.model_dump() for h in (request.history or [])]
    ctx = request.context.model_dump() if request.context else None

    try:
        agent_res = run_agent_turn(
            user_query=request.message,
            conversation_history=history,
            dashboard_context=ctx,
        )
        return ChatResponse(
            reply=agent_res["reply"],
            conversation_id=conv_id,
            sources=[],
            tools_used=agent_res["tools_used"],
            trace_steps=agent_res["trace_steps"],
        )
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"AGENT ERROR: {exc}", flush=True)
        # Fallback to standard grounded RAG if agent encounters transient error
        return generate_chat_response(request)


@router.get("/graph/status")
def graph_status_endpoint():
    """Returns the live Neo4j Knowledge Graph connectivity status."""
    return check_graph_connection()


@router.post("/stream")
def chat_stream_endpoint(
    request: ChatStreamRequest,
    current_user: User = Depends(get_current_user),
    simulate_failure: bool = Query(False, description="Simulate mid-stream exception for testing"),
) -> StreamingResponse:
    """
    Streaming Agricultural AI Chatbot endpoint using Server-Sent Events (SSE) over POST.
    - Requires authenticated user via get_current_user.
    - Enforces 20 requests/hour rate limit per user.
    - Generator flow: prepare_context -> stream tokens -> sources -> done.
    - Mid-stream exceptions emit error event: {"type":"error","message":"উত্তর সম্পূর্ণ হয়নি"}
    """
    # 1. Enforce rate limit (counted once per request, before stream begins)
    check_chat_rate_limit(current_user.id)

    # 2. Preparation phase (retrieval & prompt assembly)
    try:
        prep = prepare_context(
            message=request.message,
            user=current_user,
            context=request.context,
            history=request.history,
            conversation_id=request.conversation_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"চ্যাট প্রসেসিং সাময়িকভাবে অনুপলব্ধ: {str(exc)}",
        )

    async def event_generator():
        accumulated_text: List[str] = []
        stream_successful = False
        db: Session = SessionLocal()

        # Save user message first
        user_msg_record = ChatMessage(
            user_id=current_user.id,
            conversation_id=prep["conversation_id"],
            role="user",
            content=request.message,
            status="pending",
        )
        try:
            db.add(user_msg_record)
            db.commit()
        except Exception:
            db.rollback()

        try:
            # Check for simulated failure before any tokens
            if simulate_failure and request.message == "SIMULATE_IMMEDIATE_FAIL":
                raise RuntimeError("Simulated immediate stream failure")

            # 3. Stream Tokens
            if prep.get("early_reply"):
                words = prep["early_reply"].split(" ")
                for i, word in enumerate(words):
                    token = word + (" " if i < len(words) - 1 else "")
                    accumulated_text.append(token)
                    event_payload = {"type": "token", "text": token}
                    yield f"data: {json.dumps(event_payload, ensure_ascii=False)}\n\n"
            else:
                for delta in stream_completion(prep["messages"], model=prep["target_model"]):
                    if simulate_failure and len(accumulated_text) >= 2:
                        raise RuntimeError("Simulated mid-stream failure after 2 tokens")

                    accumulated_text.append(delta)
                    event_payload = {"type": "token", "text": delta}
                    yield f"data: {json.dumps(event_payload, ensure_ascii=False)}\n\n"

            # 4. Sources Event (sent at the end of tokens)
            sources_payload = {
                "type": "sources",
                "sources": prep.get("sources", []),
            }
            yield f"data: {json.dumps(sources_payload, ensure_ascii=False)}\n\n"

            # 5. Done Event
            done_payload = {"type": "done"}
            yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"

            stream_successful = True

        except Exception:
            # Mid-stream error: send standard error event without raw tracebacks
            error_payload = {
                "type": "error",
                "message": "উত্তর সম্পূর্ণ হয়নি",
            }
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
        finally:
            try:
                if stream_successful:
                    # Update user message status to success and persist assistant message
                    user_msg_record.status = "success"
                    db.add(user_msg_record)
                    assistant_msg = ChatMessage(
                        user_id=current_user.id,
                        conversation_id=prep["conversation_id"],
                        role="assistant",
                        content="".join(accumulated_text).strip(),
                        status="success",
                    )
                    db.add(assistant_msg)
                    db.commit()
                else:
                    # Save nothing for the assistant and mark turn as failed
                    user_msg_record.status = "failed"
                    db.add(user_msg_record)
                    db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()

        return

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
