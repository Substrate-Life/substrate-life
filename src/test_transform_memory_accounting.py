"""Regression tests for TRANSFORM memory and packet-ledger accounting."""

import unittest

from consts import SHARED_MEMORY_POOL, TRANSFORM_RLE
from organism import Substrate


class TransformMemoryAccountingTests(unittest.TestCase):
    def _loaded_rich_packet(self):
        substrate = Substrate(seed=42, phase_mode="monotonic_rich")
        org = substrate.add_organism([(0,)])
        self.assertIsNotNone(org)
        addr = org.allocate_memory(256)
        self.assertIsNotNone(addr)
        substrate.data_stream.advance_tick()
        self.assertTrue(substrate.read_packet(org, addr, 256))
        packet_id = org.byte_tags[addr]
        self.assertIsNotNone(packet_id)
        return substrate, org, addr, packet_id

    def test_partial_extent_does_not_release_untouched_allocation(self):
        substrate, org, addr, packet_id = self._loaded_rich_packet()
        pool_before = substrate.shared_memory_pool

        reduction, replenishment = substrate.apply_transform(
            org, TRANSFORM_RLE, addr, 128)

        self.assertEqual(reduction, 42)
        self.assertAlmostEqual(replenishment, 65.625)
        self.assertEqual(org.memory_allocations[addr], 256)
        self.assertEqual(substrate.shared_memory_pool, pool_before)

        tags = org.byte_tags[addr:addr + 256]
        self.assertEqual(tags.count(packet_id), 214)
        self.assertTrue(all(tag is None for tag in tags[86:128]))
        self.assertTrue(all(tag == packet_id for tag in tags[128:256]))
        self.assertAlmostEqual(org.packet_energy[packet_id], 234.375)
        self.assertAlmostEqual(org.packet_drawn[packet_id], 65.625)

        self.assertTrue(org.free_memory(addr))
        self.assertEqual(substrate.shared_memory_pool,
                         SHARED_MEMORY_POOL - 64)
        self.assertNotIn(packet_id, org.packet_energy)

    def test_full_extent_releases_only_reduced_bytes(self):
        substrate, org, addr, packet_id = self._loaded_rich_packet()
        pool_before = substrate.shared_memory_pool

        reduction, replenishment = substrate.apply_transform(
            org, TRANSFORM_RLE, addr, 256)

        self.assertEqual(reduction, 84)
        self.assertAlmostEqual(replenishment, 131.25)
        self.assertEqual(org.memory_allocations[addr], 172)
        self.assertEqual(substrate.shared_memory_pool, pool_before + 84)
        self.assertEqual(
            org.byte_tags[addr:addr + 256].count(packet_id), 172)
        self.assertAlmostEqual(org.packet_energy[packet_id], 168.75)
        self.assertAlmostEqual(org.packet_drawn[packet_id], 131.25)

        self.assertTrue(org.free_memory(addr))
        self.assertEqual(substrate.shared_memory_pool,
                         SHARED_MEMORY_POOL - 64)
        self.assertNotIn(packet_id, org.packet_energy)


if __name__ == "__main__":
    unittest.main()
