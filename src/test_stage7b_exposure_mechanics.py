"""Stage 7B two-factor endpoint mechanics tests.

Covers exactly what is NEW in ``stage7b_exposure_measure.py``,
``stage7b_exposure_config.py``, and ``stage7b_exposure_gate.py`` against
``docs/stage-7b-denominator-repair-preregistration.md``:

- byte-identity pins for every reused frozen module (inherited verbatim
  from the endpoint-repair test matrix; drift fails here first);
- the configuration echo, retained paths, supersession chain, shakedown
  table reuse, and decision-rule constants;
- the repaired two-factor estimator: hand-computed exposure denominators,
  deaths-by-age, actuarial survivorship, fecundity rates, and endpoint
  coefficients; all binding identities; loud failure on violation;
- the COLLAPSE REGRESSION: with the frozen descriptive ``l_x`` as the
  survivorship factor, the product ``l_x * (n_x/E_x)`` equals ``n_x/|C_g|``
  term-for-term on a concrete growing ledger -- the recorded fact that
  makes the risk-set actuarial factor ``l^A`` necessary (prereg Lemma C);
- supercriticality REACHABILITY: a deterministic synthetic ledger with
  juvenile mortality and sustained net growth on which the repaired
  endpoint certifies ``L(0) > 1`` -- the property Theorem B proved
  impossible under both scalar-normalised predecessor endpoints --
  verified against an independent first-principles oracle;
- feasibility-gate evaluation logic G1-G4 with the fixed shakedown table.

The unchanged shared modules keep their earlier coverage byte-identically;
nothing here duplicates it.  No fitness, selection, or evolutionary claim
is made or tested.
"""

from __future__ import annotations

from fractions import Fraction
import copy
import unittest

from stage7b2_measure import (
    build_c_vector,
    cohort_schedule,
    extract_vital_records,
)
from stage7b2_solver import MIN_CONTRAST_DELTA_R, SOLVER_RESOLUTION_RHO
from stage7b2r_population import (
    REGISTERED_REPLICATE_SEED_BASE,
    registered_configuration as repair_registered_configuration,
    shakedown_seeds as repair_shakedown_seeds,
)
from stage7b_exposure_config import (
    PRE_EXECUTION_MANIFEST_PATH,
    PREREG_DOCUMENT,
    PROTOCOL,
    RAW_RESULT_PATH,
    REDUCED_RESULT_PATH,
    RESULTS_DIR,
    endpoint_configuration,
    endpoint_decision_rule_inputs,
)
from stage7b_exposure_gate import _gate_threshold, evaluate_gate
from stage7b_exposure_measure import (
    ACTUARIAL_SURVIVORSHIP,
    EXPOSURE_FECUNDITY_M_X,
    ZERO_EXPOSURE_CONVENTION,
    actuarial_survivorship,
    deaths_by_age,
    exposure_denominators,
    exposure_schedule,
    lotka_coefficients,
)
from stage7b_endpoint_gate import evaluate_gate as legacy_evaluate_gate
from stage7b_endpoint_measure import endpoint_schedule, raw_fecundity_counts
from test_stage7b_endpoint_mechanics import (
    PINNED_HASHES,
    _synthetic_log,
    fmt,
    sha256_of,
)


def _synthetic_vitals():
    return extract_vital_records(_synthetic_log(), 30)


class FrozenModuleImmutabilityTests(unittest.TestCase):
    """Denominator-repair prereg Authorisation/section 8: frozen modules
    are never edited in place; the new window only adds files."""

    def test_pinned_hashes_unchanged(self):
        for relative_path, expected in PINNED_HASHES.items():
            self.assertEqual(sha256_of(relative_path), expected,
                             msg=f"{relative_path} drifted from its pin")

    def test_new_modules_are_additive_files(self):
        for name in ("stage7b_exposure_measure.py",
                     "stage7b_exposure_config.py",
                     "stage7b_exposure_gate.py",
                     "test_stage7b_exposure_mechanics.py"):
            self.assertNotIn(name.replace(".py", ""), PINNED_HASHES)

    def test_committed_endpoint_repair_window_untouched(self):
        # The defective-generation modules remain as committed evidence;
        # they are neither edited nor deleted by this window (prereg s8).
        self.assertNotIn("stage7b_endpoint_measure", PINNED_HASHES)
        vitals = _synthetic_vitals()
        legacy = endpoint_schedule(vitals, 102)
        repaired = exposure_schedule(vitals, 102)
        # Numerators agree bit-exactly; the denominator layer is new:
        # person-ticks thin with age while a scalar headcount would not.
        self.assertEqual(repaired["births_credited"],
                         legacy["births_credited"])
        self.assertEqual(repaired["e_x"][-1], 1)  # founder alone attains 30
        self.assertLess(repaired["e_x"][-1], repaired["cohort_size"])
        self.assertEqual(sum(repaired["e_x"]),
                         repaired["exposure_member_ticks"])


class ConfigurationCarryForwardTests(unittest.TestCase):
    """Carried ecology verbatim; only the coefficient assembly is new."""

    def test_protocol_and_paths(self):
        self.assertEqual(PROTOCOL,
                         "stage-7b-denominator-repair-preregistration")
        self.assertEqual(PREREG_DOCUMENT,
                         "docs/stage-7b-denominator-repair-preregistration.md")
        self.assertEqual(RESULTS_DIR, "results/stage7b-exposure-endpoint/")
        self.assertEqual(RAW_RESULT_PATH,
                         "results/stage7b-exposure-endpoint/"
                         "stage7b-exposure-result.json")
        self.assertEqual(REDUCED_RESULT_PATH,
                         "results/stage7b-exposure-endpoint/"
                         "stage7b-exposure-reduced.json")
        self.assertIn("pre-execution-manifest.json",
                      PRE_EXECUTION_MANIFEST_PATH)

    def test_carried_values_equal_repair_layer(self):
        echo = endpoint_configuration()
        repair = repair_registered_configuration()
        for key in ("window_ticks_W", "census_capacity_N", "buffer_depth_d",
                    "packet_rate_r", "hazard_arms", "replicates_k",
                    "seed_derivation", "genotypes_ATD",
                    "founders_per_genotype", "founder_S", "founder_R",
                    "corpse_ttl", "packet_energy", "memory_pool_bytes"):
            self.assertEqual(echo[key], repair[key], msg=key)

    def test_binding_constants_reachable(self):
        self.assertEqual(REGISTERED_REPLICATE_SEED_BASE, 20261822)
        self.assertEqual(SOLVER_RESOLUTION_RHO, Fraction(1, 256))
        self.assertEqual(MIN_CONTRAST_DELTA_R, Fraction(1, 100))

    def test_shakedown_table_reused_third_time(self):
        seeds = list(repair_shakedown_seeds())
        self.assertEqual(seeds[0], 20270000)
        self.assertEqual(len(set(seeds)), 24)
        echo = endpoint_configuration()
        self.assertIn("all three gate generations", echo["shakedown_table"])

    def test_supersedes_chain_and_identities_recorded(self):
        echo = endpoint_configuration()
        self.assertIn("stage-7b-endpoint-repair-preregistration.md",
                      echo["endpoint_supersedes"])
        self.assertIn("c_x = l^A_x * m^E_x", echo["endpoint"])
        self.assertEqual(len(echo["binding_identities"]), 5)
        self.assertIn("never substituted", echo["mediator_note"])

    def test_decision_rule_inputs_echo(self):
        inputs = endpoint_decision_rule_inputs()
        self.assertEqual(inputs["solver_resolution_rho_r"], "1/256")
        self.assertEqual(inputs["minimum_contrast_delta_r_min"], "1/100")
        self.assertEqual(inputs["minimum_complete_pairs"], 16)


class TwoFactorEstimatorTests(unittest.TestCase):
    """Repaired estimator definitions, hand-computed exactly (W=30 log)."""

    @classmethod
    def setUpClass(cls):
        cls.vitals = _synthetic_vitals()

    def test_labels_declare_roles(self):
        self.assertIn("person-ticks lived at exact age x",
                      EXPOSURE_FECUNDITY_M_X)
        self.assertIn("risk-set survivorship", ACTUARIAL_SURVIVORSHIP)
        self.assertIn("exactly 0", ZERO_EXPOSURE_CONVENTION)

    def test_exposure_hand_computed(self):
        # Genotype 102: org-0 (founder, alive through W), org-2 (born 2),
        # org-3 (born 6), org-4 (born 10); no deaths.  Person-ticks at
        # exact age x = count attaining x:
        #   x in [0,20] -> 4; [21,24] -> 3; [25,28] -> 2; [29,30] -> 1.
        schedule = exposure_schedule(self.vitals, 102)
        e_x = schedule["e_x"]
        self.assertEqual(e_x[0], 4)
        self.assertEqual(e_x[20], 4)
        self.assertEqual(e_x[21], 3)
        self.assertEqual(e_x[24], 3)
        self.assertEqual(e_x[25], 2)
        self.assertEqual(e_x[28], 2)
        self.assertEqual(e_x[29], 1)
        self.assertEqual(e_x[30], 1)
        # Binding identity (i): partition equals frozen descriptive total.
        self.assertEqual(schedule["person_ticks_credited"],
                         schedule["exposure_member_ticks"])
        self.assertEqual(schedule["person_ticks_credited"], 106)

    def test_deaths_and_actuarial_hand_computed_no_deaths(self):
        # Genotype 102 has zero in-window deaths: d_x identically 0, all
        # four members right-censored, l^A identically 1.
        d_x, censored = deaths_by_age(self.vitals, 102)
        self.assertEqual(d_x, [0] * 31)
        self.assertEqual(censored, 4)
        schedule = exposure_schedule(self.vitals, 102)
        self.assertEqual(schedule["l_actuarial_x"], [Fraction(1)] * 31)
        # Binding identity (iv).
        self.assertEqual(sum(schedule["d_x"]) + schedule["censored"],
                         schedule["cohort_size"])

    def test_deaths_and_actuarial_hand_computed_one_death(self):
        # Genotype 204: single founder org-1 died at t=8 (attained age 8).
        d_x, censored = deaths_by_age(self.vitals, 204)
        self.assertEqual(d_x[8], 1)
        self.assertEqual(sum(d_x), 1)
        self.assertEqual(censored, 0)
        schedule = exposure_schedule(self.vitals, 204)
        self.assertEqual(schedule["e_x"][:9], [1] * 9)
        self.assertEqual(schedule["e_x"][9:], [0] * 22)
        self.assertEqual(schedule["person_ticks_credited"], 9)
        # l^A survives ages 0..8 then vanishes: the transition out of
        # age 8 spends its only risk-set member.
        self.assertEqual(schedule["l_actuarial_x"][:9], [Fraction(1)] * 9)
        self.assertEqual(schedule["l_actuarial_x"][9:], [Fraction(0)] * 22)

    def test_fecundity_hand_computed(self):
        # Births to A=102 parents at parent age 2 (one) and age 4 (two);
        # no deaths at those ages, so l^A = 1 there and the endpoint
        # coefficients equal the raw per-person-tick rates exactly.
        schedule = exposure_schedule(self.vitals, 102)
        self.assertEqual(schedule["m_exposure_x"][2], Fraction(1, 4))
        self.assertEqual(schedule["m_exposure_x"][4], Fraction(2, 4))
        c_x = lotka_coefficients(schedule)
        self.assertEqual(c_x[2], Fraction(1, 4))
        self.assertEqual(c_x[4], Fraction(2, 4))
        self.assertEqual(sum(c_x.values()), Fraction(3, 4))

    def test_zero_births_genotype_gives_empty_support(self):
        schedule = exposure_schedule(self.vitals, 204)
        self.assertEqual(lotka_coefficients(schedule), {})
        self.assertEqual(schedule["establishments_credited"], 0)

    def test_lx_bit_identical_to_frozen_estimator(self):
        for genotype in (102, 204):
            legacy = cohort_schedule(self.vitals, genotype)
            repaired = exposure_schedule(self.vitals, genotype)
            self.assertEqual(repaired["l_x"], legacy["l_x"])
            self.assertEqual(repaired["died"], legacy["died"])
            self.assertEqual(repaired["censored"], legacy["censored"])
            self.assertEqual(repaired["exposure_member_ticks"],
                             legacy["exposure_member_ticks"])

    def test_establishment_mediator_unchanged(self):
        for genotype in (102, 204):
            schedule = exposure_schedule(self.vitals, genotype)
            legacy = cohort_schedule(self.vitals, genotype)
            self.assertEqual(schedule["establishment_m_x"], legacy["m_x"])
        schedule = exposure_schedule(self.vitals, 102)
        self.assertEqual(schedule["establishments_credited"], 2)

    def test_exposure_recovery_rejects_inconsistent_cohort(self):
        vitals = _synthetic_vitals()
        vitals["members"]["org-0"]["genotype_a"] = None
        # An inconsistent hand-built legacy forces the non-integer guard.
        bad_legacy = {"cohort_size": 4,
                      "l_x": [Fraction(3, 8)] + [Fraction(0)] * 30,
                      "exposure_member_ticks": 999}
        with self.assertRaises(AssertionError):
            exposure_denominators(vitals, 102, bad_legacy)

    def test_births_exceeding_person_ticks_fail_loudly(self):
        vitals = _synthetic_vitals()
        # Four extra admitted births credited to org-0 (A=102) at its age
        # 2, with fabricated member stubs born at tick 30 (so they attain
        # only age 0 and never inflate E_2).  E_2(A=102) = 4 < n_2 = 5
        # must trip binding identity (iii).
        for j in range(4):
            child = f"fake-{j}"
            vitals["members"][child] = {"genotype_a": 102,
                                        "born_tick": 30,
                                        "death_tick": None}
            vitals["births"].append({"child_id": child,
                                     "parent_id": "org-0",
                                     "tick": 2,
                                     "genotype_a": 102,
                                     "provision": "1/1"})
        with self.assertRaises(AssertionError):
            exposure_schedule(vitals, 102)


def _cascade_ledger(juvenile_mod: int = 4,
                    maturation_ages=(2, 4),
                    juvenile_death_age: int = 1,
                    adult_death_age: int = 6,
                    reproduction_cutoff: int = 24,
                    window: int = 24):
    """Deterministic growing-population ledger with juvenile mortality.

    Every member bears one child at each maturation age (while alive;
    reproduction runs to the window edge so only the final stragglers
    miss a birth); every ``juvenile_mod``-th indexed newborn dies at age
    1, survivors die at age 6.  Net replacement per capita is
    2 x 3/4 = 1.5 > 1, so the population genuinely grows -- with juvenile
    deaths placed BEFORE the maturation ages so person-ticks at
    reproductive ages are thinned relative to births.  Returns the event
    log.
    """
    log = [{"event": "founder_registered", "tick": 0,
            "organism_id": "org-0", "ancestry_id": "F0",
            "a_over_d": "102/255", "t_over_d": "128/255",
            "genotype_hash": "h102", "s_initial": "100/1",
            "r_initial": "0/1"}]
    born = {"org-0": 0}
    counter = 1

    def dies_juvenile(oid: str) -> bool:
        return oid != "org-0" and int(oid.split("-")[1]) % juvenile_mod == 0

    # Chronological simulation: whether a member is dead at any tick is a
    # pure function of its birth tick, so juvenile culls (age 1) precede
    # every maturation age and culled newborns never bear.
    by_birth: dict[int, list[str]] = {0: ["org-0"]}
    for tick in range(0, reproduction_cutoff + 1):
        for mother_age in sorted(maturation_ages):
            for parent in by_birth.get(tick - mother_age, []):
                if dies_juvenile(parent) and tick >= born[parent] + 1:
                    continue
                child = f"org-{counter}"
                counter += 1
                log.append({"event": "provision_committed", "tick": tick,
                            "organism_id": parent, "child_id": child,
                            "inherited_a_over_d": "102/255"})
                log.append({"event": "birth_admitted", "tick": tick,
                            "parent_id": parent, "child_id": child,
                            "provision": "41/2"})
                born[child] = tick
                by_birth.setdefault(tick, []).append(child)
    # Deaths are deterministic functions of birth ticks; emitted in birth
    # order (ticks disambiguate any ordering question in the extraction).
    for oid, b in sorted(born.items()):
        day = b + (juvenile_death_age if dies_juvenile(oid)
                   else adult_death_age)
        if day <= window:
            log.append({"event": "hazard_death", "tick": day,
                        "organism_id": oid})
    return log


def _oracle_l0(log: list[dict], window: int) -> Fraction:
    """First-principles recomputation of L(0) from the raw events alone."""
    born: dict[str, int] = {}
    dead: dict[str, int] = {}
    n_x = [0] * (window + 1)
    for event in log:
        kind = event["event"]
        if kind == "founder_registered":
            born[event["organism_id"]] = 0
        elif kind == "birth_admitted":
            child = event["child_id"]
            born[child] = int(event["tick"])
            n_x[int(event["tick"]) - born[event["parent_id"]]] += 1
        elif kind == "hazard_death":
            dead[event["organism_id"]] = int(event["tick"])
    cohort = sorted(born)
    size = len(cohort)
    l_counts = [0] * (window + 1)
    d_x = [0] * (window + 1)
    for oid in cohort:
        last_age = ((dead[oid] if oid in dead else window) - born[oid])
        for x in range(0, min(last_age, window) + 1):
            l_counts[x] += 1
        if oid in dead:
            d_x[last_age] += 1
    l_a = [Fraction(1)]
    for x in range(window):
        if l_counts[x] == 0:
            l_a.append(Fraction(0))
        else:
            l_a.append(l_a[-1] * Fraction(l_counts[x] - d_x[x],
                                          l_counts[x]))
    total = Fraction(0)
    for x in range(window + 1):
        if l_counts[x] and n_x[x]:
            total += l_a[x] * Fraction(n_x[x], l_counts[x])
    return total


class CollapseRegressionTests(unittest.TestCase):
    """Lemma C recorded on a concrete ledger: with the frozen descriptive
    ``l_x`` as survivorship factor, ``l_x * (n_x/E_x) == n_x/|C_g|``
    term-for-term -- the shared-denominator collapse that makes the
    risk-set actuarial factor necessary.  Concrete ledgers only."""

    @classmethod
    def setUpClass(cls):
        cls.WINDOW = 24
        cls.log = _cascade_ledger(window=cls.WINDOW)
        cls.vitals = extract_vital_records(cls.log, cls.WINDOW)
        cls.schedule = exposure_schedule(cls.vitals, 102)

    def test_naive_two_factor_form_collapses_to_scalar(self):
        naive = build_c_vector(self.schedule["l_x"],
                               self.schedule["m_exposure_x"])
        cohort = self.schedule["cohort_size"]
        counts = raw_fecundity_counts(self.vitals, 102)
        scalar = {x: Fraction(counts[x], cohort)
                  for x in range(len(counts)) if counts[x]}
        self.assertEqual(naive, scalar)
        self.assertEqual(sum(naive.values()),
                         Fraction(cohort - 1, cohort))

    def test_repaired_factors_are_independent_curves(self):
        # The registered factors are NOT rescalings of one denominator:
        # l^A conditions on death risk sets, m^E on person-ticks.
        l_a = self.schedule["l_actuarial_x"]
        e_x = self.schedule["e_x"]
        self.assertEqual(l_a[0], Fraction(1))
        self.assertLess(l_a[self.WINDOW - 1], Fraction(1))
        self.assertNotEqual(
            [l_a[x] * self.schedule["cohort_size"]
             for x in range(self.WINDOW)],
            e_x[:self.WINDOW],
            "actuarial survivorship must not be a cohort-size rescaling "
            "of the exposure vector")


class SupercriticalReachabilityTests(unittest.TestCase):
    """The property both scalar-normalised predecessors lacked by proof.

    On a growing ledger with juvenile mortality, the repaired endpoint
    certifies L(0) > 1 while both predecessor endpoints certify
    subcriticality on the SAME ledger, and the module agrees bit-exactly
    with an independent first-principles oracle.  Concrete ledgers only;
    no universal claim is encoded.
    """

    WINDOW = 24

    @classmethod
    def setUpClass(cls):
        cls.log = _cascade_ledger(window=cls.WINDOW)
        cls.vitals = extract_vital_records(cls.log, cls.WINDOW)

    def test_ledger_actually_grows_with_juvenile_mortality(self):
        founders = sum(1 for event in self.log
                       if event["event"] == "founder_registered")
        schedule = exposure_schedule(self.vitals, 102)
        cohort = schedule["cohort_size"]
        births = schedule["births_credited"]
        self.assertEqual(births, cohort - founders)
        self.assertGreater(births, founders,
                           "ledger must show genuine net growth")
        # Juvenile mortality actually thins reproductive-age person-ticks.
        self.assertLess(schedule["e_x"][2], cohort)
        self.assertLess(schedule["e_x"][4], cohort)

    def test_module_matches_first_principles_oracle(self):
        from stage7b2_solver import certified_bracket
        schedule = exposure_schedule(self.vitals, 102)
        certificate = certified_bracket(lotka_coefficients(schedule))
        oracle = _oracle_l0(self.log, self.WINDOW)
        self.assertEqual(fmt(certificate["L0_exact"]), fmt(oracle))
        self.assertEqual(certificate["status"], "SUPERCRITICAL")

    def test_supercritical_reached_where_predecessors_cannot(self):
        from stage7b2_solver import certified_bracket
        schedule = exposure_schedule(self.vitals, 102)
        cohort = schedule["cohort_size"]
        certificate = certified_bracket(lotka_coefficients(schedule))
        self.assertEqual(certificate["status"], "SUPERCRITICAL")
        self.assertGreater(certificate["L0_exact"], 1)
        # Predecessor 1: raw-fecundity scalar-cohort endpoint (the exact
        # committed generation this prereg supersedes).
        legacy = endpoint_schedule(self.vitals, 102)
        c_scalar = build_c_vector(legacy["l_x"], legacy["m_x"])
        self.assertEqual(certified_bracket(c_scalar)["status"],
                         "SUBCRITICAL")
        # Predecessor 2: establishment-filtered original (mediator here).
        c_med = build_c_vector(schedule["l_x"],
                               schedule["establishment_m_x"])
        self.assertEqual(certified_bracket(c_med)["status"], "SUBCRITICAL")
        # Both sit under the structural ceiling 1 - F/|C|.
        self.assertLess(Fraction(cohort - 1, cohort), 1)


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
        seeds = list(repair_shakedown_seeds())
        records = ([self.record(s, "SUPERCRITICAL", "SUPERCRITICAL")
                    for s in seeds[:17]]
                   + [self.record(s, "SUBCRITICAL", "SUBCRITICAL")
                      for s in seeds[17:]])
        summary = evaluate_gate(records)
        self.assertTrue(summary["gate_passed"])
        self.assertEqual(summary["gate"],
                         "stage-7b-denominator-repair-preregistration"
                         " section 5")

    def test_failing_table_reports_new_guidance(self):
        seeds = list(repair_shakedown_seeds())
        records = [self.record(s, "SUBCRITICAL", "SUBCRITICAL")
                   for s in seeds]
        summary = evaluate_gate(records)
        self.assertFalse(summary["gate_passed"])
        self.assertFalse(summary["G1_per_genotype"]["102"]["passes_G1"])
        self.assertFalse(summary["G2_joint_supercritical"]["passes_G2"])
        self.assertIn("supported by new evidence",
                      summary["failure_guidance"])

    def test_gate_logic_differs_from_predecessor_only_in_labels(self):
        # Same G1-G4 arithmetic as the committed endpoint-generation gate;
        # only the protocol labels and guidance text differ.
        seeds = list(repair_shakedown_seeds())
        records = ([self.record(s, "SUPERCRITICAL", "SUPERCRITICAL")
                    for s in seeds[:16]]
                   + [self.record(s, "SUPERCRITICAL", "SUBCRITICAL")
                      for s in seeds[16:20]]
                   + [self.record(s, "SUBCRITICAL", "SUBCRITICAL")
                      for s in seeds[20:]])
        mine = evaluate_gate(copy.deepcopy(records))
        theirs = legacy_evaluate_gate(copy.deepcopy(records))
        self.assertEqual(mine["G1_per_genotype"], theirs["G1_per_genotype"])
        self.assertEqual(mine["G2_joint_supercritical"]["replicates"],
                         theirs["G2_joint_supercritical"]["replicates"])
        self.assertEqual(mine["gate_passed"], theirs["gate_passed"])
        self.assertNotEqual(mine["gate"], theirs["gate"])


if __name__ == "__main__":
    unittest.main()
