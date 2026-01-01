"""
Project repository with specialized operations.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.models.project import Project
from app.models.swagger_spec import SwaggerSpec
from app.models.generated_mcp_server import GeneratedMCPServer
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model."""

    def __init__(self):
        super().__init__(Project)

    async def get_with_stats(self, db: AsyncSession, id: UUID) -> Optional[dict]:
        """Get project with statistics."""
        project = await self.get(db, id)
        if not project:
            return None

        # Count swagger specs
        specs_count_query = select(func.count()).select_from(SwaggerSpec).where(
            SwaggerSpec.project_id == id
        )
        specs_count = await db.scalar(specs_count_query)

        # Count generated servers across all specs
        servers_count_query = (
            select(func.count())
            .select_from(GeneratedMCPServer)
            .join(SwaggerSpec)
            .where(SwaggerSpec.project_id == id)
        )
        servers_count = await db.scalar(servers_count_query)

        return {
            "project": project,
            "swagger_specs_count": specs_count or 0,
            "generated_servers_count": servers_count or 0
        }

    async def search_by_name(
        self,
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """Search projects by name."""
        result = await db.execute(
            select(Project)
            .where(Project.name.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())


# Create singleton instance
project_repository = ProjectRepository()
