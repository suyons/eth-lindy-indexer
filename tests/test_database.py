import pytest
from datetime import datetime, UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from indexer.models.database import Base
from indexer.models.orm import Block, Transaction, Log

@pytest.fixture
def db_session():
    # Use SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_block_with_transactions_and_logs(db_session):
    # Create block
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
    db_session.add(block)
    
    # Create transaction
    tx = Transaction(
        hash="0x" + "d" * 64,
        nonce=1,
        block_hash=block.hash,
        block_number=block.number,
        transaction_index=0,
        from_address="0x" + "e" * 40,
        to_address="0x" + "f" * 40,
        value=10**18,
        gas_price=20000000000,
        gas=21000,
        input="0x"
    )
    db_session.add(tx)
    
    # Create log
    log = Log(
        log_index=0,
        transaction_hash=tx.hash,
        address="0x" + "f" * 40,
        data="0x",
        topics=["0x" + "1" * 64],
        block_number=block.number,
        block_hash=block.hash
    )
    db_session.add(log)
    
    db_session.commit()
    
    # Verify
    saved_block = db_session.query(Block).filter_by(number=12345).first()
    assert saved_block is not None
    assert len(saved_block.transactions) == 1
    assert saved_block.transactions[0].hash == tx.hash
    assert len(saved_block.logs) == 1
    assert saved_block.logs[0].transaction_hash == tx.hash
