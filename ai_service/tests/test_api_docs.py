import pytest
from fastapi.testclient import TestClient
from ..src.app import app

client = TestClient(app)

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    
    # Verify basic OpenAPI structure
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    assert "components" in schema
    
    # Verify API info
    info = schema["info"]
    assert "title" in info
    assert "version" in info
    assert "description" in info

def test_swagger_ui():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()

def test_redoc():
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "redoc" in response.text.lower()

def test_api_endpoints_documented():
    response = client.get("/openapi.json")
    schema = response.json()
    paths = schema["paths"]
    
    # Verify all endpoints are documented
    required_endpoints = [
        "/health",
        "/process",
        "/analyze",
        "/auth/register",
        "/auth/login",
        "/auth/refresh",
        "/auth/logout",
        "/auth/profile"
    ]
    
    for endpoint in required_endpoints:
        assert endpoint in paths
        assert "post" in paths[endpoint] or "get" in paths[endpoint]

def test_request_schemas():
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Verify request schemas
    components = schema["components"]
    assert "schemas" in components
    
    # Check for required schemas
    required_schemas = [
        "UserCreate",
        "UserLogin",
        "Token",
        "UserProfile",
        "PasswordChange",
        "DocumentProcess",
        "DocumentAnalyze"
    ]
    
    for schema_name in required_schemas:
        assert schema_name in components["schemas"]

def test_response_schemas():
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Verify response schemas
    components = schema["components"]
    assert "schemas" in components
    
    # Check for required response schemas
    required_schemas = [
        "UserResponse",
        "TokenResponse",
        "ProfileResponse",
        "ProcessResponse",
        "AnalyzeResponse",
        "ErrorResponse"
    ]
    
    for schema_name in required_schemas:
        assert schema_name in components["schemas"]

def test_security_schemes():
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Verify security schemes
    components = schema["components"]
    assert "securitySchemes" in components
    
    # Check for required security schemes
    required_schemes = ["BearerAuth"]
    
    for scheme in required_schemes:
        assert scheme in components["securitySchemes"]
        assert components["securitySchemes"][scheme]["type"] == "http"
        assert components["securitySchemes"][scheme]["scheme"] == "bearer"

def test_endpoint_descriptions():
    response = client.get("/openapi.json")
    schema = response.json()
    paths = schema["paths"]
    
    # Verify endpoint descriptions
    for path, methods in paths.items():
        for method, details in methods.items():
            assert "summary" in details
            assert "description" in details
            assert "responses" in details
            
            # Verify response descriptions
            for status_code, response in details["responses"].items():
                assert "description" in response

def test_parameter_descriptions():
    response = client.get("/openapi.json")
    schema = response.json()
    paths = schema["paths"]
    
    # Verify parameter descriptions
    for path, methods in paths.items():
        for method, details in methods.items():
            if "parameters" in details:
                for param in details["parameters"]:
                    assert "description" in param
                    assert "required" in param
                    assert "schema" in param

def test_example_values():
    response = client.get("/openapi.json")
    schema = response.json()
    components = schema["components"]
    
    # Verify example values in schemas
    for schema_name, schema_def in components["schemas"].items():
        if "properties" in schema_def:
            for prop_name, prop_def in schema_def["properties"].items():
                if "example" in prop_def:
                    assert isinstance(prop_def["example"], (str, int, float, bool, dict, list))

def test_error_responses():
    response = client.get("/openapi.json")
    schema = response.json()
    paths = schema["paths"]
    
    # Verify error responses
    for path, methods in paths.items():
        for method, details in methods.items():
            responses = details["responses"]
            assert "400" in responses  # Bad Request
            assert "401" in responses  # Unauthorized
            assert "422" in responses  # Validation Error
            assert "500" in responses  # Server Error 