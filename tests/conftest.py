import os
import pytest
from fastapi.testclient import TestClient

# Configure test environment
os.environ["MOCK_MODE"] = "true"
os.environ["PRELOAD_ON_STARTUP"] = "false"
os.environ["DEVICE"] = "cpu"
os.environ["API_KEY_ENABLED"] = "false"

from app.core.config import settings
settings.MOCK_MODE = True
settings.PRELOAD_ON_STARTUP = False
settings.DEVICE = "cpu"
settings.API_KEY_ENABLED = False

from app.services.auth_service import auth_service, _hash_password
from app.services.api_key_service import api_key_service
from app.main import app


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset users and tokens before each test."""
    hashed, salt = _hash_password("admin123")
    users = {
        "admin": {
            "username": "admin",
            "name": "Administrator",
            "role": "admin",
            "password_hash": hashed,
            "salt": salt,
            "created_at": 0,
            "updated_at": 0,
        }
    }
    auth_service._save_users(users)
    api_key_service.toggle_protection(False)
    settings.API_KEY_ENABLED = False


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
