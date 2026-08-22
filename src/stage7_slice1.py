"""Stage 7 Slice 1: isolated exact-rational two-account vertical slice.

This module is deliberately not wired into the population Simulation.  It fixes
four provisional semantics needed to execute one causal path while population
hazard, admission, scheduler, S=0, and mutation semantics remain out of scope.

The executable trace covers:
    forage -> extraction -> alpha split -> reproductive work from R
    -> parent-owned gestation -> offspring provisioning
    -> failed overlarge reversal -> successful partial reversal

All energy arithmetic uses fractions.Fraction.  Memory uses disjoint ownership
buckets and asserts closure after every ownership-changing operation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from consts import TRANSFORM_RLE
from datastream import DataStream
from transforms import can_reconstruct, compute_transform


# ---------------------------------------------------------------------------
# Four provisional Slice 1 decisions
# ---------------------------------------------------------------------------

TRAIT_DENOMINATOR = 255
"""Provisional D: an 8-bit numerator lattice with exact 0 and 1 endpoints."""

ALPHA_NUMERATOR = 102  # 102/255 = 2/5
PROVISION_NUMERATOR = 51  # 51/255 = 1/5

INITIAL_SHARED_MEMORY_POOL = 1024
MIN_WORKING_MEMORY = 64
MEMORY_COST_DIVISOR = 640
BASE_UPKEEP = Fraction(1, 10)


@dataclass(frozen=True)
class ReproductiveCost:
    somatic_dispatch: Fraction
    reproductive_work: Fraction


# Strong-split provisional defaults. Size-dependent entries are resolved by
# helper functions below; these preserve the currently registered total costs.
COPY_BLOCK_BASE = ReproductiveCost(Fraction(1), Fraction(1))
DIVIDE_COST = ReproductiveCost(Fraction(1), Fraction(4))


def alloc_offspring_cost(size: int) -> ReproductiveCost:
    if size <= 0:
        size = MIN_WORKING_MEMORY
    chunks = (size + 63) // 64
    return ReproductiveCost(Fraction(1), Fraction(4 + chunks))


def copy_block_cost(length: int) -> ReproductiveCost:
    if length <= 0:
        raise ValueError("COPY_BLOCK length must be positive in Slice 1")
    chunks = (length + 63) // 64
    return ReproductiveCost(
        COPY_BLOCK_BASE.somatic_dispatch,
        COPY_BLOCK_BASE.reproductive_work + chunks,
    )


def transform_cost(extent: int) -> Fraction:
    if extent <= 0:
        raise ValueError("transform extent must be positive")
    return Fraction(3 + (extent + 63) // 64)


@dataclass
class MemoryLedger:
    """Disjoint shared-memory ownership buckets with operation-level closure."""

    initial_pool: int = INITIAL_SHARED_MEMORY_POOL
    free_pool: int = field(init=False)
    somatic_active: dict[str, int] = field(default_factory=dict)
    gestation: dict[str, int] = field(default_factory=dict)
    corpse_reserved: dict[str, int] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.initial_pool <= 0:
            raise ValueError("initial memory pool must be positive")
        self.free_pool = self.initial_pool
        self.assert_closed("initial")

    @staticmethod
    def _bucket_total(bucket: dict[str, int]) -> int:
        return sum(bucket.values())

    def totals(self) -> dict[str, int]:
        return {
            "free_pool": self.free_pool,
            "somatic_active": self._bucket_total(self.somatic_active),
            "gestation": self._bucket_total(self.gestation),
            "corpse_reserved": self._bucket_total(self.corpse_reserved),
        }

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
            },
        })

    def _allocate(self, bucket: dict[str, int], owner: str, size: int,
                  operation: str) -> None:
        if size <= 0:
            raise ValueError("allocation size must be positive")
        if owner in bucket:
            raise ValueError(f"{owner} already owns an allocation in this bucket")
        if self.free_pool < size:
            raise MemoryError(f"insufficient shared memory for {operation}")
        self.free_pool -= size
        bucket[owner] = size
        self.assert_closed(operation)

    def allocate_somatic(self, owner: str, size: int) -> None:
        self._allocate(self.somatic_active, owner, size,
                       f"allocate_somatic:{owner}")

    def resize_somatic(self, owner: str, new_size: int,
                       operation: str) -> None:
        if owner not in self.somatic_active:
            raise ValueError(f"{owner} has no active allocation")
        if new_size <= 0:
            raise ValueError("active allocation size must be positive")
        old_size = self.somatic_active[owner]
        delta = new_size - old_size
        if delta > self.free_pool:
            raise MemoryError(f"insufficient shared memory for {operation}")
        self.free_pool -= delta
        self.somatic_active[owner] = new_size
        self.assert_closed(operation)

    def allocate_gestation(self, owner: str, size: int) -> None:
        self._allocate(self.gestation, owner, size,
                       f"allocate_gestation:{owner}")

    def release_gestation(self, owner: str) -> int:
        if owner not in self.gestation:
            raise ValueError(f"{owner} has no gestation allocation")
        size = self.gestation.pop(owner)
        self.free_pool += size
        self.assert_closed(f"release_gestation:{owner}")
        return size

    def move_somatic_to_corpse(self, owner: str) -> int:
        if owner not in self.somatic_active:
            raise ValueError(f"{owner} has no active allocation")
        if owner in self.corpse_reserved:
            raise ValueError(f"{owner} already has corpse memory")
        size = self.somatic_active.pop(owner)
        self.corpse_reserved[owner] = size
        self.assert_closed(f"move_somatic_to_corpse:{owner}")
        return size

    def expire_corpse(self, owner: str) -> int:
        if owner not in self.corpse_reserved:
            raise ValueError(f"{owner} has no corpse allocation")
        size = self.corpse_reserved.pop(owner)
        self.free_pool += size
        self.assert_closed(f"expire_corpse:{owner}")
        return size


@dataclass
class PacketLedger:
    """Exact packet budget plus current outstanding S/R provenance."""

    packet_id: int
    initial_budget: Fraction
    max_reducible: int = 192
    budget_remaining: Fraction = field(init=False)
    drawn_s: Fraction = Fraction(0)
    drawn_r: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        if self.initial_budget < 0:
            raise ValueError("packet budget must be non-negative")
        if self.max_reducible <= 0:
            raise ValueError("max_reducible must be positive")
        self.budget_remaining = self.initial_budget
        self.assert_closed()

    def assert_closed(self) -> None:
        if min(self.budget_remaining, self.drawn_s, self.drawn_r) < 0:
            raise AssertionError("packet ledger contains a negative account")
        if self.budget_remaining + self.drawn_s + self.drawn_r != self.initial_budget:
            raise AssertionError("packet ledger does not close")


@dataclass
class Child:
    organism_id: str
    s: Fraction
    r: Fraction = Fraction(0)
    a: int = ALPHA_NUMERATOR
    t: int = PROVISION_NUMERATOR
    d: int = TRAIT_DENOMINATOR


@dataclass
class SliceOrganism:
    """Single-organism exact-rational execution state for Slice 1."""

    organism_id: str
    memory: MemoryLedger
    s: Fraction
    r: Fraction
    a: int = ALPHA_NUMERATOR
    t: int = PROVISION_NUMERATOR
    d: int = TRAIT_DENOMINATOR
    c_s: Fraction = Fraction(0)
    c_r: Fraction = Fraction(0)
    gross_income: Fraction = Fraction(0)
    reversed_income: Fraction = Fraction(0)
    committed: Fraction = Fraction(0)
    destroyed: Fraction = Fraction(0)
    child: Child | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    initial_memory_already_committed: bool = False

    def __post_init__(self) -> None:
        if self.d <= 0 or not (0 <= self.a <= self.d) or not (0 <= self.t <= self.d):
            raise ValueError("require D>0 and 0<=A,T<=D")
        if min(self.s, self.r) < 0:
            raise ValueError("reserves must be non-negative")
        if self.initial_memory_already_committed:
            if self.memory.somatic_active.get(self.organism_id) != MIN_WORKING_MEMORY:
                raise ValueError("committed child memory is absent or wrong-sized")
            self.memory.assert_closed(f"adopt_committed_memory:{self.organism_id}")
        else:
            self.memory.allocate_somatic(self.organism_id, MIN_WORKING_MEMORY)

    @property
    def alpha(self) -> Fraction:
        return Fraction(self.a, self.d)

    @property
    def tau_r(self) -> Fraction:
        return Fraction(self.t, self.d)

    def _record(self, event: str, **data: Any) -> None:
        self.events.append({"event": event, "s": self.s, "r": self.r, **data})

    def charge_s(self, amount: Fraction, reason: str) -> None:
        amount = Fraction(amount)
        if amount < 0:
            raise ValueError("cost must be non-negative")
        if self.s < amount:
            raise RuntimeError("S=0 behavior is outside Slice 1")
        self.s -= amount
        self.c_s += amount
        self._record("charge_s", reason=reason, amount=amount)

    def charge_r(self, amount: Fraction, reason: str) -> bool:
        """R=0 default: fail without debt or S subsidy."""
        amount = Fraction(amount)
        if amount < 0:
            raise ValueError("cost must be non-negative")
        if self.r < amount:
            self._record("r_insufficient", reason=reason, required=amount)
            return False
        self.r -= amount
        self.c_r += amount
        self._record("charge_r", reason=reason, amount=amount)
        return True

    def ordinary_upkeep(self, reason: str) -> None:
        somatic_bytes = self.memory.somatic_active[self.organism_id]
        self.charge_s(
            BASE_UPKEEP + Fraction(somatic_bytes, MEMORY_COST_DIVISOR),
            f"ordinary_upkeep:{reason}",
        )
        gestation_bytes = self.memory.gestation.get(self.organism_id, 0)
        if gestation_bytes:
            amount = Fraction(gestation_bytes, MEMORY_COST_DIVISOR)
            if not self.charge_r(amount, f"gestation_upkeep:{reason}"):
                # Provisional R=0 gestation behavior: dissipate residual R,
                # release parent-owned gestation, and clear the bout.
                self.destroyed += self.r
                self.r = Fraction(0)
                self.memory.release_gestation(self.organism_id)
                raise RuntimeError("R unavailable for gestation upkeep")

    def forage_rle(self, packet: PacketLedger, data: bytes) -> bytes:
        """Run the real reversible RLE geometry and split its exact draw."""
        self.charge_s(Fraction(10), "READ")
        self.memory.resize_somatic(
            self.organism_id, len(data), "read_packet_working_memory")
        self.ordinary_upkeep("READ")

        transformed = compute_transform(TRANSFORM_RLE, data)
        if not can_reconstruct(TRANSFORM_RLE, data, transformed):
            raise AssertionError("Slice 1 RLE compression must reconstruct")
        reduction = len(data) - len(transformed)
        if reduction <= 0:
            raise AssertionError("Slice 1 forage input did not compress")
        self.charge_s(transform_cost(len(data)), "TRANSFORM_COMPRESS_256")
        self.memory.resize_somatic(
            self.organism_id, len(transformed), "rle_compression_reclaim")
        self.ordinary_upkeep("TRANSFORM_COMPRESS_256")
        quantity = packet.initial_budget * Fraction(
            reduction, packet.max_reducible)
        if quantity <= 0 or quantity > packet.budget_remaining:
            raise ValueError("invalid positive packet draw")
        delta_r = self.alpha * quantity
        delta_s = quantity - delta_r
        packet.budget_remaining -= quantity
        packet.drawn_s += delta_s
        packet.drawn_r += delta_r
        self.s += delta_s
        self.r += delta_r
        self.gross_income += quantity
        packet.assert_closed()
        self._record(
            "draw", packet_id=packet.packet_id, quantity=quantity,
            delta_s=delta_s, delta_r=delta_r,
            input_bytes=len(data), output_bytes=len(transformed),
            transform="RLE",
        )
        return transformed

    def _prepay_reproductive(self, cost: ReproductiveCost, reason: str) -> bool:
        self.charge_s(cost.somatic_dispatch, f"{reason}:dispatch")
        if not self.charge_r(cost.reproductive_work, f"{reason}:work"):
            return False
        return True

    def allocate_offspring(self, size: int = MIN_WORKING_MEMORY) -> bool:
        cost = alloc_offspring_cost(size)
        if not self._prepay_reproductive(cost, "ALLOC_OFFSPRING"):
            self.ordinary_upkeep("ALLOC_OFFSPRING_FAILED_R")
            return False
        self.memory.allocate_gestation(self.organism_id, size)
        self._record("gestation_allocated", bytes=size, owner=self.organism_id)
        self.ordinary_upkeep("ALLOC_OFFSPRING")
        return True

    def copy_block(self, genome_instructions: int) -> bool:
        if self.organism_id not in self.memory.gestation:
            raise RuntimeError("COPY_BLOCK requires parent-owned gestation")
        cost = copy_block_cost(genome_instructions)
        if not self._prepay_reproductive(cost, "COPY_BLOCK"):
            self.ordinary_upkeep("COPY_BLOCK_FAILED_R")
            return False
        self._record("copy_complete", instructions=genome_instructions)
        self.ordinary_upkeep("COPY_BLOCK")
        return True

    def divide_and_provision(self, child_id: str = "child") -> Child | None:
        if self.organism_id not in self.memory.gestation:
            raise RuntimeError("DIVIDE requires parent-owned gestation")
        if not self._prepay_reproductive(DIVIDE_COST, "DIVIDE"):
            self.ordinary_upkeep("DIVIDE_FAILED_R")
            return None

        # Atomic child-memory feasibility decided BEFORE surrendering the
        # parent-owned gestation block (architecture spec §7 steps 4-5,
        # strengthened ordering). The gestation bytes count toward
        # availability because releasing them into the pool is the next
        # unconditional act, so the boundary is exact and no feasible birth
        # is rejected. On failure the bout stays intact for the caller's
        # single-owner release; prepaid work stays sunk; nothing commits.
        gestation_bytes = self.memory.gestation[self.organism_id]
        if self.memory.free_pool + gestation_bytes < MIN_WORKING_MEMORY:
            self._record(
                "child_memory_unavailable",
                required=MIN_WORKING_MEMORY,
                available=self.memory.free_pool + gestation_bytes,
            )
            self.ordinary_upkeep("DIVIDE_CHILD_MEMORY_UNAVAILABLE")
            return None

        # Guaranteed isolated admission. Parent gestation is released exactly
        # once before child memory is independently committed.
        self.memory.release_gestation(self.organism_id)
        self.memory.allocate_somatic(child_id, MIN_WORKING_MEMORY)

        provision = self.tau_r * self.r
        self.r -= provision
        self.committed += provision
        self.child = Child(
            child_id, s=provision, a=self.a, t=self.t, d=self.d,
        )
        self._record("provision_committed", child_id=child_id, provision=provision)
        self.ordinary_upkeep("DIVIDE")
        return self.child

    def reverse_rle(self, packet: PacketLedger, compressed: bytes,
                    extent: int) -> bool:
        """Derive a return from real RLE expansion, then reverse atomically."""
        if extent <= 0 or extent > len(compressed):
            raise ValueError("invalid expansion extent")
        self.charge_s(transform_cost(extent), f"TRANSFORM_EXPAND_{extent}")
        self.ordinary_upkeep(f"TRANSFORM_EXPAND_{extent}")
        original = compressed[:extent]
        transformed = compute_transform(TRANSFORM_RLE, original)
        if not can_reconstruct(TRANSFORM_RLE, original, transformed):
            raise AssertionError("Slice 1 RLE expansion must reconstruct")
        expansion = len(transformed) - len(original)
        if expansion <= 0:
            raise AssertionError("Slice 1 reversal input did not expand")
        quantity = packet.initial_budget * Fraction(
            expansion, packet.max_reducible)
        outstanding = packet.drawn_s + packet.drawn_r
        if quantity <= 0 or quantity > outstanding:
            raise ValueError("invalid reversal quantity")
        # The packet's original-account provenance is authoritative. Never
        # recompute reversal allocation from the organism's current trait.
        debit_s = quantity * packet.drawn_s / outstanding
        debit_r = quantity * packet.drawn_r / outstanding

        # Atomic precheck: no packet/provenance/reserve state changes on failure.
        if self.s < debit_s or self.r < debit_r:
            self._record(
                "reversal_failed", packet_id=packet.packet_id,
                quantity=quantity, debit_s=debit_s, debit_r=debit_r,
                input_bytes=len(original), output_bytes=len(transformed),
                transform="RLE", reason="REVERSAL_ACCOUNT_UNAVAILABLE",
            )
            packet.assert_closed()
            return False

        self.s -= debit_s
        self.r -= debit_r
        packet.drawn_s -= debit_s
        packet.drawn_r -= debit_r
        packet.budget_remaining += quantity
        self.reversed_income += quantity
        packet.assert_closed()
        self._record(
            "partial_reversal", packet_id=packet.packet_id,
            quantity=quantity, debit_s=debit_s, debit_r=debit_r,
            input_bytes=len(original), output_bytes=len(transformed),
            transform="RLE",
        )
        return True

    def reserve_closure(self, opening_s: Fraction, opening_r: Fraction) -> dict[str, Any]:
        net_income = self.gross_income - self.reversed_income
        lhs = self.s + self.r + self.committed + self.destroyed
        rhs = Fraction(opening_s) + Fraction(opening_r) + net_income - self.c_s - self.c_r
        return {"lhs": lhs, "rhs": rhs, "closed": lhs == rhs,
                "net_income": net_income}


def run_slice1_trace() -> dict[str, Any]:
    """Run the required isolated full-cycle trace and assert all three ledgers."""
    opening_s = Fraction(100)
    opening_r = Fraction(0)
    memory = MemoryLedger()
    organism = SliceOrganism("parent", memory, opening_s, opening_r)
    source = DataStream(seed=42, phase_mode="monotonic_rich").generate_packet(0)
    packet = PacketLedger(
        packet_id=source.packet_id,
        initial_budget=Fraction(300),
        max_reducible=source.max_reducible,
    )

    compressed = organism.forage_rle(packet, source.data)
    assert organism.allocate_offspring(MIN_WORKING_MEMORY)
    assert organism.copy_block(genome_instructions=11)
    child = organism.divide_and_provision("child")
    assert child is not None

    # Provisioning must precede reversal. Real RLE expansion of the first 80
    # compressed bytes requests 125 energy and needs more R than remains; it
    # must fail atomically. Expansion of 20 bytes requests 125/4 and succeeds.
    before_failed = (
        organism.s, organism.r, packet.budget_remaining,
        packet.drawn_s, packet.drawn_r,
    )
    assert not organism.reverse_rle(packet, compressed, extent=80)
    after_failed = (
        organism.s, organism.r, packet.budget_remaining,
        packet.drawn_s, packet.drawn_r,
    )
    # Ordinary S instruction/upkeep costs are intentionally sunk on failure;
    # R and every packet field must remain unchanged.
    assert after_failed[1:] == before_failed[1:]
    assert organism.reverse_rle(packet, compressed, extent=20)

    reserve = organism.reserve_closure(opening_s, opening_r)
    packet.assert_closed()
    memory.assert_closed("cycle_complete")

    assert reserve["closed"]
    assert packet.budget_remaining + packet.drawn_s + packet.drawn_r == packet.initial_budget
    assert sum(memory.totals().values()) == memory.initial_pool
    assert next(i for i, e in enumerate(organism.events)
                if e["event"] == "provision_committed") < next(
                    i for i, e in enumerate(organism.events)
                    if e["event"] == "partial_reversal")

    return {
        "defaults": {
            "D": organism.d,
            "A": organism.a,
            "T": organism.t,
            "alpha": organism.alpha,
            "tau_r": organism.tau_r,
            "r_zero_behavior": "fail reproductive effect after S dispatch; no debt or S subsidy",
            "gestation_owner": "parent until release before child memory commit",
        },
        "reserve": reserve,
        "packet": {
            "initial_budget": packet.initial_budget,
            "budget_remaining": packet.budget_remaining,
            "drawn_s": packet.drawn_s,
            "drawn_r": packet.drawn_r,
            "closed": (
                packet.budget_remaining + packet.drawn_s + packet.drawn_r
                == packet.initial_budget
            ),
        },
        "memory": {**memory.totals(), "initial_pool": memory.initial_pool,
                   "closed": sum(memory.totals().values()) == memory.initial_pool,
                   "checkpoints": len(memory.history)},
        "parent": {"s": organism.s, "r": organism.r},
        "child": {"s": child.s, "r": child.r},
        "costs": {"c_s": organism.c_s, "c_r": organism.c_r},
        "events": organism.events,
        "memory_history": memory.history,
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    import json

    print(json.dumps(_jsonable(run_slice1_trace()), indent=2, sort_keys=True))
