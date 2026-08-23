"""Stage 8 paired-arm runner: executes the registered k = 24 pair suite of
``docs/stage-8-alpha-evolution-repair-preregistration.md`` and exports raw
measurements under ``results/stage8-alpha-evolution-paired/``.

Authorisation boundary (repair registration sections 7-10): a RETAINED
artifact for the confirmatory table may be written only AFTER (a) the
section 7 feasibility gate has passed on its fixed 12-pair shakedown table
and (b) the pre-execution freeze whose manifest is
``results/stage8-alpha-evolution-paired/pre-execution-manifest.json`` is
committed.  During the implementation window only exploratory, NON-RETAINED
shakedown execution through ``stage8_paired_gate.py`` (stdout-only
summaries) is sanctioned; anything else at the registered ecology is
unauthorised by section 10.  The runner enforces this structurally: an
artifact under the retained results directory requires the exact
registered confirmatory pair table.

Per pair ``i`` both arms run ``hazard_seed = 20310529 + i``: Arm M (the
registered dedicated-locus kernel, carried verbatim) and Arm R0 (the byte-
frozen stack with the kernel absent).  Each arm's record is assembled by
the shared measurement path of ``run_stage8_alpha.measure_population``;
the runner applies no decision rule -- the section 5 paired rule is applied
exactly once by ``reduce_stage8_paired.py``, the source-frozen reducer.
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

from run_stage8_alpha import measure_population
from stage8_paired import (
    CONFIRMATORY_PAIR_SEED_BASE,
    PAIR_REPLICATES,
    PROTOCOL,
    SHAKEDOWN_PAIR_COUNT,
    SHAKEDOWN_PAIR_SEED_BASE,
    assert_kernel_absent,
    confirmatory_pair_seed,
    registered_configuration,
    registered_m_population,
    registered_r0_population,
    shakedown_pair_seed,
)

#: Every source file a retained paired run depends on; hashed into the
#: artifact.  Shared sources are byte-identical to the frozen Stage 7B
#: stack and the additive Stage 8 layers; the paired layers are new.
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
    "stage8_paired.py",
    "run_stage8_alpha.py",
    "run_stage8_paired.py",
)


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for filename in FROZEN_SOURCES:
        if filename == "run_stage8_paired.py":
            path = __file__
        else:
            module = importlib.import_module(filename[:-3])
            path = module.__file__
            assert path is not None
        with open(path, "rb") as handle:
            hashes[filename] = hashlib.sha256(handle.read()).hexdigest()
    return hashes


def _execute_arm(arm: str, hazard_seed: int, table: str,
                 index: int) -> dict[str, Any]:
    """Construct one arm's population and measure it (no fault tolerance)."""
    if arm == "M":
        population = registered_m_population(hazard_seed)
    elif arm == "R0":
        population = registered_r0_population(hazard_seed)
        assert_kernel_absent(population)
    else:
        raise ValueError(f"unknown arm: {arm!r}")
    return measure_population(
        population, seed_table=table, replicate_index=index,
        hazard_seed=hazard_seed, arm=arm)


def execute_arm_guarded(args: tuple[str, int, str, int]) -> dict[str, Any]:
    """One arm with the registered UNEXPECTED_EXCEPTION classifier.

    Arms are guarded separately so a failure in one arm retains its twin's
    evidence instead of losing the pair.
    """
    arm, hazard_seed, table, index = args
    try:
        return _execute_arm(arm, hazard_seed, table, index)
    except Exception as error:  # noqa: BLE001 -- classified, never hidden
        record: dict[str, Any] = {
            "seed_table": table,
            "replicate_index": index,
            "hazard_seed": hazard_seed,
            "arm": arm,
            "classification": "INVALID_IMPLEMENTATION",
            "reason": "UNEXPECTED_EXCEPTION",
            "detail": repr(error),
            "traceback": traceback.format_exc(),
        }
        return record


def execute_pair(table: str, index: int) -> dict[str, Any]:
    """Both arms of registered pair ``index`` (guarded per arm)."""
    if table == "confirmatory":
        hazard_seed = confirmatory_pair_seed(index)
    elif table == "shakedown":
        hazard_seed = shakedown_pair_seed(index)
    else:
        raise ValueError(f"unknown seed table: {table!r}")
    arms = {
        arm: execute_arm_guarded((arm, hazard_seed, table, index))
        for arm in ("M", "R0")
    }
    return {"pair_index": index, "hazard_seed": hazard_seed,
            "arms": arms}


def _count_pairs(pairs: list[dict[str, Any]]) -> dict[str, int]:
    def complete(record: dict[str, Any]) -> bool:
        return record.get("classification") == "COMPLETE"

    complete_pairs = sum(
        1 for pair in pairs
        if all(complete(record) for record in pair["arms"].values()))
    return {
        "pairs_run": len(pairs),
        "pairs_both_arms_complete": complete_pairs,
        "runs_total": 2 * len(pairs),
        "runs_complete": sum(
            1 for pair in pairs for record in pair["arms"].values()
            if complete(record)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", choices=("confirmatory", "shakedown"),
                        default="confirmatory",
                        help="registered seed table to execute")
    parser.add_argument("--pairs", type=int, default=None,
                        help="k; defaults to the registered table size "
                             "(confirmatory 24 pairs, shakedown 12 pairs)")
    parser.add_argument("--workers", type=int, default=2,
                        help="parallel pair processes; pairs are isolated "
                             "seeded populations, so results are "
                             "bit-identical to sequential execution "
                             "(disclosed in the freeze manifest)")
    parser.add_argument("--out", type=str, default=None,
                        help="path for the raw JSON artifact")
    args = parser.parse_args(argv)

    if args.table == "confirmatory":
        k = PAIR_REPLICATES if args.pairs is None else args.pairs
        if k != PAIR_REPLICATES:
            parser.error(
                f"the confirmatory pair table is registered at exactly "
                f"k = {PAIR_REPLICATES} pairs; partial or extended suites "
                "are not registered")
        base = CONFIRMATORY_PAIR_SEED_BASE
    else:
        k = SHAKEDOWN_PAIR_COUNT if args.pairs is None else args.pairs
        if k != SHAKEDOWN_PAIR_COUNT:
            parser.error(
                f"the shakedown pair table is fixed at "
                f"k = {SHAKEDOWN_PAIR_COUNT}; it may not be resized")
        base = SHAKEDOWN_PAIR_SEED_BASE

    if args.out and "stage8-alpha-evolution-paired" in args.out:
        # Retained-directory guard: only the exact registered confirmatory
        # pair suite may land there (authorisation boundary, §8/§10).
        if not (args.table == "confirmatory" and k == PAIR_REPLICATES):
            parser.error(
                "artifacts under the retained stage8-alpha-evolution-paired "
                "directory require the full registered confirmatory pair "
                "suite")

    indices = list(range(k))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pairs: list[dict[str, Any]] = list(
            pool.map(execute_pair, [args.table] * k, indices))
    raw: dict[str, Any] = {
        "protocol": PROTOCOL,
        "evidence_class": "seeded PAIRED mutation-on/off reference-arm "
                          "population suite under exogenous phenotype-blind "
                          "hazard at the carried ecology; Arm M carries the "
                          "registered kernel, Arm R0 the byte-frozen stack; "
                          "endpoints measured per the registered sections "
                          "3-4; decision deferred to the reducer",
        "seed_table": args.table,
        "seed_table_derivation": f"hazard_seed = {base} + i, i in 0..{k - 1}",
        "mutation_enabled_arms": ["M"],
        "reference_arms": ["R0"],
        "registered_configuration": registered_configuration(),
        "source_manifest_sha256": _source_hashes(),
        "execution_class": (
            "one seeded confirmatory pair suite executed once"
            if args.table == "confirmatory"
            else "exploratory unretained execution (section 7)"),
        "pairs": pairs,
        "integrity": {
            "ledgers_asserted_every_operation":
                "live ledgers verified after every operation; full immutable "
                "history rescanned at every tick-complete checkpoint "
                "(carried assertion machinery, unchanged)",
            "any_checkpoint_failure_aborts_retention": True,
            "kernel_draws_retained_across_rollbacks": True,
            "arm_contrast_is_exactly_the_kernel": True,
        },
        "decision": "PENDING_REDUCTION",
        "decision_scope": (
            "Raw measurement export only. The registered section 5 paired "
            "rule is applied exactly once by the source-frozen reducer "
            "reduce_stage8_paired.py; nothing here establishes fitness, "
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
        **_count_pairs(pairs),
        "decision": raw["decision"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
