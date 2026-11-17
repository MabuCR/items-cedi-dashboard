"""Capa de acceso a datos: consultas a SQLite para la consulta de items."""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "items.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_by_item_num(item_num: str) -> dict | None:
    """Busca un item por numero exacto (como se busca una placa)."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM items WHERE item_num = ?", (item_num.strip(),)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_by_upc(upc: str) -> dict | None:
    """Busca un item por su codigo de barras (UPC) exacto -- usado por el
    escaner de camara. Muchos UPC del reporte perdieron los ceros a la
    izquierda (Excel los trato como numero en algun punto), asi que
    comparamos por valor numerico en vez de texto exacto -- si no, un
    codigo escaneado completo (con ceros) nunca hace match."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM items WHERE upc IS NOT NULL AND CAST(upc AS INTEGER) = CAST(? AS INTEGER)",
        (upc.strip(),),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def search_by_slot(slot: str, limit: int = 20) -> list[dict]:
    """Busca items cuyo slot primario coincide (un slot puede tener varios items)."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT item_num, item_desc, whse_area, prime_slot_id
        FROM items
        WHERE UPPER(prime_slot_id) = UPPER(?)
        ORDER BY item_desc
        LIMIT ?
        """,
        (slot.strip(), limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    conn = get_connection()
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total_items,
            COUNT(DISTINCT whse_area) AS areas,
            SUM(CASE WHEN upc IS NOT NULL THEN 1 ELSE 0 END) AS con_upc
        FROM items
        """
    ).fetchone()
    conn.close()
    return dict(row) if row else {}
