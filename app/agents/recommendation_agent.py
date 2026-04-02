"""
Recommendation Agent — generates a prioritized action plan from findings.
"""

import uuid
import logging
from app.schemas.findings import (
    IntegrationGap,
    OperationalRisk,
    SynergyOpportunity,
    Recommendation,
    Severity,
)
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class RecommendationAgent:
    """Synthesizes gaps, risks, and synergies into actionable recommendations."""

    def _build_context(
        self,
        gaps: list[IntegrationGap],
        risks: list[OperationalRisk],
        synergies: list[SynergyOpportunity],
    ) -> str:
        parts = ["=== INTEGRATION GAPS ==="]
        for g in gaps:
            parts.append(f"- [{g.severity.value.upper()}] {g.gap}: {g.reason}")

        parts.append("\n=== RISKS ===")
        for r in risks:
            parts.append(f"- [{r.severity.value.upper()}] {r.risk}: {r.reason}")

        parts.append("\n=== SYNERGY OPPORTUNITIES ===")
        for s in synergies:
            parts.append(f"- [{s.impact.value.upper()}] {s.opportunity}: {s.reason}")

        return "\n".join(parts)

    def recommend(
        self,
        gaps: list[IntegrationGap],
        risks: list[OperationalRisk],
        synergies: list[SynergyOpportunity],
    ) -> list[Recommendation]:
        context = self._build_context(gaps, risks, synergies)
        logger.info("Generating recommendations...")

        result = llm_service.call_with_prompt_file(
            "recommend_actions.txt",
            f"Analysis findings:\n\n{context}",
        )

        recs = []
        for item in result.get("recommendations", []):
            try:
                rec = Recommendation(
                    id=uuid.uuid4().hex[:8],
                    action=item.get("action", ""),
                    priority=Severity(item.get("priority", "medium")),
                    owner=item.get("owner", ""),
                    reason=item.get("reason", ""),
                    expected_impact=item.get("expected_impact", ""),
                    timeline=item.get("timeline", ""),
                )
                recs.append(rec)
            except Exception as e:
                logger.warning(f"Skipping malformed recommendation: {e}")
        return recs


recommendation_agent = RecommendationAgent()
