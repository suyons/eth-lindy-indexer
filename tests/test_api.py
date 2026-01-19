import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC

from indexer.api import app
from indexer.models.database import Base, get_db
from indexer.models.orm import Block

from sqlalchemy.pool import StaticPool

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "eth-lindy-indexer"}

def test_get_latest_block_empty(client):
    response = client.get("/blocks/latest")
    assert response.status_code == 404
    assert response.json()["detail"] == "No blocks found in database"

def test_get_latest_block_success(client):
    # Add a dummy block
    db = TestingSessionLocal()
    block = Block(
        number=12345,
        hash="0x" + "a" * 64,
        parent_hash="0x" + "b" * 64,
        timestamp=datetime.now(UTC),
        miner="0x" + "c" * 40,
        difficulty=1000,
        total_difficulty=2000,
        size=500,
        extra_data="0x",
        gas_limit=30000000,
        gas_used=15000000
    )
    db.add(block)
    db.commit()
    db.close()

    response = client.get("/blocks/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 12345
    assert data["hash"] == "0x" + "a" * 64
