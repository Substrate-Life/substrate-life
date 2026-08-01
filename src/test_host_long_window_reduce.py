"""Tests for the registered long-window host-channel reduction."""

from __future__ import annotations

import unittest

from host_long_window_reduce import classify_registered


class LongWindowClassificationTests(unittest.TestCase):
    def test_all_local_slices_stable_with_large_block_shift_is_timescale_separated(self):
        classification = classify_registered(
            [True] * 120,
            {"RLE": [100] * 6 + [120] * 6, "DIFF": [40] * 12},
        )
        self.assertEqual(classification, "TIMESCALE_SEPARATED_DRIFT")

    def test_all_local_slices_stable_without_large_shift_is_long_window_stable(self):
        classification = classify_registered(
            [True] * 120,
            {"RLE": [100, 116] * 6, "DIFF": [40, 50] * 6},
        )
        self.assertEqual(classification, "LONG_WINDOW_NARROW_STABLE")

    def test_any_unstable_local_slice_overrides_longer_drift(self):
        classification = classify_registered(
            [True] * 119 + [False],
            {"RLE": [100] * 6 + [130] * 6, "DIFF": [40] * 12},
        )
        self.assertEqual(classification, "WITHIN_30S_VARIATION")


if __name__ == "__main__":
    unittest.main()
