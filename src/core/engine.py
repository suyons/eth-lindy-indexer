import logging
import time
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue, Empty
from sqlalchemy.orm import Session
from core.provider import BlockchainProvider
from core.sync import IntegrityGuard, ReorgException
from core.db_service import DatabaseService
from database.repository import BlockchainRepository
from domain.schemas import BlockModel, TransactionModel, LogModel
from domain.decoder import LogDecoder

logger = logging.getLogger(__name__)


class SyncEngine:
    def __init__(self, db: Session, provider: BlockchainProvider, buffer_size: int = 10):
        self.db = db
        self.provider = provider
        self.repo = BlockchainRepository(db)
        self.guard = IntegrityGuard(self.repo)
        self.db_service = DatabaseService(self.repo)
        self.decoder = LogDecoder()
        
        # Pipelining tools
        self.buffer_size = buffer_size
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.block_buffer = PriorityQueue(maxsize=buffer_size)
        self.is_running = False

    def get_start_block(self, default_start: int = None) -> int:
        """Determine where to start syncing."""
        latest_in_db = self.repo.get_latest_block()
        if latest_in_db:
            return latest_in_db.number + 1

        if default_start is None:
            try:
                rpc_latest = self.provider.w3.eth.block_number
                return rpc_latest - 5
            except Exception:
                return 0
        return default_start

    def fetch_and_validate_block(self, block_number: int) -> dict:
        """
        Worker task: Fetch block + logs in parallel and validate Pydantic models.
        """
        # 1. Parallel RPC fetch for metadata and logs
        with ThreadPoolExecutor(max_workers=2) as inner_exec:
            f_block = inner_exec.submit(self.provider.get_block, block_number, full_transactions=True)
            f_logs = inner_exec.submit(self.provider.get_logs, {"fromBlock": block_number, "toBlock": block_number})
            
            raw_block = f_block.result()
            raw_logs = f_logs.result()

        # 2. Pydantic Validation & Serialization
        block_model = BlockModel.model_validate(dict(raw_block))
        
        txs_data = [
            TransactionModel.model_validate(dict(tx)).model_dump(by_alias=False)
            for tx in raw_block.get("transactions", [])
        ]
        
        logs_data = []
        for log in raw_logs:
            try:
                logs_data.append(LogModel.model_validate(dict(log)).model_dump(by_alias=False))
            except Exception:
                continue

        return {
            "block_number": block_number,
            "block_model": block_model,
            "txs_data": txs_data,
            "logs_data": logs_data
        }

    def _refill_buffer(self, start_height: int, rpc_latest: int):
        """Background task to keep the pre-fetch buffer full."""
        for bn in range(start_height, rpc_latest + 1):
            if not self.is_running:
                break
            try:
                # This will block if the buffer is full, effectively throttling the pre-fetcher
                if bn not in [item[0] for item in self.block_buffer.queue]:
                    processed = self.fetch_and_validate_block(bn)
                    self.block_buffer.put((bn, processed))
            except Exception as e:
                logger.error(f"Pre-fetch error for block {bn}: {e}")
                time.sleep(1) # Wait before retry

    def run(self, poll_interval: int = 5):
        """Main indexing loop: Pipelined and High-Speed."""
        current_height = self.get_start_block()
        logger.info(f"Starting PIPELINED sync engine from block {current_height}")
        self.is_running = True

        while self.is_running:
            try:
                rpc_latest = self.provider.w3.eth.block_number

                if current_height <= rpc_latest:
                    # Greedily process blocks until we reach rpc_latest
                    while current_height <= rpc_latest:
                        # 1. Fetch data (check buffer first, then fall back to direct fetch)
                        try:
                            # Try to get from buffer with a tiny timeout
                            bn, data = self.block_buffer.get(timeout=0.1)
                            if bn != current_height:
                                # Wrong block in buffer, discard and fetch directly
                                self.block_buffer = PriorityQueue(maxsize=self.buffer_size)
                                data = self.fetch_and_validate_block(current_height)
                        except Empty:
                            data = self.fetch_and_validate_block(current_height)

                        # 2. Trigger pre-fetching for next blocks in background
                        self.executor.submit(self._refill_buffer, current_height + 1, rpc_latest)

                        # 3. Integrity Check
                        self.guard.validate_block_continuity(data["block_model"])

                        # 4. Atomic Database Write
                        self.repo.insert_blocks_bulk([data["block_model"]])
                        if data["txs_data"]:
                            self.repo.insert_transactions_bulk(data["txs_data"])
                        if data["logs_data"]:
                            self.repo.insert_logs_bulk(data["logs_data"])
                            
                        self.db.commit()
                        logger.info(f"Indexed block {current_height} | {len(data['txs_data'])} txs | {len(data['logs_data'])} logs")
                        current_height += 1
                else:
                    # We are at the tip, wait for the next block
                    logger.debug(f"At chain tip. Waiting...")
                    time.sleep(poll_interval)

            except ReorgException as e:
                self.db.rollback()
                logger.warning(f"REORG detected at {e.block_number}. Resetting pipeline...")
                self.db_service.rollback_to_block(e.block_number - 1)
                # Clear buffer on reorg
                while not self.block_buffer.empty():
                    try: self.block_buffer.get_nowait()
                    except Empty: break
                current_height = self.get_start_block()
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Sync loop error: {e}")
                time.sleep(2)
                current_height = self.get_start_block()