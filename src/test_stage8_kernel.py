"""Registered Stage 8 kernel test matrix.

Named assertions of the superseding preregistration
``docs/stage-8-alpha-evolution-preregistration.md`` (sections 3, 6 G3,
7(1)) covering the dedicated-locus kernel: identity path, boundary
clamps, frozen-locus immutability, step support, supply accounting on
failed admissions and rollbacks, stream determinism, stream disjointness
from the hazard stream, and decision-record reconciliation.  The frozen
mechanics themselves are covered by the carried 7B1/7B2 matrices, which
are untouched; re-parameterising the fault matrix onto the subclass is
registered future work of the implementation window (section 7(1)) and
lands with the gate tooling.

All ledger arithmetic observed here is exact ``fractions.Fraction``;
kernel draws are integer-lattice operations on the dedicated stream.
"""

from __future__ import annotations

import json
import random
from fractions import Fraction

import unittest

from stage7_slice1 import PacketLedger
from stage7b1_mechanics import FaultInjector, InjectedFault
from stage7b2_population import Stage7B2Population
from stage8_population import (
    ALPHA_REF,
    DIRECTION_FLOOR_ALPHA,
    FROZEN_D,
    FROZEN_T,
    LATTICE_MAX,
    REGISTERED_MUTATION_PROB,
    REGISTERED_STEP_SUPPORT,
    Stage8Population,
    confirmatory_seed,
    mutation_seed,
    registered_stage8_population,
    registered_configuration,
    shakedown_seed,
    shakedown_seeds,
    stage8_founder_genomes,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def prepare_bout(population: Stage8Population, member) -> PacketLedger:
    """Drive one member to a complete gestation bout via the primitives.

    Mirrors the carried 7B1 fixture: the captured packet stays held; the
    prepaid work is sunk exactly as in the integrated cycle.
    """
    organism = member.organism
    source = population.packet_buffer.read()
    assert source is not None, "fixture buffer must contain an arrival"
    packet = PacketLedger(
        packet_id=source.packet_id,
        initial_budget=Fraction(source.e_initial),
        max_reducible=source.max_reducible,
    )
    population.packets.append(packet)
    population._register_hold(organism.organism_id, packet)
    compressed = organism.forage_rle(packet, source.data)
    population.compressed_buffers[packet.packet_id] = compressed
    assert organism.allocate_offspring()
    assert organism.copy_block(11)
    return packet


def ready_population(**overrides):
    """Stage 8 population whose org-0 holds a complete bout."""
    options: dict = dict(
        founder_genomes=[(102, FROZEN_T, FROZEN_D),
                         (204, FROZEN_T, FROZEN_D)],
        capacity=4,
        founder_s=Fraction(500),
        memory_pool=16384,
        buffer_depth=16,
        hazard_seed=20284617,
    )
    options.update(overrides)
    population = Stage8Population(**options)
    population.packet_buffer.advance_tick()
    member = population.members["org-0"]
    prepare_bout(population, member)
    return population, member


class ScriptedStream(random.Random):
    """Deterministic stand-in for the kernel stream.

    Subclasses ``random.Random`` so it is assignable wherever the kernel
    expects the stream object.  ``random_values`` feed the Bernoulli
    comparisons (mutate iff ``value < p_mu``); ``step_indices`` feed
    ``randrange``; when a script runs out the stream never mutates.
    """

    def __init__(self, random_values, step_indices):
        super().__init__(0)
        self.random_values = list(random_values)
        self.step_indices = list(step_indices)
        self.random_calls = 0
        self.randrange_calls = 0

    def random(self) -> float:  # type: ignore[override]
        self.random_calls += 1
        if self.random_values:
            return self.random_values.pop(0)
        return 1.0  # never mutate when the script runs out

    def randrange(self, n: int) -> int:  # type: ignore[override]
        self.randrange_calls += 1
        if self.step_indices:
            return self.step_indices.pop(0) % n
        return 0


def events_by_name(population, name):
    return [e for e in population.event_log if e.get("event") == name]


def event_digest(population) -> str:
    return json.dumps([repr(e) for e in population.event_log],
                      sort_keys=True)


# ---------------------------------------------------------------------------
# Registered assertions
# ---------------------------------------------------------------------------


class KernelIdentityAndSupportTests(unittest.TestCase):

    def test_no_mutation_path_is_exact_identity(self):
        """Scripted no-mutation: child genome equals the parent's exactly."""
        population, member = ready_population()
        population.mutation_rng = ScriptedStream([0.9], [])
        hazard_state = population.hazard_rng.getstate()
        child_id = population.divide_publish(member)
        self.assertIsNotNone(child_id)
        child = population.all_organisms[child_id]
        parent = member.organism
        self.assertEqual(
            (child.a, child.t, child.d), (parent.a, parent.t, parent.d))
        decision = events_by_name(population, "mutation_decision")[-1]
        self.assertFalse(decision["mutated"])
        self.assertIsNone(decision["delta"])
        self.assertEqual(decision["draws_consumed"], 1)
        self.assertEqual(population.mutation_draws, 1)
        # The hazard stream is never touched by the kernel.
        self.assertEqual(population.hazard_rng.getstate(), hazard_state)

    def test_boundary_clamp_low_and_high(self):
        """Clamping at both lattice boundaries (registered section 3)."""
        for parent_a, script, expected in (
            (0, ([0.0], [0]), 0),      # delta -4 at A=0 clamps to 0
            (255, ([0.0], [7]), 255),  # delta +4 at A=255 clamps to 255
            (1, ([0.0], [0]), 0),      # exact interior step to boundary
            (254, ([0.0], [7]), 255),
        ):
            population, member = ready_population()
            member.organism.a = parent_a  # test scaffolding, not evolution
            population.mutation_rng = ScriptedStream(*script)
            child_id = population.divide_publish(member)
            self.assertIsNotNone(child_id)
            child = population.all_organisms[child_id]
            self.assertEqual(child.a, expected)
            self.assertEqual((child.t, child.d), (FROZEN_T, FROZEN_D))

    def test_td_never_mutate_and_support_respected(self):
        """Across many scripted mutations T/D stay frozen; deltas in support."""
        population, member = ready_population(capacity=12, buffer_depth=64)
        # Nine publications total: the fixture's pre-armed bout plus eight
        # freshly prepared ones; each consumes exactly one scripted pair.
        population.mutation_rng = ScriptedStream(
            [0.0] * 9, list(range(9)))
        published = 0
        for i in range(9):
            if i > 0:
                population.packet_buffer.advance_tick()
                prepare_bout(population, member)
            child_id = population.divide_publish(member)
            self.assertIsNotNone(child_id)
            published += 1
            child = population.all_organisms[child_id]
            self.assertEqual(child.t, FROZEN_T)
            self.assertEqual(child.d, FROZEN_D)
            self.assertTrue(0 <= child.a <= LATTICE_MAX)
        decisions = events_by_name(population, "mutation_decision")
        self.assertEqual(len(decisions), published)
        for decision in decisions:
            self.assertTrue(decision["mutated"])
            self.assertIn(decision["delta"], REGISTERED_STEP_SUPPORT)
            self.assertNotEqual(decision["delta"], 0)
            expected = min(LATTICE_MAX, max(
                0, decision["parent_a"] + decision["delta"]))
            self.assertEqual(decision["child_a"], expected)

    def test_stream_derivation_and_probability_wiring(self):
        """Documented derivation; Bernoulli comparison at p_mu = 1/2."""
        self.assertEqual(mutation_seed(20284617), 20284617 * 1000003 + 7)
        self.assertEqual(REGISTERED_MUTATION_PROB, Fraction(1, 2))
        stream = random.Random(mutation_seed(7))
        mutated = sum(stream.random() < 0.5 for _ in range(4000))
        self.assertTrue(1800 <= mutated <= 2200, mutated)

    def test_founder_frozen_locus_validation(self):
        """Founders carrying any other T/D are rejected at construction."""
        with self.assertRaises(ValueError):
            Stage8Population(
                founder_genomes=[(102, 64, FROZEN_D)],
                capacity=4, founder_s=Fraction(100), memory_pool=16384,
                buffer_depth=16, hazard_seed=1)


class SupplyAccountingTests(unittest.TestCase):

    def test_no_vacancy_consumes_no_kernel_draws(self):
        """Failed admissions discard before M: no draw, no decision record."""
        from stage7_slice1 import SliceOrganism
        from stage7_slice2 import PopulationMember
        population, member = ready_population(capacity=3)
        # Register one additional member so the census is at capacity.  The
        # filler carries S = 0 so the opening reserve ledger stays closed.
        filler = SliceOrganism(
            "org-filler", population.memory, Fraction(0), Fraction(0),
            a=102, t=FROZEN_T, d=FROZEN_D)
        population.members["org-filler"] = PopulationMember(
            organism=filler, born_tick=-1)
        population.all_organisms["org-filler"] = filler
        population.ancestry["org-filler"] = "F9"
        # The filler is an additional founder-equivalent input: the census
        # identity (founders + admitted - removals == live) must include it.
        population.founders += 1
        draws_before = population.mutation_draws
        result = population.divide_publish(member)
        self.assertIsNone(result)
        self.assertEqual(population.mutation_draws, draws_before)
        self.assertEqual(events_by_name(population, "mutation_decision"), [])
        self.assertEqual(
            events_by_name(population, "divide_failed")[-1]["reason"],
            "NO_VACANCY")

    def test_rollback_retains_consumed_kernel_draws(self):
        """Fault at post_M: state rolls back; kernel draws stay consumed."""
        population, member = ready_population()
        population.mutation_rng = ScriptedStream([0.0], [2])  # mutate +3
        injector = FaultInjector()
        injector.arm("post_M")
        draws_before = population.mutation_draws
        with self.assertRaises(InjectedFault):
            population.divide_publish(member, injector)
        self.assertEqual(population.mutation_draws, draws_before + 2)
        self.assertEqual(population.vacancy_reserved, 0)
        self.assertEqual(population.admitted_births, 0)
        self.assertNotIn(member.organism.organism_id,
                         population.memory.gestation)
        failure = events_by_name(population, "divide_failed")[-1]
        self.assertEqual(failure["stage"], "M")
        # The decision record survives: it is telemetry, not ledger state.
        self.assertEqual(len(events_by_name(population, "mutation_decision")),
                         1)


class StreamAndWindowTests(unittest.TestCase):

    WINDOW = 60

    def _run_window(self, population, ticks):
        for _ in range(ticks):
            population.step()

    def test_identical_seeds_produce_identical_event_streams(self):
        one = registered_stage8_population(confirmatory_seed(0),
                                           window_ticks=self.WINDOW)
        two = registered_stage8_population(confirmatory_seed(0),
                                           window_ticks=self.WINDOW)
        self._run_window(one, self.WINDOW)
        self._run_window(two, self.WINDOW)
        self.assertEqual(event_digest(one), event_digest(two))
        self.assertGreater(one.mutation_decisions, 0)

    def test_kernel_never_touches_hazard_stream(self):
        """The hazard stream object is disjoint and untouched by Stage M."""
        seed = shakedown_seed(0)
        population = registered_stage8_population(
            seed, window_ticks=self.WINDOW)
        fresh = random.Random(seed)
        self.assertEqual(population.hazard_rng.getstate(),
                         fresh.getstate())
        population, member = ready_population(hazard_seed=seed)
        hazard_state = population.hazard_rng.getstate()
        population.mutation_rng = ScriptedStream([0.0], [5])
        child_id = population.divide_publish(member)
        self.assertIsNotNone(child_id)
        self.assertEqual(population.hazard_rng.getstate(), hazard_state)

    def test_decision_records_reconcile_with_admitted_births(self):
        """Every admitted birth carries exactly one Stage-M decision."""
        population = registered_stage8_population(
            shakedown_seed(1), window_ticks=self.WINDOW)
        self._run_window(population, self.WINDOW)
        decisions = events_by_name(population, "mutation_decision")
        births = events_by_name(population, "birth_admitted")
        self.assertEqual(len(decisions), len(births))
        self.assertEqual(len(decisions), population.mutation_decisions)
        self.assertEqual(
            {d["child_id"] for d in decisions},
            {b["child_id"] for b in births})
        for decision in decisions:
            self.assertIn("parent_a", decision)
            self.assertIn("mutated", decision)
            self.assertIn("delta", decision)
            self.assertIn("child_a", decision)
            self.assertIn("stream_position", decision)
            self.assertTrue(0 <= decision["child_a"] <= LATTICE_MAX)
            self.assertEqual(decision["child_a"] - decision["parent_a"],
                             decision["delta"] or 0)
        # Frozen loci genome-wide over the whole window.
        for organism in population.all_organisms.values():
            self.assertEqual((organism.t, organism.d),
                             (FROZEN_T, FROZEN_D))


class RegisteredConstantsTests(unittest.TestCase):

    def test_configuration_echo_matches_registration(self):
        config = registered_configuration()
        # Fraction normalises 153/255 to 3/5; the registration states both.
        self.assertEqual(config["alpha_ref"], "3/5")
        self.assertEqual(ALPHA_REF, Fraction(153, 255))
        self.assertEqual(config["direction_floor_alpha"], "8/255")
        self.assertEqual(DIRECTION_FLOOR_ALPHA, Fraction(8, 255))
        self.assertEqual(config["mutation_probability"], "1/2")
        self.assertEqual(config["step_support"],
                         [-4, -3, -2, -1, 1, 2, 3, 4])
        self.assertEqual(config["frozen_loci"], {"T": 128, "D": 255})
        self.assertEqual(config["window_ticks_W"], 2400)
        self.assertEqual(config["replicates_k"], 24)

    def test_seed_tables_disjoint_from_all_prior_tables(self):
        """Confirmatory/shakedown tables avoid every prior population table."""
        prior_maxes = [20260822 + 31, 20261822 + 31, 20270000 + 23]
        confirmatory = [confirmatory_seed(i) for i in range(24)]
        shakedown = shakedown_seeds()
        self.assertEqual(min(confirmatory), 20284617)
        self.assertEqual(min(shakedown), 20293311)
        for prior_max in prior_maxes:
            self.assertGreater(min(confirmatory), prior_max)
            self.assertGreater(min(shakedown), prior_max)
        self.assertLess(max(confirmatory), min(shakedown))
        self.assertEqual(len(set(confirmatory) | set(shakedown)), 36)

    def test_founder_blocks_carried_verbatim(self):
        self.assertEqual(stage8_founder_genomes(),
                         [(102, 128, 255)] * 3 + [(204, 128, 255)] * 3)


if __name__ == "__main__":
    unittest.main()
