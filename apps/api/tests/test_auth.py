import pytest


@pytest.mark.asyncio
async def test_register_login_me(client):
    register = await client.post(
        "/auth/register",
        json={"name": "Ada", "email": "ada@example.com", "password": "supersecret1"},
    )
    assert register.status_code == 201
    tokens = register.json()
    assert tokens["user"]["email"] == "ada@example.com"

    duplicate = await client.post(
        "/auth/register",
        json={"name": "Ada", "email": "ada@example.com", "password": "supersecret1"},
    )
    assert duplicate.status_code == 409

    login = await client.post("/auth/login", json={"email": "ada@example.com", "password": "supersecret1"})
    assert login.status_code == 200
    access_token = login.json()["access_token"]

    bad_login = await client.post("/auth/login", json={"email": "ada@example.com", "password": "wrong"})
    assert bad_login.status_code == 401

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ada@example.com"


@pytest.mark.asyncio
async def test_refresh_flow(client):
    register = await client.post(
        "/auth/register",
        json={"name": "Grace", "email": "grace@example.com", "password": "supersecret1"},
    )
    refresh_token = register.json()["refresh_token"]

    refreshed = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200
    assert "access_token" in refreshed.json()

    invalid = await client.post("/auth/refresh", json={"refresh_token": "garbage"})
    assert invalid.status_code == 401
