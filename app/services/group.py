from exceptions import BusinessLogicException
from infrastructure.models.group import Group, GroupTypeEnum
from logger import get_logger
from schemas.group import GroupResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = get_logger(__name__)


async def get_all_groups(
    session: AsyncSession,
    group_type: GroupTypeEnum | None = None,
    sort_by: str | None = None,
    order: str = "asc",
) -> list[GroupResponse]:
    logger.info(
        f"Fetching groups with filters - type: {group_type}, "
        f"sort_by: {sort_by}, order: {order}"
    )

    query = select(Group).options(
        selectinload(Group.sites), selectinload(Group.child_groups)
    )

    if group_type:
        query = query.where(Group.type == group_type)

    if sort_by:
        sort_column = getattr(Group, sort_by, None)
        if not sort_column:
            raise BusinessLogicException(detail=f"Invalid sort field: {sort_by}")
        if order == "desc":
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

    result = await session.execute(query)
    groups = result.scalars().all()
    return [GroupResponse.from_orm(g) for g in groups]


async def create_group(data: dict, session: AsyncSession) -> GroupResponse:
    logger.info(f"Creating group with data: {data}")
    group = Group(**data)
    session.add(group)
    await session.commit()
    await session.refresh(group, attribute_names=["sites", "child_groups"])
    logger.info(f"Group created with ID: {group.id}")
    return GroupResponse.from_orm(group)


async def update_group(
    group_id: int, data: dict, session: AsyncSession
) -> GroupResponse:
    logger.info(f"Updating group {group_id} with data: {data}")
    result = await session.execute(
        select(Group)
        .where(Group.id == group_id)
        .options(selectinload(Group.sites), selectinload(Group.child_groups))
    )
    group = result.scalars().first()
    if not group:
        raise BusinessLogicException(status_code=404, detail="Group not found")

    for field, value in data.items():
        setattr(group, field, value)

    await session.commit()
    await session.refresh(group, attribute_names=["sites", "child_groups"])
    return GroupResponse.from_orm(group)


async def delete_group(group_id: int, session: AsyncSession) -> None:
    logger.info(f"Deleting group with ID: {group_id}")
    result = await session.execute(select(Group).where(Group.id == group_id))
    group = result.scalars().first()
    if not group:
        raise BusinessLogicException(status_code=404, detail="Group not found")

    await session.delete(group)
    await session.commit()
    logger.info(f"Group {group_id} deleted")


async def add_child_groups(
    group_id: int, child_group_ids: list[int], session: AsyncSession
) -> GroupResponse:
    logger.info(f"Adding child groups {child_group_ids} to group {group_id}")

    # Load parent group
    result = await session.execute(
        select(Group)
        .where(Group.id == group_id)
        .options(selectinload(Group.child_groups))
    )
    group = result.scalars().first()
    if not group:
        raise BusinessLogicException(status_code=404, detail="Group not found")

    # Load child groups and validate
    result = await session.execute(select(Group).where(Group.id.in_(child_group_ids)))
    child_groups = result.scalars().all()

    if len(child_groups) != len(child_group_ids):
        raise BusinessLogicException(detail="Some child groups not found.")


    # Add new child groups
    for child in child_groups:
        if child not in group.child_groups:
            group.child_groups.append(child)

    await session.commit()
    await session.refresh(group, attribute_names=["sites", "child_groups"])
    return GroupResponse.from_orm(group)


async def remove_child_groups(
    group_id: int, child_group_ids: list[int], session: AsyncSession
) -> GroupResponse:
    logger.info(f"Removing child groups {child_group_ids} from group {group_id}")

    result = await session.execute(
        select(Group)
        .where(Group.id == group_id)
        .options(selectinload(Group.child_groups))
    )
    group = result.scalars().first()
    if not group:
        raise BusinessLogicException(status_code=404, detail="Group not found")

    group.child_groups = [c for c in group.child_groups if c.id not in child_group_ids]

    await session.commit()
    await session.refresh(group, attribute_names=["sites", "child_groups"])
    return GroupResponse.from_orm(group)
