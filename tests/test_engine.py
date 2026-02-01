import pytest
from unittest.mock import MagicMock, patch
from core.engine import SyncEngine
from core.sync import ReorgException
from domain.schemas import BlockModel

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_provider():
    return MagicMock()

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def engine(mock_db, mock_provider, mock_repo):
    engine = SyncEngine(mock_db, mock_provider)
    engine.repo = mock_repo
    # Re-initialize dependent services with the mock repo
    engine.guard = MagicMock()
    engine.db_service = MagicMock()
    return engine

def test_sync_block_success(engine, mock_provider, mock_db, mock_repo):
    block_number = 100
    mock_block = {
        "number": block_number,
        "hash": "0x" + "a" * 64,
        "parent_hash": "0x" + "b" * 64,
        "timestamp": 1673812800,
        "miner": "0x" + "c" * 40,
        "difficulty": 1000,
        "total_difficulty": 2000,
        "size": 500,
        "extra_data": "0x1234",
        "gas_limit": 30000000,
        "gas_used": 15000000,
        "transactions": []
    }
    mock_provider.get_block.return_value = mock_block
    
    engine.sync_block(block_number)
        
    assert mock_db.commit.called
    mock_repo.insert_block.assert_called_once()

def test_sync_block_reorg_trigger(engine, mock_provider, mock_db, mock_repo):
    block_number = 100
    # Provide valid data to avoid ValidationError before ReorgException
    mock_block = {
        "number": block_number,
        "hash": "0x" + "a" * 64,
        "parent_hash": "0x" + "b" * 64,
        "timestamp": 1673812800,
        "miner": "0x" + "c" * 40,
        "difficulty": 1000,
        "total_difficulty": 2000,
        "size": 500,
        "extra_data": "0x1234",
        "gas_limit": 30000000,
        "gas_used": 15000000,
        "transactions": []
    }
    mock_provider.get_block.return_value = mock_block
    
    # Simulate a reorg in the guard
    engine.guard.validate_block_continuity.side_effect = ReorgException(block_number, "0xabc", "0x456")
    
    with pytest.raises(ReorgException):
        engine.sync_block(block_number)
    
    # Should rollback to 99
    engine.db_service.rollback_to_block.assert_called_once_with(99)
