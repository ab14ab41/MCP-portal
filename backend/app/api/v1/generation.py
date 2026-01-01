"""
API endpoints for MCP server generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import io
import zipfile
import logging

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.project import Project
from app.models.swagger_spec import SwaggerSpec
from app.models.endpoint_configuration import EndpointConfiguration
from app.models.generated_mcp_server import GeneratedMCPServer
from app.services.mcp_generator import mcp_generator_service
from app.services.mcp_serving import mcp_serving_service
from fastapi.responses import StreamingResponse, JSONResponse

router = APIRouter(prefix="/swagger-specs", tags=["generation"])


class GenerateMCPRequest(BaseModel):
    """Request model for MCP generation."""
    server_name: Optional[str] = None
    server_description: Optional[str] = None


class GenerateMCPResponse(BaseModel):
    """Response model for MCP generation."""
    generation_id: uuid.UUID
    status: str
    message: str
    selected_endpoints_count: int


class GenerationStatusResponse(BaseModel):
    """Response model for generation status."""
    id: uuid.UUID
    status: str
    server_name: str
    selected_endpoints_count: int
    error_message: Optional[str]
    created_at: datetime
    lines_of_code: Optional[int]


@router.get("/deployed-servers")
async def list_deployed_servers(db: AsyncSession = Depends(get_db)):
    """
    List all MCP servers that have been deployed (active or stopped).

    Returns:
        List of deployed servers with full details, including both active and inactive
    """
    try:
        result = await db.execute(
            select(GeneratedMCPServer)
            .options(
                selectinload(GeneratedMCPServer.swagger_spec).selectinload(SwaggerSpec.project)
            )
            .where(GeneratedMCPServer.deployed_at != None)
            .order_by(GeneratedMCPServer.deployed_at.desc())
        )
        servers = result.scalars().all()

        servers_list = []
        for server in servers:
            try:
                server_dict = {
                    "id": str(server.id),
                    "server_name": server.server_name,
                    "deployment_url": server.deployment_url,
                    "deployed_at": server.deployed_at.isoformat() if server.deployed_at else None,
                    "selected_endpoints_count": server.selected_endpoints_count,
                    "lines_of_code": server.lines_of_code or 0,
                    "swagger_spec_id": str(server.swagger_spec_id),
                    "swagger_spec_title": None,
                    "project_id": None,
                    "project_name": None,
                    "base_url": None,
                    "is_active": mcp_serving_service.is_server_active(str(server.id))
                }

                # Safely access relationships
                if server.swagger_spec:
                    server_dict["swagger_spec_title"] = server.swagger_spec.title
                    server_dict["base_url"] = server.swagger_spec.base_url
                    server_dict["project_id"] = str(server.swagger_spec.project_id)

                    if server.swagger_spec.project:
                        server_dict["project_name"] = server.swagger_spec.project.name

                servers_list.append(server_dict)
            except Exception as e:
                logger.error(f"Error serializing server {server.id}: {e}")
                continue

        return {"servers": servers_list}
    except Exception as e:
        logger.error(f"Error fetching deployed servers: {e}")
        return {"servers": []}


@router.post("/{spec_id}/generate-mcp", response_model=GenerateMCPResponse)
async def generate_mcp_server(
    spec_id: uuid.UUID,
    request: GenerateMCPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate MCP server code from configured endpoints.

    Args:
        spec_id: Swagger spec ID
        request: Generation configuration
        db: Database session

    Returns:
        Generation response with ID and status
    """
    # Get swagger spec
    result = await db.execute(
        select(SwaggerSpec).where(SwaggerSpec.id == spec_id)
    )
    spec = result.scalar_one_or_none()

    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swagger specification not found"
        )

    # Get all selected endpoint configurations
    result = await db.execute(
        select(EndpointConfiguration).where(
            EndpointConfiguration.swagger_spec_id == spec_id,
            EndpointConfiguration.is_selected == True
        )
    )
    selected_endpoints = result.scalars().all()

    if not selected_endpoints:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No endpoints selected for generation"
        )

    # Validate all selected endpoints have descriptions
    missing_descriptions = [
        f"{ep.http_method} {ep.path}"
        for ep in selected_endpoints
        if not ep.mcp_description
    ]
    if missing_descriptions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing descriptions for endpoints: {', '.join(missing_descriptions)}"
        )

    # Prepare server name
    server_name = request.server_name or spec.title.replace(" ", "_")
    server_description = request.server_description or spec.spec_description

    # Prepare endpoint data for generation
    endpoints_data = []
    for ep in selected_endpoints:
        # Extract parameters list from the stored dict format {"parameters": [...]}
        param_configs = []
        if ep.parameter_configurations and isinstance(ep.parameter_configurations, dict):
            param_configs = ep.parameter_configurations.get("parameters", [])

        endpoints_data.append({
            'http_method': ep.http_method,
            'path': ep.path,
            'mcp_tool_name': ep.mcp_tool_name,
            'mcp_description': ep.mcp_description,
            'parameter_configurations': param_configs
        })

    try:
        # Generate MCP server code
        generated_files = await mcp_generator_service.generate_mcp_server(
            server_name=server_name,
            server_description=server_description,
            base_url=spec.base_url or "",
            endpoints=endpoints_data
        )

        # Calculate lines of code
        lines_of_code = len(generated_files['main_code'].splitlines())

        # Create generated server record
        generated_server = GeneratedMCPServer(
            swagger_spec_id=spec_id,
            server_name=server_name,
            server_description=server_description,
            python_code=generated_files['main_code'],
            requirements_txt=generated_files['requirements'],
            additional_files={
                'README.md': generated_files['readme'],
                'config.json.example': generated_files['config_example']
            },
            selected_endpoints_count=len(selected_endpoints),
            lines_of_code=lines_of_code,
            generation_status='completed'
        )

        db.add(generated_server)
        await db.commit()
        await db.refresh(generated_server)

        return GenerateMCPResponse(
            generation_id=generated_server.id,
            status='completed',
            message='MCP server generated successfully',
            selected_endpoints_count=len(selected_endpoints)
        )

    except Exception as e:
        # Create failed generation record
        generated_server = GeneratedMCPServer(
            swagger_spec_id=spec_id,
            server_name=server_name,
            server_description=server_description,
            python_code="",
            requirements_txt="",
            selected_endpoints_count=len(selected_endpoints),
            generation_status='failed',
            error_message=str(e)
        )

        db.add(generated_server)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate MCP server: {str(e)}"
        )


@router.get("/generated-servers/{generation_id}/status", response_model=GenerationStatusResponse)
async def get_generation_status(
    generation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of MCP generation.

    Args:
        generation_id: Generation ID
        db: Database session

    Returns:
        Generation status information
    """
    result = await db.execute(
        select(GeneratedMCPServer).where(GeneratedMCPServer.id == generation_id)
    )
    generated_server = result.scalar_one_or_none()

    if not generated_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated server not found"
        )

    return GenerationStatusResponse(
        id=generated_server.id,
        status=generated_server.generation_status,
        server_name=generated_server.server_name,
        selected_endpoints_count=generated_server.selected_endpoints_count,
        error_message=generated_server.error_message,
        created_at=generated_server.created_at,
        lines_of_code=generated_server.lines_of_code
    )


@router.get("/generated-servers/{generation_id}/download")
async def download_generated_server(
    generation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Download generated MCP server as ZIP file.

    Args:
        generation_id: Generation ID
        db: Database session

    Returns:
        ZIP file containing MCP server code
    """
    result = await db.execute(
        select(GeneratedMCPServer).where(GeneratedMCPServer.id == generation_id)
    )
    generated_server = result.scalar_one_or_none()

    if not generated_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated server not found"
        )

    if generated_server.generation_status != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Generation is not completed. Status: {generated_server.generation_status}"
        )

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main.py
        zip_file.writestr('main.py', generated_server.python_code)

        # Add requirements.txt
        zip_file.writestr('requirements.txt', generated_server.requirements_txt)

        # Add additional files
        if generated_server.additional_files:
            for filename, content in generated_server.additional_files.items():
                zip_file.writestr(filename, content)

    # Update download tracking
    generated_server.download_count += 1
    generated_server.downloaded_at = datetime.utcnow()
    await db.commit()

    # Prepare ZIP for download
    zip_buffer.seek(0)

    # Sanitize filename
    safe_name = generated_server.server_name.replace(" ", "_").replace("/", "_")

    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={safe_name}_mcp_server.zip"
        }
    )


@router.get("/{spec_id}/generated-servers")
async def list_generated_servers(
    spec_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    List all generated MCP servers for a spec.

    Args:
        spec_id: Swagger spec ID
        db: Database session

    Returns:
        List of generated servers with current deployment info
    """
    result = await db.execute(
        select(GeneratedMCPServer)
        .where(GeneratedMCPServer.swagger_spec_id == spec_id)
        .order_by(GeneratedMCPServer.created_at.desc())
    )
    servers = result.scalars().all()

    # Find the currently deployed server
    deployed_server_id = None
    for server in servers:
        if server.is_deployed:
            deployed_server_id = str(server.id)
            break

    return {
        "servers": [
            {
                "id": server.id,
                "server_name": server.server_name,
                "status": server.generation_status,
                "selected_endpoints_count": server.selected_endpoints_count,
                "lines_of_code": server.lines_of_code,
                "created_at": server.created_at,
                "download_count": server.download_count,
                "is_deployed": server.is_deployed,
                "deployment_url": server.deployment_url,
                "deployed_at": server.deployed_at
            }
            for server in servers
        ],
        "current_deployed_id": deployed_server_id
    }


@router.post("/generated-servers/{generation_id}/deploy")
async def deploy_mcp_server(
    generation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Deploy an MCP server to make it accessible via HTTP.

    Args:
        generation_id: Generation ID
        db: Database session

    Returns:
        Deployment information
    """
    result = await db.execute(
        select(GeneratedMCPServer)
        .options(selectinload(GeneratedMCPServer.swagger_spec))
        .where(GeneratedMCPServer.id == generation_id)
    )
    generated_server = result.scalar_one_or_none()

    if not generated_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated server not found"
        )

    if generated_server.generation_status != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot deploy: generation status is {generated_server.generation_status}"
        )

    if generated_server.is_deployed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server is already deployed"
        )

    # Check if there's already a deployed server for this PROJECT
    # Only one MCP can be deployed per project at a time
    project_id = generated_server.swagger_spec.project_id

    result_check = await db.execute(
        select(GeneratedMCPServer)
        .join(SwaggerSpec)
        .where(
            SwaggerSpec.project_id == project_id,
            GeneratedMCPServer.is_deployed == True,
            GeneratedMCPServer.id != generation_id
        )
    )
    existing_deployed_list = result_check.scalars().all()

    if existing_deployed_list:
        # Block deployment - don't auto-undeploy
        existing_names = [s.server_name for s in existing_deployed_list]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot deploy: Project already has a deployed MCP server ({', '.join(existing_names)}). Please undeploy it first from the 'Deployed MCPs' page."
        )

    # Get endpoint configurations for this spec
    result = await db.execute(
        select(EndpointConfiguration).where(
            EndpointConfiguration.swagger_spec_id == generated_server.swagger_spec_id,
            EndpointConfiguration.is_selected == True
        )
    )
    selected_endpoints = result.scalars().all()

    # Prepare endpoints data for serving
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
            'parameter_configurations': param_configs
        })

    # Register with serving service
    server_id = str(generation_id)
    success = await mcp_serving_service.register_server(
        server_id=server_id,
        server_name=generated_server.server_name,
        base_url=generated_server.swagger_spec.base_url or "",
        endpoints=endpoints_data
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deploy server"
        )

    # Update deployment status
    generated_server.is_deployed = True
    generated_server.deployed_at = datetime.utcnow()
    generated_server.deployment_url = f"/api/v1/mcp/serve/{server_id}"
    await db.commit()

    return {
        "message": "Server deployed successfully",
        "deployment_url": generated_server.deployment_url,
        "server_id": server_id
    }


@router.post("/generated-servers/{generation_id}/undeploy")
async def undeploy_mcp_server(
    generation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Undeploy an MCP server.

    Args:
        generation_id: Generation ID
        db: Database session

    Returns:
        Undeployment status
    """
    result = await db.execute(
        select(GeneratedMCPServer).where(GeneratedMCPServer.id == generation_id)
    )
    generated_server = result.scalar_one_or_none()

    if not generated_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated server not found"
        )

    if not generated_server.is_deployed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server is not deployed"
        )

    # Unregister from serving service
    server_id = str(generation_id)
    mcp_serving_service.unregister_server(server_id)

    # Update deployment status
    generated_server.is_deployed = False
    generated_server.deployment_url = None
    await db.commit()

    return {
        "message": "Server undeployed successfully"
    }


@router.delete("/generated-servers/{generation_id}")
async def delete_mcp_server(
    generation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an MCP server permanently.

    Args:
        generation_id: Generation ID
        db: Database session

    Returns:
        Deletion status
    """
    result = await db.execute(
        select(GeneratedMCPServer).where(GeneratedMCPServer.id == generation_id)
    )
    generated_server = result.scalar_one_or_none()

    if not generated_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated server not found"
        )

    # If deployed, unregister from serving service first
    if generated_server.is_deployed:
        server_id = str(generation_id)
        mcp_serving_service.unregister_server(server_id)

    # Delete the server
    await db.delete(generated_server)
    await db.commit()

    return {
        "message": "Server deleted successfully"
    }
