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

## GitHub Pages standalone (index.html) -- DEPRECADO

El `index.html` en la raiz del repo es una version vieja, standalone (sin
backend, datos embebidos en JS) armada cuando el reporte tenia 6,000 items
(~2.8 MB de JSON). **Ya no se puede regenerar** con el reporte actual: con
346,387 items el JSON pesaria ~109 MB, no cabe en GitHub (limite de 100 MB)
y el celular no podria cargarlo. Para ver la app actualizada en el celular,
usar la app FastAPI en vivo (seccion anterior), no este archivo estatico.

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

