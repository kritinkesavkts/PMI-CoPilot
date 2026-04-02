"""
Ingestion Agent — handles file uploads, validation, and session creation.
"""

import uuid
import logging
from pathlib import Path

from app.config import settings
from app.schemas.documents import AnalysisSession, UploadedDocument, FileType
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv"}
EXTENSION_TO_TYPE = {
    ".pdf": FileType.PDF,
    ".docx": FileType.DOCX,
    ".txt": FileType.TXT,
    ".csv": FileType.CSV,
}


class IngestionAgent:
    """Validates and ingests uploaded files into a session."""

    def create_session(self) -> AnalysisSession:
        session_id = uuid.uuid4().hex[:12]
        return storage_service.create_session(session_id)

    def validate_file(self, filename: str, size_bytes: int) -> tuple[bool, str]:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        max_bytes = settings.max_upload_mb * 1024 * 1024
        if size_bytes > max_bytes:
            return False, f"File too large: {size_bytes / 1e6:.1f}MB. Max: {settings.max_upload_mb}MB"
        return True, "OK"

    def ingest_file(
        self, session_id: str, filename: str, content: bytes
    ) -> UploadedDocument:
        """Save a file to the session and return an UploadedDocument record."""
        ext = Path(filename).suffix.lower()
        file_type = EXTENSION_TO_TYPE[ext]
        doc_id = uuid.uuid4().hex[:10]

        file_path = storage_service.save_upload(session_id, filename, content)

        doc = UploadedDocument(
            id=doc_id,
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            size_bytes=len(content),
        )

        # Update session
        session = storage_service.get_session(session_id)
        if session:
            session.documents.append(doc)
            storage_service.update_session(session)

        logger.info(f"Ingested {filename} ({file_type}) into session {session_id}")
        return doc


ingestion_agent = IngestionAgent()
