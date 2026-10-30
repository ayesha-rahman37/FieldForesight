# FieldForesight
### AI-Powered Agricultural Yield Prediction and Decision Support System

FieldForesight is an academic agricultural decision-support platform that combines crop-yield forecasting, historical agricultural data, and an AI-assisted agricultural chatbot in a web application. It uses a React frontend and a FastAPI backend, with Prophet for time-series forecasting and a LangGraph/Groq-powered assistant supported by retrieval-augmented generation (RAG).

> **Important:** This is an academic prototype. Forecasts and chatbot responses should be independently checked before being used for real farming decisions.

## Features

- **Crop yield forecasting:** Time-series forecasts generated with trained Prophet models.
- **Crop and region coverage:** The local training dataset was reported to cover 26 crop-region combinations.
- **Historical yield records:** Historical agricultural data is loaded and exposed through backend APIs.
- **Prediction history:** Previously generated prediction records can be viewed in the application.
- **Agricultural chatbot:** A LangGraph agent uses a Groq-hosted language model to answer user questions.
- **RAG-based knowledge retrieval:** ChromaDB stores indexed agricultural knowledge chunks represented using a character n-gram HashingVectorizer.
- **Web dashboard:** React interface for accessing prediction and agricultural information.
- **REST API:** FastAPI endpoints with interactive API documentation.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, TypeScript, Vite |
| Backend | Python, FastAPI, SQLAlchemy |
| Forecasting | Prophet |
| Agent orchestration | LangGraph, LangChain |
| LLM provider | Groq API |
| Retrieval | ChromaDB, scikit-learn HashingVectorizer |
| Database | SQLite by default; PostgreSQL can be configured through `DATABASE_URL` |
| Optional graph integration | Neo4j |

## Architecture Overview

1. The React frontend sends HTTP requests to the FastAPI backend.
2. The backend routes requests to prediction, history, and chatbot services.
3. Prophet models generate crop-yield forecasts from historical time-series data.
4. The LangGraph agent coordinates chatbot reasoning and its available tools.
5. The RAG service retrieves relevant indexed text chunks from ChromaDB and supplies them as context to the agent.
6. The backend returns results to the frontend.

More technical details are available in [ARCHITECTURE.md](ARCHITECTURE.md) and [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md).

## Repository Structure

```text
FieldForesight/
├── app/                 # FastAPI application, routes, models, services and scripts
│   ├── data/            # Datasets and selected local model artifacts
│   ├── models/          # SQLAlchemy models and schemas
│   ├── routes/          # API route handlers
│   ├── scripts/         # Data loading and RAG indexing scripts
│   └── services/        # Prediction, LangGraph, RAG and supporting services
├── frontend/            # React + TypeScript + Vite application
├── alembic/             # Database migrations
├── docs/knowledge/      # Markdown agricultural knowledge documents
├── requirements.txt     # Python dependencies
├── train_model.py       # Crop-region Prophet model training
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.11 recommended (the repository Dockerfile uses Python 3.11).
- Node.js and npm compatible with the Vite version specified in `frontend/package.json`.
- A Groq API key for LLM-powered chatbot functionality.
- Optional: Docker and Docker Compose for the container configuration.

## Local Setup (Windows PowerShell)

### 1. Clone the repository

```powershell
git clone https://github.com/ayesha-rahman37/FieldForesight.git
cd FieldForesight
```

### 2. Create and activate a Python virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use `.venv\Scripts\python.exe` directly or adjust the local execution policy for the current user.

### 3. Install backend dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Open `.env` and add your own credentials. At minimum, set a valid `GROQ_API_KEY` for the chatbot. Never commit `.env` or real API credentials to GitHub.

The example file documents Groq, database, frontend-origin, optional Sentinel Hub, Neo4j, and MCP configuration. Only configure optional integrations that you actually use.

### 5. Start the backend

From the repository root:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API base URL: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

At startup, the application initializes database tables and attempts to load seed data and connect to the configured graph service. A successful API startup does not mean every optional integration is available; review any startup warnings.

### 6. Install frontend dependencies

Open a second terminal:

```powershell
cd frontend
npm ci
```

### 7. Start the frontend

```powershell
npm run dev
```

Open http://localhost:5173 in your browser.

### 8. Build the frontend for production

From the `frontend` directory:

```powershell
npm run build
```

The generated `frontend/dist/` directory is a build artifact and is intentionally excluded from Git.

## Training and Rebuilding Local Artifacts

### Prophet forecasting models

The training script groups historical records by crop and region and saves a separate Prophet model for each supported combination under `app/data/models/`.

After the backend has initialized and the historical data is available in the configured database, run this command from the repository root:

```powershell
python train_model.py
```

The local training snapshot used during development was reported as 260 historical records across 26 crop-region combinations for 2015–2024. This is a dataset description, not an accuracy guarantee. Validate models using held-out temporal data before relying on forecasts.

Model binary files (`.pkl`/`.joblib`) are excluded from normal Git tracking by `.gitignore`; retrain models locally when required. The current repository contains only selected model artifacts, not a guarantee that every crop-region model binary is included.

### RAG knowledge index

The agricultural Markdown knowledge files are stored in `docs/knowledge/`. The local ChromaDB collection directory is excluded from Git. To rebuild it from the checked-in Markdown files, run from the repository root:

```powershell
python -m app.scripts.build_rag_index
```

The development index was reported as 7 documents and 28 chunks. The generated index is local runtime data and is not automatically included in a fresh clone.

## Limitations

- Forecast reliability is constrained by the amount, coverage, and quality of historical data. Out-of-sample performance needs further validation.
- Chatbot responses may be incorrect or incomplete. Fertilizer rates, pesticide guidance, and disease-treatment suggestions must be checked against current official agricultural recommendations.
- Retrieved context does not guarantee source-level citations or complete document provenance in every chatbot response.
- Neo4j is optional and requires a separately running, correctly configured graph database. Graph functions are unavailable when Neo4j cannot be reached.
- A successful local development run does not constitute a production deployment or security review.

## Documentation

- [System Architecture](ARCHITECTURE.md)
- [RAG Architecture](RAG_ARCHITECTURE.md)
- [Prompt notes](PROMPTS.md)

## Security Notes

- Keep `.env`, API keys, database passwords, and private credentials out of version control.
- Use unique, strong credentials for local and deployed services.
- Do not expose development database ports or default credentials to the public internet.
- The current source includes fallback development credentials for the MCP and Neo4j integrations, and the current Compose file includes example database credentials. Configure strong secrets through environment variables before exposing any service beyond localhost; remove hardcoded fallbacks before production deployment.
- Rotate any credential that has ever been committed to a public repository.

## Disclaimer

FieldForesight is an academic prototype intended for learning, demonstration, and decision-support research. It is not a substitute for official agricultural extension services, laboratory diagnosis, or qualified agronomic advice.

## License

No license is currently specified. Unless a license is added to this repository, reuse and redistribution are not automatically granted.
