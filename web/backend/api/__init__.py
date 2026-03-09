"""
Bingo Downloader Web - API Routes
"""
from fastapi import APIRouter

from .download import router as download_router
from .history import router as history_router
from .stats import router as stats_router
from .formats import router as formats_router

__all__ = ["download_router", "history_router", "stats_router", "formats_router"]
