import unittest
from app.services.rag_service import retrieve
import app.services.rag_service as rs


class TestRAGRetrieval(unittest.TestCase):
    def test_rag_signature_and_fields(self):
        results = retrieve("ধানের সেচ কখন দেব?", crop="Rice", k=2)
        self.assertIsInstance(results, list)
        if results:
            for item in results:
                self.assertIn("text", item)
                self.assertIn("title", item)
                self.assertIn("section", item)
                self.assertIn("score", item)
                self.assertIsInstance(item["score"], float)
                self.assertGreaterEqual(item["score"], 0.82)

    def test_crop_metadata_filter(self):
        potato_results = retrieve("নাবি ধসা রোগ", crop="Potato", k=3)
        self.assertTrue(len(potato_results) > 0)
        for r in potato_results:
            self.assertIn("আলু", r["title"])

    def test_out_of_domain_query_rejected(self):
        results = retrieve("মহাকাশযান ও রকেট প্রযুক্তি", crop="Wheat", k=2)
        self.assertEqual(len(results), 0)

    def test_missing_collection_handling(self):
        original = rs.RAG_COLLECTION_NAME
        try:
            rs.RAG_COLLECTION_NAME = "non_existent_knowledge_store"
            results = retrieve("যেকোনো প্রশ্ন", crop="Rice")
            self.assertEqual(results, [])
        finally:
            rs.RAG_COLLECTION_NAME = original


if __name__ == "__main__":
    unittest.main()

