"""Chaque test tourne dans une transaction annulée à la fin : la base n'est jamais modifiée.

Nécessite DATABASE_URL (ou .env) pointant vers une base PostgreSQL avec le schéma.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.db import engine, get_session
from app.main import app


@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(session):
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
