import unittest
from unittest.mock import Mock, patch

from app.services.data_source_status import check_weather_api


class TestWeatherStatus(unittest.TestCase):

    @patch("app.services.data_source_status.requests.get")
    def test_weather_available(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "properties": {
                "parameter": {
                    "T2M": {
                        "20240101": 20.5
                    }
                }
            }
        }
        mock_get.return_value = response

        result = check_weather_api()

        self.assertEqual(result["status"], "available")
        self.assertTrue(result["live_connection_checked"])

    @patch("app.services.data_source_status.requests.get")
    def test_weather_request_failure(self, mock_get):
        import requests
        mock_get.side_effect = requests.Timeout()

        result = check_weather_api()

        self.assertEqual(result["status"], "unavailable")
        self.assertTrue(result["live_connection_checked"])

    @patch("app.services.data_source_status.requests.get")
    def test_weather_unexpected_failure(self, mock_get):
        mock_get.side_effect = Exception("simulated failure")

        result = check_weather_api()

        self.assertEqual(result["status"], "unavailable")
        self.assertIn("Exception", result["message"])


if __name__ == "__main__":
    unittest.main()

