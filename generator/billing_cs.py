"""Billing and Customer Success data for the Fernway generator.

Everything here grows out of won deals: a won deal becomes a subscription, a
subscription produces monthly invoices and payments, and Customer Success
tracks onboarding, health and tickets for the customers that bought.

These functions take the clean deals and return rows. They do not write files;
generate.py does that, so there is one place that writes output.
"""

import random
from datetime import date, timedelta

# Last day of the simulated world. Nothing happens after it. Invoices stop here
# and recent invoices stay unpaid because their due date is still ahead.
WORLD_END = date(2026, 12, 31)

DAYS_PER_MONTH = 30  # billing every 30 days keeps dates simple and predictable
SHARE_CHURNED = 0.15
SHARE_OVERDUE = 0.10  # of invoices that are past due

PLAN_BY_SEGMENT = {"smb": "starter", "mid_market": "growth", "enterprise": "scale"}
MILESTONES = ["kickoff", "configured", "go_live"]
TICKET_PRIORITIES = ["low", "medium", "high"]
TICKET_CATEGORIES = ["bug", "how_to", "billing", "integration", "feature_request"]


def make_subscriptions(rng: random.Random, deals: list[dict], companies: list[dict]) -> list[dict]:
    """One subscription per won deal. Call this on clean deals."""
    segment_of = {c["company_id"]: c["segment"] for c in companies}
    subscriptions = []
    for deal in deals:
        if deal["stage"] != "closed_won":
            continue
        started = date.fromisoformat(deal["closed_at"]) + timedelta(days=rng.randint(0, 14))
        ended = ""
        status = "active"
        if rng.random() < SHARE_CHURNED:
            end_day = started + timedelta(days=rng.randint(60, 300))
            if end_day <= WORLD_END:
                status, ended = "churned", end_day.isoformat()
        subscriptions.append({
            "subscription_id": len(subscriptions) + 1,
            "deal_id": deal["deal_id"],
            "company_id": deal["company_id"],
            "plan": PLAN_BY_SEGMENT[segment_of[deal["company_id"]]],
            # The deal amount is a yearly contract value, so one month is a twelfth.
            "mrr_usd": round(int(deal["amount_usd"]) / 12),
            "status": status,
            "started_at": started.isoformat(),
            "ended_at": ended,
        })
    return subscriptions


def last_active_day(subscription: dict) -> date:
    return date.fromisoformat(subscription["ended_at"]) if subscription["ended_at"] else WORLD_END


def make_invoices_and_payments(rng: random.Random, subscriptions: list[dict]) -> tuple[list[dict], list[dict]]:
    invoices, payments = [], []
    for sub in subscriptions:
        issued = date.fromisoformat(sub["started_at"])
        while issued <= last_active_day(sub):
            due = issued + timedelta(days=DAYS_PER_MONTH)
            if due > WORLD_END:
                status = "open"  # not due yet, so it is neither paid nor overdue
            else:
                status = "overdue" if rng.random() < SHARE_OVERDUE else "paid"
            invoice_id = len(invoices) + 1
            invoices.append({
                "invoice_id": invoice_id,
                "subscription_id": sub["subscription_id"],
                "issued_at": issued.isoformat(),
                "due_at": due.isoformat(),
                "amount_usd": sub["mrr_usd"],
                "status": status,
            })
            if status == "paid":
                payments.append({
                    "payment_id": len(payments) + 1,
                    "invoice_id": invoice_id,
                    "paid_at": (issued + timedelta(days=rng.randint(0, DAYS_PER_MONTH))).isoformat(),
                    "amount_usd": sub["mrr_usd"],
                })
            issued += timedelta(days=DAYS_PER_MONTH)
    return invoices, payments


def make_onboarding_milestones(rng: random.Random, subscriptions: list[dict]) -> list[dict]:
    rows = []
    for sub in subscriptions:
        reached = date.fromisoformat(sub["started_at"])
        # Most customers complete onboarding; some stop part way.
        steps = len(MILESTONES) if rng.random() > 0.15 else rng.randint(1, len(MILESTONES) - 1)
        for milestone, max_gap in zip(MILESTONES[:steps], (5, 20, 40)):
            reached += timedelta(days=rng.randint(1, max_gap))
            if reached > last_active_day(sub):
                break
            rows.append({
                "milestone_id": len(rows) + 1,
                "subscription_id": sub["subscription_id"],
                "milestone": milestone,
                "reached_at": reached.isoformat(),
            })
    return rows


def make_health_scores(rng: random.Random, subscriptions: list[dict]) -> list[dict]:
    """A monthly health score per active subscription, from 0 (at risk) to 100."""
    rows = []
    for sub in subscriptions:
        scored = date.fromisoformat(sub["started_at"]) + timedelta(days=DAYS_PER_MONTH)
        level = rng.randint(40, 90)
        while scored <= last_active_day(sub):
            # The score drifts a little each month instead of jumping at random.
            level = max(0, min(100, level + rng.randint(-10, 8)))
            rows.append({
                "score_id": len(rows) + 1,
                "company_id": sub["company_id"],
                "scored_at": scored.isoformat(),
                "score": level,
                "band": "red" if level < 40 else "yellow" if level < 70 else "green",
            })
            scored += timedelta(days=DAYS_PER_MONTH)
    return rows


def make_tickets(rng: random.Random, subscriptions: list[dict]) -> list[dict]:
    rows = []
    for sub in subscriptions:
        first = date.fromisoformat(sub["started_at"])
        span = (last_active_day(sub) - first).days
        for _ in range(rng.randint(0, 6)):
            opened = first + timedelta(days=rng.randint(0, max(span, 0)))
            closed = opened + timedelta(days=rng.randint(0, 14))
            rows.append({
                "ticket_id": len(rows) + 1,
                "company_id": sub["company_id"],
                "opened_at": opened.isoformat(),
                # A ticket opened near the end of the world may still be open.
                "closed_at": closed.isoformat() if closed <= WORLD_END else "",
                "priority": rng.choice(TICKET_PRIORITIES),
                "category": rng.choice(TICKET_CATEGORIES),
            })
    return rows
