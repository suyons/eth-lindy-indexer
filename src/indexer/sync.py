import logging
from indexer.models.repository import BlockchainRepository
from indexer.models.schemas import BlockModel

logger = logging.getLogger(__name__)

class ReorgException(Exception):
    """Raised when a chain reorganization is detected."""
    def __init__(self, block_number: int, expected_parent_hash: str, actual_parent_hash: str):
        self.block_number = block_number
        self.expected_parent_hash = expected_parent_hash
        self.actual_parent_hash = actual_parent_hash
        super().__init__(
            f"Reorg detected at block {block_number}. "
            f"Expected parent hash {expected_parent_hash}, but got {actual_parent_hash}"
        )

class IntegrityGuard:
    def __init__(self, repository: BlockchainRepository):
        self.repo = repository

    def validate_block_continuity(self, new_block: BlockModel) -> bool:
        """
        Verify that the new block's parent hash matches the hash of the previous block in the DB.
        
        Returns:
            True if continuous.
        Raises:
            ReorgException: If a mismatch is detected.
        """
        previous_block_number = new_block.number - 1
        
        # Use Raw SQL via Repository
        previous_block = self.repo.get_block_by_number(previous_block_number)
        
        if not previous_block:
            logger.info(f"No previous block found in DB for height {previous_block_number}. Skipping continuity check.")
            return True

        if previous_block.hash != new_block.parent_hash:
            logger.error(
                f"Integrity check failed for block {new_block.number}. "
                f"DB Hash: {previous_block.hash}, New Block Parent Hash: {new_block.parent_hash}"
            )
            raise ReorgException(
                block_number=new_block.number,
                expected_parent_hash=previous_block.hash,
                actual_parent_hash=new_block.parent_hash
            )

        logger.debug(f"Block {new_block.number} passed integrity check.")
        return True