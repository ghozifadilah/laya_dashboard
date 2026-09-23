from typing import Any, Dict, List, Optional
import laya.presets as lp
from app.services.workflow_storage import workflow_storage


class PresetsCatalog:
    """Catalog of question presets and user-defined decision workflows."""

    def list_presets(self) -> List[Dict[str, Any]]:
        """List all available workflows from storage."""
        return workflow_storage.list_workflows()

    def get_preset_questions(
        self, preset_name: str, custom_categories: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve question schema for a given preset or custom workflow name."""
        name = preset_name.strip().lower()

        # Check workflow storage first
        custom_wf = workflow_storage.get_workflow(name)
        if custom_wf and custom_wf.get("questions"):
            return custom_wf["questions"]

        # Fallback to laya built-in presets
        if name == "triage":
            return lp.triage_questions()
        elif name == "email":
            return lp.email_questions(categories=custom_categories)
        elif name == "guard":
            return lp.guard_questions()
        elif name == "moderation":
            return lp.moderation_questions()
        elif name == "router":
            return lp.router_questions()

        return None


presets_catalog = PresetsCatalog()
