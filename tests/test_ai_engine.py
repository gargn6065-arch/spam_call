import pytest
from backend.app.services.ai_engine import AIEngine
import asyncio

@pytest.fixture
def ai_engine():
    return AIEngine()

def test_rule_based_score_no_match(ai_engine):
    score = ai_engine.rule_based_score("Hello, how are you?")
    assert score == 0.0

def test_rule_based_score_with_matches(ai_engine):
    score = ai_engine.rule_based_score("Please share your OTP for KYC update")
    # Matches: otp, kyc, kyc update.
    # Wait, "kyc" is in "kyc update".
    # Unique matches: "otp", "kyc", "kyc update".
    assert score == 3 * 0.15

def test_rule_based_score_max_cap(ai_engine):
    text = "otp bank lottery kyc prize gift refund police cbi urgent"
    score = ai_engine.rule_based_score(text)
    assert score == 0.85

@pytest.mark.asyncio
async def test_get_total_risk_score_short_text(ai_engine):
    result = await ai_engine.get_total_risk_score("Hello bank")
    assert result["combined_score"] == 0.15
    assert result["reason"] == "Transcript too short for LLM analysis"

@pytest.mark.asyncio
async def test_llm_score_no_key(ai_engine):
    # Ensure it doesn't crash without API key
    result = await ai_engine.llm_score("Scam transcript")
    assert result["score"] == 0.0
    assert "No API key" in result["reason"]
