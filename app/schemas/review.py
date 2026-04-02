"""
Schemas for human review workflow.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EDITED = "edited"
    REJECTED = "rejected"


class ReviewAction(BaseModel):
    """A single review action on a finding."""
    finding_type: str  # gap, risk, synergy, recommendation, summary
    finding_id: str
    status: ReviewStatus
    edited_content: Optional[dict] = None
    annotation: str = ""
    reviewed_by: str = "analyst"
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewState(BaseModel):
    """Overall review state for a session."""
    session_id: str
    actions: list[ReviewAction] = []
    overall_status: ReviewStatus = ReviewStatus.PENDING
    approved_at: Optional[datetime] = None


class FinalReport(BaseModel):
    """The final deliverable after human review."""
    session_id: str
    title: str = "Post-Merger Integration Analysis Report"
    executive_summary: str = ""
    document_classifications: list[dict] = []
    integration_gaps: list[dict] = []
    risks: list[dict] = []
    synergies: list[dict] = []
    recommendations: list[dict] = []
    review_state: ReviewState | None = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    report_markdown: str = ""
    report_json: dict = {}
