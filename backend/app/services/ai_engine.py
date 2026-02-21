import httpx
import os
from typing import List, Dict, Any, Optional
import json
import asyncio

from .cache import CacheService

class AIEngine:
    def __init__(self, cache_service: Optional[CacheService] = None):
        self.api_key = os.getenv("EMERGENT_API_KEY")
        self.cache_service = cache_service
        self.base_url = os.getenv("EMERGENT_BASE_URL", "https://api.emergent.ai/v1")

        # Comprehensive Hindi/Hinglish scam keywords
        self.scam_keywords = [
            "otp", "bank", "account blocked", "lottery", "kyc", "pan card", "aadhar",
            "customer care", "prize", "gift", "refund", "unauthorized transaction",
            "jeeta hai", "inaam", "khata band", "police", "cbi", "income tax",
            "urgent", "verify", "password", "pin", "cvv",
            "khata", "vadhish", "kyc update", "paisa", "transfer", "lucky draw",
            "phonepe", "gpay", "paytm", "link pe click", "screen share", "anydesk"
        ]

        self.models = ["gpt-4o-mini", "gemini-flash", "claude-sonnet"]
        self.client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        await self.client.aclose()

    def rule_based_score(self, text: str) -> float:
        text_lower = text.lower()
        matches = [word for word in self.scam_keywords if word in text_lower]
        if not matches:
            return 0.0

        unique_matches = set(matches)
        score = min(len(unique_matches) * 0.15, 0.85)
        return score

    async def llm_score(self, text: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"score": 0.0, "reason": "No API key configured", "is_scam": False}

        if self.cache_service:
            cached_result = await self.cache_service.get(f"llm_score:{text}")
            if cached_result:
                return cached_result

        prompt = f"""
        Analyze the following call transcript for potential scam activity.
        The transcript may be in English, Hindi, or Hinglish.
        Provide a scam risk score between 0.0 and 1.0 and a brief reason.

        Transcript: "{text}"

        Output format (JSON):
        {{
            "score": float,
            "reason": "string",
            "is_scam": boolean
        }}
        """

        for model in self.models:
            try:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"}
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    content = json.loads(result['choices'][0]['message']['content'])
                    if self.cache_service:
                        await self.cache_service.set(f"llm_score:{text}", content)
                    return content
                else:
                    print(f"Model {model} failed with status {response.status_code}")
            except Exception as e:
                print(f"Error with model {model}: {e}")
                continue # Try next model

        return {"score": 0.0, "reason": "All LLMs failed or timed out", "is_scam": False}

    async def get_total_risk_score(self, text: str) -> Dict[str, Any]:
        rb_score = self.rule_based_score(text)

        if len(text.split()) < 5:
            return {
                "combined_score": rb_score,
                "rule_based_score": rb_score,
                "llm_score": 0.0,
                "reason": "Transcript too short for LLM analysis",
                "is_scam": rb_score > 0.8
            }

        llm_result = await self.llm_score(text)
        combined_score = max(rb_score, llm_result.get("score", 0.0))

        return {
            "combined_score": combined_score,
            "rule_based_score": rb_score,
            "llm_score": llm_result.get("score", 0.0),
            "reason": llm_result.get("reason", "N/A"),
            "is_scam": combined_score > 0.7
        }
