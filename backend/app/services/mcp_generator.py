"""
MCP Server code generation service.
Generates complete Python MCP servers from configured endpoints.
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class MCPGeneratorService:
    """Service for generating MCP server code from endpoint configurations."""

    def __init__(self):
        self.indent = "    "

    async def generate_mcp_server(
        self,
        server_name: str,
        server_description: str,
        base_url: str,
        endpoints: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate complete MCP server code package.

        Args:
            server_name: Name of the MCP server
            server_description: Description of what the server does
            base_url: Base URL for API calls
            endpoints: List of endpoint configuration dictionaries
            config: Optional generation configuration

        Returns:
            Dictionary with generated files:
            {
                'main_code': Python code,
                'requirements': requirements.txt content,
                'readme': README.md content,
                'config_example': config.json.example content
            }
        """
        # Generate main Python code
        main_code = self._generate_main_code(
            server_name=server_name,
            server_description=server_description,
            base_url=base_url,
            endpoints=endpoints
        )

        # Generate requirements.txt
        requirements = self._generate_requirements()

        # Generate README.md
        readme = self._generate_readme(
            server_name=server_name,
            server_description=server_description,
            base_url=base_url,
            endpoints=endpoints
        )

        # Generate config example
        config_example = self._generate_config_example(base_url=base_url)

        return {
            'main_code': main_code,
            'requirements': requirements,
            'readme': readme,
            'config_example': config_example
        }

    def _generate_main_code(
        self,
        server_name: str,
        server_description: str,
        base_url: str,
        endpoints: List[Dict[str, Any]]
    ) -> str:
        """Generate the main Python MCP server code."""

        # Sanitize server name for Python identifier
        safe_server_name = self._sanitize_identifier(server_name)

        code_parts = []

        # Header and imports
        code_parts.append(f'''"""
{server_description or f'MCP Server for {server_name}'}

Auto-generated MCP server using FastMCP.
Generated: {datetime.utcnow().isoformat()}Z
"""

from typing import Any, Dict, Optional
import httpx
import logging
import sys
import json
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (never use stdout in stdio servers)
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(name="{safe_server_name}")

# API Configuration
BASE_URL = "{base_url or 'https://api.example.com'}"


async def make_api_request(
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Make HTTP request to the API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        path: API endpoint path
        params: Query parameters
        json_body: JSON request body
        headers: Additional headers

    Returns:
        JSON response as dictionary
    """
    url = f"{{BASE_URL}}{{path}}"

    if headers is None:
        headers = {{}}

    # Add authentication headers here if needed
    # headers["Authorization"] = f"Bearer {{YOUR_API_TOKEN}}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"Making {{method}} request to {{url}}")
            response = await client.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_body,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {{e.response.status_code}}: {{e.response.text}}")
            return {{
                "error": f"HTTP {{e.response.status_code}}",
                "message": str(e)
            }}
        except Exception as e:
            logger.error(f"Request error: {{str(e)}}")
            return {{
                "error": "Request failed",
                "message": str(e)
            }}

''')

        # Generate tool functions for each endpoint
        for endpoint in endpoints:
            tool_code = self._build_tool_function(endpoint)
            code_parts.append(tool_code)
            code_parts.append('\n')

        # Main entry point
        code_parts.append('''
def main():
    """Run the MCP server."""
    logger.info(f"Starting {server_name} MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
''')

        return ''.join(code_parts)

    def _build_tool_function(self, endpoint: Dict[str, Any]) -> str:
        """
        Build a single tool function from endpoint configuration.

        Args:
            endpoint: Endpoint configuration dictionary with:
                - http_method: HTTP method
                - path: API path
                - mcp_tool_name: Tool function name
                - mcp_description: Tool description
                - parameter_configurations: List of parameter configs
                - security_requirements: Security requirements info
        """
        method = endpoint.get('http_method', 'GET').upper()
        path = endpoint.get('path', '/')
        tool_name = endpoint.get('mcp_tool_name') or self._generate_tool_name(method, path)
        description = endpoint.get('mcp_description', f'{method} {path}')
        params = endpoint.get('parameter_configurations') or []
        security = endpoint.get('security_requirements') or {}

        # Sanitize tool name
        safe_tool_name = self._sanitize_identifier(tool_name)

        # Add authorization parameter if endpoint requires it
        if security.get('required', False):
            auth_param = {
                'name': 'Authorization',
                'location': 'header',
                'description': 'Authorization header (e.g., Bearer token)',
                'required': True,
                'user_required': True,
                'schema': {'type': 'string'}
            }
            # Add authorization param if not already in params
            if not any(p.get('name') == 'Authorization' and p.get('location') == 'header' for p in params):
                params = [auth_param] + params

        # Build function parameters
        func_params = self._build_function_parameters(params)

        # Build docstring
        docstring = self._build_docstring(description, params)

        # Build function body
        func_body = self._build_function_body(method, path, params)

        # Assemble function
        function_code = f'''@mcp.tool()
async def {safe_tool_name}({func_params}) -> str:
{docstring}
{func_body}
'''

        return function_code

    def _build_function_parameters(self, params: List[Dict[str, Any]]) -> str:
        """
        Build function parameter string with proper type hints.

        Uses user_required field to determine if parameter is Optional.
        If user_required=True: param_name: Type
        If user_required=False: param_name: Optional[Type] = None
        """
        if not params:
            return ""

        param_strs = []
        for param in params:
            name = param.get('name', 'param')
            safe_name = self._sanitize_identifier(name)

            # Get type from schema
            schema = param.get('schema', {})
            py_type = self._python_type_from_schema(schema)

            # Check user_required field (overrides original required)
            user_required = param.get('user_required', param.get('required', False))

            if user_required:
                # Required parameter
                param_strs.append(f"{safe_name}: {py_type}")
            else:
                # Optional parameter
                param_strs.append(f"{safe_name}: Optional[{py_type}] = None")

        return ", ".join(param_strs)

    def _build_docstring(self, description: str, params: List[Dict[str, Any]]) -> str:
        """Build function docstring."""
        lines = [f'{self.indent}"""']
        lines.append(f'{self.indent}{description}')

        if params:
            lines.append(f'{self.indent}')
            lines.append(f'{self.indent}Args:')
            for param in params:
                name = self._sanitize_identifier(param.get('name', 'param'))
                param_desc = param.get('description', 'No description')
                user_required = param.get('user_required', param.get('required', False))
                req_str = "required" if user_required else "optional"
                lines.append(f'{self.indent}{self.indent}{name}: {param_desc} ({req_str})')

        lines.append(f'{self.indent}')
        lines.append(f'{self.indent}Returns:')
        lines.append(f'{self.indent}{self.indent}JSON response as string')
        lines.append(f'{self.indent}"""')

        return '\n'.join(lines)

    def _build_function_body(
        self,
        method: str,
        path: str,
        params: List[Dict[str, Any]]
    ) -> str:
        """Build function body that makes API request."""
        lines = []

        # Separate parameters by location
        path_params = [p for p in params if p.get('location') == 'path']
        query_params = [p for p in params if p.get('location') == 'query']
        body_params = [p for p in params if p.get('location') == 'body']
        header_params = [p for p in params if p.get('location') == 'header']

        # Build path with path parameters
        if path_params:
            # Replace path parameters like {id} with f-string
            api_path = path
            for param in path_params:
                name = param.get('name')
                safe_name = self._sanitize_identifier(name)
                api_path = api_path.replace(f'{{{name}}}', f'{{{safe_name}}}')
            lines.append(f'{self.indent}path = f"{api_path}"')
        else:
            lines.append(f'{self.indent}path = "{path}"')

        # Build query parameters dict
        if query_params:
            lines.append(f'{self.indent}params = {{')
            for param in query_params:
                name = param.get('name')
                safe_name = self._sanitize_identifier(name)
                lines.append(f'{self.indent}{self.indent}"{name}": {safe_name},')
            lines.append(f'{self.indent}}}')
            lines.append(f'{self.indent}# Remove None values')
            lines.append(f'{self.indent}params = {{k: v for k, v in params.items() if v is not None}}')
        else:
            lines.append(f'{self.indent}params = None')

        # Build body
        if body_params:
            lines.append(f'{self.indent}json_body = {{')
            for param in body_params:
                name = param.get('name', 'body')
                safe_name = self._sanitize_identifier(name)
                # For body parameters, only include if not None
                lines.append(f'{self.indent}{self.indent}"{name}": {safe_name},')
            lines.append(f'{self.indent}}}')
            lines.append(f'{self.indent}# Remove None values')
            lines.append(f'{self.indent}json_body = {{k: v for k, v in json_body.items() if v is not None}}')
        else:
            lines.append(f'{self.indent}json_body = None')

        # Build headers
        if header_params:
            lines.append(f'{self.indent}headers = {{')
            for param in header_params:
                name = param.get('name')
                safe_name = self._sanitize_identifier(name)
                lines.append(f'{self.indent}{self.indent}"{name}": {safe_name},')
            lines.append(f'{self.indent}}}')
        else:
            lines.append(f'{self.indent}headers = None')

        # Make API request
        lines.append(f'{self.indent}')
        lines.append(f'{self.indent}result = await make_api_request(')
        lines.append(f'{self.indent}{self.indent}method="{method}",')
        lines.append(f'{self.indent}{self.indent}path=path,')
        lines.append(f'{self.indent}{self.indent}params=params,')
        lines.append(f'{self.indent}{self.indent}json_body=json_body,')
        lines.append(f'{self.indent}{self.indent}headers=headers')
        lines.append(f'{self.indent})')
        lines.append(f'{self.indent}')
        lines.append(f'{self.indent}return json.dumps(result, indent=2)')

        return '\n'.join(lines)

    def _python_type_from_schema(self, schema: Dict[str, Any]) -> str:
        """Convert JSON schema type to Python type hint."""
        schema_type = schema.get('type', 'string')

        type_map = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict'
        }

        return type_map.get(schema_type, 'str')

    def _sanitize_identifier(self, name: str) -> str:
        """Convert any string to valid Python identifier."""
        # Remove special characters, replace with underscore
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove leading digits
        name = re.sub(r'^[0-9]+', '', name)
        # Ensure not empty
        if not name:
            name = 'tool'
        # Ensure not a Python keyword
        if name in ['class', 'def', 'return', 'if', 'else', 'for', 'while', 'import', 'from', 'as']:
            name = f'{name}_'
        return name.lower()

    def _generate_tool_name(self, method: str, path: str) -> str:
        """Generate tool name from method and path."""
        # Example: GET /users/{id} -> get_users_id
        method_lower = method.lower()
        path_clean = re.sub(r'[^a-zA-Z0-9]', '_', path)
        path_clean = re.sub(r'_+', '_', path_clean).strip('_')
        return f"{method_lower}_{path_clean}"

    def _generate_requirements(self) -> str:
        """Generate requirements.txt content."""
        return """# MCP Server Requirements
mcp[cli]>=1.2.0
httpx>=0.26.0
pydantic>=2.5.0
"""

    def _generate_readme(
        self,
        server_name: str,
        server_description: str,
        base_url: str,
        endpoints: List[Dict[str, Any]]
    ) -> str:
        """Generate README.md content."""
        endpoint_list = '\n'.join([
            f"- `{e.get('http_method', 'GET')} {e.get('path', '/')}`: {e.get('mcp_description', 'No description')}"
            for e in endpoints
        ])

        return f"""# {server_name}

{server_description or 'Auto-generated MCP server'}

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your API credentials (if needed):
   - Edit `main.py` and add your API token/credentials in the `make_api_request` function

## Usage

Run the MCP server:
```bash
python main.py
```

The server will communicate via stdio transport.

## Configuration

Base URL: `{base_url or 'https://api.example.com'}`

## Available Tools

{endpoint_list}

## Authentication

If the API requires authentication, update the `make_api_request` function in `main.py`:

```python
headers["Authorization"] = f"Bearer {{YOUR_API_TOKEN}}"
```

## Generated

This MCP server was auto-generated by MCP Portal.
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""

    def _generate_config_example(self, base_url: str) -> str:
        """Generate config.json.example content."""
        config = {
            "base_url": base_url or "https://api.example.com",
            "api_token": "your-api-token-here",
            "timeout": 30
        }
        return json.dumps(config, indent=2)


# Create singleton instance
mcp_generator_service = MCPGeneratorService()
