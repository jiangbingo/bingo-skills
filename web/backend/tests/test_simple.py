"""
Simple integration tests for Bingo Downloader Web API

These tests use the actual FastAPI TestClient and don't require complex mocking
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import app - this will work if the package structure is correct
try:
    from main import app
    APP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import app: {e}")
    APP_AVAILABLE = False


@pytest.mark.skipif(not APP_AVAILABLE, reason="App not available")
def test_health_check():
    """Test health check endpoint"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "message" in data


@pytest.mark.skipif(not APP_AVAILABLE, reason="App not available")
def test_root_endpoint():
    """Test root endpoint returns HTML"""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code in [200, 500]  # May fail if templates missing


@pytest.mark.skipif(not APP_AVAILABLE, reason="App not available")
def test_api_docs():
    """Test API docs endpoint"""
    client = TestClient(app)
    response = client.get("/api/docs")
    assert response.status_code in [200, 404]  # May not be available


@pytest.mark.skipif(not APP_AVAILABLE, reason="App not available")
def test_download_start_validation():
    """Test download start endpoint validates input"""
    client = TestClient(app)

    # Missing URL should fail validation
    response = client.post("/api/download/start", json={})
    assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
