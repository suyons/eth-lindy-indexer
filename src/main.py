import logging
import sys
import threading
import uvicorn
from database.connection import SessionLocal
from core.provider import BlockchainProvider
from core.engine import SyncEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def run_sync_engine():
    """Function to run the sync engine in a background thread."""
    db = SessionLocal()
    try:
        provider = BlockchainProvider()
        engine = SyncEngine(db, provider)
        engine.run()
    except Exception as e:
        logger.error(f"Sync Engine crashed: {e}")
    finally:
        db.close()

def main():
    logger.info("Starting ETH Lindy Indexer (Combined Mode)...")
    
    # 1. Start Sync Engine in a background daemon thread
    sync_thread = threading.Thread(target=run_sync_engine, daemon=True)
    sync_thread.start()
    logger.info("Background Sync Engine started.")

    # 2. Start FastAPI Server in the main thread
    # We use the string import to avoid issues with reload and threading if needed
    uvicorn.run("api.router:app", host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()