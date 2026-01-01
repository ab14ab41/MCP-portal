"""
Project API endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithStats
)
from app.repositories.project import project_repository
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project."""
    project = Project(
        name=project_data.name,
        description=project_data.description
    )
    created_project = await project_repository.create(db, project)
    return created_project


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    search: str = Query(None, description="Search by project name"),
    db: AsyncSession = Depends(get_db)
):
    """List all projects with pagination."""
    if search:
        projects = await project_repository.search_by_name(db, search, skip, limit)
    else:
        projects = await project_repository.get_all(db, skip, limit)
    return projects


@router.get("/{project_id}", response_model=ProjectWithStats)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a single project by ID with statistics."""
    project_data = await project_repository.get_with_stats(db, project_id)
    if not project_data:
        raise NotFoundException("Project", str(project_id))

    project = project_data["project"]
    return ProjectWithStats(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
        swagger_specs_count=project_data["swagger_specs_count"],
        generated_servers_count=project_data["generated_servers_count"]
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a project."""
    project = await project_repository.get(db, project_id)
    if not project:
        raise NotFoundException("Project", str(project_id))

    # Update fields if provided
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description

    updated_project = await project_repository.update(db, project)
    return updated_project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a project and all associated data."""
    deleted = await project_repository.delete(db, project_id)
    if not deleted:
        raise NotFoundException("Project", str(project_id))
    return None
