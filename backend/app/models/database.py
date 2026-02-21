from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class CallRecord(Base):
    __tablename__ = "call_records"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    transcript = Column(Text)
    risk_score = Column(Float)
    is_scam = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ScamReport(Base):
    __tablename__ = "scam_reports"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer)
    reported_as = Column(String) # "false_positive" or "false_negative"
    user_feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
