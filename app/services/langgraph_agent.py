"""
LangGraph Agronomic Agent: FieldForesight Krishi Sahakari (কৃষি সহকারী)
Orchestrates:
  - Groq Llama-3.3-70B model with native structured tool calling
  - Tool execution (Prophet ML, Sentinel-2 NDVI, n8n PostgreSQL Alerts, Neo4j GraphRAG)
  - Cyclical StateGraph with tool loops
  - Strict Agricultural Safety & Pesticide Dosage Guardrail Node
"""

import os
from typing import Annotated, Any, Dict, List, Optional
import operator
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.services.agent_tools import ALL_AGENT_TOOLS

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
AGENT_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

SYSTEM_PROMPT = """তুমি বাংলাদেশ কৃষি গবেষণা কাউন্সিল (BARC), বাংলাদেশ ধান গবেষণা ইনস্টিটিউট (BRRI) ও কৃষি সম্প্রসারণ অধিদপ্তর (DAE)-এর অনুমোদিত 'ফিল্ডফোরসাইট কৃষি সহকারী' (FieldForesight Krishi Sahakari Agent)।

তোমার লক্ষ্য:
সাধারণ কৃষক ও কৃষি উদ্যোক্তাদের ফসল নির্বাচন, ফলন পূর্বাভাস, উপগ্রহ পাতার স্বাস্থ্য (NDVI), লাইভ দুর্যোগ সতর্কতা ও রোগবালাই প্রতিরোধে সরাসরি বাস্তবমুখী বৈজ্ঞানিক পরামর্শ দেওয়া।

তোমার কাছে সরাসরি নিচের স্বয়ংক্রিয় টুলস (Tools) ব্যবহারের ক্ষমতা রয়েছে:
1. `tool_predict_crop_yield`: যেকোনো জেলা ও ফসলের ১০ বছরের ক্যালিব্রেটেড সম্ভাব্য ফলন (টন/হেক্টর) নির্ণয় করতে এটি ব্যবহার করো।
2. `tool_get_satellite_vegetation_health`: সেন্টিনেল-২ উপগ্রহ এনডিভিআই সূচক ও পাতার ঘনত্বের অবস্থা জানতে এটি ব্যবহার করো।
3. `tool_get_live_disaster_and_market_alerts`: n8n রোবট দ্বারা সংগৃহীত সাম্প্রতিক দুর্যোগ (বন্যা, খরা, বৃষ্টি), সার বা বাজার দরের লাইভ সংবাদ দেখতে এটি ব্যবহার করো।
4. `tool_query_agricultural_knowledge_graph`: নিওফরজে (Neo4j) নলেজ গ্রাফ থেকে কোনো নির্দিষ্ট ফসলের অনুমোদিত রোগ, লক্ষণ ও সমন্বিত বালাই দমন (IPM) ব্যবস্থা জানতে এটি কল করো।
5. `tool_diagnose_symptom_via_graph`: কৃষক যদি কোনো রোগের লক্ষণ বর্ণনা করে (যেমন: 'সাদা শীষ', 'গাছ পুড়ে গেছে', 'চোখের মতো দাগ'), তবে নলেজ গ্রাফের মাধ্যমে সঠিক রোগ ও নিরাময় বের করতে এটি কল করো।
6. `tool_recommend_crop_varieties`: কোনো ফসলের জন্য উপযুক্ত ও রোগ-সহনশীল জাত জানতে এটি কল করো।
7. `tool_search_agronomic_documents`: বিএআরআই (BARI) ও ব্রি (BRRI)-এর অফিশিয়াল গবেষণা ম্যানুয়াল ও টেক্সট গাইডলাইন থেকে ক্রোমাডিবি (ChromaDB Vector DB)-র মাধ্যমে সেচ (যেমন AWD), সার প্রয়োগ বা চাষাবাদ কৌশল বিস্তারিত জানতে এটি ব্যবহার করো।

কঠোর নিরাপত্তা ও আচরণবিধি (Safety Guardrails):
১. যখনই ব্যবহারকারী সুনির্দিষ্ট ফলন, রোগ বা অবস্থা জানতে চাইবে, তুমি প্রথমে উপযুক্ত টুল(সমূহ) কল করবে এবং প্রাপ্ত তথ্যের ভিত্তিতে উত্তর সাজাবে।
২. মনগড়া বা আন্দাজে কোনো বিষাক্ত কীটনাশকের মিলিলিটার বা কেমিক্যাল ডোজ বানিয়ে বলবে না। সর্বদা সমন্বিত বালাই দমন (IPM), জৈব পদ্ধতি এবং ডিএই নির্দেশিকা তুলে ধরবে।
৩. রাসায়নিক ব্যবস্থা বর্ণনার সাথে সাথে কৃষককে স্থানীয় উপ-সহকারী কৃষি কর্মকর্তা (SAAO) বা কৃষি কল সেন্টার (১৬১২৩)-এ যোগাযোগ করার পরামর্শ দেবে।
৪. উত্তর হবে স্পষ্ট, প্রমিত ও আন্তরিক বাংলায় (যদি ব্যবহারকারী বাংলায় প্রশ্ন করে) অথবা ইংরেজিতে (যদি ব্যবহারকারী ইংরেজিতে প্রশ্ন করে)। অপ্রয়োজনীয় ইংরেজি পরিভাষা পরিহার করবে।
"""


class AgentState(dict):
    """
    LangGraph execution state containing:
    - messages: complete message history with tool calls and results
    - steps_taken: trace of tools invoked for frontend visibility
    - context: contextual dashboard parameters (selected crop, region, yield)
    """
    messages: Annotated[List[BaseMessage], operator.add]
    steps_taken: Annotated[List[str], operator.add]
    context: Dict[str, Any]


def _get_groq_llm():
    """Initializes Groq model with tool bindings."""
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=AGENT_MODEL,
        temperature=0.25,
        max_tokens=1000,
    )
    return llm.bind_tools(ALL_AGENT_TOOLS)


def _get_llm():
    """Initializes primary LLM (Gemini 2.5 Flash if available, otherwise Groq)."""
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        try:
            llm = ChatGoogleGenerativeAI(
                model=gemini_model,
                google_api_key=gemini_key,
                temperature=0.25,
                timeout=12.0,
            )
            return llm.bind_tools(ALL_AGENT_TOOLS)
        except Exception as exc:
            import sys
            print(f"Warning: Could not initialize Gemini tool-calling with {gemini_model}: {exc}", file=sys.stderr)

    return _get_groq_llm()


# --- Node Definitions ---

def call_model(state: AgentState) -> Dict[str, Any]:
    """Invokes LLM with current message trajectory, automatically falling back to Groq if Gemini stalls or fails."""
    messages = state["messages"]
    response = None

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
            gemini_llm = ChatGoogleGenerativeAI(
                model=gemini_model,
                google_api_key=gemini_key,
                temperature=0.25,
                timeout=12.0,
            ).bind_tools(ALL_AGENT_TOOLS)
            response = gemini_llm.invoke(messages)
        except Exception as exc:
            import sys
            print(f"Gemini agent invocation error or timeout ({exc}), falling back to Groq {AGENT_MODEL}...", file=sys.stderr)
            response = None

    if response is None:
        groq_llm = _get_groq_llm()
        response = groq_llm.invoke(messages)

    steps = []
    if response.tool_calls:
        for tc in response.tool_calls:
            tool_name = tc.get("name", "unknown_tool")
            steps.append(f"🔧 Calling Tool: {tool_name}")

    return {
        "messages": [response],
        "steps_taken": steps,
    }


def should_continue(state: AgentState) -> str:
    """Conditional router: checks if the agent requested tool execution."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "safety_guardrail"


def is_english_query(text: str) -> bool:
    """
    Determines if user input is primarily English.
    If Bengali script (\u0980-\u09FF) is present, returns False.
    Otherwise, if Latin alphabet characters exist, returns True.
    """
    has_bengali = any('\u0980' <= ch <= '\u09FF' for ch in text)
    if has_bengali:
        return False
    return any('a' <= ch.lower() <= 'z' for ch in text)


def safety_guardrail_node(state: AgentState) -> Dict[str, Any]:
    """
    Final verification node:
    Checks if pesticide or chemical intervention was discussed and ensures
    statutory DAE / SAAO / 16123 safety warnings are present in the matching language.
    """
    last_message = state["messages"][-1]
    content = str(last_message.content)

    chemical_triggers_bn = ["কীটনাশক", "ছত্রাকনাশক", "পেস্টিসাইড", "স্প্রে", "ডোজ", "প্যাক্সার", "নেটিভো", "কার্বোফিউরান"]
    chemical_triggers_en = ["pesticide", "fungicide", "spray", "dosage", "chemical", "insecticide", "nativo", "carbofuran"]

    is_en = is_english_query(content)
    needs_safety = (
        any(trigger in content for trigger in chemical_triggers_bn) or
        any(trigger in content.lower() for trigger in chemical_triggers_en)
    )

    has_disclaimer = "16123" in content or "১৬১২৩" in content or "SAAO" in content or "উপ-সহকারী কৃষি কর্মকর্তা" in content

    if needs_safety and not has_disclaimer:
        if is_en:
            supplemental_warning = (
                "\n\n> ⚠️ **Government Agricultural Safety Directive**: Before applying any chemical pesticide or fungicide, "
                "always consult your local **Sub-Assistant Agriculture Officer (SAAO)** or call the **Agricultural Call Center (16123)** "
                "for certified dosage, application timing, and safety withholding guidelines."
            )
        else:
            supplemental_warning = (
                "\n\n> ⚠️ **সরকারি কৃষি নিরাপত্তা নির্দেশিকা**: যেকোনো অনুমোদিত রাসায়নিক বা বালাইনাশক ব্যবহারের আগে "
                "সঠিক মাত্রা ও প্রয়োগবিধির জন্য আপনার স্থানীয় **উপ-সহকারী কৃষি কর্মকর্তা (SAAO)** অথবা "
                "কৃষি বাতায়ন কল সেন্টারে (**১৬১২৩**) সরাসরি যোগাযোগ করুন।"
            )
        updated_message = AIMessage(content=content + supplemental_warning)
        return {
            "messages": [updated_message],
            "steps_taken": ["🛡️ Verified DAE Agronomic Safety Guardrail"],
        }

    return {
        "steps_taken": ["✅ Safety Verification Complete"],
    }


# --- Build StateGraph Workflow ---

def build_agronomic_agent():
    workflow = StateGraph(AgentState)

    # 1. Register Nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(ALL_AGENT_TOOLS))
    workflow.add_node("safety_guardrail", safety_guardrail_node)

    # 2. Register Edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "safety_guardrail": "safety_guardrail",
        },
    )
    workflow.add_edge("tools", "agent")
    workflow.add_edge("safety_guardrail", END)

    return workflow.compile()


# Compiled Singleton Graph
agronomic_agent_graph = build_agronomic_agent()


# Common greetings & presence check patterns in Bangla and English
GREETING_PATTERNS = [
    r"^(hi|hello|hey|hola|greetings|are you here|are you there|who are you)\b",
    r"^(সালাম|আসসালামু\s*আলাইকুম|নমস্কার|আদাব|কেমন\s*আছেন|হ্যালো|হাই|কে\s*আছো|কে\s*আছেন|আছেন\s*কেউ|শুনছেন|এখানে\s*কেউ\s*আছেন)\b",
]


def _is_greeting(text: str) -> bool:
    import re
    t = text.strip().lower()
    return any(re.search(pat, t) for pat in GREETING_PATTERNS) and len(t.split()) <= 4


def run_agent_turn(
    user_query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    dashboard_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    High-level entrypoint for FastAPI chat router:
    Autonomous Orchestrator decides whether to answer directly (e.g. greeting)
    or execute multi-step tools & Neo4j graph queries.
    """
    clean_q = user_query.strip()
    user_is_en = is_english_query(clean_q)

    if _is_greeting(clean_q):
        if user_is_en:
            greeting_reply = (
                "Hello! Yes, I am here. I am your FieldForesight Agricultural Assistant. "
                "Feel free to ask any question regarding crop varieties, yield predictions, satellite NDVI canopy health, "
                "or pest and disease management. How may I assist you today?"
            )
        else:
            greeting_reply = (
                "ওয়ালাইকুম আসসালাম! আমি ফিল্ডফোরসাইট কৃষি সহকারী। আপনার ফসল নির্বাচন, "
                "ফলন পূর্বাভাস, উপগ্রহ পাতার স্বাস্থ্য বা রোগবালাই সম্পর্কিত যেকোনো প্রশ্ন সরাসরি করতে পারেন। "
                "আজ কীভাবে সাহায্য করতে পারি?"
            )
        return {
            "reply": greeting_reply,
            "trace_steps": ["💬 Handled Direct Greeting"],
            "tools_used": [],
        }

    messages: List[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]

    # Dynamic language directive
    if user_is_en:
        lang_prompt = (
            "CRITICAL LANGUAGE INSTRUCTION: The user is communicating in ENGLISH. "
            "You MUST respond completely in natural, fluent, and professional ENGLISH. "
            "Do NOT use Bengali script. Translate all variety names, crop disease symptoms, "
            "and agronomic advice clearly into English."
        )
    else:
        lang_prompt = (
            "ভাষাগত নির্দেশিকা: ব্যবহারকারী বাংলায় লিখছেন। আপনার সম্পূর্ণ উত্তর প্রমিত ও সহজবোধ্য বাংলায় দিন।"
        )
    messages.append(SystemMessage(content=lang_prompt))

    # Add dashboard context if provided (active crop, region, yield)
    if dashboard_context:
        ctx_text = (
            f"কৃষকের বর্তমান ড্যাশবোর্ড প্রেক্ষাপট: "
            f"ফসল: {dashboard_context.get('crop', 'Not selected')}, "
            f"জেলা: {dashboard_context.get('region', 'Not selected')}, "
            f"পূর্বাভাসকৃত ফলন: {dashboard_context.get('yield', 'N/A')} t/ha."
        )
        messages.append(SystemMessage(content=ctx_text))

    # Add previous turns
    if conversation_history:
        for turn in conversation_history[-6:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

    # Append current user prompt
    messages.append(HumanMessage(content=user_query))

    initial_state = {
        "messages": messages,
        "steps_taken": [],
        "context": dashboard_context or {},
    }

    result = agronomic_agent_graph.invoke(initial_state)

    final_message = result["messages"][-1]
    steps_taken = result.get("steps_taken", [])

    # Extract unique tools invoked
    tools_used = []
    for step in steps_taken:
        if "Calling Tool:" in step:
            tool_name = step.split("Calling Tool:")[-1].strip()
            if tool_name not in tools_used:
                tools_used.append(tool_name)

    # Extract clean text response
    content_raw = final_message.content
    if isinstance(content_raw, list):
        text_parts = []
        for part in content_raw:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(str(part["text"]))
            elif isinstance(part, str):
                text_parts.append(part)
        clean_reply = "\n".join(text_parts).strip() if text_parts else str(content_raw)
    else:
        clean_reply = str(content_raw).strip()

    return {
        "reply": clean_reply,
        "trace_steps": steps_taken,
        "tools_used": tools_used,
    }
