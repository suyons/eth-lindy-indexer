# PRD: ETH Lindy Indexer

## 1. Project Objective

Build a high-reliability Ethereum event indexer in Python that ensures **data integrity** in a PostgreSQL database. The system must handle "Dirty Data" via **Pydantic validation** and "Chain Reorganizations" (Reorgs) via **Atomic SQL Transactions**.

## 2. Technical Stack

- **Language:** Python 3.11+ (Strict type hinting required)
- **Data Validation:** **Pydantic v2** (For robust schema enforcement)
- **Architecture:** **Standard `src/` layout** (Decouples code from configuration)
- **Blockchain Lib:** Web3.py
- **Database:** PostgreSQL + SQLAlchemy (ORM/Core)
- **Testing:** **Pytest** (With unit and integration mocks)
- **Environment:** `python-dotenv` for secret management

---

## 3. Project Phases & Core Logic

### Phase 1: Infrastructure & "Src" Layout (Week 1)

- **Task 1.1: Standardized Scaffolding.** Setup the `/src/indexer` and `/tests` directories. Use `pyproject.toml` or `requirements.txt` to manage dependencies.
- **Task 1.2: Pydantic Data Models.** Create `models.py` defining schemas for `Block`, `Transaction`, and `Log`. Use Pydantic to validate hex strings and block numbers.
- **Task 1.3: RPC Provider Module.** Implement a `Provider` class in `provider.py` with an exponential backoff retry mechanism for failed RPC calls.

### Phase 2: The "Reorg-Proof" Database (Week 2)

- **Task 2.1: Atomic Schema Design.** Create migrations for `blocks` and `transactions` tables. Ensure `parent_hash` is indexed for fast integrity checks.
- **Task 2.2: The Integrity Guard.** Implement logic to verify the `parent_hash` of every new block against the DB's latest record before commit.
- **Task 2.3: Recursive Rollback.** Build a service that can delete the last blocks and all associated transactions in a single atomic DB transaction if a reorg is detected.

### Phase 3: Event Extraction & Validation (Week 3)

- **Task 3.1: Log Decoder.** Create a module to decode ERC-20 `Transfer` events. Use Pydantic to cast raw hex data into structured objects.
- **Task 3.2: Precision Math.** Ensure all Wei values are handled as high-precision decimals to avoid the common junior mistake of "floating point errors."

### Phase 4: Production API & Readiness (Week 4)

- **Task 4.1: FastAPI Service.** Expose the data via endpoints (e.g., `/health`, `/blocks/latest`).
- **Task 4.2: CI/CD & Docs.** Setup a Pytest suite that runs on every save. Write a README that includes a **System Architecture Diagram** and instructions for an "Editable Install" (`pip install -e .`).
