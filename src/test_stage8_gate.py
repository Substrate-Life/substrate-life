"""Registered Stage 8 gate-evaluation test matrix.

Synthetic shakedown records exercising ``stage8_gate.evaluate_gate`` and
``build_replay_evidence``'s identity logic: G1 two-thirds counting, G2
integrity refusals, G3 kernel-audit and replay requirements, and the
combined ``gate_passed`` verdict.
"""

from __future__ import annotations

import unittest

from stage8_gate import _gate_threshold, build_replay_evidence, evaluate_gate
from stage8_population import shakedown_seeds


def _complete(seed: int, *, decisions: int = 50, distinct_a: int = 5,
              kernel_ok: bool = True, checkpoints: int | None = None,
              alpha_end: str = "153/255",
              direction_class: str = "non_mover") -> dict:
    return {
        "seed_table": "shakedown",
        "replicate_index": shakedown_seeds().index(seed),
        "hazard_seed": seed,
        "classification": "COMPLETE",
        "ticks_completed": 2400,
        "window_ticks": 2400,
        # Gate-repair registration section 3: the byte-frozen stack
        # appends two `initial` entries (one per constructor layer) plus
        # one `tick_complete:<t>` entry per completed tick.
        "tick_checkpoints": checkpoints if checkpoints is not None else 2402,
        "closure_history_head": ["initial", "initial", "tick_complete:0"],
        "closure_history_tail": "tick_complete:2399",
        "mutation_telemetry": {
            "decision_records": decisions,
            "draws_total": decisions * 2 - 10,
            "problems": [] if kernel_ok else ["broken chain"],
            "passes": kernel_ok,
        },
        "genome_freeze_audit": {"passes": True if kernel_ok else False,
                                "violations": [], "records_checked": 100},
        "terminal_census": {"tick": 2400, "n_live": 30,
                            "distinct_A_values": distinct_a},
        "kernel_draw_chain": [
            {"stream_position": 0, "mutated": True, "delta": +1,
             "draws_consumed": 2}],
        "alpha_end": alpha_end,
        "direction_class": direction_class,
        "admitted_births_total": 900,
        "event_digest": f"digest-{seed}",
    }


def _invalid(seed: int, reason: str) -> dict:
    return {
        "seed_table": "shakedown",
        "replicate_index": shakedown_seeds().index(seed),
        "hazard_seed": seed,
        "classification": "INVALID_IMPLEMENTATION",
        "reason": reason,
    }


_REPLAY_OK = {
    "reexecuted_seed": shakedown_seeds()[0],
    "passes": True,
    "reexecution_identical": True,
    "mismatches": [],
}


class ThresholdTests(unittest.TestCase):

    def test_two_thirds_ceiling(self):
        self.assertEqual(_gate_threshold(12), 8)
        self.assertEqual(_gate_threshold(24), 16)
        self.assertEqual(_gate_threshold(6), 4)


class GateEvaluationTests(unittest.TestCase):

    def _records(self) -> list[dict]:
        return [_complete(seed) for seed in shakedown_seeds()]

    def test_all_conditions_pass(self):
        summary = evaluate_gate(self._records(), dict(_REPLAY_OK))
        self.assertTrue(summary["G1_evolution_operates"]["passes_G1"])
        self.assertTrue(summary["G2_implementation_integrity"]["passes_G2"])
        self.assertTrue(summary["G3_kernel_audit"]["passes_G3"])
        self.assertTrue(summary["gate_passed"])

    def test_g1_requires_two_thirds(self):
        records = self._records()
        # Three replicates lose G1 (no distinct-A spread at W): 9 >= 8.
        for record in records[:3]:
            record["terminal_census"]["distinct_A_values"] = 1
        summary = evaluate_gate(records, dict(_REPLAY_OK))
        g1 = summary["G1_evolution_operates"]
        self.assertEqual(len(g1["passing_replicates"]), 9)
        self.assertTrue(g1["passes_G1"])
        # Two more lose it: 7 < 8.
        for record in records[3:5]:
            record["terminal_census"]["distinct_A_values"] = 1
        summary = evaluate_gate(records, dict(_REPLAY_OK))
        self.assertEqual(
            len(summary["G1_evolution_operates"]["passing_replicates"]), 7)
        self.assertFalse(summary["G1_evolution_operates"]["passes_G1"])
        self.assertFalse(summary["gate_passed"])

    def test_g1_counts_zero_mutation_records_as_failure(self):
        records = self._records()
        records[0]["mutation_telemetry"]["decision_records"] = 0
        summary = evaluate_gate(records, dict(_REPLAY_OK))
        self.assertEqual(
            len(summary["G1_evolution_operates"]["passing_replicates"]), 11)

    def test_g2_refuses_overflow_and_invalid_and_checkpoints(self):
        records = self._records()
        records[1] = _invalid(records[1]["hazard_seed"], "BUFFER_OVERFLOW")
        summary = evaluate_gate(records, dict(_REPLAY_OK))
        self.assertFalse(summary["G2_implementation_integrity"]["passes_G2"])
        self.assertEqual(
            summary["G2_implementation_integrity"]["buffer_overflow_seeds"],
            [records[1]["hazard_seed"]])
        records = self._records()
        records[2] = _invalid(records[2]["hazard_seed"],
                              "UNEXPECTED_EXCEPTION")
        summary = evaluate_gate(records, dict(_REPLAY_OK))
        self.assertFalse(summary["G2_implementation_integrity"]["passes_G2"])
        records = self._records()
        # Gate-repair semantics: 2401 checkpoints = missing one closure
        # entry vs the frozen stack's W+2 deterministic count.
        records[3]["tick_checkpoints"] = 2401
        summary = evaluate_gate(records, dict(_REPLAY_OK))
        self.assertFalse(summary["G2_implementation_integrity"]["passes_G2"])
        self.assertEqual(
            summary["G2_implementation_integrity"]["checkpoint_failures"],
            [records[3]["hazard_seed"]])

    def test_g3_refuses_kernel_failure(self):
        records = self._records()
        records[4]["mutation_telemetry"]["passes"] = False
        summary = evaluate_gate(records, dict(_REPLAY_OK))
        g3 = summary["G3_kernel_audit"]
        self.assertEqual(len(g3["kernel_audit_failures"]), 1)
        self.assertFalse(g3["passes_G3"])
        self.assertFalse(summary["gate_passed"])

    def test_g3_requires_replay_evidence(self):
        summary = evaluate_gate(self._records(), None)
        self.assertFalse(summary["G3_kernel_audit"]["passes_G3"])
        replay = dict(_REPLAY_OK, reexecution_identical=False)
        summary = evaluate_gate(self._records(), replay)
        self.assertFalse(summary["G3_kernel_audit"]["passes_G3"])
        replay = dict(_REPLAY_OK, passes=False)
        summary = evaluate_gate(self._records(), replay)
        self.assertFalse(summary["G3_kernel_audit"]["passes_G3"])

    def test_no_complete_records_fails_closed(self):
        records = [_invalid(seed, "UNEXPECTED_EXCEPTION")
                   for seed in shakedown_seeds()]
        summary = evaluate_gate(records, None)
        self.assertFalse(summary["gate_passed"])
        self.assertFalse(summary["G1_evolution_operates"]["passes_G1"])


class ReplayEvidenceTests(unittest.TestCase):

    def test_identity_mismatch_reported(self):
        """build_replay_evidence compares digests against the original."""
        import stage8_gate as gate
        seed = shakedown_seeds()[0]
        original = _complete(seed)
        fresh = _complete(seed)
        fresh["event_digest"] = "different"
        original_execute = gate.execute_replicate

        def fake(table, index):
            return fresh

        try:
            gate.execute_replicate = fake
            evidence = build_replay_evidence(seed, original)
        finally:
            gate.execute_replicate = original_execute
        self.assertFalse(evidence["reexecution_identical"])
        self.assertFalse(evidence["passes"])

        fresh.update(original)  # identical aggregates and chain now

        try:
            gate.execute_replicate = fake
            evidence = build_replay_evidence(seed, original)
        finally:
            gate.execute_replicate = original_execute
        # The identity half must be satisfied; the stream-replay half
        # passes only if the genuine derivation agrees with the fixture's
        # scripted chain, so assert exactly the identity component here.
        self.assertTrue(evidence["reexecution_identical"])


if __name__ == "__main__":
    unittest.main()
