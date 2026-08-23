"""Stage 7B two-factor feasibility gate (denominator-repair prereg section 5).

Tooling for the BINDING pre-freeze feasibility gate registered at
``docs/stage-7b-denominator-repair-preregistration.md`` section 5:
exploratory, NON-RETAINED shakedowns at the exact carried ecology on the
**same fixed 24-seed table used by both prior gate generations**
(``20270000 + j``, ``j`` in ``0..23``; no new seed draw is needed or
permitted, section 5.2 -- a third reuse on identical seeds isolates the
repaired endpoint layer).  Produces no retained artifact: everything is
printed to stdout as a factual gate summary whose per-replicate evidence
and per-condition pass counts must be recorded in the freeze commit's
manifest notes (section 5.5) -- but only if the gate passes and a freeze is
actually committed.

Gate conditions (all mandatory, unchanged across generations):

- **G1** each genotype is supercritical (``L(0) > 1``, certified by the
  frozen solver contract over the repaired coefficients ``c_x = l^A_x *
  m^E_x``) individually in at least two-thirds of shakedown replicates;
- **G2** both genotypes are simultaneously supercritical in at least
  two-thirds of shakedown replicates;
- **G3** zero ``BUFFER_OVERFLOW`` triggers and zero
  ``INVALID_IMPLEMENTATION`` classifications;
- **G4** every ledger checkpoint closes in every shakedown run (enforced
  structurally: any assertion failure surfaces here as a failed replicate,
  which fails the gate).

Additionally, per denominator-repair prereg section 3, every replicate's
binding identities (exposure partition, births-vs-person-ticks) are
enforced inside the estimator and surface as G4 failures if violated.

If any condition fails, no freeze may be committed; the only correct action
is a further superseding preregistration with a diagnosis supported by new
evidence (section 5.4).  This script never applies the carried section 5
decision rule and makes no fitness, selection, or evolutionary claim;
``L(0)`` statuses are feasibility facts about the registered ecology,
measured with the exact frozen solver over the repaired endpoint.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import sys
import traceback
from typing import Any

from stage7b2_measure import (
    cohort_genotypes,
    extract_vital_records,
    fmt_rat,
)
from stage7b2_population import run_window
from stage7b2_solver import certified_bracket
from stage7b_exposure_config import (
    PREREG_DOCUMENT,
    PROTOCOL,
    endpoint_configuration,
    registered_population,
    shakedown_seeds,
)
from stage7b_exposure_measure import exposure_schedule, lotka_coefficients


def _gate_threshold(count: int) -> int:
    """Two-thirds ceiling for a shakedown-table size (integer counts)."""
    return -(-2 * count // 3)


def _count_events(event_log: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in event_log:
        kind = event.get("event", "?")
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def run_shakedown(seed: int) -> dict[str, Any]:
    """One unretained shakedown replicate under the repaired endpoint."""
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
        births_credited: dict[str, int] = {}
        person_ticks: dict[str, int] = {}
        cohort_sizes: dict[str, int] = {}
        for genotype_a in cohort_genotypes(vitals):
            schedule = exposure_schedule(vitals, genotype_a)
            c_x = lotka_coefficients(schedule)
            certificate = certified_bracket(c_x)
            genotypes_status[str(genotype_a)] = certificate["status"]
            l0_by_genotype[str(genotype_a)] = fmt_rat(certificate["L0_exact"])
            births_credited[str(genotype_a)] = schedule["births_credited"]
            person_ticks[str(genotype_a)] = schedule["person_ticks_credited"]
            cohort_sizes[str(genotype_a)] = schedule["cohort_size"]
        record.update({
            "genotype_status": genotypes_status,
            "L0_exact": l0_by_genotype,
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
    per_genotype: dict[str, dict[str, Any]] = {}
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
        "failure_guidance": (
            "Section 5.4: if any condition fails, no freeze may be "
            "committed; the correct action is a further superseding "
            "preregistration with a diagnosis supported by new evidence.  "
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
