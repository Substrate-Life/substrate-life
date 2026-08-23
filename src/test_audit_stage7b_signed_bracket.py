"""Tests for the read-only signed-bracket audit helpers (synthetic data).

These tests exercise only the pure computation helpers; they never touch
the retained artifacts.
"""

from __future__ import annotations

import unittest
from fractions import Fraction

from audit_stage7b_signed_bracket import (
    bracket_midpoint,
    independent_outcome,
    median_lower_middle,
    parse_rat,
    quantile_lower_middle,
)


def _certificate(status: str, r_lo: str, r_hi: str) -> dict:
    return {"status": status, "r_lo": r_lo, "r_hi": r_hi}


def _replicate(index: int, cert_102: dict, cert_204: dict,
               classification: str = "COMPLETE") -> dict:
    return {
        "replicate_index": index,
        "classification": classification,
        "solver_certificates": {"102": cert_102, "204": cert_204},
    }


class ParsingTests(unittest.TestCase):

    def test_parse_rat_exact(self) -> None:
        self.assertEqual(parse_rat("-1/128"), Fraction(-1, 128))
        self.assertEqual(parse_rat("3/1"), Fraction(3, 1))

    def test_midpoint_of_finite_root_bracket(self) -> None:
        certificate = _certificate("SUBCRITICAL", "-3/256", "-1/256")
        self.assertEqual(bracket_midpoint(certificate), Fraction(-1, 128))

    def test_midpoint_none_for_nonfinite_status(self) -> None:
        certificate = {"status": "NO_FINITE_ROOT", "r_lo": "0/1",
                       "r_hi": "0/1"}
        self.assertIsNone(bracket_midpoint(certificate))

    def test_median_lower_middle_convention(self) -> None:
        values = [Fraction(k) for k in range(4)]
        # Registered even-k convention: index (n-1)//2 -> 1, not 1.5.
        self.assertEqual(median_lower_middle(values), Fraction(1))

    def test_median_empty_is_none(self) -> None:
        self.assertIsNone(median_lower_middle([]))

    def test_quantile_lower_middle_monotone(self) -> None:
        values = [Fraction(k) for k in range(32)]
        q1 = quantile_lower_middle(values, 1, 4)
        median = median_lower_middle(values)
        q3 = values[(3 * 32) // 4]
        assert q1 is not None and median is not None
        self.assertLessEqual(q1, median)
        self.assertLessEqual(median, q3)


class IndependentOutcomeTests(unittest.TestCase):

    def test_all_supercritical_pairs_and_signs(self) -> None:
        replicates = [
            _replicate(0, _certificate("SUPERCRITICAL", "0/1", "1/2"),
                       _certificate("SUPERCRITICAL", "1/2", "1/1")),
            _replicate(1, _certificate("SUPERCRITICAL", "0/1", "1/2"),
                       _certificate("SUPERCRITICAL", "0/1", "1/2")),
        ]
        outcome = independent_outcome(replicates)
        self.assertEqual(outcome["complete_pairs"], 2)
        # Delta_i = mid204 - mid102: +1/2 then 0.
        self.assertEqual(outcome["sign_split"],
                         {"positive": 1, "negative": 0, "zero": 1})
        self.assertEqual(outcome["median_paired_difference"], "0/1")
        self.assertFalse(outcome["subcritical_at_this_ecology"]["102"])
        self.assertFalse(outcome["subcritical_at_this_ecology"]["204"])

    def test_subcritical_brackets_pair_as_signed_values(self) -> None:
        replicates = [
            _replicate(
                index,
                # mid102 = -8/512 = -1/64
                _certificate("SUBCRITICAL", "-9/512", "-7/512"),
                # mid204 = -4/512 = -1/128
                _certificate("SUBCRITICAL", "-5/512", "-3/512"))
            for index in range(16)
        ]
        outcome = independent_outcome(replicates)
        self.assertEqual(outcome["complete_pairs"], 16)
        # Every delta = -1/128 - (-1/64) = +1/128 >= 0.
        self.assertEqual(outcome["sign_split"],
                         {"positive": 16, "negative": 0, "zero": 0})
        self.assertEqual(outcome["median_paired_difference"], "1/128")
        self.assertTrue(outcome["subcritical_at_this_ecology"]["102"])
        self.assertTrue(outcome["subcritical_at_this_ecology"]["204"])
        # 1/128 < 1/100: the same magnitude that produced the registered
        # NO_ESTABLISHED_CONTRAST in the retained line.
        self.assertEqual(outcome["pairs_at_or_above_floor_abs"], 0)

    def test_incomplete_replicates_excluded(self) -> None:
        replicates = [
            _replicate(0, _certificate("SUPERCRITICAL", "0/1", "1/256"),
                       _certificate("SUPERCRITICAL", "1/256", "2/256")),
            _replicate(1, _certificate("SUPERCRITICAL", "0/1", "1/256"),
                       _certificate("SUPERCRITICAL", "1/256", "2/256"),
                       classification="BUFFER_OVERFLOW"),
        ]
        outcome = independent_outcome(replicates)
        self.assertEqual(outcome["complete_pairs"], 1)

    def test_no_finite_root_excludes_pair(self) -> None:
        replicates = [
            _replicate(0, _certificate("NO_FINITE_ROOT", "0/1", "0/1"),
                       _certificate("SUPERCRITICAL", "1/256", "2/256")),
            _replicate(1, _certificate("SUBCRITICAL", "-9/256", "-8/256"),
                       _certificate("SUBCRITICAL", "1/256", "2/256")),
        ]
        outcome = independent_outcome(replicates)
        self.assertEqual(outcome["complete_pairs"], 1)
        self.assertEqual(outcome["statuses"]["102"]["NO_FINITE_ROOT"], 1)
        # Delta = 3/512 - (-17/512) = 20/512 = 5/128 >= floor 1/100.
        self.assertEqual(outcome["median_paired_difference"], "5/128")


if __name__ == "__main__":
    unittest.main()
