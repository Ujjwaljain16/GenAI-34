from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db

router = APIRouter(prefix="/graphs", tags=["graphs"])


@router.get("/pending-review")
async def get_pending_review_graphs(db: AsyncSession = Depends(get_db)):
    """
    Returns a list of graph_versions with status = PENDING_REVIEW.
    """
    # Mock return for skeleton
    return [{"id": "uuid", "book_id": "uuid", "status": "PENDING_REVIEW"}]


@router.get("/{version_id}/full")
async def get_full_graph(version_id: str, db: AsyncSession = Depends(get_db)):
    """
    Fetches all concepts, edges, and validation results for a graph version.
    """
    # Mock return
    return {"concepts": [], "edges": [], "validation_results": []}


@router.post("/{version_id}/approve")
async def approve_graph(version_id: str, db: AsyncSession = Depends(get_db)):
    """
    Approves a graph version. Enqueues a publication job.
    """
    # Mock implementation
    # 1. Update graph_version status -> APPROVED
    # 2. Write graph_version_events
    # 3. Trigger Neo4j publication (or enqueue it)
    return {"status": "success", "message": "Graph approved and publication enqueued."}


@router.post("/{version_id}/reject")
async def reject_graph(
    version_id: str, reason: str, db: AsyncSession = Depends(get_db)
):
    """
    Rejects a graph version.
    """
    return {"status": "success", "message": "Graph rejected."}
