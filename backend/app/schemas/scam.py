from pydantic import BaseModel
from typing import Optional

class ScamReportCreate(BaseModel):
    call_id: Optional[int] = None
    reported_as: str # "false_positive" or "false_negative"
    user_feedback: Optional[str] = None

class CallRecordBase(BaseModel):
    phone_number: str
    transcript: str
    risk_score: float
    is_scam: bool
