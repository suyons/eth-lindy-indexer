from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.sync import IntegrityGuard, ReorgException
from database.connection import Base
from database.repository import BlockchainRepository
from domain.schemas import BlockModel


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    # Ensure tables exist
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def create_mock_block_model(number, hash_val, parent_hash):
    return BlockModel(
        number=number,
        hash=hash_val,
        parent_hash=parent_hash,
        timestamp=int(datetime.now(UTC).timestamp()),
        miner="0x" + "0" * 40,
        difficulty=1,
        total_difficulty=1,
        size=1,
        extra_data="0x",
        gas_limit=1,
        gas_used=1
    )

def test_validate_continuity_success(db_session):
    repo = BlockchainRepository(db_session)
    prev_hash = "0x" + "a" * 64
    
    # Insert previous block via repo
    repo.insert_block(create_mock_block_model(100, prev_hash, "0x" + "0" * 64))
    db_session.commit()

    guard = IntegrityGuard(repo)
    new_block = create_mock_block_model(101, "0x" + "b" * 64, prev_hash)
    
    assert guard.validate_block_continuity(new_block) is True

def test_validate_continuity_reorg_detected(db_session):
    repo = BlockchainRepository(db_session)
    prev_hash = "0x" + "a" * 64
    
    # Insert previous block via repo
    repo.insert_block(create_mock_block_model(100, prev_hash, "0x" + "0" * 64))
    db_session.commit()

    guard = IntegrityGuard(repo)
    wrong_parent_hash = "0x" + "f" * 64
    new_block = create_mock_block_model(101, "0x" + "b" * 64, wrong_parent_hash)
    
    with pytest.raises(ReorgException) as excinfo:
        guard.validate_block_continuity(new_block)
    
    assert excinfo.value.block_number == 101
    assert excinfo.value.expected_parent_hash == prev_hash
    assert excinfo.value.actual_parent_hash == wrong_parent_hash