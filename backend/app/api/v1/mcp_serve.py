"""
MCP Server serving endpoints - Implements MCP protocol over HTTP.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import json

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
async def serve_mcp(server_id: str, raw_request: Request):
    """
    Main MCP server endpoint implementing JSON-RPC protocol with streamable HTTP support.

    Handles:
    - tools/list: List available tools
    - tools/call: Execute a tool
    - initialize: Initialize MCP session
    - ping: Health check

    Args:
        server_id: Server ID
        raw_request: FastAPI Request object

    Returns:
        SSE (Server-Sent Events) response for streamable HTTP
    """
    # Parse request body
    try:
        body = await raw_request.json()
        request = MCPRequest(**body)
    except Exception as e:
        error_response = MCPResponse(
            id=None,
            error={
                "code": -32700,
                "message": f"Parse error: {str(e)}"
            }
        )
        # Return as SSE (Server-Sent Events)
        sse_data = f"data: {json.dumps(error_response.model_dump(exclude_none=True))}\n\n"
        return StreamingResponse(
            iter([sse_data]),
            media_type="text/event-stream"
        )

    # Check if server is registered
    if not mcp_serving_service.is_server_active(server_id):
        error_response = MCPResponse(
            id=request.id,
            error={
                "code": -32000,
                "message": f"Server not deployed: {server_id}"
            }
        )
        # Return as SSE (Server-Sent Events)
        sse_data = f"data: {json.dumps(error_response.model_dump(exclude_none=True))}\n\n"
        return StreamingResponse(
            iter([sse_data]),
            media_type="text/event-stream"
        )

    # Handle different MCP methods
    try:
        if request.method == "initialize":
            response = MCPResponse(
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
            )
            # Return as SSE (Server-Sent Events)
            sse_data = f"data: {json.dumps(response.model_dump(exclude_none=True))}\n\n"
            return StreamingResponse(
                iter([sse_data]),
                media_type="text/event-stream"
            )

        elif request.method == "tools/list":
            tools = mcp_serving_service.list_tools(server_id)
            response = MCPResponse(
                id=request.id,
                result={"tools": tools}
            )
            # Return as SSE (Server-Sent Events)
            sse_data = f"data: {json.dumps(response.model_dump(exclude_none=True))}\n\n"
            return StreamingResponse(
                iter([sse_data]),
                media_type="text/event-stream"
            )

        elif request.method == "tools/call":
            if not request.params:
                response = MCPResponse(
                    id=request.id,
                    error={
                        "code": -32602,
                        "message": "Missing params for tools/call"
                    }
                )
                sse_data = f"data: {json.dumps(response.model_dump(exclude_none=True))}\n\n"
                return StreamingResponse(
                    iter([sse_data]),
                    media_type="text/event-stream"
                )

            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})

            if not tool_name:
                response = MCPResponse(
                    id=request.id,
                    error={
                        "code": -32602,
                        "message": "Missing tool name"
                    }
                )
                sse_data = f"data: {json.dumps(response.model_dump(exclude_none=True))}\n\n"
                return StreamingResponse(
                    iter([sse_data]),
                    media_type="text/event-stream"
                )

            # Execute the tool
            result = await mcp_serving_service.call_tool(
                server_id=server_id,
                tool_name=tool_name,
                arguments=arguments
            )

            # Check if there was an error in execution
            if "error" in result:
                response = MCPResponse(
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
                )
                sse_data = f"data: {json.dumps(response.model_dump(exclude_none=True))}\n\n"
                return StreamingResponse(
                    iter([sse_data]),
                    media_type="text/event-stream"
                )

            # Return successful result
            response = MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            )
            sse_data = f"data: {json.dumps(response.model_dump(exclude_none=True))}\n\n"
            return StreamingResponse(
                iter([sse_data]),
                media_type="text/event-stream"
            )

        elif request.method == "ping":
            response = MCPResponse(
                id=request.id,
                result={"status": "ok"}
            )
            sse_data = f"data: {json.dumps(response.model_dump(exclude_none=True))}\n\n"
            return StreamingResponse(
                iter([sse_data]),
                media_type="text/event-stream"
            )

        else:
            response = MCPResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {request.method}"
                }
            )
            sse_data = f"data: {json.dumps(response.model_dump(exclude_none=True))}\n\n"
            return StreamingResponse(
                iter([sse_data]),
                media_type="text/event-stream"
            )

    except Exception as e:
        response = MCPResponse(
            id=request.id,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        )
        sse_data = f"data: {json.dumps(response.model_dump(exclude_none=True))}\n\n"
        return StreamingResponse(
            iter([sse_data]),
            media_type="text/event-stream"
        )


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
