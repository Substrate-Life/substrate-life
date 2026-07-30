"""Regression tests for realised treatment-parameter readback."""

import unittest

from consts import ALLOC_OFFSPRING, AND, COPY_BLOCK, DIVIDE, JUMPZ
from engine import Simulation, conditional_efficiency_assay_genome


class RealisedParameterHeaderTests(unittest.TestCase):
    def test_header_exposes_birth_and_cap_semantics(self):
        params = Simulation(seed=1).realised_parameters()
        self.assertEqual(params["offspring_viability_gate"], "none")
        self.assertEqual(
            params["cap_victim_sampling"],
            "uniform_all_incumbents_including_parent")

    def test_conditional_three_bout_genome_has_equal_length_paths(self):
        full = conditional_efficiency_assay_genome(256)
        half = conditional_efficiency_assay_genome(128)
        self.assertEqual(len(full), 23)
        self.assertEqual(len(half), 23)
        self.assertEqual(full[:5], half[:5])
        self.assertEqual(full[6:], half[6:])
        self.assertEqual(full[13], (AND, 7, 4, 2048))
        self.assertEqual(full[14], (JUMPZ, 7, 19))
        self.assertEqual(
            [instruction[0] for instruction in full].count(DIVIDE), 3)

    def test_three_bout_assay_has_fresh_copy_path_for_each_birth(self):
        sim = Simulation(
            seed=201, phase_mode="monotonic_rich", population_cap=1)
        [oid] = sim.seed_efficiency_assay_founders(
            full_count=1, half_count=0, offspring_bouts=3)
        genome = sim.substrate.organisms[oid].genome

        self.assertEqual(len(genome), 17)
        self.assertEqual(sim.substrate.organisms[oid].registers[6], 0)
        self.assertEqual(
            [instruction[0] for instruction in genome].count(
                ALLOC_OFFSPRING), 3)
        self.assertEqual(
            [instruction[0] for instruction in genome].count(COPY_BLOCK), 3)
        self.assertEqual(
            [instruction[0] for instruction in genome].count(DIVIDE), 3)

    def test_efficiency_assay_seeds_directly_at_cap(self):
        sim = Simulation(
            seed=201,
            phase_mode="monotonic_rich",
            packet_e_rich=500,
            packet_e_lean=500,
            packet_rate=11,
            buffer_depth=132,
            population_cap=155,
            initial_buffer_packets=132,
        )
        ids = sim.seed_efficiency_assay_founders()
        labels = [sim.substrate.organisms[oid].lineage_label for oid in ids]

        self.assertEqual(len(ids), 155)
        self.assertEqual(labels.count("FULL"), 78)
        self.assertEqual(labels.count("HALF"), 77)
        self.assertEqual(labels[:4], ["FULL", "HALF", "FULL", "HALF"])
        self.assertTrue(all(sim.substrate.organisms[oid].pc == 0
                            for oid in ids))
        self.assertTrue(all(sim.substrate.organisms[oid].execution_reserve == 100
                            for oid in ids))
        self.assertEqual(sim.substrate.shared_memory_pool, 81920 - 155 * 64)
        self.assertEqual(sim.substrate.memory_allocation_failures_total, 0)

    def test_efficiency_assay_first_expression_precedes_divide(self):
        sim = Simulation(
            seed=201,
            phase_mode="monotonic_rich",
            packet_e_rich=500,
            packet_e_lean=500,
            packet_rate=11,
            buffer_depth=132,
            population_cap=155,
            initial_buffer_packets=132,
        )
        sim.seed_efficiency_assay_founders()
        for _ in range(6):
            sim.step()

        reads = [row for row in sim.substrate.capture_history
                 if row["valid_read_attempts"]]
        self.assertEqual(len(reads), 1)
        self.assertEqual(reads[0]["tick"], 4)
        self.assertEqual(reads[0]["valid_read_attempts"], 155)
        self.assertEqual(reads[0]["capture_successes"], 132)
        self.assertAlmostEqual(reads[0]["capture_fraction"], 132 / 155)
        self.assertEqual(len(sim.substrate.organisms), 155)
        self.assertEqual(len(sim.substrate.divide_event_log), 0)
        self.assertEqual(sim.substrate.memory_allocation_failures_total, 0)
        extents = [org.last_transform_extent
                   for org in sim.substrate.organisms.values()]
        self.assertEqual(extents.count(256), 78)
        self.assertEqual(extents.count(128), 77)

    def test_assay_buffer_preserves_one_cycle_supply(self):
        sim = Simulation(
            seed=201,
            phase_mode="monotonic_rich",
            packet_e_rich=500,
            packet_e_lean=500,
            packet_rate=11,
            buffer_depth=132,
            population_cap=155,
            initial_buffer_packets=132,
        )
        self.assertEqual(len(sim.substrate.data_stream.buffer), 132)
        successes = sum(
            sim.substrate.data_stream.read() is not None for _ in range(155))
        self.assertEqual(successes, 132)
        self.assertAlmostEqual(successes / 155, 132 / 155)

    def test_header_reads_custom_energy_from_live_stream(self):
        sim = Simulation(
            seed=17,
            phase_mode="monotonic_rich",
            packet_e_rich=500,
            packet_e_lean=275,
            packet_rate=11,
            buffer_depth=132,
            population_cap=155,
            initial_buffer_packets=132,
        )

        realised = sim.realised_parameters()
        self.assertEqual(realised["seed"], 17)
        self.assertEqual(realised["phase_mode"], "monotonic_rich")
        self.assertEqual(realised["packet_e_rich"], 500)
        self.assertEqual(realised["packet_e_lean"], 275)
        self.assertEqual(realised["packet_rate"], 11)
        self.assertEqual(realised["buffer_depth"], 132)
        self.assertEqual(realised["population_cap"], 155)
        self.assertEqual(realised["initial_buffer_packets"], 132)
        self.assertEqual(realised["minimum_working_memory"], 64)
        self.assertEqual(realised["shared_memory_pool_initial"], 81920)

        memory = sim.realised_memory_capacity(320)
        self.assertEqual(memory["memory_pool_bytes"], 81920)
        self.assertEqual(memory["peak_bytes_per_organism"], 320)
        self.assertEqual(memory["synchronous_peak_population_ceiling"], 256)

        sim.substrate.data_stream.advance_tick()
        self.assertEqual(len(sim.substrate.data_stream.buffer), 132)
        packet = sim.substrate.data_stream.read()
        self.assertIsNotNone(packet)
        self.assertEqual(packet.e_budget, 500)

        header = sim.realised_parameter_header()
        self.assertIn("seed=17", header)
        self.assertIn("phase_mode=monotonic_rich", header)
        self.assertIn("packet_e_rich=500", header)
        self.assertIn("packet_e_lean=275", header)
        self.assertIn("packet_rate=11", header)
        self.assertIn("buffer_depth=132", header)
        self.assertIn("population_cap=155", header)
        self.assertIn("initial_buffer_packets=132", header)
        memory_header = sim.realised_memory_capacity_header(320)
        self.assertIn("peak_bytes_per_organism=320", memory_header)
        self.assertIn("synchronous_peak_population_ceiling=256",
                      memory_header)

    def test_lean_stream_uses_live_lean_energy(self):
        sim = Simulation(
            seed=19,
            phase_mode="monotonic_lean",
            packet_e_rich=500,
            packet_e_lean=275,
        )
        sim.substrate.data_stream.advance_tick()
        packet = sim.substrate.data_stream.read()
        self.assertIsNotNone(packet)
        self.assertTrue(packet.is_lean)
        self.assertEqual(packet.e_budget, 275)


if __name__ == "__main__":
    unittest.main()
