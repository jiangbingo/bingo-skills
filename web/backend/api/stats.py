"""
Bingo Downloader Web - Statistics API Endpoints
"""
from fastapi import APIRouter
from ..models import StatsResponse, ApiResponse

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/", response_model=StatsResponse)
async def get_stats():
    """Get download statistics"""
    from ..core import DownloadHistory, CORE_AVAILABLE

    if not CORE_AVAILABLE:
        return StatsResponse(
            total_downloads=0,
            successful_downloads=0,
            failed_downloads=0,
            success_rate=0.0,
            total_bytes=0,
            total_size_human="0 B",
            by_platform={}
        )

    history_db = DownloadHistory()
    raw_stats = history_db.get_stats()

    # Map raw stats to response model
    total = raw_stats.get('total', 0)
    success = raw_stats.get('success', 0)
    failed = raw_stats.get('failed', 0)
    total_size = raw_stats.get('total_size', 0)

    # Parse success_rate from string like "85.5%" to float
    success_rate_str = raw_stats.get('success_rate', '0%')
    success_rate_val = float(success_rate_str.rstrip('%')) if success_rate_str != '0%' else 0.0

    return StatsResponse(
        total_downloads=total,
        successful_downloads=success,
        failed_downloads=failed,
        success_rate=success_rate_val,
        total_bytes=total_size,
        total_size_human=_format_bytes(total_size),
        by_platform=raw_stats.get('by_platform', {})
    )


def _format_bytes(bytes_size: int) -> str:
    """Format bytes to human readable"""
    if bytes_size == 0:
        return "0 B"
    sizes = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while bytes_size >= 1024 and i < len(sizes) - 1:
        bytes_size /= 1024.0
        i += 1
    return f"{bytes_size:.1f} {sizes[i]}"


@router.get("/by-platform", response_model=dict)
async def get_stats_by_platform():
    """Get statistics grouped by platform"""
    from ..core import DownloadHistory, CORE_AVAILABLE

    if not CORE_AVAILABLE:
        return {}

    history_db = DownloadHistory()
    raw_stats = history_db.get_stats()

    return raw_stats.get("by_platform", {})
