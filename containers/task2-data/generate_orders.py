#!/usr/bin/env python3
"""Deterministic generator for orders.csv and orders_broken.csv (seeded — re-running
reproduces the same files byte-for-byte).

Deliberate traps for the sales-data-cleanup task:
- "Central" region has only cancelled orders (should contribute zero eligible revenue).
- Several rows fixed at exactly $9.99 (must be excluded: "under $10").
- Several rows fixed at exactly $10.00 (must be included: boundary is inclusive).

orders_broken.csv is identical to orders.csv except one row's amount field is replaced
with "N/A" — the fault for the broken sandbox variant (same image, bad file mounted
over the good one at `docker run` time).
"""
import copy
import csv
import random

random.seed(42)

REGIONS = ["North", "South", "East", "West", "Central"]
ROWS_PER_REGION = 40
BOUNDARY_UNDER = 9.99
BOUNDARY_AT = 10.00
NUM_UNDER_TRAPS = 5
NUM_AT_TRAPS = 3


def random_date():
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"2024-{month:02d}-{day:02d}"


def random_amount():
    return round(random.uniform(5.00, 500.00), 2)


def build_rows():
    rows = []
    order_id = 1
    for region in REGIONS:
        for _ in range(ROWS_PER_REGION):
            if region == "Central":
                status = "cancelled"
            else:
                status = "cancelled" if random.random() < 0.15 else "completed"
            rows.append({
                "order_id": f"ORD{order_id:04d}",
                "region": region,
                "amount": random_amount(),
                "status": status,
                "order_date": random_date(),
            })
            order_id += 1
    return rows


def inject_boundary_traps(rows):
    candidates = [r for r in rows if r["region"] != "Central" and r["status"] == "completed"]
    random.shuffle(candidates)
    for r in candidates[:NUM_UNDER_TRAPS]:
        r["amount"] = BOUNDARY_UNDER
    for r in candidates[NUM_UNDER_TRAPS:NUM_UNDER_TRAPS + NUM_AT_TRAPS]:
        r["amount"] = BOUNDARY_AT
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "region", "amount", "status", "order_date"])
        writer.writeheader()
        writer.writerows(rows)


def pick_corruption_target(rows):
    for r in rows:
        if r["region"] != "Central" and r["status"] == "completed" and r["amount"] not in (
            f"{BOUNDARY_UNDER:.2f}", f"{BOUNDARY_AT:.2f}"
        ):
            return r
    raise RuntimeError("no eligible row found to corrupt")


def main():
    rows = build_rows()
    inject_boundary_traps(rows)
    random.shuffle(rows)

    for r in rows:
        r["amount"] = f"{r['amount']:.2f}"

    write_csv("orders.csv", rows)
    print(f"Wrote {len(rows)} rows to orders.csv")

    broken_rows = copy.deepcopy(rows)
    target = pick_corruption_target(broken_rows)
    target["amount"] = "N/A"
    write_csv("orders_broken.csv", broken_rows)
    print(f"Wrote orders_broken.csv (corrupted amount on {target['order_id']}, region={target['region']})")


if __name__ == "__main__":
    main()
