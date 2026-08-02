"""Tests for the registered retained-trace encoding diagnostic."""

from __future__ import annotations

import unittest
from fractions import Fraction

from host_encoding_diagnostic import (
    classify_diagnostic,
    classify_mapping,
    encode_low_u8,
    encode_normalized_u8,
    encode_uleb128,
)


class EncodingDiagnosticTests(unittest.TestCase):
    def test_normalized_u8_uses_registered_half_up_rule(self):
        encoded = encode_normalized_u8(
            [(0, 5, 10)],
            ((0, 10), (5, 5), (0, 20)),
        )
        self.assertEqual(encoded, bytes((0, 0, 128)))

    def test_uleb128_is_canonical_and_self_delimiting(self):
        encoded = encode_uleb128([(0, 127, 128, 300)])
        self.assertEqual(encoded, bytes.fromhex("007f8001ac02"))

    def test_low_u8_discards_all_but_low_order_byte(self):
        encoded = encode_low_u8([(0, 255, 256, 511, 512)])
        self.assertEqual(encoded, bytes((0, 255, 0, 255, 0)))

    def test_registered_mapping_and_overall_classification(self):
        switching = classify_mapping(
            {"RLE": 18000, "DIFF": 18000, "TIE": 0},
            [
                {"RLE": 3000, "DIFF": 0, "TIE": 0},
                {"RLE": 0, "DIFF": 3000, "TIE": 0},
            ],
            {"RLE": [Fraction(1, 10), Fraction(1, 10)],
             "DIFF": [Fraction(1, 10), Fraction(1, 10)]},
        )
        threshold_only = classify_mapping(
            {"RLE": 36000, "DIFF": 0, "TIE": 0},
            [{"RLE": 3000, "DIFF": 0, "TIE": 0}],
            {"RLE": [Fraction(0), Fraction(1, 15)],
             "DIFF": [Fraction(0), Fraction(1, 15)]},
        )
        self.assertEqual(switching, {"switching": True, "block_drift": False})
        self.assertEqual(threshold_only, {"switching": False, "block_drift": False})
        self.assertEqual(
            classify_diagnostic([threshold_only, switching]),
            "MAPPING_DEPENDENT_SIGNAL",
        )


if __name__ == "__main__":
    unittest.main()
