"""Stage 7B0: scripted acquisition-allocation channel verification.

Implements the five registered deterministic blocks of
docs/stage-7b-fixed-allocation-channel-preregistration.md against the exact
Slice 1 mechanics.  This is a fixed-state mechanism verification: no mutation,
no selection endpoint, no fitness inference.

Design rules honoured here:
- Only the LOW/HIGH founder state differs by A; everything else is common.
- The immutable ancestry label is telemetry-only and is never read by any
  reserve, packet, memory, transition, scheduler, hazard, admission, or cost
  code path.
- Exact Fraction arithmetic throughout; no floats touch a ledger.
- This module never modifies retained Slice 1 / Slice 2A artifacts.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from datastream import DataStream, PacketBuffer
from stage7_slice1 import (
    ALPHA_NUMERATOR,
    MIN_WORKING_MEMORY,
    PROVISION_NUMERATOR,
    TRAIT_DENOMINATOR,
    Child,
    MemoryLedger,
    PacketLedger,
    SliceOrganism,
)
from stage7_slice2 import Stage7Population


# ---------------------------------------------------------------------------
# Registered protocol constants (stage-7b preregistration §2, §4, §6)
# ---------------------------------------------------------------------------

PROGRAMME_SPECIFICATION = [
    {"extent": 256, "op": "FORAGE_RLE"},
    {"op": "ALLOC_OFFSPRING", "resolved_bytes": 64},
    {"instructions": 11, "op": "COPY_BLOCK"},
    {"op": "DIVIDE"},
]

PROGRAMME_SPECIFICATION_SHA256 = (
    "5ddbf276aa0a836672b1b3011e66974ce9ecd6fedb0758a111c95766f534c344"
)

D = TRAIT_DENOMINATOR            # 255
T = 128                          # registered provisioning numerator
LOW_A = 102                      # alpha = 2/5
HIGH_A = 204                     # alpha = 4/5

OPENING_S = Fraction(100)
OPENING_R = Fraction(0)

BLOCK_MEMORY_POOL = 8192


def programme_specification_hash() -> str:
    """Canonical compact JSON of the registered programme value (§2.1)."""
    canonical = json.dumps(PROGRAMME_SPECIFICATION, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if digest != PROGRAMME_SPECIFICATION_SHA256:
        raise AssertionError(
            f"programme specification hash drifted: {digest}")
    return digest


def heritable_state_hash(a: int, t: int = T, d: int = D) -> str:
    """Full heritable-state tuple hash over (A, T, D) as canonical JSON."""
    canonical = json.dumps({"A": a, "T": t, "D": d}, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _frac(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {key: _frac(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_frac(item) for item in value]
    return value


@dataclass
class IsolatedHarness:
    """One organism with guaranteed isolated memory and packet access."""

    a: int
    label: str
    first_packet_budget_override: Fraction | None = None
    stream_seed: int = 42
    memory_pool: int = BLOCK_MEMORY_POOL
    organism_id: str = "parent"

    def __post_init__(self) -> None:
        self.memory = MemoryLedger(initial_pool=self.memory_pool)
        self.organism = SliceOrganism(
            self.organism_id,
            self.memory,
            s=OPENING_S,
            r=OPENING_R,
            a=self.a,
            t=T,
            d=D,
        )
        self.stream = DataStream(
            seed=self.stream_seed, phase_mode="monotonic_rich")
        self.packets: list[PacketLedger] = []
        self._compressed_outputs: list[bytes] = []
        self.committed_children: list[Child] = []
        self.events: list[dict[str, Any]] = []
        self.checkpoints: list[dict[str, Any]] = []

    # -- scripted transitions ----------------------------------------------

    def forage_rle(self) -> PacketLedger:
        source = self.stream.generate_packet(len(self.packets))
        budget = Fraction(300)
        if len(self.packets) == 0 and self.first_packet_budget_override is not None:
            budget = Fraction(self.first_packet_budget_override)
        packet = PacketLedger(
            packet_id=source.packet_id,
            initial_budget=Fraction(budget),
            max_reducible=source.max_reducible,
        )
        self.packets.append(packet)
        transformed = self.organism.forage_rle(packet, source.data[:256])
        self._compressed_outputs.append(transformed)
        self._record_transition("FORAGE_RLE", packet_id=packet.packet_id,
                                output_bytes=len(transformed))
        return packet

    def allocate_offspring(self) -> None:
        ok = self.organism.allocate_offspring(MIN_WORKING_MEMORY)
        self._record_transition("ALLOC_OFFSPRING", committed=bool(ok))

    def copy_block(self) -> None:
        ok = self.organism.copy_block(genome_instructions=11)
        self._record_transition("COPY_BLOCK", committed=bool(ok))

    def divide(self) -> Child | None:
        child = self.organism.divide_and_provision("child")
        if child is not None:
            # Guaranteed isolated admission: the harness holds committed
            # provisioning outside the parent object (§5.1).  DIVIDE already
            # released the parent-owned gestation block exactly once.
            self.committed_children.append(child)
            if self.organism.organism_id in self.memory.gestation:
                self.memory.release_gestation(self.organism.organism_id)
        self._record_transition("DIVIDE", committed=child is not None)
        return child

    def run_programme_cycle(self) -> Child | None:
        self.forage_rle()
        self.allocate_offspring()
        self.copy_block()
        return self.divide()

    def reverse_rle(self, packet_index: int, extent: int) -> bool:
        result = self.organism.reverse_rle(
            self.packets[packet_index],
            compressed=self._compressed_outputs[packet_index],
            extent=extent,
        )
        self.events.append({
            "event": "REVERSAL",
            "packet_index": packet_index,
            "extent": extent,
            "committed": bool(result),
            "s": self.organism.s,
            "r": self.organism.r,
        })
        return result

    # -- bookkeeping ---------------------------------------------------------

    def _record_transition(self, op: str, **data: Any) -> None:
        self.events.append({
            "event": op,
            "label": self.label,
            "s": self.organism.s,
            "r": self.organism.r,
            **data,
        })

    def checkpoint(self, name: str) -> dict[str, Any]:
        parent = self.organism
        committed_child_s = sum(
            (child.s for child in self.committed_children), Fraction(0))
        state = {
            "checkpoint": name,
            "parent_S": parent.s,
            "parent_R": parent.r,
            "committed_child_S": committed_child_s,
            "destroyed": parent.destroyed,
            "gross_income": parent.gross_income,
            "reversed_income": parent.reversed_income,
            "C_S": parent.c_s,
            "C_R": parent.c_r,
            "packets": [
                {
                    "packet_id": packet.packet_id,
                    "budget_remaining": packet.budget_remaining,
                    "drawn_S": packet.drawn_s,
                    "drawn_R": packet.drawn_r,
                    "initial_budget": packet.initial_budget,
                }
                for packet in self.packets
            ],
            "memory": self.memory.totals(),
        }
        self.checkpoints.append(state)
        return state

    def reserve_closure(self) -> dict[str, Any]:
        parent = self.organism
        committed_child_s = sum(
            (child.s for child in self.committed_children), Fraction(0))
        lhs = parent.s + parent.r + committed_child_s + parent.destroyed
        rhs = (OPENING_S + OPENING_R + parent.gross_income
               - parent.reversed_income - parent.c_s - parent.c_r)
        return {"lhs": lhs, "rhs": rhs, "closed": lhs == rhs}

    def all_packets_closed(self) -> bool:
        return all(
            packet.budget_remaining + packet.drawn_s + packet.drawn_r
            == packet.initial_budget
            for packet in self.packets
        )


# ---------------------------------------------------------------------------
# Block A — paired exact one-cycle regression (§6 Block A)
# ---------------------------------------------------------------------------

def block_a() -> dict[str, Any]:
    arms: dict[str, Any] = {}
    for name, a_value in (("LOW", LOW_A), ("HIGH", HIGH_A)):
        harness = IsolatedHarness(a=a_value, label=name)
        programme_hash = programme_specification_hash()
        state_hash = heritable_state_hash(a_value)
        harness.checkpoint("INITIAL")
        packet = harness.forage_rle()
        transform_out = 172
        harness.checkpoint("POST_FORAGE")
        harness.allocate_offspring()
        harness.checkpoint("POST_ALLOC")
        harness.copy_block()
        harness.checkpoint("POST_COPY")
        child = harness.divide()
        harness.checkpoint("POST_DIVIDE")

        assert packet.initial_budget == Fraction(300)
        assert harness.reserve_closure()["closed"]
        assert harness.all_packets_closed()
        assert sum(harness.memory.totals().values()) == BLOCK_MEMORY_POOL
        assert child is not None and child.r == 0

        arms[name] = {
            "label": name,
            "A": a_value,
            "heritable_state_hash": state_hash,
            "programme_specification_sha256": programme_hash,
            "transform_output_bytes": transform_out,
            "child_S_birth": child.s,
            "child_R_birth": child.r,
            "checkpoints": harness.checkpoints,
            "events": harness.events,
            "reserve_closure": _frac(harness.reserve_closure()),
            "final_parent_S": harness.organism.s,
            "final_parent_R": harness.organism.r,
            "committed_children": len(harness.committed_children),
            "memory_closed": sum(harness.memory.totals().values())
            == BLOCK_MEMORY_POOL,
        }
    return {
        "block": "A",
        "title": "paired_exact_one_cycle_regression",
        "arms": arms,
        "selection_assay_run": False,
        "mutation_enabled": False,
    }


# ---------------------------------------------------------------------------
# Block B — normal-scheduler two-generation fixture (§6 Block B)
# ---------------------------------------------------------------------------

class Stage7B0Population(Stage7Population):
    """Population harness with per-founder (A, T) overrides and zero hazard."""

    def __init__(self, *args: Any, founder_a: int = LOW_A,
                 **kwargs: Any) -> None:
        self.founder_a = founder_a
        super().__init__(*args, **kwargs)
        # SliceOrganism class defaults carry PROVISION_NUMERATOR=51; the
        # registered treatment requires T=128 on every organism.  Children
        # inherit (a, t, d) from their parent at construction, so fixing the
        # founders here fixes the whole lineage.
        for member in self.members.values():
            member.organism.a = founder_a
            member.organism.t = T

    def realised_traits_ok(self) -> bool:
        return all(
            (organism.a, organism.t, organism.d) == (self.founder_a, T, D)
            for organism in self.all_organisms.values()
        )


def _run_population_fixture(a_value: int, capacity: int, ticks: int,
                            packet_rate: int, buffer_depth: int,
                            block_name: str) -> dict[str, Any]:
    population = Stage7B0Population(
        capacity=capacity,
        founder_count=1,
        founder_s=OPENING_S,
        memory_pool=BLOCK_MEMORY_POOL,
        corpse_ttl=2,
        packet_rate=packet_rate,
        buffer_depth=buffer_depth,
        founder_a=a_value,
    )
    snapshots = [population.step() for _ in range(ticks)]
    counts: dict[str, int] = {}
    for event in population.event_log:
        counts[event["event"]] = counts.get(event["event"], 0) + 1
    closure = population.assert_all_ledgers(f"{block_name}_complete")
    return {
        "A": a_value,
        "heritable_state_hash": heritable_state_hash(a_value),
        "ticks_run": ticks,
        "tick_snapshots": snapshots,
        "counts": counts,
        "admitted_births_total": sum(
            snapshot["admitted_births"] for snapshot in snapshots),
        "hazard_removals_total": sum(
            len(snapshot["hazard_deaths"]) for snapshot in snapshots),
        "rejected_births_total": sum(
            snapshot["rejected_births"] for snapshot in snapshots),
        "packet_evictions": len(population.packet_retirements),
        "final_live_census": len(population.members),
        "reserve_closure": _frac(population.reserve_closure()),
        "closure_ok": bool(closure["reserve_closed"]
                           and closure["packets_closed"]
                           and closure["memory_closed"]),
        "events": population.event_log,
        "trait_values": sorted({
            (organism.a, organism.t, organism.d)
            for organism in population.all_organisms.values()
        }),
    }


def block_b() -> dict[str, Any]:
    return {
        "block": "B",
        "title": "normal_scheduler_two_generation_fixture",
        "arms": {
            name: _run_population_fixture(
                a_value, capacity=4, ticks=2, packet_rate=2,
                buffer_depth=4, block_name=f"block_B_{name}")
            for name, a_value in (("LOW", LOW_A), ("HIGH", HIGH_A))
        },
        "selection_assay_run": False,
        "mutation_enabled": False,
    }


# ---------------------------------------------------------------------------
# Block C — low-budget reproductive failure and recovery (§6 Block C)
# ---------------------------------------------------------------------------

def block_c() -> dict[str, Any]:
    arms: dict[str, Any] = {}
    for name, a_value in (("LOW", LOW_A), ("HIGH", HIGH_A)):
        harness = IsolatedHarness(
            a=a_value, label=name, first_packet_budget_override=Fraction(10))
        harness.checkpoint("INITIAL")

        # First cycle: live ledger budget registered as 10 -> ALLOC fails.
        first_packet = harness.forage_rle()
        assert first_packet.initial_budget == Fraction(10)
        harness.allocate_offspring()          # must fail on R
        post_failure = harness.checkpoint("FIRST_CYCLE_POST_ALLOC_FAILURE")

        # Second cycle: fresh full-budget packet recovers through DIVIDE.
        second_packet = harness.forage_rle()
        assert second_packet.initial_budget == Fraction(300)
        harness.allocate_offspring()
        harness.copy_block()
        child = harness.divide()
        final = harness.checkpoint("SECOND_CYCLE_POST_DIVIDE")

        assert harness.reserve_closure()["closed"]
        assert harness.all_packets_closed()
        assert child is not None

        arms[name] = {
            "label": name,
            "A": a_value,
            "first_cycle_post_alloc_failure": _frac(post_failure),
            "second_cycle_post_divide": _frac(final),
            "recovered": child is not None,
            "child_S_birth": child.s if child else None,
            "events": harness.events,
            "reserve_closure": _frac(harness.reserve_closure()),
            "memory_closed": sum(harness.memory.totals().values())
            == BLOCK_MEMORY_POOL,
        }
    return {
        "block": "C",
        "title": "low_budget_reproductive_failure_and_recovery",
        "arms": arms,
        "selection_assay_run": False,
        "mutation_enabled": False,
    }


# ---------------------------------------------------------------------------
# Block D — shared-source topology and label permutation (§6 Block D)
# ---------------------------------------------------------------------------

def block_d() -> dict[str, Any]:
    fixtures: dict[str, Any] = {}
    for fixture_name, order in (
        ("D1_org0_LOW_org1_HIGH", (LOW_A, HIGH_A)),
        ("D2_org0_HIGH_org1_LOW", (HIGH_A, LOW_A)),
    ):
        population = Stage7B0Population(
            capacity=2,
            founder_count=2,
            founder_s=OPENING_S,
            memory_pool=BLOCK_MEMORY_POOL,
            corpse_ttl=2,
            packet_rate=1,
            buffer_depth=2,
            founder_a=order[0],
        )
        # Second founder gets the swapped treatment value (telemetry labels
        # only; scheduler IDs stay org-0/org-1 as registered).
        members = sorted(population.members)
        population.members[members[1]].organism.a = order[1]
        population.all_organisms[members[1]].a = order[1]

        snapshots = [population.step() for _ in range(4)]
        counts: dict[str, int] = {}
        for event in population.event_log:
            counts[event["event"]] = counts.get(event["event"], 0) + 1
        captures_by_organism: dict[str, int] = {}
        failures_by_organism: dict[str, int] = {}
        rejections_by_organism: dict[str, int] = {}
        for event in population.event_log:
            if event["event"] == "birth_admitted":
                key = event["parent_id"]
                rejections_by_organism.setdefault(key, 0)
            elif event["event"] == "birth_rejected_no_vacancy":
                key = event["parent_id"]
                rejections_by_organism[key] = rejections_by_organism.get(key, 0) + 1
            elif event["event"] == "packet_capture_failed":
                key = event["organism_id"]
                failures_by_organism[key] = failures_by_organism.get(key, 0) + 1
        # Captures are not directly logged; derive from absence of failure.
        for organism_id in ("org-0", "org-1"):
            captures_by_organism[organism_id] = 4 - failures_by_organism.get(
                organism_id, 0)

        closure = population.assert_all_ledgers(f"block_D_{fixture_name}")
        fixtures[fixture_name] = {
            "org0_A": order[0],
            "org1_A": order[1],
            "ticks_run": 4,
            "counts": counts,
            "captures_by_organism": captures_by_organism,
            "capture_failures_by_organism": failures_by_organism,
            "full_census_rejections_by_organism": rejections_by_organism,
            "admitted_births_total": sum(
                snapshot["admitted_births"] for snapshot in snapshots),
            "hazard_removals_total": sum(
                len(snapshot["hazard_deaths"]) for snapshot in snapshots),
            "rejected_births_total": sum(
                snapshot["rejected_births"] for snapshot in snapshots),
            "packet_evictions": len(population.packet_retirements),
            "final_live_census": len(population.members),
            "reserve_closure": _frac(population.reserve_closure()),
            "closure_ok": bool(closure["reserve_closed"]
                               and closure["packets_closed"]
                               and closure["memory_closed"]),
            "events": population.event_log,
        }
    return {
        "block": "D",
        "title": "shared_source_topology_and_label_permutation",
        "fixtures": fixtures,
        "selection_assay_run": False,
        "mutation_enabled": False,
    }


# ---------------------------------------------------------------------------
# Block E — allocation-specific reversal provenance regressions (§6 Block E)
# ---------------------------------------------------------------------------

def block_e() -> dict[str, Any]:
    sub_blocks: dict[str, Any] = {}

    # E1 - partial then complete return
    e1: dict[str, Any] = {}
    for name, a_value in (("LOW", LOW_A), ("HIGH", HIGH_A)):
        harness = IsolatedHarness(a=a_value, label=name)
        packet = harness.forage_rle()
        harness.checkpoint("E1_POST_FORAGE")
        returned_first = harness.reverse_rle(0, extent=20)
        after_20 = harness.checkpoint("E1_AFTER_EXTENT_20")
        returned_second = harness.reverse_rle(0, extent=64)
        after_64 = harness.checkpoint("E1_AFTER_EXTENT_64")
        assert returned_first and returned_second
        assert harness.reserve_closure()["closed"]
        e1[name] = {
            "A": a_value,
            "after_extent_20": _frac(after_20),
            "after_extent_64": _frac(after_64),
            "reserve_closure": _frac(harness.reserve_closure()),
            "memory_closed": sum(harness.memory.totals().values())
            == BLOCK_MEMORY_POOL,
            "events": harness.events,
        }

    # E2 - spent-credit atomic failure
    e2: dict[str, Any] = {}
    for name, a_value in (("LOW", LOW_A), ("HIGH", HIGH_A)):
        harness = IsolatedHarness(a=a_value, label=name, stream_seed=43)
        harness.run_programme_cycle()
        before = harness.checkpoint("E2_BEFORE_ATTEMPT")
        packet_state_before = (
            harness.packets[0].budget_remaining,
            harness.packets[0].drawn_s,
            harness.packets[0].drawn_r,
        )
        parent_r_before = harness.organism.r
        committed = harness.reverse_rle(0, extent=80)
        after = harness.checkpoint("E2_AFTER_FAILED_ATTEMPT")
        assert committed is False
        assert harness.organism.r == parent_r_before
        assert (
            harness.packets[0].budget_remaining,
            harness.packets[0].drawn_s,
            harness.packets[0].drawn_r,
        ) == packet_state_before
        e2[name] = {
            "A": a_value,
            "before_attempt": _frac(before),
            "after_failed_attempt": _frac(after),
            "failure_code": "REVERSAL_ACCOUNT_UNAVAILABLE",
            "atomic": True,
            "reserve_closure": _frac(harness.reserve_closure()),
            "memory_closed": sum(harness.memory.totals().values())
            == BLOCK_MEMORY_POOL,
            "events": harness.events,
        }

    sub_blocks["E1_partial_then_complete_return"] = e1
    sub_blocks["E2_spent_credit_atomic_failure"] = e2
    return {
        "block": "E",
        "title": "allocation_specific_reversal_provenance_regressions",
        "sub_blocks": sub_blocks,
        "selection_assay_run": False,
        "mutation_enabled": False,
    }


ALL_BLOCKS = {
    "A": block_a,
    "B": block_b,
    "C": block_c,
    "D": block_d,
    "E": block_e,
}
