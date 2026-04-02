"""
Synergy Agent — identifies value-creation opportunities.
"""

import uuid
import logging
from app.schemas.extraction import ExtractionResult
from app.schemas.findings import SynergyOpportunity, Severity
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class SynergyAgent:
    """Analyzes extracted data to find synergy opportunities."""

    def _build_context(self, extractions: list[ExtractionResult]) -> str:
        parts = []
        for ext in extractions:
            parts.append(
                f"Document: {ext.document_name} (Type: {ext.classification.document_type})\n"
                f"Entities: {ext.entities.model_dump_json()}\n"
            )
        return "\n---\n".join(parts)

    def detect(self, extractions: list[ExtractionResult]) -> list[SynergyOpportunity]:
        context = self._build_context(extractions)
        logger.info("Detecting synergies...")

        result = llm_service.call_with_prompt_file(
            "detect_synergies.txt",
            f"Extracted data from uploaded documents:\n\n{context}",
        )

        synergies = []
        for item in result.get("synergies", []):
            try:
                syn = SynergyOpportunity(
                    id=uuid.uuid4().hex[:8],
                    opportunity=item.get("opportunity", ""),
                    impact=Severity(item.get("impact", "medium")),
                    category=item.get("category", "operational"),
                    reason=item.get("reason", ""),
                )
                synergies.append(syn)
            except Exception as e:
                logger.warning(f"Skipping malformed synergy: {e}")
        return synergies


synergy_agent = SynergyAgent()
