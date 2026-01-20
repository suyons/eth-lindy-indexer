import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, UTC

from indexer.api import app
from indexer.models.database import Base, get_db
from indexer.models.repository import BlockchainRepository
from indexer.models.schemas import BlockModel

# Test database setup with StaticPool for in-memory SQLite shared state
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
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
    # Use existing ORM models to create tables for Raw SQL repository to interact with
    from indexer.models.orm import Block, Transaction, Log
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
    db = TestingSessionLocal()
    repo = BlockchainRepository(db)
    
    block_data = BlockModel(
        number=12345,
        hash="0x" + "a" * 64,
        parent_hash="0x" + "b" * 64,
        timestamp=int(datetime.now(UTC).timestamp()),
        miner="0x" + "c" * 40,
        difficulty=1000,
        total_difficulty=2000,
        size=500,
        extra_data="0x",
        gas_limit=30000000,
        gas_used=15000000
    )
    repo.insert_block(block_data)
    db.commit()
    db.close()

    response = client.get("/blocks/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 12345
    assert data["hash"] == "0x" + "a" * 64