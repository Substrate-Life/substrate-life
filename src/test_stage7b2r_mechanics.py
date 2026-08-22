"""Stage 7B2-R mechanics tests: the superseding configuration layer.

Covers exactly what is NEW in ``stage7b2r_population.py``,
``stage7b2r_gate.py``, ``run_stage7b2r.py``, and ``reduce_stage7b2r.py``
against ``docs/stage-7b2-repair-preregistration.md``:

- the registered section 3 constants and their carry-forward list;
- seed-table derivations and the binding shakedown/confirmatory
  disjointness invariant (section 3 / section 6.1);
- the disclosed section 4 somatic-economy arithmetic as exact fractions;
- population construction through the unchanged Stage 7B2 machinery plus a
  short-window integration smoke (ledgers close; census bound respected);
- feasibility-gate evaluation logic G1-G4 with its two-thirds threshold;
- runner/reducer plumbing echoes and serialisation rules.

The unchanged shared modules (mechanics, measurement, solver) keep their
Stage 7B2 coverage byte-identically; nothing here duplicates it.  No
fitness, selection, or evolutionary claim is made or tested.
"""

from __future__ import annotations

from fractions import Fraction
import json
import unittest

from stage7b1_mechanics import REGISTERED_PACKET_RATE
from stage7b2_population import run_window
from stage7b2_solver import MIN_CONTRAST_DELTA_R, SOLVER_RESOLUTION_RHO
from stage7b2r_gate import _gate_threshold, evaluate_gate
from stage7b2r_population import (
    REGISTERED_BUFFER_DEPTH,
    REGISTERED_CENSUS_CAPACITY,
    REGISTERED_CORPSE_TTL,
    REGISTERED_FOUNDER_S,
    REGISTERED_GENOTYPES,
    REGISTERED_HAZARD_RATE,
    REGISTERED_MEMORY_POOL,
    REGISTERED_PACKET_ENERGY,
    REGISTERED_REPLICATE_SEED_BASE,
    REGISTERED_REPLICATES,
    REGISTERED_WINDOW_TICKS,
    SHAKEDOWN_SEED_BASE,
    SHAKEDOWN_SEED_COUNT,
    registered_configuration,
    registered_founder_genomes,
    registered_population,
    registered_seed,
    shakedown_seed,
    shakedown_seeds,
)
from reduce_stage7b2r import REDUCER_SOURCES, _jsonable
from run_stage7b2r import FROZEN_SOURCES, decision_rule_inputs


def fmt(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


class RegisteredConfigurationTests(unittest.TestCase):
    """Repair preregistration section 3 table, value by value."""

    def test_repaired_values(self):
        self.assertEqual(REGISTERED_WINDOW_TICKS, 1200)
        self.assertEqual(REGISTERED_CENSUS_CAPACITY, 48)
        self.assertEqual(REGISTERED_PACKET_ENERGY, Fraction(900))
        self.assertEqual(REGISTERED_REPLICATE_SEED_BASE, 20261822)
        self.assertEqual(REGISTERED_REPLICATES, 32)

    def test_carried_values_unchanged(self):
        self.assertEqual(REGISTERED_BUFFER_DEPTH, 64)
        self.assertEqual(REGISTERED_HAZARD_RATE, Fraction(1, 120))
        self.assertEqual(REGISTERED_GENOTYPES, ((102, 128, 255),
                                                (204, 128, 255)))
        self.assertEqual(REGISTERED_FOUNDER_S, Fraction(100))
        self.assertEqual(REGISTERED_CORPSE_TTL, 2)
        self.assertEqual(REGISTERED_MEMORY_POOL, 65536)
        self.assertEqual(REGISTERED_PACKET_RATE, 5)

    def test_configuration_echo_matches_constants(self):
        echo = registered_configuration()
        self.assertEqual(echo["window_ticks_W"], REGISTERED_WINDOW_TICKS)
        self.assertEqual(echo["census_capacity_N"],
                         REGISTERED_CENSUS_CAPACITY)
        self.assertEqual(echo["packet_energy"], "900/1")
        self.assertEqual(echo["seed_derivation"],
                         "hazard_seed = 20261822 + i, i in 0..31")
        self.assertEqual(echo["memory_pool_bytes"], 65536)
        self.assertEqual(
            echo["supersedes"],
            "ecology parameters of docs/stage-7b2-preregistration.md"
            " per docs/stage-7b2-repair-preregistration.md section 3")

    def test_memory_pool_obligation_bound(self):
        # Section 3: N*(working+gestation) + corpse_ttl*128 <= pool.
        obligation = (REGISTERED_CENSUS_CAPACITY * (64 + 64)
                      + REGISTERED_CORPSE_TTL * 128)
        self.assertEqual(obligation, 48 * 128 + 256)
        self.assertLessEqual(obligation, REGISTERED_MEMORY_POOL)

    def test_frozen_sources_listed_once_each(self):
        self.assertEqual(len(FROZEN_SOURCES), len(set(FROZEN_SOURCES)))
        self.assertIn("stage7b2r_population.py", FROZEN_SOURCES)
        self.assertIn("stage7b1_mechanics.py", FROZEN_SOURCES)
        self.assertNotIn("stage7b2r_gate.py", FROZEN_SOURCES)
        self.assertIn("reduce_stage7b2r.py", REDUCER_SOURCES)

    def test_decision_rule_inputs_echo(self):
        inputs = decision_rule_inputs()
        self.assertEqual(inputs["solver_resolution_rho_r"],
                         fmt(SOLVER_RESOLUTION_RHO))
        self.assertEqual(inputs["minimum_contrast_delta_r_min"],
                         fmt(MIN_CONTRAST_DELTA_R))
        self.assertEqual(inputs["solver_resolution_rho_r"], "1/256")
        self.assertEqual(inputs["minimum_contrast_delta_r_min"], "1/100")
        self.assertEqual(inputs["minimum_complete_pairs"], 16)


class SeedTableTests(unittest.TestCase):
    """Section 3 confirmatory table and section 6.1 shakedown table."""

    def test_confirmatory_seeds(self):
        self.assertEqual([registered_seed(i) for i in range(32)],
                         [20261822 + i for i in range(32)])
        with self.assertRaises(ValueError):
            registered_seed(32)
        with self.assertRaises(ValueError):
            registered_seed(-1)

    def test_shakedown_seeds_fixed_before_execution(self):
        seeds = shakedown_seeds()
        self.assertEqual(len(seeds), SHAKEDOWN_SEED_COUNT)
        self.assertEqual(seeds[0], SHAKEDOWN_SEED_BASE)
        self.assertEqual(seeds[-1], SHAKEDOWN_SEED_BASE + 23)
        self.assertEqual(len(set(seeds)), len(seeds))
        self.assertEqual(shakedown_seed(0), 20270000)
        with self.assertRaises(ValueError):
            shakedown_seed(24)

    def test_tables_are_disjoint(self):
        confirmatory = {registered_seed(i) for i in range(REGISTERED_REPLICATES)}
        shakedown = set(shakedown_seeds())
        self.assertEqual(confirmatory & shakedown, set())
        # Also disjoint from the retired Stage 7B2 table.
        retired = {20260822 + i for i in range(32)}
        self.assertEqual(confirmatory & retired, set())
        self.assertEqual(shakedown & retired, set())


class SomaticEconomyArithmeticTests(unittest.TestCase):
    """Section 4 disclosure, re-derived as exact fractions."""

    @staticmethod
    def margin(a: int, d: int, packet_energy: Fraction,
               n: int = REGISTERED_CENSUS_CAPACITY) -> Fraction:
        share = Fraction(a, d)
        income = Fraction(REGISTERED_PACKET_RATE, n) * (1 - share) \
            * packet_energy
        charge = (1 - Fraction(REGISTERED_PACKET_RATE, n)) * 10
        return income - charge

    def test_registered_margins_at_repaired_ecology(self):
        self.assertEqual(self.margin(102, 255, Fraction(900)),
                         Fraction(2270, 48))
        self.assertEqual(self.margin(204, 255, Fraction(900)),
                         Fraction(470, 48))

    def test_counterfactual_old_energy_is_negative_for_thin_arm(self):
        # Section 4 counterfactual: E = 300 at N = 48 would guarantee mass
        # stalling of the A=204 arm -- the reason energy rose with N.
        self.assertLess(self.margin(204, 255, Fraction(300)), 0)

    def test_income_split_values(self):
        r_over_n = Fraction(5, 48)
        self.assertEqual(r_over_n * (1 - Fraction(102, 255)) * 900,
                         Fraction(225, 4))   # 56.25
        self.assertEqual(r_over_n * (1 - Fraction(204, 255)) * 900,
                         Fraction(75, 4))    # 18.75


class PopulationConstructionTests(unittest.TestCase):
    """Construction through the unchanged Stage 7B2 machinery."""

    def test_founder_block_layout(self):
        genomes = registered_founder_genomes()
        self.assertEqual(len(genomes), 6)
        self.assertEqual(genomes[:3], [(102, 128, 255)] * 3)
        self.assertEqual(genomes[3:], [(204, 128, 255)] * 3)

    def test_construction_closes_initial_checkpoint(self):
        population = registered_population(shakedown_seed(0))
        self.assertEqual(len(population.members), 6)
        self.assertEqual(population.capacity, 48)
        self.assertEqual(population.window_ticks, 1200)
        # Two structural "initial" checkpoints: the base constructor's
        # pre-founder assertion and the post-founder registration scan.
        self.assertEqual(len(population.closure_history), 2)
        self.assertEqual(
            [entry["operation"] for entry in population.closure_history],
            ["initial", "initial"])
        self.assertEqual(population.closure_history[-1]["live_census"], 6)
        snapshot = population.closure_history[-1]
        self.assertEqual(snapshot["reserve_lhs"], snapshot["reserve_rhs"])
        self.assertEqual(population.opening_energy, Fraction(600))


class ShortWindowIntegrationTests(unittest.TestCase):
    """Small exploratory windows only; full windows belong to the gate."""

    def test_short_window_completes_with_ledgers_closed(self):
        population = registered_population(shakedown_seed(1))
        population.window_ticks = 40
        result = run_window(population)
        self.assertEqual(result["classification"], "COMPLETE")
        self.assertEqual(result["ticks_completed"], 40)
        self.assertLessEqual(len(population.members),
                             REGISTERED_CENSUS_CAPACITY)
        snapshot = population.closure_history[-1]
        self.assertEqual(snapshot["reserve_lhs"], snapshot["reserve_rhs"])
        self.assertEqual(snapshot["live_census"], len(population.members))
        self.assertLessEqual(snapshot["buffered"],
                             REGISTERED_BUFFER_DEPTH)


class FeasibilityGateLogicTests(unittest.TestCase):
    """G1-G4 evaluation over synthetic shakedown records (pure logic)."""

    @staticmethod
    def record(seed: int, status_102: str, status_204: str,
               classification: str = "COMPLETE") -> dict:
        return {
            "hazard_seed": seed,
            "classification": classification,
            "genotype_status": {"102": status_102, "204": status_204},
        }

    def test_two_thirds_threshold(self):
        self.assertEqual(_gate_threshold(24), 16)
        self.assertEqual(_gate_threshold(25), 17)

    def test_passing_table(self):
        records = [self.record(s, "SUPERCRITICAL", "SUPERCRITICAL")
                   for s in range(20270000, 20270000 + 17)]
        records += [self.record(s, "SUBCRITICAL", "SUBCRITICAL")
                    for s in range(20270000 + 17, 20270000 + 24)]
        summary = evaluate_gate(records)
        self.assertTrue(summary["gate_passed"])
        self.assertEqual(summary["two_thirds_threshold"], 16)
        self.assertEqual(summary["G2_joint_supercritical"]["replicates"], 17)
        for genotype in ("102", "204"):
            self.assertTrue(summary["G1_per_genotype"][genotype]["passes_G1"])

    def test_g1_fails_below_threshold(self):
        records = ([self.record(s, "SUPERCRITICAL", "SUPERCRITICAL")
                    for s in range(15)]
                   + [self.record(s, "SUBCRITICAL", "SUBCRITICAL")
                      for s in range(15, 24)])
        summary = evaluate_gate(records)
        self.assertFalse(summary["gate_passed"])
        self.assertFalse(summary["G1_per_genotype"]["102"]["passes_G1"])
        self.assertFalse(summary["G2_joint_supercritical"]["passes_G2"])

    def test_asymmetric_arms_fail_joint_condition(self):
        records = [self.record(s, "SUPERCRITICAL", "SUBCRITICAL")
                   for s in range(20)]
        records += [self.record(s, "SUBCRITICAL", "SUBCRITICAL")
                    for s in range(20, 24)]
        summary = evaluate_gate(records)
        self.assertTrue(summary["G1_per_genotype"]["102"]["passes_G1"])
        self.assertFalse(summary["G1_per_genotype"]["204"]["passes_G1"])
        self.assertFalse(summary["gate_passed"])

    def test_invalid_replicate_fails_gate_regardless_of_counts(self):
        records = [self.record(s, "SUPERCRITICAL", "SUPERCRITICAL")
                   for s in range(24)]
        broken = self.record(20270000, "SUPERCRITICAL", "SUPERCRITICAL",
                             classification="INVALID_IMPLEMENTATION")
        broken["reason"] = "BUFFER_OVERFLOW"
        broken["gate_failures"] = ["G3"]
        records[0] = broken
        summary = evaluate_gate(records)
        self.assertFalse(summary["G3_no_overflow_no_invalid"]
                         ["zero_buffer_overflow"])
        self.assertFalse(summary["gate_passed"])
        self.assertEqual(len(summary["invalid_replicates"]), 1)

    def test_gate_summary_discloses_scope_and_seeds(self):
        records = [self.record(s, "SUPERCRITICAL", "SUPERCRITICAL")
                   for s in shakedown_seeds()]
        summary = evaluate_gate(records)
        self.assertEqual(summary["seeds_used"], list(shakedown_seeds()))
        self.assertIn("No fitness", summary["claim_scope"])
        self.assertEqual(summary["gate"], "stage-7b2-repair-preregistration"
                                          " section 6")


class ReducerPlumbingTests(unittest.TestCase):
    """Serialisation rules and the full R reducer path."""

    def test_jsonable_fraction_mapping(self):
        payload = {"a": Fraction(3, 4), "b": [Fraction(1, 2), 7],
                   "c": {"d": Fraction(0)}}
        self.assertEqual(
            _jsonable(payload),
            {"a": "3/4", "b": ["1/2", 7], "c": {"d": "0/1"}})

    @classmethod
    def _synthetic_raw(cls) -> dict:
        """Runner-format raw artifact from a 30-tick exploratory window.

        Unit-test scale only: neither the registered ecology's purpose nor
        its window; exercises the reducer contract end-to-end without any
        execution of the registered confirmatory configuration.
        """
        import copy

        from stage7b2_measure import (
            build_c_vector,
            cohort_genotypes,
            cohort_schedule,
            extract_vital_records,
            fmt_rat,
        )
        from stage7b2_population import Stage7B2Population
        from stage7b2_solver import certified_bracket

        window = 30
        population = Stage7B2Population(
            founder_genomes=registered_founder_genomes(),
            capacity=REGISTERED_CENSUS_CAPACITY,
            founder_s=REGISTERED_FOUNDER_S,
            memory_pool=REGISTERED_MEMORY_POOL,
            hazard_seed=shakedown_seed(2),
            hazard_rate=REGISTERED_HAZARD_RATE,
            corpse_ttl=REGISTERED_CORPSE_TTL,
            packet_rate=REGISTERED_PACKET_RATE,
            buffer_depth=REGISTERED_BUFFER_DEPTH,
            packet_energy=REGISTERED_PACKET_ENERGY,
            window_ticks=window,
        )
        result = run_window(population)
        assert result["classification"] == "COMPLETE"
        vitals = extract_vital_records(population.event_log, window)
        schedules: dict[str, dict] = {}
        certificates: dict[str, dict] = {}
        for genotype_a in cohort_genotypes(vitals):
            schedule = cohort_schedule(vitals, genotype_a)
            c_x = build_c_vector(schedule["l_x"], schedule["m_x"])
            certificate = certified_bracket(c_x)
            schedules[str(genotype_a)] = {
                "cohort_size": schedule["cohort_size"],
                "died": schedule["died"],
                "censored": schedule["censored"],
                "exposure_member_ticks": schedule["exposure_member_ticks"],
                "l_x": [fmt_rat(v) for v in schedule["l_x"]],
                "m_x": [fmt_rat(v) for v in schedule["m_x"]],
            }
            exported = {"status": certificate["status"],
                        "L0_exact": fmt_rat(certificate["L0_exact"])}
            if certificate["status"] == "SUPERCRITICAL":
                exported.update({
                    "r_lo": fmt_rat(certificate["r_lo"]),
                    "r_hi": fmt_rat(certificate["r_hi"]),
                })
            certificates[str(genotype_a)] = exported
        return {
            "protocol": "stage-7b2r-preregistration",
            "registered_configuration": {"window_ticks_W": window},
            "replicates": [{
                "replicate_index": 0,
                "hazard_seed": shakedown_seed(2),
                "classification": "COMPLETE",
                "vital_records": {
                    "members": copy.deepcopy(vitals["members"]),
                    "establishments":
                        copy.deepcopy(vitals["establishments"]),
                    "attempt_counters": dict(vitals["attempt_counters"]),
                },
                "cohort_schedules": schedules,
                "solver_certificates": certificates,
            }],
        }

    def test_round_trip_reduces_bit_exact(self):
        from reduce_stage7b2r import reduce_artifact
        raw = self._synthetic_raw()
        reduced = reduce_artifact(raw)
        self.assertNotIn("reduction", reduced)
        self.assertTrue(reduced["verification"]["recomputation_bit_exact"])
        self.assertEqual(reduced["verification"]["mismatch_count"], 0)
        self.assertEqual(reduced["verification"]["invalid_implementations"],
                         [])
        self.assertIn(reduced["outcome"]["pair_contrast_class"],
                      ("DEGENERATE_REPLICATION", "ESTABLISHED_CONTRAST",
                       "NO_ESTABLISHED_CONTRAST"))
        # Single synthetic replicate below the pair floor => degenerate.
        self.assertEqual(reduced["outcome"]["complete_pairs"] <= 1, True)

    def test_tampered_export_classifies_reduction_mismatch(self):
        from reduce_stage7b2r import reduce_artifact
        raw = self._synthetic_raw()
        raw["replicates"][0]["cohort_schedules"]["102"]["l_x"][0] = "999/1"
        reduced = reduce_artifact(raw)
        self.assertEqual(reduced.get("reduction"), "REDUCTION_MISMATCH")
        self.assertFalse(reduced["decision_applied"])
        self.assertTrue(reduced["mismatches"])

    def test_invalid_replicate_listed_not_reduced(self):
        from reduce_stage7b2r import reduce_artifact
        raw = self._synthetic_raw()
        broken = dict(raw["replicates"][0])
        broken.update({"replicate_index": 1,
                       "classification": "INVALID_IMPLEMENTATION",
                       "reason": "BUFFER_OVERFLOW"})
        raw["replicates"].append(broken)
        reduced = reduce_artifact(raw)
        self.assertEqual(reduced["verification"]["invalid_implementations"],
                         [1])
        self.assertNotIn("reduction", reduced)


if __name__ == "__main__":
    unittest.main()
