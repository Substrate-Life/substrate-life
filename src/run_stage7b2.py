"""Stage 7B2 confirmatory runner: executes the registered k = 32 replicate
suite of ``docs/stage-7b2-preregistration.md`` Section 2 and exports raw
measurements under ``results/stage7b2/``.

Authorisation boundary (preregistration Section 8): this runner may only be
executed for retention AFTER the single-commit freeze whose manifest is
``results/stage7b2/pre-execution-manifest.json``.  During the implementation
window it may be exercised on exploratory, NON-RETAINED configurations only
(disclosed calibration checks; outputs kept outside the repository).

The runner applies no decision rule.  It measures, certifies solver
brackets, records classifications and identities, and writes one JSON
artifact whose schema is fixed in ``docs/stage7b2-output-schema.md``.  The
Section 5 rule is applied exactly once by ``reduce_stage7b2.py``, the
source-frozen reducer.
"""

from __future__ import annotations

from fractions import Fraction
import argparse
import hashlib
import importlib
import json
import sys
from typing import Any

from stage7b2_measure import (
    build_c_vector,
    cohort_schedule,
    cohort_genotypes,
    extract_vital_records,
    fmt_rat,
    mediator_summary,
)
from stage7b2_population import (
    REGISTERED_BUFFER_DEPTH,
    REGISTERED_CENSUS_CAPACITY,
    REGISTERED_CORPSE_TTL,
    REGISTERED_FOUNDER_S,
    REGISTERED_GENOTYPES,
    REGISTERED_HAZARD_RATE,
    REGISTERED_PACKET_ENERGY,
    REGISTERED_REPLICATES,
    REGISTERED_WINDOW_TICKS,
    registered_population,
    registered_seed,
    run_window,
)
from stage7b2_solver import (
    MIN_CONTRAST_DELTA_R,
    SOLVER_RESOLUTION_RHO,
    certified_bracket,
)

#: Every source file a retained run depends on; hashed into the artifact.
FROZEN_SOURCES = (
    "stage7b1_mechanics.py",
    "stage7_slice1.py",
    "stage7_slice2.py",
    "datastream.py",
    "transforms.py",
    "consts.py",
    "stage7b2_population.py",
    "stage7b2_measure.py",
    "stage7b2_solver.py",
    "run_stage7b2.py",
)


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for filename in FROZEN_SOURCES:
        if filename == "run_stage7b2.py":
            path = __file__
        else:
            module = importlib.import_module(filename[:-3])
            path = module.__file__
            assert path is not None
        with open(path, "rb") as handle:
            hashes[filename] = hashlib.sha256(handle.read()).hexdigest()
    return hashes


def run_replicate(index: int) -> dict[str, Any]:
    """One registered replicate: population run plus exact measurement."""
    hazard_seed = registered_seed(index)
    population = registered_population(hazard_seed)
    classification = run_window(population)
    record: dict[str, Any] = {
        "replicate_index": index,
        "hazard_seed": hazard_seed,
        **classification,
    }
    if classification["classification"] != "COMPLETE":
        # Layer-1 trigger or worse: retain the evidence, stop measuring.
        record["event_counts"] = _count_events(population.event_log)
        return record

    vitals = extract_vital_records(population.event_log,
                                   REGISTERED_WINDOW_TICKS)
    schedules: dict[int, Any] = {}
    certificates: dict[int, Any] = {}
    for genotype_a in cohort_genotypes(vitals):
        schedule = cohort_schedule(vitals, genotype_a)
        c_x = build_c_vector(schedule["l_x"], schedule["m_x"])
        certificate = certified_bracket(c_x, SOLVER_RESOLUTION_RHO)
        schedules[genotype_a] = {
            "cohort_size": schedule["cohort_size"],
            "died": schedule["died"],
            "censored": schedule["censored"],
            "exposure_member_ticks": schedule["exposure_member_ticks"],
            "l_x": [fmt_rat(v) for v in schedule["l_x"]],
            "m_x": [fmt_rat(v) for v in schedule["m_x"]],
        }
        certificates[genotype_a] = _serialise_certificate(certificate)
    admitted = sum(1 for event in population.event_log
                   if event.get("event") == "birth_admitted")
    mediators = mediator_summary(vitals, population.shadow_decisions,
                                 population.shadow_would_admit, admitted)
    record.update({
        "vital_records": {
            "members": {
                oid: {
                    "genotype_a": entry["genotype_a"],
                    "born_tick": entry["born_tick"],
                    "death_tick": entry["death_tick"],
                }
                for oid, entry in vitals["members"].items()
            },
            "establishments": [dict(event)
                               for event in vitals["establishments"]],
            "attempt_counters": vitals["attempt_counters"],
        },
        "cohort_schedules": {str(g): s for g, s in sorted(schedules.items())},
        "solver_certificates": {str(g): c
                                for g, c in sorted(certificates.items())},
        "mediators": mediators,
        "shadow_counters": {
            "shadow_decisions": population.shadow_decisions,
            "shadow_would_admit": population.shadow_would_admit,
        },
        "admitted_births_total": population.admitted_births,
        "hazard_removals_total": population.hazard_removals,
        "max_buffered": max(
            (snapshot.get("buffered", 0)
             for snapshot in population.closure_history),
            default=0),
        "tick_checkpoints": len(population.closure_history),
        "event_digest": hashlib.sha256(json.dumps(
            population.event_log, sort_keys=True, default=str).encode(),
        ).hexdigest(),
        "event_counts": _count_events(population.event_log),
    })
    return record


def _count_events(event_log: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in event_log:
        kind = event.get("event", "?")
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def _serialise_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"status": certificate["status"]}
    for key in ("support",):
        if key in certificate:
            out[key] = certificate[key]
    out["L0_exact"] = fmt_rat(certificate["L0_exact"])
    if certificate["status"] == "SUPERCRITICAL":
        out.update({
            "r_lo": fmt_rat(certificate["r_lo"]),
            "r_hi": fmt_rat(certificate["r_hi"]),
            "width": fmt_rat(certificate["width"]),
            "iterations": certificate["iterations"],
            "rho": fmt_rat(certificate["rho"]),
            "certified": certificate["certified"],
        })
    return out


def registered_configuration() -> dict[str, Any]:
    """Echo of the binding Section 2 values embedded in every artifact."""
    return {
        "window_ticks_W": REGISTERED_WINDOW_TICKS,
        "census_capacity_N": REGISTERED_CENSUS_CAPACITY,
        "buffer_depth_d": REGISTERED_BUFFER_DEPTH,
        "packet_rate_r": 5,
        "hazard_arms": ["1/120 per live member per tick"],
        "replicates_k": REGISTERED_REPLICATES,
        "seed_derivation": "hazard_seed = 20260822 + i, i in 0..31",
        "solver_resolution_rho_r": fmt_rat(SOLVER_RESOLUTION_RHO),
        "minimum_contrast_delta_r_min": fmt_rat(MIN_CONTRAST_DELTA_R),
        "genotypes_ATD": [list(g) for g in REGISTERED_GENOTYPES],
        "founders_per_genotype": 3,
        "founder_S": fmt_rat(REGISTERED_FOUNDER_S),
        "founder_R": "0/1",
        "corpse_ttl": REGISTERED_CORPSE_TTL,
        "packet_energy": fmt_rat(REGISTERED_PACKET_ENERGY),
        "mutation": "disabled; structural zero-draw M stage",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=str, default=None,
                        help="path for the retained JSON artifact")
    parser.add_argument("--replicates", type=int,
                        default=REGISTERED_REPLICATES,
                        help="k; exploratory non-retained runs may lower it")
    args = parser.parse_args(argv)

    replicates: list[dict[str, Any]] = []
    for index in range(args.replicates):
        try:
            replicates.append(run_replicate(index))
        except Exception as error:  # noqa: BLE001 -- classified, never hidden
            # An unexpected exception is an implementation bug (7B1
            # semantics): the replicate is retained as
            # INVALID_IMPLEMENTATION under the architecture section 9
            # repair policy instead of losing the whole suite.
            import traceback
            replicates.append({
                "replicate_index": index,
                "hazard_seed": registered_seed(index),
                "classification": "INVALID_IMPLEMENTATION",
                "reason": "UNEXPECTED_EXCEPTION",
                "detail": repr(error),
                "traceback": traceback.format_exc(),
            })
    complete = sum(1 for r in replicates
                   if r["classification"] == "COMPLETE")
    invalid = len(replicates) - complete
    raw: dict[str, Any] = {
        "protocol": "stage-7b2-preregistration",
        "evidence_class": "seeded, mutation-disabled confirmatory "
                          "population suite under exogenous phenotype-blind "
                          "hazard; endpoint measured per preregistration "
                          "sections 3-4; decision deferred to the reducer",
        "selection_assay_run": False,
        "mutation_enabled": False,
        "registered_configuration": registered_configuration(),
        "source_manifest_sha256": _source_hashes(),
        "execution_class": "one seeded confirmatory suite (prereg section 8.3)",
        "replicates": replicates,
        "integrity": {
            "ledgers_asserted_every_operation":
                "live ledgers verified after every operation; full immutable "
                "history rescanned at every tick-complete checkpoint "
                "(stage7b2_population.assert_all_ledgers)",
            "any_checkpoint_failure_aborts_retention": True,
        },
        "decision": "PENDING_REDUCTION",
        "decision_scope": (
            "Raw measurement export only. The preregistration section 5 "
            "decision rule is applied exactly once by the source-frozen "
            "reducer reduce_stage7b2.py; nothing here establishes fitness, "
            "selection, an optimum, an ESS, or any external-validation "
            "mechanism."),
    }
    payload = json.dumps(raw, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
        print(f"wrote {args.out}", file=sys.stderr)
    print(json.dumps({
        "replicates_run": len(replicates),
        "complete": complete,
        "invalid_implementations": invalid,
        "decision": raw["decision"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
