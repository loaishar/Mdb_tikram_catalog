Mdb_tikram_catalog

Overview
- Scripts and data to prepare and import a product catalog into MongoDB, including translations and offers.
- Repository cleaned and organized into clear folders for data, scripts, and docs.

Layout
- `scripts/`: All Python utilities and batch processors.
- `data/`
  - `imports/`: Source import files
    - `final/`: Finalized import batches
    - `chunks/`: Chunked import segments
    - `ready/`: Ready-for-import batches
  - `batches/`: Intermediate/generated batches
    - `products/`, `offers/`, `mongo/`, `misc/`
  - `updates/`: Update payloads
    - `arabic/`: Arabic-specific updates
    - `core/`: General updates (including `mongodb_updates*.json`)
  - `status/`: Import status snapshots
  - `mappings/`: ID mappings and translation maps
  - `tests/`: Test JSON payloads
  - `raw/`: Raw external files (e.g., spreadsheets)
- `docs/`: Documentation and notes.

Running Scripts
- Scripts were moved to `scripts/`. If a script used to refer to files by name in the repo root (e.g., `products_batch_1.json`), update paths to the new locations under `data/`.
- Example (Python):
  - Old: `open('products_batch_1.json')`
  - New: `open('data/batches/products/products_batch_1.json')`
- Tip: Build paths relative to the repo root to avoid issues when running from different working directories.

Conventions
- Keep large, raw inputs in `data/raw/`.
- Place transient outputs in `data/batches/` and commit only what’s needed for reproducibility.
- Prefer small, incremental JSON batches for reviewability.

Notes
- `.gitignore` updated to exclude common OS/editor and Python artifacts.
- See `docs/` for schema notes and import summaries.

