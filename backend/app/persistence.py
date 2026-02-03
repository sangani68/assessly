from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError

from .db import init_engine, get_engine, get_session_factory
from .models import Base, AssessmentReport
from .store import Session


def _sql_enabled() -> bool:
    return bool(os.environ.get("AZURE_SQL_CONNECTION_STRING"))


def _adls_enabled() -> bool:
    return bool(os.environ.get("ADLS_CONNECTION_STRING") or os.environ.get("ADLS_ACCOUNT_URL"))


def init_persistence() -> None:
    if _sql_enabled():
        init_engine()
        engine = get_engine()
        if engine is not None:
            Base.metadata.create_all(bind=engine)


def _get_blob_service() -> Optional[BlobServiceClient]:
    conn_str = os.environ.get("ADLS_CONNECTION_STRING")
    if conn_str:
        return BlobServiceClient.from_connection_string(conn_str)

    account_url = os.environ.get("ADLS_ACCOUNT_URL")
    credential = os.environ.get("ADLS_CREDENTIAL")
    if account_url and credential:
        return BlobServiceClient(account_url=account_url, credential=credential)
    return None


def _adls_container_name() -> str:
    return os.environ.get("ADLS_CONTAINER_NAME", "ai-literacy-assessments")


def _adls_prefix() -> str:
    p = os.environ.get("ADLS_BLOB_PREFIX", "").strip("/")
    return (p + "/") if p else ""


def persist_final(session: Session) -> None:
    if session.report is None:
        return

    if _sql_enabled():
        SessionLocal = get_session_factory()
        if SessionLocal is None:
            print("SQL persistence disabled: no session factory")
        else:
            with SessionLocal() as db:
                row = AssessmentReport(
                    session_id=session.id,
                    persona=session.persona,
                    scores_json=json.dumps(session.scores, ensure_ascii=False),
                    evidence_json=json.dumps(session.evidence, ensure_ascii=False),
                    report_json=json.dumps(session.report, ensure_ascii=False),
                )
                db.add(row)
                db.commit()

    if _adls_enabled():
        bsc = _get_blob_service()
        if bsc is None:
            print("ADLS persistence disabled: no blob service")
            return
        container = bsc.get_container_client(_adls_container_name())
        try:
            container.create_container()
        except ResourceExistsError:
            pass

        created = datetime.fromtimestamp(session.created_at, tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        blob_name = f"{_adls_prefix()}{session.id}_{created}.json"
        payload: Dict[str, Any] = {
            "session_id": session.id,
            "created_at": session.created_at,
            "persona": session.persona,
            "messages": session.messages,
            "scores": session.scores,
            "evidence": session.evidence,
            "report": session.report,
        }
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        container.upload_blob(
            name=blob_name,
            data=data,
            overwrite=True,
            content_settings=ContentSettings(content_type="application/json"),
        )
