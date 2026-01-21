import logging
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
        self.db.execute(sql, block.model_dump())

    def get_latest_block(self) -> Optional[BlockModel]:
        sql = text("SELECT * FROM blocks ORDER BY number DESC LIMIT 1")
        result = self.db.execute(sql).mappings().first()
        if result:
            return BlockModel.model_validate(dict(result))
        return None

    def get_block_by_number(self, number: int) -> Optional[BlockModel]:
        sql = text("SELECT * FROM blocks WHERE number = :number")
        result = self.db.execute(sql, {"number": number}).mappings().first()
        if result:
            return BlockModel.model_validate(dict(result))
        return None

    def insert_transaction(self, tx: TransactionModel):
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
        # TransactionModel uses 'from' alias, so we use model_dump(by_alias=False)
        # or map manually if needed. Pydantic v2 handles this well.
        data = tx.model_dump()
        # Ensure 'from' is mapped to 'from_address' if not using aliases in SQL
        self.db.execute(sql, data)

    def insert_log(self, log: LogModel):
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
        data = log.model_dump()
        # For SQLite/JSON handling, we might need to serialize topics
        import json

        data["topics"] = json.dumps(data["topics"])
        self.db.execute(sql, data)

    def rollback_from_height(self, block_number: int):
        """Delete all data from a certain height onwards (Atomic Reorg Handling)."""
        # SQLAlchemy Session handles the transaction atomicity
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
