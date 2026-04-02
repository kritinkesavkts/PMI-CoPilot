"""
Report Agent — generates the final executive summary and structured PMI report.
"""

import logging
from datetime import datetime
from app.schemas.findings import AnalysisFindings
from app.schemas.review import FinalReport, ReviewState
from app.services.llm_service import llm_service
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


class ReportAgent:
    """Generates executive summary and assembles the final deliverable."""

    def generate_executive_summary(self, findings: AnalysisFindings) -> str:
        """Use LLM to generate a polished executive summary."""
        context_parts = []

        context_parts.append(f"Documents analyzed: {len(findings.extractions)}")

        context_parts.append(f"\nIntegration Gaps ({len(findings.integration_gaps)}):")
        for g in findings.integration_gaps:
            context_parts.append(f"  - [{g.severity.value}] {g.gap}")

        context_parts.append(f"\nRisks ({len(findings.risks)}):")
        for r in findings.risks:
            context_parts.append(f"  - [{r.severity.value}] {r.risk}")

        context_parts.append(f"\nSynergies ({len(findings.synergies)}):")
        for s in findings.synergies:
            context_parts.append(f"  - [{s.impact.value}] {s.opportunity}")

        context_parts.append(f"\nRecommendations ({len(findings.recommendations)}):")
        for rec in findings.recommendations:
            context_parts.append(f"  - [{rec.priority.value}] {rec.action}")

        context = "\n".join(context_parts)

        result = llm_service.call_with_prompt_file(
            "executive_summary.txt",
            f"Analysis summary:\n\n{context}",
        )
        return result.get("executive_summary", "Executive summary generation failed.")

    def generate_markdown(self, findings: AnalysisFindings, summary: str) -> str:
        """Build a complete markdown report."""
        lines = [
            "# Post-Merger Integration Analysis Report",
            f"\n*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n",
            "---\n",
            "## Executive Summary\n",
            summary,
            "\n---\n",
            "## Document Classifications\n",
        ]

        for ext in findings.extractions:
            cls = ext.get("classification", {})
            lines.append(
                f"- **{ext.get('document_name', 'Unknown')}**: "
                f"{cls.get('document_type', 'Unclassified')} "
                f"(confidence: {cls.get('confidence', 0):.0%})"
            )

        lines.append("\n---\n")
        lines.append("## Integration Gaps\n")
        if findings.integration_gaps:
            for g in findings.integration_gaps:
                lines.append(f"### {g.gap}")
                lines.append(f"- **Severity:** {g.severity.value.upper()}")
                lines.append(f"- **Reason:** {g.reason}")
                if g.evidence:
                    lines.append(f"- **Evidence:** {g.evidence}")
                lines.append("")
        else:
            lines.append("*No integration gaps detected.*\n")

        lines.append("---\n")
        lines.append("## Operational Risks\n")
        if findings.risks:
            for r in findings.risks:
                lines.append(f"### {r.risk}")
                lines.append(f"- **Severity:** {r.severity.value.upper()}")
                lines.append(f"- **Reason:** {r.reason}")
                if r.evidence:
                    lines.append(f"- **Evidence:** {r.evidence}")
                lines.append("")
        else:
            lines.append("*No risks detected.*\n")

        lines.append("---\n")
        lines.append("## Synergy Opportunities\n")
        if findings.synergies:
            for s in findings.synergies:
                lines.append(f"### {s.opportunity}")
                lines.append(f"- **Impact:** {s.impact.value.upper()}")
                lines.append(f"- **Category:** {s.category}")
                lines.append(f"- **Rationale:** {s.reason}")
                lines.append("")
        else:
            lines.append("*No synergies detected.*\n")

        lines.append("---\n")
        lines.append("## Recommendations\n")
        if findings.recommendations:
            lines.append("| # | Action | Priority | Owner | Timeline |")
            lines.append("|---|--------|----------|-------|----------|")
            for i, rec in enumerate(findings.recommendations, 1):
                lines.append(
                    f"| {i} | {rec.action} | {rec.priority.value.upper()} | "
                    f"{rec.owner} | {rec.timeline} |"
                )
            lines.append("")
        else:
            lines.append("*No recommendations generated.*\n")

        return "\n".join(lines)

    def build_report(self, session_id: str, findings: AnalysisFindings) -> FinalReport:
        """Full report generation pipeline."""
        logger.info(f"Generating report for session {session_id}")

        summary = self.generate_executive_summary(findings)
        findings.executive_summary = summary

        markdown = self.generate_markdown(findings, summary)

        report_json = {
            "session_id": session_id,
            "executive_summary": summary,
            "document_count": len(findings.extractions),
            "integration_gaps": [g.model_dump(mode="json") for g in findings.integration_gaps],
            "risks": [r.model_dump(mode="json") for r in findings.risks],
            "synergies": [s.model_dump(mode="json") for s in findings.synergies],
            "recommendations": [r.model_dump(mode="json") for r in findings.recommendations],
        }

        review_state = storage_service.get_review(session_id)

        report = FinalReport(
            session_id=session_id,
            executive_summary=summary,
            document_classifications=[
                ext.get("classification", {}) for ext in findings.extractions
            ],
            integration_gaps=[g.model_dump(mode="json") for g in findings.integration_gaps],
            risks=[r.model_dump(mode="json") for r in findings.risks],
            synergies=[s.model_dump(mode="json") for s in findings.synergies],
            recommendations=[r.model_dump(mode="json") for r in findings.recommendations],
            review_state=review_state,
            report_markdown=markdown,
            report_json=report_json,
        )

        storage_service.save_report(session_id, report)
        storage_service.save_findings(session_id, findings)

        return report


report_agent = ReportAgent()
