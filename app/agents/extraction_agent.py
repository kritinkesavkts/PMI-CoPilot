"""
Extraction Agent — classifies documents and extracts key entities via LLM.
"""

import logging
from app.schemas.documents import ParsedDocument
from app.schemas.extraction import (
    ExtractionResult,
    DocumentClassification,
    ExtractedEntities,
)
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

# Truncate document text to fit context windows
MAX_CHARS = 12_000


class ExtractionAgent:
    """Uses LLM to classify documents and extract business entities."""

    def _truncate(self, text: str) -> str:
        if len(text) > MAX_CHARS:
            return text[:MAX_CHARS] + "\n\n[... truncated ...]"
        return text

    def classify(self, doc: ParsedDocument) -> DocumentClassification:
        content = self._truncate(doc.raw_text)
        result = llm_service.call_with_prompt_file(
            "classify_document.txt",
            f"Document: {doc.filename}\n\nContent:\n{content}",
        )
        try:
            return DocumentClassification(**result)
        except Exception:
            return DocumentClassification(
                document_type="Other", confidence=0.0, reasoning="Parse error"
            )

    def extract_entities(self, doc: ParsedDocument) -> ExtractedEntities:
        content = self._truncate(doc.raw_text)
        result = llm_service.call_with_prompt_file(
            "extract_entities.txt",
            f"Document: {doc.filename}\n\nContent:\n{content}",
        )
        try:
            return ExtractedEntities(**result)
        except Exception:
            return ExtractedEntities()

    def process(self, doc: ParsedDocument) -> ExtractionResult:
        logger.info(f"Extracting from {doc.filename}")
        classification = self.classify(doc)
        entities = self.extract_entities(doc)
        return ExtractionResult(
            document_id=doc.document_id,
            document_name=doc.filename,
            classification=classification,
            entities=entities,
        )

    def process_all(self, docs: list[ParsedDocument]) -> list[ExtractionResult]:
        return [self.process(doc) for doc in docs]


extraction_agent = ExtractionAgent()
