"""Flask HTTP API for creating and managing orders."""

from pathlib import Path

from flask import Flask, jsonify, request

from .orders import OrderRepository


def _parse_order(payload: object) -> tuple[str, list[tuple[str, int, float]]]:
    if not isinstance(payload, dict):
        raise ValueError("JSON object required")
    customer = payload.get("customer")
    raw_items = payload.get("items")
    if not isinstance(customer, str) or not isinstance(raw_items, list):
        raise ValueError("Fields 'customer' and 'items' are required")
    try:
        items = [(item["name"], int(item["quantity"]), float(item["price"])) for item in raw_items]
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Each item must contain name, quantity and price") from error
    return customer, items


def _as_json(order: tuple[int, str, float]) -> dict[str, object]:
    order_id, customer, total = order
    return {"id": order_id, "customer": customer, "total": total}


def create_app(database: str | Path | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = str(database or Path.cwd() / "orders.sqlite3")
    repository = OrderRepository(app.config["DATABASE"])
    app.extensions["orders_repository"] = repository

    @app.get("/")
    def index():
        return """<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>API de pedidos</title></head>
<body>
  <h1>API de pedidos</h1>
  <p>A aplicação está funcionando. Use os endpoints abaixo:</p>
  <ul>
    <li><code>GET /orders</code> — listar pedidos</li>
    <li><code>POST /orders</code> — criar pedido</li>
    <li><code>GET /orders/&lt;id&gt;</code> — consultar pedido</li>
    <li><code>PUT /orders/&lt;id&gt;</code> — atualizar pedido</li>
    <li><code>DELETE /orders/&lt;id&gt;</code> — excluir pedido</li>
  </ul>
</body>
</html>"""

    @app.get("/orders")
    def list_orders():
        return jsonify([_as_json(order) for order in repository.list_orders()])

    @app.post("/orders")
    def create_order():
        try:
            customer, items = _parse_order(request.get_json(silent=True))
            order_id = repository.create(customer, items)
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        return jsonify(_as_json(repository.get(order_id))), 201

    @app.get("/orders/<int:order_id>")
    def get_order(order_id: int):
        order = repository.get(order_id)
        if order is None:
            return jsonify({"error": "Order not found"}), 404
        return jsonify(_as_json(order))

    @app.put("/orders/<int:order_id>")
    def update_order(order_id: int):
        try:
            customer, items = _parse_order(request.get_json(silent=True))
            if not repository.update(order_id, customer, items):
                return jsonify({"error": "Order not found"}), 404
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        return jsonify(_as_json(repository.get(order_id)))

    @app.delete("/orders/<int:order_id>")
    def delete_order(order_id: int):
        if not repository.delete(order_id):
            return jsonify({"error": "Order not found"}), 404
        return "", 204

    return app
