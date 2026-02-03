from __future__ import annotations
from sqlalchemy import Column, DateTime, Integer, String, Text, func
from .db import Base


class AssessmentReport(Base):
    __tablename__ = "assessment_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    persona = Column(String(32), nullable=True)
    scores_json = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=False)
    report_json = Column(Text, nullable=True)
