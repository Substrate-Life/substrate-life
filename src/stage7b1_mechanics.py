"""Stage 7B1 transaction-safe publication mechanics.

Implements the SUPERSEDING preregistration ``docs/stage-7b1-preregistration.md``
(§§2-5 plus the §6.2 shadow-telemetry obligation) as unexecuted mechanics code
pending the single-commit freeze of preregistration §9.2.  This module makes no
fitness, selection, or evolutionary claim and runs no stochastic assay.

Registered structures built here:

- ``SharedMemoryLedger`` extends the Slice 1 ledger with the explicit
  ``child_reserved`` bucket of blocker A invariant I2:
  ``free_pool + somatic_active + gestation + child_reserved + corpse_reserved
  = initial_pool``.
- ``GuardedPacketBuffer`` implements blocker C layer 1: overflow raises
  ``BUFFER_OVERFLOW`` instead of silently discarding.
- ``FaultInjector`` is the deterministic single-fault hook of §2.4.
- ``Stage7B1Population`` publishes children through the staged G/V/M/R/P/C
  transaction of §2.1 with the §2.2 rollback rule, retires packets by the §3
  equations, performs hazard death in the §5 six-step ordering, and records
  side-effect-free ``would_admit`` shadow outcomes per §6.2.

Static no-eviction bound (blocker C layer 3, registered configuration §4.2):
with packet rate ``r = 5``, a bounded window of ``W`` ticks, initial buffered
count ``d_0``, and depth ``d = 5W + d_0``, cumulative generation over the whole
window is ``rW = 5W = d - d_0``, so even with zero consumption
``cumulative_generated - cumulative_consumed <= d - d_0 <= d`` holds by
pigeonhole at every tick boundary; with the per-tick capturer guarantee the
induction ``generated_t - consumed_t <= generated_{t-1} - consumed_{t-1} + r``
never exceeds the same bound.  Configurations that admit stalls breaking the
guarantee fall back to layers 1-2 and are invalid on trigger; they may not be
registered as no-eviction.

Telemetry labels, ancestry IDs, and genotype hashes carried by the events of
this module are never read by reserve, packet, memory, transition, scheduler,
hazard, admission, or cost logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import random
from typing import Any

from datastream import PacketBuffer
from stage7_slice1 import (
    DIVIDE_COST,
    Child,
    MIN_WORKING_MEMORY,
    MemoryLedger,
    PacketLedger,
    SliceOrganism,
)
from stage7_slice2 import PopulationMember


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class InjectedFault(RuntimeError):
    """Raised by the FaultInjector at an armed registered boundary."""

    def __init__(self, boundary: str) -> None:
        super().__init__(f"injected fault at boundary {boundary}")
        self.boundary = boundary


class BufferOverflowError(RuntimeError):
    """Blocker C layer 1: loud, run-invalidating buffer overflow."""


# ---------------------------------------------------------------------------
# Blocker A: shared-memory ledger with the explicit child_reserved bucket
# ---------------------------------------------------------------------------


@dataclass
class SharedMemoryLedger(MemoryLedger):
    """MemoryLedger plus the registered ``child_reserved`` bucket (I2)."""

    child_reserved: dict[str, int] = field(default_factory=dict)

    def totals(self) -> dict[str, int]:
        totals = super().totals()
        totals["child_reserved"] = self._bucket_total(self.child_reserved)
        return totals

    def assert_closed(self, operation: str) -> None:
        totals = self.totals()
        observed = sum(totals.values())
        if observed != self.initial_pool:
            raise AssertionError(
                f"memory ledger failed after {operation}: "
                f"{observed} != {self.initial_pool}; {totals}"
            )
        self.history.append({
            "operation": operation,
            **totals,
            "ownership": {
                "somatic_active": dict(sorted(self.somatic_active.items())),
                "gestation": dict(sorted(self.gestation.items())),
                "corpse_reserved": dict(sorted(self.corpse_reserved.items())),
                "child_reserved": dict(sorted(self.child_reserved.items())),
            },
        })

    def reserve_child_memory(self, child_id: str, size: int) -> None:
        """Atomically reserve the child's full memory obligation."""
        if size <= 0:
            raise ValueError("child memory reservation must be positive")
        if child_id in self.child_reserved:
            raise ValueError(f"{child_id} already holds a child reservation")
        if self.free_pool < size:
            raise MemoryError(
                f"CHILD_MEMORY_UNAVAILABLE required={size} "
                f"available={self.free_pool}")
        self.free_pool -= size
        self.child_reserved[child_id] = size
        self.assert_closed(f"reserve_child_memory:{child_id}")

    def release_child_reservation(self, child_id: str) -> int:
        if child_id not in self.child_reserved:
            raise ValueError(f"{child_id} holds no child reservation")
        size = self.child_reserved.pop(child_id)
        self.free_pool += size
        self.assert_closed(f"release_child_memory:{child_id}")
        return size

    def convert_child_reservation(self, child_id: str) -> int:
        """Commit-point conversion of the reservation into ownership."""
        if child_id not in self.child_reserved:
            raise ValueError(f"{child_id} holds no child reservation")
        size = self.child_reserved.pop(child_id)
        self.somatic_active[child_id] = size
        self.assert_closed(f"commit_child_memory:{child_id}")
        return size


# ---------------------------------------------------------------------------
# Blocker C: raising guarded packet buffer (layer 1)
# ---------------------------------------------------------------------------


class GuardedPacketBuffer(PacketBuffer):
    """PacketBuffer whose overflow raises instead of dropping packets."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cumulative_generated = len(self.buffer)
        self.cumulative_consumed = 0

    def advance_tick(self) -> list[Any]:
        """Advance one tick; raise BUFFER_OVERFLOW rather than evict."""
        self.current_tick += 1
        for _ in range(self.packet_rate):
            if len(self.buffer) >= self.max_depth:
                raise BufferOverflowError(
                    f"BUFFER_OVERFLOW depth={self.max_depth}")
            self.buffer.append(self.stream.generate_packet(self.current_tick))
            self.cumulative_generated += 1
        return []

    def read(self) -> Any:
        packet = super().read()
        if packet is not None:
            self.cumulative_consumed += 1
        return packet


# ---------------------------------------------------------------------------
# Blocker A: deterministic single-fault injection hook
# ---------------------------------------------------------------------------

#: Registered injection boundaries.  The commit stage C deliberately has no
#: interior boundary: the commit point is atomic by construction.
INJECTION_BOUNDARIES: frozenset[str] = frozenset({
    "post_V", "mid_M", "post_M", "mid_R", "post_R", "mid_P", "pre_C",
})

_STAGE_OF_BOUNDARY = {
    "post_V": "V",
    "mid_M": "M",
    "post_M": "M",
    "mid_R": "R",
    "post_R": "R",
    "mid_P": "P",
    "pre_C": "P",
}


class FaultInjector:
    """Deterministic hook: one armed boundary, one raise, no in-run retry."""

    def __init__(self, boundary: str | None = None) -> None:
        if boundary is not None and boundary not in INJECTION_BOUNDARIES:
            raise ValueError(f"unregistered injection boundary {boundary!r}")
        self.boundary = boundary
        self.fired_at: str | None = None

    def arm(self, boundary: str) -> None:
        if boundary not in INJECTION_BOUNDARIES:
            raise ValueError(f"unregistered injection boundary {boundary!r}")
        self.boundary = boundary
        self.fired_at = None

    def checkpoint(self, boundary: str) -> None:
        if self.boundary == boundary and self.fired_at is None:
            self.fired_at = boundary
            raise InjectedFault(boundary)


# ---------------------------------------------------------------------------
# Registered deterministic configuration (blocker C layer 3, §4.2)
# ---------------------------------------------------------------------------

REGISTERED_PACKET_RATE = 5
"""Slice 2A provisional constant, registered for the deterministic suite."""


def registered_buffer_depth(window_ticks: int, initial_buffered: int = 0) -> int:
    """Registered depth ``d = 5W + d_0`` for a bounded window of W ticks."""
    if window_ticks <= 0:
        raise ValueError("window must be positive")
    if initial_buffered < 0:
        raise ValueError("initial buffered count must be non-negative")
    return REGISTERED_PACKET_RATE * window_ticks + initial_buffered


# ---------------------------------------------------------------------------
# Blockers A/B/D/F: the transaction-safe population
# ---------------------------------------------------------------------------

_FAILURE_REASONS = frozenset(
    {"NO_VACANCY", "CHILD_MEMORY_UNAVAILABLE", "FAULT_INJECTED"})


@dataclass
class DivideTxn:
    """Private per-attempt state of one staged DIVIDE publication."""

    parent_id: str
    child_id: str
    rng_at_start: int
    r_w: Fraction = Fraction(0)
    p_value: Fraction | None = None
    vacancy_held: bool = False
    gestation_discarded: bool = False
    child_reserved: bool = False
    candidate_basis: int = 0
    committed: bool = False


class Stage7B1Population:
    """Deterministic mechanics harness with staged child publication."""

    def __init__(
        self,
        capacity: int,
        founder_count: int,
        founder_s: Fraction,
        memory_pool: int,
        hazard_schedule: dict[int, set[str]] | None = None,
        hazard_rate: Fraction = Fraction(0),
        hazard_seed: int = 73,
        corpse_ttl: int = 2,
        packet_rate: int = REGISTERED_PACKET_RATE,
        buffer_depth: int = 8,
        packet_energy: Fraction = Fraction(300),
        initial_buffer_packets: int = 0,
    ) -> None:
        if capacity <= 0 or not (0 <= founder_count <= capacity):
            raise ValueError("require capacity>0 and 0<=founders<=capacity")
        if corpse_ttl < 0:
            raise ValueError("corpse_ttl must be non-negative")
        hazard_rate = Fraction(hazard_rate)
        if not (0 <= hazard_rate <= 1):
            raise ValueError("hazard_rate must be in [0,1]")
        self.capacity = capacity
        self.memory = SharedMemoryLedger(memory_pool)
        self.hazard_schedule = hazard_schedule or {}
        self.hazard_rate = hazard_rate
        self.hazard_rng = random.Random(hazard_seed)
        self.corpse_ttl = corpse_ttl
        self.tick = 0
        self.members: dict[str, PopulationMember] = {}
        self.all_organisms: dict[str, SliceOrganism] = {}
        self.ancestry: dict[str, str] = {}
        self.packets: list[PacketLedger] = []
        self.active_packets: dict[int, PacketLedger] = {}
        self.compressed_buffers: dict[int, bytes] = {}
        self.held_packets: dict[str, set[int]] = {}
        self.retired_packet_ids: set[int] = set()
        self.retirements: list[dict[str, Any]] = []
        self.corpse_expiry: dict[str, int] = {}
        self.vacancy_reserved = 0
        self.founders = founder_count
        self.admitted_births = 0
        self.hazard_removals = 0
        self.rng_draws = 0
        self.terminal_disposed = Fraction(0)
        self.destroyed_packet_budget = Fraction(0)
        self.opening_energy = Fraction(founder_s) * founder_count
        self.next_id = founder_count
        self.event_log: list[dict[str, Any]] = []
        self.closure_history: list[dict[str, Any]] = []
        self.shadow_decisions = 0
        self.shadow_would_admit = 0
        self.capture_attempts_this_tick = 0
        self.observations: list[dict[str, Any]] | None = None
        self.packet_buffer = GuardedPacketBuffer(
            seed=42,
            phase_mode="monotonic_rich",
            packet_e_rich=Fraction(packet_energy),
            packet_e_lean=Fraction(packet_energy),
            packet_rate=packet_rate,
            buffer_depth=buffer_depth,
            initial_buffer_packets=initial_buffer_packets,
        )
        for index in range(founder_count):
            organism_id = f"org-{index}"
            organism = SliceOrganism(
                organism_id, self.memory, Fraction(founder_s), Fraction(0))
            self.members[organism_id] = PopulationMember(
                organism=organism, born_tick=-1)
            self.all_organisms[organism_id] = organism
            self.ancestry[organism_id] = f"F{index}"
        self.assert_all_ledgers("initial")

    # -- identifiers and telemetry ------------------------------------------

    def _new_id(self) -> str:
        organism_id = f"org-{self.next_id}"
        self.next_id += 1
        return organism_id

    def _emit(self, event: dict[str, Any]) -> None:
        self.event_log.append(event)

    @staticmethod
    def genotype_hash(a: int, t: int, d: int) -> str:
        """Telemetry-only digest of heritable state (A,T,D)."""
        return hashlib.sha256(f"{a}/{t}/{d}".encode()).hexdigest()[:16]

    @staticmethod
    def rat(value: Fraction) -> str:
        """Canonical exact serialisation of a rational."""
        return f"{value.numerator}/{value.denominator}"

    def consume_registered_draw(self, count: int = 1) -> None:
        """Account one unrelated registered RNG draw (testable counter)."""
        if count < 0:
            raise ValueError("draw count must be non-negative")
        self.rng_draws += count

    # -- closures -------------------------------------------------------------

    def census_closure(self) -> dict[str, Any]:
        lhs = self.founders + self.admitted_births - self.hazard_removals
        return {
            "lhs": lhs,
            "rhs": len(self.members),
            "closed": lhs == len(self.members),
        }

    def reserve_closure(self) -> dict[str, Any]:
        live = sum(
            (member.organism.s + member.organism.r
             for member in self.members.values()),
            Fraction(0),
        )
        destroyed = (
            self.terminal_disposed
            + self.destroyed_packet_budget
            + sum((organism.destroyed
                   for organism in self.all_organisms.values()), Fraction(0))
        )
        gross = sum((o.gross_income for o in self.all_organisms.values()),
                    Fraction(0))
        reversed_income = sum(
            (o.reversed_income for o in self.all_organisms.values()),
            Fraction(0))
        costs = sum((o.c_s + o.c_r for o in self.all_organisms.values()),
                    Fraction(0))
        committed = sum(
            (o.committed for o in self.all_organisms.values()), Fraction(0))
        lhs = live + destroyed + committed
        # Destroyed packet budget enters the envelope as supply and exits to
        # the destroyed sink in the same step: an undrawn residual was never
        # any member's reserve, so crediting the sink exactly once requires
        # the matching environmental supply term.  Retired drawn provenance
        # never appears here (blocker B closure equation 2).
        rhs = (self.opening_energy + self.destroyed_packet_budget
               + gross - reversed_income - costs)
        return {
            "lhs": lhs,
            "rhs": rhs,
            "closed": lhs == rhs,
            "live_reserves": live,
            "destroyed": destroyed,
            "committed": committed,
            "net_income": gross - reversed_income,
            "costs": costs,
        }

    def assert_all_ledgers(self, operation: str) -> dict[str, Any]:
        reserve = self.reserve_closure()
        if not reserve["closed"]:
            raise AssertionError(
                f"population reserve ledger failed after {operation}: "
                f"{reserve}")
        census = self.census_closure()
        if not census["closed"]:
            raise AssertionError(
                f"census ledger failed after {operation}: {census}")
        for packet in self.packets:
            packet.assert_closed()
        for packet in self.packet_buffer.buffer:
            if Fraction(packet.e_budget) != Fraction(packet.e_initial):
                raise AssertionError(
                    f"unread packet budget failed after {operation}: "
                    f"packet={packet.packet_id} remaining={packet.e_budget} "
                    f"initial={packet.e_initial}")
        for retirement in self.retirements:
            closed = (
                retirement["destroyed_budget"]
                + retirement["retired_drawn_s"]
                + retirement["retired_drawn_r"]
                == retirement["initial_budget"]
            )
            if not closed:
                raise AssertionError(
                    f"retired packet ledger failed after {operation}: "
                    f"{retirement}")
        if sum(self.memory.totals().values()) != self.memory.initial_pool:
            raise AssertionError(f"memory ledger failed after {operation}")
        if len(self.packet_buffer.buffer) > self.packet_buffer.max_depth:
            raise AssertionError(
                f"buffer depth exceeded after {operation}: "
                f"{len(self.packet_buffer.buffer)} > "
                f"{self.packet_buffer.max_depth}")
        bound = (self.packet_buffer.cumulative_generated
                 - self.packet_buffer.cumulative_consumed)
        if bound > self.packet_buffer.max_depth:
            raise AssertionError(
                f"static no-eviction bound violated after {operation}: "
                f"generated-consumed={bound} > depth="
                f"{self.packet_buffer.max_depth}")
        if self.vacancy_reserved < 0:
            raise AssertionError(f"negative vacancy reservation: {operation}")
        if len(self.members) + self.vacancy_reserved > self.capacity:
            raise AssertionError(
                f"vacancy invariant violated after {operation}: "
                f"live={len(self.members)} reserved={self.vacancy_reserved}")
        snapshot = {
            "operation": operation,
            "reserve_closed": True,
            "census_closed": True,
            "packets_closed": True,
            "memory_closed": True,
            "no_eviction_bound_ok": True,
            "reserve_lhs": reserve["lhs"],
            "reserve_rhs": reserve["rhs"],
        }
        self.closure_history.append(snapshot)
        return snapshot

    # -- Blocker F: side-effect-free shadow admission telemetry --------------

    def vacancies_available(self) -> int:
        return self.capacity - len(self.members) - self.vacancy_reserved

    def would_admit_now(self) -> bool:
        """Pure read: would a birth be admitted if capacity were available?

        Touches no census, memory, packet, or reserve state.
        """
        return self.vacancies_available() > 0

    def _record_shadow_outcome(self, would_admit: bool) -> None:
        self.shadow_decisions += 1
        self.shadow_would_admit += int(would_admit)

    # -- Blocker B: packet retirement ----------------------------------------

    def _register_hold(self, holder_id: str, packet: PacketLedger) -> None:
        self.active_packets[packet.packet_id] = packet
        self.held_packets.setdefault(holder_id, set()).add(packet.packet_id)

    def assert_not_retired(self, packet_id: int) -> None:
        if packet_id in self.retired_packet_ids:
            raise RuntimeError(
                f"packet {packet_id} is retired; no further draw, return, "
                "or re-capture may reference it")

    def attempt_return(self, holder_id: str, packet: PacketLedger,
                       extent: int) -> bool:
        """Population-mediated reversal with the retirement guard."""
        self.assert_not_retired(packet.packet_id)
        organism = self.all_organisms[holder_id]
        compressed = self.compressed_buffers.get(packet.packet_id)
        if compressed is None:
            raise ValueError("packet carries no compressed buffer to expand")
        result = organism.reverse_rle(packet, compressed, extent)
        if result:
            self._emit({
                "tick": self.tick, "phase": "packet_return",
                "event": "packet_returned", "organism_id": holder_id,
                "packet_id": packet.packet_id,
                "lifetime_a_over_d": self.rat(Fraction(organism.a, organism.d)),
                "budget_post": self.rat(packet.budget_remaining),
                "drawn_s_post": self.rat(packet.drawn_s),
                "drawn_r_post": self.rat(packet.drawn_r),
                "committed_flag": True,
            })
        else:
            self._emit({
                "tick": self.tick, "phase": "packet_return",
                "event": "packet_return_failed", "organism_id": holder_id,
                "packet_id": packet.packet_id,
                "requested_vs_debited": "atomic_no_debit",
                "committed_flag": False,
            })
        self.assert_all_ledgers(f"packet_return:{holder_id}:{packet.packet_id}")
        return result

    def explicitly_destroy_packet(self, holder_id: str, packet_id: int) -> None:
        """Terminal destruction by the holder (reason EXPLICIT_DESTROY)."""
        self.assert_not_retired(packet_id)
        if packet_id not in self.active_packets:
            raise ValueError(f"packet {packet_id} is not active")
        held = self.held_packets.get(holder_id, set())
        if packet_id not in held:
            raise ValueError(f"{holder_id} does not hold packet {packet_id}")
        packet = self.active_packets[packet_id]
        held.discard(packet_id)
        del self.active_packets[packet_id]
        self._retire_packet(packet, holder_id, "EXPLICIT_DESTROY")

    def _retire_packet(self, packet: PacketLedger, holder_id: str,
                       reason: str, verify_now: bool = True) -> None:
        if reason not in {"HOLDER_DEATH", "EXPLICIT_DESTROY"}:
            raise ValueError(f"unregistered retirement reason {reason!r}")
        if packet.packet_id in self.retired_packet_ids:
            raise AssertionError(
                f"double retirement of packet {packet.packet_id}")
        destroyed_budget = Fraction(packet.budget_remaining)
        event = {
            "tick": self.tick,
            "phase": "retirement",
            "event": "packet_retired",
            "packet_id": packet.packet_id,
            "holder_id": holder_id,
            "reason": reason,
            "destroyed_budget": destroyed_budget,
            "retired_drawn_s": Fraction(packet.drawn_s),
            "retired_drawn_r": Fraction(packet.drawn_r),
            "initial_budget": Fraction(packet.initial_budget),
        }
        self.destroyed_packet_budget += destroyed_budget
        self.retired_packet_ids.add(packet.packet_id)
        self.retirements.append(dict(event))
        self._emit(event)
        if verify_now:
            self.assert_all_ledgers(f"packet_retired:{packet.packet_id}")

    # -- Blocker D: hazard death ordering -------------------------------------

    def _hazard_remove(self, organism_id: str) -> None:
        member = self.members.pop(organism_id)
        organism = member.organism
        # Step 1: marked dead; already excluded from the survivor snapshot
        # because the hazard phase precedes it.
        member.state = "DEAD"
        # Step 2: retire any held packet with reason HOLDER_DEATH.  The
        # per-retirement closure check is deferred: between this step and
        # step 4 the victim's reserves are intentionally in transit.
        for packet_id in sorted(self.held_packets.get(organism_id, set())):
            packet = self.active_packets.pop(packet_id)
            self._retire_packet(packet, organism_id, "HOLDER_DEATH",
                                verify_now=False)
        self.held_packets.pop(organism_id, None)
        # Step 3: release live gestation; no death-tick upkeep is charged
        # (architecture §5.3: released before the upkeep boundary).
        if organism_id in self.memory.gestation:
            released = self.memory.release_gestation(organism_id)
            self._emit({
                "tick": self.tick, "phase": "hazard",
                "event": "gestation_released",
                "organism_id": organism_id,
                "gestation_bytes": released,
                "release_reason": "HAZARD_DEATH",
            })
        # Step 4: terminal disposal of exact S_o and R_o; no rescue, no
        # inheritance; one death_disposal event carries both exact amounts.
        s_disposed = organism.s
        r_disposed = organism.r
        self.terminal_disposed += s_disposed + r_disposed
        organism.s = Fraction(0)
        organism.r = Fraction(0)
        self._emit({
            "tick": self.tick, "phase": "hazard",
            "event": "death_disposal",
            "organism_id": organism_id,
            "s_disposed": s_disposed,
            "r_disposed": r_disposed,
            "ancestry_id": self.ancestry.get(organism_id),
            "genotype_hash": self.genotype_hash(organism.a, organism.t,
                                                organism.d),
            "realised_y": organism.gross_income,
        })
        # Step 5: corpse reservation for the registered TTL.
        self.memory.move_somatic_to_corpse(organism_id)
        self.corpse_expiry[organism_id] = self.tick + self.corpse_ttl
        self.hazard_removals += 1
        self._emit({
            "tick": self.tick, "phase": "hazard",
            "event": "hazard_death", "organism_id": organism_id,
        })
        # Step 6: census and reserve closures updated and asserted below.
        self.assert_all_ledgers(f"hazard_death:{organism_id}")

    def _expire_corpses(self) -> None:
        due = sorted(
            organism_id for organism_id, expiry in self.corpse_expiry.items()
            if expiry <= self.tick
        )
        for organism_id in due:
            restored = self.memory.expire_corpse(organism_id)
            del self.corpse_expiry[organism_id]
            self._emit({
                "tick": self.tick, "phase": "cleanup",
                "event": "corpse_expired", "organism_id": organism_id,
                "bytes_restored": restored,
            })
            self.assert_all_ledgers(f"corpse_expiry:{organism_id}")

    # -- Blocker A: staged DIVIDE publication transaction ---------------------

    def divide_publish(self, member: PopulationMember,
                       injector: FaultInjector | None = None) -> str | None:
        """Publish one child through the registered G/V/M/R/P/C stages.

        Returns the child id on success and ``None`` on a registered
        non-fault failure (NO_VACANCY, CHILD_MEMORY_UNAVAILABLE).  Injected
        faults roll back per §2.2 and re-raise ``InjectedFault``.
        """
        organism = member.organism
        parent_id = organism.organism_id
        # Stage G: validate the registered complete-gestation condition.
        if parent_id not in self.memory.gestation:
            raise RuntimeError("DIVIDE requires parent-owned complete gestation")
        child_id = self._new_id()
        txn = DivideTxn(parent_id=parent_id, child_id=child_id,
                        rng_at_start=self.rng_draws)
        try:
            # Stage V: atomically reserve one census vacancy.
            if self.would_admit_now():
                would_admit = True
            else:
                would_admit = False
            self._record_shadow_outcome(would_admit)
            if not would_admit:
                # Registered NO_VACANCY: no provisioning is computed; the
                # completed bout is discarded (architecture §7 step 2/4);
                # a failed attempt is never retried from stale gestation.
                self.memory.release_gestation(parent_id)
                txn.gestation_discarded = True
                self._emit({
                    "tick": self.tick, "phase": "admission",
                    "event": "divide_failed", "organism_id": parent_id,
                    "stage": "V", "reason": "NO_VACANCY",
                })
                self.next_id -= 1
                self.assert_all_ledgers(f"divide_no_vacancy:{parent_id}")
                return None
            self.vacancy_reserved += 1
            txn.vacancy_held = True
            self.observe("post_V", txn)
            if injector is not None:
                injector.checkpoint("post_V")

            # Stage M: structural zero-draw indel candidate (mutation is
            # disabled throughout Stage 7B1); consumed RNG stays consumed.
            candidate_a, candidate_t, candidate_d = organism.a, organism.t, organism.d
            if not (candidate_d > 0 and 0 <= candidate_t <= candidate_d
                    and 0 <= candidate_a <= candidate_d):
                raise ValueError("post-indel candidate violates trait bounds")
            self.observe("mid_M", txn)
            if injector is not None:
                injector.checkpoint("mid_M")
            txn.candidate_basis = MIN_WORKING_MEMORY
            self.observe("post_M", txn)
            if injector is not None:
                injector.checkpoint("post_M")

            # Stage R: release the parent gestation, then atomically reserve
            # the child's full memory obligation from the candidate basis.
            self.memory.release_gestation(parent_id)
            txn.gestation_discarded = True
            if injector is not None:
                injector.checkpoint("mid_R")
            try:
                self.memory.reserve_child_memory(child_id, txn.candidate_basis)
            except MemoryError:
                self.vacancy_reserved -= 1
                txn.vacancy_held = False
                self._emit({
                    "tick": self.tick, "phase": "admission",
                    "event": "divide_failed", "organism_id": parent_id,
                    "stage": "R", "reason": "CHILD_MEMORY_UNAVAILABLE",
                })
                self.assert_all_ledgers(
                    f"divide_child_memory_unavailable:{parent_id}")
                return None
            txn.child_reserved = True
            self.observe("post_R", txn)
            if injector is not None:
                injector.checkpoint("post_R")

            # Stage P: exact provisional provisioning P=(T/D)R_w.
            txn.r_w = organism.r
            p_value = organism.tau_r * txn.r_w
            organism.r -= p_value
            txn.p_value = p_value
            if injector is not None:
                injector.checkpoint("mid_P")
            provisional_child = Child(
                child_id, s=p_value, a=candidate_a, t=candidate_t,
                d=candidate_d,
            )
            if injector is not None:
                injector.checkpoint("pre_C")

            # Stage C: single commit point.  No injector boundary, no event
            # emission, and no fallible operation exists inside this block;
            # trait bounds were validated in stage M.
            self.memory.convert_child_reservation(child_id)
            txn.child_reserved = False
            child = SliceOrganism(
                child_id, self.memory, provisional_child.s, Fraction(0),
                a=provisional_child.a, t=provisional_child.t,
                d=provisional_child.d,
                initial_memory_already_committed=True,
            )
            self.members[child_id] = PopulationMember(
                organism=child, born_tick=self.tick)
            self.all_organisms[child_id] = child
            self.ancestry[child_id] = self.ancestry.get(parent_id, parent_id)
            self.vacancy_reserved -= 1
            txn.vacancy_held = False
            self.admitted_births += 1
            txn.committed = True
            self.observe("post_C", txn)
            self._emit({
                "tick": self.tick, "phase": "admission",
                "event": "provision_committed", "organism_id": parent_id,
                "child_id": child_id,
                "provision": p_value,
                "r_w": txn.r_w,
                "p_equation": "P=(T/D)*R_w",
                "inherited_a_over_d": f"{candidate_a}/{candidate_d}",
                "inherited_t_over_d": f"{candidate_t}/{candidate_d}",
                "ancestry_id": self.ancestry[child_id],
                "genotype_hash": self.genotype_hash(
                    candidate_a, candidate_t, candidate_d),
                "realised_y_parent": organism.gross_income,
                "parent_s_pre": self.rat(Fraction(organism.s)),
                "parent_r_pre": self.rat(Fraction(organism.r) + p_value),
                "parent_s_post": self.rat(Fraction(organism.s)),
                "parent_r_post": self.rat(Fraction(organism.r)),
                "c_s_cumulative": organism.c_s,
                "c_r_cumulative": organism.c_r,
                "child_initial_s": provisional_child.s,
                "child_initial_r": Fraction(0),
                "candidate_memory_basis": txn.candidate_basis,
                "child_memory_reserved": txn.candidate_basis,
                "gestation_bytes_released": txn.candidate_basis,
                "vacancy_reserved_after": self.vacancy_reserved,
                "copy_stage_rng_consumed": False,
                "divide_stage_rng_consumed": False,
                "rng_draws_total": self.rng_draws,
                "committed_flag": True,
            })
            self._emit({
                "tick": self.tick, "phase": "admission",
                "event": "birth_admitted", "parent_id": parent_id,
                "child_id": child_id,
                "provision": p_value,
                "ancestry_id": self.ancestry[child_id],
                "genotype_hash": self.genotype_hash(
                    candidate_a, candidate_t, candidate_d),
                "shadow_would_admit": True,
            })
            self.assert_all_ledgers(f"birth_admitted:{child_id}")
            return child_id
        except InjectedFault as fault:
            self._rollback_divide(txn, fault.boundary)
            raise
        except Exception:
            # Architecture §7 step 7: ANY exception after vacancy reservation
            # and before commit rolls back identically.  Unexpected (non-
            # injected) exceptions carry no registered failure record -- they
            # indicate an implementation bug and classify the run invalid --
            # but they must never leave a reservation or partial child.
            if not txn.committed:
                self._rollback_divide(txn, None)
            raise

    def _rollback_divide(self, txn: DivideTxn,
                         boundary: str | None) -> None:
        """Registered §2.2 rollback for any fault after V and before C.

        ``boundary is None`` marks an unexpected (non-injected) exception:
        identical resource rollback but no registered failure record.
        """
        organism = self.all_organisms[txn.parent_id]
        # Refund P exactly if it was provisionally debited: the exact stored
        # Fraction, never recomputed.
        if txn.p_value is not None:
            organism.r += txn.p_value
        # Release the child-memory reservation.
        if txn.child_reserved:
            self.memory.release_child_reservation(txn.child_id)
            txn.child_reserved = False
        # Discard candidate and gestation state if still held.
        if not txn.gestation_discarded and txn.parent_id in self.memory.gestation:
            self.memory.release_gestation(txn.parent_id)
            txn.gestation_discarded = True
        # Release the vacancy reservation.
        if txn.vacancy_held:
            self.vacancy_reserved -= 1
            txn.vacancy_held = False
        # The provisional child never entered census, scheduler, or ledger.
        # Exactly one failure-stage record; P is omitted from telemetry.
        if boundary is not None:
            self._emit({
                "tick": self.tick, "phase": "admission",
                "event": "divide_failed", "organism_id": txn.parent_id,
                "stage": _STAGE_OF_BOUNDARY[boundary],
                "reason": "FAULT_INJECTED",
            })
        self.assert_all_ledgers(f"divide_rollback:{txn.parent_id}:{boundary}")

    def observe(self, tag: str, txn: DivideTxn) -> None:
        """Optional white-box observation hook for atomicity inspection."""
        if self.observations is None:
            return
        self.observations.append({
            "tag": tag,
            "members": sorted(self.members),
            "child_visible": txn.child_id in self.members,
            "child_in_somatic": txn.child_id in self.memory.somatic_active,
            "child_reserved_bucket": txn.child_id in self.memory.child_reserved,
            "vacancy_reserved": self.vacancy_reserved,
            "memory_totals": self.memory.totals(),
        })

    # -- integrated reproductive cycle ----------------------------------------

    def _capture(self, member: PopulationMember) -> PacketLedger | None:
        organism = member.organism
        self.capture_attempts_this_tick += 1
        source = self.packet_buffer.read()
        if source is None:
            organism.charge_s(Fraction(10), "READ_EMPTY")
            self.memory.resize_somatic(
                organism.organism_id, 64, "read_empty_resize")
            organism.ordinary_upkeep("READ_EMPTY")
            self._emit({
                "tick": self.tick, "phase": "packet_capture",
                "event": "packet_capture_failed",
                "organism_id": organism.organism_id,
            })
            self.assert_all_ledgers(
                f"packet_capture_failed:{organism.organism_id}")
            return None
        packet = PacketLedger(
            packet_id=source.packet_id,
            initial_budget=Fraction(source.e_initial),
            max_reducible=source.max_reducible,
        )
        self.packets.append(packet)
        self._register_hold(organism.organism_id, packet)
        transformed = organism.forage_rle(packet, source.data)
        self.compressed_buffers[packet.packet_id] = transformed
        self._emit({
            "tick": self.tick, "phase": "packet_capture",
            "event": "packet_draw", "organism_id": organism.organism_id,
            "packet_id": packet.packet_id,
            "lifetime_a_over_d": self.rat(Fraction(organism.a, organism.d)),
            "budget_pre": self.rat(Fraction(source.e_initial)),
            "budget_post": self.rat(packet.budget_remaining),
            "drawn_s_post": self.rat(packet.drawn_s),
            "drawn_r_post": self.rat(packet.drawn_r),
            "requested_vs_debited": "equal_exact",
            "transform_code": "RLE",
            "committed_flag": True,
        })
        self.assert_all_ledgers(f"packet_draw:{organism.organism_id}")
        return packet

    def _release_failed_cycle_gestation(self, organism: SliceOrganism,
                                        reason: str) -> None:
        if organism.organism_id in self.memory.gestation:
            self.memory.release_gestation(organism.organism_id)
            organism._record("gestation_released_after_failure", reason=reason)
            self.assert_all_ledgers(
                f"gestation_failure_cleanup:{organism.organism_id}:{reason}")

    def _run_reproductive_cycle(self, member: PopulationMember) -> str | None:
        organism = member.organism
        packet = self._capture(member)
        if packet is None:
            return None
        if not organism.allocate_offspring():
            return None
        if not organism.copy_block(11):
            self._release_failed_cycle_gestation(
                organism, "COPY_BLOCK_R_UNAVAILABLE")
            return None
        # The DIVIDE opcode's reproductive work is prepaid before the staged
        # transaction begins (architecture §7: the transaction runs after
        # C_S and C_R have been prepaid; prepaid work is never refunded).
        if not organism._prepay_reproductive(DIVIDE_COST, "DIVIDE"):
            organism.ordinary_upkeep("DIVIDE_FAILED_R")
            self._release_failed_cycle_gestation(
                organism, "DIVIDE_R_UNAVAILABLE")
            return None
        child_id = self.divide_publish(member)
        return child_id

    # -- tick -----------------------------------------------------------------

    def step(self) -> dict[str, Any]:
        self.capture_attempts_this_tick = 0
        # Packet arrival (layer-1 guard raises on overflow).
        self.packet_buffer.advance_tick()
        # Hazard phase.
        hazard_deaths: list[str] = []
        if self.tick in self.hazard_schedule:
            selected_hazards = set(self.hazard_schedule[self.tick])
        else:
            selected_hazards = {
                organism_id for organism_id in sorted(self.members)
                if self.hazard_rng.random() < float(self.hazard_rate)
            }
        for organism_id in sorted(selected_hazards):
            if organism_id in self.members:
                self._hazard_remove(organism_id)
                hazard_deaths.append(organism_id)
        # Survivor snapshot and execution (newborns join next tick).
        scheduler_snapshot = sorted(self.members)
        executed = list(scheduler_snapshot)
        newborn_ids: list[str] = []
        for organism_id in scheduler_snapshot:
            member = self.members.get(organism_id)
            if member is None or member.state != "ACTIVE":
                continue
            member.last_run_tick = self.tick
            if member.organism.s < 10:
                member.state = "STALLED"
                self._emit({
                    "tick": self.tick, "phase": "scheduler",
                    "event": "somatic_stall", "organism_id": organism_id,
                    "reserve": member.organism.s,
                })
                self.assert_all_ledgers(f"somatic_stall:{organism_id}")
                continue
            try:
                child_id = self._run_reproductive_cycle(member)
            except InjectedFault:
                # Fault injection targets single transactions in dedicated
                # tests; an injected fault escaping into the tick loop is an
                # implementation bug, never a registered failure class.
                raise
            except MemoryError as error:
                try:
                    member.organism.ordinary_upkeep("MEMORY_BLOCKED_ATTEMPT")
                except RuntimeError as upkeep_error:
                    if "S=0 behavior" not in str(upkeep_error):
                        raise
                    member.state = "STALLED"
                self._release_failed_cycle_gestation(
                    member.organism, "SHARED_MEMORY_UNAVAILABLE")
                self._emit({
                    "tick": self.tick, "phase": "scheduler",
                    "event": "memory_blocked_attempt",
                    "organism_id": organism_id, "reason": str(error),
                })
                self.assert_all_ledgers(f"memory_blocked:{organism_id}")
                continue
            except RuntimeError as error:
                if "R unavailable for gestation upkeep" in str(error):
                    self._release_failed_cycle_gestation(
                        member.organism, "GESTATION_UPKEEP_R_UNAVAILABLE")
                    self._emit({
                        "tick": self.tick, "phase": "scheduler",
                        "event": "reproductive_failure",
                        "organism_id": organism_id,
                        "reason": "gestation_upkeep_r_unavailable",
                    })
                    self.assert_all_ledgers(
                        f"reproductive_failure:{organism_id}")
                    continue
                if "S=0 behavior" not in str(error):
                    raise
                member.state = "STALLED"
                self._emit({
                    "tick": self.tick, "phase": "scheduler",
                    "event": "somatic_stall", "organism_id": organism_id,
                    "reserve": member.organism.s,
                    "reason": "mid_cycle_somatic_prepayment_failure",
                })
                self.assert_all_ledgers(f"mid_cycle_stall:{organism_id}")
                continue
            if child_id is not None:
                newborn_ids.append(child_id)
        # Corpse expiry, then the tick-complete closure (layer-2 assertion
        # lives inside assert_all_ledgers).
        self._expire_corpses()
        closure = self.assert_all_ledgers(f"tick_complete:{self.tick}")
        snapshot = {
            "tick": self.tick,
            "hazard_deaths": hazard_deaths,
            "admitted_births": len(newborn_ids),
            "newborn_ids": newborn_ids,
            "live_census": len(self.members),
            "stalled_census": sum(
                m.state == "STALLED" for m in self.members.values()),
            "capture_attempts": self.capture_attempts_this_tick,
            "executed_ids": executed,
            "vacancy_reserved": self.vacancy_reserved,
            **{key: closure[key] for key in
               ("reserve_closed", "census_closed", "packets_closed",
                "memory_closed", "no_eviction_bound_ok")},
        }
        self.tick += 1
        return snapshot


def registered_deterministic_population(
    window_ticks: int,
    capacity: int = 8,
    founder_count: int = 8,
    founder_s: Fraction = Fraction(100000),
    memory_pool: int = 65536,
    hazard_rate: Fraction = Fraction(0),
    **overrides: Any,
) -> Stage7B1Population:
    """Registered §4.2 no-eviction configuration for a bounded window.

    ``r = 5``, ``d = 5W + d_0`` with ``d_0 = 0``, generous founder reserves
    so at least one live unstalled member attempts capture every tick, and
    zero hazard.  Any keyword override widens the configuration beyond the
    registered one and is the caller's responsibility.
    """
    return Stage7B1Population(
        capacity=capacity,
        founder_count=founder_count,
        founder_s=founder_s,
        memory_pool=memory_pool,
        hazard_rate=hazard_rate,
        packet_rate=REGISTERED_PACKET_RATE,
        buffer_depth=registered_buffer_depth(window_ticks, 0),
        **overrides,
    )
