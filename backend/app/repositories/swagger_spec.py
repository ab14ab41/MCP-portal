"""
SwaggerSpec repository with specialized operations.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.swagger_spec import SwaggerSpec
from app.repositories.base import BaseRepository


class SwaggerSpecRepository(BaseRepository[SwaggerSpec]):
    """Repository for SwaggerSpec model."""

    def __init__(self):
        super().__init__(SwaggerSpec)

    async def get_by_project(
        self,
        db: AsyncSession,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SwaggerSpec]:
        """Get all swagger specs for a project."""
        result = await db.execute(
            select(SwaggerSpec)
            .where(SwaggerSpec.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .order_by(SwaggerSpec.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest_by_project(
        self,
        db: AsyncSession,
        project_id: UUID
    ) -> Optional[SwaggerSpec]:
        """Get the most recent swagger spec for a project."""
        result = await db.execute(
            select(SwaggerSpec)
            .where(SwaggerSpec.project_id == project_id)
            .order_by(SwaggerSpec.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


# Create singleton instance
swagger_spec_repository = SwaggerSpecRepository()
