export interface User {
  id: number;
  username: string;
  email: string;
  role_id: number;
  role: string;
  is_active: boolean;
}

export interface UserPreference {
  user_id: number;
  last_crop?: string | null;
  last_region?: string | null;
}

export interface SavePreferenceRequest {
  user_id: number;
  crop: string;
  region: string;
}

export interface SaveResponse {
  success: boolean;
  message: string;
}
