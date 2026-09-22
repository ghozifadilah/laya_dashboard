import time
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_api_key
from app.schemas.email import (
    EmailCleanRequest,
    EmailCleanResponse,
    EmailStateRequest,
    EmailTriageRequest,
    EmailTriageResponse,
)
from app.schemas.predict import RoutingMetadata
from app.services.email_service import email_service
from app.services.laya_engine import get_laya_engine, LayaEngine

router = APIRouter()


@router.post(
    "/email/clean",
    response_model=EmailCleanResponse,
    summary="Clean and compress raw email body text",
    description="Strips reply chains, disclaimers, signatures, and extra blank lines for cleaner token budget.",
)
async def clean_email(request: EmailCleanRequest) -> EmailCleanResponse:
    res = email_service.clean_body(request.body, max_chars=request.max_chars)
    return EmailCleanResponse(**res)


@router.post(
    "/email/state",
    summary="Construct normalized email state dictionary",
    description="Parses subject, body, sender and metadata into a clean state dict formatted for Laya decision engines.",
)
async def create_email_state(request: EmailStateRequest) -> Dict[str, Any]:
    state = email_service.build_state(
        subject=request.subject,
        body=request.body,
        sender=request.sender,
        clean=request.clean,
        extra=request.extra,
    )
    return {"state": state}


@router.post(
    "/email/triage",
    response_model=EmailTriageResponse,
    summary="Full email triage pipeline (clean, classify, detect threats)",
    description="Cleans email body, formats structured state, and evaluates department classification, urgency, and risks in single forward pass.",
)
async def triage_inbound_email(
    request: EmailTriageRequest,
    api_key: str = Depends(get_api_key),
    engine: LayaEngine = Depends(get_laya_engine),
) -> EmailTriageResponse:
    start_time = time.perf_counter()
    try:
        # 1. Build structured email state
        state = email_service.build_state(
            subject=request.subject,
            body=request.body,
            sender=request.sender,
            clean=request.clean,
        )

        # 2. Get questions schema
        questions = email_service.get_email_questions(categories=request.categories)

        # 3. Predict using Laya engine
        pred_res = engine.predict(
            state=state,
            questions=questions,
            model=request.model,
        )

        answers = pred_res.get("answers", {})

        # Extract summary highlights
        category_ans = answers.get("category", {})
        summary = {
            "category": category_ans.get("choice", "unknown"),
            "category_confidence": category_ans.get("confidence", 0.0),
            "threat_detected": any(
                answers.get(k, {}).get("choice") is True
                for k in ["phishing", "security", "threat", "is_urgent", "churn_risk"]
                if k in answers
            ),
        }

        # Check for urgency or score
        if "urgency" in answers:
            summary["urgency"] = answers["urgency"].get("level") or answers["urgency"].get("score")
        if "churn_risk" in answers:
            summary["churn_risk"] = answers["churn_risk"].get("choice")

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        routing_raw = pred_res.get("routing")
        routing_meta = RoutingMetadata(**routing_raw) if routing_raw else None

        return EmailTriageResponse(
            success=True,
            clean_state=state,
            answers=answers,
            summary=summary,
            routing=routing_meta,
            latency_ms=latency_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Email triage failed: {str(e)}")
