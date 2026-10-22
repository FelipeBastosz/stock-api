import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_category_lifecycle_and_business_rules(auth_client: AsyncClient):
    # 1. Criar categoria
    resp = await auth_client.post("/categories", json={"nome": "Informática"})
    assert resp.status_code == 201
    cat = resp.json()
    assert cat["id"] is not None
    assert cat["nome"] == "Informática"
    cat_id = cat["id"]

    # 2. Conflito por duplicidade de nome (409)
    resp_dup = await auth_client.post("/categories", json={"nome": "Informática"})
    assert resp_dup.status_code == 409

    # 3. Listar categorias
    resp_list = await auth_client.get("/categories")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 1

    # 4. Atualizar categoria
    resp_up = await auth_client.put(f"/categories/{cat_id}", json={"nome": "Informática e Games"})
    assert resp_up.status_code == 200
    assert resp_up.json()["nome"] == "Informática e Games"

    # 5. Excluir categoria sem vínculos (204)
    del_resp = await auth_client.delete(f"/categories/{cat_id}")
    assert del_resp.status_code == 204

    # 6. Buscar categoria excluída (404)
    get_del = await auth_client.get(f"/categories/{cat_id}")
    assert get_del.status_code == 404


@pytest.mark.asyncio
async def test_cannot_delete_category_with_linked_products(auth_client: AsyncClient):
    # Criar categoria
    cat_resp = await auth_client.post("/categories", json={"nome": "Bebidas"})
    cat_id = cat_resp.json()["id"]

    # Criar fornecedor
    sup_resp = await auth_client.post(
        "/suppliers",
        json={
            "nome": "Distribuidora Bebidas",
            "cnpj": "11222333000144",
            "telefone": "75999998888",
            "email": "contato@bebidas.com",
        },
    )
    sup_id = sup_resp.json()["id"]

    # Criar produto vinculado à categoria
    prod_resp = await auth_client.post(
        "/products",
        json={
            "nome": "Suco de Laranja 1L",
            "sku": "SUCO-LAR-01",
            "preco_custo": 4.50,
            "preco_venda": 8.00,
            "quantidade_em_estoque": 20,
            "estoque_minimo": 5,
            "categoria_id": cat_id,
            "fornecedor_id": sup_id,
        },
    )
    assert prod_resp.status_code == 201

    # Tentar excluir a categoria com produto vinculado deve retornar 400
    del_resp = await auth_client.delete(f"/categories/{cat_id}")
    assert del_resp.status_code == 400
    data = del_resp.json()
    assert "Não é possível excluir" in data["message"]
