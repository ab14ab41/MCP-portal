"""
Pydantic schemas for Endpoint Configuration endpoints.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List


class ParameterConfigItem(BaseModel):
    """Configuration for a single parameter."""
    name: str
    type: str
    location: str  # path, query, header, cookie
    description: str
    required: bool  # Original from spec
    user_required: bool  # User's choice (can override required)
    deprecated: bool = False
    schema: Dict[str, Any] = Field(default_factory=dict)


class EndpointConfigBase(BaseModel):
    """Base endpoint configuration schema."""
    is_selected: bool = False
    mcp_tool_name: Optional[str] = None
    mcp_description: Optional[str] = None
    parameter_configurations: Optional[List[ParameterConfigItem]] = None


class EndpointConfigCreate(EndpointConfigBase):
    """Schema for creating endpoint configuration."""
    swagger_spec_id: UUID
    http_method: str
    path: str
    operation_id: Optional[str] = None
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None


class EndpointConfigUpdate(BaseModel):
    """Schema for updating endpoint configuration."""
    is_selected: Optional[bool] = None
    mcp_tool_name: Optional[str] = None
    mcp_description: Optional[str] = None
    parameter_configurations: Optional[List[ParameterConfigItem]] = None


class EndpointConfigBatchUpdate(BaseModel):
    """Schema for batch updating multiple endpoint configurations."""
    endpoint_id: UUID
    is_selected: bool
    mcp_tool_name: Optional[str] = None
    mcp_description: Optional[str] = None
    parameter_configurations: Optional[List[ParameterConfigItem]] = None


class EndpointConfigResponse(BaseModel):
    """Schema for endpoint configuration response."""
    id: UUID
    swagger_spec_id: UUID
    http_method: str
    path: str
    operation_id: Optional[str]
    is_selected: bool
    mcp_tool_name: Optional[str]
    mcp_description: Optional[str]
    parameter_configurations: Optional[List[ParameterConfigItem]]
    request_schema: Optional[Dict[str, Any]]
    response_schema: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EndpointConfigWithDetails(EndpointConfigResponse):
    """Endpoint configuration with additional details from spec."""
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    deprecated: bool = False
