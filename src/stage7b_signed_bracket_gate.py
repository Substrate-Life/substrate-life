"""Stage 7B signed-bracket feasibility gate (signed-bracket prereg section 5).

Tooling for the BINDING pre-freeze feasibility gate registered at
``docs/stage-7b-signed-bracket-preregistration.md`` section 5: exploratory,
NON-RETAINED shakedowns at the exact carried ecology on the **same fixed
24-seed table used by all three prior gate generations** (``20270000 + j``,
``j`` in ``0..23`` -- a fourth reuse; section 5.2).  Produces no retained
artifact: everything is printed to stdout as a factual gate summary whose
per-replicate evidence and per-condition pass counts must be recorded in
the freeze commit's manifest notes (section 5.5) -- but only if the gate
passes and a freeze is actually committed.

Gate conditions (all mandatory):

- **G1** at least two-thirds of shakedown replicates yield COMPLETE
  certified bracket PAIRS -- both genotypes emit a finite-root bracket
  (any of SUPERCRITICAL/CRITICAL/SUBCRITICAL); any ``NO_FINITE_ROOT``
  fails G1 for that replicate and demands diagnosis;
- **G2** zero ``BUFFER_OVERFLOW`` triggers and zero
  ``INVALID_IMPLEMENTATION`` classifications;
- **G3** every ledger checkpoint closes in every shakedown run, all five
  binding identities hold (enforced inside the reused estimator), and the
  ESTIMATOR-LAYER REGRESSION IDENTITY holds: every genotype-replicate's
  ``L0_exact`` equals the archived generation-3 (denominator-repair) value
  bit-exactly, because population runs are deterministic in the hazard
  seed and only the solver DOMAIN is new here.

If any condition fails, no freeze may be committed; the only correct
action is a further superseding preregistration with a diagnosis
supported by new evidence (section 5.4).  This script never applies the
carried section-3-table decision rule and makes no fitness, selection, or
evolutionary claim; brackets and statuses are feasibility facts about the
registered ecology, measured with the new full-line solver over the
unchanged repaired endpoint.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import os
import sys
import traceback
from typing import Any

from stage7b2_measure import (
    cohort_genotypes,
    extract_vital_records,
    fmt_rat,
)
from stage7b2_population import run_window
from stage7b_signed_bracket_config import (
    GENERATION_3_GATE_SUMMARY_PATH,
    PREREG_DOCUMENT,
    PROTOCOL,
    endpoint_configuration,
    registered_population,
    shakedown_seeds,
)
from stage7b_exposure_measure import exposure_schedule, lotka_coefficients
from stage7b_signed_bracket_solver import (
    FINITE_ROOT_STATUSES,
    full_line_certified_bracket,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _gate_threshold(count: int) -> int:
    """Two-thirds ceiling for a shakedown-table size (integer counts)."""
    return -(-2 * count // 3)


def _count_events(event_log: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in event_log:
        kind = event.get("event", "?")
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def load_generation_3_reference() -> dict[tuple[int, str], str]:
    """Archived generation-3 ``L0_exact`` values keyed by (seed, genotype).

    Read-only reuse of committed evidence; never modified. Raises loudly if
    the archived file is missing or malformed -- the regression check must
    never silently degrade.
    """
    path = os.path.join(REPO_ROOT, GENERATION_3_GATE_SUMMARY_PATH)
    with open(path, "r", encoding="utf-8") as handle:
        archived = json.load(handle)
    reference: dict[tuple[int, str], str] = {}
    for record in archived["replicate_records"]:
        seed = record["hazard_seed"]
        for genotype, l0 in record.get("L0_exact", {}).items():
            reference[(seed, genotype)] = l0
    if len(reference) != 2 * len(archived["replicate_records"]):
        raise AssertionError(
            "generation-3 reference table incomplete")
    return reference


def run_shakedown(seed: int) -> dict[str, Any]:
    """One unretained shakedown replicate under the new full-line solver."""
    record: dict[str, Any] = {"hazard_seed": seed}
    try:
        population = registered_population(seed)
        classification = run_window(population)
        record.update(classification)
        if classification["classification"] != "COMPLETE":
            record["gate_failures"] = ["G3"]
            return record
        vitals = extract_vital_records(population.event_log,
                                       population.window_ticks)
        genotypes_status: dict[str, str] = {}
        l0_by_genotype: dict[str, str] = {}
        brackets: dict[str, dict[str, Any]] = {}
        births_credited: dict[str, int] = {}
        person_ticks: dict[str, int] = {}
        cohort_sizes: dict[str, int] = {}
        for genotype_a in cohort_genotypes(vitals):
            schedule = exposure_schedule(vitals, genotype_a)
            c_x = lotka_coefficients(schedule)
            certificate = full_line_certified_bracket(c_x)
            key = str(genotype_a)
            genotypes_status[key] = certificate["status"]
            l0_by_genotype[key] = fmt_rat(certificate["L0_exact"])
            if certificate["status"] in FINITE_ROOT_STATUSES:
                brackets[key] = {
                    "r_lo": fmt_rat(certificate["r_lo"]),
                    "r_hi": fmt_rat(certificate["r_hi"]),
                }
            births_credited[key] = schedule["births_credited"]
            person_ticks[key] = schedule["person_ticks_credited"]
            cohort_sizes[key] = schedule["cohort_size"]
        record.update({
            "genotype_status": genotypes_status,
            "L0_exact": l0_by_genotype,
            "brackets": brackets,
            "births_credited": births_credited,
            "person_ticks_credited": person_ticks,
            "cohort_sizes": cohort_sizes,
            "max_buffered": max(
                (snapshot.get("buffered", 0)
                 for snapshot in population.closure_history),
                default=0),
            "tick_checkpoints": len(population.closure_history),
            "admitted_births": population.admitted_births,
            "hazard_deaths": sum(
                1 for event in population.event_log
                if event.get("event") == "hazard_death"),
            "ever_alive": len(vitals["members"]),
            "final_census": len(population.members),
            "event_counts": _count_events(population.event_log),
        })
    except Exception as error:  # noqa: BLE001 -- gate evidence, never hidden
        record.update({
            "classification": "GATE_EXCEPTION",
            "reason": repr(error),
            "traceback": traceback.format_exc(),
            "gate_failures": ["G3"],
        })
    return record


def evaluate_gate(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply conditions G1-G3 to the shakedown records."""
    complete = [r for r in records if r.get("classification") == "COMPLETE"]
    invalid = [r for r in records if r.get("classification") != "COMPLETE"]

    def finite_root(r: dict[str, Any], genotype: str) -> bool:
        return r.get("genotype_status", {}).get(genotype) in FINITE_ROOT_STATUSES

    n = len(records)
    threshold = _gate_threshold(n)
    complete_pairs = [
        r for r in complete
        if finite_root(r, "102") and finite_root(r, "204")]
    no_finite_root = [
        r for r in complete
        if not (finite_root(r, "102") and finite_root(r, "204"))]

    reference = load_generation_3_reference()
    regression_mismatches: list[dict[str, Any]] = []
    for r in complete:
        seed = r["hazard_seed"]
        for genotype, l0 in r.get("L0_exact", {}).items():
            archived_l0 = reference.get((seed, genotype))
            if archived_l0 is None:
                regression_mismatches.append({
                    "hazard_seed": seed, "genotype": genotype,
                    "reason": "no archived generation-3 record"})
            elif archived_l0 != l0:
                regression_mismatches.append({
                    "hazard_seed": seed, "genotype": genotype,
                    "archived": archived_l0, "new": l0})

    g2_pass = not invalid and all(
        r.get("reason") != "BUFFER_OVERFLOW" for r in records)
    g3_checkpoint_failures = [r["hazard_seed"] for r in records
                              if "G3" in r.get("gate_failures", [])]
    g3_pass = not g3_checkpoint_failures and not regression_mismatches

    status_counts: dict[str, dict[str, int]] = {"102": {}, "204": {}}
    for r in complete:
        for genotype, status in r.get("genotype_status", {}).items():
            status_counts.setdefault(genotype, {})
            status_counts[genotype][status] = (
                status_counts[genotype].get(status, 0) + 1)

    summary: dict[str, Any] = {
        "gate": f"{PROTOCOL} section 5",
        "prereg_document": PREREG_DOCUMENT,
        "seeds_used": sorted(r["hazard_seed"] for r in records),
        "seed_count": n,
        "two_thirds_threshold": threshold,
        "complete_replicates": len(complete),
        "replicate_records": sorted(records, key=lambda r: r["hazard_seed"]),
        "invalid_replicates": [
            {"hazard_seed": r["hazard_seed"],
             "classification": r.get("classification"),
             "reason": r.get("reason")}
            for r in invalid],
        "status_counts_per_genotype": status_counts,
        "G1_complete_bracket_pairs": {
            "pairs": len(complete_pairs),
            "of": len(complete),
            "no_finite_root_replicates": [
                r["hazard_seed"] for r in no_finite_root],
            "passes_G1": len(complete_pairs) >= threshold,
        },
        "G2_no_overflow_no_invalid": {
            "zero_buffer_overflow": g2_pass,
            "zero_invalid_implementations": not invalid,
            "passes_G2": g2_pass,
        },
        "G3_checkpoints_and_regression": {
            "checkpoint_failures": g3_checkpoint_failures,
            "regression_mismatches": regression_mismatches,
            "generation_3_reference": GENERATION_3_GATE_SUMMARY_PATH,
            "passes_G3": g3_pass,
        },
        "gate_passed": (
            len(complete_pairs) >= threshold
            and g2_pass
            and g3_pass),
        "failure_guidance": (
            "Section 5.4: if any condition fails, no freeze may be "
            "committed; the correct action is a further superseding "
            "preregistration with a diagnosis supported by new evidence. "
            "Shakedown executions produce no retained artifact "
            "(section 5.5)."),
        "registered_configuration_checked": endpoint_configuration(),
        "claim_scope": (
            "Feasibility facts only. No fitness, selection, contrast, or "
            "evolutionary claim is made or retained; the confirmatory seed "
            "table remains untouched until the single retained run."),
    }
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=2,
                        help="parallel replicates (deterministic regardless)")
    parser.add_argument("--limit", type=int, default=None,
                        help="run only the first J shakedown seeds "
                             "(implementation-window plumbing checks)")
    args = parser.parse_args(argv)

    seeds = shakedown_seeds()
    if args.limit is not None:
        seeds = seeds[:args.limit]
    print(f"[gate] {len(seeds)} shakedown seeds: {list(seeds)}",
          file=sys.stderr)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(run_shakedown, seeds))
    summary = evaluate_gate(records)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
