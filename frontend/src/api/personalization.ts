import api from './client';
import type { UserPreference, SavePreferenceRequest, SaveResponse } from '../features/personalization/types';

export const getUserPreference = async (userId: number): Promise<UserPreference> => {
  const response = await api.get<UserPreference>(`/api/personalization/${userId}`);
  return response.data;
};

export const saveUserPreference = async (payload: SavePreferenceRequest): Promise<SaveResponse> => {
  const response = await api.post<SaveResponse>('/api/personalization/save', payload);
  return response.data;
};
