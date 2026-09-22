from fastapi import APIRouter
from app.api.v1.endpoints import (
    api_keys,
    auth,
    batch,
    email,
    lang,
    models,
    predict,
    presets,
    router_mgmt,
    shortlist,
    workflows,
)

api_router = APIRouter()

# Authentication & User Management
api_router.include_router(auth.router)

# API Key & Token Management
api_router.include_router(api_keys.router)

# Custom Workflow Projects
api_router.include_router(workflows.router)

# Inference Endpoints
api_router.include_router(predict.router, tags=["Decision Inference"])
api_router.include_router(batch.router, tags=["Decision Inference"])

# Workflow Presets
api_router.include_router(presets.router, tags=["Workflow Presets"])

# Email & Document Helpers
api_router.include_router(email.router, tags=["Email & Documents"])

# Language & Script Analysis
api_router.include_router(lang.router, tags=["Language & Script Detection"])

# Taxonomy Shortlisting
api_router.include_router(shortlist.router, tags=["Taxonomy Shortlisting"])

# Router & Model Management
api_router.include_router(models.router, tags=["Models & Hardware"])
api_router.include_router(router_mgmt.router, tags=["Router Management"])
