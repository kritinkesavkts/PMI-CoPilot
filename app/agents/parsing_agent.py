"""
Parsing Agent — orchestrates document parsing across file types.
"""

import logging
from app.schemas.documents import UploadedDocument, ParsedDocument
from app.services.parser_service import parser_service

logger = logging.getLogger(__name__)


class ParsingAgent:
    """Parses uploaded documents into normalized text and sections."""

    def parse_document(self, doc: UploadedDocument) -> ParsedDocument:
        logger.info(f"Parsing {doc.filename} ({doc.file_type})")
        return parser_service.parse(
            file_path=doc.file_path,
            doc_id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
        )

    def parse_all(self, documents: list[UploadedDocument]) -> list[ParsedDocument]:
        results = []
        for doc in documents:
            try:
                parsed = self.parse_document(doc)
                results.append(parsed)
            except Exception as e:
                logger.error(f"Failed to parse {doc.filename}: {e}")
        return results


parsing_agent = ParsingAgent()
