import api from './client';
import type { ScenarioRequest, ScenarioResponse } from '../features/scenario-planner/types';

export const runScenario = async (payload: ScenarioRequest): Promise<ScenarioResponse> => {
  const response = await api.post<ScenarioResponse>('/api/scenario/', payload);
  return response.data;
};
