export interface ExplainabilityResponse {
  prediction_id: number;
  crop: string;
  region: string;
  contributions: Record<string, number>;
  top_factor: string;
  summary_text_bn: string;
}
