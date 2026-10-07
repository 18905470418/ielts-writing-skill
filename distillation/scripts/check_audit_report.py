"""Check that the audit report table matches the latest audit pack."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "distillation" / "reports"


def main() -> None:
    pack = (REPORTS / "l5-l6-audit-pack.md").read_text(encoding="utf-8")
    report = (REPORTS / "l5-l6-audit.md").read_text(encoding="utf-8")
    items = re.findall(r"^## (AUD-\d+) · (L[56]) · ([a-z\-]+) · `([A-Za-z0-9\-]+)` ← `(B[^`]+)`", pack, re.M)
    report_codes = set(re.findall(r"\| (?:L5|L6) \|", report))
    report_rows = re.findall(r"\| \d+ \| (?:L5|L6) \| [a-z\-]+ \| ([A-Za-z0-9\-（)）]+)", report)
    print("pack items:", len(items))
    print("report rows:", len(report_rows))
    pack_codes = {c for _, _, _, c, _ in items}
    missing = sorted(pack_codes - set(report_rows))
    extra = sorted(set(report_rows) - pack_codes)
    print("codes in pack but not in report:", missing[:10])
    print("codes in report but not in pack:", extra[:10])
    print("CONSISTENT" if not missing and not extra and len(items) == len(report_rows) else "MISMATCH")


if __name__ == "__main__":
    main()
