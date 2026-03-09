"""
Bingo Downloader Web - Formats API Endpoints
"""
from fastapi import APIRouter, Query, HTTPException
from ..models import FormatListResponse, ApiResponse
from ..config import detect_platform

router = APIRouter(prefix="/api/formats", tags=["formats"])


@router.get("/list", response_model=FormatListResponse)
async def list_formats(
    url: str = Query(..., description="Video URL"),
    cookies_browser: str = Query(default="chrome", description="Browser for cookies")
):
    """List available formats for a video"""
    try:
        import yt_dlp

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        if cookies_browser:
            # Use cookies from browser if needed
            pass

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            raise HTTPException(status_code=400, detail="Could not extract video info")

        # Extract format information
        formats = []
        for fmt in info.get('formats', []):
            if fmt.get('vcodec') != 'none':  # Only video formats
                formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'quality': f"{fmt.get('height', 0)}p",
                    'filesize': fmt.get('filesize'),
                    'vcodec': fmt.get('vcodec'),
                    'acodec': fmt.get('acodec'),
                    'fps': fmt.get('fps'),
                    'height': fmt.get('height'),
                    'width': fmt.get('width'),
                })

        return FormatListResponse(
            url=url,
            platform=detect_platform(url),
            title=info.get('title', 'Unknown'),
            formats=formats,
            thumbnail=info.get('thumbnail')
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
