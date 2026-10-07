"""End-to-end v2 pipeline driver (stops on the first failing step).

Runs the reproducible chain documented in distillation/README.md.
Writes reports/v2-pipeline-run.md.
"""
from __future__ import annotations

import datetime as dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "distillation" / "scripts"
REPORTS = ROOT / "distillation" / "reports"
TOPICS = [
    "education",
    "technology",
    "environment",
    "government",
    "social",
    "crime",
    "culture",
    "health",
    "media",
    "globalization-work",
]
STEPS: list[tuple[str, list[str]]] = [
    ("step1_clean_enrich", ["step1_clean_enrich.py"]),
    ("step2_blind_deviation", ["step2_blind_deviation.py"]),
    ("step3_features", ["step3_features.py"]),
    ("step4_extract_assets", ["step4_extract_assets.py"]),
    ("step4b_diff_ngrams", ["step4b_diff_ngrams.py"]),
    ("step5_build_anchors", ["step5_build_anchors.py"]),
    ("step7_question_bank", ["step7_build_question_bank.py"]),
    ("step8_units", ["step8_units.py"]),
    ("step9_candidates", ["step9_candidates.py"]),
    ("step10_preprocess", ["step10_preprocess_curation.py"]),
] + [(f"verify_curation_{t}", ["verify_curation.py", "--topic", t]) for t in TOPICS] + [
    ("step10_build", ["step10_build_l5l6.py"]),
    ("audit_l5_l6", ["audit_l5_l6.py"]),
    ("verify_assets", ["verify_assets.py"]),
    ("check_duplicates", ["check_duplicates.py"]),
    ("final_acceptance", ["final_acceptance.py"]),
]


def main() -> None:
    log = [f"# v2 流水线运行记录（{dt.datetime.now().isoformat(timespec='seconds')}）", ""]
    failed = 0
    for name, argv in STEPS:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / argv[0]), *argv[1:]],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        tail = (proc.stdout or "").strip().splitlines()
        last = tail[-1] if tail else ""
        log.append(f"- {'PASS' if proc.returncode == 0 else 'FAIL'} {name} (rc={proc.returncode}) {last}")
        print(f"{'PASS' if proc.returncode == 0 else 'FAIL'} {name} (rc={proc.returncode})")
        if proc.returncode != 0:
            failed = 1
            err = (proc.stderr or "").strip().splitlines()
            log.append("  - stderr: " + (" | ".join(err[-6:]) if err else "(none)"))
            break
    (REPORTS / "v2-pipeline-run.md").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("FAILED" if failed else "ALL STEPS PASS")
    sys.exit(failed)


if __name__ == "__main__":
    main()
