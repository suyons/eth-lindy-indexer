import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC
from indexer.models.database import Base
from indexer.models.repository import BlockchainRepository
from indexer.models.schemas import BlockModel

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    # Create tables using the existing ORM definitions for convenience in tests,
    # but the Repository will use Raw SQL to interact with them.
    from indexer.models.orm import Block, Transaction, Log
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_repository_insert_and_get_block(db_session):
    repo = BlockchainRepository(db_session)
    
    block_data = BlockModel(
        number=100,
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
    db_session.commit()
    
    latest = repo.get_latest_block()
    assert latest is not None
    assert latest.number == 100
    assert latest.hash == block_data.hash

def test_repository_rollback(db_session):
    repo = BlockchainRepository(db_session)
    
    # Insert two blocks
    for i in [100, 101]:
        repo.insert_block(BlockModel(
            number=i,
            hash=f"0x{i:064x}",
            parent_hash=f"0x{i-1:064x}",
            timestamp=int(datetime.now(UTC).timestamp()),
            miner="0x" + "0" * 40,
            difficulty=1, total_difficulty=1, size=1,
            extra_data="0x", gas_limit=1, gas_used=1
        ))
    db_session.commit()
    
    assert repo.get_latest_block().number == 101
    
    # Rollback block 101
    repo.rollback_from_height(101)
    db_session.commit()
    
    assert repo.get_latest_block().number == 100
