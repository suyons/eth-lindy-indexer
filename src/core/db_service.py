import logging

from database.repository import BlockchainRepository

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, repository: BlockchainRepository):
        self.repo = repository

    def rollback_to_block(self, target_block_number: int):
        """
        Delete all blocks, transactions, and logs starting from target_block_number.
        
        Args:
            target_block_number: The first block number to be deleted.
        """
        try:
            logger.info(f"Triggering rollback starting from block height {target_block_number}")
            
            # Use Raw SQL via Repository
            self.repo.rollback_from_height(target_block_number)
            
            # Ensure the session associated with the repository is committed
            self.repo.db.commit()
            
            logger.info(f"Successfully rolled back database to block {target_block_number - 1}")
            
        except Exception as e:
            self.repo.db.rollback()
            logger.error(f"Error during rollback to block {target_block_number}: {e}")
            raise