import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    # 1. Registrar usuário operador
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

    # 2. Rejeitar duplicidade de username
    resp_dup = await client.post("/auth/register", json=register_payload)
    assert resp_dup.status_code == 409

    # 3. Login com senha correta via endpoint JSON
    login_resp = await client.post(
        "/auth/token",
        json={"username": "joao_estoque", "password": "senha_segura_123"},
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # 4. Login com senha incorreta
    bad_login = await client.post(
        "/auth/token",
        json={"username": "joao_estoque", "password": "senha_errada"},
    )
    assert bad_login.status_code == 401

    # 5. Acessar /auth/me com token válido
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == "joao_estoque"

    # 6. Acessar /auth/me sem token
    unauth_resp = await client.get("/auth/me")
    assert unauth_resp.status_code == 401
