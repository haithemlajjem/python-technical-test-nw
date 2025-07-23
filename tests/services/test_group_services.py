from unittest.mock import MagicMock

import pytest
from infrastructure.models.group import Group, GroupTypeEnum
from schemas.group import GroupResponse
from services.group import (
    delete_group,
    get_all_groups,
    remove_child_groups,
    update_group,
)


def setup_execute_scalars_all_returning_groups(
    mock_session: MagicMock, groups: list[Group]
) -> None:
    """Helper to mock execute().scalars().all() returning groups."""
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = groups
    execute_mock = MagicMock()
    execute_mock.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_mock


def setup_execute_scalars_first_returning(
    mock_session: MagicMock, obj: Group | None
) -> None:
    """Helper to mock execute().scalars().first() returning a single Group or None."""
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = obj
    execute_mock = MagicMock()
    execute_mock.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_mock


@pytest.mark.asyncio
async def test_get_all_groups(mock_session: MagicMock) -> None:
    """
    Test that retrieving all groups returns the expected list of GroupResponse schemas.
    """
    group = Group(
        id=1, name="Group A", type=GroupTypeEnum.group1, child_groups=[], sites=[]
    )
    setup_execute_scalars_all_returning_groups(mock_session, [group])

    groups = await get_all_groups(session=mock_session)
    expected = [GroupResponse.from_orm(group)]

    assert groups == expected


@pytest.mark.asyncio
async def test_update_group(mock_session: MagicMock) -> None:
    """
    Test updating a group modifies its fields and commits the session.
    """
    existing_group = Group(id=1, name="Old Name", type=GroupTypeEnum.group1)
    update_data = {"name": "Updated Name"}

    # Mock first execute call: fetching existing group
    scalars_mock = MagicMock()
    scalars_mock.first.return_value = existing_group
    execute_result_1 = MagicMock()
    execute_result_1.scalars.return_value = scalars_mock

    # Mock second execute call: returning updated group
    execute_result_2 = MagicMock()
    execute_result_2.scalar_one.return_value = existing_group

    # Setup sequential side_effect for execute calls
    mock_session.execute.side_effect = [execute_result_1, execute_result_2]

    updated_group = await update_group(1, update_data, session=mock_session)

    # Confirm the ORM object was updated
    assert updated_group.name == update_data["name"]
    # Confirm session commit was called
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_group(mock_session: MagicMock) -> None:
    """
    Test deleting a group removes it from session and commits.
    """
    group_to_delete = Group(id=1, name="DeleteMe", type=GroupTypeEnum.group1)
    setup_execute_scalars_first_returning(mock_session, group_to_delete)

    await delete_group(1, session=mock_session)

    mock_session.delete.assert_called_once_with(group_to_delete)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_remove_child_groups(mock_session: MagicMock) -> None:
    """
    Test that removing child groups clears them from the parent and commits.
    """
    # Setup parent and children
    child1 = Group(id=2, name="Child1", type=GroupTypeEnum.group2)
    child2 = Group(id=3, name="Child2", type=GroupTypeEnum.group1)
    parent = Group(id=1, name="Parent", type=GroupTypeEnum.group1)
    parent.child_groups = [child1, child2]

    # Mock execute().scalars().first() calls returning parent, then children
    scalars_mock = MagicMock()
    scalars_mock.first.side_effect = [parent, child1, child2]
    execute_mock = MagicMock()
    execute_mock.scalars.return_value = scalars_mock

    # Mock final execute returning updated parent
    final_execute_mock = MagicMock()
    final_execute_mock.scalar_one.return_value = parent

    # Execute side effects list:
    mock_session.execute.side_effect = [
        execute_mock,
        execute_mock,
        execute_mock,
        final_execute_mock,
    ]

    result = await remove_child_groups(1, [2, 3], session=mock_session)

    # After removal, child_groups list should be empty
    assert result.id == 1
    assert parent.child_groups == []

    mock_session.commit.assert_called_once()
