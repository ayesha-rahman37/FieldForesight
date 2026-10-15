import api from './client';
import type { ExplainabilityResponse } from '../features/explainability/types';

export const getExplainability = async (predictionId: number): Promise<ExplainabilityResponse> => {
  const response = await api.get<ExplainabilityResponse>(`/api/explain/${predictionId}`);
  return response.data;
};
