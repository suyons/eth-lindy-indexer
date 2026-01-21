from unittest.mock import patch

import pytest
from web3.exceptions import Web3Exception

from core.config import settings
from core.provider import BlockchainProvider


@pytest.fixture
def provider():
    return BlockchainProvider("http://localhost:8545")


def test_provider_is_connected(provider):
    with patch.object(provider.w3, "is_connected", return_value=True):
        assert provider.is_connected() is True


def test_get_block_success(provider):
    mock_block = {"number": 100, "hash": "0x123"}
    with patch.object(provider.w3.eth, "get_block", return_value=mock_block):
        block = provider.get_block(100)
        assert block["number"] == 100
        provider.w3.eth.get_block.assert_called_once_with(100, False)


def test_get_block_retry_success(provider):
    mock_block = {"number": 100, "hash": "0x123"}
    # Fail twice, then succeed
    side_effect = [Web3Exception("Rate limit"), Web3Exception("Timeout"), mock_block]

    with patch.object(provider.w3.eth, "get_block", side_effect=side_effect):
        # We need to reduce the wait time for tests to run fast
        with patch("tenacity.wait_exponential.__call__", return_value=0):
            block = provider.get_block(100)
            assert block["number"] == 100
            assert provider.w3.eth.get_block.call_count == 3


def test_get_block_fail_after_max_retries(provider):
    with patch.object(
        provider.w3.eth, "get_block", side_effect=Web3Exception("Permanent error")
    ):
        with patch("tenacity.wait_exponential.__call__", return_value=0):
            with pytest.raises(Web3Exception):
                provider.get_block(100)
            assert provider.w3.eth.get_block.call_count == settings.retry_max_attempts


def test_get_transaction_retry(provider):
    mock_tx = {"hash": "0xabc", "value": 100}
    side_effect = [ConnectionError("Network down"), mock_tx]

    with patch.object(provider.w3.eth, "get_transaction", side_effect=side_effect):
        with patch("tenacity.wait_exponential.__call__", return_value=0):
            tx = provider.get_transaction("0xabc")
            assert tx["hash"] == "0xabc"
            assert provider.w3.eth.get_transaction.call_count == 2
