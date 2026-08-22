"""Stage 7B2 population: two-genotype co-residence on the frozen 7B1 stack.

Extends the frozen ``stage7b1_mechanics.py`` machinery (commit ``62f2672``,
byte-identical, sha-bound in ``results/stage7b1/``) with exactly what the
SUPERSEDING preregistration ``docs/stage-7b2-preregistration.md`` requires for
its confirmatory configuration and nothing else:

- explicit founder genomes ``(A, T, D)`` with immutable ancestry IDs and a
  ``founder_registered`` event per founder, so every measurement input is an
  event-ledger record;
- the registered Section 2 configuration constants (window ``W``, census
  capacity ``N``, buffer depth ``d``, hazard rate, seed derivation, genotype
  pair, founder state);
- an assertion-scheduling override of ``assert_all_ledgers`` that preserves
  every checked property while making long windows tractable: live ledgers
  (reserve envelope, census, memory pool, vacancy invariants, no-eviction
  bound, live packet ledgers, newly written retirement records) are verified
  after *every* operation exactly as before; the full historical scan of
  immutable packet/retirement records runs at the registered tick-complete
  checkpoint and at ``initial``, and only tick-complete checkpoints are
  appended to ``closure_history``.

Telemetry labels, ancestry IDs, and genotype hashes are never read by
reserve, packet, memory, transition, scheduler, hazard, admission, or cost
logic; genotype affects only the registered allocation economics through
``A/D`` inside ``SliceOrganism.forage_rle``, which is the treatment itself.

No fitness, selection, invasion-growth, or evolutionary claim is made here;
this module runs populations, it does not interpret them.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable

from stage7_slice1 import SliceOrganism
from stage7_slice2 import PopulationMember
from stage7b1_mechanics import (
    REGISTERED_PACKET_RATE,
    BufferOverflowError,
    Stage7B1Population,
)

# ---------------------------------------------------------------------------
# Registered configuration (preregistration section 2) -- binding values
# ---------------------------------------------------------------------------

REGISTERED_WINDOW_TICKS = 600
"""Window ``W``: right-censoring boundary for every replicate."""

REGISTERED_CENSUS_CAPACITY = 12
"""Census capacity ``N``, identical across replicates and genotypes."""

REGISTERED_BUFFER_DEPTH = 64
"""Buffer depth ``d``: engineering bound, uniform in every run; layers 1-2
of 7B1 section 4.1 remain armed (BUFFER_OVERFLOW raises, run invalid)."""

REGISTERED_HAZARD_RATE = Fraction(1, 120)
"""Single hazard arm: age-independent, phenotype-blind per live member."""

REGISTERED_REPLICATE_SEED_BASE = 20260822
"""Seed derivation: ``hazard_seed = 20260822 + i`` for replicate ``i``."""

REGISTERED_REPLICATES = 32
"""Replicate count ``k``; runs differ only in the hazard stream seed."""

REGISTERED_FOUNDERS_PER_GENOTYPE = 3
REGISTERED_GENOTYPES: tuple[tuple[int, int, int], ...] = (
    (102, 128, 255),
    (204, 128, 255),
)
"""Exact continuation of the retained 7B0 channel lineage (LOW/HIGH)."""

REGISTERED_FOUNDER_S = Fraction(100)
"""Opening somatic reserve of every founder (7B0 INITIAL checkpoint value)."""

REGISTERED_CORPSE_TTL = 2
"""Carried frozen constant (Slice 2A / 7B1 registrations)."""

REGISTERED_PACKET_ENERGY = Fraction(300)
"""Packet energy of the registered monotonic-rich programme family."""


def registered_seed(index: int) -> int:
    """Registered seed derivation for replicate index ``index``."""
    if not 0 <= index < REGISTERED_REPLICATES:
        raise ValueError(f"replicate index must be in [0,{REGISTERED_REPLICATES})")
    return REGISTERED_REPLICATE_SEED_BASE + index


def registered_founder_genomes() -> list[tuple[int, int, int]]:
    """Founder genome blocks: 3 per genotype, contiguous organisation IDs."""
    genomes: list[tuple[int, int, int]] = []
    for genotype in REGISTERED_GENOTYPES:
        genomes.extend([genotype] * REGISTERED_FOUNDERS_PER_GENOTYPE)
    return genomes


class Stage7B2Population(Stage7B1Population):
    """Frozen 7B1 transaction mechanics carrying explicit founder genomes."""

    _retirements_verified = 0

    def __init__(
        self,
        founder_genomes: Iterable[tuple[int, int, int]],
        *,
        capacity: int,
        founder_s: Fraction,
        memory_pool: int,
        hazard_seed: int,
        hazard_rate: Fraction = REGISTERED_HAZARD_RATE,
        corpse_ttl: int = REGISTERED_CORPSE_TTL,
        packet_rate: int = REGISTERED_PACKET_RATE,
        buffer_depth: int = REGISTERED_BUFFER_DEPTH,
        packet_energy: Fraction = REGISTERED_PACKET_ENERGY,
        window_ticks: int = REGISTERED_WINDOW_TICKS,
    ) -> None:
        self.window_ticks = int(window_ticks)
        if self.window_ticks <= 0:
            raise ValueError("window must be positive")
        genomes = [(int(a), int(t), int(d)) for a, t, d in founder_genomes]
        if not genomes:
            raise ValueError("at least one founder genome is required")
        super().__init__(
            capacity=capacity,
            founder_count=0,
            founder_s=Fraction(founder_s),
            memory_pool=memory_pool,
            hazard_rate=Fraction(hazard_rate),
            hazard_seed=hazard_seed,
            corpse_ttl=corpse_ttl,
            packet_rate=packet_rate,
            buffer_depth=buffer_depth,
            packet_energy=Fraction(packet_energy),
        )
        founder_s = Fraction(founder_s)
        self.founders = len(genomes)
        self.opening_energy = founder_s * len(genomes)
        for index, (a, t, d) in enumerate(genomes):
            organism_id = f"org-{index}"
            organism = SliceOrganism(
                organism_id, self.memory, founder_s, Fraction(0),
                a=a, t=t, d=d,
            )
            self.members[organism_id] = PopulationMember(
                organism=organism, born_tick=-1)
            self.all_organisms[organism_id] = organism
            self.ancestry[organism_id] = f"F{index}"
            self._emit({
                "tick": 0,
                "phase": "configuration",
                "event": "founder_registered",
                "organism_id": organism_id,
                "ancestry_id": f"F{index}",
                "a_over_d": f"{a}/{d}",
                "t_over_d": f"{t}/{d}",
                "genotype_hash": self.genotype_hash(a, t, d),
                "s_initial": self.rat(founder_s),
                "r_initial": "0/1",
            })
        self.next_id = len(genomes)
        self.assert_all_ledgers("initial")

    # -- assertion scheduling -------------------------------------------------

    def assert_all_ledgers(self, operation: str) -> dict[str, Any]:
        """Live-state verification per operation; full scan per checkpoint.

        Checked after every operation (identical properties to the frozen
        7B1 closure): reserve envelope, census identity, memory-pool identity,
        buffer depth, static no-eviction bound, vacancy invariants, closure of
        every live (held) packet ledger, and closure of every retirement
        record written since the last verification.  At operations named
        ``tick_complete:<t>`` (and at ``initial``) the complete immutable
        history of packet ledgers, retirement records, and unread buffered
        budgets is rescanned, and only those operations append to
        ``closure_history``.
        """
        reserve = self.reserve_closure()
        if not reserve["closed"]:
            raise AssertionError(
                f"population reserve ledger failed after {operation}: "
                f"{reserve}")
        census = self.census_closure()
        if not census["closed"]:
            raise AssertionError(
                f"census ledger failed after {operation}: {census}")
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
        for packet in self.active_packets.values():
            packet.assert_closed()
        while self._retirements_verified < len(self.retirements):
            record = self.retirements[self._retirements_verified]
            closed = (
                record["destroyed_budget"]
                + record["retired_drawn_s"]
                + record["retired_drawn_r"]
                == record["initial_budget"]
            )
            if not closed:
                raise AssertionError(
                    f"retired packet ledger failed after {operation}: "
                    f"{record}")
            self._retirements_verified += 1
        checkpoint = (operation.startswith("tick_complete:")
                      or operation == "initial")
        if checkpoint:
            for packet in self.packets:
                packet.assert_closed()
            for record in self.retirements:
                closed = (
                    record["destroyed_budget"]
                    + record["retired_drawn_s"]
                    + record["retired_drawn_r"]
                    == record["initial_budget"]
                )
                if not closed:
                    raise AssertionError(
                        f"retirement history failed after {operation}: "
                        f"{record}")
            for packet in self.packet_buffer.buffer:
                if Fraction(packet.e_budget) != Fraction(packet.e_initial):
                    raise AssertionError(
                        f"unread packet budget failed after {operation}: "
                        f"packet={packet.packet_id} "
                        f"remaining={packet.e_budget} "
                        f"initial={packet.e_initial}")
            self.closure_history.append({
                "operation": operation,
                "tick": self.tick,
                "reserve_lhs": self.rat(reserve["lhs"]),
                "reserve_rhs": self.rat(reserve["rhs"]),
                "live_reserves": self.rat(reserve["live_reserves"]),
                "destroyed": self.rat(reserve["destroyed"]),
                "committed": self.rat(reserve["committed"]),
                "live_census": len(self.members),
                "stalled_census": sum(
                    member.state == "STALLED"
                    for member in self.members.values()),
                "buffered": len(self.packet_buffer.buffer),
                "packets_retired": len(self.retirements),
            })
        return {
            "reserve_closed": True,
            "census_closed": True,
            "packets_closed": True,
            "memory_closed": True,
            "no_eviction_bound_ok": True,
        }


def registered_population(hazard_seed: int) -> Stage7B2Population:
    """The registered Section 2 confirmatory configuration, verbatim."""
    return Stage7B2Population(
        founder_genomes=registered_founder_genomes(),
        capacity=REGISTERED_CENSUS_CAPACITY,
        founder_s=REGISTERED_FOUNDER_S,
        memory_pool=65536,
        hazard_seed=hazard_seed,
        hazard_rate=REGISTERED_HAZARD_RATE,
        corpse_ttl=REGISTERED_CORPSE_TTL,
        packet_rate=REGISTERED_PACKET_RATE,
        buffer_depth=REGISTERED_BUFFER_DEPTH,
        packet_energy=REGISTERED_PACKET_ENERGY,
        window_ticks=REGISTERED_WINDOW_TICKS,
    )


def run_window(population: Stage7B2Population) -> dict[str, Any]:
    """Run the registered window; classify BUFFER_OVERFLOW per Section 2.

    Returns a classification record.  ``COMPLETE`` means every tick finished
    with all ledgers asserted closed at every checkpoint; any
    ``BufferOverflowError`` classifies the run ``INVALID_IMPLEMENTATION``
    (layer-1 trigger) with the raising tick retained as evidence.  Any other
    exception is an implementation bug and propagates after recording the
    failure tick.
    """
    ticks_completed = 0
    try:
        for _ in range(population.window_ticks):
            population.step()
            ticks_completed += 1
    except BufferOverflowError as error:
        return {
            "classification": "INVALID_IMPLEMENTATION",
            "reason": "BUFFER_OVERFLOW",
            "detail": str(error),
            "ticks_completed": ticks_completed,
        }
    return {
        "classification": "COMPLETE",
        "ticks_completed": ticks_completed,
    }
