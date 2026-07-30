"""Stage 7 Slice 2A: mechanics-only population integration.

This module extends the exact Slice 1 ledger into a bounded population harness.
It implements no mutation, evolutionary contrast, or scientific assay.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from collections import Counter
import random
from typing import Any

from datastream import PacketBuffer
from consts import PACKET_SIZE
from stage7_slice1 import (
    DIVIDE_COST,
    MemoryLedger,
    PacketLedger,
    SliceOrganism,
)


@dataclass
class PopulationMember:
    organism: SliceOrganism
    born_tick: int
    state: str = "ACTIVE"
    last_run_tick: int | None = None


class Stage7Population:
    """Deterministic mechanics harness with exogenous hazard and vacancies."""

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
        packet_rate: int = 5,
        buffer_depth: int = 8,
        packet_energy: Fraction = Fraction(300),
    ) -> None:
        if capacity <= 0 or not (0 <= founder_count <= capacity):
            raise ValueError("require capacity>0 and 0<=founders<=capacity")
        if corpse_ttl < 0:
            raise ValueError("corpse_ttl must be non-negative")
        hazard_rate = Fraction(hazard_rate)
        if not (0 <= hazard_rate <= 1):
            raise ValueError("hazard_rate must be in [0,1]")
        self.capacity = capacity
        self.memory = MemoryLedger(memory_pool)
        self.hazard_schedule = hazard_schedule or {}
        self.hazard_rate = hazard_rate
        self.hazard_rng = random.Random(hazard_seed)
        self.corpse_ttl = corpse_ttl
        self.tick = 0
        self.members: dict[str, PopulationMember] = {}
        self.all_organisms: dict[str, SliceOrganism] = {}
        self.packets: list[PacketLedger] = []
        self.corpse_expiry: dict[str, int] = {}
        self.terminal_disposed = Fraction(0)
        self.opening_energy = Fraction(founder_s) * founder_count
        self.next_id = founder_count
        self.event_log: list[dict[str, Any]] = []
        self.closure_history: list[dict[str, Any]] = []
        self.packet_buffer = PacketBuffer(
            seed=42,
            phase_mode="monotonic_rich",
            packet_e_rich=Fraction(packet_energy),
            packet_e_lean=Fraction(packet_energy),
            packet_rate=packet_rate,
            buffer_depth=buffer_depth,
            initial_buffer_packets=0,
        )

        for index in range(founder_count):
            organism_id = f"org-{index}"
            organism = SliceOrganism(
                organism_id, self.memory, Fraction(founder_s), Fraction(0))
            self.members[organism_id] = PopulationMember(
                organism=organism, born_tick=-1)
            self.all_organisms[organism_id] = organism
        self.assert_all_ledgers("initial")

    def _new_id(self) -> str:
        organism_id = f"org-{self.next_id}"
        self.next_id += 1
        return organism_id

    def _hazard_remove(self, organism_id: str) -> None:
        member = self.members.pop(organism_id)
        organism = member.organism
        if organism_id in self.memory.gestation:
            self.memory.release_gestation(organism_id)
        self.terminal_disposed += organism.s + organism.r
        organism.s = Fraction(0)
        organism.r = Fraction(0)
        member.state = "DEAD"
        self.memory.move_somatic_to_corpse(organism_id)
        self.corpse_expiry[organism_id] = self.tick + self.corpse_ttl
        self.event_log.append({
            "tick": self.tick,
            "phase": "hazard",
            "event": "hazard_death",
            "organism_id": organism_id,
        })
        self.assert_all_ledgers(f"hazard_death:{organism_id}")

    def _expire_corpses(self) -> None:
        due = sorted(
            organism_id for organism_id, expiry in self.corpse_expiry.items()
            if expiry <= self.tick
        )
        for organism_id in due:
            self.memory.expire_corpse(organism_id)
            del self.corpse_expiry[organism_id]
            self.event_log.append({
                "tick": self.tick,
                "phase": "cleanup",
                "event": "corpse_expired",
                "organism_id": organism_id,
            })
            self.assert_all_ledgers(f"corpse_expiry:{organism_id}")

    def _release_failed_cycle_gestation(self, organism: SliceOrganism,
                                         reason: str) -> None:
        if organism.organism_id in self.memory.gestation:
            self.memory.release_gestation(organism.organism_id)
            organism._record("gestation_released_after_failure", reason=reason)
            self.assert_all_ledgers(
                f"gestation_failure_cleanup:{organism.organism_id}:{reason}")

    def _run_reproductive_cycle(self, member: PopulationMember,
                                vacancies: int) -> tuple[int, str | None, bool]:
        organism = member.organism
        source = self.packet_buffer.read()
        if source is None:
            organism.charge_s(Fraction(10), "READ_EMPTY")
            self.memory.resize_somatic(
                organism.organism_id, PACKET_SIZE, "read_empty_resize")
            organism.ordinary_upkeep("READ_EMPTY")
            self.event_log.append({
                "tick": self.tick,
                "phase": "packet_capture",
                "event": "packet_capture_failed",
                "organism_id": organism.organism_id,
            })
            self.assert_all_ledgers(
                f"packet_capture_failed:{organism.organism_id}")
            return vacancies, None, False
        packet = PacketLedger(
            packet_id=source.packet_id,
            initial_budget=Fraction(source.e_initial),
            max_reducible=source.max_reducible,
        )
        self.packets.append(packet)
        organism.forage_rle(packet, source.data)
        if not organism.allocate_offspring():
            return vacancies, None, False
        if not organism.copy_block(11):
            self._release_failed_cycle_gestation(
                organism, "COPY_BLOCK_R_UNAVAILABLE")
            return vacancies, None, False
        if vacancies <= 0:
            # DIVIDE work is prepaid before the vacancy decision. No child or
            # provisioning is committed; parent-owned gestation is released.
            if not organism._prepay_reproductive(DIVIDE_COST, "DIVIDE"):
                organism.ordinary_upkeep("DIVIDE_FAILED_R")
                self._release_failed_cycle_gestation(
                    organism, "DIVIDE_R_UNAVAILABLE")
                return vacancies, None, False
            self.memory.release_gestation(organism.organism_id)
            organism._record("divide_rejected_no_vacancy")
            organism.ordinary_upkeep("DIVIDE_REJECTED_NO_VACANCY")
            self.event_log.append({
                "tick": self.tick,
                "phase": "admission",
                "event": "birth_rejected_no_vacancy",
                "parent_id": organism.organism_id,
            })
            self.assert_all_ledgers(
                f"birth_rejected_no_vacancy:{organism.organism_id}")
            return vacancies, None, True

        child_id = self._new_id()
        provisioned = organism.divide_and_provision(child_id)
        if provisioned is None:
            self._release_failed_cycle_gestation(
                organism, "DIVIDE_R_UNAVAILABLE")
            return vacancies, None, False
        child = SliceOrganism(
            child_id,
            self.memory,
            provisioned.s,
            provisioned.r,
            a=organism.a,
            t=organism.t,
            d=organism.d,
            initial_memory_already_committed=True,
        )
        self.members[child_id] = PopulationMember(
            organism=child, born_tick=self.tick)
        self.all_organisms[child_id] = child
        self.event_log.append({
            "tick": self.tick,
            "phase": "admission",
            "event": "birth_admitted",
            "parent_id": organism.organism_id,
            "child_id": child_id,
            "provision": provisioned.s,
        })
        self.assert_all_ledgers(f"birth_admitted:{child_id}")
        return vacancies - 1, child_id, False

    def reserve_closure(self) -> dict[str, Any]:
        live = sum(
            (member.organism.s + member.organism.r
             for member in self.members.values()),
            Fraction(0),
        )
        destroyed = self.terminal_disposed + sum(
            (organism.destroyed for organism in self.all_organisms.values()),
            Fraction(0),
        )
        gross = sum(
            (organism.gross_income for organism in self.all_organisms.values()),
            Fraction(0),
        )
        reversed_income = sum(
            (organism.reversed_income for organism in self.all_organisms.values()),
            Fraction(0),
        )
        costs = sum(
            (organism.c_s + organism.c_r
             for organism in self.all_organisms.values()),
            Fraction(0),
        )
        lhs = live + destroyed
        rhs = self.opening_energy + gross - reversed_income - costs
        return {
            "lhs": lhs,
            "rhs": rhs,
            "closed": lhs == rhs,
            "live_reserves": live,
            "destroyed": destroyed,
            "net_income": gross - reversed_income,
            "costs": costs,
        }

    def assert_all_ledgers(self, operation: str) -> dict[str, Any]:
        reserve = self.reserve_closure()
        if not reserve["closed"]:
            raise AssertionError(
                f"population reserve ledger failed after {operation}: {reserve}")
        for packet in self.packets:
            packet.assert_closed()
        for packet in self.packet_buffer.buffer:
            if Fraction(packet.e_budget) != Fraction(packet.e_initial):
                raise AssertionError(
                    f"unread packet budget failed after {operation}: "
                    f"packet={packet.packet_id} remaining={packet.e_budget} "
                    f"initial={packet.e_initial}")
        memory_closed = sum(self.memory.totals().values()) == self.memory.initial_pool
        if not memory_closed:
            raise AssertionError(f"memory ledger failed after {operation}")
        snapshot = {
            "operation": operation,
            "reserve_closed": True,
            "packets_closed": True,
            "memory_closed": True,
            "reserve_lhs": reserve["lhs"],
            "reserve_rhs": reserve["rhs"],
        }
        self.closure_history.append(snapshot)
        return snapshot

    def step(self) -> dict[str, Any]:
        self.packet_buffer.advance_tick()
        hazard_deaths: list[str] = []
        if self.tick in self.hazard_schedule:
            selected_hazards = set(self.hazard_schedule[self.tick])
        else:
            # Dedicated RNG stream: hazard is independent of phenotype,
            # scheduler order, packet generation, and reproductive outcomes.
            selected_hazards = {
                organism_id for organism_id in sorted(self.members)
                if self.hazard_rng.random() < float(self.hazard_rate)
            }
        for organism_id in sorted(selected_hazards):
            if organism_id in self.members:
                self._hazard_remove(organism_id)
                hazard_deaths.append(organism_id)

        vacancies = self.capacity - len(self.members)
        scheduler_snapshot = sorted(self.members)
        newborn_ids: list[str] = []
        rejected = 0
        memory_blocked = 0
        reproductive_failures = 0
        for organism_id in scheduler_snapshot:
            member = self.members.get(organism_id)
            if member is None or member.state != "ACTIVE":
                continue
            member.last_run_tick = self.tick
            if member.organism.s < 10:
                member.state = "STALLED"
                self.event_log.append({
                    "tick": self.tick,
                    "phase": "scheduler",
                    "event": "somatic_stall",
                    "organism_id": organism_id,
                    "reserve": member.organism.s,
                })
                self.assert_all_ledgers(f"somatic_stall:{organism_id}")
                continue
            try:
                vacancies, child_id, was_rejected = self._run_reproductive_cycle(
                    member, vacancies)
            except MemoryError as error:
                try:
                    member.organism.ordinary_upkeep("MEMORY_BLOCKED_ATTEMPT")
                except RuntimeError as upkeep_error:
                    if "S=0 behavior" not in str(upkeep_error):
                        raise
                    member.state = "STALLED"
                    self.event_log.append({
                        "tick": self.tick,
                        "phase": "scheduler",
                        "event": "somatic_stall",
                        "organism_id": organism_id,
                        "reserve": member.organism.s,
                        "reason": "memory_failure_upkeep_unavailable",
                    })
                self._release_failed_cycle_gestation(
                    member.organism, "SHARED_MEMORY_UNAVAILABLE")
                memory_blocked += 1
                self.event_log.append({
                    "tick": self.tick,
                    "phase": "scheduler",
                    "event": "memory_blocked_attempt",
                    "organism_id": organism_id,
                    "reason": str(error),
                })
                self.assert_all_ledgers(f"memory_blocked:{organism_id}")
                continue
            except RuntimeError as error:
                if "R unavailable for gestation upkeep" in str(error):
                    reproductive_failures += 1
                    self._release_failed_cycle_gestation(
                        member.organism, "GESTATION_UPKEEP_R_UNAVAILABLE")
                    self.event_log.append({
                        "tick": self.tick,
                        "phase": "scheduler",
                        "event": "reproductive_failure",
                        "organism_id": organism_id,
                        "reason": "gestation_upkeep_r_unavailable",
                    })
                    self.assert_all_ledgers(
                        f"reproductive_failure:{organism_id}")
                    continue
                if "S=0 behavior" not in str(error):
                    raise
                # Earlier work and memory mutations remain committed. The
                # residual S is retained, but no further instruction can run.
                member.state = "STALLED"
                self.event_log.append({
                    "tick": self.tick,
                    "phase": "scheduler",
                    "event": "somatic_stall",
                    "organism_id": organism_id,
                    "reserve": member.organism.s,
                    "reason": "mid_cycle_somatic_prepayment_failure",
                })
                self.assert_all_ledgers(f"mid_cycle_stall:{organism_id}")
                continue
            rejected += int(was_rejected)
            if child_id is not None:
                newborn_ids.append(child_id)

        self._expire_corpses()
        closure = self.assert_all_ledgers(f"tick_complete:{self.tick}")
        snapshot = {
            "tick": self.tick,
            "hazard_deaths": hazard_deaths,
            "admitted_births": len(newborn_ids),
            "rejected_births": rejected,
            "memory_blocked_attempts": memory_blocked,
            "reproductive_failures": reproductive_failures,
            "newborn_ids": newborn_ids,
            "live_census": len(self.members),
            "stalled_census": sum(
                member.state == "STALLED" for member in self.members.values()),
            "displacements": 0,
            **{key: closure[key] for key in
               ("reserve_closed", "packets_closed", "memory_closed")},
        }
        self.tick += 1
        return snapshot


def run_slice2_trace(ticks: int = 20) -> dict[str, Any]:
    """Run a bounded mechanics trace; this is not a scientific assay."""
    if ticks <= 0:
        raise ValueError("ticks must be positive")
    population = Stage7Population(
        capacity=8,
        founder_count=8,
        founder_s=Fraction(100),
        memory_pool=65536,
        hazard_rate=Fraction(1, 5),
        hazard_seed=73,
        corpse_ttl=2,
    )
    tick_snapshots = [population.step() for _ in range(ticks)]
    counts = Counter(event["event"] for event in population.event_log)
    final_reserve = population.reserve_closure()
    final_packets_closed = all(
        packet.budget_remaining + packet.drawn_s + packet.drawn_r
        == packet.initial_budget
        for packet in population.packets
    ) and all(
        Fraction(packet.e_budget) == Fraction(packet.e_initial)
        for packet in population.packet_buffer.buffer
    )
    final_memory_closed = (
        sum(population.memory.totals().values())
        == population.memory.initial_pool
    )
    trait_values = sorted({
        (organism.a, organism.t, organism.d)
        for organism in population.all_organisms.values()
    })
    return {
        "scope": "mechanics-only; no mutation or scientific assay",
        "assay_run": False,
        "decisions": {
            "somatic_insufficiency":
                "retain_reserve_and_stall_until_hazard",
            "hazard_phase": "phenotype_blind_at_tick_start",
            "admission": "non_displacing_vacancy_reservation",
            "scheduler": "stable_survivor_ids_newborns_next_tick",
            "mutation": "disabled_exact_trait_inheritance",
            "packet_feed": "shared_consumptive_buffer_five_arrivals_per_tick",
        },
        "configuration": {
            "capacity": 8,
            "founders": 8,
            "ticks": ticks,
            "hazard_rate": Fraction(1, 5),
            "hazard_seed": 73,
            "packet_rate": 5,
            "buffer_depth": 8,
            "packet_energy": 300,
            "corpse_ttl": 2,
        },
        "ticks": tick_snapshots,
        "counts": dict(counts),
        "events": population.event_log,
        "closure_history": population.closure_history,
        "final_reserve": final_reserve,
        "final_packets_closed": final_packets_closed,
        "final_memory": population.memory.totals(),
        "final_memory_closed": final_memory_closed,
        "trait_values": [list(values) for values in trait_values],
        "packet_count": len(population.packets),
    }
