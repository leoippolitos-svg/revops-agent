"""Controls every automation that writes must have (context document `writeback-rules`).

An automation decides what it would write; this module decides whether and how much of it
is written, and reports everything that was not written as "needs review", never as
"skipped", so a failure is an alert and not silence.

- Dry run by default: without --write nothing is written.
- Kill switch: --write writes only when <NAME>_ENABLED=true is set in the environment.
  Otherwise the run is a shadow run: it reports what it would write and writes nothing.
  Turning an automation off is changing a variable, not deploying code.
- Cap per run: at most N writes, read from the write-back rules table; the rest wait for review.
- Circuit breaker: after N consecutive failed writes the run stops writing.
- Post-condition: after writing, each write is read back; a mismatch needs review.

Idempotency stays with each automation: it keys every write on an explicit id (lead_id,
deal_id), so a second run overwrites the same line instead of adding one.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
BREAKER_LIMIT = 3  # consecutive failures before the run stops writing


class ControlsError(RuntimeError):
    """The write-back rules do not authorise this automation; nothing may be written."""


def writeback_cap(name: str, context_dir: Path = ROOT / "context") -> int:
    """The cap per run of an automation, from its row in the write-back rules, and proof it is authorised."""
    text = (context_dir / "rules" / "writeback-rules.md").read_text(encoding="utf-8")
    if f"RECURRING-AUTHORIZATION: {name}." not in text:
        raise ControlsError(f"writeback-rules.md has no RECURRING-AUTHORIZATION for {name}; nothing may be written")
    row = re.search(rf"^\|[^\n]*\| `{re.escape(name)}` \|[^\n]*\| (\d+) \|\s*$", text, flags=re.MULTILINE)
    if not row:
        raise ControlsError(f"writeback-rules.md has no cap per run for {name}")
    return int(row.group(1))


@dataclass
class Outcome:
    applied: list[str] = field(default_factory=list)
    needs_review: dict[str, str] = field(default_factory=dict)  # id -> reason
    breaker_open: bool = False


class WriteControls:
    def __init__(self, name: str, write_flag: bool, env: dict | None = None, cap: int | None = None,
                 breaker_limit: int = BREAKER_LIMIT):
        env = os.environ if env is None else env
        self.name = name
        self.variable = name.upper().replace("-", "_") + "_ENABLED"
        self.enabled = str(env.get(self.variable, "")).strip().lower() == "true"
        self.mode = "write" if (write_flag and self.enabled) else ("shadow" if write_flag else "dry run")
        self.cap = writeback_cap(name) if cap is None else cap
        self.breaker_limit = breaker_limit

    def describe(self) -> str:
        if self.mode == "write":
            return f"writing (kill switch {self.variable}=true, cap {self.cap} per run)"
        if self.mode == "shadow":
            return f"shadow run: {self.variable} is not true, so nothing is written; this is what would be written"
        return "dry run: nothing written (use --write)"

    def apply(self, ids: list[str], write_one: Callable[[str], None], read_back: Callable[[str], bool]) -> Outcome:
        """Write each id with write_one, within the cap and the breaker, then check each with read_back."""
        out = Outcome()
        if self.mode != "write":
            return out
        failures = 0
        for position, item in enumerate(ids):
            if out.breaker_open:
                out.needs_review[item] = "not attempted: the circuit breaker stopped the run"
                continue
            if len(out.applied) >= self.cap:
                out.needs_review[item] = f"over the cap of {self.cap} writes per run"
                continue
            try:
                write_one(item)
            except Exception as error:  # any failed write is reported, never swallowed
                failures += 1
                out.needs_review[item] = f"write failed: {error}"
                if failures >= self.breaker_limit:
                    out.breaker_open = True
                continue
            failures = 0
            out.applied.append(item)
        for item in list(out.applied):
            if not read_back(item):
                out.applied.remove(item)
                out.needs_review[item] = "written but the check after writing did not find it"
        return out
