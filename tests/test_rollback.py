import pytest
from datetime import datetime, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from indexer.models.database import Base
from indexer.models.orm import Block, Transaction, Log
from indexer.db_service import DatabaseService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def create_block(session, number):
    block = Block(
        number=number,
        hash=f"0x{number:064x}",
        parent_hash=f"0x{number-1:064x}",
        timestamp=datetime.now(UTC),
        miner="0x" + "0" * 40,
        difficulty=1,
        total_difficulty=number,
        size=1,
        extra_data="0x",
        gas_limit=30000000,
        gas_used=0
    )
    session.add(block)
    
    # Add a transaction for each block
    tx = Transaction(
        hash=f"0x{number:064x}00",
        nonce=0,
        block_hash=block.hash,
        block_number=block.number,
        transaction_index=0,
        from_address="0x" + "1" * 40,
        to_address="0x" + "2" * 40,
        value=0,
        gas_price=10**9,
        gas=21000,
        input="0x"
    )
    session.add(tx)
    
    # Add a log for each transaction
    log = Log(
        log_index=0,
        transaction_hash=tx.hash,
        address="0x" + "3" * 40,
        data="0x",
        topics=[],
        block_number=block.number,
        block_hash=block.hash
    )
    session.add(log)
    return block

def test_rollback_to_block(db_session):
    # Insert 5 blocks (100 to 104)
    for i in range(100, 105):
        create_block(db_session, i)
    db_session.commit()
    
    assert db_session.query(Block).count() == 5
    assert db_session.query(Transaction).count() == 5
    assert db_session.query(Log).count() == 5
    
    service = DatabaseService(db_session)
    
    # Rollback starting from block 103 (deletes 103, 104)
    deleted_count = service.rollback_to_block(103)
    
    assert deleted_count == 2
    assert db_session.query(Block).count() == 3
    assert db_session.query(Transaction).count() == 3
    assert db_session.query(Log).count() == 3
    
    # Verify blocks 100, 101, 102 remain
    remaining_numbers = [b.number for b in db_session.query(Block).all()]
    assert sorted(remaining_numbers) == [100, 101, 102]

def test_rollback_to_non_existent_height(db_session):
    create_block(db_session, 100)
    db_session.commit()
    
    service = DatabaseService(db_session)
    deleted_count = service.rollback_to_block(200)
    
    assert deleted_count == 0
    assert db_session.query(Block).count() == 1
