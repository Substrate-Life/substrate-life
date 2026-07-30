"""Executable regression tests for the Stage 7 isolated Slice 1."""

import unittest
from fractions import Fraction

from datastream import DataStream
from stage7_slice1 import (
    INITIAL_SHARED_MEMORY_POOL,
    MIN_WORKING_MEMORY,
    MemoryLedger,
    PacketLedger,
    SliceOrganism,
    run_slice1_trace,
)


class Stage7Slice1Tests(unittest.TestCase):
    def test_full_cycle_closes_reserve_packet_and_memory_ledgers(self):
        trace = run_slice1_trace()

        self.assertTrue(trace["reserve"]["closed"])
        self.assertEqual(trace["reserve"]["lhs"], Fraction(12567, 80))
        self.assertEqual(trace["reserve"]["rhs"], Fraction(12567, 80))
        self.assertEqual(trace["reserve"]["net_income"], Fraction(100))

        self.assertTrue(trace["packet"]["closed"])
        self.assertEqual(trace["packet"]["budget_remaining"], Fraction(200))
        self.assertEqual(trace["packet"]["drawn_s"], Fraction(60))
        self.assertEqual(trace["packet"]["drawn_r"], Fraction(40))

        self.assertTrue(trace["memory"]["closed"])
        self.assertEqual(trace["memory"]["free_pool"], 788)
        self.assertEqual(trace["memory"]["somatic_active"], 236)
        self.assertEqual(trace["memory"]["gestation"], 0)
        self.assertEqual(trace["memory"]["corpse_reserved"], 0)
        self.assertEqual(trace["memory"]["checkpoints"], 8)

    def test_provisioning_precedes_failed_and_successful_reversal(self):
        trace = run_slice1_trace()
        event_names = [event["event"] for event in trace["events"]]

        provision_index = event_names.index("provision_committed")
        failed_index = event_names.index("reversal_failed")
        successful_index = event_names.index("partial_reversal")
        self.assertLess(provision_index, failed_index)
        self.assertLess(failed_index, successful_index)

        failure = trace["events"][failed_index]
        self.assertEqual(failure["reason"], "REVERSAL_ACCOUNT_UNAVAILABLE")
        self.assertEqual(failure["input_bytes"], 80)
        self.assertEqual(failure["output_bytes"], 160)
        self.assertEqual(failure["debit_s"], Fraction(75))
        self.assertEqual(failure["debit_r"], Fraction(50))

    def test_r_zero_fails_reproductive_effect_without_cross_subsidy(self):
        memory = MemoryLedger()
        organism = SliceOrganism(
            "parent", memory, s=Fraction(100), r=Fraction(0))
        pool_before = memory.free_pool

        self.assertFalse(organism.allocate_offspring(MIN_WORKING_MEMORY))

        self.assertEqual(organism.r, Fraction(0))
        self.assertEqual(organism.c_r, Fraction(0))
        self.assertEqual(organism.s, Fraction(494, 5))
        self.assertEqual(organism.c_s, Fraction(6, 5))
        self.assertEqual(memory.free_pool, pool_before)
        self.assertEqual(memory.gestation, {})
        self.assertEqual(
            memory.free_pool
            + sum(memory.somatic_active.values())
            + sum(memory.gestation.values())
            + sum(memory.corpse_reserved.values()),
            INITIAL_SHARED_MEMORY_POOL,
        )

    def test_failed_post_provision_reversal_is_packet_atomic(self):
        memory = MemoryLedger()
        organism = SliceOrganism(
            "parent", memory, s=Fraction(100), r=Fraction(0))
        source = DataStream(seed=42, phase_mode="monotonic_rich").generate_packet(0)
        packet = PacketLedger(
            packet_id=7, initial_budget=Fraction(300),
            max_reducible=source.max_reducible)
        compressed = organism.forage_rle(packet, source.data)
        self.assertTrue(organism.allocate_offspring())
        self.assertTrue(organism.copy_block(11))
        self.assertIsNotNone(organism.divide_and_provision("child"))

        packet_before = (
            packet.budget_remaining, packet.drawn_s, packet.drawn_r)
        r_before = organism.r
        self.assertFalse(organism.reverse_rle(packet, compressed, extent=80))

        self.assertEqual(organism.r, r_before)
        self.assertEqual(
            (packet.budget_remaining, packet.drawn_s, packet.drawn_r),
            packet_before,
        )
        packet.assert_closed()

    def test_reversal_uses_packet_provenance_not_current_alpha(self):
        memory = MemoryLedger()
        organism = SliceOrganism(
            "parent", memory, s=Fraction(100), r=Fraction(0))
        source = DataStream(seed=42, phase_mode="monotonic_rich").generate_packet(0)
        packet = PacketLedger(
            packet_id=8, initial_budget=Fraction(300),
            max_reducible=source.max_reducible)
        compressed = organism.forage_rle(packet, source.data)

        # Lifetime mutation is outside Slice 1; this deliberate perturbation
        # proves reversal nevertheless follows stored provenance, not current A.
        organism.a = 0
        self.assertTrue(organism.reverse_rle(packet, compressed, extent=20))
        event = organism.events[-1]
        self.assertEqual(event["event"], "partial_reversal")
        self.assertEqual(event["debit_s"], Fraction(75, 4))
        self.assertEqual(event["debit_r"], Fraction(25, 2))
        self.assertEqual(packet.drawn_s, Fraction(60))
        self.assertEqual(packet.drawn_r, Fraction(40))
        packet.assert_closed()

    def test_gestation_release_is_exactly_once(self):
        memory = MemoryLedger()
        organism = SliceOrganism(
            "parent", memory, s=Fraction(100), r=Fraction(100))
        self.assertTrue(organism.allocate_offspring())
        memory.release_gestation("parent")

        with self.assertRaises(ValueError):
            memory.release_gestation("parent")

        self.assertEqual(
            sum(memory.totals().values()), INITIAL_SHARED_MEMORY_POOL)

    def test_invalid_trait_domains_are_rejected(self):
        cases = [
            {"d": 0, "a": 0, "t": 0},
            {"d": 255, "a": -1, "t": 0},
            {"d": 255, "a": 256, "t": 0},
            {"d": 255, "a": 0, "t": -1},
            {"d": 255, "a": 0, "t": 256},
        ]
        for traits in cases:
            with self.subTest(traits=traits), self.assertRaises(ValueError):
                SliceOrganism(
                    "parent", MemoryLedger(), s=Fraction(100),
                    r=Fraction(0), **traits)


if __name__ == "__main__":
    unittest.main()
