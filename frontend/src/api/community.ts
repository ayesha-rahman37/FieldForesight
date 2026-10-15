import api from './client';
import type { CommunityYieldAggregationResponse } from '../features/community/types';

export const getCommunityAggregation = async (
  region: string,
  crop: string,
  llmPrediction: number
): Promise<CommunityYieldAggregationResponse> => {
  const response = await api.get<CommunityYieldAggregationResponse>('/api/community/', {
    params: {
      region,
      crop,
      llm_prediction: llmPrediction,
    },
  });
  return response.data;
};
