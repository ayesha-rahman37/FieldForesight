import unittest
from unittest.mock import patch, MagicMock
from app.services.groq_service import stream_completion
from app.services import token_optimizer


class TestGroqStreaming(unittest.TestCase):
    def setUp(self):
        token_optimizer.reset_live_counter()
        token_optimizer._usage_logs.clear()
        token_optimizer._memory_cache.clear()

    @patch("app.services.groq_service.get_cached_response", return_value=None)
    @patch("app.services.groq_service._get_env_fallback")
    @patch("requests.post")
    def test_streaming_with_usage_metadata(self, mock_post, mock_env, mock_cache):
        """Tests stream_completion with mocked Groq response containing usage metadata."""
        token_optimizer.set_mode("live")
        mock_env.return_value = "fake_groq_key"

        mock_lines = [
            b'data: {"choices":[{"delta":{"content":"\xe0\xa6\x86\xe0\xa6\xb2\xe0\xa7\x81\xe0\xa6\xb0 "}}]}',
            b'data: {"choices":[{"delta":{"content":"\xe0\xa6\xa8\xe0\xa6\xbe\xe0\xa6\xac\xe0\xa6\xbf "}}]}',
            b'data: {"choices":[{"delta":{"content":"\xe0\xa6\xa7\xe0\xa6\xb8\xe0\xa6\xbe"}}], "usage": {"prompt_tokens": 120, "completion_tokens": 25, "total_tokens": 145}}',
            b'data: [DONE]',
        ]

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_lines.return_value = mock_lines
        mock_post.return_value = mock_resp

        messages = [
            {"role": "system", "content": "System prompt unique 1"},
            {"role": "user", "content": "আলুর নাবি ধসা রোগ পরীক্ষা"},
        ]

        deltas = list(stream_completion(messages, model="test-model-unique-1"))
        self.assertEqual("".join(deltas), "আলুর নাবি ধসা")

        # Verify usage logging
        self.assertTrue(len(token_optimizer._usage_logs) > 0)
        last_log = token_optimizer._usage_logs[-1]
        self.assertTrue(last_log["is_live"])
        self.assertFalse(last_log["is_estimated"])
        self.assertEqual(last_log["prompt_tokens"], 120)
        self.assertEqual(last_log["completion_tokens"], 25)

    @patch("app.services.groq_service.get_cached_response", return_value=None)
    @patch("app.services.groq_service._get_env_fallback")
    @patch("requests.post")
    def test_streaming_without_usage_metadata_marks_estimated(self, mock_post, mock_env, mock_cache):
        """Tests stream_completion without usage metadata falls back to is_estimated=True."""
        token_optimizer.set_mode("live")
        mock_env.return_value = "fake_groq_key"

        mock_lines = [
            b'data: {"choices":[{"delta":{"content":"\xe0\xa6\x97\xe0\xa6\xae "}}]}',
            b'data: {"choices":[{"delta":{"content":"\xe0\xa6\x9a\xe0\xa6\xbe\xe0\xa6\xb7"}}]}',
            b'data: [DONE]',
        ]

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_lines.return_value = mock_lines
        mock_post.return_value = mock_resp

        messages = [
            {"role": "system", "content": "System prompt unique 2"},
            {"role": "user", "content": "গম চাষ পদ্ধতি পরীক্ষা"},
        ]

        deltas = list(stream_completion(messages, model="test-model-unique-2"))
        self.assertEqual("".join(deltas), "গম চাষ")

        # Verify usage logging marked as estimated
        self.assertTrue(len(token_optimizer._usage_logs) > 0)
        last_log = token_optimizer._usage_logs[-1]
        self.assertTrue(last_log["is_live"])
        self.assertTrue(last_log["is_estimated"])
        self.assertGreater(last_log["prompt_tokens"], 0)
        self.assertGreater(last_log["completion_tokens"], 0)

    @patch("app.services.groq_service.get_cached_response", return_value=None)
    def test_streaming_replay_mode(self, mock_cache):
        """Tests stream_completion in replay mode yields tokens with zero API calls."""
        token_optimizer.set_mode("replay")
        messages = [
            {"role": "system", "content": "System prompt unique 3"},
            {"role": "user", "content": "আলুর নাবি ধসা রোগ প্রতিরোধ কীভাবে করব?"},
        ]
        deltas = list(stream_completion(messages, model="test-model-unique-3"))
        full_text = "".join(deltas)
        self.assertIn("নাবি ধসা", full_text)

        self.assertTrue(len(token_optimizer._usage_logs) > 0)
        last_log = token_optimizer._usage_logs[-1]
        self.assertFalse(last_log["is_live"])
        self.assertEqual(last_log["mode"], "replay")


if __name__ == "__main__":
    unittest.main()
