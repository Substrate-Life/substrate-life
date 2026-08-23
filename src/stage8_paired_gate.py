"""Stage 8 paired-arm feasibility gate (repair registration section 7).

Runs the BINDING pre-freeze gate: exploratory, NON-RETAINED shakedowns at
the exact registered ecology on the fixed 12-PAIR shakedown table
``20421301 + j`` (both arms per pair).  Produces no retained artifact:
everything prints to stdout as a factual summary whose per-condition pass
counts must be recorded in the freeze commit's notes (section 8(3);
df7b1f5 precedent).

Gate conditions (all mandatory):

- **G1 (evolution operates, Arm M only):** >= 2/3 of pairs COMPLETE with
  >= 1 recorded mutation event, >= 2 distinct ``A`` values among live
  members at tick W in Arm M, and zero non-frozen ``T``/``D`` anywhere in
  EITHER arm's event stream.
- **G2 (implementation integrity):** zero ``BUFFER_OVERFLOW`` /
  ``INVALID_IMPLEMENTATION`` in any arm; every ledger closes at every
  checkpoint in every arm.
- **G3 (kernel audit, Arm M):** every admitted birth carries exactly one
  Stage-M record; bounds and bit-exact stream replay checks pass -- with
  one full Arm M replicate re-executed by this gate tooling and verified
  bit-identical to its shakedown twin.
- **G4 (reference-arm integrity):** every Arm R0 record shows zero
  ``mutation_decision`` events and an empty kernel draw chain (kernel-
  absence audit passing); both arms of every pair ran the identical
  ``hazard_seed``; the pair table is complete.

If any condition fails: no freeze; a further superseding preregistration
with diagnosis, archived under ``failed-designs/``, never deleted.  This
script never applies the section 5 decision rule.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import sys
from typing import Any

from run_stage8_paired import execute_pair
from stage8_alpha_measure import replay_stream
from stage8_paired import registered_configuration, shakedown_pair_seeds


def _gate_threshold(count: int) -> int:
    """Two-thirds floor for a table size (integer counts)."""
    return -(-2 * count // 3)


def evaluate_gate(pairs: list[dict[str, Any]],
                  replay_evidence: dict[str, Any] | None) -> dict[str, Any]:
    """Apply conditions G1-G4 to the pair records."""
    n = len(pairs)
    threshold = _gate_threshold(n)

    both_complete = [p for p in pairs
                     if all(p["arms"][arm]["classification"] == "COMPLETE"
                            for arm in ("M", "R0"))]
    invalid = [
        {"pair_index": p["pair_index"], "hazard_seed": p["hazard_seed"],
         "arm": arm,
         "classification": p["arms"][arm].get("classification"),
         "reason": p["arms"][arm].get("reason")}
        for p in pairs for arm in ("M", "R0")
        if p["arms"][arm].get("classification") != "COMPLETE"]

    # G1: evolution operates in the mutation arm; genome freeze holds
    # everywhere.
    g1_passes = [
        p for p in both_complete
        if p["arms"]["M"]["mutation_telemetry"]["decision_records"] >= 1
        and p["arms"]["M"]["terminal_census"]["distinct_A_values"] >= 2]
    genome_violations = [
        {"pair_index": p["pair_index"], "arm": arm,
         "violations": p["arms"][arm]["genome_freeze_audit"]["violations"]}
        for p in pairs for arm in ("M", "R0")
        if not p["arms"][arm]["genome_freeze_audit"].get("passes")]
    g1_pass = len(g1_passes) >= threshold and not genome_violations \
        if both_complete else False

    # G2: implementation integrity across every arm.
    overflow = [(p["pair_index"], arm) for p in pairs
                for arm in ("M", "R0")
                if p["arms"][arm].get("reason") == "BUFFER_OVERFLOW"]
    # Gate-repair registration section 3: closure-history semantics pinned
    # to the byte-frozen stack's deterministic behaviour -- two constructor
    # layer `initial` entries plus one `tick_complete:<t>` entry per tick.
    def _checkpoint_failure(record: dict[str, Any]) -> bool:
        window = record.get("window_ticks", -2)
        if record.get("tick_checkpoints") != window + 2:
            return True
        if record.get("closure_history_head") != [
                "initial", "initial", "tick_complete:0"]:
            return True
        return record.get("closure_history_tail") != \
            f"tick_complete:{window - 1}"

    checkpoint_failures = [
        (p["pair_index"], arm) for p in both_complete
        for arm in ("M", "R0")
        if _checkpoint_failure(p["arms"][arm])]
    g2_pass = not invalid and not overflow and not checkpoint_failures

    # G3: kernel audit on the M arms + one bit-exact re-execution replay.
    kernel_failures = [
        {"pair_index": p["pair_index"],
         "problems": p["arms"]["M"]["mutation_telemetry"]["problems"]}
        for p in both_complete
        if not p["arms"]["M"]["mutation_telemetry"]["passes"]]
    replay_ok = replay_evidence is not None \
        and bool(replay_evidence.get("passes")) \
        and bool(replay_evidence.get("reexecution_identical"))
    g3_pass = not kernel_failures and replay_ok

    # G4: reference-arm integrity + pairing completeness.
    g4_failures = []
    for p in pairs:
        r0 = p["arms"]["R0"]
        if r0["classification"] == "COMPLETE":
            telemetry = r0.get("mutation_telemetry", {})
            if not telemetry.get("passes") \
                    or telemetry.get("decision_records") != 0 \
                    or r0.get("kernel_draw_chain") != []:
                g4_failures.append(
                    {"pair_index": p["pair_index"], "problem":
                     "R0 kernel-absence audit failed"})
    seed_mismatch = [p["pair_index"] for p in pairs
                     if p["arms"]["M"]["hazard_seed"]
                     != p["arms"]["R0"]["hazard_seed"]]
    g4_pass = not g4_failures and not seed_mismatch

    # Section 7 factual context (non-binding, threshold-free): aggregate
    # shakedown magnitudes reported so freeze notes carry the texture of
    # the exploratory runs without any rescaling freedom.
    complete_arms = [
        p["arms"][arm] for p in pairs for arm in ("M", "R0")
        if p["arms"][arm].get("classification") == "COMPLETE"]
    m_arms = [p["arms"]["M"] for p in pairs
              if p["arms"]["M"].get("classification") == "COMPLETE"]
    live = [a["terminal_census"]["n_live"] for a in complete_arms]
    distinct_a = [a["terminal_census"]["distinct_A_values"] for a in m_arms]
    factual_context = {
        "note": ("descriptive only; reported without thresholds per "
                 "section 7; may not resize anything"),
        "total_m_mutation_decision_records":
            sum(a["mutation_telemetry"]["decision_records"] for a in m_arms),
        "total_m_kernel_draws":
            sum(a["mutation_telemetry"]["draws_total"] for a in m_arms),
        "complete_arms_terminal_live_min":
            min(live) if live else None,
        "complete_arms_terminal_live_max":
            max(live) if live else None,
        "m_terminal_distinct_A_min": min(distinct_a) if distinct_a else None,
        "m_terminal_distinct_A_max": max(distinct_a) if distinct_a else None,
        "extinct_complete_arms":
            sum(1 for a in complete_arms
                if a.get("terminal_census", {}).get("n_live") == 0),
    }

    return {
        "gate": ("stage-8-alpha-evolution-repair-preregistration "
                 "section 7"),
        "pairs_used": [p["hazard_seed"] for p in pairs],
        "pair_count": n,
        "two_thirds_threshold": threshold,
        "pairs_both_arms_complete": len(both_complete),
        "invalid_runs": invalid,
        "G1_evolution_operates": {
            "passing_pairs": [p["pair_index"] for p in g1_passes],
            "threshold": threshold,
            "genome_freeze_violations": genome_violations,
            "passes_G1": g1_pass,
        },
        "G2_implementation_integrity": {
            "buffer_overflows": overflow,
            "checkpoint_failures": checkpoint_failures,
            "passes_G2": g2_pass,
        },
        "G3_kernel_audit": {
            "kernel_audit_failures": kernel_failures,
            "stream_replay": replay_evidence,
            "passes_G3": g3_pass,
        },
        "G4_reference_arm_integrity": {
            "failures": g4_failures,
            "seed_mismatches": seed_mismatch,
            "passes_G4": g4_pass,
        },
        "factual_shakedown_context": factual_context,
        "gate_passed": g1_pass and g2_pass and g3_pass and g4_pass,
        "registered_configuration_checked": registered_configuration(),
        "claim_scope": (
            "Feasibility facts only. No direction, selection, or "
            "evolutionary claim is made or retained; the confirmatory "
            "pair table remains untouched until the single retained run "
            "after the section 8 freeze is committed."),
    }


def build_replay_evidence(seed: int, original_m: dict[str, Any]) \
        -> dict[str, Any]:
    """Re-execute one full Arm M replicate; audit its stream bit-exactly.

    The fresh execution must reproduce the original record exactly (event
    digest, admitted births, draw chain) AND the documented stream
    derivation must replay its recorded chain bit-exactly.
    """
    from stage8_paired import shakedown_pair_seeds as _seeds
    from run_stage8_paired import _execute_arm

    index = _seeds().index(seed)
    fresh = _execute_arm("M", seed, "shakedown", index)
    if fresh.get("classification") != "COMPLETE":
        return {
            "reexecuted_seed": seed, "passes": False,
            "reexecution_identical": False,
            "note": "re-execution did not COMPLETE",
        }
    replay = replay_stream(seed, fresh["kernel_draw_chain"])
    identical = (
        fresh["event_digest"] == original_m["event_digest"]
        and fresh["admitted_births_total"]
        == original_m["admitted_births_total"]
        and fresh["mutation_telemetry"]["draws_total"]
        == original_m["mutation_telemetry"]["draws_total"]
        and fresh["kernel_draw_chain"] == original_m["kernel_draw_chain"])
    return {
        "reexecuted_seed": seed,
        "records_replayed": replay["records_replayed"],
        "draws_replayed": replay["draws_replayed"],
        "mismatches": replay["mismatches"],
        "reexecution_identical": identical,
        "identity_fields_compared": ["event_digest",
                                     "admitted_births_total",
                                     "draws_total", "kernel_draw_chain"],
        "passes": bool(replay["passes"]) and identical,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=2,
                        help="parallel pair processes (deterministic "
                             "regardless)")
    parser.add_argument("--limit", type=int, default=None,
                        help="run only the first J shakedown PAIRS "
                             "(implementation-window plumbing checks)")
    args = parser.parse_args(argv)

    all_seeds = shakedown_pair_seeds()
    seeds = all_seeds[:args.limit] if args.limit is not None else all_seeds
    print(f"[gate] {len(seeds)} shakedown pairs: {list(seeds)}",
          file=sys.stderr)
    index_of_seed = {seed: i for i, seed in enumerate(all_seeds)}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pairs = list(pool.map(execute_pair,
                              ["shakedown"] * len(seeds),
                              [index_of_seed[s] for s in seeds]))

    replay_evidence: dict[str, Any] | None = None
    usable = [p for p in pairs
              if p["arms"]["M"].get("classification") == "COMPLETE"]
    if usable:
        first = min(usable, key=lambda p: p["hazard_seed"])
        replay_evidence = build_replay_evidence(first["hazard_seed"],
                                                first["arms"]["M"])

    summary = evaluate_gate(pairs, replay_evidence)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
