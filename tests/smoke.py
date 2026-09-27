"""Smoke test générique des routers de app/custom.

Chaque route GET est appelée avec des valeurs plausibles (prises en base quand c'est possible)
et ne doit jamais produire d'erreur serveur. C'est le garde-fou d'exécution que la forge applique
au code écrit par l'IA, rejoué ensuite en CI à chaque commit.
Il ne prouve pas que la réponse est juste métier : ça, c'est la revue de code.
"""
from __future__ import annotations

import datetime
import decimal
import importlib
import pkgutil
import traceback
import typing
import uuid
from pathlib import Path

from fastapi.routing import APIRoute
from sqlalchemy import select

from app.core.db import Base

try:
    import app.generated.models  # noqa: F401  (remplit le registre ORM)
except ModuleNotFoundError:
    pass

CUSTOM_PACKAGE = "app.custom.routers"
APP_DIR = Path(__file__).resolve().parents[1] / "app"
TYPE_SAMPLES: dict[typing.Any, typing.Any] = {
    int: 1,
    float: 1.0,
    str: "a",
    bool: True,
    uuid.UUID: uuid.UUID(int=0),
    decimal.Decimal: decimal.Decimal("1"),
    datetime.date: datetime.date.today(),
    datetime.datetime: datetime.datetime.now(datetime.UTC),
}


def custom_router_modules() -> list[str]:
    package = importlib.import_module(CUSTOM_PACKAGE)
    return sorted(m.name for m in pkgutil.iter_modules(package.__path__))


def _singular(word: str) -> str:
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith(("sses", "xes", "ches", "shes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def _mapper_for(param: str, route_path: str):
    """customer_id -> table customers ; id sur /products/{id} -> table products."""
    if param in ("id", "pk"):
        entity = route_path.strip("/").split("/")[0].replace("-", "_")
    else:
        entity = param.rsplit("_", 1)[0] if "_" in param else param
    for mapper in Base.registry.mappers:
        table = mapper.local_table.name
        if entity in (table, _singular(table)):
            return mapper
    return None


def _base_type(annotation):
    origin = typing.get_origin(annotation)
    if origin is typing.Literal:
        return None, typing.get_args(annotation)[0]
    if origin is not None:  # Optional[X], X | None, Annotated[X, ...]
        args = [a for a in typing.get_args(annotation) if a is not type(None)]
        return _base_type(args[0]) if args else (str, None)
    return annotation, None


def sample_value(session, name: str, annotation, route_path: str):
    base, literal = _base_type(annotation)
    if literal is not None:
        return literal
    mapper = _mapper_for(name, route_path)
    if mapper is not None and len(mapper.primary_key) == 1:
        value = session.scalar(select(mapper.primary_key[0]).limit(1))
        if value is not None and (base is None or isinstance(value, base)):
            return value
    return TYPE_SAMPLES.get(base, "a")


def _short_trace(exc: BaseException) -> str:
    """Ne garde que les frames du projet (app/) : c'est ce qui aide l'IA à corriger."""
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename.startswith(str(APP_DIR))]
    lines = []
    for f in frames[-5:]:
        lines.append(f'  File "{Path(f.filename).relative_to(APP_DIR.parent)}", line {f.lineno}, in {f.name}')
        if f.line:
            lines.append(f"    {f.line}")
    lines += [line.rstrip() for line in traceback.format_exception_only(type(exc), exc)]
    return "\n".join(lines)


def _annotation(field):
    info = getattr(field, "field_info", None)
    return getattr(info, "annotation", None) or getattr(field, "type_", str)


def _required(field) -> bool:
    required = getattr(field, "required", None)
    if isinstance(required, bool):
        return required
    return field.field_info.is_required()


def smoke_router(client, session, app, module_name: str) -> list[str]:
    module = importlib.import_module(f"{CUSTOM_PACKAGE}.{module_name}")
    router = getattr(module, "router", None)
    if router is None:
        return [f"{module_name}: pas de variable 'router' au niveau module"]

    problems: list[str] = []
    generated = {
        (method, r.path)
        for r in app.routes
        if isinstance(r, APIRoute) and r.endpoint.__module__.startswith("app.generated")
        for method in r.methods
    }
    for route in router.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods:
            if (method, route.path) in generated:
                problems.append(f"{method} {route.path} masque une route CRUD générée : choisir un autre chemin")
        if "GET" not in route.methods:
            continue

        path_values = {
            p.name: sample_value(session, p.name, _annotation(p), route.path) for p in route.dependant.path_params
        }
        params = {
            q.name: sample_value(session, q.name, _annotation(q), route.path)
            for q in route.dependant.query_params
            if _required(q)
        }
        url = route.path_format.format(**{k: str(v) for k, v in path_values.items()})
        try:
            response = client.get(url, params={k: str(v) for k, v in params.items()})
        except Exception as exc:  # noqa: BLE001 - la trace est renvoyée à l'IA
            problems.append(f"GET {url} a levé une exception :\n{_short_trace(exc)}")
            continue
        if response.status_code >= 500:
            problems.append(f"GET {url} -> HTTP {response.status_code} : {response.text[:500]}")
        elif response.status_code == 200:
            try:
                response.json()
            except ValueError:
                problems.append(f"GET {url} -> réponse 200 non JSON")
    return problems
