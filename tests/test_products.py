import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_product_crud_and_advanced_filters(auth_client: AsyncClient):
    cat = (await auth_client.post("/categories", json={"nome": "Periféricos"})).json()
    sup = (
        await auth_client.post(
            "/suppliers",
            json={
                "nome": "Logitech Brasil",
                "cnpj": "44332211000100",
                "email": "contato@logitech.com",
            },
        )
    ).json()

    payload = {
        "nome": "Mouse Gamer RGB",
        "sku": "MOUSE-RGB-01",
        "preco_custo": 80.00,
        "preco_venda": 150.00,
        "quantidade_em_estoque": 2,
        "estoque_minimo": 5,
        "categoria_id": cat["id"],
        "fornecedor_id": sup["id"],
    }
    resp = await auth_client.post("/products", json=payload)
    assert resp.status_code == 201
    prod = resp.json()
    prod_id = prod["id"]
    assert prod["sku"] == "MOUSE-RGB-01"
    assert prod["category"]["nome"] == "Periféricos"
    assert prod["supplier"]["nome"] == "Logitech Brasil"

    dup_resp = await auth_client.post("/products", json=payload)
    assert dup_resp.status_code == 409

    bad_cat = payload.copy()
    bad_cat["sku"] = "OUTRO-SKU-99"
    bad_cat["categoria_id"] = 9999
    assert (await auth_client.post("/products", json=bad_cat)).status_code == 404

    search_resp = await auth_client.get("/products?busca=gamer")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) == 1
    assert search_resp.json()[0]["sku"] == "MOUSE-RGB-01"

    low_stock_resp = await auth_client.get("/products/low-stock")
    assert low_stock_resp.status_code == 200
    items = low_stock_resp.json()
    assert len(items) >= 1
    assert any(i["id"] == prod_id for i in items)

    resp_below = await auth_client.get("/products?abaixo_minimo=true")
    assert resp_below.status_code == 200
    assert any(p["id"] == prod_id for p in resp_below.json())

    resp_above = await auth_client.get("/products?abaixo_minimo=false")
    assert resp_above.status_code == 200
    assert not any(p["id"] == prod_id for p in resp_above.json())

    up_resp = await auth_client.put(f"/products/{prod_id}", json={"preco_venda": 165.00})
    assert up_resp.status_code == 200
    assert float(up_resp.json()["preco_venda"]) == 165.00
