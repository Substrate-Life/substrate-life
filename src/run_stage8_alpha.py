"""Stage 8 alpha-evolution runner: executes seeded replicate suites of
``docs/stage-8-alpha-evolution-preregistration.md`` and exports raw
measurements under ``results/stage8-alpha-evolution/``.

Authorisation boundary (preregistration sections 6-7 and 9): this runner may
write a RETAINED artifact for the confirmatory table only AFTER (a) the
section 6 feasibility gate has passed on its fixed 12-seed shakedown table
and (b) the pre-execution freeze whose manifest is
``results/stage8-alpha-evolution/pre-execution-manifest.json`` is committed.
During the implementation window only exploratory, NON-RETAINED shakedown
execution through ``stage8_gate.py`` (stdout-only summaries) is sanctioned;
any other execution at the registered ecology is unauthorised by section 9.
The runner enforces this structurally: an artifact under the retained
results directory requires the exact registered confirmatory table.

The runner applies no decision rule.  It measures the registered endpoints
and co-reports (exact ``Fraction`` arithmetic throughout), records the
kernel-audit evidence, and writes one JSON artifact whose schema is fixed in
``docs/stage8-alpha-output-schema.md``.  The section 5 rule is applied
exactly once by ``reduce_stage8_alpha.py``, the source-frozen reducer.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import hashlib
import importlib
import json
import sys
import traceback
from typing import Any

from stage7b2_measure import (
    extract_vital_records,
    mediator_summary,
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
)
from stage8_alpha_measure import (
    CHECKPOINT_TICKS,
    alpha_terciles,
    births_by_ancestry,
    census_snapshot,
    direction_class,
    genome_freeze_audit,
    kernel_reconciliation,
    run_window_with_checkpoints,
    terminal_snapshot,
)
from stage8_population import (
    CONFIRMATORY_SEED_BASE,
    PROTOCOL,
    SHAKEDOWN_SEED_BASE,
    SHAKEDOWN_SEED_COUNT,
    STAGE8_REPLICATES,
    confirmatory_seed,
    registered_configuration,
    registered_stage8_population,
    shakedown_seed,
)

#: Every source file a retained run depends on; hashed into the artifact.
#: Shared sources are byte-identical to the frozen Stage 7B stack (the
#: preregistration section 7(1) reuse rule); the Stage 8 layers are new.
FROZEN_SOURCES = (
    "stage7b1_mechanics.py",
    "stage7_slice1.py",
    "stage7_slice2.py",
    "datastream.py",
    "transforms.py",
    "consts.py",
    "stage7b2_population.py",
    "stage7b2_measure.py",
    "stage7b2r_population.py",
    "stage8_population.py",
    "stage8_alpha_measure.py",
    "run_stage8_alpha.py",
)


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for filename in FROZEN_SOURCES:
        if filename == "run_stage8_alpha.py":
            path = __file__
        else:
            module = importlib.import_module(filename[:-3])
            path = module.__file__
            assert path is not None
        with open(path, "rb") as handle:
            hashes[filename] = hashlib.sha256(handle.read()).hexdigest()
    return hashes


def _count_events(event_log: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in event_log:
        kind = event.get("event", "?")
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def measure_population(population, *, seed_table: str, replicate_index: int,
                       hazard_seed: int, arm: str | None = None) \
        -> dict[str, Any]:
    """Run one population and assemble its full measurement record.

    Shared by every arm of every generation of this stage: the single-arm
    runner passes the kernel-carrying population (arm ``"M"``), the paired
    repair runner additionally passes the byte-frozen reference population
    (arm ``"R0"``, whose kernel blocks come out empty and passing -- which
    is itself the G4 evidence).  The measurement path is identical; only
    the constructed population differs.
    """
    window = run_window_with_checkpoints(population, CHECKPOINT_TICKS)
    record: dict[str, Any] = {
        "seed_table": seed_table,
        "replicate_index": replicate_index,
        "hazard_seed": hazard_seed,
        "classification": window["classification"],
        "ticks_completed": window["ticks_completed"],
    }
    if arm is not None:
        record["arm"] = arm
    if window["classification"] != "COMPLETE":
        # Layer-1 trigger or worse: retain the evidence, stop measuring.
        record.update({
            "reason": window.get("reason"),
            "detail": window.get("detail"),
            "event_counts": _count_events(population.event_log),
        })
        return record

    event_log = population.event_log
    terminal = terminal_snapshot(window["snapshots"],
                                 population.window_ticks)
    vitals = extract_vital_records(event_log, population.window_ticks)
    admitted = sum(1 for event in event_log
                   if event.get("event") == "birth_admitted")
    decisions = [event for event in event_log
                 if event.get("event") == "mutation_decision"]
    if arm == "R0":
        # Reference arm: the registered evidence is kernel ABSENCE -- zero
        # Stage-M decisions, empty draw chain, no kernel machinery on the
        # object.  Reconciliation does not apply (its supply identity is
        # meaningful only where a kernel exists).
        from stage8_paired import assert_kernel_absent

        assert_kernel_absent(population)
        reconciliation = {
            "decision_records": len(decisions),
            "admitted_births": admitted,
            "memory_unavailable_failures": sum(
                1 for event in event_log
                if event.get("event") == "divide_failed"
                and event.get("reason") == "CHILD_MEMORY_UNAVAILABLE"),
            "draws_total": 0,
            "problems": [] if not decisions else [
                "R0 arm recorded a mutation_decision event"],
            "passes": not decisions,
        }
        draw_chain: list[dict[str, Any]] = []
    else:
        reconciliation = kernel_reconciliation(event_log)
        draw_chain = [
            {
                "stream_position": int(event["stream_position"]),
                "mutated": bool(event["mutated"]),
                "delta": event["delta"],
                "draws_consumed": int(event["draws_consumed"]),
            }
            for event in decisions
        ]
    record.update({
        "window_ticks": population.window_ticks,
        "alpha_end": terminal["alpha_mean"],
        "direction_class": direction_class(terminal["alpha_mean"]),
        "extinct": terminal["n_live"] == 0,
        "terminal_census": terminal,
        "trajectory_checkpoints": [
            {
                "tick": int(tick),
                "n_live": window["snapshots"][tick]["n_live"],
                "alpha_mean": window["snapshots"][tick]["alpha_mean"],
                "distinct_A_values":
                    window["snapshots"][tick]["distinct_A_values"],
            }
            for tick in sorted(window["snapshots"], key=int)
        ],
        "mutation_telemetry": reconciliation,
        # Ordered kernel decision chain (one entry per Stage-M decision):
        # the auditable substrate for the section 6 G3 bit-exact stream
        # replay; empty by construction on the R0 reference arm.
        "kernel_draw_chain": draw_chain,
        "genome_freeze_audit": genome_freeze_audit(event_log),
        "mediators": mediator_summary(vitals,
                                      population.shadow_decisions,
                                      population.shadow_would_admit,
                                      admitted),
        "births_by_ancestry": births_by_ancestry(event_log),
        "terminal_alpha_terciles": alpha_terciles(terminal),
        "shadow_counters": {
            "shadow_decisions": population.shadow_decisions,
            "shadow_would_admit": population.shadow_would_admit,
        },
        "admitted_births_total": population.admitted_births,
        "hazard_removals_total": population.hazard_removals,
        "mutation_stream_seed_derivation":
            (f"random.Random({hazard_seed} * 1000003 + 7)"
             if arm != "R0" else
             "kernel absent on the R0 reference arm (repair registration "
             "section 3); no mutation stream exists"),
        "max_buffered": max(
            (snapshot.get("buffered", 0)
             for snapshot in population.closure_history),
            default=0),
        "tick_checkpoints": len(population.closure_history),
        "closure_history_head":
            [entry["operation"]
             for entry in population.closure_history[:3]],
        "closure_history_tail":
            (population.closure_history[-1]["operation"]
             if population.closure_history else None),
        "event_digest": hashlib.sha256(json.dumps(
            event_log, sort_keys=True, default=str).encode(),
        ).hexdigest(),
        "event_counts": _count_events(event_log),
    })
    return record


def execute_replicate(table: str, index: int) -> dict[str, Any]:
    """One registered single-arm replicate: kernel path (arm ``"M"``).

    ``table`` selects the registered seed table ("confirmatory", k = 24,
    seeds ``20284617 + i``; or "shakedown", k = 12, seeds ``20293311 + j``)
    of the CANCELLED single-arm registration -- retained only because the
    section 6 gate tooling of that generation is still importable; the
    repair registration retires both tables and executes nothing on them.
    """
    if table == "confirmatory":
        hazard_seed = confirmatory_seed(index)
    elif table == "shakedown":
        hazard_seed = shakedown_seed(index)
    else:
        raise ValueError(f"unknown seed table: {table!r}")
    population = registered_stage8_population(hazard_seed)
    return measure_population(
        population, seed_table=table, replicate_index=index,
        hazard_seed=hazard_seed, arm="M")


def execute_replicate_guarded(args_tuple: tuple[str, int]) -> dict[str, Any]:
    """``execute_replicate`` with the registered UNEXPECTED_EXCEPTION class.

    An unexpected exception is an implementation bug (7B1 semantics): the
    replicate is retained as ``INVALID_IMPLEMENTATION`` under the carried
    repair policy instead of losing the whole suite.  Used identically by
    the sequential and parallel execution paths.
    """
    table, index = args_tuple
    try:
        return execute_replicate(table, index)
    except Exception as error:  # noqa: BLE001 -- classified, never hidden
        return {
            "seed_table": table,
            "replicate_index": index,
            "classification": "INVALID_IMPLEMENTATION",
            "reason": "UNEXPECTED_EXCEPTION",
            "detail": repr(error),
            "traceback": traceback.format_exc(),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", choices=("confirmatory", "shakedown"),
                        default="confirmatory",
                        help="registered seed table to execute")
    parser.add_argument("--replicates", type=int, default=None,
                        help="k; defaults to the registered table size "
                             "(confirmatory 24, shakedown 12)")
    parser.add_argument("--workers", type=int, default=1,
                        help="parallel replicate processes; replicates are "
                             "isolated seeded populations, so results are "
                             "bit-identical to sequential execution "
                             "(disclosed in the freeze manifest)")
    parser.add_argument("--out", type=str, default=None,
                        help="path for the raw JSON artifact")
    args = parser.parse_args(argv)

    if args.table == "confirmatory":
        k = STAGE8_REPLICATES if args.replicates is None else args.replicates
        if k != STAGE8_REPLICATES:
            parser.error(
                f"the confirmatory table is registered at exactly "
                f"k = {STAGE8_REPLICATES}; partial or extended suites are "
                "not registered")
        base = CONFIRMATORY_SEED_BASE
    else:
        k = (SHAKEDOWN_SEED_COUNT if args.replicates is None
             else args.replicates)
        if k != SHAKEDOWN_SEED_COUNT:
            parser.error(
                f"the shakedown table is fixed at "
                f"k = {SHAKEDOWN_SEED_COUNT}; it may not be resized")
        base = SHAKEDOWN_SEED_BASE

    if args.out and "stage8-alpha-evolution" in args.out:
        # Retained-directory guard: only the exact registered confirmatory
        # suite may land there (authorisation boundary, sections 7 and 9).
        if not (args.table == "confirmatory"
                and k == STAGE8_REPLICATES):
            parser.error(
                "artifacts under the retained stage8-alpha-evolution "
                "directory require the full registered confirmatory suite")

    indices = list(range(k))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        replicates: list[dict[str, Any]] = list(
            pool.map(execute_replicate_guarded,
                     [(args.table, index) for index in indices]))
    complete = sum(1 for r in replicates
                   if r["classification"] == "COMPLETE")
    raw: dict[str, Any] = {
        "protocol": PROTOCOL,
        "evidence_class": "seeded dedicated-locus mutation-enabled "
                          "population suite under exogenous phenotype-blind "
                          "hazard at the carried ecology; endpoints and "
                          "co-reports measured per the registered sections "
                          "3-4; decision deferred to the reducer",
        "seed_table": args.table,
        "seed_table_derivation": f"hazard_seed = {base} + i, i in 0..{k - 1}",
        "mutation_enabled": True,
        "registered_configuration": registered_configuration(),
        "source_manifest_sha256": _source_hashes(),
        "execution_class": (
            "one seeded suite executed once"
            if args.table == "confirmatory"
            else "exploratory unretained execution (section 6)"),
        "replicates": replicates,
        "integrity": {
            "ledgers_asserted_every_operation":
                "live ledgers verified after every operation; full immutable "
                "history rescanned at every tick-complete checkpoint "
                "(carried assertion machinery, unchanged)",
            "any_checkpoint_failure_aborts_retention": True,
            "kernel_draws_retained_across_rollbacks": True,
        },
        "decision": "PENDING_REDUCTION",
        "decision_scope": (
            "Raw measurement export only. The registered section 5 rule is "
            "applied exactly once by the source-frozen reducer "
            "reduce_stage8_alpha.py; nothing here establishes fitness, "
            "selection, an optimum, an ESS, or any external-validation "
            "mechanism."),
    }
    payload = json.dumps(raw, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
        print(f"wrote {args.out}", file=sys.stderr)
    print(json.dumps({
        "table": args.table,
        "seeds": [base + i for i in indices],
        "replicates_run": len(replicates),
        "complete": complete,
        "invalid_implementations": len(replicates) - complete,
        "decision": raw["decision"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
