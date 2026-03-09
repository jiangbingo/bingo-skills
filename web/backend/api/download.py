"""
Bingo Downloader Web - Download API Endpoints
"""
import asyncio
import uuid
import subprocess
from pathlib import Path
from typing import Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models import DownloadRequest, DownloadProgress, ApiResponse

router = APIRouter(prefix="/api/download", tags=["download"])

# In-memory task storage (in production, use Redis or similar)
active_tasks: Dict[str, DownloadProgress] = {}
task_locks: Dict[str, asyncio.Lock] = {}

# Cookies cache directory
COOKIES_CACHE_DIR = Path.home() / '.bingo-downloader' / 'cookies'
COOKIES_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Cookie encryption
try:
    from ..security.encryption import (
        encrypt_data, decrypt_data, get_encryption_status,
        is_encrypted_file, COOKIE_EXPIRATION_HOURS
    )
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    COOKIE_EXPIRATION_HOURS = 24  # Default fallback


def get_cookies_path(browser: str) -> Path:
    """Get cached cookies file path for a browser"""
    return COOKIES_CACHE_DIR / f"{browser}_cookies.txt"


def are_cookies_cached(browser: str) -> bool:
    """Check if cookies are already cached for a browser"""
    cookies_file = get_cookies_path(browser)
    if cookies_file.exists():
        import time
        age = time.time() - cookies_file.stat().st_mtime
        # Use configurable expiration (default 24 hours if encryption enabled, 7 days otherwise)
        expiration_hours = COOKIE_EXPIRATION_HOURS if ENCRYPTION_AVAILABLE else 7 * 24
        return age < expiration_hours * 3600
    return False


async def ensure_cookies(browser: str = "chrome") -> str:
    """Ensure cookies are available, return path to use"""
    cache_path = get_cookies_path(browser)

    if are_cookies_cached(browser):
        # If encrypted, decrypt to temporary file for use
        if ENCRYPTION_AVAILABLE and is_encrypted_file(cache_path):
            try:
                with open(cache_path, "r") as f:
                    encrypted_data = f.read()
                decrypted_data = decrypt_data(encrypted_data)

                # Write to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
                    tmp.write(decrypted_data)
                    tmp_path = tmp.name
                return tmp_path
            except Exception as e:
                print(f"Warning: Could not decrypt cookies: {e}")
                return browser
        return str(cache_path)

    # Extract and cache cookies
    test_url = "https://www.youtube.com/"
    try:
        # Use yt-dlp to dump cookies to file
        cmd = [
            "yt-dlp",
            "--cookies-from-browser", browser,
            "--print", "cookies",
            "--cookies", str(cache_path),
            test_url
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        if cache_path.exists():
            # Encrypt cookies if encryption is available
            if ENCRYPTION_AVAILABLE:
                try:
                    with open(cache_path, "r") as f:
                        cookies_data = f.read()
                    encrypted_data = encrypt_data(cookies_data)
                    with open(cache_path, "w") as f:
                        f.write(encrypted_data)
                    print(f"Warning: Cookies encrypted and stored at {cache_path}")
                    print(f"Warning: Cookies expire after {COOKIE_EXPIRATION_HOURS} hours")
                except Exception as e:
                    print(f"Warning: Could not encrypt cookies: {e}")
            return str(cache_path)
    except Exception as e:
        print(f"Warning: Could not cache cookies: {e}")

    # Fallback to browser name
    return browser


async def run_download(task_id: str, request: DownloadRequest):
    """Run download in background"""
    try:
        from ..core import BingoDownloader, CORE_AVAILABLE

        if not CORE_AVAILABLE:
            active_tasks[task_id].status = "failed"
            active_tasks[task_id].error = "Core modules not available"
            return

        # Update status to downloading
        active_tasks[task_id].status = "downloading"
        active_tasks[task_id].progress = 0.0

        # Map quality string to int (best = None, 1080 = 1080, etc.)
        quality_val = None if request.quality == "best" else int(request.quality)

        # Check for cached cookies
        cookies_file = None
        cookies_browser = request.cookies_browser

        if request.cookies_browser and are_cookies_cached(request.cookies_browser):
            cookies_file = str(get_cookies_path(request.cookies_browser))
            cookies_browser = None  # Use file instead of browser
        elif request.cookies_browser:
            # First time using this browser - will trigger keychain prompt
            cookies_browser = request.cookies_browser

        # Create downloader instance with config
        downloader = BingoDownloader(
            audio_only=(request.format_type == "audio"),
            quality=quality_val,
            subtitles=request.subtitles,
            cookies_browser=cookies_browser,
            cookies_file=cookies_file
        )

        # Run download
        result = await asyncio.to_thread(
            downloader.download,
            request.url
        )

        if result.get("success"):
            active_tasks[task_id].status = "completed"
            active_tasks[task_id].progress = 100.0
            active_tasks[task_id].filename = result.get("filename")
        else:
            active_tasks[task_id].status = "failed"
            active_tasks[task_id].error = result.get("error", "Unknown error")

    except Exception as e:
        active_tasks[task_id].status = "failed"
        active_tasks[task_id].error = str(e)


@router.post("/start", response_model=ApiResponse)
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start a new download task"""
    task_id = str(uuid.uuid4())

    # Initialize task
    active_tasks[task_id] = DownloadProgress(
        task_id=task_id,
        status="pending",
        progress=0.0
    )

    # Start download in background
    background_tasks.add_task(run_download, task_id, request)

    return ApiResponse(
        success=True,
        message="Download started",
        data={"task_id": task_id}
    )


@router.get("/progress/{task_id}", response_model=DownloadProgress)
async def get_progress(task_id: str):
    """Get download progress"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return active_tasks[task_id]


@router.post("/cancel/{task_id}", response_model=ApiResponse)
async def cancel_download(task_id: str):
    """Cancel a download task"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    # Mark as cancelled (actual cancellation will be implemented)
    active_tasks[task_id].status = "failed"
    active_tasks[task_id].error = "Cancelled by user"

    return ApiResponse(
        success=True,
        message="Download cancelled"
    )


@router.get("/tasks", response_model=Dict[str, DownloadProgress])
async def list_tasks():
    """List all active tasks"""
    return active_tasks


@router.post("/authorize-cookies", response_model=ApiResponse)
async def authorize_cookies(browser: str = "chrome"):
    """
    Authorize and cache cookies from browser.
    This will trigger the macOS keychain prompt.
    After successful authorization, cookies will be cached.
    """
    try:
        cache_path = await ensure_cookies(browser)

        if are_cookies_cached(browser):
            hours = COOKIE_EXPIRATION_HOURS if ENCRYPTION_AVAILABLE else 7 * 24
            message = f"Cookies from {browser}已缓存{hours}小时，之后不需要再次授权"
            if ENCRYPTION_AVAILABLE:
                message += " (已加密存储)"
            return ApiResponse(
                success=True,
                message=message
            )
        else:
            return ApiResponse(
                success=False,
                message=f"无法缓存 cookies，请确保已安装 yt-dlp 并选择 {browser}"
            )
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"授权失败: {str(e)}"
        )


@router.get("/encryption-status", response_model=Dict)
async def get_encryption_status_info():
    """Get encryption status and configuration"""
    if ENCRYPTION_AVAILABLE:
        status = get_encryption_status()
        # Remove verbose warning from API response
        status.pop("warning", None)
        return status
    else:
        return {
            "encryption_enabled": False,
            "message": "cryptography module not installed. Install with: pip install cryptography"
        }


@router.get("/cookies-status", response_model=Dict)
async def get_cookies_status():
    """Check cookies cache status for all browsers"""
    browsers = ["chrome", "firefox", "safari", "edge"]
    status = {}

    for browser in browsers:
        cache_path = get_cookies_path(browser)
        if cache_path.exists():
            import time
            age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
            status[browser] = {
                "cached": True,
                "age_hours": round(age_hours, 1)
            }
        else:
            status[browser] = {
                "cached": False,
                "age_hours": None
            }

    return status
