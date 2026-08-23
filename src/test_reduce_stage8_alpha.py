"""Registered Stage 8 reducer test matrix.

Synthetic raw-artifact fixtures exercising every branch of the source-frozen
section 5 rule (``reduce_stage8_alpha.apply_rule``) and the pre-rule
validation (``_validate``): all four outcome classes, exact-threshold
boundaries, extinction/ineligibility paths, and the refusal conditions.
"""

from __future__ import annotations

import json
import tempfile
import os
from fractions import Fraction
from typing import Iterable

import unittest

from reduce_stage8_alpha import (
    ReducerValidationError,
    _validate,
    apply_rule,
)
from stage8_alpha_measure import CHECKPOINT_TICKS, direction_class
from stage8_population import (
    CONFIRMATORY_SEED_BASE,
    PROTOCOL,
    STAGE8_REPLICATES,
    confirmatory_seed,
)


def _histogram_for(mean_alpha: Fraction, n_live: int = 24) -> dict[str, int]:
    """Exact histogram of A values whose mean A/255 equals ``mean_alpha``.

    ``mean A = alpha * 255`` must be an integer lattice value; the sum is
    spread as evenly as the lattice allows while keeping the exact mean.
    """
    mean_a = Fraction(mean_alpha) * 255
    if mean_a.denominator != 1:
        raise ValueError("alpha must be a multiple of 1/255")
    total = int(mean_a) * n_live
    base, extra = divmod(total, n_live)
    if base == 255:
        histogram = {255: n_live}
    else:
        histogram = {base: n_live - extra}
        if extra:
            histogram[base + 1] = extra
    return {str(a): c for a, c in sorted(histogram.items())}


def _complete_record(index: int, mean_alpha: Fraction | None,
                     n_live: int = 24) -> dict:
    """A validation-clean COMPLETE record with the given endpoint."""
    seed = confirmatory_seed(index)
    census_n = 0 if mean_alpha is None else n_live
    record: dict = {
        "seed_table": "confirmatory",
        "replicate_index": index,
        "hazard_seed": seed,
        "classification": "COMPLETE",
        "ticks_completed": 2400,
        "window_ticks": 2400,
        "mutation_telemetry": {"passes": True, "problems": []},
        "genome_freeze_audit": {"passes": True, "violations": []},
        "trajectory_checkpoints": [
            {"tick": tick, "n_live": census_n}
            for tick in CHECKPOINT_TICKS],
    }
    if mean_alpha is None:
        # Extinct: empty census.
        record.update({
            "terminal_census": {
                "tick": 2400, "n_live": 0, "alpha_mean": None,
                "histogram_A": {}},
            "alpha_end": None,
            "direction_class": None,
            "extinct": True,
        })
        return record
    histogram = _histogram_for(mean_alpha, n_live)
    alpha_end_text = str(Fraction(
        sum(int(a) * count for a, count in
            ((k, v) for k, v in histogram.items())),
        255 * n_live))
    record.update({
        "terminal_census": {
            "tick": 2400, "n_live": n_live,
            "alpha_mean": alpha_end_text,
            "histogram_A": histogram},
        "alpha_end": alpha_end_text,
        "direction_class": direction_class(alpha_end_text),
        "extinct": False,
    })
    return record


def _raw_artifact(records: list[dict]) -> dict:
    return {
        "protocol": PROTOCOL,
        "seed_table": "confirmatory",
        "decision": "PENDING_REDUCTION",
        "replicates": records,
    }


REF = Fraction(153, 255)
HIGH = REF + Fraction(16, 255)   # mover_up
LOW = REF - Fraction(16, 255)    # mover_down
NEAR = REF + Fraction(2, 255)    # non_mover


class RuleClassTests(unittest.TestCase):

    def _rule(self, means: Iterable[Fraction | None]) -> dict:
        records = [_complete_record(i, m) for i, m in enumerate(means)]
        replicates = _validate(_raw_artifact(records))
        return apply_rule(replicates)

    def test_established_toward_high_alpha(self):
        means = [HIGH] * 18 + [NEAR] * 6
        block = self._rule(means)
        self.assertEqual(block["outcome"], "ESTABLISHED_TOWARD_HIGH_ALPHA")
        self.assertEqual(block["counts"]["eligible_k_eff"], 24)
        self.assertEqual(block["counts"]["movers_up"], 18)

    def test_established_toward_low_alpha(self):
        means = [LOW] * 19 + [NEAR] * 5
        block = self._rule(means)
        self.assertEqual(block["outcome"], "ESTABLISHED_TOWARD_LOW_ALPHA")

    def test_split_is_null(self):
        means = [HIGH] * 12 + [LOW] * 12
        block = self._rule(means)
        self.assertEqual(block["outcome"], "NO_ESTABLISHED_DIRECTION")

    def test_all_near_is_null(self):
        means = [NEAR] * 24
        block = self._rule(means)
        self.assertEqual(block["outcome"], "NO_ESTABLISHED_DIRECTION")
        self.assertEqual(block["counts"]["movers_up"], 0)

    def test_seventeen_movers_below_threshold(self):
        means = [HIGH] * 17 + [NEAR] * 7
        block = self._rule(means)
        self.assertEqual(block["outcome"], "NO_ESTABLISHED_DIRECTION")

    def test_extinctions_shrink_k_eff_and_can_degenerate(self):
        # 10 extinct replicates -> k_eff = 14 < 16 even though every
        # eligible replicate moved the same way.
        means = [HIGH] * 14 + [None] * 10
        block = self._rule(means)
        self.assertEqual(block["outcome"], "DEGENERATE_EVOLUTION")
        self.assertEqual(block["counts"]["eligible_k_eff"], 14)
        self.assertEqual(len(block["counts"]["extinct_replicates"]), 10)

    def test_fifteen_eligible_with_unanimous_movement_degenerates(self):
        means = [HIGH] * 15 + [None] * 9
        block = self._rule(means)
        self.assertEqual(block["outcome"], "DEGENERATE_EVOLUTION")

    def test_sixteen_eligible_cannot_reach_concordance(self):
        # With exactly k_eff = 16 the concordance threshold of 18 is
        # arithmetically unreachable; even unanimous movement stays a
        # registered null rather than an established direction.
        means = [HIGH] * 16 + [None] * 8
        block = self._rule(means)
        self.assertEqual(block["outcome"], "NO_ESTABLISHED_DIRECTION")
        self.assertEqual(block["counts"]["movers_up"], 16)

    def test_median_abs_difference_among_movers(self):
        means = ([REF + Fraction(10, 255)] * 9
                 + [REF + Fraction(20, 255)] * 9 + [NEAR] * 6)
        block = self._rule(means)
        self.assertEqual(block["outcome"], "ESTABLISHED_TOWARD_HIGH_ALPHA")
        self.assertEqual(
            block["descriptive"]["median_abs_delta_alpha_among_movers_up"],
            "1/17")  # median of nine 10/255 and nine 20/255 gaps, reduced


class ValidationTests(unittest.TestCase):

    def _valid_records(self) -> list[dict]:
        return [_complete_record(i, NEAR) for i in range(24)]

    def test_clean_artifact_validates(self):
        replicates = _validate(_raw_artifact(self._valid_records()))
        self.assertEqual(len(replicates), 24)

    def test_wrong_protocol_refused(self):
        raw = _raw_artifact(self._valid_records())
        raw["protocol"] = "some-other-protocol"
        with self.assertRaises(ReducerValidationError):
            _validate(raw)

    def test_shakedown_table_refused(self):
        raw = _raw_artifact(self._valid_records())
        raw["seed_table"] = "shakedown"
        with self.assertRaises(ReducerValidationError):
            _validate(raw)

    def test_double_reduction_refused(self):
        raw = _raw_artifact(self._valid_records())
        raw["decision"] = "ALREADY_REDUCED"
        with self.assertRaises(ReducerValidationError):
            _validate(raw)

    def test_wrong_replicate_count_refused(self):
        records = self._valid_records()[:23]
        with self.assertRaises(ReducerValidationError):
            _validate(_raw_artifact(records))

    def test_wrong_seed_set_refused(self):
        records = self._valid_records()
        records[7]["hazard_seed"] = 99999999
        with self.assertRaises(ReducerValidationError):
            _validate(_raw_artifact(records))

    def test_endpoint_histogram_inconsistency_refused(self):
        records = self._valid_records()
        tampered = records[3]
        tampered["alpha_end"] = str(Fraction(200, 255))  # not what histogram says
        with self.assertRaises(ReducerValidationError):
            _validate(_raw_artifact(records))

    def test_missing_kernel_audit_refused(self):
        records = self._valid_records()
        records[5]["mutation_telemetry"] = {"passes": False, "problems": ["x"]}
        with self.assertRaises(ReducerValidationError):
            _validate(_raw_artifact(records))

    def test_direction_class_mismatch_refused(self):
        records = self._valid_records()
        records[2]["direction_class"] = "mover_up"  # NEAR is a non-mover
        with self.assertRaises(ReducerValidationError):
            _validate(_raw_artifact(records))

    def test_missing_terminal_snapshot_refused(self):
        records = self._valid_records()
        del records[1]["terminal_census"]
        with self.assertRaises(ReducerValidationError):
            _validate(_raw_artifact(records))

    def test_checkpoint_schedule_incomplete_refused(self):
        records = self._valid_records()
        records[4]["trajectory_checkpoints"] = \
            records[4]["trajectory_checkpoints"][:-1]
        with self.assertRaises(ReducerValidationError):
            _validate(_raw_artifact(records))

    def test_final_checkpoint_disagreement_refused(self):
        records = self._valid_records()
        records[6]["trajectory_checkpoints"][-1]["n_live"] = 23
        with self.assertRaises(ReducerValidationError):
            _validate(_raw_artifact(records))


class HistogramHelperTests(unittest.TestCase):

    def test_helper_hits_requested_alpha(self):
        for mean in (NEAR, HIGH, LOW):
            histogram = _histogram_for(mean, n_live=24)
            total = sum(int(a) * count for a, count in histogram.items())
            self.assertEqual(Fraction(total, 24 * 255), mean)
            self.assertLessEqual(max(int(a) for a in histogram), 255)

    def test_helper_rejects_off_lattice_alpha(self):
        with self.assertRaises(ValueError):
            _histogram_for(Fraction(1, 7), n_live=24)


if __name__ == "__main__":
    unittest.main()
