import time
from typing import Any, Dict, List, Optional, Union
import laya
from app.core.logging import logger


class ShortlistService:
    """Service for handling decisions over large option spaces (e.g. 50-500+ categories)."""

    def filter_candidates_lexical(
        self, state_text: str, criteria: Union[Dict[str, Optional[str]], List[str]], k: int = 20
    ) -> List[str]:
        """Fast BM25 / token-overlap shortlisting for candidates when embeddings are not active."""
        tokens = set(state_text.lower().split())
        scored: List[tuple[str, float]] = []

        if isinstance(criteria, dict):
            items = criteria.items()
        else:
            items = [(c, None) for c in criteria]

        for name, desc in items:
            name_str = str(name)
            desc_str = str(desc or "")
            target_tokens = set(name_str.lower().replace("_", " ").split() + desc_str.lower().split())

            # Exact match bonus
            exact_bonus = 5.0 if name_str.lower() in state_text.lower() else 0.0
            overlap = len(tokens.intersection(target_tokens))
            score = overlap + exact_bonus
            scored.append((name_str, score))

        # Sort descending by score
        scored.sort(key=lambda x: x[1], reverse=True)
        top_candidates = [item[0] for item in scored[:k]]

        # Ensure at least k or len items returned
        if not top_candidates:
            if isinstance(criteria, dict):
                top_candidates = list(criteria.keys())[:k]
            else:
                top_candidates = list(criteria)[:k]

        return top_candidates

    def execute_shortlist(
        self,
        engine: Any,
        state: Union[str, Dict[str, Any], List[Any]],
        instructions: str,
        criteria: Union[Dict[str, Optional[str]], List[str]],
        k: int = 20,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Shortlist top-k candidates and run single forward pass decision."""
        start_time = time.perf_counter()

        # 1. Extract string representation for state
        state_str = laya.common.serialize_state(state) if hasattr(laya, "common") else str(state)

        # 2. Select top-k candidates
        all_candidates_count = len(criteria)
        if all_candidates_count <= k:
            shortlisted = list(criteria.keys()) if isinstance(criteria, dict) else list(criteria)
        else:
            shortlisted = self.filter_candidates_lexical(state_str, criteria, k=k)

        # 3. Build refined choice question with shortlisted options
        if isinstance(criteria, dict):
            refined_criteria = {c: criteria.get(c) for c in shortlisted}
        else:
            refined_criteria = {c: None for c in shortlisted}

        shortlist_question = {
            "selected_option": {
                "type": "choice",
                "instructions": instructions,
                "criteria": refined_criteria,
            }
        }

        # 4. Predict using Laya engine
        pred_res = engine.predict(
            state=state,
            questions=shortlist_question,
            model=model,
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        answers = pred_res.get("answers", {})
        selected_answer = answers.get("selected_option", {})
        winning_choice = str(selected_answer.get("choice", shortlisted[0] if shortlisted else "unknown"))
        confidence = float(selected_answer.get("confidence", 0.0))

        return {
            "success": True,
            "selected_choice": winning_choice,
            "confidence": confidence,
            "shortlisted_candidates": shortlisted,
            "answers": answers,
            "routing": pred_res.get("routing"),
            "latency_ms": latency_ms,
        }


shortlist_service = ShortlistService()
