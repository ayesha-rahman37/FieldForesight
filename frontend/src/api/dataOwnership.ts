import api from './client';

export interface MyDataResponse {
  profile: {
    username: string;
    email: string;
    role: string;
    name?: string;
    created_at: string;
    region?: string;
  };
  prediction_history: Array<{
    prediction_id: string;
    date: string;
    crop: string;
    region: string;
    variety: string;
    yield_predicted: string;
    lower_bound?: number | null;
    upper_bound?: number | null;
  }>;
  prediction_count?: number;
  saved_preference: {
    last_crop: string | null;
    last_region: string | null;
    updated_at?: string;
  } | null;
  preferences_count?: number;
}

export interface PredictionHistoryRaw {
  id: number;
  crop: string;
  region: string;
  variety: string;
  cropping_type: string;
  predicted_yield: number;
  lower_bound?: number | null;
  upper_bound?: number | null;
  created_at: string | null;
}

export const fetchMyData = async (): Promise<MyDataResponse> => {
  const response = await api.get<MyDataResponse>('/api/data-ownership/my-data');
  return response.data;
};

export const fetchPredictionHistory = async (): Promise<PredictionHistoryRaw[]> => {
  const response = await api.get<PredictionHistoryRaw[]>('/api/predictions/history');
  return response.data;
};

export const deleteData = async (
  dataType: 'profile' | 'prediction_history' | 'preferences'
): Promise<{ success: boolean; message: string }> => {
  const response = await api.delete('/api/data-ownership/delete', {
    data: { data_type: dataType },
  });
  return response.data;
};
