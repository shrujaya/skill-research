# Task 2: Sales data cleanup — `sqlite3` sandbox

Base: `ubuntu:24.04`. Installs `sqlite3` and `python3` (stdlib only — agents may reach for it to
read CSVs). Runs as non-root user `agent`, working directory `/workspace`.

`orders.csv` is baked into the image at build time (via `generate_orders.py`, seed `42`), so
every container start has the identical, known-correct 200-row dataset.

## Clean run

```bash
docker run --rm -it --network none task2-data
```

## Broken run (fault injection)

Same image, no rebuild — mount `orders_broken.csv` over the good file at `docker run` time:

```bash
docker run --rm -it --network none \
  -v "$(pwd)/orders_broken.csv:/workspace/orders.csv:ro" \
  task2-data
```

`orders_broken.csv` is identical to `orders.csv` except one row (`ORD0123`, region West,
status completed) has its `amount` field replaced with `N/A` — tests whether the agent
detects and reports the malformed row rather than crashing or silently corrupting that
region's total.

## Deliberate traps in the data

- **`Central` region**: all 40 rows are `cancelled`. Decision (per spec, left open): regions
  with zero eligible orders after filtering are **omitted** from `summary.csv` entirely, not
  shown with `0.00` revenue. This is the rule the grader will assume.
- **Boundary rows**: 5 rows fixed at exactly `9.99` (must be excluded — "under $10") and 3
  rows fixed at exactly `10.00` (must be included — the boundary is inclusive).

## Regenerating the data

```bash
python3 generate_orders.py
```
Deterministic (fixed seed) — re-running reproduces byte-for-byte the same `orders.csv` and
`orders_broken.csv`, including which row gets corrupted.

## No answer key in this image

The correct `summary.csv` is intentionally **not** included here — baking an expected-output
file into the same filesystem the agent operates in would let it read the answer instead of
computing it. The reference output lives outside the container (host-side grading, added
later), never inside the image.
