import json
import os
import secrets
import threading
import time
from typing import Any, Dict, List, Optional
from app.core.logging import logger

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
TOKENS_FILE = os.path.join(DATA_DIR, "api_tokens.json")


class ApiKeyService:
    """Service for generating, managing, and validating API tokens stored in JSON."""

    def __init__(self):
        self.lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        """Ensure api_tokens.json exists with default configuration."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with self.lock:
            if not os.path.exists(TOKENS_FILE):
                # Generate initial default master API key
                default_token = "laya_live_" + secrets.token_hex(20)
                initial_data = {
                    "protection_enabled": True,  # API protection enabled by default
                    "keys": {
                        "default_master_key": {
                            "id": "key_master_1",
                            "name": "Default Master Key",
                            "token": default_token,
                            "created_at": time.time(),
                            "is_active": True,
                        }
                    }
                }
                with open(TOKENS_FILE, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, indent=2)
                logger.info(f"Initialized API tokens file with default key in {TOKENS_FILE}")

    def _read_data(self) -> Dict[str, Any]:
        if not os.path.exists(TOKENS_FILE):
            self._ensure_file()
        try:
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading api tokens file: {e}")
            return {"protection_enabled": True, "keys": {}}

    def _save_data(self, data: Dict[str, Any]):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(TOKENS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def is_protection_enabled(self) -> bool:
        """Check if global API protection is enforced."""
        with self.lock:
            return self._read_data().get("protection_enabled", True)

    def toggle_protection(self, enabled: bool) -> bool:
        """Toggle global API token requirement."""
        with self.lock:
            data = self._read_data()
            data["protection_enabled"] = enabled
            self._save_data(data)
            logger.info(f"API Token protection set to: {enabled}")
            return enabled

    def list_keys(self) -> List[Dict[str, Any]]:
        """List all registered API tokens."""
        with self.lock:
            data = self._read_data()
            return list(data.get("keys", {}).values())

    def generate_key(self, name: str) -> Dict[str, Any]:
        """Generate a new secure API token."""
        key_id = "key_" + secrets.token_hex(6)
        token_str = "laya_live_" + secrets.token_hex(20)
        now = time.time()

        key_obj = {
            "id": key_id,
            "name": name.strip() or "Production API Key",
            "token": token_str,
            "created_at": now,
            "is_active": True,
        }

        with self.lock:
            data = self._read_data()
            keys = data.get("keys", {})
            keys[key_id] = key_obj
            data["keys"] = keys
            self._save_data(data)
            logger.info(f"Generated new API token '{key_obj['name']}' (ID: {key_id})")
            return key_obj

    def delete_key(self, key_id: str) -> bool:
        """Revoke / delete an API token."""
        with self.lock:
            data = self._read_data()
            keys = data.get("keys", {})
            # Match by id or token string
            target_id = None
            for kid, kdata in keys.items():
                if kid == key_id or kdata.get("id") == key_id or kdata.get("token") == key_id:
                    target_id = kid
                    break

            if target_id and target_id in keys:
                del keys[target_id]
                data["keys"] = keys
                self._save_data(data)
                logger.info(f"API token '{key_id}' deleted/revoked.")
                return True
            return False

    def validate_token(self, token: Optional[str]) -> bool:
        """Check if a token string is a valid, active API key."""
        if not token:
            return False
        clean_token = token.replace("Bearer ", "").strip()
        with self.lock:
            data = self._read_data()
            for k in data.get("keys", {}).values():
                if k.get("is_active") and secrets.compare_digest(k.get("token", ""), clean_token):
                    return True
            return False


api_key_service = ApiKeyService()
