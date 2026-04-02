"""
Storage Service — manages session state, file storage, and report output.
Uses JSON files for simplicity. Easily swappable to SQLite or a real DB.
"""

import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.config import settings
from app.schemas.documents import AnalysisSession, UploadedDocument
from app.schemas.findings import AnalysisFindings
from app.schemas.review import ReviewState, FinalReport

logger = logging.getLogger(__name__)


class StorageService:
    """File-based session and artifact storage."""

    def _session_path(self, session_id: str) -> Path:
        return settings.session_dir / session_id

    def _state_file(self, session_id: str) -> Path:
        return self._session_path(session_id) / "session.json"

    def _findings_file(self, session_id: str) -> Path:
        return self._session_path(session_id) / "findings.json"

    def _review_file(self, session_id: str) -> Path:
        return self._session_path(session_id) / "review.json"

    def _report_file(self, session_id: str) -> Path:
        return self._session_path(session_id) / "report.json"

    # ── Sessions ─────────────────────────────────────────
    def create_session(self, session_id: str) -> AnalysisSession:
        path = self._session_path(session_id)
        path.mkdir(parents=True, exist_ok=True)
        (path / "uploads").mkdir(exist_ok=True)

        session = AnalysisSession(session_id=session_id)
        self._save_json(self._state_file(session_id), session.model_dump(mode="json"))
        return session

    def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        state_file = self._state_file(session_id)
        if not state_file.exists():
            return None
        data = json.loads(state_file.read_text())
        return AnalysisSession(**data)

    def update_session(self, session: AnalysisSession):
        self._save_json(self._state_file(session.session_id), session.model_dump(mode="json"))

    # ── File storage ─────────────────────────────────────
    def save_upload(self, session_id: str, filename: str, content: bytes) -> str:
        """Save an uploaded file and return the file path."""
        upload_dir = self._session_path(session_id) / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename
        file_path.write_bytes(content)
        return str(file_path)

    # ── Findings ─────────────────────────────────────────
    def save_findings(self, session_id: str, findings: AnalysisFindings):
        self._save_json(self._findings_file(session_id), findings.model_dump(mode="json"))

    def get_findings(self, session_id: str) -> Optional[AnalysisFindings]:
        f = self._findings_file(session_id)
        if not f.exists():
            return None
        return AnalysisFindings(**json.loads(f.read_text()))

    # ── Review ───────────────────────────────────────────
    def save_review(self, session_id: str, review: ReviewState):
        self._save_json(self._review_file(session_id), review.model_dump(mode="json"))

    def get_review(self, session_id: str) -> Optional[ReviewState]:
        f = self._review_file(session_id)
        if not f.exists():
            return None
        return ReviewState(**json.loads(f.read_text()))

    # ── Report ───────────────────────────────────────────
    def save_report(self, session_id: str, report: FinalReport):
        self._save_json(self._report_file(session_id), report.model_dump(mode="json"))

        # Also save markdown to outputs
        md_path = settings.output_dir / f"{session_id}_report.md"
        md_path.write_text(report.report_markdown)

        json_path = settings.output_dir / f"{session_id}_report.json"
        self._save_json(json_path, report.report_json)

    def get_report(self, session_id: str) -> Optional[FinalReport]:
        f = self._report_file(session_id)
        if not f.exists():
            return None
        return FinalReport(**json.loads(f.read_text()))

    # ── Helpers ──────────────────────────────────────────
    @staticmethod
    def _save_json(path: Path, data: dict):
        path.write_text(json.dumps(data, indent=2, default=str))

    def list_sessions(self) -> list[str]:
        if not settings.session_dir.exists():
            return []
        return [
            p.name
            for p in settings.session_dir.iterdir()
            if p.is_dir() and (p / "session.json").exists()
        ]


# Singleton
storage_service = StorageService()
