"""
Analyze API — orchestrates the multi-agent analysis pipeline.
"""

from fastapi import APIRouter, HTTPException
from app.services.storage_service import storage_service
from app.agents.parsing_agent import parsing_agent
from app.agents.extraction_agent import extraction_agent
from app.agents.gap_agent import gap_agent
from app.agents.risk_agent import risk_agent
from app.agents.synergy_agent import synergy_agent
from app.agents.recommendation_agent import recommendation_agent
from app.schemas.findings import AnalysisFindings

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/sessions/{session_id}/analyze")
async def run_analysis(session_id: str):
    """
    Execute the full agentic pipeline:
    parse → extract → gaps → risks → synergies → recommendations
    """
    session = storage_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.documents:
        raise HTTPException(status_code=400, detail="No documents uploaded")

    # Step 1: Parse
    session.status = "parsing"
    storage_service.update_session(session)
    parsed_docs = parsing_agent.parse_all(session.documents)

    # Step 2: Extract entities & classify
    session.status = "analyzing"
    storage_service.update_session(session)
    extractions = extraction_agent.process_all(parsed_docs)

    # Step 3: Detect gaps
    gaps = gap_agent.detect(extractions)

    # Step 4: Detect risks
    risks = risk_agent.detect(extractions)

    # Step 5: Detect synergies
    synergies = synergy_agent.detect(extractions)

    # Step 6: Generate recommendations
    recommendations = recommendation_agent.recommend(gaps, risks, synergies)

    # Assemble findings
    findings = AnalysisFindings(
        session_id=session_id,
        extractions=[e.model_dump(mode="json") for e in extractions],
        integration_gaps=gaps,
        risks=risks,
        synergies=synergies,
        recommendations=recommendations,
    )

    storage_service.save_findings(session_id, findings)

    session.status = "review"
    storage_service.update_session(session)

    return {
        "session_id": session_id,
        "status": "review",
        "documents_parsed": len(parsed_docs),
        "gaps_found": len(gaps),
        "risks_found": len(risks),
        "synergies_found": len(synergies),
        "recommendations": len(recommendations),
    }


@router.get("/sessions/{session_id}/findings")
async def get_findings(session_id: str):
    """Retrieve analysis findings for a session."""
    findings = storage_service.get_findings(session_id)
    if not findings:
        raise HTTPException(status_code=404, detail="No findings available")
    return findings.model_dump(mode="json")
