import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_license_data():
    """Sample license table for testing."""
    return {
        "CRBOT-test-1111-2222-333333333333": {
            "client_id": "client_abc",
            "status": "active",
            "expiry_date": "2027-01-01",
            "profile_url": "https://storage.example.com/profiles/client_abc"
        },
        "CRBOT-test-expired-0000-000000000000": {
            "client_id": "client_expired",
            "status": "active",
            "expiry_date": "2020-01-01",
            "profile_url": ""
        },
        "CRBOT-test-inactive-0000-000000000000": {
            "client_id": "client_inactive",
            "status": "inactive",
            "expiry_date": "2027-01-01",
            "profile_url": ""
        }
    }
