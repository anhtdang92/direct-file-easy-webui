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

def test_health_check_caching():
    # First request
    response1 = client.get("/health")
    assert response1.status_code == 200
    assert "Cache-Control" in response1.headers
    assert "max-age" in response1.headers["Cache-Control"]
    
    # Second request should be cached
    response2 = client.get("/health")
    assert response2.status_code == 200
    assert response2.headers.get("X-Cache") == "HIT"

def test_process_endpoint_caching(auth_headers, sample_w2_file):
    # First request
    with open(sample_w2_file, "rb") as f:
        response1 = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")},
            headers=auth_headers
        )
    assert response1.status_code == 200
    assert "Cache-Control" in response1.headers
    
    # Second request with same file should be cached
    with open(sample_w2_file, "rb") as f:
        response2 = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")},
            headers=auth_headers
        )
    assert response2.status_code == 200
    assert response2.headers.get("X-Cache") == "HIT"

def test_analyze_endpoint_caching(auth_headers, sample_w2_file):
    # First process the document
    with open(sample_w2_file, "rb") as f:
        process_response = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")},
            headers=auth_headers
        )
    assert process_response.status_code == 200
    process_result = process_response.json()
    
    # First analyze request
    response1 = client.post(
        "/analyze",
        json={
            "doc_type": "w2",
            "text": process_result["text"]
        },
        headers=auth_headers
    )
    assert response1.status_code == 200
    assert "Cache-Control" in response1.headers
    
    # Second analyze request should be cached
    response2 = client.post(
        "/analyze",
        json={
            "doc_type": "w2",
            "text": process_result["text"]
        },
        headers=auth_headers
    )
    assert response2.status_code == 200
    assert response2.headers.get("X-Cache") == "HIT"

def test_cache_expiration():
    # First request
    response1 = client.get("/health")
    assert response1.status_code == 200
    
    # Wait for cache to expire
    time.sleep(60)  # Assuming 60-second cache
    
    # Second request should miss cache
    response2 = client.get("/health")
    assert response2.status_code == 200
    assert response2.headers.get("X-Cache") == "MISS"

def test_cache_invalidation():
    # First request
    response1 = client.get("/health")
    assert response1.status_code == 200
    
    # Invalidate cache
    response = client.post("/cache/invalidate", json={"path": "/health"})
    assert response.status_code == 200
    
    # Second request should miss cache
    response2 = client.get("/health")
    assert response2.status_code == 200
    assert response2.headers.get("X-Cache") == "MISS"

def test_cache_by_user(auth_headers):
    # First request for user 1
    response1 = client.get("/health", headers=auth_headers)
    assert response1.status_code == 200
    
    # Request for user 2 should miss cache
    other_headers = {"Authorization": f"Bearer {create_access_token(data={'sub': 'otheruser'})}"}
    response2 = client.get("/health", headers=other_headers)
    assert response2.status_code == 200
    assert response2.headers.get("X-Cache") == "MISS"

def test_cache_headers():
    response = client.get("/health")
    assert response.status_code == 200
    
    # Verify cache headers
    assert "Cache-Control" in response.headers
    assert "ETag" in response.headers
    assert "Last-Modified" in response.headers

def test_conditional_requests():
    # First request
    response1 = client.get("/health")
    assert response1.status_code == 200
    etag = response1.headers["ETag"]
    last_modified = response1.headers["Last-Modified"]
    
    # Request with If-None-Match
    response2 = client.get("/health", headers={"If-None-Match": etag})
    assert response2.status_code == 304
    
    # Request with If-Modified-Since
    response3 = client.get("/health", headers={"If-Modified-Since": last_modified})
    assert response3.status_code == 304

def test_cache_size_limit():
    # Make multiple requests with different parameters
    for i in range(100):
        response = client.get(f"/health?param={i}")
        assert response.status_code == 200
    
    # Verify cache size hasn't exceeded limit
    response = client.get("/cache/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["size"] <= 1000  # Assuming 1000 item limit

def test_cache_compression():
    # Request with Accept-Encoding
    response = client.get("/health", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers.get("Content-Encoding") == "gzip"
    
    # Verify cached response is also compressed
    response2 = client.get("/health", headers={"Accept-Encoding": "gzip"})
    assert response2.status_code == 200
    assert response2.headers.get("Content-Encoding") == "gzip"
    assert response2.headers.get("X-Cache") == "HIT" 