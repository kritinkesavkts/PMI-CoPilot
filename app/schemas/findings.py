"""
Schemas for integration gaps, risks, synergies, and recommendations.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IntegrationGap(BaseModel):
    """A detected integration mismatch or gap."""
    id: str = ""
    gap: str
    severity: Severity
    reason: str
    evidence: str = ""
    source_documents: list[str] = []


class OperationalRisk(BaseModel):
    """A PMI risk finding."""
    id: str = ""
    risk: str
    severity: Severity
    reason: str
    evidence: str = ""
    source_documents: list[str] = []


class SynergyOpportunity(BaseModel):
    """An identified value-creation opportunity."""
    id: str = ""
    opportunity: str
    impact: Severity  # reuse low/med/high as impact level
    category: str = ""  # cost, efficiency, margin, operational
    reason: str = ""
    source_documents: list[str] = []


class Recommendation(BaseModel):
    """A prioritized action item."""
    id: str = ""
    action: str
    priority: Severity
    owner: str = ""
    reason: str = ""
    expected_impact: str = ""
    timeline: str = ""


class AnalysisFindings(BaseModel):
    """Aggregated findings from the full analysis pipeline."""
    session_id: str
    extractions: list[dict] = []  # ExtractionResult dicts
    integration_gaps: list[IntegrationGap] = []
    risks: list[OperationalRisk] = []
    synergies: list[SynergyOpportunity] = []
    recommendations: list[Recommendation] = []
    executive_summary: str = ""
