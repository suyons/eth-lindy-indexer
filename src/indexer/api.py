from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from indexer.models.database import get_db
from indexer.models.repository import BlockchainRepository
from indexer.models.schemas import BlockModel

app = FastAPI(title="ETH Lindy Indexer API")

@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    Return the system health status.
    """
    return {"status": "ok", "service": "eth-lindy-indexer"}

@app.get("/blocks/latest", response_model=BlockModel)
def get_latest_block(db: Session = Depends(get_db)):
    """
    Return the highest block number and hash currently synced in the DB using Raw SQL.
    """
    repo = BlockchainRepository(db)
    latest_block = repo.get_latest_block()
    if not latest_block:
        raise HTTPException(status_code=404, detail="No blocks found in database")
    return latest_block