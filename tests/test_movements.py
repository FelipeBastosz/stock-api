import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_movements_immutability_and_balance_updates(auth_client: AsyncClient):
    cat = (await auth_client.post("/categories", json={"nome": "Áudio"})).json()
    sup = (
        await auth_client.post(
            "/suppliers",
            json={
                "nome": "Fornecedor Fones",
                "cnpj": "99112233000188",
                "email": "audio@fornecedor.com",
            },
        )
    ).json()

    # Produto com 10 unidades iniciais
    prod = (
        await auth_client.post(
            "/products",
            json={
                "nome": "Headset Bluetooth",
                "sku": "FONE-BT-01",
                "preco_custo": 100.00,
                "preco_venda": 190.00,
                "quantidade_em_estoque": 10,
                "estoque_minimo": 3,
                "categoria_id": cat["id"],
                "fornecedor_id": sup["id"],
            },
        )
    ).json()
    prod_id = prod["id"]

    # 1. Registrar movimentação de saída (venda de 4 unidades)
    out_resp = await auth_client.post(
        "/movements",
        json={
            "produto_id": prod_id,
            "tipo": "saida",
            "quantidade": 4,
            "observacao": "Venda pedido #101",
        },
    )
    assert out_resp.status_code == 201
    assert out_resp.json()["quantidade"] == 4

    # Verificar que o saldo do produto caiu para 6
    updated_prod = (await auth_client.get(f"/products/{prod_id}")).json()
    assert updated_prod["quantidade_em_estoque"] == 6

    # 2. Registrar movimentação de entrada (reposição de 10 unidades)
    in_resp = await auth_client.post(
        "/movements",
        json={
            "produto_id": prod_id,
            "tipo": "entrada",
            "quantidade": 10,
            "observacao": "NF 5543",
        },
    )
    assert in_resp.status_code == 201

    # Verificar que o saldo do produto subiu para 16
    updated_prod = (await auth_client.get(f"/products/{prod_id}")).json()
    assert updated_prod["quantidade_em_estoque"] == 16

    # 3. Tentativa de saída maior do que o estoque disponível (deve falhar com 400)
    insufficient_resp = await auth_client.post(
        "/movements",
        json={
            "produto_id": prod_id,
            "tipo": "saida",
            "quantidade": 100,  # Maior que 16
        },
    )
    assert insufficient_resp.status_code == 400
    assert "Estoque insuficiente" in insufficient_resp.json()["message"]

    # O saldo permanece inalterado em 16
    prod_check = (await auth_client.get(f"/products/{prod_id}")).json()
    assert prod_check["quantidade_em_estoque"] == 16

    # 4. Consultar resumo de movimentações
    summary_resp = await auth_client.get(f"/movements/summary?produto_id={prod_id}")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_movimentacoes"] == 2
    assert summary["total_itens_entrada"] == 10
    assert summary["total_itens_saida"] == 4
    assert summary["saldo_periodo"] == 6

    # 5. Tentativa de exclusão do produto com histórico de movimentações é bloqueada (400)
    del_prod = await auth_client.delete(f"/products/{prod_id}")
    assert del_prod.status_code == 400
    assert "possui histórico" in del_prod.json()["message"]
