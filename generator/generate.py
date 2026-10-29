"""Generate fictional raw data for Fernway, part 1: the base entities.

Writes CSV files into data/raw/<source>/ (the data/ folder is gitignored):

    data/raw/crm/owners.csv
    data/raw/crm/companies.csv
    data/raw/crm/contacts.csv
    data/raw/marketing/campaigns.csv

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
import random
from datetime import date, timedelta
from pathlib import Path

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
    # names are unique here. Duplicate companies are injected on purpose later,
    # in part 2, where they can be tracked and tested.
    names = [f"{p} {s}" for p in COMPANY_PREFIXES for s in COMPANY_SUFFIXES]
    names = rng.sample(names, COMPANY_COUNT)

    # Only sales-side owners own accounts; onboarding and CS get them later.
    account_owners = [o for o in owners if o["team"] in ("sales", "enterprise")]

    companies = []
    for index, name in enumerate(names, start=1):
        segment, low, high = rng.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]
        # Enterprise accounts belong to the enterprise team, the rest to sales.
        team = "enterprise" if segment == "enterprise" else "sales"
        owner = rng.choice([o for o in account_owners if o["team"] == team])
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


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="" plus an explicit "\n" keeps the bytes identical on Windows and
    # Linux, so the same seed gives the same file hash everywhere.
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generate(seed: int, out_dir: Path) -> dict[str, int]:
    """Write all part-1 files and return how many rows each one has."""
    # One private Random instance, not the global one, so nothing else in the
    # program can change the sequence of numbers we draw.
    rng = random.Random(seed)

    owners = make_owners(rng)
    companies = make_companies(rng, owners)
    contacts = make_contacts(rng, companies)
    campaigns = make_campaigns(rng)

    write_csv(out_dir / "crm" / "owners.csv", owners)
    write_csv(out_dir / "crm" / "companies.csv", companies)
    write_csv(out_dir / "crm" / "contacts.csv", contacts)
    write_csv(out_dir / "marketing" / "campaigns.csv", campaigns)

    return {
        "owners": len(owners),
        "companies": len(companies),
        "contacts": len(contacts),
        "campaigns": len(campaigns),
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
