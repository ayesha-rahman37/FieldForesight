export interface ScenarioRequest {
  crop: string;
  region: string;
  variety?: string;
  cropping_type?: string;
  rainfall_adjustment_percent: number;
  temperature_adjustment_percent?: number;
}

export interface ScenarioResponse {
  original_yield: number;
  adjusted_yield: number;
  lower_bound: number;
  upper_bound: number;
  adjustment_applied: number;
  message: string;
}
