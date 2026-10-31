# App name

## What it is
One paragraph: who reads it, which decision it supports, what it does not do.

## How to run it
`python apps/<app-name>/app.py --out page.html`. No environment variable is needed: it reads the local lakehouse read-only.

## Data
The gold tables in `SPEC.md`, through `query_gold`. How each number is computed: the report context document for this app.

## Tests
`tests/test_<app_name>.py`. Start from `apps/_template/tests_template.py`: main path, empty result, stale data, escaping, no form and no script.

## Owner and status
The role that owns it; built or not, with the date.
