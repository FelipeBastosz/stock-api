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


@pytest.mark.asyncio
async def test_rbac_permissions_isolation(
    client: AsyncClient,
    auth_client: AsyncClient,
    operator_client: AsyncClient,
):
    # 1. Requisição anônima (sem token) a rota administrativa deve retornar 401
    unauth_resp = await client.post("/categories", json={"nome": "Não Autorizado"})
    assert unauth_resp.status_code == 401

    # 2. Operador tentando criar categoria (ação exclusiva de admin) deve retornar 403
    forbidden_create = await operator_client.post("/categories", json={"nome": "Tentativa Operador"})
    assert forbidden_create.status_code == 403
    assert "Acesso negado" in forbidden_create.json()["message"]

    # 3. Operador tentando excluir categoria deve retornar 403
    forbidden_delete = await operator_client.delete("/categories/1")
    assert forbidden_delete.status_code == 403

    # 4. Operador pode ler categorias (rota pública)
    read_resp = await operator_client.get("/categories")
    assert read_resp.status_code == 200

    # 5. Administrador consegue criar categoria com sucesso (201)
    admin_resp = await auth_client.post("/categories", json={"nome": "Categoria Admin"})
    assert admin_resp.status_code == 201
