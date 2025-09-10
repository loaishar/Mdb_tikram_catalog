Repository Structure

- scripts/: Python scripts for imports, updates, and utilities.
- data/
  - imports/
    - final/, chunks/, ready/
  - batches/
    - products/, offers/, mongo/, misc/
  - updates/
    - arabic/, core/
  - status/
  - mappings/
  - tests/
  - raw/
- docs/: Documentation, schema, and notes.

Rationale
- Group related data to reduce clutter and make it easy to find inputs vs generated batches vs updates.
- Enable cleaner diffs by keeping large raw files isolated.

