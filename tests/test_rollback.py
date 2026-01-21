from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.db_service import DatabaseService
from database.connection import Base
from database.repository import BlockchainRepository
from domain.schemas import BlockModel


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def create_block(repo, number):
    block = BlockModel(
        number=number,
        hash=f"0x{number:064x}",
        parent_hash=f"0x{number-1:064x}",
        timestamp=int(datetime.now(UTC).timestamp()),
        miner="0x" + "0" * 40,
        difficulty=1,
        total_difficulty=number,
        size=1,
        extra_data="0x",
        gas_limit=30000000,
        gas_used=0,
    )
    repo.insert_block(block)
    return block


def test_rollback_to_block(db_session):
    repo = BlockchainRepository(db_session)
    service = DatabaseService(repo)

    # Insert 5 blocks (100 to 104)
    for i in range(100, 105):
        create_block(repo, i)
    db_session.commit()

    # Rollback starting from block 103 (deletes 103, 104)
    service.rollback_to_block(103)

    # Verify via repo
    assert repo.get_latest_block().number == 102


def test_rollback_to_non_existent_height(db_session):
    repo = BlockchainRepository(db_session)
    service = DatabaseService(repo)

    create_block(repo, 100)
    db_session.commit()

    service.rollback_to_block(200)

    assert repo.get_latest_block().number == 100
