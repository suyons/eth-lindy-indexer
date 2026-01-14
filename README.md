# 🏛️ ETH Lindy Indexer

> **"Data is better than code. Correctness is more important than performance."** > — _The Lindy Philosophy of Resilient Infrastructure_

### 📖 The Philosophy

Named after the **Lindy Effect**, this indexer is built on the principle that blockchain data infrastructure must be as enduring and robust as the protocol it tracks. In an ecosystem of "move fast and break things," **ETH Lindy Indexer** prioritizes **Data Integrity** and **Historical Consistency**.

Most indexers fail when the chain reorganizes or the RPC returns "dirty" data. Leveraging years of Enterprise System Integration (SI) experience, this project treats the Ethereum blockchain not as a simple stream, but as a complex financial ledger requiring **Atomic Reconciliation**.

---

### 🚀 Key Features

- **Atomic Reorg Protection:** Implements a recursive rollback mechanism that ensures the database stays perfectly synced even during deep chain reorganizations.
- **Pydantic Guardrails:** Uses strict schema validation to catch malformed RPC responses before they touch the persistence layer.
- **High-Precision Accounting:** Utilizes `Decimal(78, 0)` to handle Wei-level accuracy, preventing the rounding errors common in junior-level financial apps.
- **Enterprise Scaffolding:** Organized using the professional `src/` layout with comprehensive unit tests for core sync logic.

---

### 🛠️ Tech Stack

- **Language:** Python 3.11+ (Typed)
- **Validation:** Pydantic v2
- **Blockchain:** Web3.py (JSON-RPC)
- **Database:** PostgreSQL + SQLAlchemy (ORM/Core)
- **Testing:** Pytest (Mocks & Integration)

---

### 🏗️ System Architecture

The ETH Lindy Indexer is architected to ensure data integrity at every step of the indexing process:

1. **Data Ingestion:** Connects to Ethereum nodes via JSON-RPC, fetching blocks and transactions.
2. **Validation Layer:** Each fetched block is validated against Pydantic schemas to ensure data correctness.
3. **Reconciliation Engine:** Implements a rollback mechanism to handle chain reorganizations, ensuring atomic updates to the database.
4. **Persistence Layer:** Uses SQLAlchemy to interact with PostgreSQL, ensuring high-precision storage of financial data.
5. **Testing Suite:** Comprehensive unit and integration tests to validate core functionalities and edge cases.
