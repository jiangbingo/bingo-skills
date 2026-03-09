"""
Bingo Downloader Web - Data Models
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class DownloadRequest(BaseModel):
    """Download request model"""
    url: str = Field(..., description="Video URL to download")
    quality: str = Field(default="1080", description="Video quality (360, 480, 720, 1080, best)")
    format_type: Literal["video", "audio"] = Field(default="video", description="Download type")
    audio_format: Optional[str] = Field(default="mp3", description="Audio format (mp3, wav, m4a, flac, aac)")
    subtitles: bool = Field(default=False, description="Include subtitles")
    sub_langs: Optional[str] = Field(default="en,zh", description="Subtitle languages")
    cookies_browser: Optional[str] = Field(default="chrome", description="Browser for cookies")
    download_path: Optional[str] = Field(default=None, description="Custom download path")


class FormatInfo(BaseModel):
    """Video format information"""
    format_id: str
    ext: str
    quality: str
    filesize: Optional[int] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    fps: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None


class FormatListResponse(BaseModel):
    """Response for format list"""
    url: str
    platform: str
    title: str
    formats: list[FormatInfo]
    thumbnail: Optional[str] = None


class DownloadProgress(BaseModel):
    """Download progress update"""
    task_id: str
    status: Literal["pending", "downloading", "processing", "completed", "failed"]
    progress: float = 0.0  # 0-100
    downloaded_bytes: int = 0
    total_bytes: Optional[int] = None
    speed: Optional[str] = None
    eta: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None


class DownloadHistory(BaseModel):
    """Download history record"""
    id: int
    url: str
    platform: str
    title: str
    quality: str
    filesize: int
    success: bool
    timestamp: datetime
    download_path: str


class HistoryResponse(BaseModel):
    """Response for download history"""
    total: int
    records: list[DownloadHistory]


class StatsResponse(BaseModel):
    """Response for statistics"""
    total_downloads: int
    successful_downloads: int
    failed_downloads: int
    success_rate: float
    total_bytes: int
    total_size_human: str
    by_platform: dict[str, int]


class ApiResponse(BaseModel):
    """Generic API response"""
    success: bool
    message: str
    data: Optional[dict] = None
