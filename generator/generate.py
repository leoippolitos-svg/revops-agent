"""Generate fictional raw data for Fernway.

Writes CSV files into data/raw/<source>/ (the data/ folder is gitignored):

    data/raw/crm/owners.csv
    data/raw/crm/companies.csv
    data/raw/crm/contacts.csv
    data/raw/crm/deals.csv
    data/raw/crm/deal_stage_history.csv
    data/raw/marketing/campaigns.csv
    data/raw/marketing/form_submissions.csv
    data/raw/billing/subscriptions.csv, invoices.csv, payments.csv
    data/raw/cs/onboarding_milestones.csv, health_scores.csv, tickets.csv
    data/raw/_issues.json         (answer key for the injected data-quality issues)

Run from the repository root:
    python generator/generate.py --seed 42

Why CSV files and not the database: the bronze layer may only be written by
the ingestion step (see CLAUDE.md). The generator plays the role of the
"source systems", so it only drops files, like a real export would.

Everything is invented. Names come from the short word lists below, e-mails use
example.com (a domain reserved for examples), and there are no phone numbers
or tax IDs.
"""

import argparse
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

import billing_cs  # sits next to this file; Python finds it because we run the script from here

# Simulated "today" is fixed on purpose. If we used the real date, the same seed
# would produce different files on different days, and tests would break.
SIMULATION_START = date(2025, 1, 1)
SIMULATION_DAYS = 365

COMPANY_COUNT = 300
CONTACT_COUNT = 1000

COMPANY_PREFIXES = [
    "Northbridge", "Harborline", "Stonegate", "Brightwell", "Ironvale",
    "Clearwater", "Summitview", "Redfield", "Oakmont", "Lakeshore",
    "Pinecrest", "Westmark", "Eastgate", "Silverline", "Copperfield",
    "Granite", "Maplewood", "Riverbend", "Highland", "Kestrel",
]
COMPANY_SUFFIXES = [
    "Facilities", "Maintenance", "Services", "Property Care", "Technical Group",
    "Building Systems", "Field Works", "Utilities", "Engineering", "Operations",
    "Mechanical", "Site Care", "Asset Care", "Cleaning Co", "Repair Group",
]
FIRST_NAMES = [
    "Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie",
    "Avery", "Quinn", "Drew", "Robin", "Skyler", "Reese", "Rowan", "Emery",
    "Dana", "Blake", "Cameron", "Parker",
]
LAST_NAMES = [
    "Hale", "Brooks", "Fields", "Stone", "Marsh", "Reed", "Lane", "Wells",
    "Cross", "Frost", "Moore", "Grant", "Ellis", "Shaw", "Price", "Dale",
    "Bishop", "Hayes", "Ward", "Cole",
]
JOB_TITLES = [
    "Operations Manager", "Facilities Director", "Maintenance Supervisor",
    "Head of Field Service", "COO", "IT Manager", "Procurement Lead",
    "Service Coordinator",
]
INDUSTRIES = [
    "facilities management", "HVAC", "electrical services", "elevator maintenance",
    "property management", "industrial maintenance",
]
COUNTRIES = ["US", "CA", "UK", "DE", "AU"]

# Headcount ranges decide the segment, so segment and size always agree.
SEGMENTS = [
    ("smb", 10, 99),
    ("mid_market", 100, 999),
    ("enterprise", 1000, 5000),
]
# Most companies are small; few are enterprise. Weights follow the same order.
SEGMENT_WEIGHTS = [0.6, 0.3, 0.1]

# (team, how many people). Teams are the ones described in generator/README.md.
OWNER_TEAMS = [
    ("sdr", 5),
    ("sales", 5),
    ("enterprise", 3),
    ("onboarding", 3),
    ("customer_success", 4),
]

CAMPAIGN_CHANNELS = ["paid_search", "paid_social", "webinar", "email", "event", "organic"]

# Open stages in order. A deal always moves forward through them and may stop
# at any one. The names are what the CRM stores; what each stage means for the
# business belongs in a context document (Phase 2), not here.
OPEN_STAGES = ["qualification", "discovery", "proposal", "negotiation"]
WON, LOST = "closed_won", "closed_lost"

SHARE_OF_COMPANIES_WITH_DEALS = 0.6
# Outcome of a deal that reaches its end: (won, lost, still open).
OUTCOME_WEIGHTS = [0.25, 0.35, 0.40]
# Typical deal size per segment, in USD.
DEAL_AMOUNT_RANGE = {
    "smb": (3_000, 20_000),
    "mid_market": (15_000, 80_000),
    "enterprise": (60_000, 300_000),
}

SHARE_OF_CONTACTS_WITH_FORM = 0.5
SHARE_MARKETING_MQL = 0.4

# Share of rows that get each data-quality issue (at least one row each).
ISSUE_RATES = {
    "duplicate_company": 0.03,
    "deal_without_company": 0.02,
    "stage_dates_out_of_order": 0.03,
    "mql_flag_conflict": 0.08,
    "subscription_without_deal": 0.05,
}


# Real deal ids are small numbers; an id above this base can never be a real deal.
ORPHAN_DEAL_ID_BASE = 900_000


def random_day(rng: random.Random) -> date:
    return SIMULATION_START + timedelta(days=rng.randrange(SIMULATION_DAYS))


def make_owners(rng: random.Random) -> list[dict]:
    owners = []
    for team, count in OWNER_TEAMS:
        for _ in range(count):
            owner_id = len(owners) + 1
            first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
            owners.append({
                "owner_id": owner_id,
                "full_name": f"{first} {last}",
                # The id in the e-mail keeps it unique even if two people share a name.
                "email": f"{first}.{last}.{owner_id}@example.com".lower(),
                "team": team,
            })
    return owners


def make_companies(rng: random.Random, owners: list[dict]) -> list[dict]:
    # Build every prefix + suffix pair, then draw without repeating, so company
    # names are unique in the clean data. Duplicates are injected on purpose
    # later, where they are recorded in the answer key.
    names = [f"{p} {s}" for p in COMPANY_PREFIXES for s in COMPANY_SUFFIXES]
    names = rng.sample(names, COMPANY_COUNT)

    # Only sales-side owners own accounts; onboarding and CS get them later.
    # Enterprise accounts belong to the enterprise team, the rest to sales.
    owners_by_team = {
        team: [o for o in owners if o["team"] == team] for team in ("sales", "enterprise")
    }

    companies = []
    for index, name in enumerate(names, start=1):
        segment, low, high = rng.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]
        team = "enterprise" if segment == "enterprise" else "sales"
        owner = rng.choice(owners_by_team[team])
        companies.append({
            "company_id": index,
            "name": name,
            "industry": rng.choice(INDUSTRIES),
            "segment": segment,
            "employee_count": rng.randint(low, high),
            "country": rng.choice(COUNTRIES),
            "owner_id": owner["owner_id"],
            "created_at": random_day(rng).isoformat(),
        })
    return companies


def make_contacts(rng: random.Random, companies: list[dict]) -> list[dict]:
    contacts = []
    for contact_id in range(1, CONTACT_COUNT + 1):
        company = rng.choice(companies)
        first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
        # A contact cannot exist before its company does.
        company_day = date.fromisoformat(company["created_at"])
        created = company_day + timedelta(days=rng.randrange(60))
        contacts.append({
            "contact_id": contact_id,
            "company_id": company["company_id"],
            "first_name": first,
            "last_name": last,
            "email": f"{first}.{last}.{contact_id}@example.com".lower(),
            "job_title": rng.choice(JOB_TITLES),
            "created_at": created.isoformat(),
        })
    return contacts


def make_campaigns(rng: random.Random) -> list[dict]:
    campaigns = []
    for campaign_id in range(1, 13):
        channel = CAMPAIGN_CHANNELS[(campaign_id - 1) % len(CAMPAIGN_CHANNELS)]
        campaigns.append({
            "campaign_id": campaign_id,
            "name": f"{channel}_wave_{campaign_id:02d}",
            "channel": channel,
            "started_at": random_day(rng).isoformat(),
            "budget_usd": rng.randrange(2, 41) * 500,
        })
    return campaigns


def make_deals(rng: random.Random, companies: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return (deals, stage history). Clean data: dates always move forward."""
    deals, history = [], []
    for company in companies:
        if rng.random() >= SHARE_OF_COMPANIES_WITH_DEALS:
            continue
        for kind in rng.choices(["New rollout", "Expansion", "Pilot"], k=rng.choice([1, 1, 2])):
            deal_id = len(deals) + 1
            low, high = DEAL_AMOUNT_RANGE[company["segment"]]
            created = date.fromisoformat(company["created_at"]) + timedelta(days=rng.randrange(90))

            outcome = rng.choices(["won", "lost", "open"], weights=OUTCOME_WEIGHTS)[0]
            if outcome == "won":
                stages = OPEN_STAGES + [WON]
            else:
                # A lost or open deal stops at some open stage.
                stages = OPEN_STAGES[: rng.randint(1, len(OPEN_STAGES))]
                if outcome == "lost":
                    stages = stages + [LOST]

            entered = created
            for position, stage in enumerate(stages):
                if position > 0:
                    entered += timedelta(days=rng.randint(3, 30))
                history.append({
                    "history_id": len(history) + 1,
                    "deal_id": deal_id,
                    "stage": stage,
                    "entered_at": entered.isoformat(),
                })

            closed = stages[-1] in (WON, LOST)
            deals.append({
                "deal_id": deal_id,
                "company_id": company["company_id"],
                "owner_id": company["owner_id"],
                "name": f"{company['name']} - {kind}",
                "amount_usd": rng.randrange(low, high + 1, 100),
                "stage": stages[-1],
                "created_at": created.isoformat(),
                "closed_at": entered.isoformat() if closed else "",
            })
    return deals, history


def make_form_submissions(rng: random.Random, contacts: list[dict], campaigns: list[dict]) -> list[dict]:
    """Some contacts filled a marketing form; Marketing flags some of them as MQL."""
    submissions = []
    for contact in contacts:
        if rng.random() >= SHARE_OF_CONTACTS_WITH_FORM:
            continue
        created = date.fromisoformat(contact["created_at"])
        submissions.append({
            "submission_id": len(submissions) + 1,
            "contact_id": contact["contact_id"],
            "campaign_id": rng.choice(campaigns)["campaign_id"],
            "submitted_at": (created + timedelta(days=rng.randrange(30))).isoformat(),
            "marketing_mql_flag": int(rng.random() < SHARE_MARKETING_MQL),
        })
    return submissions


def add_sales_mql_flag(contacts: list[dict], submissions: list[dict]) -> None:
    """Sales keeps its own MQL flag on the contact.

    In the clean data it agrees with Marketing's flag; contacts who never filled
    a form are not MQL. The two flags are made to disagree later, as an issue.
    """
    marketing_flag = {s["contact_id"]: s["marketing_mql_flag"] for s in submissions}
    for contact in contacts:
        contact["sales_mql_flag"] = marketing_flag.get(contact["contact_id"], 0)


def pick(rng: random.Random, ids: list, kind: str) -> list:
    """Choose which rows get an issue: a fixed share of them, at least one."""
    count = max(1, round(ISSUE_RATES[kind] * len(ids)))
    return sorted(rng.sample(ids, count))


def inject_issues(rng, companies, contacts, deals, history, submissions, subscriptions) -> list[dict]:
    """Break the clean data on purpose and return the answer key.

    This runs after all clean data exists and uses its own random generator, so
    the clean rows never change because of an issue. Each change is written to
    the returned list, so tests (and later, audits) know what to expect.
    """
    issues = []

    # 1. Duplicate companies: the same company again under a new id, with the
    #    name in a different case, as if two systems had created it.
    next_id = max(c["company_id"] for c in companies) + 1
    by_id = {c["company_id"]: c for c in companies}
    for original_id in pick(rng, list(by_id), "duplicate_company"):
        original = by_id[original_id]
        copy = dict(original, company_id=next_id, name=original["name"].upper())
        companies.append(copy)
        issues.append({"type": "duplicate_company", "table": "crm/companies",
                       "row_id": next_id, "detail": f"copy of company_id {original_id}"})
        next_id += 1

    # 2. Deals whose company association is missing.
    deal_by_id = {d["deal_id"]: d for d in deals}
    for deal_id in pick(rng, list(deal_by_id), "deal_without_company"):
        deal_by_id[deal_id]["company_id"] = ""
        issues.append({"type": "deal_without_company", "table": "crm/deals",
                       "row_id": deal_id, "detail": "company_id is empty"})

    # 3. Stage dates out of order. We swap the dates of two middle stages of a
    #    deal. Only deals with four or more stages are used, so the last stage
    #    (and with it closed_at) is never touched.
    rows_by_deal = {}
    for row in history:
        rows_by_deal.setdefault(row["deal_id"], []).append(row)
    eligible = [deal_id for deal_id, rows in rows_by_deal.items() if len(rows) >= 4]
    for deal_id in pick(rng, eligible, "stage_dates_out_of_order"):
        second, third = rows_by_deal[deal_id][1], rows_by_deal[deal_id][2]
        second["entered_at"], third["entered_at"] = third["entered_at"], second["entered_at"]
        issues.append({"type": "stage_dates_out_of_order", "table": "crm/deal_stage_history",
                       "row_id": deal_id, "detail": f"stages {second['stage']} and {third['stage']} swapped"})

    # 4. Competing MQL flags: Sales disagrees with Marketing for the same contact.
    contact_by_id = {c["contact_id"]: c for c in contacts}
    with_form = [s["contact_id"] for s in submissions]
    for contact_id in pick(rng, with_form, "mql_flag_conflict"):
        contact = contact_by_id[contact_id]
        contact["sales_mql_flag"] = 1 - contact["sales_mql_flag"]
        issues.append({"type": "mql_flag_conflict", "table": "crm/contacts",
                       "row_id": contact_id, "detail": "sales_mql_flag differs from marketing_mql_flag"})

    # 5. Subscriptions whose deal does not exist: point them at a deal id that is
    #    not in the CRM (a deal deleted, or a subscription created by hand).
    sub_by_id = {s["subscription_id"]: s for s in subscriptions}
    for subscription_id in pick(rng, list(sub_by_id), "subscription_without_deal"):
        sub_by_id[subscription_id]["deal_id"] = ORPHAN_DEAL_ID_BASE + subscription_id
        issues.append({"type": "subscription_without_deal", "table": "billing/subscriptions",
                       "row_id": subscription_id, "detail": "deal_id does not exist in crm/deals"})

    return issues


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="" plus an explicit "\n" keeps the bytes identical on Windows and
    # Linux, so the same seed gives the same file hash everywhere.
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generate(seed: int, out_dir: Path) -> dict[str, int]:
    """Write all files and return how many rows each one has."""
    # Separate Random instances, not the global one, so nothing else in the
    # program can change the sequence of numbers we draw. The base entities keep
    # their own generator: adding new data never changes them.
    rng = random.Random(seed)
    crm_rng = random.Random(f"{seed}:crm-marketing")
    billing_rng = random.Random(f"{seed}:billing-cs")
    issue_rng = random.Random(f"{seed}:issues")

    owners = make_owners(rng)
    companies = make_companies(rng, owners)
    contacts = make_contacts(rng, companies)
    campaigns = make_campaigns(rng)

    deals, history = make_deals(crm_rng, companies)
    submissions = make_form_submissions(crm_rng, contacts, campaigns)
    add_sales_mql_flag(contacts, submissions)

    # Billing and Customer Success come from the clean deals, so they are built
    # before any issue is injected into those deals.
    subscriptions = billing_cs.make_subscriptions(billing_rng, deals, companies)
    invoices, payments = billing_cs.make_invoices_and_payments(billing_rng, subscriptions)
    milestones = billing_cs.make_onboarding_milestones(billing_rng, subscriptions)
    health_scores = billing_cs.make_health_scores(billing_rng, subscriptions)
    tickets = billing_cs.make_tickets(billing_rng, subscriptions)

    issues = inject_issues(issue_rng, companies, contacts, deals, history, submissions, subscriptions)

    write_csv(out_dir / "crm" / "owners.csv", owners)
    write_csv(out_dir / "crm" / "companies.csv", companies)
    write_csv(out_dir / "crm" / "contacts.csv", contacts)
    write_csv(out_dir / "crm" / "deals.csv", deals)
    write_csv(out_dir / "crm" / "deal_stage_history.csv", history)
    write_csv(out_dir / "marketing" / "campaigns.csv", campaigns)
    write_csv(out_dir / "marketing" / "form_submissions.csv", submissions)
    write_csv(out_dir / "billing" / "subscriptions.csv", subscriptions)
    write_csv(out_dir / "billing" / "invoices.csv", invoices)
    write_csv(out_dir / "billing" / "payments.csv", payments)
    write_csv(out_dir / "cs" / "onboarding_milestones.csv", milestones)
    write_csv(out_dir / "cs" / "health_scores.csv", health_scores)
    write_csv(out_dir / "cs" / "tickets.csv", tickets)

    # The answer key is not a source system file; the leading underscore keeps it
    # apart from the source folders.
    (out_dir / "_issues.json").write_text(
        json.dumps(issues, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )

    return {
        "owners": len(owners),
        "companies": len(companies),
        "contacts": len(contacts),
        "campaigns": len(campaigns),
        "deals": len(deals),
        "deal_stage_history": len(history),
        "form_submissions": len(submissions),
        "subscriptions": len(subscriptions),
        "invoices": len(invoices),
        "payments": len(payments),
        "onboarding_milestones": len(milestones),
        "health_scores": len(health_scores),
        "tickets": len(tickets),
        "issues": len(issues),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate fictional Fernway raw data.")
    parser.add_argument("--seed", type=int, default=42, help="same seed, same data")
    parser.add_argument("--out", type=Path, default=Path("data/raw"), help="output folder")
    args = parser.parse_args()

    counts = generate(args.seed, args.out)
    for name, count in counts.items():
        print(f"{name}: {count} rows")
    print(f"written to {args.out}")


if __name__ == "__main__":
    main()
