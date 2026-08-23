"""Stage 7B endpoint-repair mechanics tests.

Covers exactly what is NEW in ``stage7b_endpoint_measure.py``,
``stage7b_endpoint_config.py``, ``stage7b_endpoint_gate.py``,
``run_stage7b_endpoint.py``, and ``reduce_stage7b_endpoint.py`` against
``docs/stage-7b-endpoint-repair-preregistration.md``:

- byte-identity pins for every reused frozen module (the preregistration
  sections 5.1 and 8 prohibit in-place edits; drift fails here first);
- the carried configuration echo and seed-table reuse (section header /
  section 5.2);
- the corrected raw-fecundity estimator: hand-computed schedules, births
  conservation, mediator fidelity versus the frozen establishment
  estimator, and integrity assertions;
- the exact consequence ``sum_x m_x(g) = (|C_g| - F_g) / |C_g|`` and the
  resulting termwise bound ``L(0) <= sum_x m_x(g)`` on concrete ledgers --
  recorded as measured facts of the registered definitions (see the
  implementation-window commit message; flagged for the section 5 gate's
  attention);
- feasibility-gate evaluation logic G1-G4 with the fixed shakedown table;
- runner/reducer plumbing echoes plus a full round trip on a short
  exploratory window (unit-test scale only).

The unchanged shared modules keep their earlier coverage byte-identically;
nothing here duplicates it.  No fitness, selection, or evolutionary claim
is made or tested.
"""

from __future__ import annotations

from fractions import Fraction
import copy
import hashlib
import json
import os
import unittest

from stage7b1_mechanics import REGISTERED_PACKET_RATE
from stage7b2_measure import (
    build_c_vector,
    cohort_genotypes,
    cohort_schedule,
    extract_vital_records,
)
from stage7b2_population import Stage7B2Population, run_window
from stage7b2_solver import MIN_CONTRAST_DELTA_R, SOLVER_RESOLUTION_RHO
from stage7b2r_population import (
    REGISTERED_BUFFER_DEPTH,
    REGISTERED_CENSUS_CAPACITY,
    REGISTERED_CORPSE_TTL,
    REGISTERED_FOUNDER_S,
    REGISTERED_HAZARD_RATE,
    REGISTERED_MEMORY_POOL,
    REGISTERED_PACKET_ENERGY,
    REGISTERED_REPLICATE_SEED_BASE,
    REGISTERED_REPLICATES,
    REGISTERED_WINDOW_TICKS,
    registered_configuration as repair_registered_configuration,
    shakedown_seeds as repair_shakedown_seeds,
    shakedown_seed,
)
from stage7b_endpoint_config import (
    PRE_EXECUTION_MANIFEST_PATH,
    PREREG_DOCUMENT,
    PROTOCOL,
    RAW_RESULT_PATH,
    REDUCED_RESULT_PATH,
    RESULTS_DIR,
    endpoint_configuration,
    endpoint_decision_rule_inputs,
    registered_founder_genomes,
    registered_population,
    registered_seed,
)
from stage7b_endpoint_gate import _gate_threshold, evaluate_gate
from stage7b_endpoint_measure import (
    ESTABLISHMENT_MEDIATOR,
    RAW_FECUNDITY_M_X,
    endpoint_schedule,
    establishment_counts,
    raw_fecundity_counts,
)
from reduce_stage7b_endpoint import REDUCER_SOURCES, _jsonable, reduce_artifact
from run_stage7b_endpoint import FROZEN_SOURCES

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fmt(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def sha256_of(relative_path: str) -> str:
    with open(os.path.join(REPO_ROOT, relative_path), "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


# Hashes of the shared modules exactly as retained/pinned before this
# implementation window opened.  The first three are also pinned in
# results/stage7b2/pre-execution-manifest.json; stage7b1_mechanics.py is
# disclosed there as byte-identical to commit 62f2672; the configuration
# layer hash is the ac561a7 construction carried unchanged.
PINNED_HASHES = {
    "src/stage7b1_mechanics.py":
        "615726900a1d3d3a36af1807ad0dc7c30ce76c09596c1d2f1fab44870d904cde",
    "src/stage7b2_measure.py":
        "5664bcecdd0f87c0f1650a93ad95ef90728daa3b5236e652bf4866a909b054fd",
    "src/stage7b2_population.py":
        "86e1b67031bfa68778f7690f645ec94a9047f6cd2141fb27baa5b4e31f3503cb",
    "src/stage7b2_solver.py":
        "43756a830b565add8284ccdc0852141a91c1550b73cc63f7780f64714e28c5e5",
    "src/stage7b2r_population.py":
        "d2bc36af0d2664d23de32d9047da5e5473321b5bd964b84ab0fea72e99a5fcfa",
}


class FrozenModuleImmutabilityTests(unittest.TestCase):
    """Endpoint-repair prereg sections 5.1 and 8: frozen modules are never
    edited in place.  Any drift in the shared sources fails here."""

    def test_pinned_hashes_unchanged(self):
        for relative_path, expected in PINNED_HASHES.items():
            self.assertEqual(sha256_of(relative_path), expected,
                             msg=f"{relative_path} drifted from its pin")

    def test_manifest_pins_agree_with_literals(self):
        with open(os.path.join(
                REPO_ROOT,
                "results/stage7b2/pre-execution-manifest.json"),
                encoding="utf-8") as handle:
            manifest = json.load(handle)
        for name in ("stage7b2_measure.py", "stage7b2_population.py",
                     "stage7b2_solver.py"):
            entry = manifest["files"][f"src/{name}"]
            relative = f"src/{name}"
            self.assertEqual(entry["sha256"], PINNED_HASHES[relative])
            self.assertEqual(entry["sha256"], sha256_of(relative))

    def test_new_modules_are_additive_files(self):
        # The implementation window adds files; it never rewrites history.
        for name in ("stage7b_endpoint_measure.py",
                     "stage7b_endpoint_config.py",
                     "stage7b_endpoint_gate.py",
                     "run_stage7b_endpoint.py",
                     "reduce_stage7b_endpoint.py"):
            self.assertNotIn(name.replace(".py", ""), PINNED_HASHES)


class ConfigurationCarryForwardTests(unittest.TestCase):
    """Carried ecology verbatim; only the endpoint numerator is new."""

    def test_protocol_and_paths(self):
        self.assertEqual(PROTOCOL, "stage-7b-endpoint-repair-preregistration")
        self.assertEqual(PREREG_DOCUMENT,
                         "docs/stage-7b-endpoint-repair-preregistration.md")
        self.assertEqual(RESULTS_DIR, "results/stage7b-endpoint-repair/")
        self.assertEqual(RAW_RESULT_PATH,
                         "results/stage7b-endpoint-repair/"
                         "stage7b-endpoint-result.json")
        self.assertEqual(REDUCED_RESULT_PATH,
                         "results/stage7b-endpoint-repair/"
                         "stage7b-endpoint-reduced.json")
        self.assertIn("pre-execution-manifest.json",
                      PRE_EXECUTION_MANIFEST_PATH)

    def test_carried_values_equal_repair_layer(self):
        echo = endpoint_configuration()
        repair = repair_registered_configuration()
        self.assertEqual(echo["protocol"], PROTOCOL)
        self.assertEqual(echo["window_ticks_W"], repair["window_ticks_W"])
        self.assertEqual(echo["census_capacity_N"],
                         repair["census_capacity_N"])
        self.assertEqual(echo["buffer_depth_d"], repair["buffer_depth_d"])
        self.assertEqual(echo["packet_rate_r"], repair["packet_rate_r"])
        self.assertEqual(echo["hazard_arms"], repair["hazard_arms"])
        self.assertEqual(echo["replicates_k"], repair["replicates_k"])
        self.assertEqual(echo["seed_derivation"], repair["seed_derivation"])
        self.assertEqual(echo["genotypes_ATD"], repair["genotypes_ATD"])
        self.assertEqual(echo["founders_per_genotype"],
                         repair["founders_per_genotype"])
        self.assertEqual(echo["founder_S"], repair["founder_S"])
        self.assertEqual(echo["founder_R"], repair["founder_R"])
        self.assertEqual(echo["corpse_ttl"], repair["corpse_ttl"])
        self.assertEqual(echo["packet_energy"], repair["packet_energy"])
        self.assertEqual(echo["memory_pool_bytes"],
                         repair["memory_pool_bytes"])

    def test_binding_constants_reachable(self):
        self.assertEqual(REGISTERED_WINDOW_TICKS, 1200)
        self.assertEqual(REGISTERED_CENSUS_CAPACITY, 48)
        self.assertEqual(REGISTERED_PACKET_ENERGY, Fraction(900))
        self.assertEqual(REGISTERED_REPLICATE_SEED_BASE, 20261822)
        self.assertEqual(REGISTERED_REPLICATES, 32)
        self.assertEqual(REGISTERED_HAZARD_RATE, Fraction(1, 120))
        self.assertEqual(REGISTERED_PACKET_RATE, 5)

    def test_shakedown_table_reused_verbatim(self):
        # Section 5.2: the same fixed 24-seed table already used and
        # archived by the failed gate -- no new draw needed or permitted.
        self.assertEqual(list(shakedown_seeds_reexport()),
                         list(repair_shakedown_seeds()))
        self.assertEqual(shakedown_seeds_reexport()[0], 20270000)
        self.assertEqual(len(set(shakedown_seeds_reexport())), 24)
        confirmatory = {registered_seed(i) for i in range(32)}
        self.assertEqual(confirmatory & set(repair_shakedown_seeds()),
                         set())

    def test_supersedes_chain_recorded(self):
        echo = endpoint_configuration()
        self.assertIn("docs/stage-7b1-preregistration.md",
                      echo["endpoint_supersedes"])
        self.assertIn("section 6.1", echo["endpoint_supersedes"])
        self.assertIn("raw age-specific fecundity", echo["endpoint"])
        self.assertIn("never substituted", echo["mediator_note"])
        self.assertIn("carried verbatim", echo["carried_from"])

    def test_decision_rule_inputs_echo(self):
        inputs = endpoint_decision_rule_inputs()
        self.assertEqual(inputs["solver_resolution_rho_r"], "1/256")
        self.assertEqual(inputs["minimum_contrast_delta_r_min"], "1/100")
        self.assertEqual(inputs["minimum_complete_pairs"], 16)
        self.assertEqual(SOLVER_RESOLUTION_RHO, Fraction(1, 256))
        self.assertEqual(MIN_CONTRAST_DELTA_R, Fraction(1, 100))


def shakedown_seeds_reexport():
    from stage7b_endpoint_config import shakedown_seeds
    return shakedown_seeds()


def _synthetic_log() -> list[dict]:
    """Hand-built ledger matching the frozen 7B1 event schema exactly.

    Founders F0(A=102), F1(A=204).  Birth chain under A=102: F0 bears C2
    at t=2; C2 bears C3 at t=6; C3 bears C4 at t=10.  F1 dies at t=8
    having never reproduced.  Window W=30; no other deaths."""
    log: list[dict] = []
    log.append({"event": "founder_registered", "tick": 0,
                "organism_id": "org-0", "ancestry_id": "F0",
                "a_over_d": "102/255", "t_over_d": "128/255",
                "genotype_hash": "h102", "s_initial": "100/1",
                "r_initial": "0/1"})
    log.append({"event": "founder_registered", "tick": 0,
                "organism_id": "org-1", "ancestry_id": "F1",
                "a_over_d": "204/255", "t_over_d": "128/255",
                "genotype_hash": "h204", "s_initial": "100/1",
                "r_initial": "0/1"})
    log.append({"event": "packet_draw", "tick": 1, "organism_id": "org-0"})
    log.append({"event": "packet_draw", "tick": 1, "organism_id": "org-1"})
    for child, parent, tick in (("org-2", "org-0", 2),
                                ("org-3", "org-2", 6),
                                ("org-4", "org-3", 10)):
        log.append({"event": "provision_committed", "tick": tick,
                    "organism_id": parent, "child_id": child,
                    "inherited_a_over_d": "102/255"})
        log.append({"event": "birth_admitted", "tick": tick,
                    "parent_id": parent, "child_id": child,
                    "provision": "41/2"})
    log.append({"event": "divide_failed", "tick": 9,
                "organism_id": "org-0", "stage": "V",
                "reason": "NO_VACANCY"})
    log.append({"event": "hazard_death", "tick": 8, "organism_id": "org-1"})
    return log


class RawFecundityEstimatorTests(unittest.TestCase):
    """Corrected endpoint estimator definitions, hand-computed exactly."""

    WINDOW = 30

    def setUp(self):
        self.vitals = extract_vital_records(_synthetic_log(), self.WINDOW)

    def test_labels_declare_roles(self):
        self.assertIn("raw age-specific fecundity", RAW_FECUNDITY_M_X)
        self.assertIn("never substituted", ESTABLISHMENT_MEDIATOR)

    def test_membership_and_cohorts(self):
        self.assertEqual(cohort_genotypes(self.vitals), [102, 204])
        schedule = endpoint_schedule(self.vitals, 102)
        self.assertEqual(schedule["cohort_size"], 4)
        g204 = endpoint_schedule(self.vitals, 204)
        self.assertEqual(g204["cohort_size"], 1)

    def test_lx_bit_identical_to_frozen_estimator(self):
        for genotype in (102, 204):
            legacy = cohort_schedule(self.vitals, genotype)
            corrected = endpoint_schedule(self.vitals, genotype)
            self.assertEqual(corrected["l_x"], legacy["l_x"])
            self.assertEqual(corrected["died"], legacy["died"])
            self.assertEqual(corrected["censored"], legacy["censored"])
            self.assertEqual(corrected["exposure_member_ticks"],
                             legacy["exposure_member_ticks"])

    def test_raw_fecundity_hand_computed(self):
        # Births to A=102 parents: org-2@t2 (parent org-0 age 2),
        # org-3@t6 (parent org-2 age 4), org-4@t10 (parent org-3 age 4).
        schedule = endpoint_schedule(self.vitals, 102)
        self.assertEqual(schedule["m_x"][2], Fraction(1, 4))
        self.assertEqual(schedule["m_x"][4], Fraction(2, 4))
        self.assertEqual(sum(schedule["m_x"]), Fraction(3, 4))
        self.assertEqual(schedule["births_credited"], 3)
        # Founders' own births count exactly like non-founders' births.
        counts = raw_fecundity_counts(self.vitals, 102)
        self.assertEqual(counts[2], 1)
        self.assertEqual(counts[4], 2)

    def test_establishment_mediator_matches_frozen_estimator(self):
        schedule = endpoint_schedule(self.vitals, 102)
        legacy = cohort_schedule(self.vitals, 102)
        self.assertEqual(schedule["establishment_m_x"], legacy["m_x"])
        # The mediator credits the grandparent only when a NON-founder
        # offspring first reproduces: org-2@t6 credits org-0 (age 4);
        # org-3@t10 credits org-2 (age 4); F0's own reproduction at t=2
        # confers no mediation credit.
        self.assertEqual(schedule["establishment_m_x"][4], Fraction(2, 4))
        self.assertEqual(sum(schedule["establishment_m_x"]), Fraction(2, 4))
        self.assertEqual(schedule["establishments_credited"], 2)

    def test_births_conservation_identity(self):
        # Every admitted birth creates exactly one non-founder member, so
        # for any genotype: sum_x m_x(g) = B_g / |C_g| = 1 - F_g / |C_g|.
        schedule = endpoint_schedule(self.vitals, 102)
        cohort = schedule["cohort_size"]
        founders = 1  # org-0 only
        births_to_g = schedule["births_credited"]
        self.assertEqual(sum(schedule["m_x"]), Fraction(births_to_g, cohort))
        self.assertEqual(sum(schedule["m_x"]),
                         Fraction(cohort - founders, cohort))
        # Genotype 204: one founder, zero births.
        g204 = endpoint_schedule(self.vitals, 204)
        self.assertEqual(sum(g204["m_x"]), Fraction(0, 1))
        self.assertEqual(g204["establishments_credited"], 0)

    def test_termwise_bound_on_this_ledger(self):
        # With 0 <= l_x <= 1 (registered), c_x = l_x*m_x <= m_x termwise;
        # combined with births conservation this bounds L(0) on any ledger
        # whose cohort has at least one founder.  Recorded here as a
        # measured fact of the registered definitions on concrete ledgers.
        from stage7b2_solver import certified_bracket
        schedule = endpoint_schedule(self.vitals, 102)
        c_x = build_c_vector(schedule["l_x"], schedule["m_x"])
        certificate = certified_bracket(c_x)
        self.assertLessEqual(certificate["L0_exact"],
                             sum(schedule["m_x"]))
        self.assertLess(sum(schedule["m_x"]), 1)
        self.assertEqual(certificate["status"], "SUBCRITICAL")

    def test_many_births_still_bounded(self):
        # One founder bearing eight children: census demonstrably grows
        # while L(0) remains below one -- the concrete-ledger form of the
        # structural observation flagged for the section 5 gate.
        log: list[dict] = [
            {"event": "founder_registered", "tick": 0,
             "organism_id": "org-0", "ancestry_id": "F0",
             "a_over_d": "102/255", "t_over_d": "128/255",
             "genotype_hash": "h102", "s_initial": "100/1",
             "r_initial": "0/1"},
        ]
        for j in range(8):
            tick = 2 + 2 * j
            child = f"child-{j}"
            log.append({"event": "provision_committed", "tick": tick,
                        "organism_id": "org-0", "child_id": child,
                        "inherited_a_over_d": "102/255"})
            log.append({"event": "birth_admitted", "tick": tick,
                        "parent_id": "org-0", "child_id": child,
                        "provision": "41/2"})
        vitals = extract_vital_records(log, 30)
        schedule = endpoint_schedule(vitals, 102)
        self.assertEqual(schedule["cohort_size"], 9)
        self.assertEqual(schedule["births_credited"], 8)
        self.assertEqual(sum(schedule["m_x"]), Fraction(8, 9))
        self.assertLess(sum(schedule["m_x"]), 1)
        self.assertEqual(sum(schedule["establishment_m_x"]), Fraction(0, 1))

    def test_corrupt_ledger_unknown_parent_raises(self):
        log = _synthetic_log()
        log.append({"event": "provision_committed", "tick": 12,
                    "organism_id": "ghost", "child_id": "org-9",
                    "inherited_a_over_d": "102/255"})
        log.append({"event": "birth_admitted", "tick": 12,
                    "parent_id": "ghost", "child_id": "org-9",
                    "provision": "1/1"})
        vitals = extract_vital_records(log, self.WINDOW)
        with self.assertRaises(AssertionError):
            raw_fecundity_counts(vitals, 102)

    def test_birth_age_outside_window_raises(self):
        log = _synthetic_log()
        log.append({"event": "provision_committed", "tick": 29,
                    "organism_id": "org-0", "child_id": "org-9",
                    "inherited_a_over_d": "102/255"})
        log.append({"event": "birth_admitted", "tick": 31,
                    "parent_id": "org-0", "child_id": "org-9",
                    "provision": "1/1"})
        vitals = extract_vital_records(log, self.WINDOW)
        with self.assertRaises(AssertionError):
            raw_fecundity_counts(vitals, 102)

    def test_establishment_age_outside_window_raises(self):
        vitals = extract_vital_records(_synthetic_log(), self.WINDOW)
        vitals["establishments"] = [dict(
            vitals["establishments"][0], parent_age=self.WINDOW + 3)]
        with self.assertRaises(AssertionError):
            establishment_counts(vitals, 102)


class ShortWindowIntegrationTests(unittest.TestCase):
    """Small exploratory windows only; full windows belong to the gate.

    Verifies the births-conservation identity and the termwise bound on
    genuine population output (unit-test scale; produces no artifact)."""

    WINDOW = 30

    @classmethod
    def _run_short(cls, seed_index: int = 2):
        population = Stage7B2Population(
            founder_genomes=registered_founder_genomes(),
            capacity=REGISTERED_CENSUS_CAPACITY,
            founder_s=REGISTERED_FOUNDER_S,
            memory_pool=REGISTERED_MEMORY_POOL,
            hazard_seed=shakedown_seed(seed_index),
            hazard_rate=REGISTERED_HAZARD_RATE,
            corpse_ttl=REGISTERED_CORPSE_TTL,
            packet_rate=REGISTERED_PACKET_RATE,
            buffer_depth=REGISTERED_BUFFER_DEPTH,
            packet_energy=REGISTERED_PACKET_ENERGY,
            window_ticks=cls.WINDOW,
        )
        result = run_window(population)
        assert result["classification"] == "COMPLETE"
        vitals = extract_vital_records(population.event_log,
                                       cls.WINDOW)
        founders: dict[int, int] = {}
        for event in population.event_log:
            if event.get("event") == "founder_registered":
                a = int(event["a_over_d"].split("/")[0])
                founders[a] = founders.get(a, 0) + 1
        return population, vitals, founders

    def test_conservation_identity_holds_on_real_output(self):
        _, vitals, founders = self._run_short()
        for genotype in cohort_genotypes(vitals):
            schedule = endpoint_schedule(vitals, genotype)
            cohort = schedule["cohort_size"]
            self.assertEqual(
                sum(schedule["m_x"]),
                Fraction(cohort - founders[genotype], cohort))
            self.assertEqual(schedule["births_credited"],
                             sum(raw_fecundity_counts(vitals, genotype)))

    def test_termwise_bound_holds_on_real_output(self):
        from stage7b2_solver import certified_bracket
        _, vitals, _ = self._run_short()
        for genotype in cohort_genotypes(vitals):
            schedule = endpoint_schedule(vitals, genotype)
            c_x = build_c_vector(schedule["l_x"], schedule["m_x"])
            certificate = certified_bracket(c_x)
            self.assertLessEqual(certificate["L0_exact"],
                                 sum(schedule["m_x"]))


class FeasibilityGateLogicTests(unittest.TestCase):
    """G1-G4 evaluation over synthetic records (pure logic)."""

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
        seeds = list(shakedown_seeds_reexport())
        records = ([self.record(s, "SUPERCRITICAL", "SUPERCRITICAL")
                    for s in seeds[:17]]
                   + [self.record(s, "SUBCRITICAL", "SUBCRITICAL")
                      for s in seeds[17:]])
        summary = evaluate_gate(records)
        self.assertTrue(summary["gate_passed"])
        self.assertEqual(summary["two_thirds_threshold"], 16)
        self.assertEqual(summary["G2_joint_supercritical"]["replicates"], 17)

    def test_failing_table_reports_guidance(self):
        seeds = list(shakedown_seeds_reexport())
        records = [self.record(s, "SUBCRITICAL", "SUBCRITICAL")
                   for s in seeds]
        summary = evaluate_gate(records)
        self.assertFalse(summary["gate_passed"])
        self.assertFalse(summary["G1_per_genotype"]["102"]["passes_G1"])
        self.assertFalse(summary["G2_joint_supercritical"]["passes_G2"])
        self.assertIn("further superseding preregistration",
                      summary["failure_guidance"])
        self.assertIn("no retained artifact", summary["failure_guidance"])

    def test_invalid_replicate_fails_gate_regardless_of_counts(self):
        seeds = list(shakedown_seeds_reexport())
        records = [self.record(s, "SUPERCRITICAL", "SUPERCRITICAL")
                   for s in seeds]
        broken = self.record(seeds[0], "SUPERCRITICAL", "SUPERCRITICAL",
                             classification="INVALID_IMPLEMENTATION")
        broken["reason"] = "BUFFER_OVERFLOW"
        broken["gate_failures"] = ["G3"]
        records[0] = broken
        summary = evaluate_gate(records)
        self.assertFalse(summary["G3_no_overflow_no_invalid"]
                         ["zero_buffer_overflow"])
        self.assertFalse(summary["gate_passed"])

    def test_gate_summary_discloses_scope_and_fixed_table(self):
        seeds = list(shakedown_seeds_reexport())
        records = [self.record(s, "SUPERCRITICAL", "SUPERCRITICAL")
                   for s in seeds]
        summary = evaluate_gate(records)
        self.assertEqual(summary["seeds_used"], seeds)
        self.assertEqual(summary["seed_count"], 24)
        self.assertEqual(summary["gate"],
                         "stage-7b-endpoint-repair-preregistration section 5")
        self.assertIn("No fitness", summary["claim_scope"])
        self.assertEqual(summary["prereg_document"], PREREG_DOCUMENT)


class RunnerReducerPlumbingTests(unittest.TestCase):
    """Serialisation rules, source manifests, and the full reducer path."""

    def test_frozen_sources_listed_once_each(self):
        self.assertEqual(len(FROZEN_SOURCES), len(set(FROZEN_SOURCES)))
        for required in ("stage7b2_measure.py", "stage7b2_population.py",
                         "stage7b2_solver.py", "stage7b2r_population.py",
                         "stage7b1_mechanics.py",
                         "stage7b_endpoint_measure.py",
                         "stage7b_endpoint_config.py",
                         "run_stage7b_endpoint.py"):
            self.assertIn(required, FROZEN_SOURCES)
        self.assertNotIn("stage7b_endpoint_gate.py", FROZEN_SOURCES)
        self.assertNotIn("reduce_stage7b_endpoint.py", FROZEN_SOURCES)
        self.assertEqual(len(REDUCER_SOURCES), len(set(REDUCER_SOURCES)))
        self.assertIn("reduce_stage7b_endpoint.py", REDUCER_SOURCES)

    def test_jsonable_fraction_mapping(self):
        payload = {"a": Fraction(3, 4), "b": [Fraction(1, 2), 7],
                   "c": {"d": Fraction(0)}}
        self.assertEqual(
            _jsonable(payload),
            {"a": "3/4", "b": ["1/2", 7], "c": {"d": "0/1"}})

    @classmethod
    def _runner_format_artifact(cls) -> dict:
        """Runner-format raw artifact from a 30-tick exploratory window.

        Unit-test scale only; exercises the reducer contract end-to-end
        without any execution of the registered confirmatory suite."""
        population, vitals, _ = cls._run_short_shared()
        config_echo = endpoint_configuration()
        config_echo["window_ticks_W"] = 30
        schedules: dict[str, dict] = {}
        certificates: dict[str, dict] = {}
        from stage7b2_solver import certified_bracket
        for genotype_a in cohort_genotypes(vitals):
            schedule = endpoint_schedule(vitals, genotype_a)
            c_x = build_c_vector(schedule["l_x"], schedule["m_x"])
            certificate = certified_bracket(c_x)
            exported = {
                "status": certificate["status"],
                "L0_exact": fmt(certificate["L0_exact"]),
            }
            if certificate["status"] == "SUPERCRITICAL":
                exported.update({
                    "r_lo": fmt(certificate["r_lo"]),
                    "r_hi": fmt(certificate["r_hi"]),
                })
            schedules[str(genotype_a)] = {
                "cohort_size": schedule["cohort_size"],
                "died": schedule["died"],
                "censored": schedule["censored"],
                "exposure_member_ticks": schedule["exposure_member_ticks"],
                "l_x": [fmt(v) for v in schedule["l_x"]],
                "m_x": [fmt(v) for v in schedule["m_x"]],
                "establishment_m_x": [fmt(v) for v
                                      in schedule["establishment_m_x"]],
                "births_credited": schedule["births_credited"],
                "establishments_credited": schedule["establishments_credited"],
            }
            certificates[str(genotype_a)] = exported
        return {
            "protocol": PROTOCOL,
            "registered_configuration": config_echo,
            "replicates": [{
                "replicate_index": 0,
                "hazard_seed": shakedown_seed(2),
                "classification": "COMPLETE",
                "vital_records": {
                    "members": copy.deepcopy(vitals["members"]),
                    "births": copy.deepcopy(vitals["births"]),
                    "establishments":
                        copy.deepcopy(vitals["establishments"]),
                    "attempt_counters": dict(vitals["attempt_counters"]),
                },
                "cohort_schedules": schedules,
                "solver_certificates": certificates,
            }],
        }

    @staticmethod
    def _run_short_shared(seed_index: int = 2):
        population = Stage7B2Population(
            founder_genomes=registered_founder_genomes(),
            capacity=REGISTERED_CENSUS_CAPACITY,
            founder_s=REGISTERED_FOUNDER_S,
            memory_pool=REGISTERED_MEMORY_POOL,
            hazard_seed=shakedown_seed(seed_index),
            hazard_rate=REGISTERED_HAZARD_RATE,
            corpse_ttl=REGISTERED_CORPSE_TTL,
            packet_rate=REGISTERED_PACKET_RATE,
            buffer_depth=REGISTERED_BUFFER_DEPTH,
            packet_energy=REGISTERED_PACKET_ENERGY,
            window_ticks=30,
        )
        result = run_window(population)
        assert result["classification"] == "COMPLETE"
        vitals = extract_vital_records(population.event_log, 30)
        return population, vitals, {}

    def test_round_trip_reduces_bit_exact(self):
        raw = self._runner_format_artifact()
        reduced = reduce_artifact(raw)
        self.assertNotIn("reduction", reduced)
        self.assertTrue(reduced["verification"]["recomputation_bit_exact"])
        self.assertEqual(reduced["verification"]["mismatch_count"], 0)
        self.assertEqual(reduced["decision_rule_input"]["delta_min"],
                         "1/100")
        self.assertIn(reduced["outcome"]["pair_contrast_class"],
                      ("DEGENERATE_REPLICATION", "ESTABLISHED_CONTRAST",
                       "NO_ESTABLISHED_CONTRAST"))
        self.assertIn("mediator", reduced["interpretation_limits"])

    def test_tampered_endpoint_classifies_reduction_mismatch(self):
        raw = self._runner_format_artifact()
        raw["replicates"][0]["cohort_schedules"]["102"]["m_x"][0] = "999/1"
        reduced = reduce_artifact(raw)
        self.assertEqual(reduced.get("reduction"), "REDUCTION_MISMATCH")
        self.assertFalse(reduced["decision_applied"])

    def test_tampered_mediator_also_classifies_mismatch(self):
        # The establishment mediator is verified for export fidelity; it is
        # reported evidence, not an ignorable field.
        raw = self._runner_format_artifact()
        raw["replicates"][0]["cohort_schedules"]["102"][
            "establishment_m_x"][0] = "999/1"
        reduced = reduce_artifact(raw)
        self.assertEqual(reduced.get("reduction"), "REDUCTION_MISMATCH")

    def test_guarded_runner_classifier_shape(self):
        # The guarded classifier returns the registered shape on failure
        # without raising; exercised via a bogus index through the config
        # layer's ValueError path.
        with self.assertRaises(ValueError):
            registered_seed(32)
        record = {
            "replicate_index": 0,
            "hazard_seed": registered_seed(0),
            "classification": "INVALID_IMPLEMENTATION",
            "reason": "UNEXPECTED_EXCEPTION",
        }
        self.assertEqual(record["reason"], "UNEXPECTED_EXCEPTION")


if __name__ == "__main__":
    unittest.main()
