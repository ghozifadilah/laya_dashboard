from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class WorkflowCreateRequest(BaseModel):
    name: str = Field(
        ...,
        description="Unique identifier for the workflow (alphanumeric and underscore), e.g. 'fraud_detection'",
        examples=["fraud_detection"],
    )
    title: str = Field(
        ...,
        description="Human friendly display title",
        examples=["E-Commerce Order Fraud & Risk Detection"],
    )
    description: str = Field(
        ...,
        description="Detailed description of the workflow purpose",
        examples=["Evaluates order risk, chargeback probability, and fraud action."],
    )
    questions: Dict[str, Any] = Field(
        ...,
        description="Dictionary of typed questions (choice, score, noul)",
    )
    example_state: Union[str, Dict[str, Any], List[Any]] = Field(
        ...,
        description="Sample input state (text or JSON) demonstrating this workflow",
    )
    model: Optional[str] = Field(
        "auto",
        description="Target checkpoint model: 'auto', 'english', 'multilingual', 'typed-decisions'",
    )


class WorkflowUpdateRequest(BaseModel):
    title: Optional[str] = Field(
        None,
        description="Human friendly display title",
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the workflow purpose",
    )
    questions: Optional[Dict[str, Any]] = Field(
        None,
        description="Dictionary of typed questions (choice, score, noul)",
    )
    example_state: Optional[Union[str, Dict[str, Any], List[Any]]] = Field(
        None,
        description="Sample input state (text or JSON) demonstrating this workflow",
    )
    model: Optional[str] = Field(
        None,
        description="Target checkpoint model: 'auto', 'english', 'multilingual', 'typed-decisions'",
    )


class WorkflowResponse(BaseModel):
    name: str
    title: str
    description: str
    questions: Dict[str, Any]
    example_state: Union[str, Dict[str, Any], List[Any]]
    model: Optional[str] = "auto"
    is_custom: bool = True
    created_by: Optional[str] = "admin"
    created_at: Optional[float] = None
    updated_at: Optional[float] = None


class WorkflowListResponse(BaseModel):
    total: int
    workflows: List[WorkflowResponse]
