"""Stage 8 alpha-evolution reducer: the source-frozen section 5 decision rule.

Applies the registered decision rule of
``docs/stage-8-alpha-evolution-preregistration.md`` section 5 EXACTLY ONCE to
one retained raw artifact produced by ``run_stage8_alpha.py``:

Let ``k_eff`` = number of **eligible** replicates -- classification COMPLETE
with >= 1 live member at tick W (= 2400).  Direction classes per replicate:
mover-up iff ``ᾱ_end - α_ref >= Δα_floor``; mover-down iff
``<= -Δα_floor``; with ``α_ref = 153/255``, ``Δα_floor = 8/255``.

1. ``DEGENERATE_EVOLUTION``   -- ``k_eff < 16``
2. ``ESTABLISHED_TOWARD_HIGH_ALPHA`` -- ``k_eff >= 16`` and movers-up >= 18
3. ``ESTABLISHED_TOWARD_LOW_ALPHA``  -- ``k_eff >= 16`` and movers-down >= 18
4. ``NO_ESTABLISHED_DIRECTION``      -- otherwise

Exactly one class is emitted.  Thresholds 16/18/24, the floor, the kernel,
and both seed tables are frozen by the preregistration; retuning any of them
after any execution is prohibited (section 9).

Before applying the rule the reducer independently validates the artifact:
registered protocol and seed table, exact replicate set, kernel-audit and
genome-freeze passes carried in every COMPLETE record, terminal-snapshot
consistency (``ᾱ_end`` recomputed from the terminal histogram), and the
recorded direction classes recomputed from the endpoint values.  Any
validation failure aborts without emitting a classification.

Co-reported alongside, descriptively (never endpoints): concordance counts,
median ``|ᾱ_end - α_ref|`` among movers, trajectory shapes, terminal
histograms, recruitment telemetry, extinctions.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from typing import Any

from stage7b2_measure import fmt_rat, parse_rat
from stage8_alpha_measure import (
    CHECKPOINT_TICKS,
    direction_class,
)
from stage8_population import (
    ALPHA_REF,
    CONFIRMATORY_SEED_BASE,
    DIRECTION_FLOOR_ALPHA,
    PROTOCOL,
    REGISTERED_WINDOW_TICKS_STAGE8,
    STAGE8_REPLICATES,
    confirmatory_seed,
)

#: Registered rule constants (section 5) embedded in the outcome block.
RULE_CONSTANTS = {
    "alpha_ref": fmt_rat(ALPHA_REF),
    "direction_floor_alpha": fmt_rat(DIRECTION_FLOOR_ALPHA),
    "minimum_eligible_k_eff": 16,
    "concordance_threshold": 18,
    "replicates_k": STAGE8_REPLICATES,
    "window_ticks_W": REGISTERED_WINDOW_TICKS_STAGE8,
}


class ReducerValidationError(RuntimeError):
    """The raw artifact failed pre-rule validation; no class is emitted."""


def _validate(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Structural + arithmetic validation; returns the replicate records."""
    if raw.get("protocol") != PROTOCOL:
        raise ReducerValidationError(
            f"protocol mismatch: {raw.get('protocol')!r}")
    if raw.get("seed_table") != "confirmatory":
        raise ReducerValidationError(
            "the section 5 rule applies to the confirmatory table only; "
            f"got {raw.get('seed_table')!r}")
    if raw.get("decision") != "PENDING_REDUCTION":
        raise ReducerValidationError(
            f"artifact decision field is {raw.get('decision')!r}, "
            "not PENDING_REDUCTION (double reduction refused)")
    replicates = raw.get("replicates")
    if not isinstance(replicates, list) or \
            len(replicates) != STAGE8_REPLICATES:
        raise ReducerValidationError(
            f"expected exactly {STAGE8_REPLICATES} replicate records")
    expected_seeds = [confirmatory_seed(i) for i in range(STAGE8_REPLICATES)]
    seeds = [record.get("hazard_seed") for record in replicates]
    if seeds != expected_seeds:
        raise ReducerValidationError(
            f"seed table mismatch: {seeds} != {expected_seeds}")

    window = REGISTERED_WINDOW_TICKS_STAGE8
    for record in replicates:
        index = record["replicate_index"]
        if record["classification"] == "COMPLETE":
            terminal = record.get("terminal_census")
            if terminal is None or terminal.get("tick") != window:
                raise ReducerValidationError(
                    f"replicate {index}: missing tick-{window} snapshot")
            checkpoints = record.get("trajectory_checkpoints", [])
            if [int(c["tick"]) for c in checkpoints] != \
                    [t for t in CHECKPOINT_TICKS]:
                raise ReducerValidationError(
                    f"replicate {index}: checkpoint ticks incomplete")
            if checkpoints[-1]["n_live"] != terminal["n_live"]:
                raise ReducerValidationError(
                    f"replicate {index}: final checkpoint disagrees with "
                    "terminal census")
            # Independent recomputation of ᾱ_end from the terminal histogram.
            histogram = {int(a): int(count) for a, count
                         in terminal["histogram_A"].items()}
            recomputed_sum = sum(a * count for a, count in histogram.items())
            n_live = terminal["n_live"]
            if sum(histogram.values()) != n_live:
                raise ReducerValidationError(
                    f"replicate {index}: histogram mass != live census")
            alpha_recomputed = Fraction(recomputed_sum, 255 * n_live) \
                if n_live else None
            if n_live and alpha_recomputed != parse_rat(record["alpha_end"]):
                raise ReducerValidationError(
                    f"replicate {index}: alpha_end != histogram "
                    "recomputation")
            if record.get("extinct") != (n_live == 0):
                raise ReducerValidationError(
                    f"replicate {index}: extinction flag inconsistent")
            # Carried kernel-audit evidence must be present and passing.
            for key in ("mutation_telemetry", "genome_freeze_audit"):
                block = record.get(key)
                if not isinstance(block, dict) or block.get("passes") is not \
                        True:
                    raise ReducerValidationError(
                        f"replicate {index}: {key} absent or failing")
            # Recorded direction class must match the endpoint value.
            if n_live and record.get("direction_class") != \
                    direction_class(record["alpha_end"]):
                raise ReducerValidationError(
                    f"replicate {index}: direction class mismatch")
    return replicates


def apply_rule(replicates: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply the registered section 5 rule; emit exactly one class."""
    window = REGISTERED_WINDOW_TICKS_STAGE8
    eligible_indices = {
        index for index, record in enumerate(replicates)
        if record["classification"] == "COMPLETE"
        and record["terminal_census"]["tick"] == window
        and record["terminal_census"]["n_live"] >= 1}
    eligible = [r for index, r in enumerate(replicates)
                if index in eligible_indices]
    ineligible = [r for index, r in enumerate(replicates)
                  if index not in eligible_indices]
    k_eff = len(eligible)

    movers_up = [r for r in eligible if r["direction_class"] == "mover_up"]
    movers_down = [r for r in eligible
                   if r["direction_class"] == "mover_down"]
    non_movers = [r for r in eligible
                  if r["direction_class"] == "non_mover"]

    if k_eff < RULE_CONSTANTS["minimum_eligible_k_eff"]:
        outcome = "DEGENERATE_EVOLUTION"
    elif len(movers_up) >= RULE_CONSTANTS["concordance_threshold"]:
        outcome = "ESTABLISHED_TOWARD_HIGH_ALPHA"
    elif len(movers_down) >= RULE_CONSTANTS["concordance_threshold"]:
        outcome = "ESTABLISHED_TOWARD_LOW_ALPHA"
    else:
        outcome = "NO_ESTABLISHED_DIRECTION"

    def _median_abs_difference(movers: list[dict[str, Any]]) -> str | None:
        if not movers:
            return None
        differences = sorted(parse_rat(r["alpha_end"]) - ALPHA_REF
                             for r in movers)
        count = len(differences)
        mid = count // 2
        median = (differences[mid] if count % 2
                  else (differences[mid - 1] + differences[mid]) / 2)
        return fmt_rat(abs(median))

    extinctions = [
        {"replicate_index": r["replicate_index"],
         "hazard_seed": r["hazard_seed"]}
        for r in replicates
        if r["classification"] == "COMPLETE"
        and r["terminal_census"]["tick"] == window
        and r["terminal_census"]["n_live"] == 0]

    return {
        "outcome": outcome,
        "rule_constants": dict(RULE_CONSTANTS),
        "applied_exactly_once": True,
        "counts": {
            "replicates": len(replicates),
            "complete": sum(1 for r in replicates
                            if r["classification"] == "COMPLETE"),
            "eligible_k_eff": k_eff,
            "ineligible": [
                {"replicate_index": r["replicate_index"],
                 "reason": (
                     "classification="
                     f"{r.get('classification')}"
                     if r.get("classification") != "COMPLETE"
                     else "extinct_at_W")}
                for r in ineligible],
            "movers_up": len(movers_up),
            "movers_down": len(movers_down),
            "non_movers": len(non_movers),
            "extinct_replicates": extinctions,
        },
        "descriptive": {
            "median_abs_delta_alpha_among_movers_up":
                _median_abs_difference(movers_up),
            "median_abs_delta_alpha_among_movers_down":
                _median_abs_difference(movers_down),
            "alpha_end_by_replicate": {
                str(r["hazard_seed"]): (
                    r["alpha_end"] if r["classification"] == "COMPLETE"
                    else None)
                for r in replicates},
            "terminal_histograms": {
                str(r["hazard_seed"]):
                    r.get("terminal_census", {}).get("histogram_A")
                for r in replicates},
            "trajectories": {
                str(r["hazard_seed"]): r.get("trajectory_checkpoints")
                for r in replicates},
            "recruitment_telemetry": {
                str(r["hazard_seed"]): r.get("mediators")
                for r in replicates},
            "births_by_ancestry": {
                str(r["hazard_seed"]): r.get("births_by_ancestry")
                for r in replicates},
            "terminal_alpha_terciles": {
                str(r["hazard_seed"]): r.get("terminal_alpha_terciles")
                for r in replicates},
        },
        "scope": (
            "Level-2 statement space only: 'the restricted architecture "
            "does / does not evolve through the channel, in the registered "
            "direction(s), at this ecology and kernel'.  No external "
            "validation, optimum, ESS, invasion-growth, causal-gradient, or "
            "open-genome claim is licensed; recruitment/vacancy/capture "
            "telemetry remains mediator-labelled."),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_artifact", type=str,
                        help="retained raw artifact from run_stage8_alpha.py")
    parser.add_argument("--out", type=str, default=None,
                        help="path for the reduced artifact (default: "
                             "<stem>-reduced.json beside the input)")
    args = parser.parse_args(argv)

    with open(args.raw_artifact, encoding="utf-8") as handle:
        raw = json.load(handle)
    try:
        replicates = _validate(raw)
    except ReducerValidationError as error:
        print(f"REDUCER_VALIDATION_FAILED: {error}", file=sys.stderr)
        return 1
    outcome_block = apply_rule(replicates)
    reduced = {
        "protocol": PROTOCOL,
        "source_artifact": args.raw_artifact,
        "decision_rule": (
            "docs/stage-8-alpha-evolution-preregistration.md section 5, "
            "applied exactly once by this source-frozen reducer"),
        "outcome_block": outcome_block,
    }
    payload = json.dumps(reduced, indent=2, sort_keys=True)
    out_path = args.out
    if out_path is None:
        stem = args.raw_artifact[:-5] if args.raw_artifact.endswith(".json") \
            else args.raw_artifact
        out_path = f"{stem}-reduced.json"
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(payload + "\n")
    print(json.dumps({
        "outcome": outcome_block["outcome"],
        "eligible_k_eff": outcome_block["counts"]["eligible_k_eff"],
        "movers_up": outcome_block["counts"]["movers_up"],
        "movers_down": outcome_block["counts"]["movers_down"],
        "non_movers": outcome_block["counts"]["non_movers"],
        "extinct": len(outcome_block["counts"]["extinct_replicates"]),
        "wrote": out_path,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
