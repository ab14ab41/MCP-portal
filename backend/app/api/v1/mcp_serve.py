"""
MCP Server serving endpoints - Implements MCP protocol over HTTP.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from app.services.mcp_serving import mcp_serving_service

router = APIRouter(prefix="/mcp", tags=["mcp-serving"])


class MCPRequest(BaseModel):
    """MCP JSON-RPC request."""
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    """MCP JSON-RPC response."""
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


@router.post("/serve/{server_id}")
async def serve_mcp(server_id: str, request: MCPRequest):
    """
    Main MCP server endpoint implementing JSON-RPC protocol.

    Handles:
    - tools/list: List available tools
    - tools/call: Execute a tool
    - initialize: Initialize MCP session
    - ping: Health check

    Args:
        server_id: Server ID
        request: MCP JSON-RPC request

    Returns:
        MCP JSON-RPC response
    """
    # Check if server is registered
    if not mcp_serving_service.is_server_active(server_id):
        return MCPResponse(
            id=request.id,
            error={
                "code": -32000,
                "message": f"Server not deployed: {server_id}"
            }
        ).model_dump()

    # Handle different MCP methods
    try:
        if request.method == "initialize":
            return MCPResponse(
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": mcp_serving_service.get_server_info(server_id).get("server_name", "Unknown"),
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            ).model_dump()

        elif request.method == "tools/list":
            tools = mcp_serving_service.list_tools(server_id)
            return MCPResponse(
                id=request.id,
                result={"tools": tools}
            ).model_dump()

        elif request.method == "tools/call":
            if not request.params:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32602,
                        "message": "Missing params for tools/call"
                    }
                ).model_dump()

            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})

            if not tool_name:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32602,
                        "message": "Missing tool name"
                    }
                ).model_dump()

            # Execute the tool
            result = await mcp_serving_service.call_tool(
                server_id=server_id,
                tool_name=tool_name,
                arguments=arguments
            )

            # Check if there was an error in execution
            if "error" in result:
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error: {result.get('message', 'Unknown error')}"
                            }
                        ],
                        "isError": True
                    }
                ).model_dump()

            # Return successful result
            import json
            return MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            ).model_dump()

        elif request.method == "ping":
            return MCPResponse(
                id=request.id,
                result={"status": "ok"}
            ).model_dump()

        else:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {request.method}"
                }
            ).model_dump()

    except Exception as e:
        return MCPResponse(
            id=request.id,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        ).model_dump()


@router.get("/serve/{server_id}/info")
async def get_server_info(server_id: str):
    """
    Get information about a deployed MCP server.

    Args:
        server_id: Server ID

    Returns:
        Server information
    """
    if not mcp_serving_service.is_server_active(server_id):
        raise HTTPException(
            status_code=404,
            detail=f"Server not deployed: {server_id}"
        )

    info = mcp_serving_service.get_server_info(server_id)
    tools = mcp_serving_service.list_tools(server_id)

    return {
        "server_id": server_id,
        "server_name": info.get("server_name"),
        "base_url": info.get("base_url"),
        "registered_at": info.get("registered_at"),
        "tools_count": len(tools),
        "tools": tools
    }
