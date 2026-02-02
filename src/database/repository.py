import logging
import json
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from domain.schemas import BlockModel, LogModel, TransactionModel

logger = logging.getLogger(__name__)


class BlockchainRepository:
    """
    Raw SQL Repository using Raw SQL via SQLAlchemy Core.
    This provides direct control over SQL performance and clarity.
    """

    def __init__(self, db: Session):
        self.db = db

    def insert_block(self, block: BlockModel):
        logger.info(f"Executing Raw SQL: INSERT INTO blocks (number={block.number})")
        sql = text(
            """
            INSERT INTO blocks (
                number, hash, parent_hash, timestamp, miner, 
                difficulty, total_difficulty, size, extra_data, 
                gas_limit, gas_used, base_fee_per_gas
            ) VALUES (
                :number, :hash, :parent_hash, :timestamp, :miner, 
                :difficulty, :total_difficulty, :size, :extra_data, 
                :gas_limit, :gas_used, :base_fee_per_gas
            )
            ON CONFLICT (number) DO NOTHING
        """
        )
        self.db.execute(sql, block.model_dump(by_alias=False))

    def get_latest_block(self) -> Optional[BlockModel]:
        logger.debug(
            "Executing Raw SQL: SELECT * FROM blocks ORDER BY number DESC LIMIT 1"
        )
        sql = text("SELECT * FROM blocks ORDER BY number DESC LIMIT 1")
        result = self.db.execute(sql).mappings().first()
        if result:
            return BlockModel.model_validate(dict(result))
        return None

    def get_block_by_number(self, number: int) -> Optional[BlockModel]:
        logger.debug(f"Executing Raw SQL: SELECT * FROM blocks WHERE number = {number}")
        sql = text("SELECT * FROM blocks WHERE number = :number")
        result = self.db.execute(sql, {"number": number}).mappings().first()
        if result:
            return BlockModel.model_validate(dict(result))
        return None

    def insert_transaction(self, tx: TransactionModel):
        logger.info(f"Executing Raw SQL: INSERT INTO transactions (hash={tx.hash})")
        sql = text(
            """
            INSERT INTO transactions (
                hash, nonce, block_hash, block_number, transaction_index, 
                from_address, to_address, value, gas_price, gas, input
            ) VALUES (
                :hash, :nonce, :block_hash, :block_number, :transaction_index, 
                :from_address, :to_address, :value, :gas_price, :gas, :input
            )
            ON CONFLICT (hash) DO NOTHING
        """
        )
        self.db.execute(sql, tx.model_dump(by_alias=False))

    def insert_log(self, log: LogModel):
        logger.info(
            f"Executing Raw SQL: INSERT INTO logs (log_index={log.log_index}, tx_hash={log.transaction_hash})"
        )
        sql = text(
            """
            INSERT INTO logs (
                log_index, transaction_hash, address, data, 
                topics, block_number, block_hash
            ) VALUES (
                :log_index, :transaction_hash, :address, :data, 
                :topics, :block_number, :block_hash
            )
        """
        )
        data = log.model_dump(by_alias=False)
        if isinstance(data["topics"], list):
            data["topics"] = json.dumps(data["topics"])
        self.db.execute(sql, data)

    def rollback_from_height(self, block_number: int):
        """Delete all data from a certain height onwards (Atomic Reorg Handling)."""
        logger.warning(
            f"Executing Raw SQL: DELETE FROM ... WHERE block_number >= {block_number}"
        )
        self.db.execute(
            text("DELETE FROM logs WHERE block_number >= :num"), {"num": block_number}
        )
        self.db.execute(
            text("DELETE FROM transactions WHERE block_number >= :num"),
            {"num": block_number},
        )
        self.db.execute(
            text("DELETE FROM blocks WHERE number >= :num"), {"num": block_number}
        )
