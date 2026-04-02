"""
Risk Agent — identifies operational, technical, and strategic risks.
"""

import uuid
import logging
from app.schemas.extraction import ExtractionResult
from app.schemas.findings import OperationalRisk, Severity
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class RiskAgent:
    """Analyzes extracted data to identify PMI risks."""

    def _build_context(self, extractions: list[ExtractionResult]) -> str:
        parts = []
        for ext in extractions:
            parts.append(
                f"Document: {ext.document_name} (Type: {ext.classification.document_type})\n"
                f"Entities: {ext.entities.model_dump_json()}\n"
            )
        return "\n---\n".join(parts)

    def detect(self, extractions: list[ExtractionResult]) -> list[OperationalRisk]:
        context = self._build_context(extractions)
        logger.info("Detecting risks...")

        result = llm_service.call_with_prompt_file(
            "detect_risks.txt",
            f"Extracted data from uploaded documents:\n\n{context}",
        )

        risks = []
        for item in result.get("risks", []):
            try:
                risk = OperationalRisk(
                    id=uuid.uuid4().hex[:8],
                    risk=item.get("risk", ""),
                    severity=Severity(item.get("severity", "medium")),
                    reason=item.get("reason", ""),
                    evidence=item.get("evidence", ""),
                )
                risks.append(risk)
            except Exception as e:
                logger.warning(f"Skipping malformed risk: {e}")
        return risks


risk_agent = RiskAgent()
