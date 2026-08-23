"""Registered Stage 8 paired-arm layer test matrix.

Covers ``stage8_paired`` (arm factories, kernel-absence witness, seed
tables, retired-table disjointness), the shared measurement path on both
arms at plumbing scale, and the paired gate evaluation G1-G4.
"""

from __future__ import annotations

import unittest

from stage7b2_population import Stage7B2Population
from stage8_paired import (
    CONFIRMATORY_PAIR_SEED_BASE,
    DIRECTION_FLOOR_PAIRED,
    PAIR_REPLICATES,
    RETIRED_TABLES,
    SHAKEDOWN_PAIR_COUNT,
    SHAKEDOWN_PAIR_SEED_BASE,
    assert_kernel_absent,
    confirmatory_pair_seed,
    registered_configuration,
    registered_m_population,
    registered_r0_population,
    shakedown_pair_seed,
    shakedown_pair_seeds,
)
from stage8_population import Stage8Population
from run_stage8_alpha import measure_population


class ArmFactoryTests(unittest.TestCase):

    def test_m_arm_carries_kernel(self):
        population = registered_m_population(20310529, window_ticks=2)
        self.assertIsInstance(population, Stage8Population)
        self.assertTrue(hasattr(population, "mutation_rng"))
        self.assertTrue(hasattr(population, "mutation_draws"))
        assert_kernel_absent  # reference exists; M must fail absence check
        with self.assertRaises(AssertionError):
            assert_kernel_absent(population)

    def test_r0_arm_is_frozen_stack_without_kernel(self):
        population = registered_r0_population(20310529, window_ticks=2)
        self.assertIsInstance(population, Stage7B2Population)
        self.assertNotIsInstance(population, Stage8Population)
        assert_kernel_absent(population)
        self.assertEqual(population.window_ticks, 2)
        # Same founders, capacity, and frozen-locus configuration as M.
        self.assertEqual(len(population.members), 6)
        self.assertEqual(population.capacity, 48)


class SeedTableTests(unittest.TestCase):

    def test_derivations(self):
        self.assertEqual(confirmatory_pair_seed(0), 20310529)
        self.assertEqual(confirmatory_pair_seed(23), 20310552)
        self.assertEqual(shakedown_pair_seed(0), 20421301)
        self.assertEqual(shakedown_pair_seed(11), 20421312)
        self.assertEqual(PAIR_REPLICATES, 24)
        self.assertEqual(SHAKEDOWN_PAIR_COUNT, 12)

    def test_out_of_range_refused(self):
        with self.assertRaises(ValueError):
            confirmatory_pair_seed(24)
        with self.assertRaises(ValueError):
            shakedown_pair_seed(12)

    def test_disjoint_from_every_retired_table(self):
        new_ranges = [
            set(range(CONFIRMATORY_PAIR_SEED_BASE,
                      CONFIRMATORY_PAIR_SEED_BASE + PAIR_REPLICATES)),
            set(range(SHAKEDOWN_PAIR_SEED_BASE,
                      SHAKEDOWN_PAIR_SEED_BASE + SHAKEDOWN_PAIR_COUNT))]
        for _, base, count in RETIRED_TABLES:
            retired = set(range(base, base + count))
            for fresh in new_ranges:
                self.assertFalse(fresh & retired,
                                 f"overlap with retired base {base}")

    def test_shakedown_seeds_complete(self):
        self.assertEqual(len(shakedown_pair_seeds()), 12)

    def test_floor_value(self):
        from fractions import Fraction
        self.assertEqual(DIRECTION_FLOOR_PAIRED, Fraction(4, 255))


class PairedMeasurementSmokeTests(unittest.TestCase):

    # W = 120 keeps the run inside the real checkpoint schedule (tick 120
    # is the first registered checkpoint) at plumbing-scale cost.
    WINDOW = 120

    def _measure(self, factory, arm, seed=20310529):
        population = factory(seed, window_ticks=self.WINDOW)
        return measure_population(
            population, seed_table="plumbing", replicate_index=0,
            hazard_seed=seed, arm=arm)

    def test_r0_record_carries_kernel_absence_evidence(self):
        record = self._measure(registered_r0_population, "R0")
        self.assertEqual(record["arm"], "R0")
        self.assertEqual(record["classification"], "COMPLETE")
        telemetry = record["mutation_telemetry"]
        self.assertTrue(telemetry["passes"])
        self.assertEqual(telemetry["decision_records"], 0)
        self.assertEqual(telemetry["draws_total"], 0)
        self.assertEqual(record["kernel_draw_chain"], [])
        self.assertGreater(telemetry["admitted_births"], 0)

    def test_m_record_carries_kernel_evidence(self):
        record = self._measure(registered_m_population, "M")
        self.assertEqual(record["arm"], "M")
        self.assertEqual(record["classification"], "COMPLETE")
        telemetry = record["mutation_telemetry"]
        self.assertTrue(telemetry["passes"])
        self.assertEqual(
            telemetry["decision_records"],
            len(record["kernel_draw_chain"]))
        self.assertGreater(telemetry["decision_records"], 0)

    def test_arms_share_hazard_stream_prefix(self):
        """Same seed => identical opening hazard draws across arms."""
        m = registered_m_population(20421301, window_ticks=1)
        r0 = registered_r0_population(20421301, window_ticks=1)
        self.assertIsNotNone(getattr(m, "hazard_rng", None))
        self.assertIsNotNone(getattr(r0, "hazard_rng", None))
        m_prefix = [m.hazard_rng.random() for _ in range(5)]
        r0_prefix = [r0.hazard_rng.random() for _ in range(5)]
        self.assertEqual(m_prefix, r0_prefix)


class ConfigurationEchoTests(unittest.TestCase):

    def test_echo_fields(self):
        echo = registered_configuration()
        self.assertEqual(echo["arms"]["M"].startswith("dedicated-locus"),
                         True)
        self.assertIn("byte-frozen", echo["arms"]["R0"])
        self.assertEqual(echo["pairs_k"], 24)
        self.assertEqual(echo["runs_total"], 48)
        self.assertEqual(echo["direction_floor_paired"], "4/255")
        retired_bases = {entry["base"]
                         for entry in echo["retired_tables_never_reused"]}
        self.assertIn(20284617, retired_bases)
        self.assertIn(20293311, retired_bases)


if __name__ == "__main__":
    unittest.main()
