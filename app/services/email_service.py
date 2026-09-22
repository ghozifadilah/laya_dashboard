from typing import Any, Dict, Optional
import laya
from app.services.presets_service import presets_catalog


class EmailService:
    """Service for parsing, cleaning, and triaging email messages."""

    def clean_body(self, raw_body: str, max_chars: int = 3000) -> Dict[str, Any]:
        """Strip reply chains, disclaimers, signatures, and extra blank lines."""
        cleaned = laya.clean_email_body(raw_body or "", max_chars=max_chars)
        orig_len = len(raw_body or "")
        clean_len = len(cleaned)
        ratio = round(clean_len / max(1, orig_len), 4)

        return {
            "cleaned_text": cleaned,
            "original_length": orig_len,
            "cleaned_length": clean_len,
            "compression_ratio": ratio,
        }

    def build_state(
        self,
        subject: str,
        body: str,
        sender: Optional[str] = None,
        clean: bool = True,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Construct a structured email state payload suitable for Laya decision evaluation."""
        extra_fields = extra or {}
        return laya.email_state(
            subject=subject or "",
            body=body or "",
            sender=sender,
            clean=clean,
            **extra_fields,
        )

    def get_email_questions(self, categories: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get email classification question schema."""
        return laya.email_questions(categories=categories)


email_service = EmailService()
