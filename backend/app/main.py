from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .schemas import StartSessionRequest, StartSessionResponse, SetPersonaRequest, ChatRequest, ChatResponse, AuthRequest, AuthResponse
from .store import STORE
from .assessor import Assessor
from .persistence import init_persistence, persist_final
from .bank import QUESTION_BANK

load_dotenv()

app = FastAPI(title="AI Literacy Avatar Assessor (MoD Sandbox)", version="0.1.0")

cors_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS","").split(",") if o.strip()]
if not cors_origins:
    cors_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assessor = Assessor()

STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def on_startup():
    init_persistence()

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"ok": True}

@app.get("/config")
def get_config():
    return {
        "speech_key": os.environ.get("AZURE_SPEECH_KEY", ""),
        "speech_region": os.environ.get("AZURE_SPEECH_REGION", ""),
        "backend_url": os.environ.get("PUBLIC_BACKEND_URL", "http://localhost:8000"),
    }

@app.post("/auth/verify", response_model=AuthResponse)
def verify_auth(req: AuthRequest):
    pw = os.environ.get("APP_ACCESS_PASSWORD", "")
    return AuthResponse(ok=bool(pw) and req.password == pw)

@app.post("/session/start", response_model=StartSessionResponse)
def start_session(_: StartSessionRequest):
    s = STORE.create_session()
    assistant_text = (
        "Hi — I’m your AI literacy assessment guide. Please don’t share confidential or personal data. "
        "Which role best describes you: Executive, Project Manager, Business User, End User, IT Engineer, or IT Architect?"
    )
    s.messages.append({"role":"assistant","content":assistant_text})
    return StartSessionResponse(
        session_id=s.id,
        assistant_text=assistant_text,
        suggested_personas=["EXECUTIVE","PM","BUSINESS_USER","END_USER","IT_ENGINEER","IT_ARCHITECT"]
    )

@app.post("/session/{session_id}/persona")
def set_persona(session_id: str, req: SetPersonaRequest):
    try:
        s = STORE.get(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session_not_found")
    s.persona = req.persona
    assistant_text = f"Thanks. I’ll tailor this for the {req.persona.replace('_',' ').title()} persona. Let’s begin."
    s.messages.append({"role":"assistant","content":assistant_text})
    return {"session_id": session_id, "assistant_text": assistant_text}

@app.post("/session/{session_id}/chat", response_model=ChatResponse)
async def chat(session_id: str, req: ChatRequest):
    try:
        s = STORE.get(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session_not_found")

    if s.done:
        return ChatResponse(session_id=session_id, assistant_text="Session already complete. Start a new session.", done=True, scores=s.scores, evidence=s.evidence, report=s.report)

    if not s.persona:
        txt = req.user_text.upper()
        if "EXEC" in txt: s.persona = "EXECUTIVE"
        elif txt in ["PM","PROJECT MANAGER","PROGRAM MANAGER"]: s.persona = "PM"
        elif "ARCH" in txt: s.persona = "IT_ARCHITECT"
        elif "ENGINEER" in txt or txt in ["IT ENG","IT ENGINEER","ENGINEER"]: s.persona = "IT_ENGINEER"
        elif "BUS" in txt: s.persona = "BUSINESS_USER"
        elif "END" in txt or "USER" in txt: s.persona = "END_USER"
        else:
            assistant_text = "Please choose one: Executive, Project Manager (PM), Business User, or End User."
            s.messages.append({"role":"assistant","content":assistant_text})
            return ChatResponse(session_id=session_id, assistant_text=assistant_text)

    s.messages.append({"role":"user","content": req.user_text})

    result = await assessor.next(
        persona=s.persona,
        asked_question_ids=s.asked_question_ids,
        messages=s.messages,
        current_scores=s.scores,
        current_evidence=s.evidence,
    )

    assistant_text = result["assistant_text"]
    s.messages.append({"role":"assistant","content":assistant_text})

    s.scores.update({k:int(v) for k,v in (result.get("scores") or {}).items()})
    s.evidence = list(dict.fromkeys((s.evidence or []) + (result.get("evidence") or [])))

    nid = result.get("next_question_id")
    if nid:
        s.asked_question_ids.append(nid)
        q = next((x for x in QUESTION_BANK if x["id"] == nid), None)
        if q:
            s.messages.append({"role":"assistant","content": q["prompt"]})
            assistant_text = assistant_text + "\n\n" + q["prompt"]

    s.done = bool(result.get("done"))
    s.report = result.get("report")

    if s.done and not s.persisted:
        try:
            persist_final(s)
            s.persisted = True
        except Exception as e:
            print(f"persist_final failed for session {s.id}: {e}")

    return ChatResponse(
        session_id=session_id,
        assistant_text=assistant_text,
        next_question_id=nid,
        done=s.done,
        scores=s.scores,
        evidence=s.evidence,
        report=s.report
    )
