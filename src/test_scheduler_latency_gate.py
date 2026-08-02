"""Tests for the registered scheduler-latency sensitivity reducer."""

from __future__ import annotations

from fractions import Fraction
import unittest

from scheduler_latency_gate import (
    classify_gate,
    classify_morphology,
    encode_uleb128,
    extract_latency_values,
    nearest_index_percentile,
    reduction_sign_counts,
    verify_journal_coverage,
    zigzag,
)


class SchedulerLatencyGateTests(unittest.TestCase):
    def test_latency_values_use_deadline_lateness_and_signed_cadence_deviation(self):
        records = [
            {"scheduled_deadline_monotonic_ns": 100, "wake_monotonic_ns": 110},
            {"scheduled_deadline_monotonic_ns": 200, "wake_monotonic_ns": 230},
            {"scheduled_deadline_monotonic_ns": 300, "wake_monotonic_ns": 305},
        ]
        lateness, deviation = extract_latency_values(records, cadence_ns=100)
        self.assertEqual(lateness, [30, 5])
        self.assertEqual(deviation, [20, -25])

    def test_zigzag_and_uleb128_match_registered_vectors(self):
        self.assertEqual([zigzag(x) for x in (0, -1, 1, -2, 2)], [0, 1, 2, 3, 4])
        self.assertEqual(encode_uleb128([0, 127, 128, 300]), bytes.fromhex("007f8001ac02"))
        self.assertEqual(nearest_index_percentile([10, 20], 1, 2), 20)
        self.assertEqual(
            reduction_sign_counts([-2, 0, 1, 3]),
            {"positive": 2, "zero": 1, "negative": 1},
        )

    def test_gate_separates_direct_from_morphological_response(self):
        passive = {
            "latency": {"median_ns": 100, "p99_ns": 500},
            "winner_counts": {"RLE": 30000, "DIFF": 6000, "TIE": 0},
            "criteria": {"switching": False, "block_drift": False},
            "block_medians": {
                "RLE": [Fraction(0)] * 12,
                "DIFF": [Fraction(0)] * 12,
            },
        }
        loaded = {
            "latency": {"median_ns": 250, "p99_ns": 600},
            "winner_counts": {"RLE": 18000, "DIFF": 18000, "TIE": 0},
            "criteria": {"switching": False, "block_drift": False},
            "block_medians": {
                "RLE": [Fraction(0)] * 12,
                "DIFF": [Fraction(0)] * 12,
            },
        }
        result = classify_gate(passive, loaded)
        self.assertTrue(result["directly_responsive"])
        self.assertTrue(result["morphologically_responsive"])
        self.assertEqual(result["classification"], "LOAD_SENSITIVE_LATENCY_MORPHOLOGY")

    def test_morphology_requires_strict_block_majorities(self):
        result = classify_morphology(
            {"RLE": 18000, "DIFF": 18000, "TIE": 0},
            [
                {"RLE": 1200, "DIFF": 1000, "TIE": 800},
                {"RLE": 1000, "DIFF": 1200, "TIE": 800},
            ],
            {"RLE": [Fraction(0), Fraction(0)],
             "DIFF": [Fraction(0), Fraction(1, 15)]},
        )
        self.assertEqual(result, {"switching": False, "block_drift": False})

    def test_morphology_property_disappearance_is_a_symmetric_response(self):
        sham = {
            "latency": {"median_ns": 100, "p99_ns": 500},
            "winner_counts": {"RLE": 18000, "DIFF": 18000, "TIE": 0},
            "criteria": {"switching": True, "block_drift": False},
            "block_medians": {"RLE": [Fraction(0)] * 12,
                              "DIFF": [Fraction(0)] * 12},
        }
        compile_arm = {
            **sham,
            "criteria": {"switching": False, "block_drift": False},
        }
        result = classify_gate(sham, compile_arm)
        self.assertTrue(result["morphologically_responsive"])
        self.assertEqual(
            result["classification"], "MORPHOLOGY_CHANGE_WITHOUT_DIRECT_SHIFT"
        )

    def test_sham_journal_coverage_rejects_heartbeat_gap(self):
        billion = 1_000_000_000
        records = [
            {"scheduled_deadline_monotonic_ns": 40 * billion,
             "read_end_monotonic_ns": 40 * billion},
            {"scheduled_deadline_monotonic_ns": 80 * billion,
             "read_end_monotonic_ns": 79 * billion},
        ]
        events = [
            {"event": "manager_started", "monotonic_ns": 0},
            {"event": "worker_ready", "worker": 0, "monotonic_ns": billion},
            {"event": "worker_ready", "worker": 1, "monotonic_ns": 2*billion},
            {"event": "workload_started", "arm": "S", "mode": "sham", "monotonic_ns": 10*billion},
            {"event": "heartbeat", "live_workers": 2, "monotonic_ns": 10*billion},
            {"event": "heartbeat", "live_workers": 2, "monotonic_ns": 20*billion},
            {"event": "heartbeat", "live_workers": 2, "monotonic_ns": 30*billion},
            {"event": "capture_started", "monotonic_ns": 40*billion},
            {"event": "heartbeat", "live_workers": 2, "monotonic_ns": 40*billion},
            {"event": "heartbeat", "live_workers": 2, "monotonic_ns": 50*billion},
            {"event": "heartbeat", "live_workers": 2, "monotonic_ns": 60*billion},
            {"event": "heartbeat", "live_workers": 2, "monotonic_ns": 70*billion},
            {"event": "heartbeat", "live_workers": 2, "monotonic_ns": 80*billion},
            {"event": "capture_completed", "monotonic_ns": 80*billion},
            {"event": "workload_stopped", "monotonic_ns": 81*billion,
             "cleanup_success": True, "live_workers_after_join": 0,
             "workers": [{"invocations": 0}, {"invocations": 0}]},
        ]
        result = verify_journal_coverage(events, records, "S", "sham")
        self.assertEqual(result["heartbeat_count"], 8)
        broken = [dict(event) for event in events if event.get("monotonic_ns") != 60*billion]
        with self.assertRaisesRegex(ValueError, "heartbeat gap"):
            verify_journal_coverage(broken, records, "S", "sham")


if __name__ == "__main__":
    unittest.main()
