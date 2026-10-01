# Cloud Fallback Rule

The system should prefer the locally trained crop-region Prophet model whenever sufficient historical data is available.

## Primary Rule

If a valid local crop-region model exists and sufficient historical data is available:

Final Prediction = Local Prophet Prediction

## Fallback Rule

If the local crop-region model is unavailable or the local historical dataset is insufficient:

Fallback Prediction = Cloud-Supported Estimate

## Combined Formula

Final Prediction = (1 - Fallback Weight) × Local Prediction
                 + Fallback Weight × Fallback Estimate

Where:

Fallback Weight = 0 when reliable local prediction is available.

Fallback Weight increases when local historical coverage is insufficient.

## Priority

Local Historical Data
        ↓
Local Prophet Model
        ↓
Validated Local Prediction
        ↓
Cloud Fallback Estimate