import logging
from typing import Any, Dict, List, Optional

from web3 import Web3
from web3._utils.events import get_event_data

from domain.schemas import TransferEvent

logger = logging.getLogger(__name__)

# Minimal ERC-20 ABI for Transfer event
ERC20_TRANSFER_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "from", "type": "address"},
        {"indexed": True, "name": "to", "type": "address"},
        {"indexed": False, "name": "value", "type": "uint256"},
    ],
    "name": "Transfer",
    "type": "event",
}

TRANSFER_EVENT_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

class LogDecoder:
    def __init__(self):
        self.w3 = Web3()
        self.transfer_abi = ERC20_TRANSFER_ABI

    def decode_transfer_log(self, log: Dict[str, Any]) -> Optional[TransferEvent]:
        """
        Decode a single log entry if it matches the ERC-20 Transfer event signature.
        """
        try:
            if not log.get("topics") or log["topics"][0] != TRANSFER_EVENT_TOPIC:
                return None

            # Prepare log for web3.py helper
            log_for_web3 = dict(log)
            if "transactionIndex" not in log_for_web3:
                log_for_web3["transactionIndex"] = 0
            if "blockHash" not in log_for_web3:
                log_for_web3["blockHash"] = "0x" + "0" * 64
            if "address" not in log_for_web3:
                log_for_web3["address"] = "0x" + "0" * 40
            
            decoded_data = get_event_data(self.w3.codec, self.transfer_abi, log_for_web3)
            args = decoded_data["args"]
            
            tx_hash = log.get("transactionHash")
            if tx_hash:
                tx_hash = tx_hash if isinstance(tx_hash, str) else tx_hash.hex()
            else:
                tx_hash = "0x" + "0" * 64

            return TransferEvent(
                from_address=args["from"],
                to_address=args["to"],
                value=args["value"],
                transaction_hash=tx_hash,
                block_number=log.get("blockNumber", 0),
                log_index=log.get("logIndex", 0)
            )
        except Exception as e:
            logger.error(f"Failed to decode log: {e}")
            return None

    def decode_batch(self, logs: List[Dict[str, Any]]) -> List[TransferEvent]:
        """Decode a list of logs and return only valid TransferEvents."""
        decoded_events = []
        for log in logs:
            event = self.decode_transfer_log(log)
            if event:
                decoded_events.append(event)
        return decoded_events