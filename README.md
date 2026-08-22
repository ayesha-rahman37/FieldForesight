# FieldForesight (YieldMax)

AI-powered crop yield prediction platform for Bangladeshi farmers, built for the International AI Builders Congress 2026 — AgriSphere AI domain, YieldMax challenge.

## Project Overview

FieldForesight predicts crop yield across seasons using historical weather and yield data, combined with scenario planning and Bangla-language advisory — helping smallholder farmers make informed decisions without requiring expensive hardware or sensors.

## Tech Stack

- **Backend:** FastAPI (Python)
- **ML/Prediction:** Prophet (time-series forecasting)
- **Database:** PostgreSQL
- **Frontend:** React
- **LLM Advisory:** Groq API
- **Deployment:** Render (backend) + Vercel (frontend)

## Project Structure

```
FieldForesight/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   └── schemas.py       # Request/response data models
│   ├── routes/
│   │   └── prediction.py    # API endpoints
│   ├── services/
│   │   └── prediction_service.py   # Core prediction logic
│   └── data/                # Dataset & trained model (not tracked in git)
├── train_model.py           # Script to train the Prophet model
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
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the model
**Important:** This step is required before running the server, as the trained model file is not tracked in git.
```bash
python train_model.py
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Test the API
Open your browser and go to:
```
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/predict` | Returns yield prediction with confidence range |

### Example Request
```json
{
  "crop": "Rice",
  "region": "Rangpur",
  "variety": "HYV"
}
```

### Example Response
```json
{
  "predicted_yield": 4.89,
  "lower_bound": 4.67,
  "upper_bound": 5.1,
  "message": "Forecast ready for Rice in Rangpur"
}
```

## Current Status

- [x] Backend base structure
- [x] Prophet model training pipeline
- [x] Prediction API (dummy data)
- [ ] Real historical dataset integration
- [ ] Recent-anomaly weighting
- [ ] Variety-aware & mixed-cropping support
- [ ] Frontend (React)
- [ ] Bangla advisory (Groq API)
- [ ] Admin panel & authentication

## Challenge

**YieldMax** — Predictive yield optimization across seasons, under AgriSphere AI domain, International AI Builders Congress 2026.
