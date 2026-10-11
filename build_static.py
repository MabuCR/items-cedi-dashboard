"""
Arma una pagina HTML standalone (sin backend) para Puppy Pages: mismo look
de la app FastAPI, pero con los datos embebidos y la busqueda resuelta en
JavaScript puro (como el viejo unidades_qr.html).

Uso: python build_static.py
Lee data/items_export.json y escribe items_cedi_static.html en la raiz del proyecto.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "data" / "items_export.json"
OUT_PATH = BASE_DIR / "items_cedi_static.html"

TEMPLATE_HEAD = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Consulta de Items - CEDI Walmart</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {
      --walmart-blue: #0053e2;
      --spark-yellow: #ffc220;
      --green: #2a8703;
      --red: #ea1100;
    }
    body { background: #f4f6fb; font-family: 'Segoe UI', system-ui, sans-serif; }
    .walmart-header { background: var(--walmart-blue); }
    .green-badge { background: #d4edda; color: var(--green); border: 1px solid #b7dfbc; }
    .inactive-badge { background: #f8d7da; color: var(--red); border: 1px solid #f5c2c7; }
    .card { background: white; border-radius: 16px; box-shadow: 0 2px 16px rgba(0,83,226,0.10); }
    .search-input:focus { outline: none; box-shadow: 0 0 0 3px rgba(0,83,226,0.2); border-color: var(--walmart-blue); }
    .search-btn { background: var(--walmart-blue); }
    .search-btn:active { background: #0042b5; }
    .tag { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
    .fade-in { animation: fadeIn 0.3s ease; }
    @keyframes fadeIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
    .match-row:hover { background: #f0f5ff; }
  </style>
</head>
<body class="min-h-screen">
  <header class="walmart-header text-white px-4 py-4 flex items-center gap-3 sticky top-0 z-20 shadow-lg">
    <div>
      <svg width="36" height="36" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="20" r="10" fill="#ffc220"/>
        <circle cx="50" cy="80" r="10" fill="#ffc220"/>
        <circle cx="20" cy="50" r="10" fill="#ffc220"/>
        <circle cx="80" cy="50" r="10" fill="#ffc220"/>
        <circle cx="29" cy="29" r="10" fill="#ffc220"/>
        <circle cx="71" cy="71" r="10" fill="#ffc220"/>
        <circle cx="71" cy="29" r="10" fill="#ffc220"/>
        <circle cx="29" cy="71" r="10" fill="#ffc220"/>
      </svg>
    </div>
    <div>
      <div class="text-lg font-bold leading-tight">Consulta de Items</div>
      <div class="text-blue-200 text-xs">CEDI Walmart - Inventario GLS 2026</div>
    </div>
  </header>

  <main class="px-4 py-6 max-w-lg mx-auto">

    <div class="card p-5 mb-4 text-center">
      <div class="text-sm text-gray-500">Items cargados</div>
      <div class="text-2xl font-black text-blue-700" id="totalItems">-</div>
      <div class="text-xs text-gray-400 mt-1" id="statsLine"></div>
    </div>

    <div class="card p-5 mb-4">
      <p class="text-gray-500 text-sm mb-3 text-center">
        Ingresa el numero de item o el slot (ubicacion)
      </p>
      <div class="flex gap-2">
        <input
          id="searchInput"
          type="text"
          placeholder="Ej: 205019 o MA18N"
          class="search-input flex-1 border-2 border-gray-200 rounded-xl px-4 py-3 text-lg font-mono tracking-wide"
          autocomplete="off"
        />
        <button id="searchBtn" class="search-btn text-white rounded-xl px-5 font-bold text-lg">-&gt;</button>
      </div>
    </div>

    <div id="resultado"></div>

  </main>

  <script id="items-data" type="application/json">
"""

TEMPLATE_TAIL = """
  </script>
  <script>
    const ITEMS = JSON.parse(document.getElementById('items-data').textContent);
    const byItemNum = new Map();
    const bySlot = new Map();
    for (const it of ITEMS) {
      byItemNum.set(String(it.item_num), it);
      const slotKey = (it.prime_slot_id || '').toUpperCase();
      if (!slotKey) continue;
      if (!bySlot.has(slotKey)) bySlot.set(slotKey, []);
      bySlot.get(slotKey).push(it);
    }

    const totalEl = document.getElementById('totalItems');
    const statsEl = document.getElementById('statsLine');
    const sinExistencia = ITEMS.filter(it => it.boh_zero_ind === 'Y').length;
    const areas = new Set(ITEMS.map(it => it.whse_area)).size;
    totalEl.textContent = ITEMS.length.toLocaleString('es');
    statsEl.textContent = `${sinExistencia} sin existencia \u00b7 ${areas} areas de bodega`;

    const resultado = document.getElementById('resultado');
    const input = document.getElementById('searchInput');
    const btn = document.getElementById('searchBtn');

    function num(v) {
      if (v === null || v === undefined || v === '') return '\u2014';
      return String(Math.round(Number(v)));
    }

    function esc(s) {
      if (s === null || s === undefined) return '';
      const d = document.createElement('div');
      d.textContent = String(s);
      return d.innerHTML;
    }

    function renderCard(item) {
      const sinStock = item.boh_zero_ind === 'Y';
      const badge = sinStock
        ? '<div class="tag inactive-badge mt-1">Sin existencia</div>'
        : '<div class="tag green-badge mt-1">Disponible</div>';
      resultado.innerHTML = `
        <div class="card p-5 fade-in">
          <div class="flex items-start justify-between mb-4">
            <div>
              <div class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Item #</div>
              <div class="text-3xl font-black text-blue-700 font-mono">${esc(item.item_num)}</div>
              <div class="text-sm text-gray-600 mt-1">${esc(item.item_desc)}</div>
            </div>
            ${badge}
          </div>
          <hr class="border-gray-100 mb-4"/>
          <div class="grid grid-cols-2 gap-3 mb-4 text-sm">
            <div><div class="text-gray-400 text-xs uppercase">Ubicacion (Slot)</div><div class="font-bold font-mono">${esc(item.prime_slot_id) || '\u2014'}</div></div>
            <div><div class="text-gray-400 text-xs uppercase">Area de bodega</div><div class="font-bold">${esc(item.whse_area) || '\u2014'}</div></div>
            <div><div class="text-gray-400 text-xs uppercase">Seccion</div><div class="font-bold">${esc(item.sel_sect) || '\u2014'}</div></div>
            <div><div class="text-gray-400 text-xs uppercase">Marshal area</div><div class="font-bold">${esc(item.marshal_area) || '\u2014'}</div></div>
          </div>
          <div class="bg-blue-50 rounded-xl p-3 mb-4">
            <div class="text-xs text-blue-700 font-bold uppercase mb-2">Existencias (cajas)</div>
            <div class="grid grid-cols-3 gap-2 text-center">
              <div><div class="text-lg font-black text-blue-700">${num(item.on_hand_whpk)}</div><div class="text-xs text-gray-500">WHPK</div></div>
              <div><div class="text-lg font-black text-blue-700">${num(item.on_hand_vnpk)}</div><div class="text-xs text-gray-500">VNPK</div></div>
              <div><div class="text-lg font-black text-blue-700">${num(item.on_hand_eaches)}</div><div class="text-xs text-gray-500">Eaches</div></div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3 mb-4 text-sm">
            <div><div class="text-gray-400 text-xs uppercase">Tipo reposicion</div><div class="font-bold">${esc(item.repl_type) || '\u2014'}</div></div>
            <div><div class="text-gray-400 text-xs uppercase">% Reposicion / Max</div><div class="font-bold">${num(item.repl_pct)}% / ${num(item.prime_max)}</div></div>
            <div><div class="text-gray-400 text-xs uppercase">Empaque (Whpk/Vnpk/Ea)</div><div class="font-bold">${num(item.qty_whpk)} / ${num(item.qty_vnpk)} / ${num(item.qty_eaches)}</div></div>
            <div><div class="text-gray-400 text-xs uppercase">Pallet Ti x Hi</div><div class="font-bold">${num(item.whse_ti)} x ${num(item.whse_hi)}</div></div>
            <div><div class="text-gray-400 text-xs uppercase">Vida de anaquel</div><div class="font-bold">${num(item.shelf_life)} dias (${esc(item.rot_code) || '\u2014'})</div></div>
            <div><div class="text-gray-400 text-xs uppercase">Costo (WAC)</div><div class="font-bold">${esc(item.wac) || '\u2014'}</div></div>
          </div>
          <div class="text-xs text-gray-400 text-center">
            Depto ${num(item.dept_num)} \u00b7 Grupo ${esc(item.stack_group_code) || '\u2014'}
            ${item.extra_size_ind === 'Y' ? ' \u00b7 Tamano extra' : ''}
          </div>
        </div>`;
    }

    function renderMatchList(matches) {
      const rows = matches.map(m => `
        <button class="match-row w-full text-left py-3 px-2 rounded-lg flex items-center justify-between" data-item="${esc(m.item_num)}">
          <div>
            <div class="font-mono font-bold text-blue-700">${esc(m.item_num)}</div>
            <div class="text-sm text-gray-600">${esc(m.item_desc)}</div>
            <div class="text-xs text-gray-400">${esc(m.whse_area) || '\u2014'} \u00b7 ${esc(m.prime_slot_id) || '\u2014'}</div>
          </div>
          ${m.boh_zero_ind === 'Y' ? '<span class="tag inactive-badge">Sin stock</span>' : '<span class="tag green-badge">OK</span>'}
        </button>`).join('');
      resultado.innerHTML = `<div class="card p-3 fade-in divide-y divide-gray-100">${rows}</div>`;
      resultado.querySelectorAll('.match-row').forEach(btnEl => {
        btnEl.addEventListener('click', () => renderCard(byItemNum.get(btnEl.dataset.item)));
      });
    }

    function renderNotFound(query) {
      resultado.innerHTML = `
        <div class="card p-5 text-center fade-in">
          <div class="font-bold text-gray-700 text-lg">Item no encontrado</div>
          <div class="text-gray-500 text-sm mt-1">${query ? `No hay resultados para "${esc(query)}".` : 'Escribe un numero de item o un slot.'}</div>
        </div>`;
    }

    function search() {
      const q = input.value.trim();
      if (!q) { resultado.innerHTML = ''; return; }
      if (/^\\d+$/.test(q)) {
        const item = byItemNum.get(q);
        if (item) { renderCard(item); } else { renderNotFound(q); }
        return;
      }
      const matches = bySlot.get(q.toUpperCase()) || [];
      if (matches.length === 1) { renderCard(matches[0]); }
      else if (matches.length > 1) { renderMatchList(matches); }
      else { renderNotFound(q); }
    }

    let debounce;
    input.addEventListener('keyup', (e) => {
      clearTimeout(debounce);
      if (e.key === 'Enter') { search(); return; }
      debounce = setTimeout(search, 300);
    });
    btn.addEventListener('click', search);
  </script>
</body>
</html>
"""


def build() -> None:
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"No encontre {JSON_PATH}. Corre antes: python export_json.py")

    json_text = JSON_PATH.read_text(encoding="utf-8")
    # </script> dentro del JSON (no deberia haber, pero por las dudas) rompe el parseo HTML.
    json_text = json_text.replace("</script>", "<\\/script>")

    html = TEMPLATE_HEAD + json_text + TEMPLATE_TAIL
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Listo! {OUT_PATH} ({OUT_PATH.stat().st_size / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    build()
