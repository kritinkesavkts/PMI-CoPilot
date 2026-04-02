"""
Export API — generates and retrieves the final PMI report.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

from app.services.storage_service import storage_service
from app.agents.review_agent import review_agent
from app.agents.report_agent import report_agent

router = APIRouter(prefix="/api", tags=["export"])


@router.post("/sessions/{session_id}/export")
async def generate_report(session_id: str):
    """Generate the final report (applies review edits first)."""
    findings = storage_service.get_findings(session_id)
    if not findings:
        raise HTTPException(status_code=404, detail="No findings to export")

    # Apply review edits
    findings = review_agent.apply_edits_to_findings(session_id, findings)

    # Generate report
    report = report_agent.build_report(session_id, findings)

    session = storage_service.get_session(session_id)
    if session:
        session.status = "complete"
        storage_service.update_session(session)

    return {
        "session_id": session_id,
        "status": "complete",
        "report_summary_length": len(report.executive_summary),
        "markdown_length": len(report.report_markdown),
    }


@router.get("/sessions/{session_id}/report/json")
async def get_report_json(session_id: str):
    """Download report as JSON."""
    report = storage_service.get_report(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet")
    return JSONResponse(content=report.report_json)


@router.get("/sessions/{session_id}/report/markdown")
async def get_report_markdown(session_id: str):
    """Download report as Markdown."""
    report = storage_service.get_report(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet")
    return PlainTextResponse(
        content=report.report_markdown,
        media_type="text/markdown",
    )
