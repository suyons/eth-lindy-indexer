import json
import logging
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from domain.schemas import BlockModel

logger = logging.getLogger(__name__)


class BlockchainRepository:
    """
    High-performance Raw SQL Repository.
    Uses optimized multi-row insertions for maximum throughput.
    """

    def __init__(self, db: Session):
        self.db = db

    def insert_blocks_bulk(self, blocks: List[BlockModel]):
        if not blocks:
            return
        logger.debug(f"Executing Raw SQL: Bulk INSERT {len(blocks)} blocks")
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
        self.db.execute(sql, [b.model_dump(by_alias=False) for b in blocks])

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

    def insert_transactions_bulk(self, transactions_data: List[dict]):
        """Fastest multi-row insert for transactions."""
        if not transactions_data:
            return
        logger.debug(
            f"Executing Raw SQL: Bulk INSERT {len(transactions_data)} transactions"
        )
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
        # SQLAlchemy + Psycopg2 will optimize this into a single efficient command
        self.db.execute(sql, transactions_data)

    def insert_logs_bulk(self, logs_data: List[dict]):
        """Fastest multi-row insert for logs."""
        if not logs_data:
            return
        logger.debug(f"Executing Raw SQL: Bulk INSERT {len(logs_data)} logs")
        sql = text(
            """
            INSERT INTO logs (
                log_index, transaction_hash, address, data, 
                topics, block_number, block_hash
            ) VALUES (
                :log_index, :transaction_hash, :address, :data, 
                CAST(:topics AS jsonb), :block_number, :block_hash
            )
        """
        )

        # Ensure topics are serialized to JSON strings for PostgreSQL jsonb column
        for data in logs_data:
            if "topics" in data and isinstance(data["topics"], (list, dict)):
                data["topics"] = json.dumps(data["topics"])

        self.db.execute(sql, logs_data)

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
