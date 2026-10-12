import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_supplier_lifecycle_and_uniqueness(client: AsyncClient):
    # 1. Cadastrar fornecedor
    payload = {
        "nome": "Tech Suprimentos Ltda",
        "cnpj": "12345678000199",
        "telefone": "7532214455",
        "email": "vendas@techsuprimentos.com",
    }
    resp = await client.post("/suppliers", json=payload)
    assert resp.status_code == 201
    sup = resp.json()
    sup_id = sup["id"]
    assert sup["nome"] == payload["nome"]
    assert sup["cnpj"] == payload["cnpj"]

    # 2. Rejeitar duplicidade de CNPJ
    resp_dup_cnpj = await client.post(
        "/suppliers",
        json={
            "nome": "Outro Nome",
            "cnpj": "12345678000199",
            "email": "outro@email.com",
        },
    )
    assert resp_dup_cnpj.status_code == 409

    # 3. Rejeitar duplicidade de Email
    resp_dup_email = await client.post(
        "/suppliers",
        json={
            "nome": "Outro Fornecedor",
            "cnpj": "99887766000111",
            "email": "vendas@techsuprimentos.com",
        },
    )
    assert resp_dup_email.status_code == 409

    # 4. Atualizar fornecedor
    resp_up = await client.put(
        f"/suppliers/{sup_id}",
        json={"nome": "Tech Suprimentos Internacional"},
    )
    assert resp_up.status_code == 200
    assert resp_up.json()["nome"] == "Tech Suprimentos Internacional"

    # 5. Excluir sem produtos vinculados
    del_resp = await client.delete(f"/suppliers/{sup_id}")
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_cannot_delete_supplier_with_linked_products(client: AsyncClient):
    cat_resp = await client.post("/categories", json={"nome": "Acessórios"})
    cat_id = cat_resp.json()["id"]

    sup_resp = await client.post(
        "/suppliers",
        json={
            "nome": "Fornecedor Cabos",
            "cnpj": "55667788000122",
            "email": "cabos@fornecedor.com",
        },
    )
    sup_id = sup_resp.json()["id"]

    # Cadastra produto vinculado
    await client.post(
        "/products",
        json={
            "nome": "Cabo HDMI 2.0",
            "sku": "CABO-HDMI-01",
            "preco_custo": 15.00,
            "preco_venda": 35.00,
            "quantidade_em_estoque": 10,
            "estoque_minimo": 2,
            "categoria_id": cat_id,
            "fornecedor_id": sup_id,
        },
    )

    # Bloqueio de exclusão por integridade referencial
    del_resp = await client.delete(f"/suppliers/{sup_id}")
    assert del_resp.status_code == 400
    assert "Não é possível excluir" in del_resp.json()["message"]
