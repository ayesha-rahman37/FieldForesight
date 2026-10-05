export interface NDVIResponse {
  region: string;
  vegetation_status: string;
  ndvi_value?: number | null;
  computed_at?: string | null;
}
