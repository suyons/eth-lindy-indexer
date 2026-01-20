import logging
from typing import Any, Dict, Optional, Union

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from web3 import Web3
from web3.exceptions import Web3Exception
from web3.types import BlockData, TxData

from core.config import settings

logger = logging.getLogger(__name__)

class BlockchainProvider:
    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or settings.rpc_url
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
    def is_connected(self) -> bool:
        return self.w3.is_connected()

    @retry(
        retry=retry_if_exception_type((Web3Exception, ConnectionError, Exception)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(settings.retry_max_attempts),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def get_block(self, block_identifier: Union[int, str], full_transactions: bool = False) -> BlockData:
        """
        Fetch a block by number or hash with retry logic.
        """
        try:
            block = self.w3.eth.get_block(block_identifier, full_transactions)
            if not block:
                raise Web3Exception(f"Block {block_identifier} not found")
            return block
        except Exception as e:
            logger.error(f"Error fetching block {block_identifier}: {e}")
            raise

    @retry(
        retry=retry_if_exception_type((Web3Exception, ConnectionError, Exception)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(settings.retry_max_attempts),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def get_transaction(self, tx_hash: str) -> TxData:
        """
        Fetch a transaction by hash with retry logic.
        """
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            if not tx:
                raise Web3Exception(f"Transaction {tx_hash} not found")
            return tx
        except Exception as e:
            logger.error(f"Error fetching transaction {tx_hash}: {e}")
            raise

    @retry(
        retry=retry_if_exception_type((Web3Exception, ConnectionError, Exception)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(settings.retry_max_attempts),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def get_logs(self, filter_params: Dict[str, Any]) -> list:
        """
        Fetch logs with retry logic.
        """
        try:
            return self.w3.eth.get_logs(filter_params)
        except Exception as e:
            logger.error(f"Error fetching logs with params {filter_params}: {e}")
            raise
