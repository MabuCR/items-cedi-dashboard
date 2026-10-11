"""FastAPI app: consulta movil de items (SKUs) del CEDI."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import db

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.filters["num"] = lambda v: "\u2014" if v is None else f"{v:.0f}"

app = FastAPI(title="Consulta de Items - CEDI")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request, "stats": db.get_stats()})


@app.get("/buscar", response_class=HTMLResponse)
def buscar(request: Request, q: str = Query(default="")):
    q = q.strip()
    context = {"request": request, "query": q}

    if not q:
        return templates.TemplateResponse(request, "partials/not_found.html", context)

    # Numero puro -> buscamos por item# exacto (como una placa).
    # Cualquier otra cosa (ningun slot del CEDI es puramente numerico) -> por slot.
    if q.isdigit():
        item = db.get_by_item_num(q)
        if item:
            context["item"] = item
            return templates.TemplateResponse(request, "partials/result_card.html", context)
        return templates.TemplateResponse(request, "partials/not_found.html", context)

    matches = db.search_by_slot(q)
    if len(matches) == 1:
        item = db.get_by_item_num(matches[0]["item_num"])
        context["item"] = item
        return templates.TemplateResponse(request, "partials/result_card.html", context)
    if matches:
        context["matches"] = matches
        return templates.TemplateResponse(request, "partials/match_list.html", context)

    return templates.TemplateResponse(request, "partials/not_found.html", context)


@app.get("/item/{item_num}", response_class=HTMLResponse)
def item_detail(request: Request, item_num: str):
    item = db.get_by_item_num(item_num)
    context = {"request": request, "item": item, "query": item_num}
    if not item:
        return templates.TemplateResponse(request, "partials/not_found.html", context)
    return templates.TemplateResponse(request, "partials/result_card.html", context)
