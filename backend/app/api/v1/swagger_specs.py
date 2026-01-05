"""
Swagger Spec API endpoints.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import json

from app.database import get_db
from app.models.swagger_spec import SwaggerSpec
from app.models.project import Project
from app.schemas.swagger_spec import (
    SwaggerSpecResponse,
    SwaggerSpecFromContent,
    SwaggerSpecFromURL,
    SwaggerSpecWithEndpoints,
    ValidationResult,
    SwaggerSpecUpdateBaseURL
)
from app.repositories.swagger_spec import swagger_spec_repository
from app.repositories.project import project_repository
from app.services.swagger_parser import swagger_parser_service
from app.services.mcp_serving import mcp_serving_service
from app.utils.exceptions import NotFoundException, BadRequestException, InvalidSwaggerSpecException
from app.config import settings
from sqlalchemy import select
from app.models.generated_mcp_server import GeneratedMCPServer
from app.models.endpoint_configuration import EndpointConfiguration
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/swagger-specs", tags=["swagger-specs"])


@router.post("/upload", response_model=SwaggerSpecResponse, status_code=201)
async def upload_swagger_spec(
    project_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a Swagger/OpenAPI specification file."""
    # Verify project exists
    project = await project_repository.get(db, project_id)
    if not project:
        raise NotFoundException("Project", str(project_id))

    # Validate file size
    contents = await file.read()
    if len(contents) > settings.max_upload_size:
        raise BadRequestException(f"File size exceeds maximum of {settings.max_upload_size} bytes")

    # Validate file extension
    filename = file.filename or ""
    file_ext = filename.lower().split(".")[-1]
    if file_ext not in ["json", "yaml", "yml"]:
        raise BadRequestException("Invalid file type. Only JSON, YAML, and YML files are allowed")

    # Decode content
    try:
        content_str = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise BadRequestException("File must be UTF-8 encoded")

    # Determine format
    format = "json" if file_ext == "json" else "yaml"

    # Parse and validate spec
    spec = await swagger_parser_service.parse_spec(content_str, format, validate=True)

    # Extract metadata
    version = swagger_parser_service.get_spec_version(spec)
    title = spec.get("info", {}).get("title", "Untitled API")
    description = spec.get("info", {}).get("description")
    base_url = swagger_parser_service.extract_base_url(spec)

    # Extract endpoints
    endpoints = await swagger_parser_service.extract_endpoints(spec)

    # Create endpoints summary
    endpoints_summary = [
        {
            "method": ep["method"],
            "path": ep["path"],
            "operation_id": ep.get("operation_id"),
            "summary": ep.get("summary", "")
        }
        for ep in endpoints
    ]

    # Create swagger spec record
    swagger_spec = SwaggerSpec(
        project_id=project_id,
        spec_version=version,
        title=title,
        spec_description=description,
        base_url=base_url,
        original_spec=spec,
        source_type="upload",
        source_reference=filename,
        total_endpoints=len(endpoints),
        endpoints_summary={"endpoints": endpoints_summary}
    )

    created_spec = await swagger_spec_repository.create(db, swagger_spec)
    return created_spec


@router.post("/from-url", response_model=SwaggerSpecResponse, status_code=201)
async def create_spec_from_url(
    spec_data: SwaggerSpecFromURL,
    db: AsyncSession = Depends(get_db)
):
    """Fetch and create a Swagger spec from a URL."""
    # Verify project exists
    project = await project_repository.get(db, spec_data.project_id)
    if not project:
        raise NotFoundException("Project", str(spec_data.project_id))

    # Fetch spec from URL
    content_str, format = await swagger_parser_service.fetch_spec_from_url(str(spec_data.url))

    # Parse and validate spec
    spec = await swagger_parser_service.parse_spec(content_str, format, validate=True)

    # Extract metadata
    version = swagger_parser_service.get_spec_version(spec)
    title = spec.get("info", {}).get("title", "Untitled API")
    description = spec.get("info", {}).get("description")
    base_url = swagger_parser_service.extract_base_url(spec)

    # Extract endpoints
    endpoints = await swagger_parser_service.extract_endpoints(spec)

    # Create endpoints summary
    endpoints_summary = [
        {
            "method": ep["method"],
            "path": ep["path"],
            "operation_id": ep.get("operation_id"),
            "summary": ep.get("summary", "")
        }
        for ep in endpoints
    ]

    # Create swagger spec record
    swagger_spec = SwaggerSpec(
        project_id=spec_data.project_id,
        spec_version=version,
        title=title,
        spec_description=description,
        base_url=base_url,
        original_spec=spec,
        source_type="url",
        source_reference=str(spec_data.url),
        total_endpoints=len(endpoints),
        endpoints_summary={"endpoints": endpoints_summary}
    )

    created_spec = await swagger_spec_repository.create(db, swagger_spec)
    return created_spec


@router.post("/from-content", response_model=SwaggerSpecResponse, status_code=201)
async def create_spec_from_content(
    spec_data: SwaggerSpecFromContent,
    db: AsyncSession = Depends(get_db)
):
    """Create a Swagger spec from pasted content."""
    # Verify project exists
    project = await project_repository.get(db, spec_data.project_id)
    if not project:
        raise NotFoundException("Project", str(spec_data.project_id))

    # Parse and validate spec
    spec = await swagger_parser_service.parse_spec(spec_data.content, spec_data.format, validate=True)

    # Extract metadata
    version = swagger_parser_service.get_spec_version(spec)
    title = spec.get("info", {}).get("title", "Untitled API")
    description = spec.get("info", {}).get("description")
    base_url = swagger_parser_service.extract_base_url(spec)

    # Extract endpoints
    endpoints = await swagger_parser_service.extract_endpoints(spec)

    # Create endpoints summary
    endpoints_summary = [
        {
            "method": ep["method"],
            "path": ep["path"],
            "operation_id": ep.get("operation_id"),
            "summary": ep.get("summary", "")
        }
        for ep in endpoints
    ]

    # Create swagger spec record
    swagger_spec = SwaggerSpec(
        project_id=spec_data.project_id,
        spec_version=version,
        title=title,
        spec_description=description,
        base_url=base_url,
        original_spec=spec,
        source_type="paste",
        source_reference=None,
        total_endpoints=len(endpoints),
        endpoints_summary={"endpoints": endpoints_summary}
    )

    created_spec = await swagger_spec_repository.create(db, swagger_spec)
    return created_spec


@router.get("/{spec_id}", response_model=SwaggerSpecResponse)
async def get_swagger_spec(
    spec_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a swagger spec by ID."""
    spec = await swagger_spec_repository.get(db, spec_id)
    if not spec:
        raise NotFoundException("Swagger Spec", str(spec_id))
    return spec


@router.get("/{spec_id}/endpoints", response_model=SwaggerSpecWithEndpoints)
async def get_swagger_spec_endpoints(
    spec_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a swagger spec with full endpoint details."""
    spec = await swagger_spec_repository.get(db, spec_id)
    if not spec:
        raise NotFoundException("Swagger Spec", str(spec_id))

    # Extract endpoints from stored spec
    endpoints = await swagger_parser_service.extract_endpoints(spec.original_spec)

    return SwaggerSpecWithEndpoints(
        id=spec.id,
        project_id=spec.project_id,
        spec_version=spec.spec_version,
        title=spec.title,
        spec_description=spec.spec_description,
        base_url=spec.base_url,
        source_type=spec.source_type,
        source_reference=spec.source_reference,
        total_endpoints=spec.total_endpoints,
        endpoints_summary=spec.endpoints_summary,
        created_at=spec.created_at,
        updated_at=spec.updated_at,
        endpoints=endpoints
    )


@router.get("/project/{project_id}", response_model=List[SwaggerSpecResponse])
async def list_project_specs(
    project_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all swagger specs for a project."""
    # Verify project exists
    project = await project_repository.get(db, project_id)
    if not project:
        raise NotFoundException("Project", str(project_id))

    specs = await swagger_spec_repository.get_by_project(db, project_id, skip, limit)
    return specs


@router.delete("/{spec_id}", status_code=204)
async def delete_swagger_spec(
    spec_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a swagger spec."""
    deleted = await swagger_spec_repository.delete(db, spec_id)
    if not deleted:
        raise NotFoundException("Swagger Spec", str(spec_id))
    return None


@router.post("/validate", response_model=ValidationResult)
async def validate_swagger_spec(
    content: str = Form(...),
    format: str = Form(..., pattern="^(json|yaml)$")
):
    """Validate a Swagger/OpenAPI specification without saving it."""
    try:
        spec = await swagger_parser_service.parse_spec(content, format, validate=True)
        version = swagger_parser_service.get_spec_version(spec)

        return ValidationResult(
            valid=True,
            version=version,
            errors=None,
            warnings=None
        )
    except InvalidSwaggerSpecException as e:
        return ValidationResult(
            valid=False,
            version=None,
            errors=[str(e)],
            warnings=None
        )


@router.patch("/{spec_id}/base-url", response_model=SwaggerSpecResponse)
async def update_base_url(
    spec_id: UUID,
    update_data: SwaggerSpecUpdateBaseURL,
    db: AsyncSession = Depends(get_db)
):
    """
    Update the base URL for a Swagger spec.

    This will also update all deployed MCP servers using this spec.
    """
    # Get the swagger spec
    spec = await swagger_spec_repository.get(db, spec_id)
    if not spec:
        raise NotFoundException("Swagger Spec", str(spec_id))

    # Update base URL
    spec.base_url = update_data.base_url
    await db.commit()
    await db.refresh(spec)

    logger.info(f"Updated base_url for spec {spec_id} to: {update_data.base_url}")

    # Find all deployed MCP servers using this spec
    result = await db.execute(
        select(GeneratedMCPServer).where(
            GeneratedMCPServer.swagger_spec_id == spec_id,
            GeneratedMCPServer.is_deployed == True
        )
    )
    deployed_servers = result.scalars().all()

    # Re-register each deployed server with new base URL
    for server in deployed_servers:
        try:
            # Get endpoint configurations
            result = await db.execute(
                select(EndpointConfiguration).where(
                    EndpointConfiguration.swagger_spec_id == spec_id,
                    EndpointConfiguration.is_selected == True
                )
            )
            selected_endpoints = result.scalars().all()

            # Prepare endpoints data
            endpoints_data = []
            for ep in selected_endpoints:
                param_configs = []
                if ep.parameter_configurations and isinstance(ep.parameter_configurations, dict):
                    param_configs = ep.parameter_configurations.get("parameters", [])

                endpoints_data.append({
                    'http_method': ep.http_method,
                    'path': ep.path,
                    'mcp_tool_name': ep.mcp_tool_name,
                    'mcp_description': ep.mcp_description,
                    'parameter_configurations': param_configs,
                    'security_requirements': ep.security_requirements
                })

            # Re-register the server with new base URL
            await mcp_serving_service.register_server(
                server_id=str(server.id),
                server_name=server.server_name,
                base_url=update_data.base_url,
                endpoints=endpoints_data
            )

            logger.info(f"Re-registered MCP server {server.id} with new base_url")

        except Exception as e:
            logger.error(f"Error re-registering MCP server {server.id}: {e}")

    return spec
