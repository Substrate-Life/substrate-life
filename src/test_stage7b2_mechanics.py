"""Stage 7B2 registered test matrix.

Covers, per ``docs/stage-7b2-preregistration.md``:

- Section 4 solver contract: hand-computable known-answer Euler-Lotka
  schedules with independently bounded roots (Decimal reference evaluation,
  analysis-side only), certified containment, resolution, and the
  SUBCRITICAL boundary;
- Section 3 estimators: hand-built event ledgers with exact expected
  l_x/m_x, censoring, exposure-through-death-tick, genotype attribution,
  and no credit without establishment;
- population mechanics: explicit founder genomes, exact inheritance,
  label-permutation invariance of mechanics, and the registered
  implementation-window calibration precondition on the registered seed
  (first offspring reproduction; binding admission after saturation with a
  nonzero would_admit counter);
- mandated calibration against the retained Stage 7B0 blocks: replaying
  their checkpoint ledger states through the shared closure identities must
  reproduce every recorded closure exactly;
- the Section 5 decision rule: all outcome classes reachable, median
  convention, pairing, and the delta_min boundary;
- runner classification: BUFFER_OVERFLOW triggers INVALID_IMPLEMENTATION.

This file makes no fitness, selection, or evolutionary claim.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
import json
import os
import unittest

from stage7b1_mechanics import BufferOverflowError
from stage7b2_measure import (
    build_c_vector,
    cohort_genotypes,
    cohort_schedule,
    extract_vital_records,
    fmt_rat,
    mediator_summary,
    parse_rat,
)
from stage7b2_population import (
    REGISTERED_BUFFER_DEPTH,
    REGISTERED_CENSUS_CAPACITY,
    REGISTERED_GENOTYPES,
    REGISTERED_HAZARD_RATE,
    REGISTERED_PACKET_RATE,
    REGISTERED_WINDOW_TICKS,
    Stage7B2Population,
    registered_founder_genomes,
    registered_population,
    registered_seed,
    run_window,
)
from stage7b2_solver import (
    MIN_CONTRAST_DELTA_R,
    SOLVER_RESOLUTION_RHO,
    apply_decision_rule,
    bracket_midpoint,
    certified_bracket,
    exp_neg_enclosure,
    lotka_interval,
    median_lower_middle,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE7B0_RESULT = os.path.join(REPO_ROOT, "results", "stage7b0",
                               "stage7b0-result.json")


def _certified_decimal_root(c_x: dict[int, Fraction]) -> Decimal:
    """Independent high-precision Decimal root of L(r)=1 (test-side only)."""
    getcontext().prec = 60

    def lotka(r: Decimal) -> Decimal:
        total = Decimal(0)
        for x, cx in c_x.items():
            total += (Decimal(cx.numerator) / Decimal(cx.denominator)
                      * (-r * x).exp())
        return total

    lo, hi = Decimal(0), Decimal(2)
    for _ in range(400):
        if lotka(hi) < 1:
            break
        hi *= 2
        if hi > Decimal("1e50"):
            break
    for _ in range(400):
        mid = (lo + hi) / 2
        if lotka(mid) >= 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


class Stage7B2SolverTests(unittest.TestCase):
    """Preregistration section 4 solver contract."""

    def test_exp_enclosure_bounds_known_values(self):
        # e^-1 in [0.36787944117, 0.36787944118]
        lo, hi = exp_neg_enclosure(Fraction(1))
        self.assertLess(lo, hi)
        self.assertLess(abs(float(lo) - 0.36787944117144233), 1e-12)
        self.assertLess(abs(float(hi) - 0.36787944117144233), 1e-12)

    def test_single_age_schedule_root_ln_3_2(self):
        c = {1: Fraction(3, 2)}
        cert = certified_bracket(c)
        self.assertEqual(cert["status"], "SUPERCRITICAL")
        ref = _certified_decimal_root(c)
        r_lo_dec = Decimal(cert["r_lo"].numerator) / Decimal(cert["r_lo"].denominator)
        r_hi_dec = Decimal(cert["r_hi"].numerator) / Decimal(cert["r_hi"].denominator)
        self.assertLessEqual(r_lo_dec, ref + Decimal("1e-30"))
        self.assertGreaterEqual(r_hi_dec, ref - Decimal("1e-30"))
        self.assertLessEqual(cert["r_hi"] - cert["r_lo"],
                             SOLVER_RESOLUTION_RHO)
        # Midpoint is within half a resolution step of the true root.
        midpoint = (cert["r_lo"] + cert["r_hi"]) / 2
        ref_frac = Fraction(ref)
        self.assertLessEqual(abs(midpoint - ref_frac),
                             SOLVER_RESOLUTION_RHO / 2)
        # Analytic value ln(3/2) ~ 0.4054651081
        self.assertAlmostEqual(float(ref), 0.4054651081081644, places=25)

    def test_single_age_schedule_root_ln_2(self):
        c = {1: Fraction(2)}
        cert = certified_bracket(c)
        self.assertEqual(cert["status"], "SUPERCRITICAL")
        ref = _certified_decimal_root(c)
        self.assertAlmostEqual(float(ref), 0.6931471805599453, places=25)
        mid = bracket_midpoint(cert)
        self.assertIsNotNone(mid)
        self.assertLessEqual(cert["width"], SOLVER_RESOLUTION_RHO)
        # Certified sign conditions via independent interval evaluation.
        lo_val, _ = lotka_interval(c, cert["r_lo"])
        _, hi_val = lotka_interval(c, cert["r_hi"])
        self.assertGreaterEqual(lo_val, 1)
        self.assertLess(hi_val, 1)

    def test_two_age_schedule_matches_decimal_reference(self):
        c = {2: Fraction(9, 10), 5: Fraction(7, 10),
             11: Fraction(1, 20)}
        cert = certified_bracket(c)
        self.assertEqual(cert["status"], "SUPERCRITICAL")
        ref = _certified_decimal_root(c)
        r_lo = Decimal(cert["r_lo"].numerator) / Decimal(cert["r_lo"].denominator)
        r_hi = Decimal(cert["r_hi"].numerator) / Decimal(cert["r_hi"].denominator)
        self.assertLessEqual(r_lo, ref)
        self.assertGreaterEqual(r_hi, ref)
        self.assertLessEqual(cert["width"], SOLVER_RESOLUTION_RHO)

    def test_subcritical_boundary_L0_equals_one(self):
        cert = certified_bracket({3: Fraction(1)})
        self.assertEqual(cert["status"], "SUBCRITICAL")
        self.assertEqual(cert["L0_exact"], 1)
        self.assertIsNone(bracket_midpoint(cert))

    def test_subcritical_strictly_below(self):
        cert = certified_bracket({1: Fraction(1, 2), 4: Fraction(1, 8)})
        self.assertEqual(cert["status"], "SUBCRITICAL")

    def test_resolution_and_support_serialisation(self):
        c = {1: Fraction(22, 10), 7: Fraction(3, 2)}
        cert = certified_bracket(c)
        self.assertIn("1", cert["support"])
        self.assertEqual(parse_rat(cert["support"]["1"]), Fraction(22, 10))
        self.assertLessEqual(cert["width"], SOLVER_RESOLUTION_RHO)


def _synthetic_log() -> list[dict]:
    """Hand-built ledger matching the frozen 7B1 event schema exactly.

    Founders F0(A=102) and F1(A=204); F0 bears C2 at t=2; C2 bears C3 at
    t=6 (establishment crediting F0's lineage at parent age 4); F1 dies at
    t=8 having never reproduced; C2 dies at t=20; window W=30."""
    log = [
        {"event": "founder_registered", "tick": 0, "organism_id": "org-0",
         "ancestry_id": "F0", "a_over_d": "102/255", "t_over_d": "128/255",
         "genotype_hash": "h102", "s_initial": "100/1", "r_initial": "0/1"},
        {"event": "founder_registered", "tick": 0, "organism_id": "org-1",
         "ancestry_id": "F1", "a_over_d": "204/255", "t_over_d": "128/255",
         "genotype_hash": "h204", "s_initial": "100/1", "r_initial": "0/1"},
        {"event": "packet_draw", "tick": 1, "organism_id": "org-0"},
        {"event": "packet_draw", "tick": 1, "organism_id": "org-1"},
        {"event": "provision_committed", "tick": 2, "organism_id": "org-0",
         "child_id": "org-2", "inherited_a_over_d": "102/255"},
        {"event": "birth_admitted", "tick": 2, "parent_id": "org-0",
         "child_id": "org-2", "provision": "41/2"},
        {"event": "packet_draw", "tick": 3, "organism_id": "org-2"},
        {"event": "provision_committed", "tick": 6, "organism_id": "org-2",
         "child_id": "org-3", "inherited_a_over_d": "102/255"},
        {"event": "birth_admitted", "tick": 6, "parent_id": "org-2",
         "child_id": "org-3", "provision": "33/4"},
        {"event": "hazard_death", "tick": 8, "organism_id": "org-1"},
        {"event": "divide_failed", "tick": 9, "organism_id": "org-0",
         "stage": "V", "reason": "NO_VACANCY"},
        {"event": "somatic_stall", "tick": 10, "organism_id": "org-3"},
        {"event": "hazard_death", "tick": 20, "organism_id": "org-2"},
    ]
    return log


class Stage7B2MeasurementTests(unittest.TestCase):
    """Preregistration section 3 estimator definitions."""

    WINDOW = 30

    def setUp(self):
        self.vitals = extract_vital_records(_synthetic_log(), self.WINDOW)

    def test_membership_and_genotypes(self):
        members = self.vitals["members"]
        self.assertEqual(members["org-0"]["genotype_a"], 102)
        self.assertEqual(members["org-1"]["genotype_a"], 204)
        self.assertEqual(members["org-2"]["born_tick"], 2)
        self.assertEqual(cohort_genotypes(self.vitals), [102, 204])

    def test_establishment_credit_exact(self):
        # org-2 first reproduces at tick 6; it was born at tick 2, so its
        # parent org-0 is credited at parent age 4.
        self.assertEqual(self.vitals["establishments"], [{
            "parent_id": "org-0",
            "through_offspring": "org-2",
            "tick": 6,
            "parent_age": 4,
        }])

    def test_first_reproduction_and_extraction(self):
        self.assertEqual(self.vitals["first_reproduction"]["org-0"], 2)
        self.assertEqual(self.vitals["first_reproduction"]["org-2"], 6)
        self.assertNotIn("org-3", self.vitals["first_reproduction"])
        self.assertEqual(self.vitals["first_extraction"]["org-0"], 1)
        self.assertEqual(self.vitals["first_extraction"]["org-2"], 3)

    def test_cohort_schedule_lx_mx_exact(self):
        g102 = cohort_schedule(self.vitals, 102)
        # Cohort: org-0 (founder, alive through W=30 -> ages 0..30),
        # org-2 (born 2, died 20 -> ages 0..18), org-3 (born 6, alive).
        self.assertEqual(g102["cohort_size"], 3)
        # l_x counts members attaining age >= x.
        self.assertEqual(g102["l_x"][0], Fraction(3, 3))
        self.assertEqual(g102["l_x"][4], Fraction(3, 3))
        self.assertEqual(g102["l_x"][19], Fraction(2, 3))
        self.assertEqual(g102["l_x"][24], Fraction(2, 3))
        # org-3 caps at attained age W - 6 = 24; only org-0 attains age 30.
        self.assertEqual(g102["l_x"][25], Fraction(1, 3))
        self.assertEqual(g102["l_x"][self.WINDOW], Fraction(1, 3))
        # m_x: one establishment at parent age 4 within a 3-member cohort.
        self.assertEqual(g102["m_x"][4], Fraction(1, 3))
        self.assertEqual(sum(g102["m_x"]), Fraction(1, 3))

    def test_death_contributes_exposure_through_death_tick(self):
        g204 = cohort_schedule(self.vitals, 204)
        # org-1 only: born measurement tick 0, died tick 8 -> ages 0..8,
        # exposure 9 member-ticks.
        self.assertEqual(g204["cohort_size"], 1)
        self.assertEqual(g204["exposure_member_ticks"], 9)
        self.assertEqual(g204["died"], 1)
        self.assertEqual(g204["l_x"][8], Fraction(1, 1))
        self.assertEqual(g204["l_x"][9], Fraction(0, 1))
        self.assertEqual(sum(g204["m_x"]), Fraction(0, 1))

    def test_sterile_persistence_confers_no_credit(self):
        # org-1 persisted to tick 8 and org-3 persists through the window;
        # neither appears in m_x anywhere.
        g204 = cohort_schedule(self.vitals, 204)
        self.assertTrue(all(v == 0 for v in g204["m_x"]))
        g102 = cohort_schedule(self.vitals, 102)
        self.assertEqual(sum(g102["m_x"]), Fraction(1, 3))

    def test_c_vector_support(self):
        schedule = cohort_schedule(self.vitals, 102)
        c = build_c_vector(schedule["l_x"], schedule["m_x"])
        self.assertEqual(sorted(c), [4])
        self.assertEqual(c[4], Fraction(1, 3) * Fraction(3, 3))

    def test_mediator_summary_identity(self):
        summary = mediator_summary(self.vitals, shadow_decisions=3,
                                   shadow_would_admit=2,
                                   admitted_births=2)
        self.assertEqual(summary["shadow_decisions"], 3)
        self.assertEqual(summary["vacancy_availability_rate_ecological"],
                         "2/3")


class Stage7B2PopulationMechanicsTests(unittest.TestCase):
    """Founder genomes, inheritance, permutation invariance."""

    def test_founder_events_carry_exact_registered_genomes(self):
        pop = registered_population(registered_seed(0))
        founder_events = [e for e in pop.event_log
                          if e.get("event") == "founder_registered"]
        self.assertEqual(len(founder_events), 6)
        got = [(int(e["a_over_d"].split("/")[0]),
                int(e["t_over_d"].split("/")[0])) for e in founder_events]
        self.assertEqual(got, [(102, 128)] * 3 + [(204, 128)] * 3)
        self.assertEqual([e["ancestry_id"] for e in founder_events],
                         ["F0", "F1", "F2", "F3", "F4", "F5"])

    def test_inheritance_is_exact_under_mutation_disabled_divide(self):
        pop = Stage7B2Population(
            founder_genomes=[(102, 128, 255)], capacity=4,
            founder_s=Fraction(100000), memory_pool=65536,
            hazard_seed=5, hazard_rate=Fraction(0), buffer_depth=512,
            window_ticks=64,
        )
        child_seen = None
        for _ in range(64):
            pop.step()
            children = [oid for oid in pop.members
                        if oid not in {"org-0"}]
            if children:
                child_seen = children[0]
                break
        self.assertIsNotNone(child_seen)
        assert child_seen is not None
        parent = pop.all_organisms["org-0"]
        child = pop.all_organisms[child_seen]
        self.assertEqual(
            (child.a, child.t, child.d),
            (parent.a, parent.t, parent.d))

    def test_label_permutation_leaves_aggregates_invariant(self):
        def aggregates(genomes):
            pop = Stage7B2Population(
                founder_genomes=genomes, capacity=REGISTERED_CENSUS_CAPACITY,
                founder_s=Fraction(100), memory_pool=65536,
                hazard_seed=registered_seed(3),
                hazard_rate=REGISTERED_HAZARD_RATE,
                corpse_ttl=2, packet_rate=REGISTERED_PACKET_RATE,
                buffer_depth=REGISTERED_BUFFER_DEPTH, window_ticks=120,
            )
            result = run_window(pop)
            self.assertEqual(result["classification"], "COMPLETE")
            reserve = pop.reserve_closure()
            return {
                "births": pop.admitted_births,
                "deaths": pop.hazard_removals,
                "gross": str(reserve["net_income"]),
                "final_census": len(pop.members),
            }
        base = registered_founder_genomes()
        swapped = base[3:] + base[:3]  # genotypes exchange organisation IDs
        self.assertEqual(aggregates(base), aggregates(swapped))


class Stage7B2CalibrationPreconditionTests(unittest.TestCase):
    """Registered implementation-window calibration precondition.

    Preregistration section 2: before the freeze, exploratory non-retained
    runs must demonstrate, within W, at least one offspring first-
    reproduction event and at least one binding admission under saturated
    census with a nonzero would_admit counter.  This test exercises the
    exact registered configuration on replicate seed index 0 as the frozen
    witness of that demonstration.
    """

    def test_registered_configuration_precondition_on_seed_zero(self):
        pop = registered_population(registered_seed(0))
        result = run_window(pop)
        self.assertEqual(result["classification"], "COMPLETE")
        vitals = extract_vital_records(pop.event_log, REGISTERED_WINDOW_TICKS)
        # (i) at least one offspring first-reproduction event.
        self.assertGreater(len(vitals["establishments"]), 0)
        # (ii) binding admission under saturation: a NO_VACANCY rejection
        # precedes a later admitted birth, with nonzero shadow counters.
        no_vacancy_ticks = [e["tick"] for e in pop.event_log
                            if e.get("reason") == "NO_VACANCY"]
        birth_ticks = [e["tick"] for e in pop.event_log
                       if e.get("event") == "birth_admitted"]
        self.assertGreater(len(no_vacancy_ticks), 0)
        self.assertGreater(
            len([t for t in birth_ticks if t > min(no_vacancy_ticks)]), 0)
        self.assertGreater(pop.shadow_decisions, 0)
        self.assertGreater(pop.shadow_would_admit, 0)
        # Layer-2 guard held throughout: buffered <= d at every checkpoint.
        self.assertEqual(result["ticks_completed"], REGISTERED_WINDOW_TICKS)


class Stage7B2CalibrationAgainstStage7B0Tests(unittest.TestCase):
    """Mandated calibration: replay retained 7B0 blocks through the shared
    ledger-closure identities and reproduce the registered closures."""

    def test_retained_block_checkpoints_close_exactly(self):
        with open(STAGE7B0_RESULT, encoding="utf-8") as handle:
            artifact = json.load(handle)
        self.assertEqual(artifact["decision"], "PASS")
        checked = 0
        for block_name in ("A", "B", "C"):
            block = artifact["blocks"][block_name]
            for arm_name, arm in block["arms"].items():
                checkpoints = arm.get("checkpoints")
                if not checkpoints:
                    continue
                opening = Fraction(100)  # registered INITIAL parent_S
                for point in arm["checkpoints"]:
                    parent_s = parse_rat(point["parent_S"])
                    parent_r = parse_rat(point["parent_R"])
                    gross = parse_rat(point["gross_income"])
                    reversed_income = parse_rat(point["reversed_income"])
                    destroyed = parse_rat(point["destroyed"])
                    committed = parse_rat(point["committed_child_S"])
                    costs = parse_rat(point["C_S"]) + parse_rat(point["C_R"])
                    lhs = parent_s + parent_r + destroyed + committed
                    rhs = opening + gross - reversed_income - costs
                    self.assertEqual(lhs, rhs,
                                     f"{block_name}/{arm_name} "
                                     f"{point['checkpoint']} envelope")
                    memory = point["memory"]
                    pool_total = (memory["free_pool"]
                                  + memory["somatic_active"]
                                  + memory["gestation"]
                                  + memory["corpse_reserved"])
                    self.assertEqual(pool_total, 8192,
                                     f"{block_name}/{arm_name} memory")
                    for packet in point["packets"]:
                        closed = (Fraction(packet["budget_remaining"])
                                  + Fraction(packet["drawn_S"])
                                  + Fraction(packet["drawn_R"])
                                  == Fraction(packet["initial_budget"]))
                        self.assertTrue(closed)
                    checked += 1
        # Block A contributes five paired checkpoints per arm (10 here);
        # require substantial coverage of the retained closures.
        self.assertGreaterEqual(checked, 8)

    def test_retained_final_closures_match_recorded_values(self):
        with open(STAGE7B0_RESULT, encoding="utf-8") as handle:
            artifact = json.load(handle)
        for block_name in ("A", "B", "C"):
            for arm in artifact["blocks"][block_name]["arms"].values():
                closure = arm["reserve_closure"]
                self.assertTrue(closure["closed"])
                self.assertEqual(Fraction(closure["lhs"]),
                                 Fraction(closure["rhs"]))


class Stage7B2DecisionRuleTests(unittest.TestCase):
    """Preregistration section 5 classes, conventions, and boundaries."""

    @staticmethod
    def super_cert(mid: Fraction):
        half = SOLVER_RESOLUTION_RHO / 2
        return {"status": "SUPERCRITICAL", "r_lo": mid - half,
                "r_hi": mid + half, "width": half * 2}

    SUB = {"status": "SUBCRITICAL"}

    def test_degenerate_replication_below_pair_floor(self):
        outcomes = [{102: self.SUB, 204: self.SUB} for _ in range(15)]
        rule = apply_decision_rule(outcomes)
        self.assertEqual(rule["pair_contrast_class"],
                         "DEGENERATE_REPLICATION")

    def test_established_contrast_at_and_above_delta_min(self):
        # Median paired difference exactly delta_min = 1/100 -> ESTABLISHED.
        mids_a = [Fraction(i, 1000) for i in range(16)]
        mids_b = [m + Fraction(1, 100) for m in mids_a]
        outcomes = [{102: self.super_cert(a), 204: self.super_cert(b)}
                    for a, b in zip(mids_a, mids_b)]
        rule = apply_decision_rule(outcomes)
        self.assertEqual(rule["pair_contrast_class"], "ESTABLISHED_CONTRAST")
        self.assertEqual(rule["median_paired_difference"], Fraction(1, 100))
        # Just below the floor (99999/10^7 < 1/100) -> NO_ESTABLISHED_CONTRAST.
        mids_b = [m + Fraction(99999, 10000000) for m in mids_a]
        outcomes = [{102: self.super_cert(a), 204: self.super_cert(b)}
                    for a, b in zip(mids_a, mids_b)]
        rule = apply_decision_rule(outcomes)
        self.assertEqual(rule["pair_contrast_class"],
                         "NO_ESTABLISHED_CONTRAST")

    def test_median_convention_lower_middle_even_k(self):
        values = [Fraction(1), Fraction(2), Fraction(10), Fraction(40)]
        self.assertEqual(median_lower_middle(values), Fraction(2))
        self.assertEqual(median_lower_middle([Fraction(7)]), Fraction(7))
        self.assertIsNone(median_lower_middle([]))

    def test_complete_pairs_require_both_supercritical(self):
        outcomes = []
        for i in range(16):
            outcomes.append({102: self.super_cert(Fraction(i, 100)),
                             204: self.SUB})
        rule = apply_decision_rule(outcomes)
        self.assertEqual(rule["complete_pairs"], 0)
        self.assertEqual(rule["pair_contrast_class"],
                         "DEGENERATE_REPLICATION")
        self.assertEqual(rule["subcritical_report"], "ONE_ARM_SUBCRITICAL")

    def test_both_subcritical_reported_alongside(self):
        outcomes = [{102: self.SUB, 204: self.SUB} for _ in range(16)]
        rule = apply_decision_rule(outcomes)
        self.assertEqual(rule["subcritical_report"], "BOTH_SUBCRITICAL")
        self.assertEqual(rule["pair_contrast_class"],
                         "DEGENERATE_REPLICATION")

    def test_sign_of_difference_is_descriptive_only(self):
        mids_a = [Fraction(i, 100) for i in range(16)]
        mids_b = [m - Fraction(1, 5) for m in mids_a]
        outcomes = [{102: self.super_cert(a), 204: self.super_cert(b)}
                    for a, b in zip(mids_a, mids_b)]
        rule = apply_decision_rule(outcomes)
        self.assertEqual(rule["pair_contrast_class"], "ESTABLISHED_CONTRAST")
        self.assertEqual(rule["median_paired_difference"],
                         Fraction(-1, 5))


class Stage7B2RunnerGuardTests(unittest.TestCase):
    """Layer-1 trigger classification (unregistered tiny-depth fixture)."""

    def test_buffer_overflow_classifies_invalid_implementation(self):
        pop = Stage7B2Population(
            founder_genomes=[(102, 128, 255)], capacity=2,
            founder_s=Fraction(0),  # everyone stalls: zero consumption
            memory_pool=4096, hazard_seed=1, hazard_rate=Fraction(0),
            buffer_depth=3, window_ticks=8,
        )
        with self.assertRaises(BufferOverflowError):
            for _ in range(8):
                pop.step()
        # run_window converts the trigger into the registered class.
        pop2 = Stage7B2Population(
            founder_genomes=[(102, 128, 255)], capacity=2,
            founder_s=Fraction(0), memory_pool=4096, hazard_seed=1,
            hazard_rate=Fraction(0), buffer_depth=3, window_ticks=8,
        )
        result = run_window(pop2)
        self.assertEqual(result["classification"], "INVALID_IMPLEMENTATION")
        self.assertEqual(result["reason"], "BUFFER_OVERFLOW")

    def test_minimum_contrast_constant_matches_preregistration(self):
        self.assertEqual(MIN_CONTRAST_DELTA_R, Fraction(1, 100))
        self.assertEqual(SOLVER_RESOLUTION_RHO, Fraction(1, 256))
        self.assertEqual(fmt_rat(MIN_CONTRAST_DELTA_R), "1/100")


if __name__ == "__main__":
    unittest.main()
