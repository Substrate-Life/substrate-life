"""Registered Stage 8 paired-reducer and paired-gate test matrix.

Synthetic raw-artifact fixtures exercising every branch of the source-
frozen section 5 paired rule (``reduce_stage8_paired``) and the paired
gate evaluation (``stage8_paired_gate.evaluate_gate``): all four outcome
classes, exact-threshold boundaries, extinction/ineligibility handling,
leakage monitoring, validation refusals, and G4 reference-arm failures.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable

import unittest

from reduce_stage8_paired import (
    ReducerValidationError,
    _validate,
    apply_rule,
    paired_difference,
)
from stage8_alpha_measure import CHECKPOINT_TICKS
from stage8_paired import (
    CONFIRMATORY_PAIR_SEED_BASE,
    DIRECTION_FLOOR_PAIRED as FLOOR,
    PAIR_REPLICATES,
    PROTOCOL,
    confirmatory_pair_seed,
)
from stage8_paired_gate import evaluate_gate


def _histogram_for(mean_alpha: Fraction, n_live: int = 20) -> dict[str, int]:
    mean_a = Fraction(mean_alpha) * 255
    total = int(mean_a) * n_live
    base, extra = divmod(total, n_live)
    histogram = {base: n_live - extra}
    if extra:
        histogram[base + 1] = extra
    return {str(a): c for a, c in sorted(histogram.items())}


def _arm_record(arm: str, index: int, alpha: Fraction | None,
                n_live: int = 20, *,
                kernel_ok: bool = True) -> dict:
    seed = confirmatory_pair_seed(index)
    census_n = 0 if alpha is None else n_live
    record: dict = {
        "arm": arm,
        "seed_table": "confirmatory",
        "replicate_index": index,
        "hazard_seed": seed,
        "classification": "COMPLETE",
        "ticks_completed": 2400,
        "window_ticks": 2400,
        "tick_checkpoints": 2401,
        "trajectory_checkpoints": [
            {"tick": tick, "n_live": census_n} for tick in CHECKPOINT_TICKS],
        "genome_freeze_audit": {"passes": True, "violations": [],
                                "records_checked": 100},
    }
    if alpha is None:
        record.update({
            "terminal_census": {"tick": 2400, "n_live": 0,
                                "alpha_mean": None, "histogram_A": {},
                                "live_by_ancestry": {}},
            "alpha_end": None, "direction_class": None, "extinct": True,
        })
        if arm == "M":
            record["mutation_telemetry"] = {
                "passes": kernel_ok, "problems": []}
        else:
            record["mutation_telemetry"] = {
                "passes": True, "decision_records": 0, "draws_total": 0}
        return record
    histogram = _histogram_for(alpha, n_live)
    alpha_end_text = str(Fraction(
        sum(int(a) * c for a, c in
            ((int(k), v) for k, v in histogram.items())),
        255 * n_live))
    # G1 requires >=2 distinct A values among live members (evidence the
    # kernel actually diversified the lineage).  Rebuild the M-arm
    # histogram with >=2 values while keeping the mean EXACTLY equal to
    # alpha: take total_a = alpha*255*n and split it as (base-1, rest
    # spread) so the sum is unchanged.
    if arm == "M" and n_live >= 2:
        total_a = int(Fraction(alpha) * 255 * n_live)
        base, extra = divmod(total_a, n_live)
        if extra == 0:
            # exact-equal case: move one member down one unit and another
            # up one unit; mean preserved exactly, 3 distinct values.
            if base >= 1 and n_live >= 3:
                histogram = {str(base - 1): 1, str(base): n_live - 2,
                             str(base + 1): 1}
        else:
            # remainder case: give one member an extra +1 above its share
            # and drop one other member by 1 to compensate exactly.
            histogram = {str(base): n_live - extra - 1,
                         str(base + 1): extra}
            if base >= 1:
                histogram[str(base - 1)] = 1
                histogram[str(base)] -= 1
                histogram[str(base + 2)] = 1
                histogram[str(base + 1)] -= 0
                histogram = {k: v for k, v in histogram.items() if v > 0}
    ancestry = {"F0": census_n - 1, "F3": 1} \
        if arm == "M" else {"F0": census_n, }
    record.update({
        "terminal_census": {"tick": 2400, "n_live": n_live,
                            "alpha_mean": alpha_end_text,
                            "histogram_A": histogram,
                            "distinct_A_values": len(histogram),
                            "live_by_ancestry": ancestry},
        "alpha_end": alpha_end_text,
        "direction_class": None,
        "extinct": False,
    })
    from stage8_alpha_measure import direction_class

    record["direction_class"] = direction_class(alpha_end_text)
    if arm == "M":
        record["kernel_draw_chain"] = [
            {"stream_position": 0, "mutated": True, "delta": +1,
             "draws_consumed": 2}]
        record["mutation_telemetry"] = {
            "passes": kernel_ok,
            "decision_records": 1 if kernel_ok else 0,
            "draws_total": 2 if kernel_ok else 0,
            "problems": [] if kernel_ok else ["broken"],
        }
    else:
        record["kernel_draw_chain"] = []
        record["mutation_telemetry"] = {
            "passes": True, "decision_records": 0,
            "draws_total": 0, "admitted_births": 50}
    return record


def _pair(index: int, alpha_m: Fraction | None,
          alpha_r0: Fraction | None = Fraction(153, 255), **kwargs) -> dict:
    return {
        "pair_index": index,
        "hazard_seed": confirmatory_pair_seed(index),
        "arms": {
            "M": _arm_record("M", index, alpha_m, **kwargs),
            "R0": _arm_record("R0", index, alpha_r0),
        },
    }


def _raw(pairs: list[dict]) -> dict:
    return {
        "protocol": PROTOCOL,
        "seed_table": "confirmatory",
        "decision": "PENDING_REDUCTION",
        "pairs": pairs,
    }


REF = Fraction(153, 255)
UP = REF + Fraction(8, 255)      # D = +8/255, mover-up pair
DOWN = REF - Fraction(8, 255)    # D = -8/255, mover-down pair


class PairedRuleTests(unittest.TestCase):

    def _rule(self, alphas: Iterable[tuple[Fraction | None,
                                           Fraction | None]]) -> dict:
        pairs = [_pair(i, m, r) for i, (m, r) in enumerate(alphas)]
        validated = _validate(_raw(pairs))
        return apply_rule(validated)

    def test_established_toward_high_alpha(self):
        block = self._rule([(UP, REF)] * 18 + [(REF, REF)] * 6)
        self.assertEqual(block["outcome"], "ESTABLISHED_TOWARD_HIGH_ALPHA")
        self.assertEqual(block["counts"]["eligible_k_eff"], 24)
        self.assertEqual(block["counts"]["movers_up_pairs"], 18)

    def test_established_toward_low_alpha(self):
        block = self._rule([(DOWN, REF)] * 19 + [(REF, REF)] * 5)
        self.assertEqual(block["outcome"], "ESTABLISHED_TOWARD_LOW_ALPHA")

    def test_split_is_null(self):
        block = self._rule([(UP, REF)] * 12 + [(DOWN, REF)] * 12)
        self.assertEqual(block["outcome"], "NO_ESTABLISHED_DIRECTION")

    def test_common_mode_lottery_cancels(self):
        """The O1 scenario: both arms land on the same winning side."""
        # Every pair's winner sits at 102/255 in BOTH arms: raw ᾱ_end is
        # far below α_ref in each arm, but the paired difference is ~0.
        winner = Fraction(102, 255)
        alphas = [(winner, winner)] * 24
        block = self._rule(alphas)
        self.assertEqual(block["outcome"], "NO_ESTABLISHED_DIRECTION")
        self.assertEqual(block["counts"]["movers_up_pairs"], 0)

    def test_extinctions_shrink_k_eff(self):
        alphas = ([(UP, REF)] * 14 + [(None, REF)] * 5
                  + [(UP, None)] * 5)
        block = self._rule(alphas)
        self.assertEqual(block["outcome"], "DEGENERATE_EVOLUTION")
        self.assertEqual(block["counts"]["eligible_k_eff"], 14)
        self.assertEqual(len(block["counts"]["extinct_pairs"]), 10)

    def test_ineligible_reasons_recorded(self):
        alphas = [(UP, REF)] * 23 + [(None, REF)]
        block = self._rule(alphas)
        ineligible = block["counts"]["ineligible_pairs"]
        self.assertEqual(len(ineligible), 1)
        self.assertIn("M:extinct_at_W", ineligible[0]["reason"])

    def test_median_d_values(self):
        alphas = ([(REF + Fraction(10, 255), REF)] * 9
                  + [(REF + Fraction(30, 255), REF)] * 9
                  + [(REF, REF)] * 6)
        block = self._rule(alphas)
        self.assertEqual(block["outcome"], "ESTABLISHED_TOWARD_HIGH_ALPHA")
        self.assertEqual(
            block["descriptive"]["median_D_among_movers_up"],
            str((Fraction(10, 255) + Fraction(30, 255)) / 2))

    def test_leakage_monitor_fires_on_plurality_flip(self):
        pairs = [_pair(i, UP, REF) for i in range(24)]
        # Flip the R0 plurality of pair 0 to a different founder.
        census = pairs[0]["arms"]["R0"]["terminal_census"]
        census["live_by_ancestry"] = {"F4": 15, "F0": 5}
        block = apply_rule(_validate(_raw(pairs)))
        self.assertEqual(len(block["counts"]["leakage_pairs"]), 1)
        self.assertEqual(block["counts"]["leakage_pairs"][0]["R0_plurality"],
                         "F4")


class PairedValidationTests(unittest.TestCase):

    def _valid_pairs(self) -> list[dict]:
        return [_pair(i, REF, REF) for i in range(24)]

    def test_clean_artifact_validates(self):
        self.assertEqual(len(_validate(_raw(self._valid_pairs()))), 24)

    def test_missing_arm_refused(self):
        pairs = self._valid_pairs()
        del pairs[3]["arms"]["R0"]
        with self.assertRaises(ReducerValidationError):
            _validate(_raw(pairs))

    def test_extra_arm_refused(self):
        pairs = self._valid_pairs()
        pairs[5]["arms"]["X"] = pairs[5]["arms"]["M"]
        with self.assertRaises(ReducerValidationError):
            _validate(_raw(pairs))

    def test_arm_label_mismatch_refused(self):
        pairs = self._valid_pairs()
        pairs[7]["arms"]["M"]["arm"] = "R0"
        with self.assertRaises(ReducerValidationError):
            _validate(_raw(pairs))

    def test_r0_kernel_evidence_failure_refused(self):
        pairs = self._valid_pairs()
        pairs[9]["arms"]["R0"]["mutation_telemetry"]["passes"] = False
        with self.assertRaises(ReducerValidationError):
            _validate(_raw(pairs))

    def test_wrong_protocol_refused(self):
        raw = _raw(self._valid_pairs())
        raw["protocol"] = "other"
        with self.assertRaises(ReducerValidationError):
            _validate(raw)

    def test_double_reduction_refused(self):
        raw = _raw(self._valid_pairs())
        raw["decision"] = "REDUCED"
        with self.assertRaises(ReducerValidationError):
            _validate(raw)

    def test_wrong_seed_set_refused(self):
        pairs = self._valid_pairs()
        pairs[11]["hazard_seed"] = 1
        with self.assertRaises(ReducerValidationError):
            _validate(_raw(pairs))

    def test_endpoint_histogram_inconsistency_refused(self):
        pairs = self._valid_pairs()
        pairs[13]["arms"]["M"]["alpha_end"] = str(Fraction(200, 255))
        with self.assertRaises(ReducerValidationError):
            _validate(_raw(pairs))

    def test_paired_difference_helper(self):
        m = {"alpha_end": "157/255"}
        r0 = {"alpha_end": "153/255"}
        self.assertEqual(paired_difference(m, r0), Fraction(4, 255))
        self.assertIsNone(paired_difference({"alpha_end": None}, r0))


class PairedGateEvaluationTests(unittest.TestCase):

    def _pairs(self) -> list[dict]:
        return [_pair(i, UP, REF) for i in range(12)]

    def _replay_ok(self) -> dict:
        return {"passes": True, "reexecution_identical": True}

    def test_all_conditions_pass(self):
        summary = evaluate_gate(self._pairs(), self._replay_ok())
        self.assertTrue(summary["G1_evolution_operates"]["passes_G1"])
        self.assertTrue(summary["G2_implementation_integrity"]["passes_G2"])
        self.assertTrue(summary["G3_kernel_audit"]["passes_G3"])
        self.assertTrue(summary["G4_reference_arm_integrity"]["passes_G4"])
        self.assertTrue(summary["gate_passed"])

    def test_g1_requires_two_thirds_of_pairs(self):
        pairs = self._pairs()
        for pair in pairs[:5]:
            pair["arms"]["M"]["terminal_census"]["distinct_A_values"] = 1
        summary = evaluate_gate(pairs, self._replay_ok())
        self.assertFalse(summary["G1_evolution_operates"]["passes_G1"])

    def test_g1_genome_violation_anywhere_fails(self):
        pairs = self._pairs()
        pairs[0]["arms"]["R0"]["genome_freeze_audit"]["passes"] = False
        summary = evaluate_gate(pairs, self._replay_ok())
        self.assertFalse(summary["G1_evolution_operates"]["passes_G1"])

    def test_g2_counts_invalid_runs(self):
        pairs = self._pairs()
        pairs[2]["arms"]["R0"]["classification"] = "INVALID_IMPLEMENTATION"
        pairs[2]["arms"]["R0"]["reason"] = "UNEXPECTED_EXCEPTION"
        summary = evaluate_gate(pairs, self._replay_ok())
        self.assertFalse(summary["G2_implementation_integrity"]["passes_G2"])
        self.assertEqual(len(summary["invalid_runs"]), 1)

    def test_g4_detects_kernel_activity_in_reference(self):
        pairs = self._pairs()
        bad = pairs[4]["arms"]["R0"]["mutation_telemetry"]
        bad["decision_records"] = 3
        bad["passes"] = False
        summary = evaluate_gate(pairs, self._replay_ok())
        self.assertFalse(summary["G4_reference_arm_integrity"]["passes_G4"])
        self.assertFalse(summary["gate_passed"])

    def test_g4_detects_nonempty_reference_chain(self):
        pairs = self._pairs()
        pairs[6]["arms"]["R0"]["kernel_draw_chain"] = [
            {"stream_position": 0, "mutated": True, "delta": +1,
             "draws_consumed": 2}]
        summary = evaluate_gate(pairs, self._replay_ok())
        self.assertFalse(summary["G4_reference_arm_integrity"]["passes_G4"])

    def test_g4_detects_seed_mismatch_within_pair(self):
        pairs = self._pairs()
        pairs[8]["arms"]["R0"]["hazard_seed"] += 1
        summary = evaluate_gate(pairs, self._replay_ok())
        self.assertEqual(
            summary["G4_reference_arm_integrity"]["seed_mismatches"], [8])

    def test_g3_requires_replay_evidence(self):
        summary = evaluate_gate(self._pairs(), None)
        self.assertFalse(summary["G3_kernel_audit"]["passes_G3"])
        self.assertFalse(summary["gate_passed"])


if __name__ == "__main__":
    unittest.main()
