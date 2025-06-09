import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from ..src.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_process_document_text(sample_w2_file):
    with open(sample_w2_file, "rb") as f:
        response = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["type"] == "text"
    assert len(result["text"]) > 0

def test_process_document_invalid_file(temp_dir):
    # Create an invalid file
    invalid_file = temp_dir / "invalid.txt"
    invalid_file.write_text("Invalid content")
    
    with open(invalid_file, "rb") as f:
        response = client.post(
            "/process",
            files={"file": ("invalid.txt", f, "text/plain")}
        )
    
    assert response.status_code == 400
    result = response.json()
    assert result["success"] is False
    assert "error" in result

def test_analyze_document(sample_w2_file):
    # First process the document
    with open(sample_w2_file, "rb") as f:
        process_response = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")}
        )
    
    assert process_response.status_code == 200
    process_result = process_response.json()
    
    # Then analyze it
    analyze_response = client.post(
        "/analyze",
        json={
            "doc_type": "w2",
            "text": process_result["text"]
        }
    )
    
    assert analyze_response.status_code == 200
    result = analyze_response.json()
    assert result["success"] is True
    assert result["type"] == "w2"
    
    # Verify extracted data
    data = result["data"]
    assert data["employer_name"] == "ACME Corporation"
    assert data["employer_ein"] == "12-3456789"
    assert data["employee_ssn"] == "123-45-6789"
    assert data["wages"] == "50,000.00"
    assert data["federal_tax_withheld"] == "8,000.00"
    
    # Verify totals
    totals = result["totals"]
    assert totals["total_wages"] == 50000.0
    assert totals["total_taxes_withheld"] == 14325.0

def test_analyze_document_invalid_type(sample_w2_file):
    # First process the document
    with open(sample_w2_file, "rb") as f:
        process_response = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")}
        )
    
    assert process_response.status_code == 200
    process_result = process_response.json()
    
    # Try to analyze with invalid type
    analyze_response = client.post(
        "/analyze",
        json={
            "doc_type": "invalid_type",
            "text": process_result["text"]
        }
    )
    
    assert analyze_response.status_code == 400
    result = analyze_response.json()
    assert result["success"] is False
    assert "error" in result

def test_analyze_document_missing_text():
    analyze_response = client.post(
        "/analyze",
        json={
            "doc_type": "w2",
            "text": ""
        }
    )
    
    assert analyze_response.status_code == 400
    result = analyze_response.json()
    assert result["success"] is False
    assert "error" in result

def test_process_multiple_documents(sample_w2_file, sample_1099_file):
    # Process W-2
    with open(sample_w2_file, "rb") as f:
        w2_response = client.post(
            "/process",
            files={"file": ("sample_w2.txt", f, "text/plain")}
        )
    
    assert w2_response.status_code == 200
    w2_result = w2_response.json()
    
    # Process 1099
    with open(sample_1099_file, "rb") as f:
        form1099_response = client.post(
            "/process",
            files={"file": ("sample_1099.txt", f, "text/plain")}
        )
    
    assert form1099_response.status_code == 200
    form1099_result = form1099_response.json()
    
    # Analyze both documents
    w2_analysis = client.post(
        "/analyze",
        json={
            "doc_type": "w2",
            "text": w2_result["text"]
        }
    ).json()
    
    form1099_analysis = client.post(
        "/analyze",
        json={
            "doc_type": "1099",
            "text": form1099_result["text"]
        }
    ).json()
    
    # Verify both analyses were successful
    assert w2_analysis["success"] is True
    assert w2_analysis["type"] == "w2"
    
    assert form1099_analysis["success"] is True
    assert form1099_analysis["type"] == "1099"
    
    # Verify data was extracted correctly
    w2_data = w2_analysis["data"]
    assert w2_data["employer_name"] == "ACME Corporation"
    assert w2_data["wages"] == "50,000.00"
    
    form1099_data = form1099_analysis["data"]
    assert form1099_data["payer_name"] == "XYZ Consulting"
    assert form1099_data["nonemployee_compensation"] == "25,000.00" 