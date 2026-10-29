# Pipeline

Phase 1. `ingest.py` appends each generator batch to `bronze`; `dbt/` builds `silver` and `gold`; `checks/` compares today with yesterday and alerts on failures. Rules: [docs/standards/data-modeling.md](../docs/standards/data-modeling.md).

## Ingestion (`ingest.py`)

```bash
python generator/generate.py --seed 42 --days 3   # makes data/raw/as_of=<date>/ folders
python pipeline/ingest.py                         # loads them into data/lakehouse.duckdb
```

- Each `as_of=<date>` folder is one batch. Each CSV is appended to `bronze.<source>_<object>` (for example `crm/deals.csv` becomes `bronze.crm_deals`) with `_loaded_at`, `_source` and `_batch_id` added.
- Bronze mirrors the source: every column stays text and nothing is cleaned. Because each batch is a full export, bronze holds every version of a row; silver keeps the latest.
- Running it twice loads nothing new. Each batch loads in one transaction together with its row in `bronze._ingestion_log`, so a failed batch leaves nothing behind and can be retried.
- Only this script writes to bronze.

## Silver (`dbt/`)

```bash
cd pipeline/dbt
dbt build --profiles-dir .     # builds silver and runs its tests on data/lakehouse.duckdb
```

- One model per entity in `dbt/models/silver/`, in the `silver` schema (`silver.company`, `silver.deal`, ...). Each one keeps only the latest version of every row (the `latest_version` macro) and gives columns their real types.
- Data-quality problems are flagged, not deleted: `company.is_possible_duplicate`, `deal.has_company`, `subscription.has_matching_deal`. Deciding what to do with them is a business rule.
- `dbt/models/silver/schema.yml` describes every model and column; those descriptions are the catalog the agent reads. Every table has a tested primary key.
- Set `LAKEHOUSE_PATH` to point dbt at another DuckDB file.
