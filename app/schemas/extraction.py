"""
Schemas for entity extraction and document classification.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ExtractedEntities(BaseModel):
    """Key entities extracted from a document."""
    company_names: list[str] = []
    departments: list[str] = []
    systems: list[str] = []
    tools: list[str] = []
    roles: list[str] = []
    kpis: list[str] = []
    costs: list[str] = []
    dates: list[str] = []
    geographies: list[str] = []
    obligations: list[str] = []
    process_references: list[str] = []


class DocumentClassification(BaseModel):
    """Classification of a document by type."""
    document_type: str = Field(
        ...,
        description="E.g. 'Org Structure', 'Systems Inventory', 'Process Documentation', 'Vendor List', 'Financial Summary', 'Policy Document', 'Operating Model', 'Other'"
    )
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    reasoning: str = ""


class ExtractionResult(BaseModel):
    """Full extraction output for a single document."""
    document_id: str
    document_name: str
    classification: DocumentClassification
    entities: ExtractedEntities
