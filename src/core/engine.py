import logging
import time
from sqlalchemy.orm import Session
from core.provider import BlockchainProvider
from core.sync import IntegrityGuard, ReorgException
from core.db_service import DatabaseService
from database.repository import BlockchainRepository
from domain.schemas import BlockModel, TransactionModel

logger = logging.getLogger(__name__)

class SyncEngine:
    def __init__(self, db: Session, provider: BlockchainProvider):
        self.db = db
        self.provider = provider
        self.repo = BlockchainRepository(db)
        self.guard = IntegrityGuard(self.repo)
        self.db_service = DatabaseService(self.repo)

    def get_start_block(self, default_start: int = 0) -> int:
        """Determine where to start syncing."""
        latest_in_db = self.repo.get_latest_block()
        if latest_in_db:
            return latest_in_db.number + 1
        return default_start

    def sync_block(self, block_number: int):
        """Fetch, validate, and save a single block."""
        try:
            logger.info(f"Syncing block {block_number}...")
            
            # 1. Fetch from RPC
            raw_block = self.provider.get_block(block_number, full_transactions=True)
            block_model = BlockModel.model_validate(dict(raw_block))
            
            # 2. Check Continuity (Reorg Detection)
            self.guard.validate_block_continuity(block_model)
            
            # 3. Save to DB (Atomic)
            self.repo.insert_block(block_model)
            
            # Optional: Save transactions
            for tx in raw_block.get('transactions', []):
                tx_model = TransactionModel.model_validate(dict(tx))
                self.repo.insert_transaction(tx_model)
            
            self.db.commit()
            logger.info(f"Successfully indexed block {block_number}")
            
        except ReorgException as e:
            logger.warning(f"Reorg detected: {e}. Rolling back...")
            # Rollback to the previous safe block
            self.db_service.rollback_to_block(e.block_number - 1)
            # The next iteration will retry from the safe height
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to sync block {block_number}: {e}")
            raise

    def run(self, start_block: int = None, poll_interval: int = 12):
        """Main indexing loop."""
        current_height = start_block if start_block is not None else self.get_start_block()
        
        logger.info(f"Starting sync engine from block {current_height}")
        
        while True:
            try:
                rpc_latest = self.provider.w3.eth.block_number
                
                if current_height <= rpc_latest:
                    self.sync_block(current_height)
                    current_height += 1
                else:
                    logger.debug(f"Reached chain tip ({rpc_latest}). Waiting...")
                    time.sleep(poll_interval)
                    
            except ReorgException:
                # Re-calculate height after rollback
                current_height = self.get_start_block()
            except Exception as e:
                logger.error(f"Loop error: {e}")
                time.sleep(poll_interval)
