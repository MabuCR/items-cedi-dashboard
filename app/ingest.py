"""
Carga el reporte "item CEDI" (.xlsx, item/slot master) a SQLite.
Este reporte reemplazo al viejo GLS Item Report (ver app/ingest_xls_legacy.py):
cubre TODAS las areas/pasillos del CEDI (no solo Meat/Wet) y trae el UPC real
de cada item (util para el escaner de camara), pero NO trae existencias on-hand
(no hay columna de stock disponible en este formato).

Reusable: si te mandan un reporte nuevo, pisa data/raw_items.xlsx y corre
este script de nuevo (python -m app.ingest).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import openpyxl

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_XLSX = BASE_DIR / "data" / "raw_items.xlsx"
DB_PATH = BASE_DIR / "data" / "items.db"

# Mapea el indice de columna del xlsx (fila 1 = header) a nombre de columna SQL.
# Se descartan columnas de dimensiones/peso detallado y datos de logistica interna
# (vendor_ti/hi, x/y/z coord, etc.) para no saturar la UI movil.
COLUMN_MAP: dict[int, str] = {
    1: "whse_area",
    2: "marshal_area",
    3: "dept_num",
    5: "item_num",
    6: "upc",
    7: "item_desc",
    8: "wac",
    10: "qty_whpk",
    16: "qty_vnpk",
    33: "whse_ti",
    34: "whse_hi",
    40: "rot_code",
    42: "shelf_life",
    43: "whse_life",
    44: "min_rec_day",
    45: "repl_pct",
    52: "sel_sect",
    53: "prime_slot_id",
    63: "repl_type",
    67: "prime_max",
}

TEXT_COLS = {
    "whse_area", "marshal_area", "item_num", "upc", "item_desc",
    "rot_code", "sel_sect", "prime_slot_id", "repl_type",
}

COLUMNS = list(COLUMN_MAP.values())

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {", ".join(f"{c} {'TEXT' if c in TEXT_COLS else 'REAL'}" for c in COLUMNS)}
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_items_item_num ON items(item_num);
CREATE INDEX IF NOT EXISTS idx_items_upc ON items(upc);
CREATE INDEX IF NOT EXISTS idx_items_desc ON items(item_desc);
CREATE INDEX IF NOT EXISTS idx_items_area ON items(whse_area);
"""


def _clean(value, is_text: bool, numeric_text: bool = False):
    if value is None or value == "":
        return None
    if numeric_text:
        # Excel entrega numeros puros (item #, UPC) como float o int;
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
    if not SOURCE_XLSX.exists():
        raise FileNotFoundError(f"No encontre el reporte fuente en {SOURCE_XLSX}")

    wb = openpyxl.load_workbook(SOURCE_XLSX, read_only=True, data_only=True)
    sheet = wb[wb.sheetnames[0]]

    conn = sqlite3.connect(DB_PATH)
    conn.executescript("DROP TABLE IF EXISTS items;")
    conn.executescript(SCHEMA)

    placeholders = ", ".join("?" for _ in COLUMNS)
    insert_sql = f"INSERT OR IGNORE INTO items ({', '.join(COLUMNS)}) VALUES ({placeholders})"

    numeric_text_cols = {"item_num", "upc"}
    rows_to_insert = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[5] in (None, ""):
            continue
        values = []
        for col_idx in COLUMN_MAP:
            name = COLUMN_MAP[col_idx]
            raw = row[col_idx]
            values.append(_clean(raw, name in TEXT_COLS, numeric_text=(name in numeric_text_cols)))
        rows_to_insert.append(values)

    conn.executemany(insert_sql, rows_to_insert)
    conn.commit()
    conn.close()
    return len(rows_to_insert)


if __name__ == "__main__":
    n = ingest()
    print(f"Listo! Cargue {n} items en {DB_PATH}")
