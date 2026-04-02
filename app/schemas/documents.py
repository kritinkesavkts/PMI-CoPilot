"""
Schemas for document ingestion and parsing.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"


class UploadedDocument(BaseModel):
    """Represents a single uploaded file in a session."""
    id: str = Field(..., description="Unique document identifier")
    filename: str
    file_type: FileType
    file_path: str
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class ParsedSection(BaseModel):
    """A logical section extracted from a document."""
    heading: Optional[str] = None
    content: str
    section_index: int = 0


class ParsedDocument(BaseModel):
    """Result of parsing a single document."""
    document_id: str
    filename: str
    file_type: FileType
    raw_text: str
    sections: list[ParsedSection] = []
    row_count: Optional[int] = None          # for CSV
    column_names: Optional[list[str]] = None  # for CSV
    metadata: dict = {}


class AnalysisSession(BaseModel):
    """A session groups uploaded docs and tracks workflow state."""
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    documents: list[UploadedDocument] = []
    status: str = "created"  # created | parsing | analyzing | review | complete
