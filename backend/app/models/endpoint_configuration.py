"""
EndpointConfiguration model.
"""

from sqlalchemy import String, Text, Boolean, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from typing import Dict, Any

from app.models.base import Base, TimestampMixin


class EndpointConfiguration(Base, TimestampMixin):
    """EndpointConfiguration model for user selections and descriptions."""

    __tablename__ = "endpoint_configurations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    swagger_spec_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("swagger_specs.id", ondelete="CASCADE"),
        nullable=False
    )

    # Endpoint identification
    http_method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    operation_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # User configuration
    is_selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mcp_tool_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mcp_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Parameter configurations (JSONB array)
    # Each param: {name, type, description, required, location, user_required}
    parameter_configurations: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Request/response schemas
    request_schema: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    response_schema: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    swagger_spec: Mapped["SwaggerSpec"] = relationship(
        "SwaggerSpec",
        back_populates="endpoint_configurations"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "http_method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD')",
            name="endpoint_configurations_method_check"
        ),
        UniqueConstraint(
            "swagger_spec_id",
            "http_method",
            "path",
            name="endpoint_configurations_unique_per_spec"
        ),
    )

    def __repr__(self) -> str:
        return f"<EndpointConfiguration(id={self.id}, method={self.http_method}, path={self.path})>"
