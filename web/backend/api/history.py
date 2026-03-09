"""
Bingo Downloader Web - History API Endpoints
"""
from fastapi import APIRouter, Query
from ..models import HistoryResponse, ApiResponse
from typing import Optional

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    platform: Optional[str] = None
):
    """Get download history"""
    from ..core import DownloadHistory, CORE_AVAILABLE

    if not CORE_AVAILABLE:
        return HistoryResponse(total=0, records=[])

    history_db = DownloadHistory()

    if platform:
        records = history_db.get_history_by_platform(platform, limit)
    else:
        records = history_db.get_recent_history(limit)

    total = history_db.get_total_count()

    return HistoryResponse(
        total=total,
        records=records
    )


@router.delete("/clear", response_model=ApiResponse)
async def clear_history():
    """Clear all download history"""
    from ..core import DownloadHistory, CORE_AVAILABLE

    if not CORE_AVAILABLE:
        return ApiResponse(success=False, message="Core modules not available")

    history_db = DownloadHistory()
    history_db.clear_history()

    return ApiResponse(
        success=True,
        message="History cleared"
    )


@router.delete("/{record_id}", response_model=ApiResponse)
async def delete_record(record_id: int):
    """Delete a specific history record"""
    from ..core import DownloadHistory, CORE_AVAILABLE

    if not CORE_AVAILABLE:
        return ApiResponse(success=False, message="Core modules not available")

    history_db = DownloadHistory()
    history_db.delete_record(record_id)

    return ApiResponse(
        success=True,
        message=f"Record {record_id} deleted"
    )
