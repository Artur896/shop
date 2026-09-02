import pytest


async def _register(client, name, email):
    r = await client.post("/auth/register", json={"name": name, "email": email, "password": "supersecret1"})
    assert r.status_code == 201
    body = r.json()
    return body["access_token"], body["user"]["id"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_and_item_crud(client):
    token, _ = await _register(client, "Owner", "owner@example.com")

    created = await client.post("/lists", json={"name": "Supermercado", "description": "Compra semanal"}, headers=_auth(token))
    assert created.status_code == 201
    list_id = created.json()["id"]
    assert created.json()["my_role"] == "owner"

    item = await client.post(
        f"/lists/{list_id}/items",
        json={"name": "Leche", "quantity": 2, "unit": "litros", "category": "lacteos"},
        headers=_auth(token),
    )
    assert item.status_code == 201
    item_id = item.json()["id"]
    assert item.json()["is_completed"] is False

    completed = await client.post(f"/items/{item_id}/complete", headers=_auth(token))
    assert completed.status_code == 200
    assert completed.json()["is_completed"] is True

    detail = await client.get(f"/lists/{list_id}", headers=_auth(token))
    assert detail.json()["total_items"] == 1
    assert detail.json()["completed_items"] == 1

    deleted = await client.delete(f"/items/{item_id}", headers=_auth(token))
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_sharing_and_isolation(client):
    owner_token, _ = await _register(client, "Owner2", "owner2@example.com")
    viewer_token, viewer_id = await _register(client, "Viewer", "viewer@example.com")

    created = await client.post("/lists", json={"name": "Casa"}, headers=_auth(owner_token))
    list_id = created.json()["id"]

    # A non-member can't see the list at all — 404, not 403, so existence isn't leaked.
    forbidden = await client.get(f"/lists/{list_id}", headers=_auth(viewer_token))
    assert forbidden.status_code == 404

    invite = await client.post(
        f"/lists/{list_id}/members",
        json={"email": "viewer@example.com", "role": "viewer"},
        headers=_auth(owner_token),
    )
    assert invite.status_code == 201
    invitation_id = invite.json()["id"]

    invitations = await client.get("/invitations", headers=_auth(viewer_token))
    assert len(invitations.json()) == 1

    accepted = await client.post(f"/invitations/{invitation_id}/accept", headers=_auth(viewer_token))
    assert accepted.status_code == 200

    now_visible = await client.get(f"/lists/{list_id}", headers=_auth(viewer_token))
    assert now_visible.status_code == 200
    assert now_visible.json()["my_role"] == "viewer"

    # Viewer cannot add items.
    denied = await client.post(
        f"/lists/{list_id}/items", json={"name": "Pan"}, headers=_auth(viewer_token)
    )
    assert denied.status_code == 404

    # Viewer cannot delete the list either.
    denied_delete = await client.delete(f"/lists/{list_id}", headers=_auth(viewer_token))
    assert denied_delete.status_code == 404
