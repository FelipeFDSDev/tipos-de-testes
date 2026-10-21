"""SQLite repository and business rules for orders."""

import sqlite3
from pathlib import Path
from threading import RLock


def calculate_total(items: list[tuple[str, int, float]]) -> float:
    """Calculate the total for (name, quantity, unit price) items."""
    if not items:
        raise ValueError("The order must contain at least one item")
    total = 0.0
    for name, quantity, price in items:
        if not name.strip() or quantity <= 0 or price < 0:
            raise ValueError("Invalid item")
        total += quantity * price
    return round(total, 2)


class OrderRepository:
    """SQLite persistence for order CRUD operations."""

    def __init__(self, database: str | Path = "orders.sqlite3") -> None:
        self.connection = sqlite3.connect(str(database), check_same_thread=False)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS orders "
            "(id INTEGER PRIMARY KEY, customer TEXT NOT NULL, total REAL NOT NULL)"
        )
        self.connection.commit()
        self._lock = RLock()

    def create(self, customer: str, items: list[tuple[str, int, float]]) -> int:
        if not customer.strip():
            raise ValueError("Customer is required")
        total = calculate_total(items)
        with self._lock:
            cursor = self.connection.execute(
                "INSERT INTO orders (customer, total) VALUES (?, ?)", (customer, total)
            )
            self.connection.commit()
            return int(cursor.lastrowid)

    def get(self, order_id: int) -> tuple[int, str, float] | None:
        with self._lock:
            row = self.connection.execute(
                "SELECT id, customer, total FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
        return (int(row[0]), str(row[1]), float(row[2])) if row else None

    def list_orders(self) -> list[tuple[int, str, float]]:
        with self._lock:
            rows = self.connection.execute(
                "SELECT id, customer, total FROM orders ORDER BY id"
            ).fetchall()
        return [(int(row[0]), str(row[1]), float(row[2])) for row in rows]

    def update(self, order_id: int, customer: str, items: list[tuple[str, int, float]]) -> bool:
        if not customer.strip():
            raise ValueError("Customer is required")
        total = calculate_total(items)
        with self._lock:
            cursor = self.connection.execute(
                "UPDATE orders SET customer = ?, total = ? WHERE id = ?",
                (customer, total, order_id),
            )
            self.connection.commit()
            return cursor.rowcount > 0

    def delete(self, order_id: int) -> bool:
        with self._lock:
            cursor = self.connection.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            self.connection.commit()
            return cursor.rowcount > 0

    def close(self) -> None:
        with self._lock:
            self.connection.close()
