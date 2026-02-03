from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal, Any

Persona = Literal["EXECUTIVE", "PM", "BUSINESS_USER", "END_USER", "IT_ENGINEER", "IT_ARCHITECT"]

class StartSessionRequest(BaseModel):
    user_display_name: Optional[str] = None

class StartSessionResponse(BaseModel):
    session_id: str
    assistant_text: str
    suggested_personas: List[Persona]

class SetPersonaRequest(BaseModel):
    persona: Persona

class ChatRequest(BaseModel):
    user_text: str = Field(..., min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    session_id: str
    assistant_text: str
    next_question_id: Optional[str] = None
    done: bool = False
    scores: Dict[str, int] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    report: Optional[Dict[str, Any]] = None

class AuthRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=200)

class AuthResponse(BaseModel):
    ok: bool
