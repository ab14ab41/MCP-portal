"""
Swagger/OpenAPI parsing service using Prance.
Handles both OpenAPI 2.0 (Swagger) and 3.0+ specifications.
"""

from typing import Dict, List, Any, Literal, Tuple, Optional
import yaml
import json
import httpx
from prance import ResolvingParser, ValidationError

from app.utils.exceptions import InvalidSwaggerSpecException


class SwaggerParserService:
    """Service for parsing and extracting data from OpenAPI specifications."""

    async def parse_spec(
        self,
        content: str,
        format: Literal["json", "yaml"],
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Parse and validate OpenAPI specification.

        Args:
            content: The spec content as string
            format: Format of the content ('json' or 'yaml')
            validate: Whether to validate the spec

        Returns:
            Parsed and resolved specification dictionary

        Raises:
            InvalidSwaggerSpecException: If spec is invalid
        """
        try:
            # Parse content
            if format == "yaml":
                spec_dict = yaml.safe_load(content)
            else:
                spec_dict = json.loads(content)

            if not spec_dict:
                raise InvalidSwaggerSpecException("Empty specification")

            # Validate and resolve references
            if validate:
                try:
                    # Prance resolves $ref references automatically
                    parser = ResolvingParser(spec_string=content, backend='openapi-spec-validator')
                    return parser.specification
                except ValidationError as e:
                    raise InvalidSwaggerSpecException(str(e))
                except Exception as e:
                    # Fallback: try without validation if it fails
                    return spec_dict

            return spec_dict

        except yaml.YAMLError as e:
            raise InvalidSwaggerSpecException(f"YAML parsing error: {str(e)}")
        except json.JSONDecodeError as e:
            raise InvalidSwaggerSpecException(f"JSON parsing error: {str(e)}")
        except Exception as e:
            raise InvalidSwaggerSpecException(f"Failed to parse specification: {str(e)}")

    async def fetch_spec_from_url(self, url: str) -> Tuple[str, Literal["json", "yaml"]]:
        """
        Fetch OpenAPI specification from a URL.

        Args:
            url: URL to fetch the spec from

        Returns:
            Tuple of (content, format)

        Raises:
            InvalidSwaggerSpecException: If fetch fails
        """
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "").lower()
                content = response.text

                # Detect format from content type or content
                if "yaml" in content_type or "yml" in content_type:
                    format = "yaml"
                elif "json" in content_type:
                    format = "json"
                else:
                    # Try to detect from content
                    try:
                        json.loads(content)
                        format = "json"
                    except:
                        format = "yaml"

                return content, format

        except httpx.HTTPStatusError as e:
            raise InvalidSwaggerSpecException(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            error_msg = f"Failed to fetch from URL: {str(e)}"
            # Provide helpful hint for localhost URLs
            if "localhost" in url.lower() or "127.0.0.1" in url:
                error_msg += "\n\nNote: If your API is running on your local machine, use 'host.docker.internal' instead of 'localhost'.\nExample: http://host.docker.internal:5000/openapi.json"
            raise InvalidSwaggerSpecException(error_msg)
        except Exception as e:
            raise InvalidSwaggerSpecException(f"Unexpected error fetching spec: {str(e)}")

    def get_spec_version(self, spec: Dict[str, Any]) -> str:
        """
        Determine OpenAPI version from specification.

        Args:
            spec: Parsed specification dictionary

        Returns:
            Version string (e.g., '2.0', '3.0.0', '3.1.0')
        """
        if "openapi" in spec:
            return spec["openapi"]  # OpenAPI 3.x
        elif "swagger" in spec:
            return spec["swagger"]  # Swagger 2.0
        else:
            raise InvalidSwaggerSpecException("Unable to determine OpenAPI version")

    def extract_base_url(self, spec: Dict[str, Any]) -> Optional[str]:
        """
        Extract base URL from specification.

        Args:
            spec: Parsed specification dictionary

        Returns:
            Base URL or None
        """
        version = self.get_spec_version(spec)

        if version.startswith("3."):
            # OpenAPI 3.x: servers array
            servers = spec.get("servers", [])
            if servers and len(servers) > 0:
                return servers[0].get("url")
        else:
            # OpenAPI 2.0: host + basePath + schemes
            host = spec.get("host", "")
            base_path = spec.get("basePath", "")
            schemes = spec.get("schemes", ["https"])

            if host:
                scheme = schemes[0] if schemes else "https"
                return f"{scheme}://{host}{base_path}"

        return None

    async def extract_endpoints(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all endpoints from parsed specification.

        Args:
            spec: Parsed specification dictionary

        Returns:
            List of endpoint dictionaries
        """
        endpoints = []
        version = self.get_spec_version(spec)

        for path, path_item in spec.get("paths", {}).items():
            for method in ["get", "post", "put", "delete", "patch", "options", "head"]:
                if method in path_item:
                    operation = path_item[method]

                    # Extract regular parameters (query, path, header, etc.)
                    parameters = self._extract_parameters(operation, path_item, version)

                    # Extract body parameters from request body schema
                    body_params = self._extract_body_parameters(operation, version)
                    parameters.extend(body_params)

                    endpoint = {
                        "method": method.upper(),
                        "path": path,
                        "operation_id": operation.get("operationId"),
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "tags": operation.get("tags", []),
                        "parameters": parameters,
                        "request_body": self._extract_request_body(operation, version),
                        "responses": self._extract_responses(operation, version),
                        "deprecated": operation.get("deprecated", False)
                    }

                    endpoints.append(endpoint)

        return endpoints

    def _extract_parameters(
        self,
        operation: Dict,
        path_item: Dict,
        version: str
    ) -> List[Dict[str, Any]]:
        """
        Extract and normalize parameters for both OpenAPI versions.

        Args:
            operation: Operation object
            path_item: Path item object
            version: OpenAPI version

        Returns:
            List of normalized parameter dictionaries
        """
        parameters = []

        # Combine operation-level and path-level parameters
        all_params = path_item.get("parameters", []) + operation.get("parameters", [])

        for param in all_params:
            param_info = {
                "name": param.get("name"),
                "location": param.get("in"),  # path, query, header, cookie
                "description": param.get("description", ""),
                "required": param.get("required", False),
                "deprecated": param.get("deprecated", False),
                "schema": self._normalize_schema(param, version)
            }
            parameters.append(param_info)

        return parameters

    def _extract_request_body(self, operation: Dict, version: str) -> Optional[Dict[str, Any]]:
        """
        Extract request body schema (OpenAPI 3.0+) or body parameter (2.0).

        Args:
            operation: Operation object
            version: OpenAPI version

        Returns:
            Request body information or None
        """
        if version.startswith("3."):
            # OpenAPI 3.0+: requestBody
            request_body = operation.get("requestBody")
            if request_body:
                return {
                    "required": request_body.get("required", False),
                    "description": request_body.get("description", ""),
                    "content": request_body.get("content", {})
                }
        else:
            # OpenAPI 2.0: body parameter
            for param in operation.get("parameters", []):
                if param.get("in") == "body":
                    return {
                        "required": param.get("required", False),
                        "description": param.get("description", ""),
                        "schema": param.get("schema", {})
                    }

        return None

    def _extract_body_parameters(self, operation: Dict, version: str) -> List[Dict[str, Any]]:
        """
        Extract individual parameters from request body schema.
        Converts body schema properties into individual parameters.

        Args:
            operation: Operation object
            version: OpenAPI version

        Returns:
            List of body parameter dictionaries
        """
        body_params = []

        if version.startswith("3."):
            # OpenAPI 3.0+: requestBody with content
            request_body = operation.get("requestBody")
            if request_body:
                content = request_body.get("content", {})
                # Check for application/json content type
                json_content = content.get("application/json") or content.get("*/*")
                if json_content:
                    schema = json_content.get("schema", {})
                    body_params = self._extract_schema_properties(
                        schema,
                        request_body.get("required", False)
                    )
        else:
            # OpenAPI 2.0: body parameter with schema
            for param in operation.get("parameters", []):
                if param.get("in") == "body":
                    schema = param.get("schema", {})
                    body_params = self._extract_schema_properties(
                        schema,
                        param.get("required", False)
                    )
                    break

        return body_params

    def _extract_schema_properties(self, schema: Dict[str, Any], body_required: bool) -> List[Dict[str, Any]]:
        """
        Extract properties from a schema object and convert to parameters.

        Args:
            schema: Schema object containing properties
            body_required: Whether the entire body is required

        Returns:
            List of parameter dictionaries
        """
        params = []

        # Handle object schemas with properties
        if schema.get("type") == "object" and "properties" in schema:
            properties = schema.get("properties", {})
            required_props = schema.get("required", [])

            for prop_name, prop_schema in properties.items():
                param = {
                    "name": prop_name,
                    "location": "body",
                    "description": prop_schema.get("description", ""),
                    "required": prop_name in required_props,
                    "deprecated": prop_schema.get("deprecated", False),
                    "schema": {
                        "type": prop_schema.get("type", "string"),
                        "format": prop_schema.get("format"),
                        "enum": prop_schema.get("enum"),
                        "default": prop_schema.get("default"),
                        "example": prop_schema.get("example"),
                        "items": prop_schema.get("items"),
                        "properties": prop_schema.get("properties"),
                    }
                }
                params.append(param)

        # Handle array schemas
        elif schema.get("type") == "array":
            # For arrays, create a single parameter representing the array
            param = {
                "name": "body",
                "location": "body",
                "description": schema.get("description", "Request body array"),
                "required": body_required,
                "deprecated": schema.get("deprecated", False),
                "schema": {
                    "type": "array",
                    "items": schema.get("items", {}),
                }
            }
            params.append(param)

        # Handle primitive types (string, number, etc.)
        elif schema.get("type") in ["string", "number", "integer", "boolean"]:
            param = {
                "name": "body",
                "location": "body",
                "description": schema.get("description", "Request body"),
                "required": body_required,
                "deprecated": schema.get("deprecated", False),
                "schema": {
                    "type": schema.get("type"),
                    "format": schema.get("format"),
                }
            }
            params.append(param)

        return params

    def _extract_responses(self, operation: Dict, version: str) -> Dict[str, Any]:
        """
        Extract response schemas for all status codes.

        Args:
            operation: Operation object
            version: OpenAPI version

        Returns:
            Dictionary of response information by status code
        """
        responses = {}

        for status_code, response_obj in operation.get("responses", {}).items():
            responses[status_code] = {
                "description": response_obj.get("description", ""),
                "schema": self._extract_response_schema(response_obj, version)
            }

        return responses

    def _normalize_schema(self, param: Dict, version: str) -> Dict[str, Any]:
        """
        Normalize schema representation between OpenAPI versions.

        Args:
            param: Parameter object
            version: OpenAPI version

        Returns:
            Normalized schema dictionary
        """
        if version.startswith("3."):
            return param.get("schema", {})
        else:
            # OpenAPI 2.0: schema is inline
            return {
                "type": param.get("type"),
                "format": param.get("format"),
                "enum": param.get("enum"),
                "default": param.get("default"),
                "items": param.get("items")
            }

    def _extract_response_schema(self, response_obj: Dict, version: str) -> Dict[str, Any]:
        """
        Extract response schema based on OpenAPI version.

        Args:
            response_obj: Response object
            version: OpenAPI version

        Returns:
            Response schema dictionary
        """
        if version.startswith("3."):
            # OpenAPI 3.0+: content with media types
            content = response_obj.get("content", {})
            # Prefer application/json
            if "application/json" in content:
                return content["application/json"].get("schema", {})
            # Fallback to first content type
            for media_type, media_obj in content.items():
                return media_obj.get("schema", {})
        else:
            # OpenAPI 2.0: direct schema
            return response_obj.get("schema", {})

        return {}


# Create singleton instance
swagger_parser_service = SwaggerParserService()
