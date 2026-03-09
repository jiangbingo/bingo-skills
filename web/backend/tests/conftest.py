"""
Test configuration and fixtures for Bingo Downloader Web API tests
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_download_dir():
    """Create a temporary download directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ytdlp():
    """Mock yt-dlp subprocess calls"""
    with patch('subprocess.Popen') as mock_popen:
        mock_process = Mock()
        mock_process.communicate.return_value = (b'[download] Destination: test.mp4\n[download] 100% of 10.00MiB', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def mock_download_history():
    """Mock DownloadHistory class"""
    with patch('api.history.DownloadHistory') as mock_history:
        mock_instance = Mock()
        mock_instance.get_history.return_value = [
            {
                'id': 1,
                'url': 'https://www.youtube.com/watch?v=test',
                'platform': 'YouTube',
                'title': 'Test Video',
                'quality': '1080',
                'filesize': 1024000,
                'timestamp': '2024-01-01 12:00:00',
                'success': True,
                'download_path': '/tmp/test.mp4'
            }
        ]
        mock_instance.get_recent_history.return_value = mock_instance.get_history.return_value
        mock_instance.get_history_by_platform.return_value = mock_instance.get_history.return_value
        mock_instance.get_total_count.return_value = 1
        mock_instance.get_stats.return_value = {
            'total': 10,
            'success': 8,
            'failed': 2,
            'success_rate': '80.0%',
            'total_size': 10240000,
            'by_platform': {
                'YouTube': 5,
                'Bilibili': 3,
                'TikTok': 2
            }
        }
        mock_history.return_value = mock_instance
        yield mock_history


@pytest.fixture
def sample_download_request():
    """Sample download request data"""
    return {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "quality": "1080",
        "format_type": "video",
        "subtitles": False,
        "cookies_browser": "chrome"
    }


@pytest.fixture
def sample_formats_response():
    """Sample formats list response"""
    return {
        "formats": [
            {"id": "137", "ext": "mp4", "height": 1080, "width": 1920},
            {"id": "22", "ext": "mp4", "height": 720, "width": 1280},
            {"id": "18", "ext": "mp4", "height": 360, "width": 640}
        ]
    }
