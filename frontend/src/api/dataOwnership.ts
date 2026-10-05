import api from './client';

export interface MyDataResponse {
  profile: {
    username: string;
    email: string;
    created_at: string;
  };
  prediction_history: Array<{
    id: number;
    crop: string;
    region: string;
    predicted_yield: number;
    created_at: string;
  }>;
  saved_preference: {
    last_crop: string | null;
    last_region: string | null;
  } | null;
}

export const fetchMyData = async (): Promise<MyDataResponse> => {
  const response = await api.get<MyDataResponse>('/api/data-ownership/my_data');
  return response.data;
};

export const deleteData = async (dataType: 'profile' | 'prediction_history' | 'preferences'): Promise<{ success: boolean; message: string }> => {
  const response = await api.delete('/api/data-ownership/delete', {
    data: { data_type: dataType },
  });
  return response.data;
};
