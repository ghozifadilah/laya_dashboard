import hashlib
import json
import os
import secrets
import threading
import time
from typing import Any, Dict, Optional
from fastapi import Header, HTTPException, status
from app.core.logging import logger

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password using PBKDF2 HMAC SHA-256."""
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    ).hex()
    return hashed, salt


class AuthService:
    """Authentication and user management service backed by JSON storage."""

    def __init__(self):
        self.lock = threading.Lock()
        self.sessions: Dict[str, Dict[str, Any]] = {}  # token -> {username, created_at}
        self._ensure_users_file()

    def _ensure_users_file(self):
        """Ensure data directory and users.json exist with default admin user."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with self.lock:
            if not os.path.exists(USERS_FILE):
                hashed, salt = _hash_password("admin123")
                default_data = {
                    "users": {
                        "admin": {
                            "username": "admin",
                            "name": "Administrator",
                            "role": "admin",
                            "password_hash": hashed,
                            "salt": salt,
                            "created_at": time.time(),
                            "updated_at": time.time(),
                        }
                    }
                }
                with open(USERS_FILE, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=2)
                logger.info(f"Initialized default admin user in {USERS_FILE}")

    def _read_users(self) -> Dict[str, Any]:
        """Read users data from JSON."""
        if not os.path.exists(USERS_FILE):
            self._ensure_users_file()
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("users", {})
        except Exception as e:
            logger.error(f"Error reading users file: {e}")
            return {}

    def _save_users(self, users: Dict[str, Any]):
        """Save users dict to JSON."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users}, f, indent=2)

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Validate credentials and return user info with session token."""
        with self.lock:
            users = self._read_users()
            user = users.get(username.strip().lower())
            if not user:
                return None

            salt = user.get("salt", "")
            expected_hash = user.get("password_hash", "")
            hashed, _ = _hash_password(password, salt)

            if secrets.compare_digest(hashed, expected_hash):
                token = secrets.token_hex(32)
                user_info = {
                    "username": user["username"],
                    "name": user.get("name", user["username"]),
                    "role": user.get("role", "user"),
                }
                self.sessions[token] = {
                    "user": user_info,
                    "created_at": time.time(),
                }
                return {"token": token, "user": user_info}
            return None

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Verify old password and change to new password in JSON."""
        if len(new_password) < 4:
            raise ValueError("New password must be at least 4 characters long.")

        with self.lock:
            users = self._read_users()
            uname = username.strip().lower()
            user = users.get(uname)
            if not user:
                raise ValueError("User not found.")

            salt = user.get("salt", "")
            expected_hash = user.get("password_hash", "")
            hashed, _ = _hash_password(old_password, salt)

            if not secrets.compare_digest(hashed, expected_hash):
                raise ValueError("Password lama tidak sesuai.")

            # Create new salt and hash
            new_hashed, new_salt = _hash_password(new_password)
            user["password_hash"] = new_hashed
            user["salt"] = new_salt
            user["updated_at"] = time.time()
            users[uname] = user

            self._save_users(users)
            logger.info(f"Password updated successfully for user '{username}'")
            return True

    def get_user_by_token(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        """Resolve user profile from token."""
        if not token:
            return None
        session = self.sessions.get(token)
        if not session:
            return None
        return session.get("user")

    def logout(self, token: str):
        """Invalidate token session."""
        if token in self.sessions:
            del self.sessions[token]


auth_service = AuthService()


async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Extract current user from Bearer or Token header if provided."""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    return auth_service.get_user_by_token(token)


async def get_current_user_required(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Enforce authentication header."""
    user = await get_current_user_optional(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Silakan login terlebih dahulu.",
        )
    return user
