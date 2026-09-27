import json
import os

import pytest

from app.main import app
from tests.smoke import custom_router_modules, smoke_router


@pytest.mark.parametrize("module_name", custom_router_modules())
def test_custom_router_smoke(module_name, session):
    from fastapi.testclient import TestClient

    from app.core.db import get_session

    app.dependency_overrides[get_session] = lambda: session
    try:
        with TestClient(app, raise_server_exceptions=True) as client:
            problems = smoke_router(client, session, app, module_name)
    finally:
        app.dependency_overrides.clear()
    if report := os.environ.get("FORGE_SMOKE_REPORT"):  # lu par la forge pour renvoyer les erreurs à l'IA
        with open(report, "w", encoding="utf-8") as fh:
            json.dump(problems, fh, ensure_ascii=False)
    assert not problems, "\n\n".join(problems)
