# Consulta de Items - CEDI Walmart

App movil para buscar items (SKUs) del CEDI por numero o descripcion, y ver
su ubicacion en bodega, existencias y datos de reposicion. Es la hermana del
proyecto `unidades_qr.html` pero para items en vez de camiones/unidades.

## Fuente de datos

Reporte GLS Item Report exportado desde el WMS: `data/raw_items.xls`
(formato `.xls` clasico, no se puede abrir con openpyxl por eso usamos `xlrd`).

**Nunca se commitea** (`data/` esta en `.gitignore`) porque trae info
operativa interna del CEDI.

## Como correrlo

```powershell
uv venv
uv pip install --python .venv\Scripts\python.exe `
  --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple `
  --allow-insecure-host pypi.ci.artifacts.walmart.com `
  fastapi "uvicorn[standard]" jinja2 xlrd

# 1. Copia el reporte nuevo a data/raw_items.xls
# 2. Carga a SQLite
.venv\Scripts\python.exe -m app.ingest

# 3. Levanta el server
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8424 --reload
```

Abre `http://127.0.0.1:8424` en el celular o en el navegador.

## Actualizar los datos

Cuando tengas un reporte GLS nuevo:

1. Pisa `data/raw_items.xls` con el archivo nuevo.
2. Corre `python -m app.ingest` de nuevo (recrea la tabla `items` desde cero).
3. No hace falta reiniciar el server si corre con `--reload`.

## Que muestra la ficha de un item

- Ubicacion (slot primario), area de bodega, seccion, marshal area
- Existencias en WHPK / VNPK / Eaches, con badge verde/rojo segun stock
- Tipo y porcentaje de reposicion, maximo de slot primario
- Empaque (cantidades por WHPK/VNPK/Eaches) y pallet Ti x Hi
- Vida de anaquel y codigo de rotacion
- Costo (WAC), departamento y grupo de apilado

## Busqueda

- Si escribis solo numeros, se busca match exacto por `ITEM #` (como una placa).
- Si escribis texto, se busca por coincidencia parcial en la descripcion;
  si hay varios resultados se muestra una lista para elegir.
