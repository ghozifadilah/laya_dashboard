from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, status
from app.schemas.workflows import (
    WorkflowCreateRequest,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowUpdateRequest,
)
from app.services.auth_service import get_current_user_optional
from app.services.workflow_storage import workflow_storage

router = APIRouter(prefix="/workflows", tags=["Workflow Projects"])


@router.get(
    "",
    response_model=WorkflowListResponse,
    summary="List all custom user-defined workflows",
)
@router.get(
    "/",
    response_model=WorkflowListResponse,
    include_in_schema=False,
)
async def list_custom_workflows() -> WorkflowListResponse:
    items = workflow_storage.list_workflows()
    return WorkflowListResponse(
        total=len(items),
        workflows=[WorkflowResponse(**item) for item in items],
    )


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new custom decision workflow / project",
)
@router.post(
    "/",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_custom_workflow(
    request: WorkflowCreateRequest,
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
) -> WorkflowResponse:
    uname = user.get("username", "admin") if user else "admin"

    saved = workflow_storage.save_workflow(
        name=request.name,
        title=request.title,
        description=request.description,
        questions=request.questions,
        example_state=request.example_state,
        model=request.model,
        created_by=uname,
    )
    return WorkflowResponse(**saved)


@router.get(
    "/{workflow_name}",
    response_model=WorkflowResponse,
    summary="Get custom workflow details by name",
)
async def get_custom_workflow(
    workflow_name: str = Path(..., description="Workflow unique identifier"),
) -> WorkflowResponse:
    item = workflow_storage.get_workflow(workflow_name)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{workflow_name}' tidak ditemukan.",
        )
    return WorkflowResponse(**item)


@router.put(
    "/{workflow_name}",
    response_model=WorkflowResponse,
    summary="Update an existing custom workflow",
)
async def update_custom_workflow(
    workflow_name: str = Path(..., description="Workflow unique identifier"),
    request: WorkflowUpdateRequest = ...,
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
) -> WorkflowResponse:
    existing = workflow_storage.get_workflow(workflow_name)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{workflow_name}' tidak ditemukan.",
        )
    uname = user.get("username", "admin") if user else "admin"
    updated = workflow_storage.save_workflow(
        name=workflow_name,
        title=request.title if request.title is not None else existing.get("title", workflow_name),
        description=request.description if request.description is not None else existing.get("description", ""),
        questions=request.questions if request.questions is not None else existing.get("questions", {}),
        example_state=request.example_state if request.example_state is not None else existing.get("example_state", ""),
        model=request.model if request.model is not None else existing.get("model", "auto"),
        created_by=existing.get("created_by", uname),
    )
    return WorkflowResponse(**updated)


@router.delete(
    "/{workflow_name}",
    summary="Delete a custom workflow",
)
async def delete_custom_workflow(
    workflow_name: str = Path(..., description="Workflow unique identifier"),
) -> Dict[str, Any]:
    deleted = workflow_storage.delete_workflow(workflow_name)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{workflow_name}' tidak ditemukan.",
        )
    return {"success": True, "message": f"Workflow '{workflow_name}' berhasil dihapus."}
