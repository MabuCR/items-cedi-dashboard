"""
Carga el reporte GLS Item Report (.xls) a SQLite.
Reusable: si te mandan un reporte nuevo, pisa data/raw_items.xls y corre
este script de nuevo (python -m app.ingest).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import xlrd

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_XLS = BASE_DIR / "data" / "raw_items.xls"
DB_PATH = BASE_DIR / "data" / "items.db"

# Mapea el indice de columna del xls (fila 0 = header) a nombre de columna SQL.
# Se descartan columnas poco usadas en consulta operativa (sanitarios, fitosanitario,
# dimensiones detalladas, etc.) para no cargar ruido a la UI movil.
COLUMN_MAP: dict[int, str] = {
    0: "business_group",
    2: "item_num",
    3: "item_desc",
    4: "dept_num",
    5: "prime_slot_id",
    6: "prime_max",
    7: "repl_pct",
    8: "whse_ti",
    9: "whse_hi",
    10: "pick_seq",
    11: "repl_type",
    13: "slot_ht",
    14: "qty_whpk",
    15: "qty_vnpk",
    16: "qty_eaches",
    19: "whse_area",
    20: "sel_sect",
    21: "marshal_area",
    23: "shelf_life",
    24: "min_rec_day",
    25: "whse_life",
    26: "rot_code",
    27: "wac",
    47: "boh_zero_ind",
    48: "on_hand_whpk",
    55: "on_hand_vnpk",
    56: "on_hand_eaches",
    57: "extra_size_ind",
    58: "stack_group_code",
}

TEXT_COLS = {
    "business_group", "item_num", "item_desc", "prime_slot_id", "repl_type",
    "whse_area", "sel_sect", "marshal_area", "rot_code", "wac",
    "boh_zero_ind", "extra_size_ind", "stack_group_code",
}

COLUMNS = list(COLUMN_MAP.values())

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {", ".join(f"{c} {'TEXT' if c in TEXT_COLS else 'REAL'}" for c in COLUMNS)}
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_items_item_num ON items(item_num);
CREATE INDEX IF NOT EXISTS idx_items_desc ON items(item_desc);
CREATE INDEX IF NOT EXISTS idx_items_area ON items(whse_area);
"""


def _clean(value, is_text: bool, numeric_text: bool = False):
    if value is None or value == "":
        return None
    if numeric_text:
        # Excel entrega numeros puros (ej item #) como float (205019.0);
        # los normalizamos a texto entero para que calcen en busquedas exactas.
        try:
            fval = float(value)
            return str(int(fval)) if fval.is_integer() else str(value).strip()
        except (TypeError, ValueError):
            return str(value).strip()
    if is_text:
        return str(value).strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ingest() -> int:
    if not SOURCE_XLS.exists():
        raise FileNotFoundError(f"No encontre el reporte fuente en {SOURCE_XLS}")

    wb = xlrd.open_workbook(SOURCE_XLS)
    sheet = wb.sheet_by_index(0)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript("DROP TABLE IF EXISTS items;")
    conn.executescript(SCHEMA)

    placeholders = ", ".join("?" for _ in COLUMNS)
    insert_sql = f"INSERT OR IGNORE INTO items ({', '.join(COLUMNS)}) VALUES ({placeholders})"

    rows_to_insert = []
    for r in range(1, sheet.nrows):
        item_num_cell = sheet.cell_value(r, 2)
        if item_num_cell in (None, ""):
            continue
        values = []
        for col_idx in COLUMN_MAP:
            name = COLUMN_MAP[col_idx]
            raw = sheet.cell_value(r, col_idx)
            values.append(_clean(raw, name in TEXT_COLS, numeric_text=(name == "item_num")))
        rows_to_insert.append(values)

    conn.executemany(insert_sql, rows_to_insert)
    conn.commit()
    conn.close()
    return len(rows_to_insert)


if __name__ == "__main__":
    n = ingest()
    print(f"Listo! Cargue {n} items en {DB_PATH}")
