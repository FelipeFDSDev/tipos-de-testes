import pytest

from test_types_demo.app import create_app
from test_types_demo import OrderRepository


@pytest.mark.integration
def test_order_repository_create_read_update_delete(tmp_path):
    repository = OrderRepository(tmp_path / "orders.sqlite")
    try:
        order_id = repository.create("Ana", [("Caderno", 2, 12.50), ("Lápis", 4, 1.25)])
        assert repository.get(order_id) == (order_id, "Ana", 30.0)
        assert repository.update(order_id, "Bia", [("Livro", 1, 45.0)])
        assert repository.get(order_id) == (order_id, "Bia", 45.0)
        assert repository.list_orders() == [(order_id, "Bia", 45.0)]
        assert repository.delete(order_id)
        assert repository.get(order_id) is None
    finally:
        repository.close()


@pytest.mark.integration
def test_orders_api_supports_crud(tmp_path):
    app = create_app(tmp_path / "api.sqlite")
    app.config["TESTING"] = True
    client = app.test_client()
    payload = {"customer": "Ana", "items": [{"name": "Caderno", "quantity": 2, "price": 12.5}]}

    created = client.post("/orders", json=payload)
    assert created.status_code == 201
    order_id = created.json["id"]
    assert created.json == {"id": order_id, "customer": "Ana", "total": 25.0}
    assert client.get("/orders").json == [created.json]
    assert client.get(f"/orders/{order_id}").json == created.json

    updated = client.put(f"/orders/{order_id}", json={"customer": "Bia", "items": [{"name": "Livro", "quantity": 1, "price": 40}]})
    assert updated.status_code == 200
    assert updated.json["customer"] == "Bia"
    assert updated.json["total"] == 40.0
    assert client.delete(f"/orders/{order_id}").status_code == 204
    assert client.get(f"/orders/{order_id}").status_code == 404

    app.extensions["orders_repository"].close()
