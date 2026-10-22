import unittest
from unittest.mock import patch

import pandas as pd

from app.services.data_fusion_service import (
    get_regional_environmental_data,
)


class TestDataFusionService(unittest.TestCase):

    def test_unknown_district(self):
        result = get_regional_environmental_data("InvalidDistrict")

        self.assertEqual(result["region"], "InvalidDistrict")
        self.assertEqual(result["weather"]["status"], "unavailable")
        self.assertEqual(result["satellite"]["status"], "unavailable")

    @patch("app.services.data_fusion_service.fetch_ndvi_for_region")
    @patch("app.services.data_fusion_service.fetch_weather_data")
    def test_both_sources_available(self, mock_weather, mock_ndvi):
        mock_weather.return_value = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-02-01"]),
            "temperature": [24.0, 26.0],
            "rainfall": [5.0, 10.0],
        })
        mock_ndvi.return_value = 0.65

        result = get_regional_environmental_data(
            "Dhaka", start_year=2024, end_year=2024
        )

        self.assertEqual(result["weather"]["status"], "available")
        self.assertEqual(result["satellite"]["status"], "available")
        self.assertEqual(result["satellite"]["ndvi_value"], 0.65)
        self.assertEqual(
            result["satellite"]["vegetation_status"], "Healthy"
        )
        mock_weather.assert_called_once()
        mock_ndvi.assert_called_once_with("Dhaka")

    @patch("app.services.data_fusion_service.fetch_ndvi_for_region")
    @patch("app.services.data_fusion_service.fetch_weather_data")
    def test_weather_failure_does_not_stop_satellite(
        self, mock_weather, mock_ndvi
    ):
        mock_weather.side_effect = RuntimeError("Weather API unavailable")
        mock_ndvi.return_value = 0.35

        result = get_regional_environmental_data(
            "Dhaka", start_year=2024, end_year=2024
        )

        self.assertEqual(result["weather"]["status"], "unavailable")
        self.assertIn("error", result["weather"])
        self.assertEqual(result["satellite"]["status"], "available")
        self.assertEqual(
            result["satellite"]["vegetation_status"], "Moderate"
        )


if __name__ == "__main__":
    unittest.main()

