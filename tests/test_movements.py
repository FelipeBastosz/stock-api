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

    updated_prod = (await auth_client.get(f"/products/{prod_id}")).json()
    assert updated_prod["quantidade_em_estoque"] == 6

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

    updated_prod = (await auth_client.get(f"/products/{prod_id}")).json()
    assert updated_prod["quantidade_em_estoque"] == 16

    insufficient_resp = await auth_client.post(
        "/movements",
        json={
            "produto_id": prod_id,
            "tipo": "saida",
            "quantidade": 100,
        },
    )
    assert insufficient_resp.status_code == 400
    assert "Estoque insuficiente" in insufficient_resp.json()["message"]

    prod_check = (await auth_client.get(f"/products/{prod_id}")).json()
    assert prod_check["quantidade_em_estoque"] == 16

    summary_resp = await auth_client.get(f"/movements/summary?produto_id={prod_id}")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_movimentacoes"] == 2
    assert summary["total_itens_entrada"] == 10
    assert summary["total_itens_saida"] == 4
    assert summary["saldo_periodo"] == 6

    del_prod = await auth_client.delete(f"/products/{prod_id}")
    assert del_prod.status_code == 400
    assert "possui histórico" in del_prod.json()["message"]


@pytest.mark.asyncio
async def test_movements_advanced_filters_and_date_validation(auth_client: AsyncClient):
    import asyncio
    from datetime import datetime, timedelta, timezone

    cat = (await auth_client.post("/categories", json={"nome": "Redes"})).json()
    sup = (
        await auth_client.post(
            "/suppliers",
            json={
                "nome": "Fornecedor Roteadores",
                "cnpj": "77889900000133",
                "email": "redes@fornecedor.com",
            },
        )
    ).json()

    prod = (
        await auth_client.post(
            "/products",
            json={
                "nome": "Roteador Wi-Fi 6",
                "sku": "ROT-WIFI6-01",
                "preco_custo": 250.00,
                "preco_venda": 420.00,
                "quantidade_em_estoque": 20,
                "estoque_minimo": 5,
                "categoria_id": cat["id"],
                "fornecedor_id": sup["id"],
            },
        )
    ).json()

    await auth_client.post(
        "/movements",
        json={"produto_id": prod["id"], "tipo": "entrada", "quantidade": 15},
    )

    resp_sup = await auth_client.get(f"/movements?fornecedor_id={sup['id']}")
    assert resp_sup.status_code == 200
    movs = resp_sup.json()
    assert len(movs) >= 1
    assert all(m["product"]["fornecedor_id"] == sup["id"] for m in movs if m.get("product"))

    agora = datetime.now(timezone.utc)
    inicio = (agora - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    fim = (agora + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    resp_period = await auth_client.get(
        "/movements",
        params={"data_inicio": inicio, "data_fim": fim},
    )
    assert resp_period.status_code == 200
    assert len(resp_period.json()) >= 1

    data_invalida_inicio = (agora + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    data_invalida_fim = (agora - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    bad_range = await auth_client.get(
        "/movements",
        params={"data_inicio": data_invalida_inicio, "data_fim": data_invalida_fim},
    )
    assert bad_range.status_code == 400
    assert "não pode ser posterior" in bad_range.json()["message"]

    safe_tz_resp = await auth_client.get(
        "/movements",
        params={"data_inicio": "2026-10-20T10:00:00Z", "data_fim": "2026-10-25T10:00:00"},
    )
    assert safe_tz_resp.status_code == 200


@pytest.mark.asyncio
async def test_concurrent_movements_race_condition(auth_client: AsyncClient):
    cat = (await auth_client.post("/categories", json={"nome": "Concorrência"})).json()
    sup = (
        await auth_client.post(
            "/suppliers",
            json={
                "nome": "Fornecedor Concorrência",
                "cnpj": "33445566000177",
                "email": "concorrencia@fornecedor.com",
            },
        )
    ).json()

    prod = (
        await auth_client.post(
            "/products",
            json={
                "nome": "Placa de Vídeo RTX 4090",
                "sku": "RTX-4090-LIMITED",
                "preco_custo": 5000.00,
                "preco_venda": 9500.00,
                "quantidade_em_estoque": 5,
                "estoque_minimo": 1,
                "categoria_id": cat["id"],
                "fornecedor_id": sup["id"],
            },
        )
    ).json()
    prod_id = prod["id"]

    resp1 = await auth_client.post(
        "/movements",
        json={"produto_id": prod_id, "tipo": "saida", "quantidade": 2},
    )
    assert resp1.status_code == 201

    resp2 = await auth_client.post(
        "/movements",
        json={"produto_id": prod_id, "tipo": "saida", "quantidade": 2},
    )
    assert resp2.status_code == 201

    resp3 = await auth_client.post(
        "/movements",
        json={"produto_id": prod_id, "tipo": "saida", "quantidade": 2},
    )
    assert resp3.status_code == 400
    assert "Estoque insuficiente" in resp3.json()["message"]

    final_prod = (await auth_client.get(f"/products/{prod_id}")).json()
    assert final_prod["quantidade_em_estoque"] == 1

