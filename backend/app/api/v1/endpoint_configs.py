"""
Endpoint Configuration API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.endpoint_configuration import EndpointConfiguration
from app.models.swagger_spec import SwaggerSpec
from app.schemas.endpoint_config import (
    EndpointConfigResponse,
    EndpointConfigUpdate,
    EndpointConfigBatchUpdate,
    EndpointConfigWithDetails,
    ParameterConfigItem
)
from app.repositories.endpoint_config import endpoint_config_repository
from app.repositories.swagger_spec import swagger_spec_repository
from app.services.swagger_parser import swagger_parser_service
from app.utils.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/endpoint-configurations", tags=["endpoint-configurations"])


@router.post("/initialize/{swagger_spec_id}", response_model=List[EndpointConfigResponse])
async def initialize_endpoint_configurations(
    swagger_spec_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize endpoint configurations from a swagger spec.
    Creates configuration records for all endpoints in the spec.
    """
    # Get the swagger spec
    swagger_spec = await swagger_spec_repository.get(db, swagger_spec_id)
    if not swagger_spec:
        raise NotFoundException("Swagger Spec", str(swagger_spec_id))

    # Check if configurations already exist
    existing_configs = await endpoint_config_repository.get_by_swagger_spec(db, swagger_spec_id)
    if existing_configs:
        # Transform and return existing configurations
        result = []
        for config in existing_configs:
            param_configs = []
            if config.parameter_configurations and "parameters" in config.parameter_configurations:
                for param in config.parameter_configurations["parameters"]:
                    param_configs.append(ParameterConfigItem(**param))

            config_dict = {
                "id": config.id,
                "swagger_spec_id": config.swagger_spec_id,
                "http_method": config.http_method,
                "path": config.path,
                "operation_id": config.operation_id,
                "is_selected": config.is_selected,
                "mcp_tool_name": config.mcp_tool_name,
                "mcp_description": config.mcp_description,
                "parameter_configurations": param_configs,
                "request_schema": config.request_schema,
                "response_schema": config.response_schema,
                "created_at": config.created_at,
                "updated_at": config.updated_at
            }
            result.append(EndpointConfigResponse(**config_dict))
        return result

    # Extract endpoints from the spec
    endpoints = await swagger_parser_service.extract_endpoints(swagger_spec.original_spec)

    # Create configuration for each endpoint
    created_configs = []
    for endpoint in endpoints:
        # Convert parameters to ParameterConfigItem format
        parameter_configs = []
        for param in endpoint.get("parameters", []):
            param_config = {
                "name": param["name"],
                "type": param["schema"].get("type", "string"),
                "location": param["location"],
                "description": param.get("description", ""),
                "required": param["required"],
                "user_required": param["required"],  # Initialize with original value
                "deprecated": param.get("deprecated", False),
                "schema": param["schema"]
            }
            parameter_configs.append(param_config)

        # Create endpoint configuration
        config = EndpointConfiguration(
            swagger_spec_id=swagger_spec_id,
            http_method=endpoint["method"],
            path=endpoint["path"],
            operation_id=endpoint.get("operation_id"),
            is_selected=False,
            mcp_tool_name=None,
            mcp_description=None,
            parameter_configurations={"parameters": parameter_configs} if parameter_configs else None,
            request_schema=endpoint.get("request_body"),
            response_schema=endpoint.get("responses")
        )

        created_config = await endpoint_config_repository.create(db, config)

        # Transform for response
        param_configs = []
        if created_config.parameter_configurations and "parameters" in created_config.parameter_configurations:
            for param in created_config.parameter_configurations["parameters"]:
                param_configs.append(ParameterConfigItem(**param))

        config_dict = {
            "id": created_config.id,
            "swagger_spec_id": created_config.swagger_spec_id,
            "http_method": created_config.http_method,
            "path": created_config.path,
            "operation_id": created_config.operation_id,
            "is_selected": created_config.is_selected,
            "mcp_tool_name": created_config.mcp_tool_name,
            "mcp_description": created_config.mcp_description,
            "parameter_configurations": param_configs,
            "request_schema": created_config.request_schema,
            "response_schema": created_config.response_schema,
            "created_at": created_config.created_at,
            "updated_at": created_config.updated_at
        }
        created_configs.append(EndpointConfigResponse(**config_dict))

    await db.commit()
    return created_configs


@router.get("/swagger-spec/{swagger_spec_id}", response_model=List[EndpointConfigWithDetails])
async def get_endpoint_configurations(
    swagger_spec_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all endpoint configurations for a swagger spec with details."""
    # Verify swagger spec exists
    swagger_spec = await swagger_spec_repository.get(db, swagger_spec_id)
    if not swagger_spec:
        raise NotFoundException("Swagger Spec", str(swagger_spec_id))

    # Get configurations
    configs = await endpoint_config_repository.get_by_swagger_spec(db, swagger_spec_id)

    # If no configs exist, initialize them
    if not configs:
        configs = await initialize_endpoint_configurations(swagger_spec_id, db)

    # Extract endpoints from spec to get additional details
    endpoints = await swagger_parser_service.extract_endpoints(swagger_spec.original_spec)
    endpoints_map = {
        f"{ep['method']}:{ep['path']}": ep
        for ep in endpoints
    }

    # Enrich configurations with endpoint details
    result = []
    for config in configs:
        key = f"{config.http_method}:{config.path}"
        endpoint = endpoints_map.get(key, {})

        # Convert parameter_configurations to ParameterConfigItem
        param_configs = []
        if config.parameter_configurations and "parameters" in config.parameter_configurations:
            for param in config.parameter_configurations["parameters"]:
                param_configs.append(ParameterConfigItem(**param))

        config_dict = {
            "id": config.id,
            "swagger_spec_id": config.swagger_spec_id,
            "http_method": config.http_method,
            "path": config.path,
            "operation_id": config.operation_id,
            "is_selected": config.is_selected,
            "mcp_tool_name": config.mcp_tool_name,
            "mcp_description": config.mcp_description,
            "parameter_configurations": param_configs,
            "request_schema": config.request_schema,
            "response_schema": config.response_schema,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "summary": endpoint.get("summary", ""),
            "description": endpoint.get("description", ""),
            "tags": endpoint.get("tags", []),
            "deprecated": endpoint.get("deprecated", False)
        }
        result.append(EndpointConfigWithDetails(**config_dict))

    return result


@router.put("/{config_id}", response_model=EndpointConfigResponse)
async def update_endpoint_configuration(
    config_id: UUID,
    update_data: EndpointConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a single endpoint configuration."""
    config = await endpoint_config_repository.get(db, config_id)
    if not config:
        raise NotFoundException("Endpoint Configuration", str(config_id))

    # Validate that if is_selected is True, mcp_description must be provided
    is_selected = update_data.is_selected if update_data.is_selected is not None else config.is_selected
    mcp_description = update_data.mcp_description if update_data.mcp_description is not None else config.mcp_description

    if is_selected and not mcp_description:
        raise BadRequestException("mcp_description is required when is_selected is true")

    # Update fields
    if update_data.is_selected is not None:
        config.is_selected = update_data.is_selected
    if update_data.mcp_tool_name is not None:
        config.mcp_tool_name = update_data.mcp_tool_name
    if update_data.mcp_description is not None:
        config.mcp_description = update_data.mcp_description
    if update_data.parameter_configurations is not None:
        # Convert to dict format for storage
        param_dicts = [param.model_dump() for param in update_data.parameter_configurations]
        config.parameter_configurations = {"parameters": param_dicts}

    updated_config = await endpoint_config_repository.update(db, config)
    await db.commit()

    # Transform parameter_configurations to list format for response
    param_configs = []
    if updated_config.parameter_configurations and "parameters" in updated_config.parameter_configurations:
        for param in updated_config.parameter_configurations["parameters"]:
            param_configs.append(ParameterConfigItem(**param))

    # Create response dict with transformed data
    config_dict = {
        "id": updated_config.id,
        "swagger_spec_id": updated_config.swagger_spec_id,
        "http_method": updated_config.http_method,
        "path": updated_config.path,
        "operation_id": updated_config.operation_id,
        "is_selected": updated_config.is_selected,
        "mcp_tool_name": updated_config.mcp_tool_name,
        "mcp_description": updated_config.mcp_description,
        "parameter_configurations": param_configs,
        "request_schema": updated_config.request_schema,
        "response_schema": updated_config.response_schema,
        "created_at": updated_config.created_at,
        "updated_at": updated_config.updated_at
    }

    return EndpointConfigResponse(**config_dict)


@router.post("/batch-update", response_model=List[EndpointConfigResponse])
async def batch_update_endpoint_configurations(
    updates: List[EndpointConfigBatchUpdate],
    db: AsyncSession = Depends(get_db)
):
    """Batch update multiple endpoint configurations."""
    updated_configs = []

    for update_item in updates:
        config = await endpoint_config_repository.get(db, update_item.endpoint_id)
        if not config:
            continue  # Skip non-existent configs

        # Validate selection requirement
        if update_item.is_selected and not update_item.mcp_description:
            raise BadRequestException(
                f"mcp_description is required for endpoint {config.http_method} {config.path}"
            )

        # Update fields
        config.is_selected = update_item.is_selected
        config.mcp_tool_name = update_item.mcp_tool_name
        config.mcp_description = update_item.mcp_description

        if update_item.parameter_configurations:
            param_dicts = [param.model_dump() for param in update_item.parameter_configurations]
            config.parameter_configurations = {"parameters": param_dicts}

        updated_config = await endpoint_config_repository.update(db, config)

        # Transform parameter_configurations to list format for response
        param_configs = []
        if updated_config.parameter_configurations and "parameters" in updated_config.parameter_configurations:
            for param in updated_config.parameter_configurations["parameters"]:
                param_configs.append(ParameterConfigItem(**param))

        # Create response dict with transformed data
        config_dict = {
            "id": updated_config.id,
            "swagger_spec_id": updated_config.swagger_spec_id,
            "http_method": updated_config.http_method,
            "path": updated_config.path,
            "operation_id": updated_config.operation_id,
            "is_selected": updated_config.is_selected,
            "mcp_tool_name": updated_config.mcp_tool_name,
            "mcp_description": updated_config.mcp_description,
            "parameter_configurations": param_configs,
            "request_schema": updated_config.request_schema,
            "response_schema": updated_config.response_schema,
            "created_at": updated_config.created_at,
            "updated_at": updated_config.updated_at
        }
        updated_configs.append(EndpointConfigResponse(**config_dict))

    await db.commit()
    return updated_configs


@router.get("/selected/{swagger_spec_id}", response_model=List[EndpointConfigResponse])
async def get_selected_configurations(
    swagger_spec_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get only selected endpoint configurations for a swagger spec."""
    # Verify swagger spec exists
    swagger_spec = await swagger_spec_repository.get(db, swagger_spec_id)
    if not swagger_spec:
        raise NotFoundException("Swagger Spec", str(swagger_spec_id))

    configs = await endpoint_config_repository.get_selected_by_swagger_spec(db, swagger_spec_id)

    # Transform parameter_configurations to list format for response
    result = []
    for config in configs:
        param_configs = []
        if config.parameter_configurations and "parameters" in config.parameter_configurations:
            for param in config.parameter_configurations["parameters"]:
                param_configs.append(ParameterConfigItem(**param))

        config_dict = {
            "id": config.id,
            "swagger_spec_id": config.swagger_spec_id,
            "http_method": config.http_method,
            "path": config.path,
            "operation_id": config.operation_id,
            "is_selected": config.is_selected,
            "mcp_tool_name": config.mcp_tool_name,
            "mcp_description": config.mcp_description,
            "parameter_configurations": param_configs,
            "request_schema": config.request_schema,
            "response_schema": config.response_schema,
            "created_at": config.created_at,
            "updated_at": config.updated_at
        }
        result.append(EndpointConfigResponse(**config_dict))

    return result


@router.delete("/{config_id}", status_code=204)
async def delete_endpoint_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete an endpoint configuration."""
    deleted = await endpoint_config_repository.delete(db, config_id)
    if not deleted:
        raise NotFoundException("Endpoint Configuration", str(config_id))
    return None
