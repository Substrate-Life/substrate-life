"""Stage 7B2-R feasibility gate (repair preregistration section 6).

Runs the BINDING pre-freeze feasibility gate: exploratory, NON-RETAINED
shakedowns at the exact section 3 configuration on the fixed 24-seed table
``20270000 + j`` (``j`` in ``0..23``, fixed in ``stage7b2r_population.py``
before any execution at this ecology and disjoint from the registered
confirmatory table ``{20261822, ..., 20261853}``).  Produces no retained
artifact: everything is printed to stdout as a factual gate summary whose
per-condition pass counts must be recorded in the freeze commit's manifest
notes (section 6.4).

Gate conditions (all mandatory):

- **G1** each genotype is supercritical (``L(0) > 1``, certified by the
  frozen solver contract) individually in at least two-thirds of shakedown
  replicates;
- **G2** both genotypes are simultaneously supercritical in at least
  two-thirds of shakedown replicates;
- **G3** zero ``BUFFER_OVERFLOW`` triggers and zero
  ``INVALID_IMPLEMENTATION`` classifications;
- **G4** every ledger checkpoint closes in every shakedown run (enforced
  structurally: any assertion failure surfaces here as a failed replicate,
  which fails the gate).

If any condition fails, no freeze may be committed; the only correct action
is a further superseding preregistration (section 6.3).  This script never
applies the section 5 decision rule and makes no fitness, selection, or
evolutionary claim; ``L(0)`` statuses are feasibility facts about the
registered ecology, measured with the exact frozen estimators.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import sys
import traceback
from typing import Any

from stage7b2_measure import (
    build_c_vector,
    cohort_genotypes,
    cohort_schedule,
    extract_vital_records,
    fmt_rat,
)
from stage7b2_population import run_window
from stage7b2_solver import certified_bracket
from stage7b2r_population import (
    REGISTERED_REPLICATES,
    SHAKEDOWN_SEED_COUNT,
    registered_configuration,
    registered_population,
    registered_seed,
    shakedown_seed,
    shakedown_seeds,
)


def _gate_threshold(count: int) -> int:
    """Two-thirds ceiling for a shakedown-table size (integer counts)."""
    return -(-2 * count // 3)


def run_shakedown(seed: int) -> dict[str, Any]:
    """One unretained shakedown replicate: population run plus measurement."""
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
        admitted = sum(1 for event in population.event_log
                       if event.get("event") == "birth_admitted")
        genotypes_status: dict[str, str] = {}
        l0_by_genotype: dict[str, str] = {}
        for genotype_a in cohort_genotypes(vitals):
            schedule = cohort_schedule(vitals, genotype_a)
            c_x = build_c_vector(schedule["l_x"], schedule["m_x"])
            certificate = certified_bracket(c_x)
            genotypes_status[str(genotype_a)] = certificate["status"]
            l0_by_genotype[str(genotype_a)] = fmt_rat(certificate["L0_exact"])
        record.update({
            "genotype_status": genotypes_status,
            "L0_exact": l0_by_genotype,
            "max_buffered": max(
                (snapshot.get("buffered", 0)
                 for snapshot in population.closure_history),
                default=0),
            "tick_checkpoints": len(population.closure_history),
            "admitted_births": admitted,
            "shadow_decisions": population.shadow_decisions,
            "ever_alive": len(vitals["members"]),
            "final_census": len(population.members),
        })
    except Exception as error:  # noqa: BLE001 -- gate evidence, never hidden
        record.update({
            "classification": "GATE_EXCEPTION",
            "reason": repr(error),
            "traceback": traceback.format_exc(),
            "gate_failures": ["G3", "G4"],
        })
    return record


def evaluate_gate(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply conditions G1-G4 to the shakedown records."""
    complete = [r for r in records if r.get("classification") == "COMPLETE"]
    invalid = [r for r in records if r.get("classification") != "COMPLETE"]

    def supercritical(r: dict[str, Any], genotype: str) -> bool:
        return r.get("genotype_status", {}).get(genotype) == "SUPERCRITICAL"

    n = len(records)
    threshold = _gate_threshold(n)
    per_genotype = {}
    joint = 0
    for genotype in ("102", "204"):
        count = sum(1 for r in complete if supercritical(r, genotype))
        per_genotype[genotype] = {
            "supercritical_replicates": count,
            "of": len(complete),
            "passes_G1": count >= threshold,
        }
    joint = sum(
        1 for r in complete
        if all(supercritical(r, g) for g in ("102", "204")))
    g3_pass = not invalid and all(
        r.get("reason") != "BUFFER_OVERFLOW" for r in records)
    g4_failures = [r["hazard_seed"] for r in records
                   if "G4" in r.get("gate_failures", [])]
    summary = {
        "gate": "stage-7b2-repair-preregistration section 6",
        "seeds_used": sorted(r["hazard_seed"] for r in records),
        "seed_count": n,
        "two_thirds_threshold": threshold,
        "complete_replicates": len(complete),
        "invalid_replicates": [
            {"hazard_seed": r["hazard_seed"],
             "classification": r.get("classification"),
             "reason": r.get("reason")}
            for r in invalid],
        "G1_per_genotype": per_genotype,
        "G2_joint_supercritical": {
            "replicates": joint,
            "of": len(complete),
            "passes_G2": joint >= threshold,
        },
        "G3_no_overflow_no_invalid": {
            "zero_buffer_overflow": g3_pass,
            "zero_invalid_implementations": not invalid,
            "passes_G3": g3_pass,
        },
        "G4_all_checkpoints_closed": {
            "checkpoint_failures": g4_failures,
            "passes_G4": not g4_failures,
        },
        "gate_passed": (
            all(per_genotype[g]["passes_G1"] for g in ("102", "204"))
            and joint >= threshold
            and g3_pass
            and not g4_failures),
        "registered_configuration_checked": registered_configuration(),
        "claim_scope": ("Feasibility facts only. No fitness, selection, "
                        "contrast, or evolutionary claim is made or "
                        "retained; the confirmatory seed table remains "
                        "untouched until the single retained run."),
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
