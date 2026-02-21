from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
import asyncio
import os

from app.services.ai_engine import AIEngine
from app.services.stt import STTService
from app.services.cache import CacheService
from app.db.session import get_db, engine
from app.models.database import Base, CallRecord, ScamReport
from app.schemas.scam import ScamReportCreate

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time Scam Call Detection Engine")
cache_service = CacheService()
ai_engine = AIEngine(cache_service=cache_service)
stt_service = STTService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_event():
    await ai_engine.close()
    await cache_service.close()

@app.get("/")
async def root():
    return {"message": "Real-Time Scam Call Detection Engine is running"}

@app.websocket("/ws/call")
async def websocket_call_endpoint(websocket: WebSocket):
    await websocket.accept()

    current_transcript = ""
    last_analysis = {"combined_score": 0.0, "is_scam": False, "reason": "Initial"}

    try:
        while True:
            # Receive message (can be text or binary audio)
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                raise WebSocketDisconnect()

            new_text = ""
            if "text" in message:
                data = json.loads(message["text"])
                new_text = data.get("text", "")
            elif "bytes" in message:
                # Handle binary audio data
                audio_chunk = message["bytes"]
                new_text = await stt_service.transcribe_stream(audio_chunk)

            if not new_text:
                continue

            current_transcript += " " + new_text

            # Analyze transcript
            last_analysis = await ai_engine.get_total_risk_score(current_transcript.strip())

            response = {
                "transcript": current_transcript.strip(),
                "risk_score": last_analysis["combined_score"],
                "reason": last_analysis["reason"],
                "alert": last_analysis["is_scam"]
            }
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        # Save the call record on disconnect
        if current_transcript:
            with get_db() as db:
                call_record = CallRecord(
                    transcript=current_transcript.strip(),
                    risk_score=last_analysis["combined_score"],
                    is_scam=last_analysis["is_scam"]
                )
                db.add(call_record)
                db.commit()
                print(f"Saved call record {call_record.id}")
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        if not websocket.client_state.name == "DISCONNECTED":
            await websocket.close()

@app.post("/report")
async def report_scam(report: ScamReportCreate):
    with get_db() as db:
        new_report = ScamReport(
            call_id=report.call_id,
            reported_as=report.reported_as,
            user_feedback=report.user_feedback
        )
        db.add(new_report)
        db.commit()
    return {"status": "success", "message": "Report submitted"}

@app.get("/education")
async def get_education():
    return [
        {
            "type": "Lottery Scam",
            "description": "Caller claims you won a prize but asks for a processing fee.",
            "tips": ["Never pay to receive a prize.", "Verify with official sources."]
        },
        {
            "type": "Bank KYC Scam",
            "description": "Caller threatens to block your account unless you provide OTP.",
            "tips": ["Banks never ask for OTP over call.", "Visit your branch for KYC updates."]
        },
        {
            "type": "Police/CBI Impersonation",
            "description": "Caller claims you are involved in a crime and demands money.",
            "tips": ["Law enforcement doesn't settle cases over phone calls.", "Stay calm and report to local police."]
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
