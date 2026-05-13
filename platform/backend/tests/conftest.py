import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Item, User
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


def _db_fixture_enabled() -> bool:
    """Set PYTEST_DISABLE_DB_FIXTURE=1 to run tests that do not need Postgres (e.g. stateless IPTV routes)."""
    return os.environ.get("PYTEST_DISABLE_DB_FIXTURE", "").lower() not in (
        "1",
        "true",
        "yes",
    )


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session | None, None, None]:
    if not _db_fixture_enabled():
        yield None
        return
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(Item)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
