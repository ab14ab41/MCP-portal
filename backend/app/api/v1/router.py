"""
Main API v1 router.
"""

from fastapi import APIRouter
from app.api.v1 import projects, swagger_specs, endpoint_configs, generation, mcp_serve, ai_testing

api_router = APIRouter()

# Include sub-routers
# Note: generation.router must come before swagger_specs.router
# because both use /swagger-specs prefix and generation has
# /deployed-servers which would otherwise match /{spec_id}
api_router.include_router(projects.router)
api_router.include_router(generation.router)
api_router.include_router(swagger_specs.router)
api_router.include_router(endpoint_configs.router)
api_router.include_router(mcp_serve.router)
api_router.include_router(ai_testing.router)
