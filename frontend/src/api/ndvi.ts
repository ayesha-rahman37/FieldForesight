import api from './client';
import type { NDVIResponse } from '../features/vegetation-health/types';

export const getNDVI = async (region: string): Promise<NDVIResponse> => {
  const response = await api.get<NDVIResponse>(`/api/ndvi/${encodeURIComponent(region)}`);
  return response.data;
};
