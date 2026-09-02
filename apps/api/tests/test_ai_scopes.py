import pytest


async def _register(client, name, email):
    r = await client.post("/auth/register", json={"name": name, "email": email, "password": "supersecret1"})
    return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_ai_default_scopes_exclude_delete(client):
    user_token = await _register(client, "AIUser", "aiuser@example.com")

    connect = await client.post("/integrations/claude/connect", json={}, headers=_auth(user_token))
    assert connect.status_code == 200
    ai_token = connect.json()["token"]
    assert "items:delete" not in connect.json()["scopes"]

    created = await client.post(
        "/ai/lists",
        json={
            "name": "Carne asada",
            "items": [{"name": "Carbon"}, {"name": "Tortillas", "quantity": 2, "unit": "kg"}],
        },
        headers=_auth(ai_token),
    )
    assert created.status_code == 201
    body = created.json()
    assert body["total_items"] == 2
    list_id = body["id"]

    items = await client.get(f"/lists/{list_id}/items", headers=_auth(user_token))
    item_id = items.json()[0]["id"]

    # Default-connected AI integration has no items:delete scope.
    denied = await client.delete(f"/ai/items/{item_id}", headers=_auth(ai_token))
    assert denied.status_code == 403

    # It does have items:update, so completing an item works fine.
    completed = await client.post(f"/ai/items/{item_id}/complete", headers=_auth(ai_token))
    assert completed.status_code == 200

    activity = await client.get("/activity", headers=_auth(user_token))
    actions = [a["action"] for a in activity.json()]
    assert "create_list" in actions
    assert "complete_item" in actions


@pytest.mark.asyncio
async def test_ai_ambiguous_list_name(client):
    user_token = await _register(client, "AmbigUser", "ambig@example.com")
    connect = await client.post(
        "/integrations/chatgpt/connect", json={"scopes": ["lists:read", "lists:create"]}, headers=_auth(user_token)
    )
    ai_token = connect.json()["token"]

    await client.post("/ai/lists", json={"name": "Casa"}, headers=_auth(ai_token))
    await client.post("/ai/lists", json={"name": "Casa"}, headers=_auth(ai_token))

    result = await client.get("/ai/lists", params={"name": "Casa"}, headers=_auth(ai_token))
    assert result.status_code == 200
    assert result.json()["ambiguous"] is True
    assert len(result.json()["lists"]) == 2


@pytest.mark.asyncio
async def test_ai_token_revoked_on_disconnect(client):
    user_token = await _register(client, "RevokeUser", "revoke@example.com")
    connect = await client.post("/integrations/gemini/connect", json={}, headers=_auth(user_token))
    ai_token = connect.json()["token"]

    ok = await client.get("/ai/lists", headers=_auth(ai_token))
    assert ok.status_code == 200

    await client.delete("/integrations/gemini", headers=_auth(user_token))

    revoked = await client.get("/ai/lists", headers=_auth(ai_token))
    assert revoked.status_code == 401
