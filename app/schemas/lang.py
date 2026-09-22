from typing import Dict, Optional
from pydantic import BaseModel, Field


class LangDetectRequest(BaseModel):
    text: str = Field(
        ...,
        description="The raw text snippet to inspect for language and script characteristics.",
        examples=["मुझसे दो बार शुल्क लिया गया, कृपया पैसे वापस करें।"],
    )


class LangDetectResponse(BaseModel):
    language: Optional[str] = Field(None, description="Detected ISO language code (e.g. 'en', 'hi', 'de', 'es', 'zh') or None if undecided")
    script: str = Field(..., description="Dominant writing script (e.g. 'latin', 'devanagari', 'cyrillic', 'arabic')")
    is_english: bool = Field(..., description="True if text is predominantly English in Latin script")
    language_undecided: bool = Field(..., description="True if language could not be determined unambiguously")
    diacritic_rate: float = Field(..., description="Rate of diacritics / accented characters")
    non_latin_fraction: float = Field(..., description="Proportion of letters belonging to non-Latin scripts")
    script_profile: Dict[str, float] = Field(..., description="Percentage distribution across all detected scripts")
    recommended_model: str = Field(
        ...,
        description="Recommended Laya checkpoint for this text ('english' or 'multilingual')",
    )
