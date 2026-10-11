import json
import os
import sqlite3

conn = sqlite3.connect("data/items.db")
conn.row_factory = sqlite3.Row

COLS = [
    "item_num", "item_desc", "prime_slot_id", "whse_area", "sel_sect",
    "marshal_area", "repl_type", "repl_pct", "prime_max", "qty_whpk",
    "qty_vnpk", "qty_eaches", "whse_ti", "whse_hi", "shelf_life", "rot_code",
    "wac", "on_hand_whpk", "on_hand_vnpk", "on_hand_eaches", "boh_zero_ind",
    "dept_num", "stack_group_code", "extra_size_ind",
]

rows = conn.execute(f"SELECT {', '.join(COLS)} FROM items").fetchall()
data = [dict(r) for r in rows]
conn.close()

out_path = "data/items_export.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

print("items:", len(data))
print("size KB:", round(os.path.getsize(out_path) / 1024, 1))
