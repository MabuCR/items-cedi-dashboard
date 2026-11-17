"""
Exporta los items de SQLite a un JSON compacto (formato array, no objetos
repetidos) y lo comprime con gzip, listo para servir desde GitHub Pages.

Por que array y no objeto por fila: con 346k+ items, repetir el nombre de
cada campo en cada fila (formato dict) pesa ~106 MB. Guardando solo los
valores en arrays (el orden de campos se guarda una sola vez en "fields")
el JSON crudo baja a ~40 MB, y comprimido con gzip queda en ~7 MB -- entra
comodo en GitHub (limite 100 MB) y es rapido de descargar en el celular.

Uso: python export_json.py
Escribe items_data.json.gz en la raiz del proyecto (se commitea a git, a
diferencia de data/ que esta gitignored).
"""
import gzip
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "items.db"
OUT_PATH = BASE_DIR / "items_data.json.gz"

# Mismo orden que se usa en el JS de items_cedi_static.html -- si cambias
# este orden, actualiza tambien el mapeo FIELD_IDX en build_static.py.
COLS = [
    "item_num", "item_desc", "prime_slot_id", "whse_area", "sel_sect",
    "marshal_area", "repl_type", "repl_pct", "prime_max", "qty_whpk",
    "qty_vnpk", "whse_ti", "whse_hi", "shelf_life", "rot_code",
    "wac", "upc", "dept_num",
]


def export() -> None:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(f"SELECT {', '.join(COLS)} FROM items").fetchall()
    conn.close()

    payload = {"fields": COLS, "rows": [list(r) for r in rows]}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    with gzip.open(OUT_PATH, "wb", compresslevel=9) as f:
        f.write(raw)

    print(f"items: {len(payload['rows'])}")
    print(f"raw MB: {len(raw) / 1024 / 1024:.2f}")
    print(f"gz MB: {OUT_PATH.stat().st_size / 1024 / 1024:.2f}  -> {OUT_PATH}")


if __name__ == "__main__":
    export()
