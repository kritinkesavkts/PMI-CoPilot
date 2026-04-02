"""
Tests for report agent — validates markdown generation and report assembly.
These tests do NOT call the LLM; they test formatting and structure.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.agents.report_agent import report_agent
from app.schemas.findings import (
    AnalysisFindings,
    IntegrationGap,
    OperationalRisk,
    SynergyOpportunity,
    Recommendation,
    Severity,
)


class TestReportMarkdown:
    def _sample_findings(self) -> AnalysisFindings:
        return AnalysisFindings(
            session_id="test_report",
            extractions=[
                {
                    "document_name": "acquireco_model.txt",
                    "classification": {
                        "document_type": "Operating Model",
                        "confidence": 0.95,
                    },
                    "entities": {
                        "company_names": ["AcquireCo"],
                        "systems": ["Salesforce"],
                    },
                }
            ],
            integration_gaps=[
                IntegrationGap(
                    id="g1", gap="Duplicate CRM", severity=Severity.HIGH,
                    reason="Both companies run different CRMs.",
                    evidence="Salesforce vs HubSpot",
                )
            ],
            risks=[
                OperationalRisk(
                    id="r1", risk="Key person dependency", severity=Severity.MEDIUM,
                    reason="Shared services relies on one director.",
                    evidence="Tom Nguyen manages IT, HR, and Finance.",
                )
            ],
            synergies=[
                SynergyOpportunity(
                    id="s1", opportunity="Consolidate CRM", impact=Severity.HIGH,
                    category="cost", reason="Eliminate $120K in duplicate licensing.",
                )
            ],
            recommendations=[
                Recommendation(
                    id="rec1", action="Evaluate CRM consolidation within 30 days",
                    priority=Severity.HIGH, owner="Revenue Operations Lead",
                    reason="Reduces cost and unifies sales workflows.",
                    expected_impact="$120K annual savings, unified pipeline visibility",
                    timeline="30 days",
                )
            ],
        )

    def test_markdown_contains_required_sections(self):
        findings = self._sample_findings()
        md = report_agent.generate_markdown(findings, "This is the executive summary.")

        assert "# Post-Merger Integration Analysis Report" in md
        assert "## Executive Summary" in md
        assert "## Document Classifications" in md
        assert "## Integration Gaps" in md
        assert "## Operational Risks" in md
        assert "## Synergy Opportunities" in md
        assert "## Recommendations" in md

    def test_markdown_includes_findings_data(self):
        findings = self._sample_findings()
        md = report_agent.generate_markdown(findings, "Summary text here.")

        assert "Duplicate CRM" in md
        assert "Key person dependency" in md
        assert "Consolidate CRM" in md
        assert "Revenue Operations Lead" in md
        assert "acquireco_model.txt" in md

    def test_markdown_empty_findings(self):
        findings = AnalysisFindings(session_id="empty_test")
        md = report_agent.generate_markdown(findings, "No findings.")

        assert "No integration gaps detected" in md
        assert "No risks detected" in md
        assert "No synergies detected" in md
        assert "No recommendations generated" in md

    def test_severity_formatting(self):
        findings = self._sample_findings()
        md = report_agent.generate_markdown(findings, "Test summary.")

        assert "HIGH" in md
        assert "MEDIUM" in md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
