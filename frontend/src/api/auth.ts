import api from './client';
import type { User } from '../features/personalization/types';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CropItem {
  id: number;
  name: string;
  type?: string;
}

export interface RegionItem {
  id: number;
  name: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  region?: string;
}

export const registerUser = async (payload: RegisterPayload): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/api/auth/register', payload);
  return response.data;
};

export const loginUser = async (username: string, password: string): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/api/auth/login', { username, password });
  return response.data;
};

export const getMe = async (): Promise<User> => {
  const response = await api.get<User>('/api/auth/me');
  return response.data;
};

export const logoutUser = async (): Promise<void> => {
  try {
    await api.post('/api/auth/logout');
  } catch (err) {
    // Ignore error if session is already invalid
  }
};

export const fetchCrops = async (): Promise<string[]> => {
  const response = await api.get<any[]>('/api/crops');
  if (Array.isArray(response.data)) {
    return response.data.map((item) => (typeof item === 'object' ? item.name : String(item)));
  }
  return [];
};

export const fetchRegions = async (): Promise<string[]> => {
  const response = await api.get<any[]>('/api/regions');
  if (Array.isArray(response.data)) {
    return response.data.map((item) => (typeof item === 'object' ? item.name : String(item)));
  }
  return [];
};
