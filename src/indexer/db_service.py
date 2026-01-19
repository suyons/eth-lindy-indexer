import logging
from sqlalchemy import delete
from sqlalchemy.orm import Session
from indexer.models.orm import Block, Transaction, Log

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    def rollback_to_block(self, target_block_number: int) -> int:
        """
        Delete all blocks, transactions, and logs starting from target_block_number.
        
        Args:
            target_block_number: The first block number to be deleted.
            
        Returns:
            The number of blocks deleted.
        """
        try:
            # We rely on SQLAlchemy's cascade delete for Transactions and Logs
            # defined in the ORM models.
            
            # Find all blocks to be deleted
            blocks_to_delete = self.db.query(Block).filter(Block.number >= target_block_number).all()
            num_deleted = len(blocks_to_delete)
            
            if num_deleted > 0:
                logger.info(f"Rolling back {num_deleted} blocks starting from {target_block_number}")
                
                # We can delete blocks one by one to trigger ORM cascades, 
                # or use a bulk delete if we handle relations manually.
                # Since we use 'delete-orphan' cascades on relationships, 
                # we should delete the Block objects.
                
                for block in blocks_to_delete:
                    self.db.delete(block)
                
                self.db.commit()
                logger.info(f"Successfully rolled back to block {target_block_number - 1}")
            else:
                logger.info(f"No blocks found to rollback for height >= {target_block_number}")
            
            return num_deleted
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during rollback to block {target_block_number}: {e}")
            raise
