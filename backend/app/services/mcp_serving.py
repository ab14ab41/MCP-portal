"""
MCP Serving Service - Dynamically serves MCP endpoints over HTTP/SSE.
"""

import httpx
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPServingService:
    """Service for dynamically serving MCP endpoints."""

    def __init__(self):
        self.active_servers: Dict[str, Dict[str, Any]] = {}

    async def register_server(
        self,
        server_id: str,
        server_name: str,
        base_url: str,
        endpoints: List[Dict[str, Any]]
    ) -> bool:
        """
        Register an MCP server for serving.

        Args:
            server_id: Unique server ID
            server_name: Server name
            base_url: Base URL for API calls
            endpoints: List of endpoint configurations

        Returns:
            True if registered successfully
        """
        try:
            self.active_servers[server_id] = {
                "server_name": server_name,
                "base_url": base_url,
                "endpoints": endpoints,
                "registered_at": datetime.utcnow().isoformat()
            }
            logger.info(f"Registered MCP server: {server_id} ({server_name})")
            return True
        except Exception as e:
            logger.error(f"Failed to register MCP server {server_id}: {e}")
            return False

    def unregister_server(self, server_id: str) -> bool:
        """
        Unregister an MCP server.

        Args:
            server_id: Server ID to unregister

        Returns:
            True if unregistered successfully
        """
        if server_id in self.active_servers:
            del self.active_servers[server_id]
            logger.info(f"Unregistered MCP server: {server_id}")
            return True
        return False

    def is_server_active(self, server_id: str) -> bool:
        """Check if a server is currently active."""
        return server_id in self.active_servers

    def get_server_info(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered server."""
        return self.active_servers.get(server_id)

    def list_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """
        List all available tools for a server.

        Returns MCP tools list format.
        """
        server_info = self.active_servers.get(server_id)
        if not server_info:
            return []

        tools = []
        for endpoint in server_info["endpoints"]:
            tool_name = endpoint.get("mcp_tool_name") or self._generate_tool_name(
                endpoint["http_method"],
                endpoint["path"]
            )

            # Build input schema from parameters
            input_schema = self._build_input_schema(endpoint.get("parameter_configurations", []))

            tools.append({
                "name": tool_name,
                "description": endpoint.get("mcp_description", ""),
                "inputSchema": input_schema
            })

        return tools

    def _build_input_schema(self, params: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build JSON schema for tool input."""
        properties = {}
        required = []

        for param in params:
            name = param.get("name", "param")
            schema_type = param.get("schema", {}).get("type", "string")

            # Map schema types to JSON schema types
            json_type_map = {
                "string": "string",
                "integer": "number",
                "number": "number",
                "boolean": "boolean",
                "array": "array",
                "object": "object"
            }

            properties[name] = {
                "type": json_type_map.get(schema_type, "string"),
                "description": param.get("description", "")
            }

            # Check user_required field
            if param.get("user_required", param.get("required", False)):
                required.append(name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    async def call_mcp_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Alias for call_tool for compatibility."""
        return await self.call_tool(server_id, tool_name, arguments)

    async def call_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on a registered MCP server.

        Args:
            server_id: Server ID
            tool_name: Tool name to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        server_info = self.active_servers.get(server_id)
        if not server_info:
            return {
                "error": "Server not found",
                "message": f"No server registered with ID: {server_id}"
            }

        # Find the endpoint that matches the tool name
        endpoint = None
        for ep in server_info["endpoints"]:
            ep_tool_name = ep.get("mcp_tool_name") or self._generate_tool_name(
                ep["http_method"],
                ep["path"]
            )
            if ep_tool_name == tool_name:
                endpoint = ep
                break

        if not endpoint:
            return {
                "error": "Tool not found",
                "message": f"No tool named '{tool_name}' in this server"
            }

        # Execute the API call
        try:
            result = await self._execute_api_call(
                base_url=server_info["base_url"],
                endpoint=endpoint,
                arguments=arguments
            )
            return result
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "error": "Execution failed",
                "message": str(e)
            }

    async def _execute_api_call(
        self,
        base_url: str,
        endpoint: Dict[str, Any],
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the actual API call to the backend service."""
        method = endpoint["http_method"].upper()
        path = endpoint["path"]
        params = endpoint.get("parameter_configurations", [])

        # Separate parameters by location
        path_params = {p["name"]: arguments.get(p["name"]) for p in params if p.get("location") == "path" and p["name"] in arguments}
        query_params = {p["name"]: arguments.get(p["name"]) for p in params if p.get("location") == "query" and p["name"] in arguments}
        body_params = {p["name"]: arguments.get(p["name"]) for p in params if p.get("location") == "body" and p["name"] in arguments}
        header_params = {p["name"]: arguments.get(p["name"]) for p in params if p.get("location") == "header" and p["name"] in arguments}

        # Build the URL with path parameters
        url_path = path
        for param_name, param_value in path_params.items():
            url_path = url_path.replace(f"{{{param_name}}}", str(param_value))

        full_url = f"{base_url}{url_path}"

        # Prepare request
        json_body = body_params if body_params else None

        # Use longer timeout for AI/generation endpoints (5 minutes)
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=full_url,
                    params=query_params,
                    json=json_body,
                    headers=header_params
                )
                response.raise_for_status()

                # Try to parse as JSON
                try:
                    return response.json()
                except:
                    return {"result": response.text}

            except httpx.HTTPStatusError as e:
                return {
                    "error": f"HTTP {e.response.status_code}",
                    "message": e.response.text
                }
            except Exception as e:
                return {
                    "error": "Request failed",
                    "message": str(e)
                }

    def _generate_tool_name(self, method: str, path: str) -> str:
        """Generate tool name from method and path."""
        import re
        method_lower = method.lower()
        path_clean = re.sub(r'[^a-zA-Z0-9]', '_', path)
        path_clean = re.sub(r'_+', '_', path_clean).strip('_')
        return f"{method_lower}_{path_clean}"

    async def reload_deployed_servers_from_db(self, db):
        """
        Reload all deployed servers from database on startup.
        This ensures servers remain active after backend restarts.
        """
        from sqlalchemy import select
        from app.models.generated_mcp_server import GeneratedMCPServer
        from app.models.endpoint_configuration import EndpointConfiguration

        try:
            # Get all deployed servers
            result = await db.execute(
                select(GeneratedMCPServer).where(GeneratedMCPServer.is_deployed == True)
            )
            deployed_servers = result.scalars().all()

            logger.info(f"Reloading {len(deployed_servers)} deployed MCP servers...")

            for server in deployed_servers:
                # Get endpoint configurations for this server
                result = await db.execute(
                    select(EndpointConfiguration).where(
                        EndpointConfiguration.swagger_spec_id == server.swagger_spec_id,
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
                        'parameter_configurations': param_configs
                    })

                # Get base URL from swagger spec
                from app.models.swagger_spec import SwaggerSpec
                result = await db.execute(
                    select(SwaggerSpec).where(SwaggerSpec.id == server.swagger_spec_id)
                )
                spec = result.scalar_one_or_none()

                if spec:
                    # Re-register the server
                    await self.register_server(
                        server_id=str(server.id),
                        server_name=server.server_name,
                        base_url=spec.base_url or "",
                        endpoints=endpoints_data
                    )
                    logger.info(f"Reloaded MCP server: {server.server_name} (ID: {server.id})")

            logger.info(f"Successfully reloaded {len(deployed_servers)} MCP servers")

        except Exception as e:
            logger.error(f"Error reloading deployed servers: {e}")


# Create singleton instance
mcp_serving_service = MCPServingService()
