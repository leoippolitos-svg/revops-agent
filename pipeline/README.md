# Pipeline

Phase 1. `ingest.py` appends each generator batch to `bronze`; `dbt/` builds `silver` and `gold`; `checks/` compares today with yesterday and alerts on failures. Rules: [docs/standards/data-modeling.md](../docs/standards/data-modeling.md).
