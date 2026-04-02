"""
Review API — human review workflow endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.agents.review_agent import review_agent
from app.schemas.review import ReviewAction, ReviewStatus

router = APIRouter(prefix="/api", tags=["review"])


class ReviewActionRequest(BaseModel):
    finding_type: str  # gap, risk, synergy, recommendation
    finding_id: str
    status: ReviewStatus
    edited_content: Optional[dict] = None
    annotation: str = ""


@router.post("/sessions/{session_id}/review")
async def submit_review(session_id: str, action: ReviewActionRequest):
    """Submit a review action on a specific finding."""
    review_action = ReviewAction(
        finding_type=action.finding_type,
        finding_id=action.finding_id,
        status=action.status,
        edited_content=action.edited_content,
        annotation=action.annotation,
    )
    state = review_agent.apply_action(session_id, review_action)
    return {"status": "ok", "total_actions": len(state.actions)}


@router.post("/sessions/{session_id}/approve")
async def approve_session(session_id: str):
    """Approve all findings and mark session ready for export."""
    state = review_agent.approve_all(session_id)
    return {
        "status": state.overall_status.value,
        "approved_at": str(state.approved_at),
    }


@router.get("/sessions/{session_id}/review")
async def get_review_state(session_id: str):
    """Get current review state."""
    state = review_agent.get_review_state(session_id)
    if not state:
        return {"session_id": session_id, "overall_status": "pending", "actions": []}
    return state.model_dump(mode="json")
