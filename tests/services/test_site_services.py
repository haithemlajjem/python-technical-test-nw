from datetime import date
from typing import Any
from unittest.mock import MagicMock

import pytest
from exceptions import BusinessLogicException
from infrastructure.models.site import CountryEnum, Site
from services.site import create_site, delete_site, get_all_sites, get_site_by_id


def setup_mock_execute_returning_sites(
    mock_session: MagicMock, sites: list[Site]
) -> None:
    """Helper to mock session.execute().scalars().all() returning list of sites."""
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = sites
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result


def setup_mock_execute_returning_site_or_none(
    mock_session: MagicMock, site: Site | None
) -> None:
    """Helper to mock session.execute().scalars().first() returning one site or None."""
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = site
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result


@pytest.mark.asyncio
async def test_get_all_sites_no_filters(mock_session: MagicMock) -> None:
    """
    Test get_all_sites returns all sites without any filter.
    """
    sample_site = Site(
        id=1, name="SiteA", country=CountryEnum.FR, installation_date=date.today()
    )
    setup_mock_execute_returning_sites(mock_session, [sample_site])

    sites = await get_all_sites(session=mock_session)
    assert sites == [sample_site]


@pytest.mark.asyncio
async def test_get_site_by_id_found(mock_session: MagicMock) -> None:
    """
    Test get_site_by_id returns the site when found.
    """
    expected_site = Site(
        id=1, name="Found", country=CountryEnum.FR, installation_date=date.today()
    )
    setup_mock_execute_returning_site_or_none(mock_session, expected_site)

    result = await get_site_by_id(1, session=mock_session)
    assert result == expected_site


@pytest.mark.asyncio
async def test_get_site_by_id_not_found_raises(mock_session: MagicMock) -> None:
    """
    Test get_site_by_id raises BusinessLogicException when site not found.
    """
    setup_mock_execute_returning_site_or_none(mock_session, None)

    with pytest.raises(BusinessLogicException, match="Site not found") as exc_info:
        await get_site_by_id(999, session=mock_session)
    assert "Site not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_site_success(mock_session: MagicMock) -> None:
    """
    Test creating a site successfully when no conflicts exist.
    """
    site_data: dict[str, Any] = {
        "name": "Site B",
        "country": CountryEnum.FR,
        "installation_date": date.today(),
        "max_power_megawatt": 10.5,
        "min_power_megawatt": 2.0,
    }

    # Mock no conflict found on French date check
    no_conflict_mock = MagicMock()
    no_conflict_mock.scalars.return_value.first.return_value = None

    # Mock returned created site object
    created_site = Site(id=1, **site_data)
    fetch_created_mock = MagicMock()
    fetch_created_mock.scalar_one.return_value = created_site

    mock_session.execute.side_effect = [no_conflict_mock, fetch_created_mock]

    site = await create_site(site_data.copy(), session=mock_session)
    assert site.id == 1
    assert site.name == site_data["name"]


@pytest.mark.asyncio
async def test_create_site_french_site_already_exists_raises(
    mock_session: MagicMock,
) -> None:
    """
    Test that creating a French site on a conflicting date raises 
    BusinessLogicException.
    """
    site_data: dict[str, Any] = {
        "name": "Duplicate FR Site",
        "country": CountryEnum.FR,
        "installation_date": date.today(),
        "max_power_megawatt": 10.5,
        "min_power_megawatt": 2.0,
    }

    conflict_site = Site(id=99, **site_data)
    conflict_mock = MagicMock()
    conflict_mock.scalars.return_value.first.return_value = conflict_site
    mock_session.execute.return_value = conflict_mock

    with pytest.raises(
        BusinessLogicException, match="already exists for date"
    ) as exc_info:
        await create_site(site_data.copy(), session=mock_session)
    assert "already exists for date" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_site_italian_site_on_weekday_raises(
    mock_session: MagicMock,
) -> None:
    """
    Test that creating an Italian site on a weekday (not weekend) raises 
    BusinessLogicException.
    """
    weekday = date(2025, 7, 23)  # Wednesday

    site_data: dict[str, Any] = {
        "name": "Invalid IT Site",
        "country": CountryEnum.IT,
        "installation_date": weekday,
        "max_power_megawatt": 10.5,
        "min_power_megawatt": 2.0,
    }

    mock_session.execute.return_value = MagicMock()

    with pytest.raises(BusinessLogicException, match="weekends") as exc_info:
        await create_site(site_data.copy(), session=mock_session)
    assert "weekends" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_site(mock_session: MagicMock) -> None:
    """
    Test deleting a site triggers delete and commit on session.
    """
    site_to_delete = Site(
        id=1,
        name="DeleteMe",
        country=CountryEnum.FR,
        installation_date=date.today(),
        max_power_megawatt=10.5,
        min_power_megawatt=2.0,
    )

    setup_mock_execute_returning_site_or_none(mock_session, site_to_delete)

    await delete_site(1, session=mock_session)

    mock_session.delete.assert_called_once_with(site_to_delete)
    mock_session.commit.assert_called_once()
