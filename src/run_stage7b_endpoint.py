"""Stage 7B endpoint-repair confirmatory runner: executes the registered
k = 32 replicate suite at the carried section 3 ecology under the corrected
raw-fecundity endpoint (``docs/stage-7b-endpoint-repair-preregistration.md``
sections 3-4) and exports raw measurements under
``results/stage7b-endpoint-repair/``.

Authorisation boundary (endpoint-repair prereg sections 5, 6 and 8): this
runner may only be executed for retention AFTER (a) the section 5 feasibility
gate has passed on its reused fixed shakedown table and (b) the single-commit
freeze whose manifest is
``results/stage7b-endpoint-repair/pre-execution-manifest.json`` is committed.
During the implementation window only the section 5 exploratory,
NON-RETAINED shakedowns (``stage7b_endpoint_gate.py``) are sanctioned; any
other execution at the registered ecology is unauthorised by section 8.

The runner applies no decision rule.  It measures with the corrected
endpoint (raw age-specific fecundity ``m_x``; the establishment/first-
reproduction quantity stays a reported mediator), certifies solver brackets
with the byte-identical frozen solver, records classifications and
identities, and writes one JSON artifact whose schema is fixed in
``docs/stage7b-endpoint-output-schema.md``.  The carried section 5 rule is
applied exactly once by ``reduce_stage7b_endpoint.py``, the source-frozen
reducer.  The existing frozen modules ``stage7b2_measure.py``,
``stage7b2_population.py``, ``stage7b2_solver.py``, and
``stage7b2r_population.py`` are reused unmodified.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
import argparse
import hashlib
import importlib
import json
import sys
from typing import Any

from stage7b2_measure import (
    build_c_vector,
    cohort_genotypes,
    extract_vital_records,
    fmt_rat,
)
from stage7b2_population import run_window
from stage7b2_solver import certified_bracket
from stage7b_endpoint_config import (
    PREREG_DOCUMENT,
    PROTOCOL,
    endpoint_configuration,
    endpoint_decision_rule_inputs,
    registered_population,
    registered_seed,
)
from stage7b_endpoint_measure import endpoint_schedule

#: Every source file a retained run depends on; hashed into the artifact.
#: Shared sources stay byte-identical to their retained freezes/pins
#: (endpoint-repair prereg sections 5.1 and 8); only the configuration,
#: measurement-numerator, runner, reducer, gate, tests, and schema are new.
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
    "stage7b_endpoint_measure.py",
    "stage7b_endpoint_config.py",
    "run_stage7b_endpoint.py",
)


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for filename in FROZEN_SOURCES:
        if filename == "run_stage7b_endpoint.py":
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
                                   population.window_ticks)
    schedules: dict[int, Any] = {}
    certificates: dict[int, Any] = {}
    for genotype_a in cohort_genotypes(vitals):
        schedule = endpoint_schedule(vitals, genotype_a)
        c_x = build_c_vector(schedule["l_x"], schedule["m_x"])
        certificate = certified_bracket(c_x)
        schedules[genotype_a] = {
            "cohort_size": schedule["cohort_size"],
            "died": schedule["died"],
            "censored": schedule["censored"],
            "exposure_member_ticks": schedule["exposure_member_ticks"],
            "l_x": [fmt_rat(v) for v in schedule["l_x"]],
            # Corrected ENDPOINT numerator (raw fecundity):
            "m_x": [fmt_rat(v) for v in schedule["m_x"]],
            # Reported MEDIATOR (former endpoint), never substituted:
            "establishment_m_x": [fmt_rat(v)
                                  for v in schedule["establishment_m_x"]],
            "births_credited": schedule["births_credited"],
            "establishments_credited": schedule["establishments_credited"],
        }
        certificates[genotype_a] = _serialise_certificate(certificate)
    mediators = _mediator_summary(population, vitals)
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
            # Births are estimator inputs of the corrected raw-fecundity
            # m_x; retained so the reducer recomputes it independently.
            "births": [_serialise_birth(birth)
                       for birth in vitals["births"]],
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


def run_replicate_guarded(index: int) -> dict[str, Any]:
    """``run_replicate`` with the registered UNEXPECTED_EXCEPTION classifier.

    An unexpected exception is an implementation bug (7B1 semantics): the
    replicate is retained as ``INVALID_IMPLEMENTATION`` under the
    architecture section 9 repair policy instead of losing the whole suite.
    Used identically by the sequential and parallel execution paths.
    """
    try:
        return run_replicate(index)
    except Exception as error:  # noqa: BLE001 -- classified, never hidden
        import traceback
        return {
            "replicate_index": index,
            "hazard_seed": registered_seed(index),
            "classification": "INVALID_IMPLEMENTATION",
            "reason": "UNEXPECTED_EXCEPTION",
            "detail": repr(error),
            "traceback": traceback.format_exc(),
        }


def _mediator_summary(population: Any, vitals: dict[str, Any]) -> dict[str, Any]:
    """Reported mediators via the frozen summary, plus the establishment
    mediator counts.  Mediators earn nothing on their own and are never
    substituted for the endpoint (endpoint-repair prereg section 3)."""
    from stage7b2_measure import mediator_summary
    return mediator_summary(vitals, population.shadow_decisions,
                            population.shadow_would_admit,
                            population.admitted_births)


def _count_events(event_log: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in event_log:
        kind = event.get("event", "?")
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def _serialise_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"status": certificate["status"]}
    if "support" in certificate:
        out["support"] = certificate["support"]
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


def _serialise_birth(birth: dict[str, Any]) -> dict[str, Any]:
    """Exact serialisation of one estimator-input birth record."""
    provision = birth.get("provision")
    if isinstance(provision, Fraction):
        provision = fmt_rat(provision)
    return {
        "child_id": birth["child_id"],
        "parent_id": birth["parent_id"],
        "tick": int(birth["tick"]),
        "genotype_a": int(birth["genotype_a"]),
        "provision": provision,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=str, default=None,
                        help="path for the retained JSON artifact")
    parser.add_argument("--replicates", type=int, default=32,
                        help="k; only the frozen k = 32 suite may be retained")
    parser.add_argument("--workers", type=int, default=1,
                        help="parallel replicate processes; replicates are "
                             "isolated seeded populations, so results are "
                             "bit-identical to sequential execution "
                             "(disclosed in the freeze manifest)")
    args = parser.parse_args(argv)

    indices = list(range(args.replicates))
    # Both paths use the same guarded replicate function, so classification
    # semantics are identical; parallelism only reorders wall-clock work,
    # never results (isolated seeded populations, ordered map).
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        replicates: list[dict[str, Any]] = list(
            pool.map(run_replicate_guarded, indices))
    complete = sum(1 for r in replicates
                   if r["classification"] == "COMPLETE")
    invalid = len(replicates) - complete
    raw: dict[str, Any] = {
        "protocol": PROTOCOL,
        "prereg_document": PREREG_DOCUMENT,
        "evidence_class": "seeded, mutation-disabled confirmatory "
                          "population suite under exogenous phenotype-blind "
                          "hazard at the carried section 3 ecology "
                          "(N=48, E=900, W=1200); endpoint measured per the "
                          "corrected section 3 (raw age-specific fecundity "
                          "m_x); decision deferred to the reducer",
        "selection_assay_run": False,
        "mutation_enabled": False,
        "registered_configuration": endpoint_configuration(),
        "decision_rule_inputs": endpoint_decision_rule_inputs(),
        "source_manifest_sha256": _source_hashes(),
        "execution_class": "one seeded confirmatory suite (endpoint-repair "
                           "prereg section 6.3), executed once after the "
                           "section 5 gate passed and the section 6 freeze "
                           "committed",
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
            "by docs/stage-7b2-repair-preregistration.md section 3 and by "
            "docs/stage-7b-endpoint-repair-preregistration.md) is applied "
            "exactly once by the source-frozen reducer "
            "reduce_stage7b_endpoint.py over the corrected endpoint; "
            "nothing here establishes fitness, selection, an optimum, an "
            "ESS, or any external-validation mechanism."),
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
