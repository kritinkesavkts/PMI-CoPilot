"""
Review Agent — manages human review state for findings.
"""

import logging
from datetime import datetime
from app.schemas.review import ReviewAction, ReviewState, ReviewStatus
from app.schemas.findings import AnalysisFindings
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


class ReviewAgent:
    """Handles human review, edit, approval, and rejection of findings."""

    def init_review(self, session_id: str) -> ReviewState:
        """Initialize a review state for a session."""
        review = ReviewState(session_id=session_id)
        storage_service.save_review(session_id, review)
        return review

    def apply_action(self, session_id: str, action: ReviewAction) -> ReviewState:
        """Apply a single review action (approve, edit, reject) to a finding."""
        review = storage_service.get_review(session_id)
        if not review:
            review = self.init_review(session_id)

        # Replace existing action for same finding, or append
        review.actions = [
            a for a in review.actions
            if not (a.finding_type == action.finding_type and a.finding_id == action.finding_id)
        ]
        review.actions.append(action)
        storage_service.save_review(session_id, review)
        return review

    def approve_all(self, session_id: str) -> ReviewState:
        """Mark the entire session as approved."""
        review = storage_service.get_review(session_id)
        if not review:
            review = self.init_review(session_id)

        review.overall_status = ReviewStatus.APPROVED
        review.approved_at = datetime.utcnow()
        storage_service.save_review(session_id, review)
        return review

    def get_review_state(self, session_id: str) -> ReviewState | None:
        return storage_service.get_review(session_id)

    def apply_edits_to_findings(
        self, session_id: str, findings: AnalysisFindings
    ) -> AnalysisFindings:
        """Apply approved edits back onto findings for report generation."""
        review = storage_service.get_review(session_id)
        if not review:
            return findings

        for action in review.actions:
            if action.status == ReviewStatus.REJECTED:
                # Remove rejected findings
                self._remove_finding(findings, action.finding_type, action.finding_id)
            elif action.status == ReviewStatus.EDITED and action.edited_content:
                self._update_finding(
                    findings, action.finding_type, action.finding_id, action.edited_content
                )
        return findings

    @staticmethod
    def _remove_finding(findings: AnalysisFindings, ftype: str, fid: str):
        attr_map = {
            "gap": "integration_gaps",
            "risk": "risks",
            "synergy": "synergies",
            "recommendation": "recommendations",
        }
        attr = attr_map.get(ftype)
        if attr:
            items = getattr(findings, attr)
            setattr(findings, attr, [i for i in items if i.id != fid])

    @staticmethod
    def _update_finding(findings: AnalysisFindings, ftype: str, fid: str, edits: dict):
        attr_map = {
            "gap": "integration_gaps",
            "risk": "risks",
            "synergy": "synergies",
            "recommendation": "recommendations",
        }
        attr = attr_map.get(ftype)
        if attr:
            items = getattr(findings, attr)
            for item in items:
                if item.id == fid:
                    for key, val in edits.items():
                        if hasattr(item, key):
                            setattr(item, key, val)


review_agent = ReviewAgent()
