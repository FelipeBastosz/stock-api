import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    register_payload = {
        "username": "joao_estoque",
        "email": "joao@estoque.com",
        "password": "senha_segura_123",
        "role": "operator",
    }
    resp = await client.post("/auth/register", json=register_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "joao_estoque"
    assert data["email"] == "joao@estoque.com"
    assert data["role"] == "operator"
    assert "hashed_password" not in data

    resp_dup = await client.post("/auth/register", json=register_payload)
    assert resp_dup.status_code == 409

    login_resp = await client.post(
        "/auth/token",
        json={"username": "joao_estoque", "password": "senha_segura_123"},
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    bad_login = await client.post(
        "/auth/token",
        json={"username": "joao_estoque", "password": "senha_errada"},
    )
    assert bad_login.status_code == 401

    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == "joao_estoque"

    unauth_resp = await client.get("/auth/me")
    assert unauth_resp.status_code == 401


@pytest.mark.asyncio
async def test_rbac_permissions_isolation(
    client: AsyncClient,
    auth_client: AsyncClient,
    operator_client: AsyncClient,
):
    unauth_resp = await client.post("/categories", json={"nome": "Não Autorizado"})
    assert unauth_resp.status_code == 401

    forbidden_create = await operator_client.post("/categories", json={"nome": "Tentativa Operador"})
    assert forbidden_create.status_code == 403
    assert "Acesso negado" in forbidden_create.json()["message"]

    forbidden_delete = await operator_client.delete("/categories/1")
    assert forbidden_delete.status_code == 403

    read_resp = await operator_client.get("/categories")
    assert read_resp.status_code == 200

    admin_resp = await auth_client.post("/categories", json={"nome": "Categoria Admin"})
    assert admin_resp.status_code == 201


@pytest.mark.asyncio
async def test_cors_preflight_headers(client: AsyncClient):
    resp = await client.options(
        "/products",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert resp.headers.get("access-control-allow-credentials") == "true"
