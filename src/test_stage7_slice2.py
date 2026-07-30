"""TDD regressions for Stage 7 Slice 2A population mechanics."""

import unittest
from fractions import Fraction
import hashlib
import tempfile
from pathlib import Path

from stage7_slice2 import Stage7Population, run_slice2_trace


class Stage7Slice2PopulationTests(unittest.TestCase):
    def test_trace_runner_writes_artifact_with_source_manifest(self):
        from run_stage7_slice2_trace import write_trace_artifact

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "trace.json"
            artifact = write_trace_artifact(output, ticks=2)

            self.assertFalse(artifact["assay_run"])
            self.assertEqual(artifact["configuration"]["ticks"], 2)
            self.assertTrue(artifact["final_reserve"]["closed"])
            self.assertTrue(artifact["final_packets_closed"])
            self.assertTrue(artifact["final_memory_closed"])
            manifest = artifact["source_manifest"]
            self.assertIn("stage7_slice1.py", manifest)
            self.assertIn("stage7_slice2.py", manifest)
            self.assertIn("test_stage7_slice2.py", manifest)
            self.assertIn("run_stage7_slice2_trace.py", manifest)
            for name, entry in manifest.items():
                source = Path(__file__).with_name(name)
                self.assertEqual(entry["sha256"],
                                 hashlib.sha256(source.read_bytes()).hexdigest())
                self.assertEqual(entry["bytes"], source.stat().st_size)
                self.assertEqual(entry["mtime_ns"], source.stat().st_mtime_ns)

    def test_packet_ledger_uses_live_source_budget(self):
        population = Stage7Population(
            capacity=1,
            founder_count=1,
            founder_s=Fraction(100),
            memory_pool=2048,
            packet_energy=Fraction(240),
        )

        snapshot = population.step()

        self.assertEqual(population.packets[0].initial_budget, Fraction(240))
        self.assertTrue(snapshot["packets_closed"])

    def test_global_packet_closure_includes_unread_buffer_packets(self):
        population = Stage7Population(
            capacity=1,
            founder_count=1,
            founder_s=Fraction(100),
            memory_pool=2048,
            packet_rate=5,
            buffer_depth=8,
        )
        population.step()
        self.assertEqual(len(population.packet_buffer.buffer), 4)

        buffered = population.packet_buffer.buffer[0]
        buffered.e_budget -= 1

        with self.assertRaises(AssertionError):
            population.assert_all_ledgers("injected_buffer_corruption")

    def test_failed_reproductive_work_releases_cycle_gestation(self):
        population = Stage7Population(
            capacity=1,
            founder_count=1,
            founder_s=Fraction(100),
            memory_pool=2048,
            packet_energy=Fraction(35),
            packet_rate=1,
        )

        first = population.step()

        self.assertNotIn("org-0", population.memory.gestation)
        self.assertEqual(first["admitted_births"], 0)
        self.assertTrue(first["reserve_closed"])
        self.assertTrue(first["memory_closed"])

        second = population.step()
        self.assertTrue(second["reserve_closed"])
        self.assertTrue(second["memory_closed"])

    def test_gestation_upkeep_r_failure_is_recoverable_population_event(self):
        population = Stage7Population(
            capacity=1,
            founder_count=1,
            founder_s=Fraction(100),
            memory_pool=2048,
            packet_energy=Fraction(29),
            packet_rate=1,
        )

        snapshot = population.step()

        self.assertEqual(snapshot["reproductive_failures"], 1)
        self.assertEqual(snapshot["live_census"], 1)
        self.assertNotIn("org-0", population.memory.gestation)
        self.assertEqual(population.members["org-0"].organism.r, Fraction(0))
        self.assertTrue(snapshot["reserve_closed"])
        self.assertTrue(snapshot["packets_closed"])
        self.assertTrue(snapshot["memory_closed"])

    def test_memory_pressure_blocks_attempt_without_death_or_leak(self):
        population = Stage7Population(
            capacity=2,
            founder_count=2,
            founder_s=Fraction(100),
            memory_pool=128,
            packet_rate=5,
        )

        snapshot = population.step()

        self.assertEqual(snapshot["memory_blocked_attempts"], 2)
        self.assertEqual(snapshot["live_census"], 2)
        self.assertEqual(snapshot["hazard_deaths"], [])
        self.assertEqual(population.memory.totals(), {
            "free_pool": 0,
            "somatic_active": 128,
            "gestation": 0,
            "corpse_reserved": 0,
        })
        self.assertEqual(len(population.packets), 2)
        self.assertEqual(population.members["org-0"].organism.s,
                         Fraction(449, 5))
        self.assertEqual(population.members["org-1"].organism.s,
                         Fraction(449, 5))
        self.assertTrue(snapshot["reserve_closed"])
        self.assertTrue(snapshot["packets_closed"])
        self.assertTrue(snapshot["memory_closed"])

    def test_hazard_precedes_scheduler_and_birth_fills_without_displacement(self):
        population = Stage7Population(
            capacity=2,
            founder_count=2,
            founder_s=Fraction(100),
            memory_pool=4096,
            hazard_schedule={0: {"org-0"}},
            corpse_ttl=2,
        )

        snapshot = population.step()

        self.assertEqual(snapshot["hazard_deaths"], ["org-0"])
        self.assertEqual(snapshot["admitted_births"], 1)
        self.assertEqual(snapshot["rejected_births"], 0)
        self.assertEqual(snapshot["live_census"], 2)
        self.assertEqual(snapshot["displacements"], 0)
        child_id = snapshot["newborn_ids"][0]
        self.assertEqual(population.members[child_id].born_tick, 0)
        self.assertIsNone(population.members[child_id].last_run_tick)
        self.assertEqual(
            (population.members[child_id].organism.a,
             population.members[child_id].organism.t,
             population.members[child_id].organism.d),
            (102, 51, 255),
        )
        self.assertTrue(snapshot["reserve_closed"])
        self.assertTrue(snapshot["packets_closed"])
        self.assertTrue(snapshot["memory_closed"])

    def test_full_census_rejects_birth_without_provision_or_displacement(self):
        population = Stage7Population(
            capacity=1,
            founder_count=1,
            founder_s=Fraction(100),
            memory_pool=2048,
            hazard_schedule={},
        )
        parent = population.members["org-0"].organism

        snapshot = population.step()

        self.assertEqual(snapshot["admitted_births"], 0)
        self.assertEqual(snapshot["rejected_births"], 1)
        self.assertEqual(snapshot["live_census"], 1)
        self.assertEqual(snapshot["displacements"], 0)
        self.assertEqual(parent.committed, Fraction(0))
        self.assertNotIn("org-0", population.memory.gestation)
        self.assertIn("org-0", population.memory.somatic_active)
        rejection = next(
            event for event in population.event_log
            if event["event"] == "birth_rejected_no_vacancy")
        self.assertEqual(rejection["parent_id"], "org-0")
        self.assertTrue(snapshot["reserve_closed"])
        self.assertTrue(snapshot["packets_closed"])
        self.assertTrue(snapshot["memory_closed"])

    def test_somatic_insufficiency_stalls_until_exogenous_hazard(self):
        population = Stage7Population(
            capacity=1,
            founder_count=1,
            founder_s=Fraction(5),
            memory_pool=1024,
            hazard_schedule={1: {"org-0"}},
            corpse_ttl=2,
        )

        stalled = population.step()

        self.assertEqual(stalled["stalled_census"], 1)
        self.assertEqual(stalled["live_census"], 1)
        self.assertEqual(population.members["org-0"].state, "STALLED")
        self.assertEqual(population.members["org-0"].organism.s, Fraction(5))
        self.assertEqual(stalled["hazard_deaths"], [])
        self.assertTrue(stalled["reserve_closed"])

        removed = population.step()

        self.assertEqual(removed["hazard_deaths"], ["org-0"])
        self.assertEqual(removed["live_census"], 0)
        self.assertEqual(removed["stalled_census"], 0)
        self.assertIn("org-0", population.memory.corpse_reserved)
        self.assertTrue(removed["reserve_closed"])
        self.assertTrue(removed["memory_closed"])

    def test_many_organism_many_tick_trace_closes_without_assay(self):
        trace = run_slice2_trace(ticks=20)

        self.assertEqual(len(trace["ticks"]), 20)
        self.assertTrue(all(tick["reserve_closed"] for tick in trace["ticks"]))
        self.assertTrue(all(tick["packets_closed"] for tick in trace["ticks"]))
        self.assertTrue(all(tick["memory_closed"] for tick in trace["ticks"]))
        self.assertTrue(all(
            checkpoint["reserve_closed"]
            and checkpoint["packets_closed"]
            and checkpoint["memory_closed"]
            for checkpoint in trace["closure_history"]
        ))
        self.assertGreater(trace["counts"]["hazard_death"], 0)
        self.assertGreater(trace["counts"]["birth_admitted"], 0)
        self.assertGreater(trace["counts"]["birth_rejected_no_vacancy"], 0)
        self.assertGreater(trace["counts"]["somatic_stall"], 0)
        self.assertGreater(trace["counts"]["corpse_expired"], 0)
        self.assertGreater(trace["counts"]["packet_capture_failed"], 0)
        self.assertLessEqual(trace["packet_count"], 20 * 5)
        self.assertEqual(trace["counts"].get("displacement", 0), 0)
        self.assertEqual(trace["counts"].get("mutation", 0), 0)
        self.assertLessEqual(max(tick["live_census"] for tick in trace["ticks"]), 8)
        self.assertTrue(trace["final_reserve"]["closed"])
        self.assertTrue(trace["final_packets_closed"])
        self.assertTrue(trace["final_memory_closed"])
        self.assertEqual(trace["trait_values"], [[102, 51, 255]])
        self.assertFalse(trace["assay_run"])
        self.assertEqual(trace["decisions"]["somatic_insufficiency"],
                         "retain_reserve_and_stall_until_hazard")
        self.assertEqual(trace["decisions"]["hazard_phase"],
                         "phenotype_blind_at_tick_start")
        self.assertEqual(trace["decisions"]["admission"],
                         "non_displacing_vacancy_reservation")
        self.assertEqual(trace["decisions"]["scheduler"],
                         "stable_survivor_ids_newborns_next_tick")
        self.assertEqual(trace["decisions"]["mutation"],
                         "disabled_exact_trait_inheritance")


if __name__ == "__main__":
    unittest.main()
