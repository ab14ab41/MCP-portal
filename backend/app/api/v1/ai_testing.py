"""
API endpoints for AI agent testing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import logging
import re

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.generated_mcp_server import GeneratedMCPServer
from app.models.endpoint_configuration import EndpointConfiguration
from app.services.ai_agent_tester import ai_agent_tester_service
from app.services.mcp_serving import mcp_serving_service

router = APIRouter(prefix="/ai-testing", tags=["ai-testing"])


def _generate_tool_name(method: str, path: str) -> str:
    """Generate tool name from method and path - matches mcp_serving.py logic."""
    method_lower = method.lower()
    path_clean = re.sub(r'[^a-zA-Z0-9]', '_', path)
    path_clean = re.sub(r'_+', '_', path_clean).strip('_')
    return f"{method_lower}_{path_clean}"


class TestMessageRequest(BaseModel):
    """Request model for testing with AI."""
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = None
    provider: Optional[str] = "anthropic"  # "anthropic" or "openai"
    model: Optional[str] = None  # Model name (e.g., "gpt-4o" for OpenAI)
    api_key: Optional[str] = None  # Override API key
    base_url: Optional[str] = None  # Override base URL (for OpenAI-compatible APIs)
    server_ids: Optional[List[str]] = None  # Optional array of server IDs to combine tools from
    custom_tools: Optional[List[Dict[str, Any]]] = None  # Optional custom tools to use
    authorization: Optional[str] = None  # Authorization header value (e.g., "Bearer token123")


class ToolExecutionRequest(BaseModel):
    """Request model for tool execution."""
    tool_call: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    provider: Optional[str] = "anthropic"  # "anthropic" or "openai"
    model: Optional[str] = None  # Model name (e.g., "gpt-4o" for OpenAI)
    api_key: Optional[str] = None  # Override API key
    base_url: Optional[str] = None  # Override base URL (for OpenAI-compatible APIs)
    server_ids: Optional[List[str]] = None  # Optional array of server IDs
    custom_tools: Optional[List[Dict[str, Any]]] = None  # Optional custom tools
    authorization: Optional[str] = None  # Authorization header value (e.g., "Bearer token123")


class TestMessageResponse(BaseModel):
    """Response model for AI test."""
    response: str
    tool_calls: List[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]
    stop_reason: str
    usage: Dict[str, int]
    requires_tool_execution: bool = False


class ToolExecutionResponse(BaseModel):
    """Response model for tool execution."""
    response: str
    tool_execution_result: Any
    additional_tool_calls: List[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]
    stop_reason: str
    usage: Dict[str, int]


@router.get("/deployed-servers/{server_id}/tools")
async def get_mcp_tools(
    server_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the list of tools available for a deployed MCP server.

    Args:
        server_id: The ID of the deployed MCP server
        db: Database session

    Returns:
        List of tools in Anthropic's tool format
    """
    # Get the deployed server
    result = await db.execute(
        select(GeneratedMCPServer).where(
            GeneratedMCPServer.id == server_id,
            GeneratedMCPServer.is_deployed == True
        )
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployed server not found"
        )

    # Get the endpoint configurations for this server
    result = await db.execute(
        select(EndpointConfiguration).where(
            EndpointConfiguration.swagger_spec_id == server.swagger_spec_id,
            EndpointConfiguration.is_selected == True
        )
    )
    endpoints = result.scalars().all()

    # Convert to Anthropic tool format
    tools = []
    for endpoint in endpoints:
        # Build input schema from parameter configurations
        properties = {}
        required = []

        if endpoint.parameter_configurations and "parameters" in endpoint.parameter_configurations:
            for param in endpoint.parameter_configurations["parameters"]:
                param_schema = {
                    "type": param.get("type", "string"),
                    "description": param.get("description", "")
                }

                # Add enum if present in the schema
                if param.get("schema") and param["schema"].get("enum"):
                    param_schema["enum"] = param["schema"]["enum"]

                # Add to properties
                properties[param["name"]] = param_schema

                # Add to required if user_required is True
                if param.get("user_required", False):
                    required.append(param["name"])

        # Build tool definition - use same name generation as mcp_serving.py
        tool_name = endpoint.mcp_tool_name or _generate_tool_name(
            endpoint.http_method,
            endpoint.path
        )

        tool = {
            "name": tool_name,
            "description": endpoint.mcp_description or f"{endpoint.http_method} {endpoint.path}",
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

        tools.append(tool)

    return {
        "server_id": str(server_id),
        "server_name": server.server_name,
        "tools": tools,
        "tool_count": len(tools)
    }


@router.post("/deployed-servers/{server_id}/test", response_model=TestMessageResponse)
async def test_with_ai(
    server_id: uuid.UUID,
    request: TestMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Test a deployed MCP server with an AI agent.
    Supports testing with multiple servers by passing server_ids or custom_tools.

    Args:
        server_id: The primary ID of the deployed MCP server (used for tool execution)
        request: The test request with message and conversation history
        db: Database session

    Returns:
        AI response with tool calls if any
    """
    # Get the deployed server
    result = await db.execute(
        select(GeneratedMCPServer).where(
            GeneratedMCPServer.id == server_id,
            GeneratedMCPServer.is_deployed == True
        )
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployed server not found"
        )

    # Get tools - use custom tools if provided, otherwise fetch from server(s)
    if request.custom_tools:
        tools = request.custom_tools
    elif request.server_ids:
        # Combine tools from multiple servers
        all_tools = []
        for sid in request.server_ids:
            try:
                tools_response = await get_mcp_tools(uuid.UUID(sid), db)
                all_tools.extend(tools_response["tools"])
            except:
                logger.warning(f"Failed to fetch tools from server {sid}")
        tools = all_tools
    else:
        # Default: get tools from primary server
        tools_response = await get_mcp_tools(server_id, db)
        tools = tools_response["tools"]

    try:
        # Test with selected provider
        if request.provider == "openai":
            # Use OpenAI-compatible API
            model = request.model or "gpt-4o"
            result = await ai_agent_tester_service.test_mcp_with_openai(
                server_id=str(server_id),
                server_name=server.server_name,
                message=request.message,
                conversation_history=request.conversation_history,
                mcp_tools=tools,
                model=model,
                api_key=request.api_key,
                base_url=request.base_url
            )
        else:
            # Default to Anthropic Claude
            result = await ai_agent_tester_service.test_mcp_with_claude(
                server_id=str(server_id),
                server_name=server.server_name,
                message=request.message,
                conversation_history=request.conversation_history,
                mcp_tools=tools,
                model=request.model,
                api_key=request.api_key
            )

        return TestMessageResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error testing with AI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing with AI: {str(e)}"
        )


@router.post("/deployed-servers/{server_id}/execute-tool", response_model=ToolExecutionResponse)
async def execute_tool(
    server_id: uuid.UUID,
    request: ToolExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a tool and get Claude's final response.

    Args:
        server_id: The ID of the deployed MCP server
        request: The tool execution request
        db: Database session

    Returns:
        Final AI response after tool execution
    """
    # Get the deployed server
    result = await db.execute(
        select(GeneratedMCPServer).where(
            GeneratedMCPServer.id == server_id,
            GeneratedMCPServer.is_deployed == True
        )
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployed server not found"
        )

    # Get tools - use custom tools if provided, otherwise fetch from server(s)
    if request.custom_tools:
        tools = request.custom_tools
    elif request.server_ids:
        # Combine tools from multiple servers
        all_tools = []
        for sid in request.server_ids:
            try:
                tools_response = await get_mcp_tools(uuid.UUID(sid), db)
                all_tools.extend(tools_response["tools"])
            except:
                logger.warning(f"Failed to fetch tools from server {sid}")
        tools = all_tools
    else:
        # Default: get tools from primary server
        tools_response = await get_mcp_tools(server_id, db)
        tools = tools_response["tools"]

    # Inject authorization into tool call arguments if provided
    tool_call = request.tool_call.copy()
    if request.authorization:
        if "input" not in tool_call:
            tool_call["input"] = {}
        # Only add Authorization if the tool has it as a parameter
        tool_name = tool_call.get("name", "")
        matching_tool = next((t for t in tools if t["name"] == tool_name), None)
        if matching_tool:
            tool_schema = matching_tool.get("input_schema", {})
            tool_properties = tool_schema.get("properties", {})
            if "Authorization" in tool_properties:
                tool_call["input"]["Authorization"] = request.authorization

    try:
        # Execute tool and continue conversation with selected provider
        if request.provider == "openai":
            # Use OpenAI-compatible API
            model = request.model or "gpt-4o"
            result = await ai_agent_tester_service.execute_tool_and_continue_openai(
                server_id=str(server_id),
                tool_call=tool_call,
                conversation_history=request.conversation_history,
                mcp_tools=tools,
                model=model,
                api_key=request.api_key,
                base_url=request.base_url
            )
        else:
            # Default to Anthropic Claude
            result = await ai_agent_tester_service.execute_tool_and_continue(
                server_id=str(server_id),
                tool_call=tool_call,
                conversation_history=request.conversation_history,
                mcp_tools=tools,
                model=request.model,
                api_key=request.api_key
            )

        return ToolExecutionResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing tool: {str(e)}"
        )
