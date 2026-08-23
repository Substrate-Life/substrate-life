"""Stage 8 pre-freeze feasibility gate (preregistration section 6).

Runs the BINDING pre-freeze gate: exploratory, NON-RETAINED shakedowns at
the exact registered ecology, kernel, and window on the fixed 12-seed
shakedown table ``20293311 + j`` (``j`` in ``0..11``, fixed in
``stage8_population.py`` before any execution and disjoint from every prior
population table and from the confirmatory table).  Produces no retained
artifact: everything is printed to stdout as a factual gate summary whose
per-condition pass counts must be recorded in the freeze commit's notes
(section 7(3); df7b1f5 precedent).  Shakedown summaries are reported
without thresholds as factual context; they may not resize anything.

Gate conditions (all mandatory):

- **G1 (evolution operates):** >= 2/3 of shakedown replicates COMPLETE with
  >= 1 recorded mutation event, >= 2 distinct ``A`` values among live
  members at tick W, and zero ``T``/``D`` values other than 128/255 anywhere
  in the event stream.
- **G2 (implementation integrity):** zero ``BUFFER_OVERFLOW`` /
  ``INVALID_IMPLEMENTATION``; every ledger closes at every checkpoint in
  every replicate (carried assertion machinery -- any assertion failure
  surfaces here as a failed replicate, which fails the gate).
- **G3 (kernel audit):** every admitted birth carries exactly one Stage-M
  record; every recorded child satisfies ``0 <= A <= 255``, ``T = 128``,
  ``D = 255``; replaying the documented stream derivation reproduces the
  recorded draw sequence bit-exactly on one full replicate re-executed by
  this gate tooling -- and that re-execution is bit-identical to the same
  seed's original shakedown record.

If any condition fails: no freeze; a further superseding preregistration
with diagnosis, archived under ``failed-designs/``, never deleted.  This
script never applies the section 5 decision rule and makes no fitness,
selection, or evolutionary claim.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import sys
from typing import Any

from run_stage8_alpha import (
    execute_replicate,
    execute_replicate_guarded,
)
from stage8_alpha_measure import replay_stream
from stage8_population import registered_configuration, shakedown_seeds


def _gate_threshold(count: int) -> int:
    """Two-thirds floor for a shakedown-table size (integer counts)."""
    return -(-2 * count // 3)


def evaluate_gate(records: list[dict[str, Any]],
                  replay_evidence: dict[str, Any] | None) -> dict[str, Any]:
    """Apply conditions G1-G3 to the shakedown records.

    ``replay_evidence`` is None when no COMPLETE record exists for a
    re-execution (which itself fails G3).
    """
    complete = [r for r in records if r.get("classification") == "COMPLETE"]
    invalid = [r for r in records if r.get("classification") != "COMPLETE"]
    n = len(records)
    threshold = _gate_threshold(n)

    g1_passes = [
        r for r in complete
        if r["mutation_telemetry"]["decision_records"] >= 1
        and r["terminal_census"]["distinct_A_values"] >= 2
        and r["genome_freeze_audit"]["passes"]]
    g1_pass = len(g1_passes) >= threshold if complete else False

    overflow = [r["hazard_seed"] for r in records
                if r.get("reason") == "BUFFER_OVERFLOW"]
    invalid_seeds = [r["hazard_seed"] for r in invalid]
    # Gate-repair registration section 3: closure-history semantics pinned
    # to the byte-frozen stack's deterministic behaviour -- two constructor
    # layer `initial` entries plus one `tick_complete:<t>` entry per tick,
    # with registered head/tail pins.  A COMPLETE replicate must carry all
    # of them; anything else means a ledger verification path was skipped.
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
        r["hazard_seed"] for r in complete if _checkpoint_failure(r)]
    g2_pass = not overflow and not invalid_seeds and not checkpoint_failures

    kernel_failures = [
        {"hazard_seed": r["hazard_seed"],
         "mutation_problems": r["mutation_telemetry"]["problems"],
         "genome_violations": r["genome_freeze_audit"]["violations"]}
        for r in complete
        if not (r["mutation_telemetry"]["passes"]
                and r["genome_freeze_audit"]["passes"])]
    replay_ok = replay_evidence is not None \
        and bool(replay_evidence.get("passes")) \
        and bool(replay_evidence.get("reexecution_identical"))
    g3_pass = not kernel_failures and replay_ok

    return {
        "gate": "stage-8-alpha-evolution-preregistration section 6",
        "seeds_used": sorted(r["hazard_seed"] for r in records),
        "seed_count": n,
        "two_thirds_threshold": threshold,
        "complete_replicates": len(complete),
        "replicate_summaries": [
            {
                "hazard_seed": r["hazard_seed"],
                "classification": r.get("classification"),
                "admitted_births": r.get("admitted_births_total"),
                "mutation_decisions": r.get(
                    "mutation_telemetry", {}).get("decision_records"),
                "kernel_draws": r.get("mutation_telemetry", {}).get(
                    "draws_total"),
                "terminal_n_live": r.get(
                    "terminal_census", {}).get("n_live"),
                "terminal_distinct_A": r.get(
                    "terminal_census", {}).get("distinct_A_values"),
                "alpha_end": r.get("alpha_end"),
                "direction_class": r.get("direction_class"),
            }
            for r in sorted(records, key=lambda r: r["hazard_seed"])],
        "invalid_replicates": [
            {"hazard_seed": r["hazard_seed"],
             "classification": r.get("classification"),
             "reason": r.get("reason")}
            for r in invalid],
        "G1_evolution_operates": {
            "passing_replicates": [r["hazard_seed"] for r in g1_passes],
            "of_complete": len(complete),
            "threshold": threshold,
            "passes_G1": g1_pass,
        },
        "G2_implementation_integrity": {
            "buffer_overflow_seeds": overflow,
            "invalid_implementations": invalid_seeds,
            "checkpoint_failures": checkpoint_failures,
            "passes_G2": g2_pass,
        },
        "G3_kernel_audit": {
            "kernel_audit_failures": kernel_failures,
            "stream_replay": replay_evidence,
            "passes_G3": g3_pass,
        },
        "gate_passed": g1_pass and g2_pass and g3_pass,
        "registered_configuration_checked": registered_configuration(),
        "claim_scope": (
            "Feasibility facts only. No fitness, selection, direction, or "
            "evolutionary claim is made or retained; the confirmatory seed "
            "table remains untouched until the single retained run after "
            "the section 7 freeze is committed."),
    }


def build_replay_evidence(seed: int, original: dict[str, Any]) \
        -> dict[str, Any]:
    """Re-execute one full replicate and audit its stream bit-exactly (G3).

    The gate tooling re-executes the whole replicate in-process, then:

    1. replays the documented derivation
       ``random.Random(hazard_seed * 1000003 + 7)`` against the fresh run's
       recorded draw chain -- every Bernoulli/step/position must match
       bit-exactly;
    2. verifies the re-execution is bit-identical to the parallel-path
       shakedown record of the same seed (event digest, admitted births,
       full ordered draw chain).
    """
    fresh = execute_replicate("shakedown",
                              shakedown_seeds().index(seed))
    if fresh.get("classification") != "COMPLETE":
        return {
            "reexecuted_seed": seed,
            "passes": False,
            "reexecution_identical": False,
            "note": "re-execution did not COMPLETE",
            "reason": fresh.get("reason"),
        }
    chain = fresh["kernel_draw_chain"]
    # replay_stream expects decision-shaped records; the chain entries carry
    # exactly the fields it reads.
    replay = replay_stream(seed, chain)
    identical = (
        fresh["event_digest"] == original["event_digest"]
        and fresh["admitted_births_total"]
        == original["admitted_births_total"]
        and fresh["mutation_telemetry"]["draws_total"]
        == original["mutation_telemetry"]["draws_total"]
        and fresh["kernel_draw_chain"] == original["kernel_draw_chain"])
    return {
        "reexecuted_seed": seed,
        "seed_derivation": replay["seed_derivation"],
        "records_replayed": replay["records_replayed"],
        "draws_replayed": replay["draws_replayed"],
        "mismatches": replay["mismatches"],
        "reexecution_identical": identical,
        "identity_fields_compared": ["event_digest", "admitted_births_total",
                                     "draws_total", "kernel_draw_chain"],
        "passes": bool(replay["passes"]) and identical,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=2,
                        help="parallel replicates (deterministic regardless)")
    parser.add_argument("--limit", type=int, default=None,
                        help="run only the first J shakedown seeds "
                             "(implementation-window plumbing checks)")
    args = parser.parse_args(argv)

    all_seeds = shakedown_seeds()
    seeds = all_seeds[:args.limit] if args.limit is not None else all_seeds
    print(f"[gate] {len(seeds)} shakedown seeds: {list(seeds)}",
          file=sys.stderr)
    index_of_seed = {seed: index for index, seed in enumerate(all_seeds)}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(execute_replicate_guarded,
                                [("shakedown", index_of_seed[seed])
                                 for seed in seeds]))

    replay_evidence: dict[str, Any] | None = None
    complete_records = [r for r in records
                        if r.get("classification") == "COMPLETE"]
    if complete_records:
        first = min(complete_records, key=lambda r: r["hazard_seed"])
        replay_evidence = build_replay_evidence(first["hazard_seed"], first)

    summary = evaluate_gate(records, replay_evidence)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
