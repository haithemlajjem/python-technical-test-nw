import json
from typing import Any



def test_list_groups_route(client: Any, monkeypatch: Any) -> None:
    """Test GET /groups returns a list."""

    async def mock_get_all_groups(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return []

    monkeypatch.setattr("routes.group.get_all_groups", mock_get_all_groups)

    response = client.get("/groups/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_group_route(
    client: Any, monkeypatch: Any, sample_group_data: dict[str, Any]
) -> None:
    """Test POST /groups creates a group and returns it with id."""

    async def mock_create_group(data: dict[str, Any], session: Any) -> dict[str, Any]:
        return {**data, "id": 1}

    monkeypatch.setattr("routes.group.create_group", mock_create_group)

    response = client.post("/groups/", json=sample_group_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_group_data["name"]
    assert "id" in data


def test_update_group_route(client: Any, monkeypatch: Any) -> None:
    """Test PATCH /groups/{group_id} updates a group and returns full data."""

    async def mock_update_group(
        group_id: int, data: dict[str, Any], session: Any
    ) -> dict[str, Any]:
        return {
            "id": group_id,
            "name": data.get("name", "Default Group"),
            "type": "group1",
            "description": "Some description",
        }

    monkeypatch.setattr("routes.group.update_group", mock_update_group)

    update_data = {"name": "Updated Group"}
    response = client.patch("/groups/1", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Updated Group"


def test_delete_group_route(client: Any, monkeypatch: Any) -> None:
    """Test DELETE /groups/{group_id} returns 204 no content."""

    async def mock_delete_group(group_id: int, session: Any) -> None:
        return None

    monkeypatch.setattr("routes.group.delete_group", mock_delete_group)

    response = client.delete("/groups/1")
    assert response.status_code == 204


def test_add_child_groups_route(client: Any, monkeypatch: Any) -> None:
    """Test POST /groups/{group_id}/child-groups adds children and returns group."""

    async def mock_add_child_groups(
        group_id: int, child_group_ids: list[int], session: Any
    ) -> dict[str, Any]:
        return {
            "id": group_id,
            "name": "Group A",
            "type": "group1",
            "description": "Child groups added",
        }

    monkeypatch.setattr("routes.group.add_child_groups", mock_add_child_groups)

    response = client.post("/groups/1/child-groups", json=[2, 3])
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1


def test_remove_child_groups_route(client: Any, monkeypatch: Any) -> None:
    """Test DELETE /groups/{group_id}/child-groups removes children 
    and returns group."""

    async def mock_remove_child_groups(
        group_id: int, child_group_ids: list[int], session: Any
    ) -> dict[str, Any]:
        return {
            "id": group_id,
            "name": "Group A",
            "type": "group1",
            "description": "Child groups removed",
        }

    monkeypatch.setattr("routes.group.remove_child_groups", mock_remove_child_groups)

    response = client.request(
        "DELETE",
        "/groups/1/child-groups",
        content=json.dumps([2, 3]),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
