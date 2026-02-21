# Real-Time Scam Call Detection Engine

This project aims to build a real-time content-based scam detection system that works even for unknown numbers.

## Tech Stack
- **Backend:** FastAPI
- **Real-time communication:** WebSocket
- **Database:** PostgreSQL
- **Cache:** Redis
- **STT:** Whisper (streaming)
- **AI Engine:** Hybrid (LLM + Rule-based scoring)
- **LLM Integration:** GPT-4o-mini (Primary), Gemini Flash (Fallback), Claude Sonnet (Advanced Reasoning)

## Features (MVP Scope)
- Real-time voice-to-text conversion
- Live AI risk scoring and dynamic risk escalation
- High-risk alert notifications
- False positive/negative reporting
- Basic scam education section

## Language Support
- Hinglish (Hindi + English mix)
- Pure Hindi
