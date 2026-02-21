# Real-Time Scam Call Detection Engine

This project aims to build a real-time content-based scam detection system that works even for unknown numbers.

## Tech Stack
- **Backend:** FastAPI
- **Real-time communication:** WebSocket
- **Database:** SQLite (default for MVP) / PostgreSQL
- **Cache:** Redis (with in-memory fallback)
- **STT:** Whisper (streaming)
- **AI Engine:** Hybrid (LLM + Rule-based scoring)
- **LLM Integration:** GPT-4o-mini (Primary), Gemini Flash (Fallback), Claude Sonnet (Advanced Reasoning) via Emergent API Key.

## Getting Started

### Prerequisites
- Python 3.8+
- Redis (optional, system falls back to in-memory cache if not found)

### Setup
1. Clone the repository.
2. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   - Copy `.env.example` to `.env`.
   - Add your `EMERGENT_API_KEY` to the `.env` file.
   ```bash
   cp .env.example .env
   ```

### Running the Application
1. Start the FastAPI server:
   ```bash
   PYTHONPATH=. uvicorn app.main:app --reload
   ```
   The server will start at `http://localhost:8000`.

2. Open the Demo:
   - Open `demo.html` in your web browser.
   - You can type messages in the input box to simulate a call transcript.
   - The system will provide real-time risk scores and alerts.

### Testing
To run the unit tests:
```bash
PYTHONPATH=. pytest tests/test_ai_engine.py
```

## Features (MVP Scope)
- **Real-time voice-to-text:** Supports binary audio stream via WebSockets.
- **Live AI risk scoring:** Combines rule-based keyword matching with LLM analysis.
- **Dynamic risk escalation:** Alerts triggered when risk exceeds threshold (0.7).
- **High-risk alert notifications:** Visual alerts in the demo UI.
- **False positive/negative reporting:** Users can report incorrect detections.
- **Scam education section:** Provides tips on common scam types.

## Language Support
- Hinglish (Hindi + English mix)
- Pure Hindi
- English
