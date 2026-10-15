# FieldForesight (YieldMax)

AI-powered crop yield prediction platform for Bangladeshi farmers, built for the International AI Builders Congress 2026 — AgriSphere AI domain, YieldMax challenge.

## Project Overview

FieldForesight predicts crop yield across seasons using historical yield data and time-series machine learning, combined with crop variety and cropping-type adjustments.

The platform is designed to help farmers and agricultural stakeholders make data-driven yield decisions without requiring expensive hardware or sensors.

## Tech Stack

- **Backend:** FastAPI (Python)
- **ML/Prediction:** Prophet (time-series forecasting)
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Model Serialization:** Joblib
- **API Documentation:** FastAPI Swagger UI

## Project Structure

```text
FieldForesight/

├── app/
│   ├── main.py                         # FastAPI application entry point
│   ├── database.py                     # Database configuration
│   │
│   ├── models/
│   │   ├── schemas.py                  # Prediction request/response models
│   │   ├── prediction_history.py       # Prediction history database model
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── session.py
│   │   ├── user_preference.py
│   │   ├── explainability_cache.py
│   │   └── ndvi_cache.py
│   │
│   ├── routes/
│   │   ├── prediction.py               # Yield prediction API
│   │   ├── history.py                  # Prediction history API
│   │   ├── crops.py                    # Crop API
│   │   ├── regions.py                  # Region API
│   │   ├── auth.py
│   │   ├── explainability.py
│   │   ├── scenario_planner.py
│   │   ├── personalization.py
│   │   ├── ndvi.py
│   │   ├── community.py
│   │   └── data_ownership.py
│   │
│   ├── services/
│   │   ├── prediction_service.py       # Core prediction logic
│   │   ├── adjustment_rules.py         # Variety and cropping adjustments
│   │   ├── auth_service.py
│   │   ├── explainability_service.py
│   │   ├── scenario_planner_service.py
│   │   ├── personalization_service.py
│   │   ├── ndvi_service.py
│   │   └── data_ownership_service.py
│   │
│   ├── data/                           # Dataset and trained model
│   ├── templates/
│   │   └── index.html                  # Web dashboard
│   └── static/
│       └── style.css                   # Frontend styling
│
├── train_model.py                      # Prophet model training
├── requirements.txt
└── .gitignore
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ayesha-rahman37/FieldForesight.git
cd FieldForesight
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Train the model

**Important:** The trained model file is generated locally and is not tracked in git.

Make sure the required historical dataset is available and run:

```bash
python train_model.py
```

The trained model will be saved as:

```text
app/data/trained_model.pkl
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

### 6. Open the web dashboard

```text
http://127.0.0.1:8000
```

### 7. Test the API

Open:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/predict` | Returns crop yield prediction with confidence range |
| GET | `/api/predictions/history` | Returns previous prediction records |
| GET | `/api/crops` | Returns available crops |
| GET | `/api/regions` | Returns available regions |

Additional modules are available for authentication, explainability, scenario planning, personalization, NDVI, community features, and data ownership.

## Prediction API

### Example Request

```json
{
  "crop": "Rice",
  "region": "Rangpur",
  "variety": "HYV",
  "cropping_type": "single"
}
```

### Example Response

```json
{
  "predicted_yield": 4.89,
  "lower_bound": 4.67,
  "upper_bound": 5.10,
  "message": "Yield prediction generated for Rice in Rangpur using HYV variety and single cropping."
}
```

## Prediction Logic

The prediction system uses Prophet for time-series forecasting.

The prediction pipeline is:

```text
Historical Yield Data
        ↓
Recent-Anomaly Weighting
        ↓
Prophet Forecasting
        ↓
Base Yield Prediction
        ↓
Variety Adjustment
        ↓
Cropping-Type Adjustment
        ↓
Final Prediction
        ↓
Prediction History
```

### Variety Support

| Variety | Coefficient |
|---|---:|
| HYV | 1.00 |
| Local | 0.82 |

### Cropping-Type Support

| Cropping Type | Coefficient |
|---|---:|
| Single | 1.00 |
| Intercrop | 0.88 |
| Rotation | 0.95 |

## Prediction History

Each successful prediction is stored in the database.

Stored information includes:

- Crop
- Region
- Variety
- Cropping type
- Predicted yield
- Lower prediction bound
- Upper prediction bound
- Prediction timestamp

The stored records can be retrieved using:

```text
GET /api/predictions/history
```
