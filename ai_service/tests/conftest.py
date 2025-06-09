import pytest
import os
import tempfile
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def sample_w2_file(temp_dir):
    """Create a sample W-2 text file."""
    file_path = temp_dir / "sample_w2.txt"
    content = """
Form W-2 Wage and Tax Statement 2023
Employer's name: ACME Corporation
Employer's EIN: 12-3456789
Employee's SSN: 123-45-6789
Employee's name: John Doe
Employee's address: 123 Main St, Anytown, USA
Wages, tips, other compensation: 50,000.00
Federal income tax withheld: 8,000.00
Social security wages: 50,000.00
Social security tax withheld: 3,100.00
Medicare wages and tips: 50,000.00
Medicare tax withheld: 725.00
State: CA
State income tax: 2,500.00
State wages, tips, etc: 50,000.00
"""
    file_path.write_text(content)
    return file_path

@pytest.fixture
def sample_1099_file(temp_dir):
    """Create a sample 1099-NEC text file."""
    file_path = temp_dir / "sample_1099.txt"
    content = """
Form 1099-NEC Non-Employee Compensation 2023
Payer's name: XYZ Consulting
Payer's TIN: 98-7654321
Payer's address: 456 Business Ave, Anytown, USA
Recipient's name: John Doe
Recipient's TIN: 123-45-6789
Recipient's address: 123 Main St, Anytown, USA
Box 1: 25,000.00
Box 4: 3,750.00
State: CA
State ID number: 1234567
State income: 1,250.00
Box 16: 1,250.00
"""
    file_path.write_text(content)
    return file_path

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("API_KEY", "test_api_key")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG") 