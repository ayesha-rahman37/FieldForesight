from app.schemas.community import RegionYieldPoint, CommunityYieldAggregationResponse


def get_community_aggregation(region:str,crop:str,llm_prediction:float) -> CommunityYieldAggregationResponse:
    mock_data = [
        RegionYieldPoint(year=2023, yield_value=4.0),
        RegionYieldPoint(year=2024, yield_value=4.3),
        RegionYieldPoint(year=2025, yield_value=4.1),
    ]

    avg_yield = sum(p.yield_value for p in mock_data) / len(mock_data)

    if llm_prediction > avg_yield:
        note = f"তোমার prediction ({llm_prediction}) এলাকার গড়ের ({avg_yield:.2f}) চেয়ে বেশি।"
    else:
        note = f"তোমার prediction ({llm_prediction}) এলাকার গড়ের ({avg_yield:.2f}) কাছাকাছি বা কম।"

    return CommunityYieldAggregationResponse(
        region=region,
        crop=crop,
        district_avg_value=round(avg_yield, 2),
        historical_trend=mock_data,
        llm_prediction=llm_prediction,
        comparison_note_bn=note
    )