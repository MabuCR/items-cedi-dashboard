# Consulta de Items - CEDI Walmart

App movil para buscar items (SKUs) del CEDI por numero o descripcion, y ver
su ubicacion en bodega, existencias y datos de reposicion. Es la hermana del
proyecto `unidades_qr.html` pero para items en vez de camiones/unidades.

## Fuente de datos

Reporte "item CEDI" exportado del WMS: `data/raw_items.xlsx` (item/slot master,
NO el viejo GLS Item Report). Cubre **todas las areas del CEDI** (no solo
Meat/Wet como el reporte viejo) y trae el **UPC real** de cada item, pero
**no trae existencias on-hand** (ese dato no esta en este formato de reporte).

Se carga con `openpyxl` (es `.xlsx` moderno). El reporte viejo `.xls` (GLS Item
Report, con existencias pero solo 2 areas) se sigue pudiendo cargar con
`app/ingest_xls_legacy.py` si algun dia vuelve a llegar en ese formato.

**Nunca se commitea** (`data/` esta en `.gitignore`) porque trae info
operativa interna del CEDI.

## Como correrlo

```powershell
uv venv
uv pip install --python .venv\Scripts\python.exe `
  --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple `
  --allow-insecure-host pypi.ci.artifacts.walmart.com `
  fastapi "uvicorn[standard]" jinja2 openpyxl xlrd

# 1. Copia el reporte nuevo a data/raw_items.xlsx
# 2. Carga a SQLite
.venv\Scripts\python.exe -m app.ingest

# 3. Levanta el server
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8425 --reload
```

Abre `http://127.0.0.1:8425` en el celular o en el navegador.

(Nota: el puerto se movio de 8424 a 8425 porque quedo un socket fantasma
pegado en 8424 que Windows no deja matar -- si el 8424 algun dia se libera,
no hay problema en volver a usarlo.)

## Ver la app desde el celular (red local, con camara)

La camara del navegador **no funciona en `http://` plano sobre una IP de red
local** (solo en `https://` o `localhost`). Para probar el escaner desde el
celular conectado al mismo WiFi que la PC:

```powershell
# 1. Genera un certificado autofirmado (una sola vez, valido ~2 anios)
.venv\Scripts\python.exe generate_cert.py

# 2. Levanta el server en https, escuchando en toda la red (no solo localhost)
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8426 `
  --ssl-keyfile certs\key.pem --ssl-certfile certs\cert.pem
```

En el celular (misma red WiFi), abri `https://<IP-de-la-PC>:8426` (ver la IP
con `ipconfig`, interfaz Wi-Fi). El navegador va a avisar que el certificado
no es de confianza (es autofirmado) -- toca "Avanzado" / "Continuar de
todas formas", es normal y esperado.

(Nota: tambien se probaron los puertos 8424 y 8425 pero quedaron sockets
fantasma pegados que Windows no deja matar ni ver con tasklist -- si se
liberan solos en algun reinicio, no hay problema en volver a usarlos.)

## GitHub Pages standalone (index.html) -- SIN BACKEND, funciona con el reporte actual

El `index.html` en la raiz del repo es una version standalone (sin backend,
sin wifi de Walmart, sin laptop prendida) para usar desde cualquier celular.

La clave para que funcione con 346,387 items: `export_json.py` exporta los
datos como **array de arrays** (los nombres de columna se guardan una sola
vez en vez de repetirse en cada fila) y lo comprime con gzip. Eso baja el
peso de ~106 MB (formato ingenuo, un objeto por fila) a solo **~7 MB**
comprimidos -- entra comodo en GitHub (limite 100 MB por archivo) y el
celular lo descarga una sola vez en un par de segundos con wifi o datos.

```powershell
python export_json.py   # regenera items_data.json.gz desde data/items.db
python build_static.py  # regenera index.html (el HTML en si es chiquito, ~14 KB)
git add items_data.json.gz index.html export_json.py build_static.py
git commit -m "Actualiza datos"
git push
```

Despues de activar GitHub Pages (Settings > Pages > Deploy from branch >
`main` > `/root`), la app queda en `https://mabucr.github.io/items-cedi-dashboard/`.
Busca por item#, UPC o slot (ubicacion) igual que la version con backend, y
la camara (boton amarillo) tambien funciona porque GitHub Pages sirve todo
por `https://` (la camara del navegador no funciona en `http://` plano).

## Actualizar los datos

Cuando tengas un reporte nuevo:

1. Pisa `data/raw_items.xlsx` con el archivo nuevo.
2. Corre `python -m app.ingest` de nuevo (recrea la tabla `items` desde cero).
3. No hace falta reiniciar el server si corre con `--reload`.

## Que muestra la ficha de un item

- Ubicacion (slot primario), area de bodega, seccion, marshal area
- UPC (codigo de barras)
- Empaque (cantidades por WHPK/VNPK) y pallet Ti x Hi
- Tipo y porcentaje de reposicion, maximo de slot primario
- Vida de anaquel y codigo de rotacion
- Costo (WAC) y departamento

## Busqueda

- Si escribis solo numeros, se busca match exacto por `ITEM #`, y si no hay
  match se busca por `UPC` (el codigo de barras que lee la camara).
- Si escribis letras/numeros (ej `MA18N`), se busca por `PRIME SLOT ID` (slot).
  Ningun slot del CEDI es puramente numerico, asi que no hay ambiguedad.
- Un slot puede tener mas de un item; si hay varios se muestra una lista para elegir.

## Escaner de codigo de barras (camara)

El boton amarillo junto al buscador abre la camara del celular (via
`html5-qrcode`, 100% navegador, sin backend nuevo) y busca automaticamente
el item apenas detecta un codigo de barras valido. Requiere `https://` o
`localhost` (las camaras del navegador no funcionan en `http://` plano salvo
en `127.0.0.1`/`localhost`).

