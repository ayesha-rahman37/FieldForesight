
import json
import time
import uuid
from collections import defaultdict
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatStreamRequest
from app.services.auth_service import get_current_user
from app.services.chat_service import generate_chat_response
from app.services.langgraph_agent import (
    run_agent_turn,
    astream_agent_turn,
)
from app.services.graph_service import check_graph_connection


router = APIRouter()


# ============================================================
# RATE LIMITING
# ============================================================

_USER_RATE_LIMITS: Dict[int, List[float]] = defaultdict(list)

RATE_LIMIT_MAX_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 3600.0


def check_chat_rate_limit(user_id: int) -> None:

    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS

    timestamps = [
        timestamp
        for timestamp in _USER_RATE_LIMITS[user_id]
        if timestamp > cutoff
    ]

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:

        raise HTTPException(
            status_code=429,
            detail="ঘণ্টায় সর্বোচ্চ ২০টি প্রশ্ন করা যাবে। অনুগ্রহ করে পরে চেষ্টা করুন।",
        )

    timestamps.append(now)
    _USER_RATE_LIMITS[user_id] = timestamps


# ============================================================
# STANDARD CHAT
# ============================================================

@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse, include_in_schema=False)
def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:

    return chat_agent_endpoint(
        request,
        current_user=current_user,
    )


# ============================================================
# LANGGRAPH AGENT CHAT
# ============================================================

@router.post("/agent", response_model=ChatResponse)
def chat_agent_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:

    check_chat_rate_limit(current_user.id)

    conv_id = request.conversation_id or str(uuid.uuid4())

    history = [
        item.model_dump()
        for item in (request.history or [])
    ]

    context = (
        request.context.model_dump()
        if request.context
        else None
    )

    try:

        agent_res = run_agent_turn(
            user_query=request.message,
            conversation_history=history,
            dashboard_context=context,
        )

        return ChatResponse(
            reply=agent_res["reply"],
            conversation_id=conv_id,
            sources=agent_res.get("sources", []),
            tools_used=agent_res.get("tools_used", []),
            trace_steps=agent_res.get("trace_steps", []),
        )

    except Exception as exc:

        import traceback

        traceback.print_exc()

        print(
            f"AGENT ERROR: {exc}",
            flush=True,
        )

        return generate_chat_response(request)


# ============================================================
# GRAPH STATUS
# ============================================================

@router.get("/graph/status")
def graph_status_endpoint():

    return check_graph_connection()


# ============================================================
# LANGGRAPH STREAMING CHAT
# ============================================================

@router.post("/stream")
def chat_stream_endpoint(
    request: ChatStreamRequest,
    current_user: User = Depends(get_current_user),
    simulate_failure: bool = Query(
        False,
        description="Simulate a streaming failure for testing",
    ),
) -> StreamingResponse:

    """
    FieldForesight LangGraph Streaming Chat.

    Uses:
        - LangGraph Agent
        - Groq streaming
        - Agricultural tools
        - RAG tools registered in ALL_AGENT_TOOLS
        - Safety guardrail
        - Conversation history
        - SQLAlchemy chat persistence
    """

    check_chat_rate_limit(current_user.id)

    conv_id = request.conversation_id or str(uuid.uuid4())

    history = [
        item.model_dump()
        for item in (request.history or [])
    ]

    context = (
        request.context.model_dump()
        if request.context
        else None
    )

    async def event_generator():

        db: Session = SessionLocal()

        accumulated_text: List[str] = []
        stream_successful = False

        user_msg_record = ChatMessage(
            user_id=current_user.id,
            conversation_id=conv_id,
            role="user",
            content=request.message,
            status="pending",
        )

        try:

            db.add(user_msg_record)
            db.commit()

        except Exception as exc:

            db.rollback()

            print(
                f"USER MESSAGE SAVE ERROR: {exc}",
                flush=True,
            )

        try:

            # --------------------------------------------
            # FAILURE SIMULATION
            # --------------------------------------------

            if (
                simulate_failure
                and request.message == "SIMULATE_IMMEDIATE_FAIL"
            ):

                raise RuntimeError(
                    "Simulated immediate stream failure"
                )

            # --------------------------------------------
            # RUN LANGGRAPH AGENT
            # --------------------------------------------

            async for event in astream_agent_turn(
                user_query=request.message,
                conversation_history=history,
                dashboard_context=context,
            ):

                event_type = event.get("type")

                # ----------------------------------------
                # TEXT TOKEN
                # ----------------------------------------

                if event_type == "token":

                    token_text = event.get("text", "")

                    if not token_text:
                        continue

                    accumulated_text.append(token_text)

                    payload = {
                        "type": "token",
                        "text": token_text,
                    }

                    yield (
                        "data: "
                        + json.dumps(payload, ensure_ascii=False)
                        + "\n\n"
                    )

                # ----------------------------------------
                # FINAL TEXT CORRECTION
                # ----------------------------------------

                elif event_type == "replace":

                    replacement = event.get("text", "")

                    accumulated_text = [replacement]

                    payload = {
                        "type": "replace",
                        "text": replacement,
                    }

                    yield (
                        "data: "
                        + json.dumps(payload, ensure_ascii=False)
                        + "\n\n"
                    )

                # ----------------------------------------
                # COMPLETION
                # ----------------------------------------

                elif event_type == "done":

                    sources = event.get("sources", [])

                    sources_payload = {
                        "type": "sources",
                        "sources": sources,
                    }

                    yield (
                        "data: "
                        + json.dumps(
                            sources_payload,
                            ensure_ascii=False,
                        )
                        + "\n\n"
                    )

                    done_payload = {
                        "type": "done",
                        "conversation_id": conv_id,
                        "tools_used": event.get("tools_used", []),
                        "trace_steps": event.get("trace_steps", []),
                    }

                    yield (
                        "data: "
                        + json.dumps(
                            done_payload,
                            ensure_ascii=False,
                        )
                        + "\n\n"
                    )

                    stream_successful = True

            if not stream_successful:

                raise RuntimeError(
                    "LangGraph stream ended without a completion event"
                )

        except Exception as exc:

            print(
                f"LANGGRAPH STREAM ERROR: {exc}",
                flush=True,
            )

            error_payload = {
                "type": "error",
                "message": (
                    "উত্তর সম্পূর্ণ করা যায়নি। "
                    "অনুগ্রহ করে আবার চেষ্টা করুন।"
                ),
            }

            yield (
                "data: "
                + json.dumps(
                    error_payload,
                    ensure_ascii=False,
                )
                + "\n\n"
            )

        finally:

            # --------------------------------------------
            # SAVE CONVERSATION
            # --------------------------------------------

            try:

                if stream_successful:

                    user_msg_record.status = "success"
                    db.add(user_msg_record)

                    assistant_msg = ChatMessage(
                        user_id=current_user.id,
                        conversation_id=conv_id,
                        role="assistant",
                        content="".join(accumulated_text).strip(),
                        status="success",
                    )

                    db.add(assistant_msg)
                    db.commit()

                else:

                    user_msg_record.status = "failed"
                    db.add(user_msg_record)
                    db.commit()

            except Exception as exc:

                db.rollback()

                print(
                    f"CHAT DATABASE ERROR: {exc}",
                    flush=True,
                )

            finally:

                db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
