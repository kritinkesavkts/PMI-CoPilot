"""
Tests for agents — validates ingestion, parsing orchestration, and review logic.
These tests do NOT call the LLM; they test the non-LLM logic paths.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.agents.ingestion_agent import ingestion_agent, ALLOWED_EXTENSIONS
from app.agents.parsing_agent import parsing_agent
from app.agents.review_agent import review_agent
from app.schemas.documents import UploadedDocument, FileType
from app.schemas.review import ReviewAction, ReviewStatus
from app.schemas.findings import (
    AnalysisFindings,
    IntegrationGap,
    OperationalRisk,
    SynergyOpportunity,
    Recommendation,
    Severity,
)


class TestIngestionAgent:
    def test_validate_allowed_files(self):
        ok, _ = ingestion_agent.validate_file("report.pdf", 1000)
        assert ok
        ok, _ = ingestion_agent.validate_file("data.csv", 1000)
        assert ok
        ok, _ = ingestion_agent.validate_file("notes.txt", 1000)
        assert ok
        ok, _ = ingestion_agent.validate_file("doc.docx", 1000)
        assert ok

    def test_reject_unsupported_extension(self):
        ok, msg = ingestion_agent.validate_file("image.png", 1000)
        assert not ok
        assert "Unsupported" in msg

    def test_reject_oversized_file(self):
        huge = 100 * 1024 * 1024  # 100MB
        ok, msg = ingestion_agent.validate_file("big.pdf", huge)
        assert not ok
        assert "too large" in msg

    def test_create_session(self):
        session = ingestion_agent.create_session()
        assert session.session_id
        assert session.status == "created"
        assert len(session.documents) == 0


class TestParsingAgent:
    def test_parse_all_with_txt(self):
        # Create a temp file and a mock UploadedDocument
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Integration test content for parsing agent.")
            f.flush()

            doc = UploadedDocument(
                id="test1",
                filename="test.txt",
                file_type=FileType.TXT,
                file_path=f.name,
                size_bytes=100,
            )

            results = parsing_agent.parse_all([doc])
            assert len(results) == 1
            assert "Integration test content" in results[0].raw_text

            os.unlink(f.name)

    def test_parse_all_handles_errors_gracefully(self):
        doc = UploadedDocument(
            id="bad1",
            filename="missing.txt",
            file_type=FileType.TXT,
            file_path="/nonexistent/path.txt",
            size_bytes=0,
        )
        # Should not crash — returns empty list since parse fails
        results = parsing_agent.parse_all([doc])
        # The TXT parser reads the file; it may return error text or skip
        assert isinstance(results, list)


class TestReviewAgent:
    def _make_findings(self, session_id: str) -> AnalysisFindings:
        return AnalysisFindings(
            session_id=session_id,
            integration_gaps=[
                IntegrationGap(
                    id="g1", gap="Duplicate CRM", severity=Severity.HIGH,
                    reason="Two CRMs", evidence="Salesforce vs HubSpot"
                ),
                IntegrationGap(
                    id="g2", gap="No DR plan", severity=Severity.MEDIUM,
                    reason="Missing plan", evidence="Not documented"
                ),
            ],
            risks=[
                OperationalRisk(
                    id="r1", risk="Key person risk", severity=Severity.HIGH,
                    reason="Tom owns everything", evidence="Single point of failure"
                ),
            ],
            synergies=[
                SynergyOpportunity(
                    id="s1", opportunity="Consolidate CRM", impact=Severity.HIGH,
                    category="cost", reason="Save $120K/yr"
                ),
            ],
            recommendations=[
                Recommendation(
                    id="rec1", action="Assess CRM consolidation",
                    priority=Severity.HIGH, owner="RevOps", reason="Cost savings"
                ),
            ],
        )

    def test_remove_rejected_findings(self):
        session_id = "test_review_session"
        findings = self._make_findings(session_id)

        # Initialize review
        review_agent.init_review(session_id)

        # Reject gap g2
        action = ReviewAction(
            finding_type="gap",
            finding_id="g2",
            status=ReviewStatus.REJECTED,
        )
        review_agent.apply_action(session_id, action)

        # Apply edits
        updated = review_agent.apply_edits_to_findings(session_id, findings)
        assert len(updated.integration_gaps) == 1
        assert updated.integration_gaps[0].id == "g1"

    def test_approve_all(self):
        session_id = "test_approve_session"
        review_agent.init_review(session_id)
        state = review_agent.approve_all(session_id)
        assert state.overall_status == ReviewStatus.APPROVED
        assert state.approved_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
