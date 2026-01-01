"""
GeneratedMCPServer model.
"""

from sqlalchemy import String, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from typing import Dict, Any

from app.models.base import Base, TimestampMixin


class GeneratedMCPServer(Base, TimestampMixin):
    """GeneratedMCPServer model for final output storage."""

    __tablename__ = "generated_mcp_servers"

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

    # Generation metadata
    server_name: Mapped[str] = mapped_column(String(255), nullable=False)
    server_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_config: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Generated code
    python_code: Mapped[str] = mapped_column(Text, nullable=False)
    requirements_txt: Mapped[str] = mapped_column(Text, nullable=False)

    # Additional files (optional)
    additional_files: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Statistics
    selected_endpoints_count: Mapped[int] = mapped_column(Integer, nullable=False)
    lines_of_code: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Status tracking
    generation_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending"
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Deployment tracking
    is_deployed: Mapped[bool] = mapped_column(nullable=False, default=False)
    deployed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    deployment_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Download tracking
    downloaded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    swagger_spec: Mapped["SwaggerSpec"] = relationship(
        "SwaggerSpec",
        back_populates="generated_servers"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "generation_status IN ('pending', 'generating', 'completed', 'failed')",
            name="generated_mcp_servers_status_check"
        ),
    )

    def __repr__(self) -> str:
        return f"<GeneratedMCPServer(id={self.id}, name={self.server_name}, status={self.generation_status})>"
