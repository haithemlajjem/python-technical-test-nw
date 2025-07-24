from fastapi import APIRouter, Depends, Query
from infrastructure.db import get_session
from schemas.site import SiteCreate, SiteResponse, SiteUpdate
from services.site import create_site, delete_site, get_all_sites, update_site
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/sites", tags=["Sites"])

session_dep = Depends(get_session)


@router.get("/", response_model=list[SiteResponse])
async def list_sites(
    country: str | None = Query(None, description="Filter by country (FR or IT)"),
    sort_by: str | None = Query("installation_date", description="Field to sort by"),
    order: str | None = Query("asc", description="Sort order: asc or desc"),
    session: AsyncSession = session_dep,
):
    """
    Retrieve all sites with optional filtering and sorting.
    """
    return await get_all_sites(session, country=country, sort_by=sort_by, order=order)


@router.post("/", response_model=SiteResponse, status_code=201)
async def create_new_site(data: SiteCreate, session: AsyncSession = session_dep):
    """
    Create a new site with all business rules applied.
    """
    return await create_site(data.model_dump(), session)


@router.patch("/{site_id}", response_model=SiteResponse)
async def update_existing_site(
    site_id: int, data: SiteUpdate, session: AsyncSession = session_dep
):
    """
    Update an existing site with validation and filters.
    """
    return await update_site(site_id, data.model_dump(exclude_unset=True), session)


@router.delete("/{site_id}", status_code=204)
async def delete_existing_site(site_id: int, session: AsyncSession = session_dep):
    """
    Delete a site by ID.
    """
    await delete_site(site_id, session)
