"""
SwaggerSpec model.
"""

from sqlalchemy import String, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from typing import List, Dict, Any

from app.models.base import Base, TimestampMixin


class SwaggerSpec(Base, TimestampMixin):
    """SwaggerSpec model for storing OpenAPI specifications."""

    __tablename__ = "swagger_specs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    # Spec metadata
    spec_version: Mapped[str] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    spec_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Original spec storage
    original_spec: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Parsed endpoints summary
    total_endpoints: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    endpoints_summary: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="swagger_specs")
    endpoint_configurations: Mapped[List["EndpointConfiguration"]] = relationship(
        "EndpointConfiguration",
        back_populates="swagger_spec",
        cascade="all, delete-orphan"
    )
    generated_servers: Mapped[List["GeneratedMCPServer"]] = relationship(
        "GeneratedMCPServer",
        back_populates="swagger_spec",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "spec_version IN ('2.0', '3.0.0', '3.0.1', '3.0.2', '3.0.3', '3.1.0')",
            name="swagger_specs_spec_version_check"
        ),
        CheckConstraint(
            "source_type IN ('upload', 'url', 'paste', 'endpoint')",
            name="swagger_specs_source_type_check"
        ),
    )

    def __repr__(self) -> str:
        return f"<SwaggerSpec(id={self.id}, title={self.title}, version={self.spec_version})>"
