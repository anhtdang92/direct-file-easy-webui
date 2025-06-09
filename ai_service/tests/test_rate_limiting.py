import pytest
import time
from fastapi.testclient import TestClient
from ..src.app import app
from ..src.auth import create_access_token

client = TestClient(app)

# Test user data
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    access_token = create_access_token(data={"sub": TEST_USER["username"]})
    return {"Authorization": f"Bearer {access_token}"}

def test_rate_limit_health_check():
    # Make multiple requests in quick succession
    for _ in range(10):
        response = client.get("/health")
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get("/health")
    assert response.status_code == 429
    assert "Too Many Requests" in response.json()["detail"]

def test_rate_limit_process_endpoint(auth_headers, sample_w2_file):
    # Make multiple requests in quick succession
    for _ in range(5):
        with open(sample_w2_file, "rb") as f:
            response = client.post(
                "/process",
                files={"file": ("sample_w2.txt", f, "text/plain")},
                headers=auth_headers
            )
        assert response.status_code == 200
    
    # Next request should be rate limited
    with open(sample_w2_file, "rb") as f:
        response = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")},
            headers=auth_headers
        )
    assert response.status_code == 429

def test_rate_limit_analyze_endpoint(auth_headers, sample_w2_file):
    # First process the document
    with open(sample_w2_file, "rb") as f:
        process_response = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")},
            headers=auth_headers
        )
    assert process_response.status_code == 200
    process_result = process_response.json()
    
    # Make multiple analyze requests in quick succession
    for _ in range(5):
        response = client.post(
            "/analyze",
            json={
                "doc_type": "w2",
                "text": process_result["text"]
            },
            headers=auth_headers
        )
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.post(
        "/analyze",
        json={
            "doc_type": "w2",
            "text": process_result["text"]
        },
        headers=auth_headers
    )
    assert response.status_code == 429

def test_rate_limit_reset():
    # Make requests until rate limited
    for _ in range(10):
        response = client.get("/health")
        assert response.status_code == 200
    
    response = client.get("/health")
    assert response.status_code == 429
    
    # Wait for rate limit to reset
    time.sleep(60)  # Assuming 60-second window
    
    # Should work again
    response = client.get("/health")
    assert response.status_code == 200

def test_different_rate_limits():
    # Test different rate limits for different endpoints
    endpoints = [
        ("/health", 10),  # 10 requests per minute
        ("/process", 5),  # 5 requests per minute
        ("/analyze", 5)   # 5 requests per minute
    ]
    
    for endpoint, limit in endpoints:
        # Make requests until rate limited
        for _ in range(limit):
            response = client.get(endpoint)
            assert response.status_code == 200
        
        # Next request should be rate limited
        response = client.get(endpoint)
        assert response.status_code == 429

def test_rate_limit_headers():
    # Make requests and check rate limit headers
    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        
        # Verify remaining requests decrease
        remaining = int(response.headers["X-RateLimit-Remaining"])
        assert remaining >= 0

def test_rate_limit_by_ip():
    # Test rate limiting by IP address
    headers = {"X-Forwarded-For": "192.168.1.1"}
    
    # Make requests from same IP
    for _ in range(10):
        response = client.get("/health", headers=headers)
        assert response.status_code == 200
    
    response = client.get("/health", headers=headers)
    assert response.status_code == 429
    
    # Try from different IP
    headers = {"X-Forwarded-For": "192.168.1.2"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200

def test_rate_limit_by_user(auth_headers):
    # Test rate limiting by authenticated user
    for _ in range(5):
        response = client.get("/health", headers=auth_headers)
        assert response.status_code == 200
    
    response = client.get("/health", headers=auth_headers)
    assert response.status_code == 429
    
    # Try with different user
    other_headers = {"Authorization": f"Bearer {create_access_token(data={'sub': 'otheruser'})}"}
    response = client.get("/health", headers=other_headers)
    assert response.status_code == 200

def test_rate_limit_error_response():
    # Make requests until rate limited
    for _ in range(10):
        response = client.get("/health")
        assert response.status_code == 200
    
    response = client.get("/health")
    assert response.status_code == 429
    error = response.json()
    assert "detail" in error
    assert "retry_after" in error
    assert isinstance(error["retry_after"], int)
    assert error["retry_after"] > 0 