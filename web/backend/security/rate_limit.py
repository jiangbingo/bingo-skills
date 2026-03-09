"""
Bingo Downloader Web - Rate Limiting
IP-based rate limiting to prevent API abuse
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict
from typing import Dict, Tuple
import time
import os
import asyncio

# Configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))  # requests per minute
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Public paths excluded from rate limiting
PUBLIC_PATHS = [
    "/",
    "/health",
    "/static",
]


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window.
    In production, use Redis or similar for distributed rate limiting.
    """

    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window
        self.clients: Dict[str, list[float]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if the client is allowed to make a request.

        Args:
            client_id: Unique identifier for the client (IP address)

        Returns:
            Tuple of (allowed, retry_after)
            - allowed: True if request is allowed, False otherwise
            - retry_after: Seconds to wait before next request (if not allowed)
        """
        async with self.lock:
            now = time.time()
            client_timestamps = self.clients[client_id]

            # Remove timestamps outside the window
            self.clients[client_id] = [
                ts for ts in client_timestamps if ts > now - self.window
            ]

            # Check if limit is exceeded
            if len(self.clients[client_id]) >= self.requests:
                # Calculate retry_after time
                oldest_timestamp = min(self.clients[client_id])
                retry_after = int(oldest_timestamp + self.window - now) + 1
                return False, retry_after

            # Add current timestamp
            self.clients[client_id].append(now)
            return True, 0

    async def cleanup(self):
        """Clean up old entries to prevent memory leaks"""
        async with self.lock:
            now = time.time()
            for client_id in list(self.clients.keys()):
                self.clients[client_id] = [
                    ts for ts in self.clients[client_id] if ts > now - self.window
                ]
                if not self.clients[client_id]:
                    del self.clients[client_id]


# Global rate limiter instance
rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on all API requests.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting if disabled
        if not RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for public paths
        if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
            return await call_next(request)

        # Get client IP address
        # Try to get real IP from headers (for proxied requests)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        allowed, retry_after = await rate_limiter.is_allowed(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "message": f"Rate limit exceeded. Please wait {retry_after} seconds before making another request.",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                    "X-RateLimit-Window": str(RATE_LIMIT_WINDOW),
                },
            )

        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Window"] = str(RATE_LIMIT_WINDOW)

        return response


def rate_limit_middleware(app):
    """Factory function to create rate limit middleware"""
    return RateLimitMiddleware(app)
