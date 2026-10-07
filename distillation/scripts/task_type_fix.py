"""Reviewed task-type corrections for the sample library (Task 2, step 1).

The task-1 classifier documents its boundaries as:
  * "discuss both views" -> discussion;
  * "positive/negative development" -> adv-disadv;
  * mixed asks such as "why + agree" -> two-part;
  * single What/How/Why questions -> report.

Two implementation misfires are corrected here:
  1. Single evaluation asks that merely contain the phrase "best way to X"
     (e.g. "The best way to ... is ... To what extent do you agree?") were
     routed to two-part because RE_REPORT matched "best way to solve".
     A single ask like that is an opinion task.
  2. Questions that genuinely contain a "why" ask *and* an evaluation ask
     ("Do you think this is a positive or a negative development?") were
     routed to adv-disadv because the adv regex runs first. Under the
     documented boundary ("why + agree" -> two-part) these are two-part.

The corrections below are applied to the training split by step 1 and are
also importable for the blindtest at calibration time. Record ids are never
changed (schema: ids stay stable even when a label is corrected).
"""
from __future__ import annotations

import re

DISCUSS = re.compile(r"discuss\s+both|discuss\s+the\s+(?:two|both)|both\s+(?:of\s+these\s+)?(?:views|sides|opinions)", re.I)
EVAL_ASK = re.compile(
    r"do\s+you\s+(?:agree|disagree)|to\s+what\s+extent|agree\s+or\s+disagree|"
    r"is\s+(?:this|it)\s+(?:a\s+)?(?:good|bad|positive|negative|acceptable|justified|right|wrong)|"
    r"do\s+you\s+think\s+(?:it|this)\s+is\s+(?:a\s+)?(?:good|bad|positive|negative|acceptable|justified|right|wrong)",
    re.I,
)
POSNEG_ASK = re.compile(r"(?:positive|negative)\s+(?:or\s+(?:a\s+)?(?:positive|negative)\s+)?(?:development|trend|change|step|situation|habit|impact)", re.I)
WHY_ASK = re.compile(r"\bwhy\b|\bwhat\s+(?:are\s+)?(?:the\s+)?(?:causes?|reasons?|factors?)\b", re.I)
BEST_WAY = re.compile(r"\bbest\s+way\b", re.I)
ADV_DISADV_ASK = re.compile(
    r"advantages?\s*(?:and|or|&|/)\s*disadvantages?|disadvantages?\s*(?:and|or|&|/)\s*advantages?|pros\s+and\s+cons|"
    r"outweigh",
    re.I,
)
SECOND_ASK = re.compile(
    r"\bwhy\b|\bwhat\s+(?:are|do)\b|\bhow\s+(?:can|could|should|might)\b|\bwhat\s+(?:solutions?|measures?|steps?)\b",
    re.I,
)

# One-off corrections found in the manual review of the 136-candidate diff
# (see reports/cleaning-report.md). All are unambiguous under either reading
# of the task-1 taxonomy.
MANUAL_OVERRIDES: dict[str, str] = {
    # single agree/disagree about a claim -> opinion
    "B6-ADV-024": "opinion",
    "B75-ADV-053": "opinion",
    # advantages/disadvantages questions that fell through the adv regex
    "B85-REP-008": "adv-disadv",
    "B9-OP-030": "adv-disadv",
    # two explicit independent asks (why + opinion / why + measure / why + pos-neg)
    "B6-OP-023": "two-part",
    "B6-OP-026": "two-part",
    "B65-OP-016": "two-part",
    "B65-OP-044": "two-part",
    "B65-REP-018": "two-part",
    "B7-OP-029": "two-part",
    "B8-OP-009": "two-part",
    "B8-OP-054": "two-part",
    "B8-OP-060": "two-part",
    "B8-REP-023": "two-part",
    "B85-OP-019": "two-part",
    "B85-OP-073": "two-part",
    # single evaluation ask with a justifying "Why?" -> adv-disadv
    "B65-ADV-054": "adv-disadv",
}


def _question_count(q: str) -> int:
    return max(q.count("?"), 1)


def effective_task_type(question: str, current: str, rec_id: str = "") -> str:
    """Return the reviewed task type for one question."""
    q = re.sub(r"\s+", " ", question)
    if rec_id in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[rec_id]
    if DISCUSS.search(q):
        return "discussion"
    # why/report ask + evaluation ask -> two-part (documented boundary);
    # this covers the "why ...? positive or negative development?" family that
    # the adv regex used to swallow before the opinion/report mixing check.
    if WHY_ASK.search(q) and (EVAL_ASK.search(q) or POSNEG_ASK.search(q)):
        return "two-part"
    # a single "best way ... agree?" ask is an opinion task
    if (
        BEST_WAY.search(q)
        and EVAL_ASK.search(q)
        and not ADV_DISADV_ASK.search(q)
        and not SECOND_ASK.search(q)
    ):
        if _question_count(q) <= 2:
            return "opinion"
    return current


def apply(rec: dict) -> str:
    return effective_task_type(rec.get("question", ""), rec.get("task_type", "opinion"), rec.get("id", ""))
