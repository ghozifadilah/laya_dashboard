"""Pydantic schemas for request validation and response serialization."""

from app.schemas.predict import (
    PredictRequest,
    PredictResponse,
    AnswerItem,
    RoutingMetadata,
)
from app.schemas.batch import BatchPredictRequest, BatchPredictResponse
from app.schemas.presets import (
    PresetListResponse,
    PresetDetail,
    PresetExecuteRequest,
)
from app.schemas.email import (
    EmailStateRequest,
    EmailCleanRequest,
    EmailCleanResponse,
    EmailTriageRequest,
    EmailTriageResponse,
)
from app.schemas.lang import LangDetectRequest, LangDetectResponse
from app.schemas.shortlist import ShortlistRequest, ShortlistResponse
from app.schemas.models import (
    ModelInfo,
    ModelListResponse,
    PreloadRequest,
    PreloadResponse,
    InspectRouteRequest,
    InspectRouteResponse,
)
