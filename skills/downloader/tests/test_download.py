#!/usr/bin/env python3
"""
Unit tests for Bingo Downloader Python script.

Run with: pytest tests/test_download.py -v
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from download import BingoDownloader, SmartFormatSelector, DownloadHistory
    from download import detect_platform, is_playlist_url
except ImportError:
    pytest.skip("download.py not available", allow_module_level=True)


class TestPlatformDetection:
    """Test platform detection functionality."""

    def test_detect_youtube(self):
        """Test YouTube URL detection."""
        assert detect_platform("https://www.youtube.com/watch?v=xxx") == "YouTube"
        assert detect_platform("https://youtu.be/xxx") == "YouTube"
        assert detect_platform("https://youtube.com/shorts/xxx") == "YouTube"

    def test_detect_bilibili(self):
        """Test Bilibili URL detection."""
        assert detect_platform("https://www.bilibili.com/video/BV1xx") == "Bilibili"

    def test_detect_twitter(self):
        """Test Twitter/X URL detection."""
        assert detect_platform("https://twitter.com/user/status/123") == "Twitter/X"
        assert detect_platform("https://x.com/user/status/123") == "Twitter/X"

    def test_detect_tiktok(self):
        """Test TikTok/Douyin URL detection."""
        assert detect_platform("https://www.tiktok.com/@user/video/123") == "TikTok/Douyin"
        assert detect_platform("https://www.douyin.com/video/123") == "TikTok/Douyin"

    def test_detect_unknown(self):
        """Test unknown platform detection."""
        assert detect_platform("https://example.com/video/123") == "Unknown"


class TestPlaylistDetection:
    """Test playlist URL detection."""

    def test_youtube_playlist(self):
        """Test YouTube playlist detection."""
        assert is_playlist_url("https://www.youtube.com/playlist?list=xxx")
        assert is_playlist_url("https://www.youtube.com/watch?v=xxx&list=yyy")

    def test_bilibili_playlist(self):
        """Test Bilibili playlist detection."""
        assert is_playlist_url("https://www.bilibili.com/list/xxx")

    def test_single_video(self):
        """Test single video URL (not playlist)."""
        assert not is_playlist_url("https://www.youtube.com/watch?v=xxx")


class TestSmartFormatSelector:
    """Test smart format selection."""

    @pytest.fixture
    def selector(self):
        """Create a SmartFormatSelector instance."""
        return SmartFormatSelector()

    def test_selector_initialization(self, selector):
        """Test selector is initialized properly."""
        assert selector is not None
        assert selector.history_db is not None


class TestDownloadHistory:
    """Test download history management."""

    @pytest.fixture
    def temp_history(self, tmp_path):
        """Create a temporary history database."""
        db_path = tmp_path / ".test-yt-dlp-downloads.json"
        return DownloadHistory(db_path=str(db_path))

    def test_history_initialization(self, temp_history):
        """Test history database initialization."""
        assert temp_history is not None

    def test_record_download(self, temp_history):
        """Test recording a download."""
        temp_history.record_download(
            url="https://www.youtube.com/watch?v=test",
            platform="YouTube",
            title="Test Video",
            quality="1080",
            filesize=1024000,
            success=True,
            download_path="/tmp"
        )

        history = temp_history.get_history(limit=10)
        assert len(history) == 1
        assert history[0]['url'] == "https://www.youtube.com/watch?v=test"
        assert history[0]['platform'] == "YouTube"

    def test_get_stats(self, temp_history):
        """Test getting download statistics."""
        # Record some downloads
        for i in range(5):
            temp_history.record_download(
                url=f"https://www.youtube.com/watch?v=test{i}",
                platform="YouTube",
                title=f"Test Video {i}",
                quality="1080",
                filesize=1024000,
                success=True if i < 4 else False
            )

        stats = temp_history.get_stats()
        assert stats['total'] == 5
        assert stats['successful'] == 4
        assert stats['failed'] == 1


class TestBingoDownloader:
    """Test main BingoDownloader class."""

    @pytest.fixture
    def downloader(self, tmp_path):
        """Create a BingoDownloader instance with temp directory."""
        return BingoDownloader(
            download_path=tmp_path / "downloads",
            audio_only=False,
            quality="1080",
            subtitles=False,
            write_thumbnail=False
        )

    def test_downloader_initialization(self, downloader):
        """Test downloader is initialized properly."""
        assert downloader is not None
        assert downloader.audio_only is False
        assert downloader.quality == "1080"
        assert downloader.subtitles is False

    def test_detect_platform(self, downloader):
        """Test platform detection through downloader."""
        assert downloader.detect_platform("https://www.youtube.com/watch?v=xxx") == "YouTube"
        assert downloader.detect_platform("https://www.bilibili.com/video/BV1xx") == "Bilibili"

    def test_is_playlist(self, downloader):
        """Test playlist detection through downloader."""
        assert downloader.is_playlist("https://www.youtube.com/playlist?list=xxx")
        assert not downloader.is_playlist("https://www.youtube.com/watch?v=xxx")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
