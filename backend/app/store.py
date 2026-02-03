from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time, uuid

@dataclass
class Session:
    id: str
    created_at: float = field(default_factory=lambda: time.time())
    persona: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    asked_question_ids: List[str] = field(default_factory=list)
    scores: Dict[str, int] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    done: bool = False
    report: Optional[Dict[str, Any]] = None
    persisted: bool = False

class InMemoryStore:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self) -> Session:
        sid = uuid.uuid4().hex
        s = Session(id=sid)
        self._sessions[sid] = s
        return s

    def get(self, sid: str) -> Session:
        if sid not in self._sessions:
            raise KeyError("session_not_found")
        return self._sessions[sid]

STORE = InMemoryStore()
