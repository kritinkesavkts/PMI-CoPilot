"""
Gap Agent — detects integration mismatches and gaps across documents.
"""

import uuid
import logging
from app.schemas.extraction import ExtractionResult
from app.schemas.findings import IntegrationGap, Severity
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class GapAgent:
    """Analyzes extracted data to find integration gaps."""

    def _build_context(self, extractions: list[ExtractionResult]) -> str:
        parts = []
        for ext in extractions:
            parts.append(
                f"Document: {ext.document_name} (Type: {ext.classification.document_type})\n"
                f"Entities: {ext.entities.model_dump_json()}\n"
            )
        return "\n---\n".join(parts)

    def detect(self, extractions: list[ExtractionResult]) -> list[IntegrationGap]:
        context = self._build_context(extractions)
        logger.info("Detecting integration gaps...")

        result = llm_service.call_with_prompt_file(
            "detect_gaps.txt",
            f"Extracted data from uploaded documents:\n\n{context}",
        )

        gaps = []
        for item in result.get("integration_gaps", []):
            try:
                gap = IntegrationGap(
                    id=uuid.uuid4().hex[:8],
                    gap=item.get("gap", ""),
                    severity=Severity(item.get("severity", "medium")),
                    reason=item.get("reason", ""),
                    evidence=item.get("evidence", ""),
                )
                gaps.append(gap)
            except Exception as e:
                logger.warning(f"Skipping malformed gap: {e}")
        return gaps


gap_agent = GapAgent()
