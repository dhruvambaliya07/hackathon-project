import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("AI_API_KEY", "test-key")
os.environ.setdefault("AI_MODEL", "test-model")
os.environ.setdefault("EMBEDDING_MODEL", "test-embedding")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")


@pytest.fixture(scope="session", autouse=True)
def sqlite_schema() -> None:
	if not os.environ["DATABASE_URL"].startswith("sqlite"):
		return
	import app.models  # noqa: F401
	from app.db.base import Base
	from app.db.session import engine

	Base.metadata.create_all(engine)