from exceptions import BusinessLogicException
from infrastructure.models.group import Group, GroupTypeEnum
from infrastructure.models.site import CountryEnum, Site
from logger import get_logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = get_logger(__name__)


async def get_all_sites(
    session: AsyncSession,
    country: CountryEnum | None = None,
    sort_by: str | None = None,
    order: str = "asc",
) -> list[Site]:
    """
    Retrieve all sites with optional filtering and sorting.
    """
    logger.info(
        f"Fetching sites with filters - country: {country}, "
        "sort_by: {sort_by}, order: {order}"
    )
    query = select(Site).options(selectinload(Site.groups))  # Eager load groups

    if country:
        query = query.where(Site.country == country)

    if sort_by:
        sort_column = getattr(Site, sort_by, None)
        if not sort_column:
            raise BusinessLogicException(detail=f"Invalid sort field: {sort_by}")
        if order == "desc":
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)

    result = await session.execute(query)
    return result.scalars().all()


async def get_site_by_id(site_id: int, session: AsyncSession) -> Site:
    """
    Retrieve a single site by ID.
    """
    logger.info(f"Fetching site with ID: {site_id}")
    result = await session.execute(
        select(Site).options(selectinload(Site.groups)).where(Site.id == site_id)
    )
    site = result.scalars().first()
    if not site:
        raise BusinessLogicException(status_code=404, detail="Site not found")
    return site


async def create_site(data: dict, session: AsyncSession) -> Site:
    """
    Create a new site with business logic:
    - Only one French site can be installed per day.
    - Italian sites must be installed on weekends.
    - No site can be linked to a group of type 'group3'.
    """
    logger.info(f"Creating site with data: {data}")
    country = data.get("country")
    installation_date = data.get("installation_date")

    # Rule: Only one French site per day
    if country == CountryEnum.FR:
        query = select(Site).where(
            and_(
                Site.country == CountryEnum.FR,
                Site.installation_date == installation_date,
            )
        )
        result = await session.execute(query)
        if result.scalars().first():
            raise BusinessLogicException(
                detail=f"A French site already exists for date {installation_date}"
            )

    # Rule: Italian sites must be installed on weekends
    if country == CountryEnum.IT:
        if installation_date.weekday() not in (5, 6):  # 5=Saturday, 6=Sunday
            raise BusinessLogicException(
                detail="Italian sites must be installed on weekends."
            )

    # Rule: No group3 association
    group_ids = data.pop("group_ids", [])
    groups = []
    if group_ids:
        for gid in group_ids:
            result = await session.execute(select(Group).where(Group.id == gid))
            group = result.scalars().first()
            if not group:
                raise BusinessLogicException(detail=f"Group {gid} not found.")
            if group.type == GroupTypeEnum.group3:
                raise BusinessLogicException(detail="Cannot link site to group3.")
            groups.append(group)

    site = Site(**data)
    site.groups = groups

    session.add(site)
    await session.commit()

    result = await session.execute(
        select(Site).options(selectinload(Site.groups)).where(Site.id == site.id)
    )
    site = result.scalar_one()

    logger.info(f"Site created with ID: {site.id}")
    return site


async def update_site(site_id: int, data: dict, session: AsyncSession) -> Site:
    """
    Update an existing site with business logic.
    """
    logger.info(f"Updating site {site_id} with data: {data}")
    site = await get_site_by_id(site_id, session)

    if "country" in data or "installation_date" in data:
        # Apply country/date constraints again
        country = data.get("country", site.country)
        installation_date = data.get("installation_date", site.installation_date)

        if country == CountryEnum.FR:
            query = select(Site).where(
                and_(
                    Site.country == CountryEnum.FR,
                    Site.installation_date == installation_date,
                    Site.id != site.id,
                )
            )
            result = await session.execute(query)
            if result.scalars().first():
                raise BusinessLogicException(
                    detail=f"A French site already exists for date {installation_date}"
                )

        if country == CountryEnum.IT and installation_date.weekday() not in (5, 6):
            raise BusinessLogicException(
                detail="Italian sites must be installed on weekends."
            )

    for field, value in data.items():
        setattr(site, field, value)

    await session.commit()

    result = await session.execute(
        select(Site).options(selectinload(Site.groups)).where(Site.id == site.id)
    )
    site = result.scalar_one()
    return site


async def delete_site(site_id: int, session: AsyncSession) -> None:
    """
    Delete a site.
    """
    logger.info(f"Deleting site with ID: {site_id}")
    site = await get_site_by_id(site_id, session)
    await session.delete(site)
    await session.commit()
    logger.info(f"Site {site_id} deleted")
