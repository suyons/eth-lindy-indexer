# ETH Lindy Indexer

A high-reliability Ethereum event indexer in Python that ensures data integrity through Pydantic validation and handles chain reorganizations via atomic SQL transactions using a **Raw SQL Repository**.

## 🏗 System Architecture

```mermaid
graph TD
    RPC[Ethereum RPC Node] --> |Raw Data| Provider[Resilient Blockchain Provider]
    Provider --> |Retry Logic| Provider
    Provider --> |Block/Log JSON| Pydantic[Pydantic Validation]
    Pydantic --> |Validated Models| Sync[Sync Service]
    Sync --> |Continuity Check| Repo[Raw SQL Repository]
    Repo --> |Raw SQL / text| DB[(PostgreSQL Database)]
    DB --> |Persistence| API[FastAPI Service]
    API --> |Latest Block| Repo
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

2. **Setup Environment:**
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

### Configuration

Create a `.env` file based on `.env.example`:

```env
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your-api-key
DATABASE_URL=postgresql://user:password@localhost:5432/lindy_indexer
RETRY_MAX_ATTEMPTS=5
```

## 🛠 Usage

### Running the API

```bash
uv run uvicorn api.router:app --reload
```

### Running Tests

```bash
pytest
```

## 🔒 Data Integrity & Implementation Style

- **Raw SQL Repository:** Direct control over SQL performance and clarity using `sqlalchemy.text()` and Pydantic for result mapping.
- **Pydantic Validation:** Strict schema enforcement for all blockchain data.
- **Integrity Guard:** Parent hash verification against the database to detect reorgs.
- **High-Precision Math:** 80-digit decimal precision for all Wei calculations.
