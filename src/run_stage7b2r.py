"""Stage 7B2-R confirmatory runner: executes the registered k = 32 replicate
suite of ``docs/stage-7b2-repair-preregistration.md`` Section 3 (carrying the
Section 5 rule of ``docs/stage-7b2-preregistration.md`` verbatim) and exports
raw measurements under ``results/stage7b2-repair/``.

Authorisation boundary (repair preregistration Sections 6-7 and 9): this
runner may only be executed for retention AFTER (a) the Section 6 feasibility
gate has passed on its fixed shakedown table and (b) the single-commit freeze
whose manifest is ``results/stage7b2-repair/pre-execution-manifest.json`` is
committed.  During the implementation window only the Section 6 exploratory,
NON-RETAINED shakedowns (``stage7b2r_gate.py``) are sanctioned; any other
execution at the registered ecology is unauthorised by Section 9.

The runner applies no decision rule.  It measures, certifies solver
brackets, records classifications and identities, and writes one JSON
artifact whose schema is fixed in ``docs/stage7b2r-output-schema.md``.  The
carried Section 5 rule is applied exactly once by ``reduce_stage7b2r.py``,
the source-frozen reducer.
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
from stage7b2_population import run_window
from stage7b2_solver import (
    MIN_CONTRAST_DELTA_R,
    SOLVER_RESOLUTION_RHO,
    certified_bracket,
)
from stage7b2r_population import (
    REGISTERED_BUFFER_DEPTH,
    REGISTERED_CENSUS_CAPACITY,
    REGISTERED_CORPSE_TTL,
    REGISTERED_FOUNDER_S,
    REGISTERED_GENOTYPES,
    REGISTERED_HAZARD_RATE,
    REGISTERED_MEMORY_POOL,
    REGISTERED_PACKET_ENERGY,
    REGISTERED_REPLICATES,
    REGISTERED_WINDOW_TICKS,
    registered_configuration,
    registered_population,
    registered_seed,
)

#: Every source file a retained run depends on; hashed into the artifact.
#: Shared sources are byte-identical to the retained Stage 7B2 freeze
#: (repair preregistration section 7.2); the configuration layer is new.
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
    "stage7b2r_population.py",
    "run_stage7b2r.py",
)


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for filename in FROZEN_SOURCES:
        if filename == "run_stage7b2r.py":
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


def decision_rule_inputs() -> dict[str, Any]:
    """Carried section 5 rule constants embedded in every artifact."""
    return {
        "solver_resolution_rho_r": fmt_rat(SOLVER_RESOLUTION_RHO),
        "minimum_contrast_delta_r_min": fmt_rat(MIN_CONTRAST_DELTA_R),
        "minimum_complete_pairs": 16,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=str, default=None,
                        help="path for the retained JSON artifact")
    parser.add_argument("--replicates", type=int,
                        default=REGISTERED_REPLICATES,
                        help="k; only the frozen k = 32 suite may be retained")
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
        "protocol": "stage-7b2r-preregistration",
        "evidence_class": "seeded, mutation-disabled confirmatory "
                          "population suite under exogenous phenotype-blind "
                          "hazard at the repaired section 3 ecology; "
                          "endpoint measured per the carried sections 3-4; "
                          "decision deferred to the reducer",
        "selection_assay_run": False,
        "mutation_enabled": False,
        "registered_configuration": registered_configuration(),
        "decision_rule_inputs": decision_rule_inputs(),
        "source_manifest_sha256": _source_hashes(),
        "execution_class": "one seeded confirmatory suite (repair prereg "
                           "section 7.3), executed once after the section 6 "
                           "gate passed and the section 7 freeze committed",
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
            "Raw measurement export only. The carried section 5 rule "
            "(docs/stage-7b2-preregistration.md section 5, carried verbatim "
            "by docs/stage-7b2-repair-preregistration.md section 3) is "
            "applied exactly once by the source-frozen reducer "
            "reduce_stage7b2r.py; nothing here establishes fitness, "
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
