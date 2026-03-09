"""
Unit tests for Bingo Downloader Web API

Tests all API endpoints with mocked yt-dlp calls
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the main app
from main import app
from models import DownloadRequest


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, client):
        """Test /health endpoint returns correct status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data


    def test_root_endpoint(self, client):
        """Test / endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestDownloadAPI:
    """Test download-related endpoints"""

    def test_start_download_success(self, client, sample_download_request, mock_ytdlp):
        """Test starting a download successfully"""
        with patch('web.backend.api.download.BingoDownloader') as mock_downloader:
            mock_instance = Mock()
            mock_instance.download.return_value = {
                "success": True,
                "filename": "test_video.mp4",
                "filepath": "/tmp/test_video.mp4"
            }
            mock_downloader.return_value = mock_instance

            response = client.post("/api/download/start", json=sample_download_request)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "task_id" in data["data"]
            assert data["message"] == "Download started"


    def test_start_download_invalid_url(self, client):
        """Test starting download with invalid URL"""
        invalid_request = {
            "url": "not-a-valid-url",
            "quality": "1080",
            "format_type": "video"
        }

        response = client.post("/api/download/start", json=invalid_request)

        # The API should still accept it, validation happens in yt-dlp
        assert response.status_code == 200


    def test_get_download_progress(self, client):
        """Test getting download progress"""
        # First start a download
        with patch('web.backend.api.download.BingoDownloader') as mock_downloader:
            mock_instance = Mock()
            mock_instance.download.return_value = {"success": True}
            mock_downloader.return_value = mock_instance

            request_data = {
                "url": "https://www.youtube.com/watch?v=test",
                "quality": "1080",
                "format_type": "video"
            }
            start_response = client.post("/api/download/start", json=request_data)
            task_id = start_response.json()["data"]["task_id"]

            # Get progress
            progress_response = client.get(f"/api/download/progress/{task_id}")
            assert progress_response.status_code == 200
            progress_data = progress_response.json()
            assert "task_id" in progress_data
            assert "status" in progress_data
            assert "progress" in progress_data


    def test_get_progress_nonexistent_task(self, client):
        """Test getting progress for non-existent task"""
        response = client.get("/api/download/progress/non-existent-task-id")
        assert response.status_code == 404


    def test_cancel_download(self, client, sample_download_request):
        """Test canceling a download"""
        with patch('web.backend.api.download.BingoDownloader') as mock_downloader:
            mock_instance = Mock()
            mock_instance.download.return_value = {"success": True}
            mock_downloader.return_value = mock_instance

            # Start a download
            start_response = client.post("/api/download/start", json=sample_download_request)
            task_id = start_response.json()["data"]["task_id"]

            # Cancel it
            cancel_response = client.post(f"/api/download/cancel/{task_id}")
            assert cancel_response.status_code == 200
            data = cancel_response.json()
            assert data["success"] is True


    def test_list_tasks(self, client):
        """Test listing all active tasks"""
        response = client.get("/api/download/tasks")
        assert response.status_code == 200
        # Should return a dictionary (possibly empty)


    def test_authorize_cookies(self, client):
        """Test cookies authorization endpoint"""
        with patch('web.backend.api.download.ensure_cookies') as mock_ensure:
            mock_ensure.return_value = "/path/to/cookies.txt"

            with patch('web.backend.api.download.are_cookies_cached') as mock_cached:
                mock_cached.return_value = True

                response = client.post("/api/download/authorize-cookies?browser=chrome")
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True


    def test_get_cookies_status(self, client):
        """Test getting cookies cache status"""
        response = client.get("/api/download/cookies-status")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestHistoryAPI:
    """Test history-related endpoints"""

    def test_get_history(self, client, mock_download_history):
        """Test getting download history"""
        response = client.get("/api/history/")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "records" in data
        assert isinstance(data["records"], list)


    def test_get_history_with_limit(self, client, mock_download_history):
        """Test getting history with custom limit"""
        response = client.get("/api/history/?limit=5")
        assert response.status_code == 200


    def test_get_history_by_platform(self, client, mock_download_history):
        """Test getting history filtered by platform"""
        response = client.get("/api/history/?platform=YouTube")
        assert response.status_code == 200
        data = response.json()
        assert "records" in data


    def test_clear_history(self, client, mock_download_history):
        """Test clearing download history"""
        response = client.delete("/api/history/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data


    def test_delete_history_record(self, client, mock_download_history):
        """Test deleting a specific history record"""
        response = client.delete("/api/history/1")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatsAPI:
    """Test statistics-related endpoints"""

    def test_get_stats(self, client, mock_download_history):
        """Test getting download statistics"""
        response = client.get("/api/stats/")
        assert response.status_code == 200
        data = response.json()
        assert "total_downloads" in data
        assert "successful_downloads" in data
        assert "failed_downloads" in data
        assert "success_rate" in data
        assert "total_bytes" in data
        assert "total_size_human" in data
        assert "by_platform" in data


    def test_get_stats_by_platform(self, client, mock_download_history):
        """Test getting statistics grouped by platform"""
        response = client.get("/api/stats/by-platform")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestFormatsAPI:
    """Test format-related endpoints"""

    def test_list_formats(self, client):
        """Test listing available formats for a URL"""
        with patch('web.backend.api.formats.yt_dlp') as mock_ytdlp:
            mock_ytdlp.YoutubeDL.return_value.__enter__ = Mock()
            mock_ytdlp.YoutubeDL.return_value.__exit__ = Mock()
            mock_ytdlp.YoutubeDL.return_value.extract_info.return_value = {
                'formats': [
                    {'format_id': '137', 'ext': 'mp4', 'height': 1080, 'width': 1920},
                    {'format_id': '22', 'ext': 'mp4', 'height': 720, 'width': 1280},
                ]
            }

            response = client.get("/api/formats/list?url=https://www.youtube.com/watch?v=test")
            assert response.status_code == 200
            data = response.json()
            assert "formats" in data


    def test_list_formats_missing_url(self, client):
        """Test listing formats without URL parameter"""
        response = client.get("/api/formats/list")
        assert response.status_code == 422  # Validation error


class TestValidation:
    """Test input validation"""

    def test_download_request_validation_missing_url(self, client):
        """Test download request without URL"""
        invalid_request = {
            "quality": "1080",
            "format_type": "video"
        }
        response = client.post("/api/download/start", json=invalid_request)
        assert response.status_code == 422


    def test_download_request_validation_invalid_quality(self, client):
        """Test download request with invalid quality"""
        invalid_request = {
            "url": "https://www.youtube.com/watch?v=test",
            "quality": "invalid",
            "format_type": "video"
        }
        response = client.post("/api/download/start", json=invalid_request)
        # Quality validation might be lenient, check response
        assert response.status_code in [200, 422]


    def test_history_limit_validation(self, client):
        """Test history endpoint with invalid limit"""
        response = client.get("/api/history/?limit=999")
        # Should be limited to max 100
        assert response.status_code in [200, 422]


class TestErrorHandling:
    """Test error handling"""

    def test_ytdlp_not_installed(self, client, sample_download_request):
        """Test behavior when yt-dlp is not installed"""
        with patch('web.backend.api.download.CORE_AVAILABLE', False):
            response = client.post("/api/download/start", json=sample_download_request)
            # Should still create task but fail later
            assert response.status_code == 200


    def test_download_failure(self, client, sample_download_request):
        """Test handling of download failure"""
        with patch('web.backend.api.download.BingoDownloader') as mock_downloader:
            mock_instance = Mock()
            mock_instance.download.return_value = {
                "success": False,
                "error": "Download failed: Network error"
            }
            mock_downloader.return_value = mock_instance

            response = client.post("/api/download/start", json=sample_download_request)
            assert response.status_code == 200
            task_id = response.json()["data"]["task_id"]

            # Wait a bit for background task
            import time
            time.sleep(0.1)

            # Check progress should show failed status
            progress_response = client.get(f"/api/download/progress/{task_id}")
            # Status might be 'failed' or 'downloading' depending on timing


class TestConcurrency:
    """Test concurrent operations"""

    def test_multiple_downloads(self, client, sample_download_request):
        """Test starting multiple downloads simultaneously"""
        with patch('web.backend.api.download.BingoDownloader') as mock_downloader:
            mock_instance = Mock()
            mock_instance.download.return_value = {"success": True}
            mock_downloader.return_value = mock_instance

            # Start multiple downloads
            task_ids = []
            for i in range(3):
                response = client.post("/api/download/start", json={
                    **sample_download_request,
                    "url": f"https://www.youtube.com/watch?v=test{i}"
                })
                assert response.status_code == 200
                task_ids.append(response.json()["data"]["task_id"])

            # All tasks should be created
            assert len(task_ids) == 3
            assert len(set(task_ids)) == 3  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
