"""Stage 8 paired-arm reducer: the source-frozen section 5 decision rule.

Applies the registered paired rule of
``docs/stage-8-alpha-evolution-repair-preregistration.md`` section 5
EXACTLY ONCE to one retained raw artifact produced by
``run_stage8_paired.py``.

For each pair ``i`` the endpoint is the exact paired difference

    ``D_i = ᾱ_end(M, s_i) − ᾱ_end(R0, s_i)``,

with each ``ᾱ_end`` the equal-weight mean of ``A/255`` over live members at
the tick-W census close.  Let ``k_eff`` = number of eligible pairs (both
arms COMPLETE, each with >= 1 live member at W):

1. ``DEGENERATE_EVOLUTION``          -- ``k_eff < 16``
2. ``ESTABLISHED_TOWARD_HIGH_ALPHA`` -- ``k_eff >= 16`` and
   ``#{D_i >= +Δ_pair_floor} >= 18``
3. ``ESTABLISHED_TOWARD_LOW_ALPHA``  -- ``k_eff >= 16`` and
   ``#{D_i <= −Δ_pair_floor} >= 18``
4. ``NO_ESTABLISHED_DIRECTION``      -- otherwise (including splits)

with ``Δ_pair_floor = 4/255``.  Exactly one class is emitted; thresholds,
floor, tables, and arm definitions are frozen by the registration and may
never be retuned after any execution (section 10).

Before applying the rule the reducer independently validates the artifact:
protocol and table, exact pair/seed set, one M + one R0 record per pair,
kernel evidence present and passing on BOTH arms (Arm M reconciliation;
Arm R0 kernel-absence audit), per-record terminal-snapshot consistency
(``ᾱ_end`` recomputed from the terminal histogram), and recorded direction
classes matching the endpoint values.  Any failure aborts without a class.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from typing import Any

from stage7b2_measure import fmt_rat, parse_rat
from stage8_alpha_measure import CHECKPOINT_TICKS, direction_class
from stage8_population import (
    ALPHA_REF,
    REGISTERED_WINDOW_TICKS_STAGE8,
)
from stage8_paired import (
    CONFIRMATORY_PAIR_SEED_BASE,
    DIRECTION_FLOOR_PAIRED,
    PAIR_REPLICATES,
    PROTOCOL,
    confirmatory_pair_seed,
)

RULE_CONSTANTS = {
    "direction_floor_paired": fmt_rat(DIRECTION_FLOOR_PAIRED),
    "alpha_ref_per_arm": fmt_rat(ALPHA_REF),
    "minimum_eligible_k_eff": 16,
    "concordance_threshold": 18,
    "pairs_k": PAIR_REPLICATES,
    "window_ticks_W": REGISTERED_WINDOW_TICKS_STAGE8,
}


class ReducerValidationError(RuntimeError):
    """The raw artifact failed pre-rule validation; no class is emitted."""


def _validate(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Structural + arithmetic validation; returns validated pairs."""
    if raw.get("protocol") != PROTOCOL:
        raise ReducerValidationError(
            f"protocol mismatch: {raw.get('protocol')!r}")
    if raw.get("seed_table") != "confirmatory":
        raise ReducerValidationError(
            "the section 5 paired rule applies to the confirmatory table "
            f"only; got {raw.get('seed_table')!r}")
    if raw.get("decision") != "PENDING_REDUCTION":
        raise ReducerValidationError(
            f"artifact decision field is {raw.get('decision')!r}, "
            "not PENDING_REDUCTION (double reduction refused)")
    pairs = raw.get("pairs")
    if not isinstance(pairs, list) or len(pairs) != PAIR_REPLICATES:
        raise ReducerValidationError(
            f"expected exactly {PAIR_REPLICATES} pair records")
    expected_seeds = [confirmatory_pair_seed(i)
                      for i in range(PAIR_REPLICATES)]
    seeds = [pair.get("hazard_seed") for pair in pairs]
    if seeds != expected_seeds:
        raise ReducerValidationError(
            f"seed table mismatch: {seeds} != {expected_seeds}")

    window = REGISTERED_WINDOW_TICKS_STAGE8
    for pair in pairs:
        index = pair["pair_index"]
        arms = pair.get("arms")
        if not isinstance(arms, dict) or set(arms) != {"M", "R0"}:
            raise ReducerValidationError(
                f"pair {index}: must carry exactly one M and one R0 arm")
        for name in ("M", "R0"):
            _validate_arm(index, name, arms[name], window)
        # Recorded per-arm direction classes must match endpoint values.
        for name in ("M", "R0"):
            record = arms[name]
            if record["classification"] == "COMPLETE" \
                    and record["terminal_census"]["n_live"] >= 1 \
                    and record.get("direction_class") != \
                    direction_class(record["alpha_end"]):
                raise ReducerValidationError(
                    f"pair {index} arm {name}: direction class mismatch")
    return pairs


def _validate_arm(pair_index: int, name: str, record: dict[str, Any],
                  window: int) -> None:
    if record.get("arm") != name:
        raise ReducerValidationError(
            f"pair {pair_index}: arm label {record.get('arm')!r} != {name!r}")
    if record["classification"] != "COMPLETE":
        return
    if record.get("terminal_census", {}).get("tick") != window:
        raise ReducerValidationError(
            f"pair {pair_index} arm {name}: missing tick-{window} snapshot")
    checkpoints = record.get("trajectory_checkpoints", [])
    if [int(c["tick"]) for c in checkpoints] != list(CHECKPOINT_TICKS):
        raise ReducerValidationError(
            f"pair {pair_index} arm {name}: checkpoint ticks incomplete")
    if checkpoints[-1]["n_live"] != record["terminal_census"]["n_live"]:
        raise ReducerValidationError(
            f"pair {pair_index} arm {name}: final checkpoint disagrees "
            "with terminal census")
    histogram = {int(a): int(count) for a, count
                 in record["terminal_census"]["histogram_A"].items()}
    n_live = record["terminal_census"]["n_live"]
    if sum(histogram.values()) != n_live:
        raise ReducerValidationError(
            f"pair {pair_index} arm {name}: histogram mass != live census")
    alpha_recomputed = Fraction(
        sum(a * count for a, count in histogram.items()), 255 * n_live) \
        if n_live else None
    if n_live and alpha_recomputed != parse_rat(record["alpha_end"]):
        raise ReducerValidationError(
            f"pair {pair_index} arm {name}: alpha_end != histogram "
            "recomputation")
    if record.get("extinct") != (n_live == 0):
        raise ReducerValidationError(
            f"pair {pair_index} arm {name}: extinction flag inconsistent")
    audit = record.get("mutation_telemetry")
    if not isinstance(audit, dict) or audit.get("passes") is not True:
        raise ReducerValidationError(
            f"pair {pair_index} arm {name}: kernel evidence absent/failing")


def paired_difference(record_m: dict[str, Any],
                      record_r0: dict[str, Any]) -> Fraction | None:
    """Exact ``D_i`` when both endpoints exist; None otherwise."""
    if record_m.get("alpha_end") is None or \
            record_r0.get("alpha_end") is None:
        return None
    return parse_rat(record_m["alpha_end"]) - parse_rat(record_r0["alpha_end"])


def apply_rule(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply the registered section 5 paired rule; emit exactly one class."""
    window = REGISTERED_WINDOW_TICKS_STAGE8
    eligible_indices: set[int] = set()
    differences: dict[int, Fraction] = {}
    extinctions: list[dict[str, Any]] = []
    leakage: list[dict[str, Any]] = []
    for index, pair in enumerate(pairs):
        m_record, r0_record = pair["arms"]["M"], pair["arms"]["R0"]

        def _live(record: dict[str, Any]) -> int | None:
            if record["classification"] != "COMPLETE":
                return None
            census = record.get("terminal_census", {})
            return census.get("n_live") if census.get("tick") == window \
                else None

        m_live, r0_live = _live(m_record), _live(r0_record)
        if m_live == 0 or r0_live == 0:
            extinctions.append({
                "pair_index": index,
                "hazard_seed": pair["hazard_seed"],
                "extinct_arms": [name for name, live in
                                 (("M", m_live), ("R0", r0_live))
                                 if live == 0]})
        difference = paired_difference(m_record, r0_record) \
            if (m_live is not None and m_live >= 1
                and r0_live is not None and r0_live >= 1) else None
        if difference is not None:
            eligible_indices.add(index)
            differences[index] = difference

        # Leakage monitor (descriptive): do the two arms disagree on which
        # founder ancestry holds the terminal plurality?
        try:
            m_ancestries = m_record["terminal_census"]["live_by_ancestry"]
            r0_ancestries = r0_record["terminal_census"]["live_by_ancestry"]
            if m_ancestries and r0_ancestries:
                m_top = max(m_ancestries, key=m_ancestries.get)
                r0_top = max(r0_ancestries, key=r0_ancestries.get)
                if m_top != r0_top:
                    leakage.append({
                        "pair_index": index,
                        "hazard_seed": pair["hazard_seed"],
                        "M_plurality": m_top, "R0_plurality": r0_top})
        except (KeyError, TypeError):
            pass

    k_eff = len(eligible_indices)
    ups = [i for i in sorted(eligible_indices)
           if differences[i] >= DIRECTION_FLOOR_PAIRED]
    downs = [i for i in sorted(eligible_indices)
             if differences[i] <= -DIRECTION_FLOOR_PAIRED]
    non = [i for i in sorted(eligible_indices)
           if abs(differences[i]) < DIRECTION_FLOOR_PAIRED]

    if k_eff < RULE_CONSTANTS["minimum_eligible_k_eff"]:
        outcome = "DEGENERATE_EVOLUTION"
    elif len(ups) >= RULE_CONSTANTS["concordance_threshold"]:
        outcome = "ESTABLISHED_TOWARD_HIGH_ALPHA"
    elif len(downs) >= RULE_CONSTANTS["concordance_threshold"]:
        outcome = "ESTABLISHED_TOWARD_LOW_ALPHA"
    else:
        outcome = "NO_ESTABLISHED_DIRECTION"

    def _median(values: list[Fraction]) -> str | None:
        if not values:
            return None
        ordered = sorted(values)
        mid = len(ordered) // 2
        median = ordered[mid] if len(ordered) % 2 \
            else (ordered[mid - 1] + ordered[mid]) / 2
        return fmt_rat(median)

    return {
        "outcome": outcome,
        "rule_constants": dict(RULE_CONSTANTS),
        "applied_exactly_once": True,
        "counts": {
            "pairs": len(pairs),
            "eligible_k_eff": k_eff,
            "movers_up_pairs": len(ups),
            "movers_down_pairs": len(downs),
            "non_mover_pairs": len(non),
            "ineligible_pairs": [
                {"pair_index": i, "hazard_seed": pairs[i]["hazard_seed"],
                 "reason": _ineligible_reason(pairs[i]["arms"])}
                for i in range(len(pairs)) if i not in eligible_indices],
            "extinct_pairs": extinctions,
            "leakage_pairs": leakage,
        },
        "descriptive": {
            "paired_differences": {
                str(pairs[i]["hazard_seed"]): (
                    fmt_rat(differences[i]) if i in differences else None)
                for i in range(len(pairs))},
            "median_D_among_movers_up": _median(
                [differences[i] for i in ups]),
            "median_D_among_movers_down": _median(
                [differences[i] for i in downs]),
            "median_abs_D_all_eligible": _median(
                [abs(differences[i]) for i in sorted(eligible_indices)]),
            "alpha_end_by_arm_and_seed": {
                str(pair["hazard_seed"]): {
                    arm: (pair["arms"][arm].get("alpha_end")
                          if pair["arms"][arm]["classification"] == "COMPLETE"
                          else None)
                    for arm in ("M", "R0")}
                for pair in pairs},
            "trajectories_by_arm_and_seed": {
                str(pair["hazard_seed"]): {
                    arm: pair["arms"][arm].get("trajectory_checkpoints")
                    for arm in ("M", "R0")}
                for pair in pairs},
            "recruitment_telemetry_by_arm_and_seed": {
                str(pair["hazard_seed"]): {
                    arm: pair["arms"][arm].get("mediators")
                    for arm in ("M", "R0")}
                for pair in pairs},
            "births_by_ancestry_by_arm_and_seed": {
                str(pair["hazard_seed"]): {
                    arm: pair["arms"][arm].get("births_by_ancestry")
                    for arm in ("M", "R0")}
                for pair in pairs},
        },
        "scope": (
            "Level-2 statement space only, relative to the mutation-off "
            "reference at the same seeds: 'the restricted architecture "
            "does / does not redistribute allocation through the channel, "
            "in the registered direction(s), beyond Δ_pair_floor = 4/255, "
            "at this ecology, kernel, and window'.  A null licenses "
            "exactly that bounded-negative statement; no external "
            "validation, optimum, ESS, causal-gradient, open-genome, or "
            "other-ecology claim is licensed."),
    }


def _ineligible_reason(arms: dict[str, dict[str, Any]]) -> str:
    reasons = []
    for name in ("M", "R0"):
        record = arms[name]
        if record["classification"] != "COMPLETE":
            reasons.append(f"{name}:{record['classification']}")
        elif record.get("terminal_census", {}).get("n_live") == 0:
            reasons.append(f"{name}:extinct_at_W")
    return ";".join(reasons) if reasons else "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_artifact", type=str,
                        help="retained raw artifact from run_stage8_paired.py")
    parser.add_argument("--out", type=str, default=None,
                        help="path for the reduced artifact (default: "
                             "<stem>-reduced.json beside the input)")
    args = parser.parse_args(argv)

    with open(args.raw_artifact, encoding="utf-8") as handle:
        raw = json.load(handle)
    try:
        pairs = _validate(raw)
    except ReducerValidationError as error:
        print(f"REDUCER_VALIDATION_FAILED: {error}", file=sys.stderr)
        return 1
    outcome_block = apply_rule(pairs)
    reduced = {
        "protocol": PROTOCOL,
        "source_artifact": args.raw_artifact,
        "decision_rule": (
            "docs/stage-8-alpha-evolution-repair-preregistration.md "
            "section 5, applied exactly once by this source-frozen reducer"),
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
        "movers_up_pairs": outcome_block["counts"]["movers_up_pairs"],
        "movers_down_pairs": outcome_block["counts"]["movers_down_pairs"],
        "non_mover_pairs": outcome_block["counts"]["non_mover_pairs"],
        "leakage_pairs": len(outcome_block["counts"]["leakage_pairs"]),
        "wrote": out_path,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
