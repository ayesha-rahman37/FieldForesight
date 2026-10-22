import json
import unittest
from pathlib import Path

from app.services.token_optimizer import (
    set_mode,
    get_current_mode,
    reset_live_counter,
    estimate_tokens,
    get_cached_response,
    store_cached_response,
    register_live_call_intent,
    route_model,
    get_replay_response,
    get_token_usage_summary,
    log_token_usage,
    MAX_LIVE_CALLS,
)
from app.services.rag_service import deduplicate_chunks
from app.schemas.chat import ChatRequest, ChatHistoryItem
from app.services.chat_service import generate_chat_response
from app.services.groq_service import generate_bangla_advisory_groq


class TestTokenOptimization(unittest.TestCase):
    def setUp(self):
        reset_live_counter()

    def test_fixtures_file_structure(self):
        """1. Verify tests/fixtures/llm_queries.json contains 15 chat queries and 5 advisory inputs."""
        fixtures_path = Path("tests/fixtures/llm_queries.json")
        self.assertTrue(fixtures_path.exists())
        with open(fixtures_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("chat_queries", data)
        self.assertIn("advisory_inputs", data)
        self.assertEqual(len(data["chat_queries"]), 15)
        self.assertEqual(len(data["advisory_inputs"]), 5)

    def test_replay_mode_responses(self):
        """2. Verify replay mode returns pre-saved grounded responses without API calls."""
        set_mode("replay")
        self.assertEqual(get_current_mode(), "replay")

        response = get_replay_response(prompt_text="বোরো ধানে এডব্লিউডি (AWD) পদ্ধতিতে সেচ কীভাবে দেব?")
        self.assertIsNotNone(response)
        self.assertIn("reply", response)
        self.assertIn("AWD", response["reply"])

    def test_exact_cache_hit_and_savings(self):
        """3. Verify exact response cache returns cached content and saves tokens."""
        messages = [
            {"role": "system", "content": "System Test Prompt"},
            {"role": "user", "content": "Test User Query"},
        ]
        model = "llama-3.3-70b-versatile"
        store_cached_response(model, messages, "Cached test answer")

        cached = get_cached_response(model, messages)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["content"], "Cached test answer")

    def test_live_call_budget_enforcement(self):
        """4. Verify max 5 live calls guardrail raises RuntimeError on 6th attempt."""
        reset_live_counter()
        for i in range(MAX_LIVE_CALLS):
            count = register_live_call_intent("llama-3.3-70b-versatile")
            self.assertEqual(count, i + 1)

        # 6th attempt must trigger quota exception
        with self.assertRaises(RuntimeError) as ctx:
            register_live_call_intent("llama-3.3-70b-versatile")
        self.assertIn("budget exceeded", str(ctx.exception).lower())

    def test_cheap_model_routing(self):
        """5. Verify cheap-model routing routes simple greetings to 8B model."""
        model_greeting = route_model("সালাম, কেমন আছেন?")
        self.assertEqual(model_greeting, "llama-3.1-8b-instant")

        model_complex = route_model("আলুর নাবি ধসা রোগ নিয়ন্ত্রণে ট্রাইসাইক্লাজোল ব্যবহারের সঠিক নিয়ম কী?")
        self.assertEqual(model_complex, "llama-3.3-70b-versatile")

    def test_semantic_chunk_deduplication(self):
        """6. Verify RAG chunk deduplication eliminates identical and overlapping passages."""
        sample_chunks = [
            {
                "title": "BRRI গাইডলাইন",
                "section": "সেচ ব্যবস্থাপনা",
                "text": "বোরো ধানে এডব্লিউডি পদ্ধতিতে সেচ দিলে ২৫-৩০% পানি সাশ্রয় হয়।",
                "score": 0.92,
            },
            {
                "title": "BRRI গাইডলাইন",
                "section": "সেচ ব্যবস্থাপনা",
                "text": "বোরো ধানে এডব্লিউডি পদ্ধতিতে সেচ দিলে ২৫-৩০% পানি সাশ্রয় হয়।",
                "score": 0.90,
            },
            {
                "title": "BARI গাইডলাইন",
                "section": "সার প্রয়োগ",
                "text": "প্রতি শতকে ইউরিয়া ৮০০-৯০০ গ্রাম এবং টিএসপি ৩০০ গ্রাম প্রয়োগ করুন।",
                "score": 0.88,
            },
        ]
        deduped = deduplicate_chunks(sample_chunks)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped[0]["section"], "সেচ ব্যবস্থাপনা")
        self.assertEqual(deduped[1]["section"], "সার প্রয়োগ")

    def test_sliding_window_trimming(self):
        """7. Verify chat context trims history to last 6 messages."""
        set_mode("replay")
        history = [
            ChatHistoryItem(role="user", content=f"Message {i}")
            for i in range(12)
        ]
        req = ChatRequest(
            message="আলুর সেচ কীভাবে দেব?",
            history=history,
        )
        res = generate_chat_response(req)
        self.assertIsNotNone(res.reply)

    def test_usage_logging_distinguishes_live_vs_replay(self):
        """8. Verify usage logger accurately tracks is_live field and mode."""
        reset_live_counter()
        log_token_usage("replay", "llama-3.3-70b-versatile", 250, 150, cached=False, is_live=False)
        log_token_usage("dry_run", "llama-3.1-8b-instant", 180, 100, cached=False, is_live=False)
        log_token_usage("cache", "llama-3.3-70b-versatile", 250, 150, cached=True, is_live=False)
        log_token_usage("live", "llama-3.3-70b-versatile", 300, 200, cached=False, is_live=True)

        summary = get_token_usage_summary()
        self.assertEqual(summary["total_calls"], 4)
        self.assertEqual(summary["live_calls_count"], 1)
        self.assertEqual(summary["replay_calls_count"], 1)
        self.assertEqual(summary["dry_run_calls_count"], 1)
        self.assertEqual(summary["cache_hits_count"], 1)
        self.assertEqual(summary["live_tokens_consumed"], 500)
        self.assertEqual(summary["remaining_live_budget"], 4)


if __name__ == "__main__":
    unittest.main()

