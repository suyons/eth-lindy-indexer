# ETH Lindy Indexer

A high-reliability Ethereum event indexer in Python that ensures data integrity through Pydantic validation and handles chain reorganizations via atomic SQL transactions.

## 🏗 System Architecture

```mermaid
graph TD
    RPC[Ethereum RPC Node] --> |Raw Data| Provider[Resilient Blockchain Provider]
    Provider --> |Retry Logic| Provider
    Provider --> |Block/Log JSON| Pydantic[Pydantic Validation]
    Pydantic --> |Validated Models| Sync[Sync Service]
    Sync --> |Parent Hash Check| Integrity[Integrity Guard]
    Integrity --> |Mismatch Detected| Rollback[Recursive Rollback Service]
    Integrity --> |Continuous| DB[(PostgreSQL Database)]
    DB --> |Persistence| API[FastAPI Service]
    API --> |JSON Responses| User[End User]
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/suyons/eth-lindy-indexer.git
   cd eth-lindy-indexer
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies (Editable Install):**
   ```bash
   pip install -e ".[dev]"
   ```

### Configuration

Create a `.env` file in the root directory based on `.env.example`:

```env
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your-api-key
DATABASE_URL=postgresql://user:password@localhost:5432/lindy_indexer
RETRY_MAX_ATTEMPTS=5
```

## 🛠 Usage

### Running the API

```bash
uvicorn indexer.api:app --reload
```

The API will be available at `http://localhost:8000`.

- Health Check: `GET /health`
- Latest Block: `GET /blocks/latest`

### Running Tests

```bash
pytest
```

## 🔒 Data Integrity Features

- **Pydantic Validation:** All data from the blockchain is validated against strict schemas before being processed.
- **Integrity Guard:** Every new block's `parent_hash` is verified against the database to detect chain reorganizations.
- **Atomic Rollback:** If a reorg is detected, the system performs an atomic recursive rollback to the last known consistent block.
- **High-Precision Math:** Wei values are handled using Python's `Decimal` type with 80 digits of precision to avoid floating-point errors.
