import os
import pytest

# Set env vars before any app imports so config picks them up
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32chars!"
os.environ["DATABASE_URL"] = "sqlite://"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import the db module so we can patch its engine before main.py uses it
import app.core.database as _db_module

# StaticPool ensures all connections reuse the same underlying SQLite connection,
# so tables created by create_all() remain visible to test sessions.
_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_db_module.engine = _test_engine
_db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# Import app AFTER patching — main.py does `from app.core.database import engine`
# which will now bind to _test_engine
from app.core.database import Base, get_db
from app.main import app  # also runs Base.metadata.create_all(bind=engine)

# Disable auth rate limiting in tests — the suite makes many /auth calls and the
# 10/min per-IP limit would otherwise reject later registrations with 429.
from app.routes.auth import limiter as _auth_limiter
_auth_limiter.enabled = False

# Ensure all tables exist (main.py's create_all uses our engine, but guard anyway)
Base.metadata.create_all(bind=_test_engine)

_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with __import__("fastapi.testclient", fromlist=["TestClient"]).TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
