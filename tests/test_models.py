import pytest
from datetime import datetime
from pydantic import ValidationError
from indexer.models.schemas import BlockModel, TransactionModel, LogModel

def test_block_model_valid():
    valid_block = {
        "number": 12345,
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
        "base_fee_per_gas": 1000000000
    }
    block = BlockModel(**valid_block)
    assert block.number == 12345
    assert isinstance(block.timestamp, datetime)

def test_block_model_invalid_hash():
    invalid_block = {
        "number": 12345,
        "hash": "0x" + "a" * 63, # Too short
        "parent_hash": "0x" + "b" * 64,
        "timestamp": 1673812800,
        "miner": "0x" + "c" * 40,
        "difficulty": 1000,
        "total_difficulty": 2000,
        "size": 500,
        "extra_data": "0x1234",
        "gas_limit": 30000000,
        "gas_used": 15000000
    }
    with pytest.raises(ValidationError):
        BlockModel(**invalid_block)

def test_transaction_model_valid():
    valid_tx = {
        "hash": "0x" + "d" * 64,
        "nonce": 1,
        "block_hash": "0x" + "a" * 64,
        "block_number": 12345,
        "transaction_index": 0,
        "from": "0x" + "e" * 40,
        "to": "0x" + "f" * 40,
        "value": 10**18,
        "gas_price": 20 * 10**9,
        "gas": 21000,
        "input": "0x"
    }
    tx = TransactionModel(**valid_tx)
    assert tx.hash == "0x" + "d" * 64
    assert tx.from_address == "0x" + "e" * 40

def test_log_model_valid():
    valid_log = {
        "log_index": 0,
        "transaction_hash": "0x" + "d" * 64,
        "address": "0x" + "f" * 40,
        "data": "0x0000000000000000000000000000000000000000000000000000000000000001",
        "topics": ["0x" + "1" * 64],
        "block_number": 12345,
        "block_hash": "0x" + "a" * 64
    }
    log = LogModel(**valid_log)
    assert log.log_index == 0
    assert len(log.topics) == 1
