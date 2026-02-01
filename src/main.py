import logging
import sys
from database.connection import SessionLocal
from core.provider import BlockchainProvider
from core.engine import SyncEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def main():
    db = SessionLocal()
    provider = BlockchainProvider()
    
    engine = SyncEngine(db, provider)
    
    # You can specify a start block here or let it auto-detect from DB
    try:
        engine.run()
    except KeyboardInterrupt:
        logging.info("Indexer stopped by user.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
