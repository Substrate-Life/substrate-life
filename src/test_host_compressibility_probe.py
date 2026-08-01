"""Tests for the cheap non-organism host-compressibility probe."""

from __future__ import annotations

import unittest

from host_compressibility_probe import analyze_payloads


class HostCompressibilityProbeTests(unittest.TestCase):
    def test_narrow_single_winner_is_classified_stable(self):
        payloads = [bytes([7]) * 240 for _ in range(300)]

        result = analyze_payloads(payloads, block_size=50)

        self.assertEqual(result["classification"], "NARROW_STABLE")
        self.assertEqual(result["winner_counts"], {"RLE": 300, "DIFF": 0, "TIE": 0})
        self.assertEqual(result["reduction_p90_minus_p10"], {"RLE": 0, "DIFF": 0})

    def test_contiguous_opposite_winner_periods_are_switching_capable(self):
        rle_payload = b"".join(bytes([value]) * 3 for value in range(80))
        diff_payload = bytes((index * 7) % 256 for index in range(240))
        payloads = [rle_payload] * 150 + [diff_payload] * 150

        result = analyze_payloads(payloads, block_size=50)

        self.assertEqual(result["classification"], "SWITCHING_CAPABLE")
        self.assertEqual(result["winner_counts"], {"RLE": 150, "DIFF": 150, "TIE": 0})
        self.assertIn("RLE", result["block_majorities"])
        self.assertIn("DIFF", result["block_majorities"])

    def test_mixed_without_required_periods_is_ambiguous(self):
        rle_payload = bytes([3]) * 240
        diff_payload = bytes((index * 7) % 256 for index in range(240))
        payloads = [rle_payload if index % 5 else diff_payload for index in range(300)]

        result = analyze_payloads(payloads, block_size=50)

        self.assertEqual(result["classification"], "AMBIGUOUS")


if __name__ == "__main__":
    unittest.main()
