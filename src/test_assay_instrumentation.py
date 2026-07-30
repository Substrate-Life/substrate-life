"""Regression tests for assay measurement instrumentation."""

import unittest

from consts import DIVIDE, NOP, PACKET_SIZE, TRANSFORM, TRANSFORM_RLE
from engine import InstructionEngine, Simulation
from organism import Substrate


class AssayInstrumentationTests(unittest.TestCase):
    def test_transform_event_persists_live_r4(self):
        sim = Simulation(
            seed=42, phase_mode="monotonic_rich",
            packet_e_rich=500, packet_e_lean=500,
            packet_rate=1, buffer_depth=1,
            initial_buffer_packets=1, population_cap=1)
        sim.seed_efficiency_assay_founders(
            full_count=1, half_count=0, offspring_bouts=2)
        for _ in range(6):
            sim.step()

        [event] = sim.substrate.transform_event_log
        self.assertEqual(event["tick"], 5)
        self.assertEqual(event["lineage_label"], "FULL")
        self.assertEqual(event["extent"], PACKET_SIZE)
        self.assertEqual(event["r4"], 2187)
        self.assertGreater(event["replenishment"], 0)
        founder = next(iter(sim.substrate.organisms.values()))
        self.assertEqual(founder.first_positive_extraction_tick, 5)

    def test_death_stage_uses_first_positive_extraction_not_static_gate(self):
        substrate = Substrate(seed=42, phase_mode="monotonic_rich")
        org = substrate.add_organism([(NOP,)], reserve=1,
                                     lineage_label="HALF")
        org.first_positive_extraction_tick = 9
        substrate.tick = 12
        substrate.remove_organism(org.id, "test death")

        death = substrate.ancestry[-1]
        self.assertEqual(death["first_positive_extraction_tick"], 9)
        self.assertTrue(death["reached_first_positive_extraction"])
        self.assertEqual(death["death_stage"],
                         "post_extraction_pre_first_offspring")

    def test_divide_event_logs_parent_phenotype_and_outcome(self):
        substrate = Substrate(seed=42, phase_mode="monotonic_rich")
        parent = substrate.add_organism(
            [(NOP,)], reserve=100, lineage_label="HALF")
        parent.registers[5] = 128
        parent.last_transform_op = TRANSFORM_RLE
        parent.last_transform_extent = 128
        addr = parent.allocate_memory(64)
        parent.gestation_region = addr
        parent.gestation_size = 64
        parent.gestation_buffer = [(NOP,)]
        substrate.tick = 7

        InstructionEngine(substrate)._execute_instr(parent, DIVIDE, ())

        event = substrate.divide_event_log[-1]
        self.assertEqual(event["tick"], 7)
        self.assertEqual(event["parent_id"], parent.id)
        self.assertEqual(event["resolved_transform_extent"], 128)
        self.assertTrue(event["offspring_instantiated"])
        self.assertIsNone(event["materialization_failure_reason"])
        self.assertIsNotNone(event["offspring_id"])
        self.assertEqual(event["transfer_reserve"], 50)

    def test_lineage_inherits_and_first_divide_survives_death(self):
        substrate = Substrate(seed=42, phase_mode="monotonic_rich")
        parent = substrate.add_organism(
            [(NOP,)], reserve=100, lineage_label="HALF")
        self.assertIsNotNone(parent)
        self.assertEqual(parent.founder_lineage_id, parent.id)
        parent.registers[5] = 128
        addr = parent.allocate_memory(64)
        parent.gestation_region = addr
        parent.gestation_size = 64
        parent.gestation_buffer = [(NOP,)]
        substrate.tick = 7

        offspring_id = substrate.reproduce(parent)

        self.assertIsNotNone(offspring_id)
        offspring = substrate.organisms[offspring_id]
        self.assertEqual(offspring.lineage_label, "HALF")
        self.assertEqual(offspring.founder_lineage_id,
                         parent.founder_lineage_id)
        self.assertEqual(parent.first_divide_tick, 7)
        self.assertEqual(substrate.birth_log[-1]["lineage_label"], "HALF")
        self.assertEqual(substrate.birth_log[-1]["founder_lineage_id"],
                         parent.founder_lineage_id)
        self.assertEqual(substrate.birth_log[-1]["birth_reserve"], 50)

        substrate.remove_organism(parent.id, "test death")
        death = substrate.ancestry[-1]
        self.assertEqual(death["lineage_label"], "HALF")
        self.assertEqual(death["founder_lineage_id"],
                         parent.founder_lineage_id)
        self.assertEqual(death["first_divide_tick"], 7)
        self.assertEqual(death["death_stage"],
                         "post_first_offspring_instantiation")
        self.assertEqual(death["cause"], "test death")

    def test_transform_logs_resolved_execution_not_ancestry(self):
        substrate = Substrate(seed=42, phase_mode="monotonic_rich")
        org = substrate.add_organism([(NOP,)], lineage_label="FULL")
        self.assertIsNotNone(org)
        org.registers[0] = 128
        engine = InstructionEngine(substrate)

        engine._execute_instr(org, TRANSFORM,
                              (TRANSFORM_RLE, 0, 0))

        self.assertEqual(org.lineage_label, "FULL")
        self.assertEqual(org.last_transform_op, TRANSFORM_RLE)
        self.assertEqual(org.last_transform_extent, 128)
        self.assertEqual(org.last_transform_tick, 0)
        self.assertEqual(
            org.transform_execution_counts[(TRANSFORM_RLE, 128)], 1)

    def test_capture_fraction_counts_only_valid_full_reads(self):
        substrate = Substrate(seed=42, phase_mode="monotonic_rich")
        org = substrate.add_organism([(NOP,)])
        self.assertIsNotNone(org)
        addr = org.allocate_memory(PACKET_SIZE)
        substrate.data_stream.advance_tick()

        substrate.tick = 4
        self.assertTrue(substrate.read_packet(org, addr, PACKET_SIZE))
        substrate.data_stream.buffer.clear()
        substrate.tick = 16
        self.assertFalse(substrate.read_packet(org, addr, PACKET_SIZE))
        self.assertFalse(substrate.read_packet(org, addr, 128))

        self.assertEqual(substrate.capture_attempts_total, 2)
        self.assertEqual(substrate.capture_successes_total, 1)
        self.assertEqual(substrate.invalid_read_attempts_total, 1)
        self.assertEqual(len(substrate.read_event_log), 2)
        first, recurrent = substrate.read_event_log
        self.assertTrue(first["is_first_valid_read"])
        self.assertEqual(first["age"], 4)
        self.assertTrue(first["capture_success"])
        self.assertFalse(recurrent["is_first_valid_read"])
        self.assertEqual(recurrent["read_interval"], 12)
        self.assertFalse(recurrent["capture_success"])

    def test_simulation_saves_per_tick_capture_history(self):
        sim = Simulation(seed=42, phase_mode="monotonic_rich")
        sim.seed_m1_block(tau_r5=51)
        for _ in range(6):
            sim.step()

        records_with_reads = [
            row for row in sim.substrate.capture_history
            if row["valid_read_attempts"] > 0
        ]
        self.assertTrue(records_with_reads)
        row = records_with_reads[0]
        self.assertEqual(row["capture_successes"], 1)
        self.assertEqual(row["capture_fraction"], 1.0)
        self.assertIn("buffer_occupancy", row)
        self.assertIn("shared_memory_pool", row)
        self.assertEqual(
            row["committed_memory"],
            sim.substrate.initial_shared_memory_pool -
            row["shared_memory_pool"])
        self.assertIn("memory_allocation_failures_total", row)


if __name__ == "__main__":
    unittest.main()
