import json
import os
import threading
import time
from typing import Any, Dict, List, Optional, Union
from app.core.logging import logger

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
WORKFLOWS_FILE = os.path.join(DATA_DIR, "custom_workflows.json")


class WorkflowStorage:
    """Storage service for custom user projects and decision workflows in JSON."""

    def __init__(self):
        self.lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        """Ensure custom_workflows.json exists."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with self.lock:
            if not os.path.exists(WORKFLOWS_FILE):
                with open(WORKFLOWS_FILE, "w", encoding="utf-8") as f:
                    json.dump({"workflows": {}}, f, indent=2)

    def _read_all(self) -> Dict[str, Any]:
        if not os.path.exists(WORKFLOWS_FILE):
            self._ensure_file()
        try:
            with open(WORKFLOWS_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("workflows", {})
        except Exception as e:
            logger.error(f"Error reading workflows file: {e}")
            return {}

    def _write_all(self, workflows: Dict[str, Any]):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(WORKFLOWS_FILE, "w", encoding="utf-8") as f:
            json.dump({"workflows": workflows}, f, indent=2)

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all saved custom workflows."""
        with self.lock:
            data = self._read_all()
            return list(data.values())

    def get_workflow(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow by name."""
        with self.lock:
            data = self._read_all()
            return data.get(name.strip().lower())

    def save_workflow(
        self,
        name: str,
        title: str,
        description: str,
        questions: Dict[str, Any],
        example_state: Union[str, Dict[str, Any], List[Any]],
        model: Optional[str] = None,
        created_by: Optional[str] = "admin",
    ) -> Dict[str, Any]:
        """Create or update a custom workflow."""
        key = name.strip().lower().replace(" ", "_")
        now = time.time()

        with self.lock:
            data = self._read_all()
            existing = data.get(key, {})
            created_at = existing.get("created_at", now)

            workflow_obj = {
                "name": key,
                "title": title.strip(),
                "description": description.strip(),
                "questions": questions,
                "example_state": example_state,
                "model": model or "auto",
                "created_by": created_by or "admin",
                "created_at": created_at,
                "updated_at": now,
                "is_custom": True,
            }

            data[key] = workflow_obj
            self._write_all(data)
            logger.info(f"Custom workflow '{key}' saved successfully.")
            return workflow_obj

    def delete_workflow(self, name: str) -> bool:
        """Delete custom workflow."""
        key = name.strip().lower()
        with self.lock:
            data = self._read_all()
            if key in data:
                del data[key]
                self._write_all(data)
                logger.info(f"Custom workflow '{key}' deleted.")
                return True
            return False


workflow_storage = WorkflowStorage()
