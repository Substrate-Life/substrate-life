"""Unit tests for the capped-population calibration reducer."""

import math
import unittest

from run_conditional_population_calibration import json_safe, summarize_cohort


class PopulationCalibrationRunnerTests(unittest.TestCase):
    def test_json_safe_converts_tuple_keys_recursively(self):
        value = {("RLE", 256): {("nested", 1): [1, 2]}}
        self.assertEqual(
            json_safe(value),
            {"('RLE', 256)": {"('nested', 1)": [1, 2]}},
        )

    def test_cohort_summary_uses_complete_lifetimes_only(self):
        rows = [
            {
                "endpoint": "death", "lifetime_live_births": 0,
                "death_age": 4, "first_valid_read_age": None,
                "first_live_birth_age": None,
                "death_cause": "displacement",
                "death_stage": "pre_first_valid_read",
            },
            {
                "endpoint": "death", "lifetime_live_births": 2,
                "death_age": 18, "first_valid_read_age": 5,
                "first_live_birth_age": 10,
                "death_cause": "displacement",
                "death_stage": "post_first_live_birth",
            },
            {
                "endpoint": "censored_alive", "lifetime_live_births": 99,
                "death_age": None, "first_valid_read_age": 5,
                "first_live_birth_age": 10,
                "death_cause": None, "death_stage": None,
            },
        ]
        result = summarize_cohort(rows)
        self.assertEqual(result["complete_deaths"], 2)
        self.assertEqual(result["censored_alive"], 1)
        self.assertAlmostEqual(result["unresolved_fraction"], 1 / 3)
        self.assertEqual(result["lifetime_live_births_mean"], 1)
        self.assertEqual(result["lifetime_live_births_variance_population"], 1)
        self.assertEqual(result["lifetime_live_births_distribution"],
                         {"0": 1, "2": 1})
        self.assertTrue(math.isclose(result["Ne_variance_heuristic"], 77.5))
        self.assertEqual(result["first_live_birth_age_mean_among_reproducers"],
                         10)


if __name__ == "__main__":
    unittest.main()
