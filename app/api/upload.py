"""
Upload API — file upload and session management.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.agents.ingestion_agent import ingestion_agent

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/sessions")
async def create_session():
    """Create a new analysis session."""
    session = ingestion_agent.create_session()
    return {"session_id": session.session_id, "status": session.status}


@router.post("/sessions/{session_id}/upload")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    """Upload a document to an existing session."""
    content = await file.read()
    valid, msg = ingestion_agent.validate_file(file.filename, len(content))
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    doc = ingestion_agent.ingest_file(session_id, file.filename, content)
    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type.value,
        "size_bytes": doc.size_bytes,
    }
