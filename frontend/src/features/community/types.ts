export interface RegionYieldPoint {
  year: number;
  yield_value: number;
}

export interface CommunityYieldAggregationResponse {
  region: string;
  crop: string;
  district_avg_value: number;
  historical_trend: RegionYieldPoint[];
  llm_prediction: number;
  comparison_note_bn: string;
}
