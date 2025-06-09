import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from ..src.app import app, get_current_user
from ..src.auth import create_access_token, verify_password, get_password_hash

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

def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "username": TEST_USER["username"],
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USER["username"]
    assert data["email"] == TEST_USER["email"]
    assert "id" in data

def test_login_user():
    response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_protected_endpoint_with_auth(auth_headers, sample_w2_file):
    with open(sample_w2_file, "rb") as f:
        response = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")},
            headers=auth_headers
        )
    assert response.status_code == 200

def test_protected_endpoint_without_auth(sample_w2_file):
    with open(sample_w2_file, "rb") as f:
        response = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")}
        )
    assert response.status_code == 401

def test_invalid_token():
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 401

def test_token_expiration():
    # Create an expired token
    expired_token = create_access_token(
        data={"sub": TEST_USER["username"]},
        expires_delta=timedelta(microseconds=1)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    
    # Wait for token to expire
    import time
    time.sleep(0.1)
    
    response = client.get("/health", headers=headers)
    assert response.status_code == 401

def test_refresh_token(auth_headers):
    response = client.post("/auth/refresh", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_user_profile(auth_headers):
    response = client.get("/auth/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USER["username"]
    assert data["email"] == TEST_USER["email"]

def test_update_user_profile(auth_headers):
    new_email = "newemail@example.com"
    response = client.put(
        "/auth/profile",
        json={"email": new_email},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == new_email

def test_change_password(auth_headers):
    new_password = "newpassword123"
    response = client.put(
        "/auth/change-password",
        json={
            "current_password": TEST_USER["password"],
            "new_password": new_password
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Verify new password works
    login_response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": new_password
        }
    )
    assert login_response.status_code == 200

def test_rate_limiting(auth_headers):
    # Make multiple requests in quick succession
    for _ in range(10):
        response = client.get("/health", headers=auth_headers)
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get("/health", headers=auth_headers)
    assert response.status_code == 429

def test_concurrent_auth_requests():
    import concurrent.futures
    
    def make_request():
        return client.post(
            "/auth/login",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
    
    # Make multiple concurrent login requests
    with concurrent.futures.ThreadPoolExecutor() as executor:
        responses = list(executor.map(lambda _: make_request(), range(5)))
    
    # Verify all requests were handled properly
    assert all(response.status_code == 200 for response in responses)

def test_logout(auth_headers):
    response = client.post("/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify token is no longer valid
    response = client.get("/health", headers=auth_headers)
    assert response.status_code == 401 