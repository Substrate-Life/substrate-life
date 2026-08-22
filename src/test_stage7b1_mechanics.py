"""Registered Stage 7B1 test matrix (preregistration §§2-5 plus §6.2).

Every test method below is a named registered assertion of the superseding
preregistration ``docs/stage-7b1-preregistration.md``.  The matrix is frozen
together with the mechanics, runner, and output schema per §9.2; the retained
execution of this matrix is the authorised deterministic verification class
of §9.3 and happens only after the freeze commit.

All arithmetic observed here is exact ``fractions.Fraction``.
"""

from __future__ import annotations

from fractions import Fraction
import unittest

from stage7_slice1 import MIN_WORKING_MEMORY, PacketLedger
from stage7b1_mechanics import (
    INJECTION_BOUNDARIES,
    BufferOverflowError,
    FaultInjector,
    GuardedPacketBuffer,
    InjectedFault,
    REGISTERED_PACKET_RATE,
    Stage7B1Population,
    registered_buffer_depth,
    registered_deterministic_population,
)

_STAGE_OF_BOUNDARY = {
    "post_V": "V",
    "mid_M": "M",
    "post_M": "M",
    "mid_R": "R",
    "post_R": "R",
    "mid_P": "P",
    "pre_C": "P",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def prepare_bout(population: Stage7B1Population, member) -> PacketLedger:
    """Drive one member to a complete gestation bout via the primitives.

    The packet captured on the way stays held by the member; prepaid work
    (C_S/C_R) is sunk exactly as in the integrated cycle.
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
    """Population whose org-0 holds a complete bout (gestation live)."""
    options: dict = dict(
        capacity=4,
        founder_count=2,
        founder_s=Fraction(500),
        memory_pool=16384,
        buffer_depth=16,
    )
    options.update(overrides)
    population = Stage7B1Population(**options)
    population.packet_buffer.advance_tick()
    member = population.members["org-0"]
    attempt_work = member.organism.c_s + member.organism.c_r
    prepare_bout(population, member)
    return population, member, attempt_work


def two_holders_population():
    """Two members each holding one freshly captured (drawn-on) packet."""
    population = Stage7B1Population(
        capacity=6, founder_count=2, founder_s=Fraction(500),
        memory_pool=16384, buffer_depth=16)
    population.packet_buffer.advance_tick()
    packets = []
    for organism_id in ("org-0", "org-1"):
        member = population.members[organism_id]
        packets.append(prepare_bout(population, member))
    return population, packets


def event_indices(population: Stage7B1Population, name: str) -> list[int]:
    return [i for i, e in enumerate(population.event_log)
            if e.get("event") == name]


def deep_state(population: Stage7B1Population):
    """Every mechanic-relevant mutable state component except shadow counters."""
    return (
        tuple(sorted((oid, m.state, m.born_tick)
                     for oid, m in population.members.items())),
        tuple(sorted((oid, o.s, o.r, o.c_s, o.c_r, o.gross_income,
                      o.reversed_income, o.committed, o.destroyed,
                      o.a, o.t, o.d)
                     for oid, o in population.all_organisms.items())),
        population.memory.free_pool,
        tuple(sorted(population.memory.somatic_active.items())),
        tuple(sorted(population.memory.gestation.items())),
        tuple(sorted(population.memory.child_reserved.items())),
        tuple(sorted(population.memory.corpse_reserved.items())),
        tuple(p.packet_id for p in population.packet_buffer.buffer),
        population.rng_draws,
        population.vacancy_reserved,
        population.admitted_births,
        population.hazard_removals,
        len(population.event_log),
    )


# ---------------------------------------------------------------------------
# Blocker A -- atomic child-publication transaction (preregistration §2)
# ---------------------------------------------------------------------------


class Stage7B1RollbackMatrixTests(unittest.TestCase):
    """The seven fault-injection boundary tests, each asserting I1-I8."""

    def _run_faulted_attempt(self, boundary: str):
        population, member, attempt_work = ready_population()
        organism = member.organism
        context = {
            "census_ids": sorted(population.members),
            "admitted": population.admitted_births,
            "removals": population.hazard_removals,
            "r_before": organism.r,
            "attempt_work": attempt_work,
            "txn_work": organism.c_s + organism.c_r,
            "rng_at_injection": population.rng_draws,
            "organism_ids": sorted(population.all_organisms),
        }
        injector = FaultInjector(boundary)
        with self.assertRaises(InjectedFault) as caught:
            population.divide_publish(member, injector)
        self.assertEqual(caught.exception.boundary, boundary)
        self.assertEqual(injector.fired_at, boundary)
        return population, member, context, boundary

    def _assert_I1_to_I8(self, population, member, context, boundary):
        organism = member.organism
        # I1: census unchanged; hazard/admission counters unchanged.
        self.assertEqual(sorted(population.members), context["census_ids"])
        self.assertEqual(population.admitted_births, context["admitted"])
        self.assertEqual(population.hazard_removals, context["removals"])
        # I2: memory ledger closes exactly with an empty child_reserved bucket.
        totals = population.memory.totals()
        self.assertEqual(
            sum(totals.values()), population.memory.initial_pool)
        self.assertEqual(totals["child_reserved"], 0)
        self.assertEqual(population.memory.child_reserved, {})
        # I3: no census-, scheduler-, or ledger-visible partial child.
        self.assertEqual(sorted(population.all_organisms),
                         context["organism_ids"])
        for bucket in (population.memory.somatic_active,
                       population.memory.gestation,
                       population.memory.corpse_reserved):
            for owner in bucket:
                self.assertIn(owner, context["organism_ids"])
        # I4: parent R equals its pre-P value exactly (refund not recompute).
        self.assertIsInstance(organism.r, Fraction)
        self.assertEqual(organism.r, context["r_before"])
        # I5: prepaid work retained; strictly greater than attempt start.
        work_now = organism.c_s + organism.c_r
        self.assertGreaterEqual(work_now, context["txn_work"])
        self.assertGreater(work_now, context["attempt_work"])
        # I6: RNG counter equals its value at the injection point.
        self.assertEqual(population.rng_draws, context["rng_at_injection"])
        # I7: exactly one failure-stage record with exact fields, no P.
        indices = event_indices(population, "divide_failed")
        self.assertEqual(len(indices), 1)
        failure = population.event_log[indices[0]]
        self.assertEqual(
            set(failure),
            {"event", "tick", "phase", "organism_id", "stage", "reason"},
        )
        self.assertNotIn("provision", failure)
        self.assertEqual(failure["reason"], "FAULT_INJECTED")
        self.assertEqual(failure["stage"], _STAGE_OF_BOUNDARY[boundary])
        self.assertEqual(failure["organism_id"], organism.organism_id)
        self.assertNotIn("provision_committed",
                         [e.get("event") for e in population.event_log])
        self.assertNotIn("birth_admitted",
                         [e.get("event") for e in population.event_log])
        # I8: reserve, packet, memory, and census closures close immediately.
        snapshot = population.assert_all_ledgers("rollback_matrix_check")
        self.assertTrue(snapshot["reserve_closed"])
        self.assertTrue(snapshot["census_closed"])
        self.assertTrue(snapshot["packets_closed"])
        self.assertTrue(snapshot["memory_closed"])
        self.assertEqual(population.vacancy_reserved, 0)

    def test_rollback_after_vacancy(self):
        population, member, context, boundary = self._run_faulted_attempt(
            "post_V")
        self._assert_I1_to_I8(population, member, context, boundary)

    def test_rollback_in_mutation(self):
        population, member, context, boundary = self._run_faulted_attempt(
            "mid_M")
        self._assert_I1_to_I8(population, member, context, boundary)

    def test_rollback_after_mutation(self):
        population, member, context, boundary = self._run_faulted_attempt(
            "post_M")
        self._assert_I1_to_I8(population, member, context, boundary)

    def test_rollback_in_child_memory(self):
        population, member, context, boundary = self._run_faulted_attempt(
            "mid_R")
        self._assert_I1_to_I8(population, member, context, boundary)

    def test_rollback_after_child_memory(self):
        population, member, context, boundary = self._run_faulted_attempt(
            "post_R")
        self._assert_I1_to_I8(population, member, context, boundary)
        # The reservation existed between post_R and rollback; it is gone now.
        self.assertEqual(population.memory.child_reserved, {})

    def test_rollback_in_provisioning(self):
        population, member, context, boundary = self._run_faulted_attempt(
            "mid_P")
        self._assert_I1_to_I8(population, member, context, boundary)

    def test_rollback_before_commit(self):
        population, member, context, boundary = self._run_faulted_attempt(
            "pre_C")
        self._assert_I1_to_I8(population, member, context, boundary)


class Stage7B1CommitSemanticsTests(unittest.TestCase):
    """test_commit_is_atomic, stale-bout, RNG survival, regression lock."""

    def test_commit_is_atomic(self):
        population, member, _ = ready_population()
        population.observations = []
        child_id = population.divide_publish(member)
        self.assertIsNotNone(child_id)
        observations = population.observations
        self.assertEqual([o["tag"] for o in observations],
                         ["post_V", "mid_M", "post_M", "post_R", "post_C"])
        # No observable interleaving state exists between P and C: the child
        # is absent from every observation until the single post-C snapshot,
        # where census visibility, somatic ownership, and vacancy conversion
        # appear together, and the ledger closes at every observation point.
        for observation in observations:
            self.assertEqual(sum(observation["memory_totals"].values()),
                             population.memory.initial_pool)
            if observation["tag"] != "post_C":
                self.assertFalse(observation["child_visible"])
                self.assertFalse(observation["child_in_somatic"])
                self.assertFalse(observation["child_visible"]
                                 or observation["child_reserved_bucket"] is False
                                 and observation["child_in_somatic"])
        final = observations[-1]
        self.assertTrue(final["child_visible"])
        self.assertTrue(final["child_in_somatic"])
        self.assertFalse(final["child_reserved_bucket"])
        self.assertEqual(final["vacancy_reserved"], 0)
        # Structural: the commit interior exposes no injection boundary.
        self.assertNotIn("in_C", INJECTION_BOUNDARIES)
        self.assertNotIn("post_C", INJECTION_BOUNDARIES)
        self.assertTrue(INJECTION_BOUNDARIES.isdisjoint({"in_C", "mid_C",
                                                         "post_C"}))
        # Any exception before commit rolls back identically (architecture
        # §7 step 7): corrupt traits raise at the M-stage bound check after V
        # reserved a vacancy; nothing may leak except the registered bout
        # discard of §2.2 (gestation released, free pool restored by its
        # exact byte count).
        population2, member2, _ = ready_population()
        member2.organism.t = 999  # bypass construction validation
        gestation_bytes = population2.memory.gestation["org-0"]
        state_before = deep_state(population2)
        with self.assertRaises(ValueError):
            population2.divide_publish(member2)
        expected = list(state_before)
        expected[2] = state_before[2] + gestation_bytes  # bout back to pool
        expected[4] = ()                        # gestation bucket emptied
        # The rollback is silent for unexpected exceptions: zero registered
        # failure records and no other movement anywhere.
        expected[12] = state_before[12]
        self.assertEqual(tuple(expected), deep_state(population2))
        self.assertEqual(population2.vacancy_reserved, 0)
        self.assertEqual(event_indices(population2, "divide_failed"), [])
        population2.assert_all_ledgers("unexpected_exception_rollback")

    def test_no_stale_bout_retry(self):
        population, member, _ = ready_population()
        injector = FaultInjector("mid_M")
        with self.assertRaises(InjectedFault):
            population.divide_publish(member, injector)
        # The released/discarded gestation cannot be consumed by a retry.
        self.assertNotIn(member.organism.organism_id,
                         population.memory.gestation)
        with self.assertRaises(RuntimeError):
            population.divide_publish(member)

    def test_rng_consumption_survives_failure(self):
        population, member, _ = ready_population()
        population.consume_registered_draw(3)
        counter_at_arm = population.rng_draws
        injector = FaultInjector("mid_M")
        with self.assertRaises(InjectedFault):
            population.divide_publish(member, injector)
        # No replay and no extra draw across the failed transaction.
        self.assertEqual(population.rng_draws, counter_at_arm)
        # A subsequent unrelated draw observes the advanced counter.
        population.consume_registered_draw(1)
        self.assertEqual(population.rng_draws, counter_at_arm + 1)

    def test_child_memory_unavailable_is_atomic(self):
        # Population-level regression lock for the atomic CHILD_MEMORY_
        # UNAVAILABLE behaviour (commit 7ab6dba, formerly f90da66): a child
        # obligation larger than the released gestation block plus free pool
        # fails the R-stage reservation atomically.
        population = Stage7B1Population(
            capacity=4, founder_count=2, founder_s=Fraction(500),
            memory_pool=16384, buffer_depth=16)
        population.packet_buffer.advance_tick()
        member = population.members["org-0"]
        organism = member.organism
        source = population.packet_buffer.read()
        packet = PacketLedger(
            packet_id=source.packet_id,
            initial_budget=Fraction(source.e_initial),
            max_reducible=source.max_reducible)
        population.packets.append(packet)
        compressed = organism.forage_rle(packet, source.data)
        population.compressed_buffers[packet.packet_id] = compressed
        # Undersized bout: releasing it cannot fund the full child basis.
        assert organism.allocate_offspring(size=32)
        assert organism.copy_block(11)
        # Apply demographic memory pressure through the ledger itself: grow
        # the parent's somatic footprint until even releasing the 32-byte
        # gestation leaves less than the 64-byte child basis in free pool.
        pressure = (population.memory.free_pool + 32
                    - MIN_WORKING_MEMORY + 1)
        self.assertGreater(pressure, 0)
        population.memory.resize_somatic(
            organism.organism_id,
            population.memory.somatic_active[organism.organism_id]
            + pressure,
            "fixture_demographic_pressure")
        r_before = organism.r
        census_before = sorted(population.members)
        result = population.divide_publish(member)
        self.assertIsNone(result)
        failures = [population.event_log[i]
                    for i in event_indices(population, "divide_failed")]
        self.assertEqual(len(failures), 1)
        failure = failures[0]
        self.assertEqual(
            set(failure),
            {"event", "tick", "phase", "organism_id", "stage", "reason"})
        self.assertEqual(failure["stage"], "R")
        self.assertEqual(failure["reason"], "CHILD_MEMORY_UNAVAILABLE")
        self.assertNotIn("provision", failure)
        # Atomic: no vacancy leak, no partial child, exact ledgers, retained
        # prepaid work, untouched provisioning debit.
        self.assertEqual(population.vacancy_reserved, 0)
        self.assertEqual(sorted(population.members), census_before)
        self.assertEqual(population.memory.child_reserved, {})
        self.assertNotIn(organism.organism_id, population.memory.gestation)
        self.assertEqual(organism.r, r_before)
        self.assertGreater(organism.c_s + organism.c_r, 0)
        population.assert_all_ledgers("child_memory_unavailable_lock")


# ---------------------------------------------------------------------------
# Blocker B -- packet retirement equations (preregistration §3)
# ---------------------------------------------------------------------------


class Stage7B1RetirementTests(unittest.TestCase):
    def _partial_return(self, population, holder_id, packet, extent=8):
        drawn_before = packet.drawn_s + packet.drawn_r
        ok = population.attempt_return(holder_id, packet, extent)
        assert ok, "fixture return must succeed"
        assert packet.drawn_s + packet.drawn_r < drawn_before
        return drawn_before

    def test_retire_on_holder_death(self):
        population, packets = two_holders_population()
        victim, survivor = "org-1", "org-0"
        self._partial_return(population, victim, packets[1])
        budget_at_death = packets[1].budget_remaining
        drawn_s_at_death = packets[1].drawn_s
        drawn_r_at_death = packets[1].drawn_r
        population._hazard_remove(victim)
        retire_events = [population.event_log[i]
                         for i in event_indices(population, "packet_retired")]
        self.assertEqual(len(retire_events), 1)
        event = retire_events[0]
        self.assertEqual(
            set(event),
            {"tick", "phase", "event", "packet_id", "holder_id", "reason",
             "destroyed_budget", "retired_drawn_s", "retired_drawn_r",
             "initial_budget"})
        self.assertEqual(event["reason"], "HOLDER_DEATH")
        self.assertEqual(event["holder_id"], victim)
        self.assertEqual(event["destroyed_budget"], budget_at_death)
        self.assertEqual(event["retired_drawn_s"], drawn_s_at_death)
        self.assertEqual(event["retired_drawn_r"], drawn_r_at_death)
        # Live identity held at retirement: B + D_S + D_R == B_init.
        self.assertEqual(
            event["destroyed_budget"] + event["retired_drawn_s"]
            + event["retired_drawn_r"],
            event["initial_budget"])
        self.assertIn(packets[1].packet_id, population.retired_packet_ids)
        self.assertNotIn(packets[1].packet_id, population.active_packets)
        self.assertNotIn(victim, population.held_packets)
        # Registered death ordering: retirement precedes disposal and the
        # hazard record.
        order = ([i for i in event_indices(population, "packet_retired")]
                 + [i for i in event_indices(population, "death_disposal")]
                 + [i for i in event_indices(population, "hazard_death")])
        self.assertEqual(order, sorted(order))

    def test_destroyed_budget_exact(self):
        population, packets = two_holders_population()
        population.explicitly_destroy_packet("org-0", packets[0].packet_id)
        population._hazard_remove("org-1")
        total_retired = sum((entry["destroyed_budget"]
                             for entry in population.retirements), Fraction(0))
        # Equation 1: physical destruction is an energy sink exactly once.
        self.assertEqual(population.destroyed_packet_budget, total_retired)
        reserve = population.reserve_closure()
        self.assertTrue(reserve["closed"])
        expected_destroyed = (
            population.terminal_disposed
            + population.destroyed_packet_budget
            + sum((o.destroyed for o in population.all_organisms.values()),
                  Fraction(0)))
        self.assertEqual(reserve["destroyed"], expected_destroyed)
        reasons = {entry["reason"] for entry in population.retirements}
        self.assertEqual(reasons, {"EXPLICIT_DESTROY", "HOLDER_DEATH"})

    def test_double_retirement_raises(self):
        population, packets = two_holders_population()
        packet_id = packets[0].packet_id
        population.explicitly_destroy_packet("org-0", packet_id)
        with self.assertRaises(RuntimeError):
            population.explicitly_destroy_packet("org-0", packet_id)
        with self.assertRaises(AssertionError):
            population._retire_packet(packets[0], "org-0", "HOLDER_DEATH")

    def test_retired_provenance_not_a_sink(self):
        population, packets = two_holders_population()
        packet = packets[0]
        self._partial_return(population, "org-0", packet)
        destroyed_before = population.reserve_closure()["destroyed"]
        live_before = population.reserve_closure()["live_reserves"]
        drawn_s, drawn_r = packet.drawn_s, packet.drawn_r
        population.explicitly_destroy_packet("org-0", packet.packet_id)
        # Only destroyed_budget entered the sink; retired drawn provenance is
        # bookkeeping and never re-enters any ledger.
        destroyed_after = population.reserve_closure()["destroyed"]
        self.assertEqual(
            destroyed_after - destroyed_before, packet.budget_remaining + 0)
        reserve = population.reserve_closure()
        self.assertTrue(reserve["closed"])
        self.assertEqual(reserve["live_reserves"], live_before)
        retirement = population.retirements[-1]
        self.assertEqual(retirement["retired_drawn_s"], drawn_s)
        self.assertEqual(retirement["retired_drawn_r"], drawn_r)
        # Any later draw, return, or re-capture referencing the id raises.
        organism = population.all_organisms["org-0"]
        s_before, r_before = organism.s, organism.r
        with self.assertRaises(RuntimeError):
            population.attempt_return("org-0", packet, extent=4)
        self.assertEqual((organism.s, organism.r), (s_before, r_before))


# ---------------------------------------------------------------------------
# Blocker C -- proven no-eviction configuration (preregistration §4)
# ---------------------------------------------------------------------------


class Stage7B1NoEvictionTests(unittest.TestCase):
    def test_overflow_raises_not_drops(self):
        buffer = GuardedPacketBuffer(
            seed=42, phase_mode="monotonic_rich",
            packet_e_rich=Fraction(300), packet_e_lean=Fraction(300),
            packet_rate=REGISTERED_PACKET_RATE, buffer_depth=3)
        with self.assertRaises(BufferOverflowError) as caught:
            buffer.advance_tick()
        self.assertIn("BUFFER_OVERFLOW", str(caught.exception))
        # Every generated packet is retained: nothing was silently discarded
        # (three arrivals filled the depth; the raise preempted the rest).
        self.assertEqual(buffer.cumulative_generated, len(buffer.buffer))
        self.assertEqual(len(buffer.buffer), 3)
        self.assertEqual([p.packet_id for p in buffer.buffer], [1, 2, 3])

    def test_bound_holds_for_registered_fixture(self):
        window_ticks = 4
        population = registered_deterministic_population(
            window_ticks=window_ticks)
        depth = registered_buffer_depth(window_ticks, 0)
        self.assertEqual(depth, REGISTERED_PACKET_RATE * window_ticks)
        for _ in range(window_ticks):
            snapshot = population.step()
            # Capturer guarantee: at least one live unstalled member attempts
            # capture on every tick.
            self.assertGreaterEqual(snapshot["capture_attempts"], 1)
            generated = population.packet_buffer.cumulative_generated
            consumed = population.packet_buffer.cumulative_consumed
            self.assertLessEqual(generated - consumed, depth)
        # Unread buffered packets at window end are listed, not retired.
        self.assertEqual(population.retirements, [])
        self.assertGreaterEqual(len(population.packet_buffer.buffer), 0)
        for packet in population.packet_buffer.buffer:
            self.assertEqual(Fraction(packet.e_budget),
                             Fraction(packet.e_initial))
        population.assert_all_ledgers("registered_window_end")

    def test_all_stalled_triggers_guard(self):
        # Deliberately removing the capturer guarantee must trip layer 1 (or
        # layer 2) loudly -- never drop a packet silently.
        population = Stage7B1Population(
            capacity=3, founder_count=3, founder_s=Fraction(0),
            memory_pool=4096, packet_rate=REGISTERED_PACKET_RATE,
            buffer_depth=3)
        with self.assertRaises(BufferOverflowError):
            population.step()


# ---------------------------------------------------------------------------
# Blocker D -- hazard death with live gestation (preregistration §5)
# ---------------------------------------------------------------------------


class Stage7B1HazardDeathTests(unittest.TestCase):
    def test_death_between_alloc_and_copy(self):
        population, member, _ = ready_population()
        organism = member.organism
        work_before = organism.c_s + organism.c_r
        s_before, r_before = organism.s, organism.r
        free_before = population.memory.free_pool
        population._hazard_remove(organism.organism_id)
        # Gestation released to free_pool with the registered reason.
        releases = [population.event_log[i] for i in
                    event_indices(population, "gestation_released")]
        self.assertEqual(len(releases), 1)
        release = releases[0]
        self.assertEqual(release["release_reason"], "HAZARD_DEATH")
        self.assertEqual(release["gestation_bytes"], 64)
        self.assertNotIn(organism.organism_id, population.memory.gestation)
        self.assertEqual(population.memory.free_pool, free_before + 64)
        # No gestation upkeep is charged at the death tick.
        self.assertEqual(organism.c_s + organism.c_r, work_before)
        # Terminal disposal carries both exact amounts; corpse reserved.
        disposals = [population.event_log[i] for i in
                     event_indices(population, "death_disposal")]
        self.assertEqual(len(disposals), 1)
        disposal = disposals[0]
        self.assertEqual(disposal["s_disposed"], s_before)
        self.assertEqual(disposal["r_disposed"], r_before)
        self.assertIn(organism.organism_id, population.memory.corpse_reserved)
        population.assert_all_ledgers("death_between_alloc_and_copy")

    def test_death_holding_packet(self):
        population, member, _ = ready_population()
        packet = population.active_packets[
            sorted(population.held_packets["org-0"])[0]]
        budget_at_death = packet.budget_remaining
        population._hazard_remove("org-0")
        retirements = [population.event_log[i] for i in
                       event_indices(population, "packet_retired")]
        self.assertEqual(len(retirements), 1)
        event = retirements[0]
        self.assertEqual(event["reason"], "HOLDER_DEATH")
        self.assertEqual(event["destroyed_budget"], budget_at_death)
        self.assertEqual(event["holder_id"], "org-0")
        self.assertIn(packet.packet_id, population.retired_packet_ids)
        population.assert_all_ledgers("death_holding_packet")

    def test_corpse_expiry_restores_memory_closure(self):
        population = Stage7B1Population(
            capacity=4, founder_count=2, founder_s=Fraction(500),
            memory_pool=16384, corpse_ttl=2, buffer_depth=16,
            hazard_schedule={0: {"org-0"}})
        first = population.step()
        self.assertEqual(first["hazard_deaths"], ["org-0"])
        self.assertIn("org-0", population.memory.corpse_reserved)
        corpse_bytes = population.memory.corpse_reserved["org-0"]
        self.assertEqual(population.corpse_expiry["org-0"], 2)
        second = population.step()  # tick 1: not yet due
        self.assertEqual(second["hazard_deaths"], [])
        self.assertIn("org-0", population.memory.corpse_reserved)
        third = population.step()  # tick 2: expiry due
        self.assertNotIn("org-0", population.memory.corpse_reserved)
        expired = [population.event_log[i] for i in
                   event_indices(population, "corpse_expired")]
        self.assertEqual(len(expired), 1)
        self.assertEqual(expired[0]["bytes_restored"], corpse_bytes)
        # The corpse's bytes rejoined free_pool at expiry; other legitimate
        # allocation/deallocation also occurs within the same tick (further
        # reproduction by survivors), so the closure check -- not a raw
        # free_pool delta -- is the registered assertion.
        population.assert_all_ledgers("corpse_expiry_closure")

    def test_death_disposal_exact(self):
        population, packets = two_holders_population()
        victim = population.all_organisms["org-1"]
        s_disposed_expected = victim.s
        r_disposed_expected = victim.r
        others_before = {
            oid: (o.s, o.r) for oid, o in population.all_organisms.items()
            if oid != "org-1" and oid in population.members}
        terminal_before = population.terminal_disposed
        population._hazard_remove("org-1")
        self.assertEqual(population.terminal_disposed - terminal_before,
                         s_disposed_expected + r_disposed_expected)
        self.assertEqual((victim.s, victim.r), (Fraction(0), Fraction(0)))
        for oid, (s_value, r_value) in others_before.items():
            self.assertEqual((population.all_organisms[oid].s,
                              population.all_organisms[oid].r),
                             (s_value, r_value))
        disposal = [population.event_log[i]
                    for i in event_indices(population, "death_disposal")][-1]
        self.assertEqual(disposal["s_disposed"], s_disposed_expected)
        self.assertEqual(disposal["r_disposed"], r_disposed_expected)
        population.assert_all_ledgers("death_disposal_exact")

    def test_dead_member_not_scheduled(self):
        population = Stage7B1Population(
            capacity=4, founder_count=2, founder_s=Fraction(500),
            memory_pool=16384, buffer_depth=16,
            hazard_schedule={0: {"org-0"}})
        first = population.step()
        self.assertEqual(first["hazard_deaths"], ["org-0"])
        self.assertNotIn("org-0", first["executed_ids"])
        self.assertNotIn("org-0", population.members)
        scheduler_events_dead = [
            e for e in population.event_log
            if e.get("organism_id") == "org-0"
            and e.get("phase") in ("scheduler", "admission",
                                   "packet_capture")]
        self.assertEqual(scheduler_events_dead, [])
        # Census identity holds: founders + admitted - hazard_removals ==
        # live_census (no fixed magic number; org-1 may itself reproduce
        # within the same tick).
        census = population.census_closure()
        self.assertTrue(census["closed"])
        self.assertEqual(first["live_census"], len(population.members))
        second = population.step()
        self.assertNotIn("org-0", second["executed_ids"])
        self.assertNotIn("org-0", population.members)
        self.assertGreaterEqual(len(population.members), first["live_census"])
        population.assert_all_ledgers("dead_member_not_scheduled")


# ---------------------------------------------------------------------------
# Blocker F -- side-effect-free shadow admission telemetry (§6.2)
# ---------------------------------------------------------------------------


class Stage7B1ShadowTelemetryTests(unittest.TestCase):
    def test_shadow_counters_side_effect_free(self):
        population = Stage7B1Population(
            capacity=4, founder_count=2, founder_s=Fraction(500),
            memory_pool=16384, buffer_depth=16)
        population.packet_buffer.advance_tick()
        # Pure read: repeated evaluation under varying vacancy pressure
        # changes no state whatsoever.
        before = deep_state(population)
        for _ in range(3):
            self.assertTrue(population.would_admit_now())
        self.assertEqual(deep_state(population), before)
        population.vacancy_reserved += 2
        under_pressure = deep_state(population)
        self.assertFalse(population.would_admit_now())
        self.assertEqual(deep_state(population), under_pressure)
        population.vacancy_reserved -= 2
        self.assertTrue(population.would_admit_now())
        self.assertEqual(deep_state(population), before)
        # Integrated decisions: fill the census through admitted births while
        # org-0 holds a prepared bout, then let its decision hit NO_VACANCY.
        # org-1 (a founder with ample S) repeatedly completes fresh bouts;
        # each successful DIVIDE records a would-admit shadow outcome.
        prepare_bout(population, population.members["org-0"])
        admitted = 0
        filler_id = "org-1"
        while len(population.members) < population.capacity:
            source = population.packet_buffer.read()
            self.assertIsNotNone(source)
            packet = PacketLedger(
                packet_id=source.packet_id,
                initial_budget=Fraction(source.e_initial),
                max_reducible=source.max_reducible)
            organism = population.all_organisms[filler_id]
            population.packets.append(packet)
            population._register_hold(filler_id, packet)
            population.compressed_buffers[packet.packet_id] = (
                organism.forage_rle(packet, source.data))
            assert organism.allocate_offspring()
            assert organism.copy_block(11)
            child_id = population.divide_publish(
                population.members[filler_id])
            self.assertIsNotNone(child_id)
            admitted += 1
        census_before_decision = len(population.members)
        self.assertEqual(census_before_decision, population.capacity)
        outcome = population.divide_publish(population.members["org-0"])
        self.assertIsNone(outcome)
        v_rejections = len([
            e for e in population.event_log
            if e.get("event") == "divide_failed"
            and e.get("reason") == "NO_VACANCY"])
        self.assertEqual(v_rejections, 1)
        # Exactly one shadow outcome per admission decision reaching stage V;
        # the full-census decision recorded would_not_admit.
        self.assertEqual(population.shadow_decisions, admitted + 1)
        self.assertEqual(population.shadow_would_admit, admitted)
        # The counters touched nothing else: all ledgers close and a further
        # pure evaluation still changes no state.
        population.assert_all_ledgers("shadow_side_effect_free")
        state_snapshot = deep_state(population)
        population.would_admit_now()
        self.assertEqual(deep_state(population), state_snapshot)


if __name__ == "__main__":
    unittest.main()
