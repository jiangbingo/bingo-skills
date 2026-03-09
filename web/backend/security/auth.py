"""
Bingo Downloader Web - API Key Authentication
Optional API Key authentication for API endpoints
"""
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Optional
import os

# Configuration
API_KEY_ENABLED = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
API_KEY_NAME = os.getenv("API_KEY_NAME", "X-API-Key")
VALID_API_KEYS = set(
    key.strip()
    for key in os.getenv("API_KEYS", "").split(",")
    if key.strip()
)

# Public endpoints that don't require authentication
PUBLIC_PATHS = [
    "/",
    "/health",
    "/static",
    "/api/docs",
    "/api/redoc",
    "/openapi.json",
]


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check API key authentication.
    Can be enabled/disabled via API_KEY_ENABLED environment variable.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip authentication if disabled
        if not API_KEY_ENABLED:
            return await call_next(request)

        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
            return await call_next(request)

        # Verify API key
        api_key = request.headers.get(API_KEY_NAME)
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "message": "API key is missing. Please provide X-API-Key header.",
                },
            )

        if api_key not in VALID_API_KEYS:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "success": False,
                    "message": "Invalid API key.",
                },
            )

        return await call_next(request)


def api_key_middleware(app):
    """Factory function to create API key middleware"""
    return APIKeyMiddleware(app)


def verify_api_key(api_key: str) -> bool:
    """
    Verify if the provided API key is valid.

    Args:
        api_key: The API key to verify

    Returns:
        True if API key is valid, False otherwise
    """
    if not API_KEY_ENABLED:
        return True
    return api_key in VALID_API_KEYS


def get_api_key_from_header(request: Request) -> Optional[str]:
    """
    Extract API key from request header.

    Args:
        request: The incoming request

    Returns:
        The API key if present, None otherwise
    """
    return request.headers.get(API_KEY_NAME)


# FastAPI dependency for route-level authentication
async def require_api_key(request: Request) -> Optional[str]:
    """
    FastAPI dependency to require API key for specific routes.

    Raises:
        HTTPException: If API key is missing or invalid

    Returns:
        The API key if valid
    """
    if not API_KEY_ENABLED:
        return None

    api_key = get_api_key_from_header(request)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing. Please provide X-API-Key header.",
        )

    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    return api_key
