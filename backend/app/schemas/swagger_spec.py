"""
Pydantic schemas for SwaggerSpec endpoints.
"""

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List, Literal


class SwaggerSpecBase(BaseModel):
    """Base swagger spec schema."""
    title: str = Field(..., description="API title from spec")
    spec_description: Optional[str] = Field(None, description="API description from spec")


class SwaggerSpecFromContent(BaseModel):
    """Schema for creating spec from pasted content."""
    project_id: UUID = Field(..., description="Project ID")
    content: str = Field(..., min_length=1, description="Swagger spec content (JSON or YAML)")
    format: Literal["json", "yaml"] = Field(..., description="Content format")


class SwaggerSpecFromURL(BaseModel):
    """Schema for creating spec from URL."""
    project_id: UUID = Field(..., description="Project ID")
    url: HttpUrl = Field(..., description="URL to fetch the spec from")


class SwaggerSpecResponse(SwaggerSpecBase):
    """Schema for swagger spec response."""
    id: UUID
    project_id: UUID
    spec_version: str
    base_url: Optional[str]
    source_type: str
    source_reference: Optional[str]
    total_endpoints: int
    endpoints_summary: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EndpointSummary(BaseModel):
    """Summary of a single endpoint."""
    method: str
    path: str
    operation_id: Optional[str]
    summary: str
    tags: List[str]
    deprecated: bool


class SwaggerSpecWithEndpoints(SwaggerSpecResponse):
    """Swagger spec with detailed endpoint information."""
    endpoints: List[Dict[str, Any]] = Field(default_factory=list, description="Full endpoint details")


class ValidationResult(BaseModel):
    """Result of spec validation."""
    valid: bool
    version: Optional[str] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class SwaggerSpecUpdateBaseURL(BaseModel):
    """Schema for updating swagger spec base URL."""
    base_url: str = Field(..., description="Base URL for the API (e.g., https://api.example.com)")
