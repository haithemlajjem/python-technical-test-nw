from typing import Any



def test_list_sites_route(client: Any, monkeypatch: Any) -> None:
    """Test GET /sites returns an empty list."""

    async def mock_get_all_sites(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return []

    monkeypatch.setattr("routes.site.get_all_sites", mock_get_all_sites)

    response = client.get("/sites/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_site_route(
    client: Any, monkeypatch: Any, sample_site_data: dict[str, Any]
) -> None:
    """Test POST /sites creates a site and returns it with id."""

    async def mock_create_site(data: dict[str, Any], session: Any) -> dict[str, Any]:
        return {**data, "id": 1}

    monkeypatch.setattr("routes.site.create_site", mock_create_site)

    response = client.post("/sites/", json=sample_site_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_site_data["name"]
    assert "id" in data


def test_update_site_route(
    client: Any, monkeypatch: Any, sample_site_data: dict[str, Any]
) -> None:
    """Test PATCH /sites/{site_id} updates a site and returns full data."""

    async def mock_update_site(
        site_id: int, data: dict[str, Any], session: Any
    ) -> dict[str, Any]:
        updated = {**sample_site_data, **data, "id": site_id}
        return updated

    monkeypatch.setattr("routes.site.update_site", mock_update_site)

    update_data = {"name": "Updated Site"}
    response = client.patch("/sites/1", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Updated Site"


def test_delete_site_route(client: Any, monkeypatch: Any) -> None:
    """Test DELETE /sites/{site_id} returns 204 no content."""

    async def mock_delete_site(site_id: int, session: Any) -> None:
        return None

    monkeypatch.setattr("routes.site.delete_site", mock_delete_site)

    response = client.delete("/sites/1")
    assert response.status_code == 204
