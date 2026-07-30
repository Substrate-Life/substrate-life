"""Regression tests for gestation-allocation release at DIVIDE."""

import unittest

from consts import (
    ALLOC_OFFSPRING, CORPSE_POOL_TTL, DIVIDE, JUMP, NOP,
    MIN_WORKING_MEMORY, SHARED_MEMORY_POOL,
)
from engine import InstructionEngine, Simulation
from organism import Substrate


class GestationMemoryAccountingTests(unittest.TestCase):
    def test_offspring_maturation_delays_execution_but_charges_full_upkeep(self):
        sim = Simulation(
            seed=42, phase_mode="monotonic_rich", population_cap=2,
            offspring_maturation_delay=7)
        parent = sim.substrate.add_organism([(DIVIDE,)], reserve=100)
        parent.registers[5] = 50
        addr = parent.allocate_memory(64)
        parent.gestation_region = addr
        parent.gestation_size = 64
        parent.gestation_buffer = [(NOP,)]

        sim.step()  # offspring is born during tick 0 execution
        offspring_id = sim.substrate.birth_log[-1]["id"]
        offspring = sim.substrate.organisms[offspring_id]
        birth_reserve = sim.substrate.birth_log[-1]["birth_reserve"]
        full_upkeep = offspring.compute_upkeep()
        self.assertEqual(offspring.maturation_remaining, 7)
        self.assertEqual(sim.substrate.birth_log[-1]["maturation_delay"], 7)
        self.assertAlmostEqual(
            offspring.execution_reserve, birth_reserve - full_upkeep)

        for _ in range(7):
            sim.step()
        self.assertIsNone(offspring.last_execution_tick)
        self.assertEqual(offspring.maturation_remaining, 0)
        self.assertAlmostEqual(
            offspring.execution_reserve,
            birth_reserve - 8 * full_upkeep)

        sim.step()
        self.assertEqual(offspring.last_execution_tick, 8)

    def test_cap_event_distinguishes_dead_vacancy_from_live_displacement(self):
        substrate = Substrate(
            seed=0, phase_mode="monotonic_rich", population_cap=2)
        parent = substrate.add_organism([(NOP,)], reserve=100)
        vacancy = substrate.add_organism([(NOP,)], reserve=100)
        substrate.remove_organism(vacancy.id, "same-tick death")
        parent.registers[5] = 128
        addr = parent.allocate_memory(64)
        parent.gestation_region = addr
        parent.gestation_size = 64
        parent.gestation_buffer = [(NOP,)]

        child_id = substrate.reproduce(parent)

        self.assertIsNotNone(child_id)
        replacement = substrate.cap_replacement_log[-1]
        self.assertEqual(replacement["victim_id"], vacancy.id)
        self.assertFalse(replacement["victim_was_live"])
        substrate.remove_organism(child_id, "reserve exhausted")
        summary = substrate.displacement_viability_summary()
        self.assertEqual(summary["all_cap_events"], 1)
        self.assertEqual(summary["live_displacements"], 0)
        self.assertEqual(summary[
            "live_displacements_caused_by_offspring_dying_before_first_extraction"],
            0)
        self.assertIsNone(summary[
            "doomed_offspring_fraction_of_live_displacements"])

    def test_cap_displacement_can_select_nonparent_resident(self):
        substrate = Substrate(
            seed=0, phase_mode="monotonic_rich", population_cap=2)
        parent = substrate.add_organism([(NOP,)], reserve=100)
        resident = substrate.add_organism([(DIVIDE,)], reserve=100)
        parent.registers[5] = 128
        addr = parent.allocate_memory(64)
        parent.gestation_region = addr
        parent.gestation_size = 64
        parent.gestation_buffer = [(NOP,)]

        child_id = substrate.reproduce(parent)

        self.assertIsNotNone(child_id)
        self.assertIn(parent.id, substrate.organisms)
        self.assertNotIn(resident.id, substrate.organisms)
        self.assertIn(child_id, substrate.organisms)
        self.assertEqual(len(substrate.organisms), 2)
        self.assertEqual(substrate.ancestry[-1]["cause"], "displacement")
        replacement = substrate.cap_replacement_log[-1]
        self.assertEqual(replacement["victim_id"], resident.id)
        self.assertFalse(replacement["victim_is_reproducing_parent"])
        self.assertTrue(replacement["victim_was_live"])
        self.assertEqual(replacement["victim_next_opcode"], DIVIDE)
        self.assertTrue(replacement["victim_pending_divide"])

    def test_cap_displacement_can_select_reproducing_parent(self):
        substrate = Substrate(
            seed=2, phase_mode="monotonic_rich", population_cap=2)
        parent = substrate.add_organism([(DIVIDE,)], reserve=100)
        resident = substrate.add_organism([(NOP,)], reserve=100)
        parent.registers[5] = 128
        addr = parent.allocate_memory(64)
        parent.gestation_region = addr
        parent.gestation_size = 64
        parent.gestation_buffer = [(NOP,)]

        alive = InstructionEngine(substrate).execute(parent)
        child_id = substrate.birth_log[-1]["id"]

        self.assertFalse(alive)
        self.assertNotIn(parent.id, substrate.organisms)
        self.assertIn(resident.id, substrate.organisms)
        self.assertIn(child_id, substrate.organisms)
        replacement = substrate.cap_replacement_log[-1]
        self.assertEqual(replacement["victim_id"], parent.id)
        self.assertTrue(replacement["victim_is_reproducing_parent"])
        parent_death = next(row for row in substrate.ancestry
                            if row["id"] == parent.id)
        self.assertEqual(parent_death["cause"], "displacement")
        self.assertEqual(parent_death["first_divide_tick"], substrate.tick)
        self.assertEqual(parent_death["divides"], 1)
        self.assertAlmostEqual(parent_death["terminal_reserve"], 45.0)

    def _parent_with_gestation(self, reserve=100.0, r5=128):
        substrate = Substrate(seed=42, phase_mode="monotonic_rich")
        parent = substrate.add_organism([(NOP,)], reserve=reserve)
        self.assertIsNotNone(parent)
        parent.registers[5] = r5
        addr = parent.allocate_memory(64)
        self.assertIsNotNone(addr)
        parent.gestation_region = addr
        parent.gestation_size = 64
        parent.gestation_buffer = [(NOP,)]
        return substrate, parent, addr

    def test_successful_divide_releases_parent_gestation_allocation(self):
        substrate, parent, gestation_addr = self._parent_with_gestation()

        offspring_id = substrate.reproduce(parent)

        self.assertIsNotNone(offspring_id)
        self.assertNotIn(gestation_addr, parent.memory_allocations)
        self.assertEqual(parent.memory_allocations, {0: 64})
        self.assertEqual(substrate.shared_memory_pool,
                         SHARED_MEMORY_POOL - 2 * 64)

    def test_failed_reallocation_clears_stale_gestation_bout(self):
        substrate, parent, _gestation_addr = self._parent_with_gestation()
        parent.gestation_buffer = [(NOP,)]
        parent.copy_pointer = 1
        # Freeing the old 64-byte gestation block leaves only 64 available;
        # the requested 128-byte replacement therefore fails.
        substrate.shared_memory_pool = 0

        InstructionEngine(substrate)._execute_instr(
            parent, ALLOC_OFFSPRING, (128,))

        self.assertTrue(parent.fail_flag)
        self.assertIsNone(parent.gestation_region)
        self.assertEqual(parent.gestation_size, 0)
        self.assertEqual(parent.gestation_buffer, [])
        self.assertEqual(parent.copy_pointer, 0)
        reserve_before_divide = parent.execution_reserve
        self.assertIsNone(substrate.reproduce(parent))
        self.assertEqual(parent.last_reproduction_failure_reason,
                         "missing_gestation_buffer")
        self.assertEqual(parent.execution_reserve, reserve_before_divide)

    def test_under_endowed_offspring_is_instantiated_and_gestation_released(self):
        substrate, parent, gestation_addr = self._parent_with_gestation(r5=1)

        offspring_id = substrate.reproduce(parent)

        self.assertIsNotNone(offspring_id)
        offspring = substrate.organisms[offspring_id]
        self.assertAlmostEqual(offspring.execution_reserve, 100 / 256)
        self.assertIsNone(parent.last_reproduction_failure_reason)
        self.assertNotIn(gestation_addr, parent.memory_allocations)
        self.assertEqual(parent.memory_allocations, {0: 64})
        self.assertEqual(substrate.shared_memory_pool,
                         SHARED_MEMORY_POOL - 2 * 64)

    def test_memory_failure_precedes_transfer_and_has_no_transfer_field(self):
        substrate, parent, old_gestation = self._parent_with_gestation()
        # Replace the ordinary 64-byte gestation allocation with a VM-reachable
        # one-byte allocation. Releasing it leaves 63 bytes: still below the
        # 64-byte offspring minimum.
        self.assertTrue(parent.free_memory(old_gestation))
        gestation = parent.allocate_memory(1)
        parent.gestation_region = gestation
        parent.gestation_size = 1
        parent.gestation_buffer = [(NOP,)]
        parent.copy_pointer = 1
        parent.genome = [(DIVIDE,)]
        parent.genome_length = 1
        substrate.shared_memory_pool = MIN_WORKING_MEMORY - 2
        reserve_before = parent.execution_reserve

        self.assertFalse(InstructionEngine(substrate).execute(parent))

        event = substrate.divide_event_log[-1]
        self.assertFalse(event["offspring_instantiated"])
        self.assertEqual(event["materialization_failure_reason"],
                         "insufficient_shared_memory")
        self.assertEqual(event["reserve_before_transfer"], reserve_before)
        self.assertEqual(event["reserve_after_transfer"], reserve_before)
        self.assertNotIn("transfer_reserve", event)
        # DIVIDE's ordinary instruction cost is still paid after the failed
        # attempt; the provisioning transfer itself is not debited.
        self.assertAlmostEqual(parent.execution_reserve, reserve_before - 5.0)
        self.assertIsNone(parent.gestation_region)
        self.assertEqual(parent.gestation_buffer, [])
        self.assertEqual(substrate.shared_memory_pool,
                         MIN_WORKING_MEMORY - 1)

    def test_doomed_transfer_is_not_refunded_and_child_memory_returns_once(self):
        substrate, parent, _gestation_addr = self._parent_with_gestation(r5=1)
        initial_parent_reserve = parent.execution_reserve

        offspring_id = substrate.reproduce(parent)
        offspring = substrate.organisms[offspring_id]
        transfer = initial_parent_reserve / 256
        self.assertAlmostEqual(parent.execution_reserve,
                               initial_parent_reserve - transfer)
        self.assertAlmostEqual(offspring.execution_reserve, transfer)
        self.assertAlmostEqual(parent.execution_reserve +
                               offspring.execution_reserve,
                               initial_parent_reserve)

        substrate.remove_organism(offspring_id, "reserve exhausted")
        reserve_after_death = parent.execution_reserve
        self.assertAlmostEqual(reserve_after_death,
                               initial_parent_reserve - transfer)
        self.assertAlmostEqual(substrate.ancestry[-1]["terminal_reserve"],
                               transfer)
        self.assertFalse(substrate.ancestry[-1][
            "reached_first_positive_extraction"])
        self.assertEqual(substrate.corpse_allocated_bytes(), 64)
        self.assertEqual(substrate.shared_memory_pool,
                         SHARED_MEMORY_POOL - 2 * 64)

        substrate.tick = CORPSE_POOL_TTL
        self.assertEqual(substrate.expire_corpse_memory(), 64)
        self.assertEqual(substrate.corpse_allocated_bytes(), 0)
        self.assertEqual(substrate.shared_memory_pool,
                         SHARED_MEMORY_POOL - 64)
        self.assertEqual(substrate.expire_corpse_memory(), 0)
        self.assertEqual(substrate.shared_memory_pool,
                         SHARED_MEMORY_POOL - 64)

    def test_under_endowed_offspring_bears_cap_memory_and_natural_death_costs(self):
        sim = Simulation(
            seed=0, phase_mode="monotonic_rich", population_cap=2)
        parent = sim.substrate.add_organism(
            [(DIVIDE,), (JUMP, 0)], reserve=100)
        resident = sim.substrate.add_organism(
            [(NOP,), (JUMP, 0)], reserve=100)
        parent.registers[5] = 1
        addr = parent.allocate_memory(64)
        parent.gestation_region = addr
        parent.gestation_size = 64
        parent.gestation_buffer = [(NOP,), (JUMP, 0)]

        sim.step()

        birth = next(row for row in sim.substrate.birth_log
                     if row["parent"] == parent.id)
        child = sim.substrate.organisms[birth["id"]]
        self.assertEqual(sim.substrate.cap_replacement_log[-1]["victim_id"],
                         resident.id)
        self.assertTrue(sim.substrate.cap_replacement_log[-1]["victim_was_live"])
        self.assertEqual(child.state, "ACTIVE")
        self.assertAlmostEqual(child.execution_reserve,
                               100 / 256 - child.compute_upkeep())

        sim.step()

        death = next(row for row in sim.substrate.ancestry
                     if row["id"] == child.id)
        self.assertEqual(death["cause"], "reserve exhausted")
        self.assertEqual(death["death_stage"], "pre_first_extraction")
        self.assertFalse(death["reached_first_positive_extraction"])
        displacement = sim.substrate.cap_replacement_log[-1]
        self.assertEqual(displacement["causing_offspring_id"], child.id)
        self.assertEqual(displacement["causing_offspring_outcome"],
                         "died_before_first_extraction")
        summary = sim.substrate.displacement_viability_summary()
        self.assertEqual(summary[
            "live_displacements_caused_by_offspring_dying_before_first_extraction"],
            1)
        self.assertEqual(summary[
            "doomed_offspring_fraction_of_live_displacements"],
                         1.0)
        self.assertEqual(summary[
            "unresolved_causing_offspring_live_displacements"], 0)
        self.assertGreater(sim.substrate.corpse_allocated_bytes(), 0)

        for _ in range(CORPSE_POOL_TTL + 1):
            sim.step()
        self.assertEqual(sim.substrate.corpse_allocated_bytes(), 0)
        self.assertEqual(
            sim.substrate.shared_memory_pool,
            SHARED_MEMORY_POOL - parent.get_working_memory_size())

if __name__ == "__main__":
    unittest.main()
