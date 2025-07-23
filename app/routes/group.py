from fastapi import APIRouter, Depends, Query
from infrastructure.db import get_session
from infrastructure.models.group import GroupTypeEnum
from schemas.group import GroupCreate, GroupResponse, GroupUpdate
from services.group import (
    add_child_groups,
    create_group,
    delete_group,
    get_all_groups,
    remove_child_groups,
    update_group,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/", response_model=list[GroupResponse])
async def list_groups(
    group_type: GroupTypeEnum | None = Query(None, description="Filter groups by type"),
    sort_by: str | None = Query(
        None, description="Field to sort by (e.g., 'name' or 'id')"
    ),
    order: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve all groups with optional filters and sorting.
    """
    return await get_all_groups(session, group_type, sort_by, order)


@router.post("/", response_model=GroupResponse, status_code=201)
async def create_new_group(
    data: GroupCreate, session: AsyncSession = Depends(get_session)
):
    """
    Create a new group with business logic:
    """
    return await create_group(data.model_dump(), session)


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_existing_group(
    group_id: int, data: GroupUpdate, session: AsyncSession = Depends(get_session)
):
    """
    Update an existing group.
    """
    return await update_group(group_id, data.model_dump(exclude_unset=True), session)


@router.delete("/{group_id}", status_code=204)
async def delete_existing_group(
    group_id: int, session: AsyncSession = Depends(get_session)
):
    """
    Delete a group by ID.
    """
    await delete_group(group_id, session)


@router.post("/{group_id}/child-groups", response_model=GroupResponse)
async def add_child_groups_endpoint(
    group_id: int,
    child_group_ids: list[int],
    session: AsyncSession = Depends(get_session),
):
    """
    Add a child group to a group
    """
    return await add_child_groups(group_id, child_group_ids, session)


@router.delete("/{group_id}/child-groups", response_model=GroupResponse)
async def remove_child_groups_endpoint(
    group_id: int,
    child_group_ids: list[int],
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a child group from a group
    """
    return await remove_child_groups(group_id, child_group_ids, session)
