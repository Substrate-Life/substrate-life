"""Stage 7B signed-bracket mechanics tests.

Covers exactly what is NEW in ``stage7b_signed_bracket_solver.py``,
``stage7b_signed_bracket_config.py``, and ``stage7b_signed_bracket_gate.py``
against ``docs/stage-7b-signed-bracket-preregistration.md``:

- byte-identity pins for every reused frozen module across all four Stage
  7B gate generations (drift fails here first);
- the full-line solver contract: ``exp_pos_enclosure`` known values, the
  SUPERCRITICAL/CRITICAL/SUBCRITICAL/NO_FINITE_ROOT classification table
  on hand-computable schedules with independently bounded roots (Decimal
  reference evaluation, analysis-side only), certified containment and
  resolution on both branches;
- the completed Section-3 decision rule: complete-pair availability from
  ANY finite-root status (not just joint supercriticality), sign-split
  reporting, and the carried class thresholds;
- the configuration echo, retained paths, and carried-values agreement
  with the denominator-repair layer;
- gate evaluation logic G1-G3 including the ``NO_FINITE_ROOT`` failure
  path and the generation-3 regression identity (using the real archived
  reference file, read-only).

This file makes no fitness, selection, or evolutionary claim.
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from fractions import Fraction
import copy
import json
import os
import unittest

from stage7b2_solver import (
    MIN_CONTRAST_DELTA_R,
    MIN_COMPLETE_PAIRS,
    SOLVER_RESOLUTION_RHO,
)
from stage7b1_mechanics import REGISTERED_PACKET_RATE
from stage7b2_measure import cohort_genotypes, extract_vital_records
from stage7b2_population import Stage7B2Population, run_window
from stage7b2r_population import (
    REGISTERED_BUFFER_DEPTH,
    REGISTERED_CENSUS_CAPACITY,
    REGISTERED_CORPSE_TTL,
    REGISTERED_FOUNDER_S,
    REGISTERED_HAZARD_RATE,
    REGISTERED_MEMORY_POOL,
    REGISTERED_PACKET_ENERGY,
    registered_founder_genomes,
    shakedown_seed,
)
from stage7b2r_population import shakedown_seeds as repair_shakedown_seeds
from stage7b_signed_bracket_config import (
    GENERATION_3_GATE_SUMMARY_PATH,
    PRE_EXECUTION_MANIFEST_PATH,
    PREREG_DOCUMENT,
    PROTOCOL,
    RAW_RESULT_PATH,
    REDUCED_RESULT_PATH,
    RESULTS_DIR,
    decision_rule_inputs,
    endpoint_configuration,
)
from stage7b_exposure_config import endpoint_configuration as exposure_configuration
from stage7b_exposure_measure import exposure_schedule, lotka_coefficients
from stage7b_signed_bracket_gate import (
    _gate_threshold,
    evaluate_gate,
    load_generation_3_reference,
)
from stage7b_signed_bracket_solver import (
    FINITE_ROOT_STATUSES,
    apply_full_line_decision_rule,
    exp_pos_enclosure,
    full_line_bracket_midpoint,
    full_line_certified_bracket,
    lotka_interval_signed,
)
from reduce_stage7b_signed_bracket import (
    REDUCER_SOURCES,
    _jsonable,
    reduce_artifact,
)
from run_stage7b_signed_bracket import FROZEN_SOURCES, _serialise_birth
from test_stage7b_endpoint_mechanics import fmt, sha256_of

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Hashes of the shared modules exactly as retained/pinned before this
# implementation window opened (signed-bracket prereg Authorisation
# section: every module reused across all four Stage 7B gate
# generations).
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
    "src/stage7b_endpoint_measure.py":
        "19d5380a0dae469443c39487a9e3b2d450de558280493ae285c377a30380256a",
    "src/stage7b_endpoint_config.py":
        "c6c73ccc5eeb89710f1d74a2d1f0777468bc1c45f92e4b150966c05d6c01f5bf",
    "src/stage7b_endpoint_gate.py":
        "5d3c8d8c16db4b99a8dec2db9c07894e1133179bb3a3c04e6325017e1388d1f2",
    "src/run_stage7b_endpoint.py":
        "4571729302e51594e5812e7c505d156616dbf5ba8cdc6914163c80378b5c386d",
    "src/reduce_stage7b_endpoint.py":
        "b234dfee6a3b63d4ed14782ee891e046359fc12c0493299838864b10bace17bf",
    "src/stage7b_exposure_measure.py":
        "87668aac1981811906b9ebd4e78515141178c4e428ee800af3d9ba43ee779f32",
    "src/stage7b_exposure_config.py":
        "6d75f54681c90adbdbefba5a0254a4660969482598fe7753788a2081d5896b11",
    "src/stage7b_exposure_gate.py":
        "f3f6a3d35598c4d4903bfa7d52b58c14e643582208d4750cee1d51ac4b136242",
}


def _certified_decimal_root(c_x: dict[int, Fraction]) -> Decimal:
    """Independent high-precision Decimal root of L(r)=1 (test-side only).

    Searches the full real line (unlike the positive-only helper in
    ``test_stage7b2_mechanics.py``): expands a bracket outward in both
    directions before bisecting.
    """
    getcontext().prec = 60

    def lotka(r: Decimal) -> Decimal:
        total = Decimal(0)
        for x, cx in c_x.items():
            total += (Decimal(cx.numerator) / Decimal(cx.denominator)
                      * (-r * x).exp())
        return total

    lo, hi = Decimal(-2), Decimal(2)
    for _ in range(400):
        if lotka(hi) < 1:
            break
        hi *= 2
        if hi > Decimal("1e50"):
            break
    for _ in range(400):
        if lotka(lo) >= 1:
            break
        lo *= 2
        if lo < Decimal("-1e50"):
            break
    for _ in range(600):
        mid = (lo + hi) / 2
        if lotka(mid) >= 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


class FrozenModuleImmutabilityTests(unittest.TestCase):
    """Signed-bracket prereg Authorisation/section 8: frozen modules are
    never edited in place; the new window only adds files."""

    def test_pinned_hashes_unchanged(self):
        for relative_path, expected in PINNED_HASHES.items():
            self.assertEqual(sha256_of(relative_path), expected,
                             msg=f"{relative_path} drifted from its pin")

    def test_new_modules_are_additive_files(self):
        for name in ("stage7b_signed_bracket_solver.py",
                     "stage7b_signed_bracket_config.py",
                     "stage7b_signed_bracket_gate.py",
                     "run_stage7b_signed_bracket.py",
                     "reduce_stage7b_signed_bracket.py",
                     "test_stage7b_signed_bracket_mechanics.py"):
            self.assertNotIn(name.replace(".py", ""), PINNED_HASHES)


class ExpPosEnclosureTests(unittest.TestCase):
    """Rigorous e^{+t} enclosure: known values, containment, monotone."""

    def test_e1_bounds_known_value(self):
        getcontext().prec = 60
        ref = Decimal(1).exp()
        lo, hi = exp_pos_enclosure(Fraction(1))
        lo_dec = Decimal(lo.numerator) / Decimal(lo.denominator)
        hi_dec = Decimal(hi.numerator) / Decimal(hi.denominator)
        self.assertLessEqual(lo_dec, ref)
        self.assertGreaterEqual(hi_dec, ref)
        self.assertLess(hi - lo, Fraction(1, 2 ** 40))

    def test_e_large_t_bounds_known_value(self):
        getcontext().prec = 60
        ref = Decimal(10).exp()
        lo, hi = exp_pos_enclosure(Fraction(10))
        lo_dec = Decimal(lo.numerator) / Decimal(lo.denominator)
        hi_dec = Decimal(hi.numerator) / Decimal(hi.denominator)
        self.assertLessEqual(lo_dec, ref)
        self.assertGreaterEqual(hi_dec, ref)

    def test_rejects_nonpositive_t(self):
        with self.assertRaises(ValueError):
            exp_pos_enclosure(Fraction(0))
        with self.assertRaises(ValueError):
            exp_pos_enclosure(Fraction(-1))

    def test_lower_bound_is_partial_sum_always_valid(self):
        for t in (Fraction(1, 3), Fraction(5), Fraction(37, 4)):
            lo, hi = exp_pos_enclosure(t)
            self.assertLessEqual(lo, hi)


class LotkaIntervalSignedTests(unittest.TestCase):
    """Dispatch correctness and negative-branch containment."""

    def test_dispatches_to_frozen_positive_branch(self):
        from stage7b2_solver import lotka_interval
        c = {1: Fraction(3, 2), 3: Fraction(1, 4)}
        for r in (Fraction(0), Fraction(1, 4), Fraction(2)):
            self.assertEqual(lotka_interval_signed(c, r),
                             lotka_interval(c, r))

    def test_negative_branch_matches_decimal_reference(self):
        c = {1: Fraction(1, 2)}
        r = Fraction(-1)
        lo, hi = lotka_interval_signed(c, r)
        # L(-1) = (1/2) * e^{1} ~= 1.359140914229523
        ref = Decimal("1.3591409142295225")
        self.assertLess(Decimal(lo.numerator) / Decimal(lo.denominator), ref)
        self.assertGreater(Decimal(hi.numerator) / Decimal(hi.denominator),
                           ref)


class FullLineSolverContractTests(unittest.TestCase):
    """Section 3 classification table on hand-computable schedules."""

    def test_supercritical_matches_frozen_positive_branch(self):
        c = {1: Fraction(3, 2)}
        cert = full_line_certified_bracket(c)
        self.assertEqual(cert["status"], "SUPERCRITICAL")
        ref = _certified_decimal_root(c)
        r_lo = Decimal(cert["r_lo"].numerator) / Decimal(cert["r_lo"].denominator)
        r_hi = Decimal(cert["r_hi"].numerator) / Decimal(cert["r_hi"].denominator)
        self.assertLessEqual(r_lo, ref)
        self.assertGreaterEqual(r_hi, ref)
        self.assertLessEqual(cert["width"], SOLVER_RESOLUTION_RHO)

    def test_critical_boundary_exact_equality(self):
        c = {1: Fraction(1)}
        cert = full_line_certified_bracket(c)
        self.assertEqual(cert["status"], "CRITICAL")
        self.assertEqual(cert["r_lo"], Fraction(0))
        self.assertEqual(cert["r_hi"], Fraction(0))
        self.assertEqual(cert["width"], Fraction(0))

    def test_critical_is_l0_one_not_approximate(self):
        # L(0) = 99/100 + 1/100 = 1 exactly; must be CRITICAL, not
        # SUBCRITICAL-with-tiny-negative-bracket.
        c = {1: Fraction(99, 100), 2: Fraction(1, 100)}
        cert = full_line_certified_bracket(c)
        self.assertEqual(cert["status"], "CRITICAL")

    def test_subcritical_negative_root_matches_decimal_reference(self):
        # L(r) = (1/2) e^{-r} = 1 => r = ln(1/2) ~= -0.6931471805599453
        c = {1: Fraction(1, 2)}
        cert = full_line_certified_bracket(c)
        self.assertEqual(cert["status"], "SUBCRITICAL")
        self.assertLess(cert["r_lo"], 0)
        self.assertLess(cert["r_hi"], 0)
        ref = _certified_decimal_root(c)
        r_lo = Decimal(cert["r_lo"].numerator) / Decimal(cert["r_lo"].denominator)
        r_hi = Decimal(cert["r_hi"].numerator) / Decimal(cert["r_hi"].denominator)
        self.assertLessEqual(r_lo, ref)
        self.assertGreaterEqual(r_hi, ref)
        self.assertLessEqual(cert["width"], SOLVER_RESOLUTION_RHO)

    def test_subcritical_multi_age_matches_decimal_reference(self):
        c = {2: Fraction(1, 5), 6: Fraction(3, 20)}
        cert = full_line_certified_bracket(c)
        self.assertEqual(cert["status"], "SUBCRITICAL")
        ref = _certified_decimal_root(c)
        r_lo = Decimal(cert["r_lo"].numerator) / Decimal(cert["r_lo"].denominator)
        r_hi = Decimal(cert["r_hi"].numerator) / Decimal(cert["r_hi"].denominator)
        self.assertLessEqual(r_lo, ref)
        self.assertGreaterEqual(r_hi, ref)

    def test_no_finite_root_zero_support(self):
        cert = full_line_certified_bracket({})
        self.assertEqual(cert["status"], "NO_FINITE_ROOT")
        self.assertEqual(cert["L0_exact"], Fraction(0))

    def test_no_finite_root_age_zero_only_support(self):
        # S_plus == 0 with nonzero c_0 != 1: constant L(r) = c_0 forever.
        cert = full_line_certified_bracket({0: Fraction(1, 2)})
        self.assertEqual(cert["status"], "NO_FINITE_ROOT")

    def test_bracket_deterministic_repeatable(self):
        c = {3: Fraction(7, 20), 9: Fraction(1, 50)}
        first = full_line_certified_bracket(c)
        second = full_line_certified_bracket(c)
        self.assertEqual(first["status"], second["status"])
        self.assertEqual(first["r_lo"], second["r_lo"])
        self.assertEqual(first["r_hi"], second["r_hi"])


class BracketMidpointTests(unittest.TestCase):
    def test_midpoint_for_every_finite_root_status(self):
        super_cert = full_line_certified_bracket({1: Fraction(3, 2)})
        crit_cert = full_line_certified_bracket({1: Fraction(1)})
        sub_cert = full_line_certified_bracket({1: Fraction(1, 2)})
        for cert in (super_cert, crit_cert, sub_cert):
            self.assertIn(cert["status"], FINITE_ROOT_STATUSES)
            mid = full_line_bracket_midpoint(cert)
            self.assertIsNotNone(mid)
            self.assertEqual(mid, (cert["r_lo"] + cert["r_hi"]) / 2)

    def test_midpoint_none_for_rootless(self):
        cert = full_line_certified_bracket({})
        self.assertIsNone(full_line_bracket_midpoint(cert))


class DecisionRuleTests(unittest.TestCase):
    """Section-3-table decision rule: complete pairs from ANY finite root."""

    def _pair(self, cert_102: dict, cert_204: dict) -> dict:
        return {102: cert_102, 204: cert_204}

    def test_complete_pair_from_mixed_signed_statuses(self):
        # 102 supercritical, 204 subcritical: still a COMPLETE pair under
        # the repaired rule (both finite-root), unlike the superseded
        # joint-supercriticality rule.
        super_cert = full_line_certified_bracket({1: Fraction(3, 2)})
        sub_cert = full_line_certified_bracket({1: Fraction(1, 2)})
        outcomes = [self._pair(super_cert, sub_cert)] * MIN_COMPLETE_PAIRS
        details = apply_full_line_decision_rule(outcomes)
        self.assertEqual(details["complete_pairs"], MIN_COMPLETE_PAIRS)
        self.assertNotEqual(details["pair_contrast_class"],
                            "DEGENERATE_REPLICATION")

    def test_no_finite_root_excludes_pair(self):
        super_cert = full_line_certified_bracket({1: Fraction(3, 2)})
        rootless = full_line_certified_bracket({})
        outcomes = [self._pair(super_cert, rootless)] * 20
        details = apply_full_line_decision_rule(outcomes)
        self.assertEqual(details["complete_pairs"], 0)
        self.assertEqual(details["pair_contrast_class"],
                         "DEGENERATE_REPLICATION")

    def test_degenerate_below_floor(self):
        super_cert = full_line_certified_bracket({1: Fraction(3, 2)})
        sub_cert = full_line_certified_bracket({1: Fraction(1, 2)})
        outcomes = ([self._pair(super_cert, sub_cert)] * (MIN_COMPLETE_PAIRS - 1))
        details = apply_full_line_decision_rule(outcomes)
        self.assertEqual(details["pair_contrast_class"],
                         "DEGENERATE_REPLICATION")

    def test_established_contrast_at_delta_min_boundary(self):
        cert_a = full_line_certified_bracket({1: Fraction(3, 2)})
        cert_b = full_line_certified_bracket({1: Fraction(1, 2)})
        mid_a = full_line_bracket_midpoint(cert_a)
        mid_b = full_line_bracket_midpoint(cert_b)
        self.assertGreaterEqual(abs(mid_a - mid_b), MIN_CONTRAST_DELTA_R)
        outcomes = [self._pair(cert_a, cert_b)] * MIN_COMPLETE_PAIRS
        details = apply_full_line_decision_rule(outcomes)
        self.assertEqual(details["pair_contrast_class"], "ESTABLISHED_CONTRAST")

    def test_no_established_contrast_when_close(self):
        cert_a = full_line_certified_bracket({1: Fraction(3, 2)})
        cert_b = full_line_certified_bracket({1: Fraction(3, 2)})
        outcomes = [self._pair(cert_a, cert_b)] * MIN_COMPLETE_PAIRS
        details = apply_full_line_decision_rule(outcomes)
        self.assertEqual(details["pair_contrast_class"],
                         "NO_ESTABLISHED_CONTRAST")

    def test_both_subcritical_reported(self):
        cert_a = full_line_certified_bracket({1: Fraction(1, 2)})
        cert_b = full_line_certified_bracket({1: Fraction(1, 3)})
        outcomes = [self._pair(cert_a, cert_b)] * MIN_COMPLETE_PAIRS
        details = apply_full_line_decision_rule(outcomes)
        self.assertEqual(details["subcritical_report"], "BOTH_SUBCRITICAL")

    def test_sign_split_reported_descriptively(self):
        cert_super = full_line_certified_bracket({1: Fraction(3, 2)})
        cert_sub = full_line_certified_bracket({1: Fraction(1, 2)})
        outcomes = [self._pair(cert_super, cert_sub)] * MIN_COMPLETE_PAIRS
        details = apply_full_line_decision_rule(outcomes)
        self.assertEqual(details["sign_split"]["positive"], 0)
        self.assertEqual(details["sign_split"]["negative"], MIN_COMPLETE_PAIRS)

    def test_requires_exactly_two_genotypes(self):
        cert = full_line_certified_bracket({1: Fraction(3, 2)})
        with self.assertRaises(ValueError):
            apply_full_line_decision_rule([{102: cert}])


class ConfigurationCarryForwardTests(unittest.TestCase):
    def test_protocol_and_paths(self):
        self.assertEqual(PROTOCOL, "stage-7b-signed-bracket-preregistration")
        self.assertEqual(PREREG_DOCUMENT,
                         "docs/stage-7b-signed-bracket-preregistration.md")
        self.assertEqual(RESULTS_DIR, "results/stage7b-signed-bracket/")
        self.assertEqual(RAW_RESULT_PATH,
                         "results/stage7b-signed-bracket/"
                         "stage7b-signed-bracket-result.json")
        self.assertEqual(REDUCED_RESULT_PATH,
                         "results/stage7b-signed-bracket/"
                         "stage7b-signed-bracket-reduced.json")
        self.assertIn("pre-execution-manifest.json",
                      PRE_EXECUTION_MANIFEST_PATH)

    def test_carried_values_equal_exposure_layer(self):
        echo = endpoint_configuration()
        exposure = exposure_configuration()
        for key in ("window_ticks_W", "census_capacity_N", "buffer_depth_d",
                    "packet_rate_r", "hazard_arms", "replicates_k",
                    "seed_derivation", "genotypes_ATD",
                    "founders_per_genotype", "founder_S", "founder_R",
                    "corpse_ttl", "packet_energy", "memory_pool_bytes",
                    "binding_identities", "endpoint"):
            self.assertEqual(echo[key], exposure[key], msg=key)

    def test_solver_domain_registered(self):
        echo = endpoint_configuration()
        self.assertIn("full real line", echo["solver_domain"])
        self.assertIn("stage-7b2-preregistration.md section 4",
                      echo["solver_domain_supersedes"])

    def test_shakedown_table_reused_fourth_time(self):
        seeds = list(repair_shakedown_seeds())
        self.assertEqual(seeds[0], 20270000)
        self.assertEqual(len(set(seeds)), 24)
        echo = endpoint_configuration()
        self.assertIn("fourth time", echo["shakedown_table"])

    def test_decision_rule_inputs_echo(self):
        inputs = decision_rule_inputs()
        self.assertEqual(inputs["solver_resolution_rho_r"], "1/256")
        self.assertEqual(inputs["minimum_contrast_delta_r_min"], "1/100")
        self.assertEqual(inputs["minimum_complete_pairs"], 16)

    def test_generation_3_reference_path_exists(self):
        path = os.path.join(REPO_ROOT, GENERATION_3_GATE_SUMMARY_PATH)
        self.assertTrue(os.path.isfile(path), msg=path)


class GenerationThreeRegressionTests(unittest.TestCase):
    """Read-only reuse of the archived generation-3 gate evidence."""

    def test_reference_table_complete_and_spot_checked(self):
        reference = load_generation_3_reference()
        self.assertEqual(len(reference), 48)  # 24 seeds x 2 genotypes
        self.assertEqual(reference[(20270000, "204")], "212/215")

    def test_evaluate_gate_regression_pass_on_real_archived_values(self):
        path = os.path.join(REPO_ROOT, GENERATION_3_GATE_SUMMARY_PATH)
        with open(path, "r", encoding="utf-8") as handle:
            archived = json.load(handle)
        archived_records = {r["hazard_seed"]: r
                            for r in archived["replicate_records"][:3]}
        records = []
        for seed, archived_record in archived_records.items():
            records.append({
                "hazard_seed": seed,
                "classification": "COMPLETE",
                "genotype_status": {"102": "SUBCRITICAL", "204": "SUBCRITICAL"},
                "L0_exact": dict(archived_record["L0_exact"]),
            })
        summary = evaluate_gate(records)
        self.assertTrue(summary["G3_checkpoints_and_regression"]["passes_G3"])
        self.assertEqual(
            summary["G3_checkpoints_and_regression"]["regression_mismatches"],
            [])

    def test_evaluate_gate_regression_fails_on_tampered_value(self):
        path = os.path.join(REPO_ROOT, GENERATION_3_GATE_SUMMARY_PATH)
        with open(path, "r", encoding="utf-8") as handle:
            archived = json.load(handle)
        record = dict(archived["replicate_records"][0])
        tampered = dict(record["L0_exact"])
        tampered["102"] = "1/1"  # deliberately wrong
        records = [{
            "hazard_seed": record["hazard_seed"],
            "classification": "COMPLETE",
            "genotype_status": {"102": "SUBCRITICAL", "204": "SUBCRITICAL"},
            "L0_exact": tampered,
        }]
        summary = evaluate_gate(records)
        self.assertFalse(summary["G3_checkpoints_and_regression"]["passes_G3"])
        self.assertFalse(summary["gate_passed"])
        self.assertEqual(
            len(summary["G3_checkpoints_and_regression"]["regression_mismatches"]),
            1)


class FeasibilityGateLogicTests(unittest.TestCase):
    """G1-G3 evaluation over synthetic records (pure logic)."""

    @staticmethod
    def _real_seed_records(n: int) -> list[dict]:
        """Real archived seeds/L0 so the regression check passes cleanly."""
        path = os.path.join(REPO_ROOT, GENERATION_3_GATE_SUMMARY_PATH)
        with open(path, "r", encoding="utf-8") as handle:
            archived = json.load(handle)
        return [dict(r) for r in archived["replicate_records"][:n]]

    def test_two_thirds_threshold(self):
        self.assertEqual(_gate_threshold(24), 16)
        self.assertEqual(_gate_threshold(25), 17)

    def test_passing_table_all_finite_root(self):
        records = self._real_seed_records(24)
        for r in records:
            r["classification"] = "COMPLETE"
            r["genotype_status"] = {"102": "SUBCRITICAL", "204": "SUBCRITICAL"}
        summary = evaluate_gate(records)
        self.assertTrue(summary["gate_passed"])
        self.assertEqual(summary["gate"],
                         "stage-7b-signed-bracket-preregistration section 5")

    def test_no_finite_root_fails_g1(self):
        records = self._real_seed_records(24)
        for r in records:
            r["classification"] = "COMPLETE"
            r["genotype_status"] = {"102": "NO_FINITE_ROOT", "204": "SUBCRITICAL"}
        summary = evaluate_gate(records)
        self.assertFalse(summary["gate_passed"])
        self.assertFalse(summary["G1_complete_bracket_pairs"]["passes_G1"])
        self.assertEqual(summary["G1_complete_bracket_pairs"]["pairs"], 0)

    def test_invalid_classification_fails_g2(self):
        records = self._real_seed_records(24)
        for r in records[:20]:
            r["classification"] = "COMPLETE"
            r["genotype_status"] = {"102": "SUBCRITICAL", "204": "SUBCRITICAL"}
        for r in records[20:]:
            r["classification"] = "INVALID_IMPLEMENTATION"
        summary = evaluate_gate(records)
        self.assertFalse(summary["G2_no_overflow_no_invalid"]["passes_G2"])
        self.assertFalse(summary["gate_passed"])


class RunnerReducerPlumbingTests(unittest.TestCase):
    """Serialisation rules, source manifests, and the full reducer path.

    Uses a unit-test-scale (W=30) exploratory window on the gate's own
    shakedown-seed table, exactly per the endpoint-repair precedent:
    exercises the reducer contract end-to-end without any execution at
    the registered W=1200 confirmatory ecology (signed-bracket prereg
    sections 5/6/8 authorise only the fixed-table gate shakedowns before
    freeze)."""

    def test_frozen_sources_listed_once_each(self):
        self.assertEqual(len(FROZEN_SOURCES), len(set(FROZEN_SOURCES)))
        for required in ("stage7b2_measure.py", "stage7b2_population.py",
                         "stage7b2_solver.py", "stage7b2r_population.py",
                         "stage7b1_mechanics.py",
                         "stage7b_endpoint_measure.py",
                         "stage7b_exposure_measure.py",
                         "stage7b_exposure_config.py",
                         "stage7b_signed_bracket_solver.py",
                         "stage7b_signed_bracket_config.py",
                         "run_stage7b_signed_bracket.py"):
            self.assertIn(required, FROZEN_SOURCES)
        self.assertNotIn("stage7b_signed_bracket_gate.py", FROZEN_SOURCES)
        self.assertNotIn("reduce_stage7b_signed_bracket.py", FROZEN_SOURCES)
        self.assertEqual(len(REDUCER_SOURCES), len(set(REDUCER_SOURCES)))
        self.assertIn("reduce_stage7b_signed_bracket.py", REDUCER_SOURCES)

    def test_jsonable_fraction_mapping(self):
        payload = {"a": Fraction(3, 4), "b": [Fraction(1, 2), 7],
                   "c": {"d": Fraction(0)}}
        self.assertEqual(
            _jsonable(payload),
            {"a": "3/4", "b": ["1/2", 7], "c": {"d": "0/1"}})

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
        return population, vitals

    @classmethod
    def _runner_format_artifact(cls) -> dict:
        """Runner-format raw artifact from a 30-tick exploratory window."""
        population, vitals = cls._run_short_shared()
        config_echo = endpoint_configuration()
        config_echo["window_ticks_W"] = 30
        schedules: dict[str, dict] = {}
        certificates: dict[str, dict] = {}
        for genotype_a in cohort_genotypes(vitals):
            schedule = exposure_schedule(vitals, genotype_a)
            c_x = lotka_coefficients(schedule)
            certificate = full_line_certified_bracket(c_x)
            exported = {
                "status": certificate["status"],
                "L0_exact": fmt(certificate["L0_exact"]),
            }
            if certificate["status"] in FINITE_ROOT_STATUSES:
                exported.update({
                    "r_lo": fmt(certificate["r_lo"]),
                    "r_hi": fmt(certificate["r_hi"]),
                })
            schedules[str(genotype_a)] = {
                "cohort_size": schedule["cohort_size"],
                "died": schedule["died"],
                "censored": schedule["censored"],
                "exposure_member_ticks": schedule["exposure_member_ticks"],
                "l_actuarial_x": [fmt(v) for v in schedule["l_actuarial_x"]],
                "m_exposure_x": [fmt(v) for v in schedule["m_exposure_x"]],
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
                    "births": [_serialise_birth(birth)
                               for birth in vitals["births"]],
                    "establishments":
                        copy.deepcopy(vitals["establishments"]),
                    "attempt_counters": dict(vitals["attempt_counters"]),
                },
                "cohort_schedules": schedules,
                "solver_certificates": certificates,
            }],
        }

    def test_round_trip_reduces_bit_exact(self):
        raw = self._runner_format_artifact()
        reduced = reduce_artifact(raw)
        self.assertNotIn("reduction", reduced)
        self.assertTrue(reduced["verification"]["recomputation_bit_exact"])
        self.assertEqual(reduced["verification"]["mismatch_count"], 0)
        self.assertEqual(reduced["decision_rule_input"]
                         ["minimum_contrast_delta_r_min"], "1/100")
        self.assertIn(reduced["outcome"]["pair_contrast_class"],
                      ("DEGENERATE_REPLICATION", "ESTABLISHED_CONTRAST",
                       "NO_ESTABLISHED_CONTRAST"))
        self.assertIn("mediator", reduced["interpretation_limits"])

    def test_tampered_endpoint_classifies_reduction_mismatch(self):
        raw = self._runner_format_artifact()
        raw["replicates"][0]["cohort_schedules"]["102"][
            "m_exposure_x"][0] = "999/1"
        reduced = reduce_artifact(raw)
        self.assertEqual(reduced.get("reduction"), "REDUCTION_MISMATCH")
        self.assertFalse(reduced["decision_applied"])

    def test_tampered_mediator_also_classifies_mismatch(self):
        raw = self._runner_format_artifact()
        raw["replicates"][0]["cohort_schedules"]["102"][
            "establishment_m_x"][0] = "999/1"
        reduced = reduce_artifact(raw)
        self.assertEqual(reduced.get("reduction"), "REDUCTION_MISMATCH")

    def test_protocol_mismatch_refused_by_main_guard(self):
        raw = self._runner_format_artifact()
        raw["protocol"] = "some-other-protocol"
        self.assertNotEqual(raw["protocol"], PROTOCOL)


if __name__ == "__main__":
    unittest.main()
