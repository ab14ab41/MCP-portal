"""
EndpointConfiguration repository with specialized operations.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.models.endpoint_configuration import EndpointConfiguration
from app.repositories.base import BaseRepository


class EndpointConfigRepository(BaseRepository[EndpointConfiguration]):
    """Repository for EndpointConfiguration model."""

    def __init__(self):
        super().__init__(EndpointConfiguration)

    async def get_by_swagger_spec(
        self,
        db: AsyncSession,
        swagger_spec_id: UUID
    ) -> List[EndpointConfiguration]:
        """Get all endpoint configurations for a swagger spec."""
        result = await db.execute(
            select(EndpointConfiguration)
            .where(EndpointConfiguration.swagger_spec_id == swagger_spec_id)
            .order_by(EndpointConfiguration.path, EndpointConfiguration.http_method)
        )
        return list(result.scalars().all())

    async def get_selected_by_swagger_spec(
        self,
        db: AsyncSession,
        swagger_spec_id: UUID
    ) -> List[EndpointConfiguration]:
        """Get only selected endpoint configurations for a swagger spec."""
        result = await db.execute(
            select(EndpointConfiguration)
            .where(
                EndpointConfiguration.swagger_spec_id == swagger_spec_id,
                EndpointConfiguration.is_selected == True
            )
            .order_by(EndpointConfiguration.path, EndpointConfiguration.http_method)
        )
        return list(result.scalars().all())

    async def count_selected_by_swagger_spec(
        self,
        db: AsyncSession,
        swagger_spec_id: UUID
    ) -> int:
        """Count selected endpoints for a swagger spec."""
        result = await db.execute(
            select(func.count())
            .select_from(EndpointConfiguration)
            .where(
                EndpointConfiguration.swagger_spec_id == swagger_spec_id,
                EndpointConfiguration.is_selected == True
            )
        )
        return result.scalar() or 0

    async def get_by_spec_and_endpoint(
        self,
        db: AsyncSession,
        swagger_spec_id: UUID,
        http_method: str,
        path: str
    ) -> Optional[EndpointConfiguration]:
        """Get endpoint configuration by spec, method, and path."""
        result = await db.execute(
            select(EndpointConfiguration)
            .where(
                EndpointConfiguration.swagger_spec_id == swagger_spec_id,
                EndpointConfiguration.http_method == http_method,
                EndpointConfiguration.path == path
            )
        )
        return result.scalar_one_or_none()


# Create singleton instance
endpoint_config_repository = EndpointConfigRepository()
