# FieldForesight
### AI-Powered Agricultural Yield Prediction and Decision Support System

FieldForesight is an AI-powered agricultural decision support system designed to support crop yield forecasting and provide agriculture-related information through an intelligent chatbot. The platform combines machine learning, time-series forecasting, retrieval-augmented generation (RAG), and a web-based interface to help users explore agricultural insights.

## Key Features

- **Crop Yield Prediction:** Forecasts crop yield using trained Prophet time-series models.
- **Multi-Crop and Regional Forecasting:** Includes trained models for 26 crop-region combinations.
- **Historical Yield Data:** Stores and displays historical agricultural yield records.
- **Agricultural Chatbot:** Provides agriculture-related responses using a LangGraph-based agent and Groq LLM.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant information from an indexed agricultural knowledge collection using ChromaDB.
- **Yield Insights Dashboard:** Presents agricultural information and prediction results through a web interface.
- **REST API:** Provides backend services through FastAPI.

## Technology Stack

### Frontend
- React 19
- TypeScript
- Vite

### Backend
- Python
- FastAPI
- SQLAlchemy

### Machine Learning and AI
- Prophet for time-series forecasting
- LangGraph for agent orchestration
- Groq API for language model integration
- ChromaDB for vector storage and retrieval
- HashingVectorizer for text representation

## System Architecture

The application follows a frontend-backend architecture.

1. The React frontend sends requests to the FastAPI backend.
2. The backend processes prediction, historical data, and chatbot requests.
3. Prophet models generate yield forecasts.
4. The chatbot uses LangGraph to coordinate the AI workflow.
5. The RAG service retrieves relevant indexed agricultural knowledge from ChromaDB.
6. Results are returned to the frontend for presentation.

## Project Structure

```text
FieldForesight/
│
├── app/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   ├── data/
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*Note: This is a simplified overview. Actual files and directories may vary.*

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FieldForesight
```

### 2. Create a Python Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and configure the required values.

Example:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
CHATBOT_MAX_TOKENS=3000
```

Never commit your actual `.env` file or API keys to GitHub.

### 5. Run the Backend

From the project root:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Install Frontend Dependencies

Open another terminal:

```bash
cd frontend
npm install
```

### 7. Run the Frontend

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## Model and Knowledge Base

### Yield Forecasting

Prophet time-series models are used for agricultural yield forecasting. The current training dataset contains:

- 260 historical yield records
- 26 crop-region combinations
- Historical years from 2015 to 2024

Forecast performance depends on the availability, quality, and coverage of historical data.

### Agricultural Knowledge Retrieval

The RAG component uses ChromaDB for persistent vector storage and a character n-gram HashingVectorizer for text representation.

The indexed knowledge collection currently contains:

- 7 documents
- 28 text chunks

Retrieved content is provided to the chatbot as contextual information for generating agriculture-related responses.

## Limitations

- Prediction quality depends on the available historical dataset and model performance.
- Agricultural chatbot responses may require verification against authoritative agricultural guidelines.
- Retrieved information may not cover every crop, region, or agricultural condition.
- Source-level citations and complete document provenance are not currently guaranteed.
- The Neo4j knowledge graph connection may require additional configuration; graph functionality should not be considered available unless the database is running and verified.

## Future Improvements

- Expand the historical agricultural dataset.
- Improve forecasting evaluation and model validation.
- Add verified agricultural sources and document-level citations.
- Improve multilingual agricultural question answering.
- Complete and validate knowledge graph integration.
- Enhance deployment, monitoring, and scalability.

## Disclaimer

FieldForesight is an academic decision-support project. Its predictions and chatbot responses are intended for informational purposes and should not replace verified agricultural recommendations from qualified experts or official agricultural authorities.

## License

This project is developed for academic purposes. Add an appropriate open-source license before permitting external reuse.
