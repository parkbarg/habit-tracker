import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

TEST_DATABASE_NAME = "habit_tracker_test"

# settings はimport時に作られるため、backendを読み込む前に接続先をテスト用DBへ向ける
os.environ.setdefault(
    "DATABASE_URL",
    f"postgresql+psycopg://habit_tracker:habit_tracker@localhost:5432/{TEST_DATABASE_NAME}",
)

from backend.core.config import settings  # noqa: E402
from backend.db.session import engine, get_db  # noqa: E402
from backend.main import app  # noqa: E402

# 開発用DBを誤って変更しないよう、テスト用DB以外への接続ではテストを開始しない
if make_url(settings.database_url).database != TEST_DATABASE_NAME:
    pytest.exit(
        f"DATABASE_URL must point to '{TEST_DATABASE_NAME}': {settings.database_url}",
        returncode=1,
    )


@pytest.fixture
def db_session() -> Iterator[Session]:
    # テスト全体を外側のトランザクションで包み、終了時にロールバックしてデータを分離する。
    # アプリ側の commit / rollback はSAVEPOINTに対して行われる。
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
