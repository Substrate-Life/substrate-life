"""Stage 7B0 block regressions against the registered protocol values.

These tests pin the frozen design-calibration values in
docs/stage-7b-fixed-allocation-channel-preregistration.md.  They are
regressions on disclosed calibration, not prospective predictions, and they
establish no fitness, selection, or population result.
"""

from __future__ import annotations

import unittest
from fractions import Fraction

import stage7b0_blocks as b0


def parse(value):
    """Parse an _frac-serialised rational back into a Fraction."""
    parsed: object = value
    if isinstance(value, str) and "/" in value:
        numerator, denominator = value.split("/")
        parsed = Fraction(int(numerator), int(denominator))
    assert isinstance(parsed, Fraction)
    return parsed


class ProgrammeIdentityTests(unittest.TestCase):

    def test_programme_specification_hash_matches_registration(self):
        self.assertEqual(
            b0.programme_specification_hash(),
            "5ddbf276aa0a836672b1b3011e66974ce9ecd6fedb0758a111c95766f534c344",
        )

    def test_treatment_identity_constants(self):
        self.assertEqual(b0.D, 255)
        self.assertEqual(b0.T, 128)
        self.assertEqual(b0.LOW_A, 102)
        self.assertEqual(b0.HIGH_A, 204)
        self.assertEqual(Fraction(b0.LOW_A, b0.D), Fraction(2, 5))
        self.assertEqual(Fraction(b0.HIGH_A, b0.D), Fraction(4, 5))
        self.assertEqual(Fraction(b0.T, b0.D), Fraction(128, 255))


class BlockATests(unittest.TestCase):

    def setUp(self):
        self.result = b0.block_a()
        self.low = self.result["arms"]["LOW"]
        self.high = self.result["arms"]["HIGH"]

    def test_common_registered_quantities(self):
        post_forage = next(
            checkpoint for checkpoint in self.low["checkpoints"]
            if checkpoint["checkpoint"] == "POST_FORAGE")
        final = self.low["checkpoints"][-1]
        self.assertEqual(parse(post_forage["gross_income"]), Fraction(525, 4))
        self.assertEqual(parse(final["C_S"]), Fraction(879, 40))
        self.assertEqual(parse(final["C_R"]), Fraction(56, 5))

    def test_low_arm_exact_values(self):
        self.assertEqual(
            parse(self.low["child_S_birth"]), Fraction(26432, 1275))
        self.assertEqual(
            parse(self.low["final_parent_S"]), Fraction(6271, 40))
        self.assertEqual(self.low["child_R_birth"], 0)

    def test_high_arm_exact_values(self):
        self.assertEqual(
            parse(self.high["child_S_birth"]), Fraction(60032, 1275))
        self.assertEqual(
            parse(self.high["final_parent_S"]), Fraction(4171, 40))
        self.assertEqual(self.high["child_R_birth"], 0)

    def test_closure_and_memory(self):
        for arm in (self.low, self.high):
            closure = arm["reserve_closure"]
            self.assertTrue(closure["closed"])
            self.assertEqual(parse(closure["lhs"]), parse(closure["rhs"]))
            self.assertTrue(arm["memory_closed"])

    def test_allocation_split_by_arm(self):
        # Y_R=(A/D)Y exactly: LOW draws 105/2 to R, HIGH draws 105.  The
        # split is read from packet provenance (drawn_R/drawn_S), which the
        # harness records at each checkpoint.
        for arm, expected_r in ((self.low, Fraction(105, 2)),
                                (self.high, Fraction(105))):
            post_forage = next(
                checkpoint for checkpoint in arm["checkpoints"]
                if checkpoint["checkpoint"] == "POST_FORAGE")
            packet = post_forage["packets"][0]
            delta_r = parse(packet["drawn_R"])
            delta_s = parse(packet["drawn_S"])
            quantity = parse(post_forage["gross_income"])
            self.assertEqual(delta_r, expected_r)
            self.assertEqual(delta_s + delta_r, quantity)


class BlockBTests(unittest.TestCase):

    def setUp(self):
        self.result = b0.block_b()

    def test_both_arms_realise_registered_two_generation_sequence(self):
        for name, arm in self.result["arms"].items():
            with self.subTest(arm=name):
                self.assertEqual(arm["admitted_births_total"], 3)
                self.assertEqual(arm["hazard_removals_total"], 0)
                self.assertEqual(arm["rejected_births_total"], 0)
                self.assertEqual(arm["packet_evictions"], 0)
                self.assertEqual(arm["final_live_census"], 4)
                self.assertTrue(arm["closure_ok"])

    def test_newborn_deferral_ordering(self):
        for name, arm in self.result["arms"].items():
            with self.subTest(arm=name):
                tick_zero = arm["tick_snapshots"][0]
                tick_one = arm["tick_snapshots"][1]
                self.assertEqual(tick_zero["newborn_ids"], ["org-1"])
                self.assertEqual(tick_one["admitted_births"], 2)

    def test_realised_traits_equal_registration(self):
        for name, arm in self.result["arms"].items():
            population_a = arm["A"]
            self.assertIn([population_a, b0.T, b0.D],
                          [[a, t, d] for a, t, d in arm["trait_values"]])


class BlockCTests(unittest.TestCase):

    def setUp(self):
        self.result = b0.block_c()

    def test_first_cycle_failure_state_exact(self):
        expected = {
            "LOW": (Fraction(6671, 80), Fraction(7, 4)),
            "HIGH": (Fraction(6531, 80), Fraction(7, 2)),
        }
        for name, (expected_s, expected_r) in expected.items():
            failure = self.result["arms"][name][
                "first_cycle_post_alloc_failure"]
            self.assertEqual(parse(failure["parent_S"]), expected_s)
            self.assertEqual(parse(failure["parent_R"]), expected_r)

    def test_recovery_on_second_packet_without_subsidy(self):
        for name, arm in self.result["arms"].items():
            with self.subTest(arm=name):
                self.assertTrue(arm["recovered"])
                events = [event["event"] for event in arm["events"]]
                # Exactly two FORAGE opportunities; recovery DIVIDE committed.
                self.assertEqual(events.count("FORAGE_RLE"), 2)
                self.assertEqual(events.count("ALLOC_OFFSPRING"), 2)
                self.assertEqual(events[-1], "DIVIDE")

    def test_first_packet_budget_was_registered_ten(self):
        for name, arm in self.result["arms"].items():
            failure = arm["first_cycle_post_alloc_failure"]
            packet = failure["packets"][0]
            self.assertEqual(parse(packet["initial_budget"]), Fraction(10))


class BlockDTests(unittest.TestCase):

    def setUp(self):
        self.result = b0.block_d()

    def test_topology_counts_identical_across_permutation(self):
        for fixture_name, fixture in self.result["fixtures"].items():
            with self.subTest(fixture=fixture_name):
                captures = fixture["captures_by_organism"]
                failures = fixture["capture_failures_by_organism"]
                rejections = fixture["full_census_rejections_by_organism"]
                self.assertEqual(captures.get("org-0"), 4)
                self.assertNotIn("org-0", failures)
                self.assertEqual(failures.get("org-1"), 4)
                self.assertEqual(rejections.get("org-0"), 4)
                self.assertNotIn("org-1", rejections)
                self.assertEqual(fixture["admitted_births_total"], 0)
                self.assertEqual(fixture["packet_evictions"], 0)
                self.assertEqual(fixture["final_live_census"], 2)
                self.assertTrue(fixture["closure_ok"])

    def test_label_permutation_moves_history_with_scheduler_id(self):
        fixtures = self.result["fixtures"]
        d1 = fixtures["D1_org0_LOW_org1_HIGH"]["captures_by_organism"]
        d2 = fixtures["D2_org0_HIGH_org1_LOW"]["captures_by_organism"]
        # Capture history follows org-0 regardless of which treatment sits
        # there: the topology is configured, not attached to LOW or HIGH.
        self.assertEqual(d1["org-0"], d2["org-0"])
        self.assertEqual(d1.get("org-1", 0), d2.get("org-1", 0))


class BlockETests(unittest.TestCase):

    def setUp(self):
        self.result = b0.block_e()
        self.e1 = self.result["sub_blocks"]["E1_partial_then_complete_return"]
        self.e2 = self.result["sub_blocks"]["E2_spent_credit_atomic_failure"]

    def test_e1_partial_return_provenance_exact(self):
        expected_after_20 = {
            "LOW": (Fraction(200), Fraction(60), Fraction(40)),
            "HIGH": (Fraction(200), Fraction(20), Fraction(80)),
        }
        for name, (budget, drawn_s, drawn_r) in expected_after_20.items():
            packet = self.e1[name]["after_extent_20"]["packets"][0]
            self.assertEqual(parse(packet["budget_remaining"]), budget)
            self.assertEqual(parse(packet["drawn_S"]), drawn_s)
            self.assertEqual(parse(packet["drawn_R"]), drawn_r)

    def test_e1_complete_return_restores_full_budget(self):
        for name, arm in self.e1.items():
            packet = arm["after_extent_64"]["packets"][0]
            self.assertEqual(parse(packet["budget_remaining"]), Fraction(300))
            self.assertEqual(parse(packet["drawn_S"]), Fraction(0))
            self.assertEqual(parse(packet["drawn_R"]), Fraction(0))

    def test_e2_spent_credit_state_before_attempt_exact(self):
        expected = {
            "LOW": (
                Fraction(52451, 2550),
                (Fraction(675, 4), Fraction(315, 4), Fraction(105, 2)),
            ),
            "HIGH": (
                Fraction(59563, 1275),
                (Fraction(675, 4), Fraction(105, 4), Fraction(105)),
            ),
        }
        for name, (expected_r, expected_packet) in expected.items():
            before = self.e2[name]["before_attempt"]
            self.assertEqual(parse(before["parent_R"]), expected_r)
            packet = before["packets"][0]
            got = tuple(
                parse(field) for field in
                (packet["budget_remaining"],
                 packet["drawn_S"],
                 packet["drawn_R"]))
            self.assertEqual(got, expected_packet)

    def test_e2_failure_is_atomic_with_sunk_somatic_charge_only(self):
        for name, arm in self.e2.items():
            with self.subTest(arm=name):
                self.assertFalse(arm["atomic"] is not True)
                before = arm["before_attempt"]
                after = arm["after_failed_attempt"]
                # Parent R unchanged; every packet field unchanged.
                self.assertEqual(
                    parse(before["parent_R"]), parse(after["parent_R"]))
                before_packet = before["packets"][0]
                after_packet = after["packets"][0]
                for field_name in ("budget_remaining", "drawn_S", "drawn_R"):
                    self.assertEqual(
                        parse(before_packet[field_name]),
                        parse(after_packet[field_name]))
                # Parent S alone decreased by the registered 859/160.
                s_delta = parse(before["parent_S"]) - parse(after["parent_S"])
                self.assertEqual(s_delta, Fraction(859, 160))
                self.assertEqual(
                    arm["failure_code"], "REVERSAL_ACCOUNT_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
