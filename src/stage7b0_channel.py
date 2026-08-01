"""Deterministic Stage 7B0 scripted acquisition-allocation verification.

Importing this module has no simulation side effects. Fixed inputs and disabled
mutation make execution exactly reproducible. This is mechanism verification,
not a selection, mutation, invasion, or evolutionary assay.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from datastream import DataStream
from stage7_slice1 import MemoryLedger, PacketLedger, SliceOrganism
from stage7_slice2 import Stage7Population


ROOT = Path(__file__).resolve().parent.parent
PROTOCOL_RELATIVE_PATH = "docs/stage-7b-fixed-allocation-channel-preregistration.md"
PROTOCOL_SHA256 = "8ecabac15a8487724b09ab6dca1340e55e63de39c9717c580cd18dd52947c113"
PROGRAM_SPEC_CANONICAL = (
    '[{"extent":256,"op":"FORAGE_RLE"},'
    '{"op":"ALLOC_OFFSPRING","resolved_bytes":64},'
    '{"instructions":11,"op":"COPY_BLOCK"},{"op":"DIVIDE"}]'
)
PROGRAM_SPEC_SHA256 = hashlib.sha256(PROGRAM_SPEC_CANONICAL.encode()).hexdigest()

BLOCK_IDS = ("A", "B", "C", "D1", "D2", "E1", "E2")
GATE_IDS = (
    "realised_treatment",
    "programme_identity",
    "allocation_identity",
    "direct_debit_isolation",
    "reversal_provenance",
    "recovery",
    "lifecycle",
    "topology",
    "closure",
    "no_hidden_gate",
)
CHECKPOINT_REQUIREMENTS = {
    "A": ("INITIAL", "POST_FORAGE", "POST_ALLOC", "POST_COPY", "POST_DIVIDE", "FINAL"),
    "B": ("INITIAL", "POST_PACKET_ARRIVAL", "POST_MEMBER", "POST_ADMISSION", "TICK_COMPLETE"),
    "C": ("INITIAL", "POST_FORAGE", "POST_ALLOC", "POST_COPY", "POST_DIVIDE", "FINAL"),
    "D1": ("INITIAL", "POST_PACKET_ARRIVAL", "POST_MEMBER", "POST_REJECTION", "TICK_COMPLETE"),
    "D2": ("INITIAL", "POST_PACKET_ARRIVAL", "POST_MEMBER", "POST_REJECTION", "TICK_COMPLETE"),
    "E1": ("INITIAL", "POST_FORAGE", "POST_REVERSAL", "FINAL"),
    "E2": ("INITIAL", "POST_FORAGE", "POST_ALLOC", "POST_COPY", "POST_DIVIDE", "POST_REVERSAL", "FINAL"),
}
BLOCK_CHECK_KEYS = {
    "A": ("realised_treatment", "programme_identity", "allocation_identity", "direct_debit_isolation", "all_checkpoints_closed", "no_hidden_gate"),
    "B": ("realised_treatment", "programme_identity", "allocation_identity", "direct_debit_isolation", "two_generation_sequence", "all_checkpoints_closed", "no_hidden_gate"),
    "C": ("realised_treatment", "programme_identity", "allocation_identity", "direct_debit_isolation", "registered_recovery", "all_checkpoints_closed", "no_hidden_gate"),
    "D1": ("realised_treatment", "programme_identity", "allocation_identity", "direct_debit_isolation", "shared_source_topology", "all_checkpoints_closed", "no_hidden_gate"),
    "D2": ("realised_treatment", "programme_identity", "allocation_identity", "direct_debit_isolation", "shared_source_topology", "all_checkpoints_closed", "no_hidden_gate"),
    "E1": ("realised_treatment", "programme_identity", "allocation_identity", "partial_and_complete_reversal", "all_checkpoints_closed", "no_hidden_gate"),
    "E2": ("realised_treatment", "programme_identity", "allocation_identity", "direct_debit_isolation", "spent_credit_atomic_failure", "all_checkpoints_closed", "no_hidden_gate"),
}
REQUIRED_FREEZE_FILES = (
    PROTOCOL_RELATIVE_PATH,
    "src/stage7b0_channel.py",
    "src/run_stage7b0_channel.py",
    "src/analyze_stage7b0_channel.py",
    "src/test_stage7b0_channel.py",
    "src/stage7_slice1.py",
    "src/stage7_slice2.py",
    "src/datastream.py",
    "src/transforms.py",
    "src/consts.py",
)


@dataclass(frozen=True)
class Treatment:
    label: str
    a: int
    t: int = 128
    d: int = 255

    @property
    def alpha(self) -> Fraction:
        return Fraction(self.a, self.d)

    @property
    def heritable_state_sha256(self) -> str:
        payload = json.dumps(
            {"A": self.a, "D": self.d, "T": self.t},
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode()).hexdigest()


LOW = Treatment("LOW", 102)
HIGH = Treatment("HIGH", 204)
TREATMENTS = (LOW, HIGH)


EvidenceSink = list[dict[str, Any]]


def _require_block_lease(evidence: EvidenceSink, block_id: str) -> None:
    if not isinstance(evidence, list):
        raise TypeError(f"block {block_id} requires an evidence list")


def _begin_block(evidence: EvidenceSink, block_id: str) -> None:
    _require_block_lease(evidence, block_id)


def _emit_retained(evidence: EvidenceSink, event: dict[str, Any]) -> None:
    evidence.append(_jsonable(event))


def _complete_block_lease(
    evidence: EvidenceSink, block_id: str, result: dict[str, Any],
) -> None:
    _emit_retained(evidence, {
        "kind": "block_complete", "block": block_id, "result": result,
    })


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _participant_values(
    organism_id: str,
    role: str,
    treatment_label: str,
    a: int,
    t: int,
    d: int,
) -> dict[str, Any]:
    treatment = Treatment(treatment_label, a, t, d)
    return {
        "role": role,
        "organism_id": organism_id,
        "treatment_label": treatment_label,
        "A": a,
        "T": t,
        "D": d,
        "heritable_state_sha256": treatment.heritable_state_sha256,
    }


def _participant(
    organism: SliceOrganism,
    role: str,
    treatment_label: str,
) -> dict[str, Any]:
    return _participant_values(
        organism.organism_id, role, treatment_label,
        organism.a, organism.t, organism.d,
    )


def _identity(
    initial: list[dict[str, Any]],
    terminal: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "programme_sha256": PROGRAM_SPEC_SHA256,
        "initial_participants": initial,
        "terminal_participants": terminal,
    }


def _label_for_a(a: int) -> str:
    if a == 102:
        return "LOW"
    if a == 204:
        return "HIGH"
    raise ValueError(f"unregistered A value {a}")


def _organism_state(organism: SliceOrganism, role: str) -> dict[str, Any]:
    label = _label_for_a(organism.a)
    child = organism.child
    return {
        "participant": _participant(organism, role, label),
        "S": organism.s,
        "R": organism.r,
        "C_S": organism.c_s,
        "C_R": organism.c_r,
        "gross_income": organism.gross_income,
        "reversed_income": organism.reversed_income,
        "committed": organism.committed,
        "destroyed": organism.destroyed,
        "child": None if child is None else {
            "organism_id": child.organism_id, "S": child.s, "R": child.r,
            "A": child.a, "T": child.t, "D": child.d,
        },
        "events": _jsonable(organism.events),
    }


def _packet_snapshot(packet: PacketLedger) -> dict[str, Any]:
    lhs = packet.budget_remaining + packet.drawn_s + packet.drawn_r
    return {
        "packet_id": packet.packet_id,
        "kind": "captured",
        "initial_budget": packet.initial_budget,
        "budget_remaining": packet.budget_remaining,
        "drawn_S": packet.drawn_s,
        "drawn_R": packet.drawn_r,
        "lhs": lhs,
        "rhs": packet.initial_budget,
        "closed": lhs == packet.initial_budget,
    }


def _isolated_checkpoint(
    name: str,
    detail: str,
    parent: SliceOrganism,
    memory: MemoryLedger,
    packets: list[PacketLedger],
) -> dict[str, Any]:
    opening_s, opening_r = Fraction(100), Fraction(0)
    reserve_lhs = parent.s + parent.r + parent.committed + parent.destroyed
    reserve_rhs = (
        opening_s + opening_r + parent.gross_income - parent.reversed_income
        - parent.c_s - parent.c_r
    )
    reserve = {
        "kind": "isolated", "opening_S": opening_s, "opening_R": opening_r,
        "current_S": parent.s, "current_R": parent.r,
        "committed": parent.committed, "destroyed": parent.destroyed,
        "gross_income": parent.gross_income,
        "reversed_income": parent.reversed_income,
        "C_S": parent.c_s, "C_R": parent.c_r,
        "lhs": reserve_lhs, "rhs": reserve_rhs,
        "closed": reserve_lhs == reserve_rhs,
    }
    memory_totals = memory.totals()
    memory_lhs = sum(memory_totals.values())
    packet_states = [_packet_snapshot(packet) for packet in packets]
    memory_state = {
        "initial_pool": memory.initial_pool,
        "totals": memory_totals,
        "lhs": memory_lhs,
        "rhs": memory.initial_pool,
        "ownership": {
            "somatic_active": dict(sorted(memory.somatic_active.items())),
            "gestation": dict(sorted(memory.gestation.items())),
            "corpse_reserved": dict(sorted(memory.corpse_reserved.items())),
        },
        "closed": memory_lhs == memory.initial_pool,
    }
    participants = [_participant(parent, "parent", _label_for_a(parent.a))]
    if parent.child is not None:
        participants.append(_participant_values(
            parent.child.organism_id, "descendant", _label_for_a(parent.child.a),
            parent.child.a, parent.child.t, parent.child.d,
        ))
    closed = (
        reserve["closed"] and all(packet["closed"] for packet in packet_states)
        and memory_state["closed"]
    )
    return {
        "name": name, "detail": detail, "reserve": reserve,
        "packets": packet_states, "memory": memory_state, "census": None,
        "participants": participants,
        "accounts": [_organism_state(parent, "parent")],
        "population_events": [],
        "evictions": 0, "closed": closed,
    }

def _population_checkpoint(
    name: str,
    detail: str,
    population: Stage7Population,
) -> dict[str, Any]:
    reserve_base = population.reserve_closure()
    gross = sum((item.gross_income for item in population.all_organisms.values()), Fraction(0))
    reversed_income = sum((item.reversed_income for item in population.all_organisms.values()), Fraction(0))
    costs = sum((item.c_s + item.c_r for item in population.all_organisms.values()), Fraction(0))
    reserve = {
        "kind": "population", "opening_energy": population.opening_energy,
        "live_reserves": reserve_base["live_reserves"],
        "destroyed": reserve_base["destroyed"], "gross_income": gross,
        "reversed_income": reversed_income, "costs": costs,
        "lhs": reserve_base["lhs"], "rhs": reserve_base["rhs"],
        "closed": reserve_base["closed"],
    }
    packets = [_packet_snapshot(packet) for packet in population.packets]
    for packet in population.packet_buffer.buffer:
        initial = Fraction(packet.e_initial)
        remaining = Fraction(packet.e_budget)
        packets.append({
            "packet_id": packet.packet_id, "kind": "unread",
            "initial_budget": initial, "budget_remaining": remaining,
            "drawn_S": Fraction(0), "drawn_R": Fraction(0),
            "lhs": remaining, "rhs": initial, "closed": remaining == initial,
        })
    memory_totals = population.memory.totals()
    memory_lhs = sum(memory_totals.values())
    memory_state = {
        "initial_pool": population.memory.initial_pool,
        "totals": memory_totals, "lhs": memory_lhs,
        "rhs": population.memory.initial_pool,
        "ownership": {
            "somatic_active": dict(sorted(population.memory.somatic_active.items())),
            "gestation": dict(sorted(population.memory.gestation.items())),
            "corpse_reserved": dict(sorted(population.memory.corpse_reserved.items())),
        },
        "closed": memory_lhs == population.memory.initial_pool,
    }
    births = sum(event["event"] == "birth_admitted" for event in population.event_log)
    deaths = sum(event["event"] == "hazard_death" for event in population.event_log)
    founder_fraction = population.opening_energy / Fraction(100)
    if founder_fraction.denominator != 1:
        raise ValueError("registered population founder input is not an integer multiple of 100")
    founders = int(founder_fraction)
    expected_census = founders + births - deaths
    census = {
        "founders": founders, "admitted_births": births,
        "hazard_removals": deaths, "lhs": expected_census,
        "rhs": len(population.members), "closed": expected_census == len(population.members),
    }
    generated = population.packet_buffer.stream.next_packet_id
    evictions = generated - len(population.packets) - len(population.packet_buffer.buffer)
    participants = []
    for organism_id in sorted(population.members):
        organism = population.members[organism_id].organism
        numeric_id = int(organism_id.split("-")[1])
        role = "founder" if numeric_id < founders else "descendant"
        participants.append(_participant(organism, role, _label_for_a(organism.a)))
    closed = (
        reserve["closed"] and all(packet["closed"] for packet in packets)
        and memory_state["closed"] and census["closed"] and evictions == 0
    )
    return {
        "name": name, "detail": detail, "reserve": reserve,
        "packets": packets, "memory": memory_state, "census": census,
        "participants": participants,
        "accounts": [
            _organism_state(
                population.members[organism_id].organism,
                "founder" if int(organism_id.split("-")[1]) < founders else "descendant",
            )
            for organism_id in sorted(population.members)
        ],
        "population_events": list(population.event_log),
        "evictions": evictions, "closed": closed,
    }

def _transition(
    operation: str,
    result: str,
    actor: str = "parent",
    tick: int | None = None,
) -> dict[str, Any]:
    return {"tick": tick, "actor": actor, "operation": operation, "result": result}


def _finish_block(arms: dict[str, Any]) -> dict[str, Any]:
    return {"raw": {"arms": arms}}


def _record_checkpoint(
    lease: EvidenceSink,
    block_id: str,
    arm_id: str,
    checkpoints: list[dict[str, Any]],
    checkpoint: dict[str, Any],
) -> None:
    _require_block_lease(lease, block_id)
    checkpoints.append(checkpoint)
    _emit_retained(lease, {
        "kind": "checkpoint",
        "block": block_id,
        "arm": arm_id,
        "checkpoint": checkpoint,
    })


def _packet_closed(packet: PacketLedger) -> bool:
    return packet.budget_remaining + packet.drawn_s + packet.drawn_r == packet.initial_budget


def _memory_closed(memory: MemoryLedger) -> bool:
    return sum(memory.totals().values()) == memory.initial_pool


def _allocation_events_close(organisms: list[SliceOrganism]) -> bool:
    for organism in organisms:
        for event in organism.events:
            if event["event"] != "draw":
                continue
            y = event["quantity"]
            if event["delta_r"] != organism.alpha * y:
                return False
            if event["delta_s"] != y - event["delta_r"]:
                return False
    return True


def _direct_debit_isolated(organisms: list[SliceOrganism]) -> bool:
    for organism in organisms:
        for event in organism.events:
            if event["event"] == "charge_s":
                reason = event["reason"]
                if reason.startswith("gestation_upkeep:") or reason.endswith(":work"):
                    return False
            if event["event"] == "charge_r":
                reason = event["reason"]
                if reason.endswith(":dispatch") or reason.startswith("ordinary_upkeep:"):
                    return False
    return True


def _realised_treatment(organisms: list[SliceOrganism], treatment: Treatment) -> bool:
    return all(
        (organism.a, organism.t, organism.d)
        == (treatment.a, treatment.t, treatment.d)
        for organism in organisms
    )


def _new_isolated(treatment: Treatment, owner: str = "parent") -> tuple[MemoryLedger, SliceOrganism]:
    memory = MemoryLedger(8192)
    organism = SliceOrganism(
        owner,
        memory,
        Fraction(100),
        Fraction(0),
        a=treatment.a,
        t=treatment.t,
        d=treatment.d,
    )
    return memory, organism


def _block_a(lease: EvidenceSink) -> dict[str, Any]:
    _require_block_lease(lease, "A")
    progress = lease
    expected = {
        "LOW": {"ys": Fraction(315, 4), "yr": Fraction(105, 2), "rw": Fraction(413, 10), "child": Fraction(26432, 1275), "parent_s": Fraction(6271, 40)},
        "HIGH": {"ys": Fraction(105, 4), "yr": Fraction(105), "rw": Fraction(469, 5), "child": Fraction(60032, 1275), "parent_s": Fraction(4171, 40)},
    }
    arms: dict[str, Any] = {}
    checks = {name: True for name in BLOCK_CHECK_KEYS["A"]}
    expected_transitions = [
        _transition("FORAGE_RLE", "SUCCESS"), _transition("ALLOC_OFFSPRING", "SUCCESS"),
        _transition("COPY_BLOCK", "SUCCESS"), _transition("DIVIDE", "SUCCESS"),
    ]
    for treatment in TREATMENTS:
        memory, parent = _new_isolated(treatment)
        source = DataStream(seed=42, phase_mode="monotonic_rich").generate_packet(0)
        packet = PacketLedger(source.packet_id, Fraction(300), source.max_reducible)
        checkpoints: list[dict[str, Any]] = []
        transitions: list[dict[str, Any]] = []
        initial = [_participant(parent, "parent", treatment.label)]
        _record_checkpoint(progress, "A", treatment.label, checkpoints, _isolated_checkpoint("INITIAL", "before programme", parent, memory, [packet]))
        compressed = parent.forage_rle(packet, source.data)
        transitions.append(_transition("FORAGE_RLE", "SUCCESS"))
        _record_checkpoint(progress, "A", treatment.label, checkpoints, _isolated_checkpoint("POST_FORAGE", "after FORAGE_RLE", parent, memory, [packet]))
        allocated = parent.allocate_offspring(64)
        transitions.append(_transition("ALLOC_OFFSPRING", "SUCCESS" if allocated else "R_INSUFFICIENT"))
        _record_checkpoint(progress, "A", treatment.label, checkpoints, _isolated_checkpoint("POST_ALLOC", "after ALLOC_OFFSPRING", parent, memory, [packet]))
        copied = parent.copy_block(11) if allocated else False
        transitions.append(_transition("COPY_BLOCK", "SUCCESS" if copied else "FAILED"))
        _record_checkpoint(progress, "A", treatment.label, checkpoints, _isolated_checkpoint("POST_COPY", "after COPY_BLOCK", parent, memory, [packet]))
        child = parent.divide_and_provision("child") if copied else None
        transitions.append(_transition("DIVIDE", "SUCCESS" if child is not None else "FAILED"))
        _record_checkpoint(progress, "A", treatment.label, checkpoints, _isolated_checkpoint("POST_DIVIDE", "after DIVIDE", parent, memory, [packet]))
        _record_checkpoint(progress, "A", treatment.label, checkpoints, _isolated_checkpoint("FINAL", "registered stop", parent, memory, [packet]))
        draw = next(event for event in parent.events if event["event"] == "draw")
        rw = draw["delta_r"] - parent.c_r
        exp = expected[treatment.label]
        terminal = [_participant(parent, "parent", treatment.label)]
        if child is not None:
            terminal.append(_participant_values(child.organism_id, "descendant", treatment.label, child.a, child.t, child.d))
        checks["realised_treatment"] &= _realised_treatment([parent], treatment)
        checks["programme_identity"] &= transitions == expected_transitions
        checks["allocation_identity"] &= (len(compressed) == 172 and draw["quantity"] == Fraction(525, 4) and draw["delta_s"] == exp["ys"] and draw["delta_r"] == exp["yr"])
        checks["direct_debit_isolation"] &= (_direct_debit_isolated([parent]) and parent.c_s == Fraction(879, 40) and parent.c_r == Fraction(56, 5))
        checks["all_checkpoints_closed"] &= all(cp["closed"] for cp in checkpoints)
        checks["no_hidden_gate"] &= (child is not None and rw == exp["rw"] and child.s == exp["child"] and child.r == 0 and parent.s == exp["parent_s"])
        arms[treatment.label] = {
            "identity": _identity(initial, terminal),
            "fixture": {"memory_pool": 8192, "parent_id": "parent", "opening_S": 100, "opening_R": 0, "seed": 42, "generation_tick": 0, "packet_id": 1, "packet_budget": 300, "max_reducible": 192, "child_id": "child"},
            "checkpoints": checkpoints,
            "transitions": transitions,
            "terminal": {"compressed_bytes": len(compressed), "parent_S": parent.s, "parent_R": parent.r, "child_S": None if child is None else child.s, "child_R": None if child is None else child.r, "organisms": [_organism_state(parent, "parent")], "memory_history": memory.history},
        }
    return _finish_block(arms)

def _configure_founder(population: Stage7Population, organism_id: str, treatment: Treatment) -> None:
    organism = population.members[organism_id].organism
    organism.a, organism.t, organism.d = treatment.a, treatment.t, treatment.d


def _derive_member_transitions(
    organism_events: list[dict[str, Any]],
    population_events: list[dict[str, Any]],
    tick: int,
    organism_id: str,
) -> list[dict[str, Any]]:
    transitions: list[dict[str, Any]] = []
    if any(event["event"] == "draw" for event in organism_events):
        transitions.append(_transition("FORAGE_RLE", "SUCCESS", organism_id, tick))
    elif any(event["event"] == "packet_capture_failed" for event in population_events):
        return [_transition("READ_EMPTY", "NO_PACKET", organism_id, tick)]
    if any(event["event"] == "gestation_allocated" for event in organism_events):
        transitions.append(_transition("ALLOC_OFFSPRING", "SUCCESS", organism_id, tick))
    if any(event["event"] == "copy_complete" for event in organism_events):
        transitions.append(_transition("COPY_BLOCK", "SUCCESS", organism_id, tick))
    if any(event["event"] == "provision_committed" for event in organism_events):
        transitions.append(_transition("DIVIDE", "SUCCESS", organism_id, tick))
    elif any(event["event"] == "divide_rejected_no_vacancy" for event in organism_events):
        transitions.append(_transition("DIVIDE", "REJECTED_NO_VACANCY", organism_id, tick))
    return transitions


def _registered_population_step(
    population: Stage7Population,
    block_id: str,
    arm_id: str,
    checkpoints: list[dict[str, Any]],
    progress: EvidenceSink,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    _require_block_lease(progress, block_id)
    tick = population.tick
    if population.hazard_schedule.get(tick) or population.hazard_rate != 0:
        raise ValueError("registered B/D fixtures prohibit hazard removals")
    before_ids = [packet.packet_id for packet in population.packet_buffer.buffer]
    population.packet_buffer.advance_tick()
    after_ids = [packet.packet_id for packet in population.packet_buffer.buffer]
    arrivals = [packet_id for packet_id in after_ids if packet_id not in before_ids]
    _record_checkpoint(progress, block_id, arm_id, checkpoints,
        _population_checkpoint("POST_PACKET_ARRIVAL", f"tick={tick};arrivals={arrivals}", population))

    vacancies = population.capacity - len(population.members)
    scheduler_snapshot = sorted(population.members)
    newborn_ids: list[str] = []
    rejected = 0
    transitions: list[dict[str, Any]] = []
    for organism_id in scheduler_snapshot:
        member = population.members.get(organism_id)
        if member is None or member.state != "ACTIVE" or member.organism.s < 10:
            raise ValueError(f"unregistered scheduler state for {organism_id}")
        member.last_run_tick = tick
        organism_start = len(member.organism.events)
        population_start = len(population.event_log)
        vacancies, child_id, was_rejected = population._run_reproductive_cycle(member, vacancies)
        organism_events = member.organism.events[organism_start:]
        population_events = population.event_log[population_start:]
        for event in organism_events:
            event["tick"] = tick
            event["actor"] = organism_id
        transitions.extend(_derive_member_transitions(organism_events, population_events, tick, organism_id))
        rejected += int(was_rejected)
        if child_id is not None:
            newborn_ids.append(child_id)
        for event in population_events:
            if event["event"] == "birth_admitted":
                _record_checkpoint(progress, block_id, arm_id, checkpoints,
                    _population_checkpoint("POST_ADMISSION", f"tick={tick};child={event['child_id']}", population))
            elif event["event"] == "birth_rejected_no_vacancy":
                _record_checkpoint(progress, block_id, arm_id, checkpoints,
                    _population_checkpoint("POST_REJECTION", f"tick={tick};parent={event['parent_id']}", population))
        _record_checkpoint(progress, block_id, arm_id, checkpoints,
            _population_checkpoint("POST_MEMBER", f"tick={tick};organism={organism_id}", population))

    population._expire_corpses()
    closure = population.assert_all_ledgers(f"tick_complete:{tick}")
    _record_checkpoint(progress, block_id, arm_id, checkpoints,
        _population_checkpoint("TICK_COMPLETE", f"tick={tick}", population))
    snapshot = {
        "tick": tick,
        "packet_arrivals": arrivals,
        "scheduler_snapshot": scheduler_snapshot,
        "admitted_births": len(newborn_ids),
        "rejected_births": rejected,
        "newborn_ids": newborn_ids,
        "live_census": len(population.members),
        "reserve_closed": closure["reserve_closed"],
        "packets_closed": closure["packets_closed"],
        "memory_closed": closure["memory_closed"],
    }
    population.tick += 1
    return snapshot, transitions, {"before_buffer": before_ids, "after_arrival_buffer": after_ids}


def _population_closes(population: Stage7Population, checkpoints: list[dict[str, Any]]) -> bool:
    return (
        bool(checkpoints) and all(checkpoint["closed"] for checkpoint in checkpoints)
        and population.reserve_closure()["closed"]
        and all(_packet_closed(packet) for packet in population.packets)
        and all(Fraction(packet.e_budget) == Fraction(packet.e_initial) for packet in population.packet_buffer.buffer)
        and _memory_closed(population.memory)
    )

def _run_block_b_arm(
    treatment: Treatment,
    lease: EvidenceSink,
) -> tuple[dict[str, Any], dict[str, bool]]:
    _require_block_lease(lease, "B")
    progress = lease
    population = Stage7Population(
        capacity=4, founder_count=1, founder_s=Fraction(100), memory_pool=8192,
        hazard_schedule={}, hazard_rate=Fraction(0), corpse_ttl=2,
        packet_rate=2, buffer_depth=4, packet_energy=Fraction(300),
    )
    _configure_founder(population, "org-0", treatment)
    checkpoints: list[dict[str, Any]] = []
    transitions: list[dict[str, Any]] = []
    tick_trace: list[dict[str, Any]] = []
    initial = [_participant(population.all_organisms["org-0"], "founder", treatment.label)]
    _record_checkpoint(progress, "B", treatment.label, checkpoints,
        _population_checkpoint("INITIAL", "before tick 0", population))
    for _ in range(2):
        snapshot, emitted, buffer_trace = _registered_population_step(
            population, "B", treatment.label, checkpoints, progress)
        transitions.extend(emitted)
        tick_trace.append({"snapshot": snapshot, "buffer": buffer_trace})
    births = [event for event in population.event_log if event["event"] == "birth_admitted"]
    expected_births = [(0, "org-0", "org-1"), (1, "org-0", "org-2"), (1, "org-1", "org-3")]
    observed_births = [(event["tick"], event["parent_id"], event["child_id"]) for event in births]
    expected_transitions = [
        _transition(op, "SUCCESS", "org-0", 0)
        for op in ("FORAGE_RLE", "ALLOC_OFFSPRING", "COPY_BLOCK", "DIVIDE")
    ] + [
        _transition(op, "SUCCESS", actor, 1)
        for actor in ("org-0", "org-1")
        for op in ("FORAGE_RLE", "ALLOC_OFFSPRING", "COPY_BLOCK", "DIVIDE")
    ]
    organisms = list(population.all_organisms.values())
    terminal = [
        _participant(org, "founder" if oid == "org-0" else "descendant", treatment.label)
        for oid, org in population.all_organisms.items()
    ]
    checks = {
        "realised_treatment": _realised_treatment(organisms, treatment),
        "programme_identity": transitions == expected_transitions,
        "allocation_identity": _allocation_events_close(organisms),
        "direct_debit_isolation": _direct_debit_isolated(organisms),
        "two_generation_sequence": (
            observed_births == expected_births
            and tick_trace[0]["snapshot"]["packet_arrivals"] == [1, 2]
            and tick_trace[0]["snapshot"]["scheduler_snapshot"] == ["org-0"]
            and tick_trace[1]["snapshot"]["packet_arrivals"] == [3, 4]
            and tick_trace[1]["snapshot"]["scheduler_snapshot"] == ["org-0", "org-1"]
            and [packet.packet_id for packet in population.packet_buffer.buffer] == [4]
            and len(population.members) == 4
        ),
        "all_checkpoints_closed": _population_closes(population, checkpoints),
        "no_hidden_gate": (
            not any(event["event"] in {"hazard_death", "somatic_stall", "birth_rejected_no_vacancy"} for event in population.event_log)
            and tick_trace[-1]["snapshot"]["admitted_births"] == 2
            and population.packet_buffer.stream.next_packet_id == 4
        ),
    }
    arm = {
        "identity": _identity(initial, terminal),
        "fixture": {"capacity": 4, "founders": 1, "founder_id": "org-0", "founder_S": 100, "founder_R": 0, "memory_pool": 8192, "seed": 42, "packet_rate": 2, "buffer_depth": 4, "packet_budget": 300, "hazard_rate": 0, "corpse_ttl": 2, "ticks": [0, 1]},
        "checkpoints": checkpoints,
        "transitions": transitions,
        "terminal": {"tick_trace": tick_trace, "population_events": population.event_log, "final_buffer_ids": [packet.packet_id for packet in population.packet_buffer.buffer], "final_census": len(population.members), "organisms": [_organism_state(organism, "founder" if organism_id == "org-0" else "descendant") for organism_id, organism in sorted(population.all_organisms.items())], "memory_history": population.memory.history},
    }
    return arm, checks


def _block_b(lease: EvidenceSink) -> dict[str, Any]:
    _require_block_lease(lease, "B")
    arms: dict[str, Any] = {}
    aggregate = {name: True for name in BLOCK_CHECK_KEYS["B"]}
    for treatment in TREATMENTS:
        arm, checks = _run_block_b_arm(treatment, lease)
        arms[treatment.label] = arm
        for name, value in checks.items():
            aggregate[name] &= value
    return _finish_block(arms)

def _block_c(lease: EvidenceSink) -> dict[str, Any]:
    _require_block_lease(lease, "C")
    progress = lease
    expected_first = {
        "LOW": (Fraction(6671, 80), Fraction(7, 4), Fraction(21, 8), Fraction(7, 4)),
        "HIGH": (Fraction(6531, 80), Fraction(7, 2), Fraction(7, 8), Fraction(7, 2)),
    }
    aggregate = {name: True for name in BLOCK_CHECK_KEYS["C"]}
    arms: dict[str, Any] = {}
    expected_transitions = [
        _transition("FORAGE_RLE", "SUCCESS"),
        _transition("ALLOC_OFFSPRING", "R_INSUFFICIENT"),
        _transition("FORAGE_RLE", "SUCCESS"),
        _transition("ALLOC_OFFSPRING", "SUCCESS"),
        _transition("COPY_BLOCK", "SUCCESS"),
        _transition("DIVIDE", "SUCCESS"),
    ]
    for treatment in TREATMENTS:
        memory, parent = _new_isolated(treatment)
        stream = DataStream(seed=42, phase_mode="monotonic_rich")
        source1, source2 = stream.generate_packet(0), stream.generate_packet(1)
        packet1 = PacketLedger(source1.packet_id, Fraction(10), source1.max_reducible)
        packet2 = PacketLedger(source2.packet_id, Fraction(300), source2.max_reducible)
        packets = [packet1, packet2]
        checkpoints: list[dict[str, Any]] = []
        transitions: list[dict[str, Any]] = []
        initial = [_participant(parent, "parent", treatment.label)]
        _record_checkpoint(progress, "C", treatment.label, checkpoints, _isolated_checkpoint("INITIAL", "before first forage", parent, memory, packets))
        parent.forage_rle(packet1, source1.data)
        transitions.append(_transition("FORAGE_RLE", "SUCCESS"))
        _record_checkpoint(progress, "C", treatment.label, checkpoints, _isolated_checkpoint("POST_FORAGE", "first opportunity", parent, memory, packets))
        first_alloc = parent.allocate_offspring(64)
        transitions.append(_transition("ALLOC_OFFSPRING", "SUCCESS" if first_alloc else "R_INSUFFICIENT"))
        first_state = (parent.s, parent.r)
        first_failure_event = next((event for event in reversed(parent.events) if event["event"] == "r_insufficient"), None)
        no_first_gestation = memory.totals()["gestation"] == 0 and parent.child is None
        _record_checkpoint(progress, "C", treatment.label, checkpoints, _isolated_checkpoint("POST_ALLOC", "first failed allocation", parent, memory, packets))
        parent.forage_rle(packet2, source2.data)
        transitions.append(_transition("FORAGE_RLE", "SUCCESS"))
        _record_checkpoint(progress, "C", treatment.label, checkpoints, _isolated_checkpoint("POST_FORAGE", "second opportunity", parent, memory, packets))
        second_alloc = parent.allocate_offspring(64)
        transitions.append(_transition("ALLOC_OFFSPRING", "SUCCESS" if second_alloc else "R_INSUFFICIENT"))
        _record_checkpoint(progress, "C", treatment.label, checkpoints, _isolated_checkpoint("POST_ALLOC", "second allocation", parent, memory, packets))
        copied = parent.copy_block(11) if second_alloc else False
        transitions.append(_transition("COPY_BLOCK", "SUCCESS" if copied else "FAILED"))
        _record_checkpoint(progress, "C", treatment.label, checkpoints, _isolated_checkpoint("POST_COPY", "second copy", parent, memory, packets))
        child = parent.divide_and_provision("child") if copied else None
        transitions.append(_transition("DIVIDE", "SUCCESS" if child is not None else "FAILED"))
        _record_checkpoint(progress, "C", treatment.label, checkpoints, _isolated_checkpoint("POST_DIVIDE", "second divide", parent, memory, packets))
        _record_checkpoint(progress, "C", treatment.label, checkpoints, _isolated_checkpoint("FINAL", "registered stop", parent, memory, packets))
        exp_s, exp_r, exp_ys, exp_yr = expected_first[treatment.label]
        draws = [event for event in parent.events if event["event"] == "draw"]
        terminal = [_participant(parent, "parent", treatment.label)]
        if child is not None:
            terminal.append(_participant_values(child.organism_id, "descendant", treatment.label, child.a, child.t, child.d))
        aggregate["realised_treatment"] &= _realised_treatment([parent], treatment)
        aggregate["programme_identity"] &= transitions == expected_transitions
        aggregate["allocation_identity"] &= (_allocation_events_close([parent]) and draws[0]["quantity"] == Fraction(35, 8) and draws[0]["delta_s"] == exp_ys and draws[0]["delta_r"] == exp_yr and draws[1]["quantity"] == Fraction(525, 4))
        aggregate["direct_debit_isolation"] &= _direct_debit_isolated([parent])
        aggregate["registered_recovery"] &= (
            first_alloc is False and first_state == (exp_s, exp_r)
            and first_failure_event is not None and first_failure_event["reason"] == "ALLOC_OFFSPRING:work"
            and no_first_gestation and second_alloc and child is not None
            and source1.packet_id == 1 and source2.packet_id == 2
        )
        aggregate["all_checkpoints_closed"] &= all(cp["closed"] for cp in checkpoints)
        aggregate["no_hidden_gate"] &= child is not None and child.r == 0 and len(draws) == 2
        arms[treatment.label] = {
            "identity": _identity(initial, terminal),
            "fixture": {"memory_pool": 8192, "parent_id": "parent", "opening_S": 100, "opening_R": 0, "seed": 42, "packets": [{"generation_tick": 0, "packet_id": 1, "budget": 10}, {"generation_tick": 1, "packet_id": 2, "budget": 300}], "max_reducible": 192, "child_id": "child"},
            "checkpoints": checkpoints,
            "transitions": transitions,
            "terminal": {"first_state": {"S": first_state[0], "R": first_state[1]}, "first_failure_event": first_failure_event, "no_first_gestation": no_first_gestation, "parent_S": parent.s, "parent_R": parent.r, "child_S": None if child is None else child.s, "organisms": [_organism_state(parent, "parent")], "memory_history": memory.history},
        }
    return _finish_block(arms)

def _run_block_d_fixture(
    block_id: str,
    first: Treatment,
    second: Treatment,
    lease: EvidenceSink,
) -> tuple[dict[str, Any], dict[str, bool]]:
    _require_block_lease(lease, block_id)
    progress = lease
    population = Stage7Population(
        capacity=2, founder_count=2, founder_s=Fraction(100), memory_pool=8192,
        hazard_schedule={}, hazard_rate=Fraction(0), corpse_ttl=2,
        packet_rate=1, buffer_depth=2, packet_energy=Fraction(300),
    )
    _configure_founder(population, "org-0", first)
    _configure_founder(population, "org-1", second)
    labels = {"org-0": first.label, "org-1": second.label}
    checkpoints: list[dict[str, Any]] = []
    transitions: list[dict[str, Any]] = []
    tick_trace: list[dict[str, Any]] = []
    initial = [
        _participant(population.all_organisms["org-0"], "founder", first.label),
        _participant(population.all_organisms["org-1"], "founder", second.label),
    ]
    _record_checkpoint(progress, block_id, "fixture", checkpoints,
        _population_checkpoint("INITIAL", "before tick 0", population))
    for _ in range(4):
        snapshot, emitted, buffer_trace = _registered_population_step(
            population, block_id, "fixture", checkpoints, progress)
        transitions.extend(emitted)
        tick_trace.append({"snapshot": snapshot, "buffer": buffer_trace})
    expected_transitions = [
        item for tick in range(4) for item in (
            _transition("FORAGE_RLE", "SUCCESS", "org-0", tick),
            _transition("ALLOC_OFFSPRING", "SUCCESS", "org-0", tick),
            _transition("COPY_BLOCK", "SUCCESS", "org-0", tick),
            _transition("DIVIDE", "REJECTED_NO_VACANCY", "org-0", tick),
            _transition("READ_EMPTY", "NO_PACKET", "org-1", tick),
        )
    ]
    draws = [event for event in population.all_organisms["org-0"].events if event["event"] == "draw"]
    misses = [event for event in population.event_log if event["event"] == "packet_capture_failed"]
    rejects = [event for event in population.event_log if event["event"] == "birth_rejected_no_vacancy"]
    organisms = list(population.all_organisms.values())
    terminal = [
        _participant(population.all_organisms["org-0"], "founder", first.label),
        _participant(population.all_organisms["org-1"], "founder", second.label),
    ]
    checks = {
        "realised_treatment": (_realised_treatment([population.all_organisms["org-0"]], first) and _realised_treatment([population.all_organisms["org-1"]], second)),
        "programme_identity": transitions == expected_transitions,
        "allocation_identity": _allocation_events_close(organisms),
        "direct_debit_isolation": _direct_debit_isolated(organisms),
        "shared_source_topology": (
            [event["packet_id"] for event in draws] == [1, 2, 3, 4]
            and [(event["tick"], event["organism_id"]) for event in misses] == [(k, "org-1") for k in range(4)]
            and [(event["tick"], event["parent_id"]) for event in rejects] == [(k, "org-0") for k in range(4)]
            and all(item["snapshot"]["packet_arrivals"] == [index + 1] for index, item in enumerate(tick_trace))
            and not population.packet_buffer.buffer and len(population.packets) == 4
        ),
        "all_checkpoints_closed": _population_closes(population, checkpoints),
        "no_hidden_gate": (len(population.members) == 2 and all(item["snapshot"]["admitted_births"] == 0 for item in tick_trace) and population.packet_buffer.stream.next_packet_id == 4),
    }
    arm = {
        "identity": _identity(initial, terminal),
        "fixture": {"capacity": 2, "founders": 2, "founder_ids": ["org-0", "org-1"], "founder_S": 100, "founder_R": 0, "labels": labels, "memory_pool": 8192, "seed": 42, "packet_rate": 1, "buffer_depth": 2, "packet_budget": 300, "hazard_rate": 0, "corpse_ttl": 2, "ticks": [0, 1, 2, 3]},
        "checkpoints": checkpoints,
        "transitions": transitions,
        "terminal": {"tick_trace": tick_trace, "population_events": population.event_log, "capture_owner_ids": ["org-0"] * len(draws), "capture_labels": [first.label] * len(draws), "packet_ids": [event["packet_id"] for event in draws], "final_census": len(population.members), "organisms": [_organism_state(organism, "founder") for _, organism in sorted(population.all_organisms.items())], "memory_history": population.memory.history},
    }
    return arm, checks


def _block_d(
    lease: EvidenceSink,
    block_id: str,
    first: Treatment,
    second: Treatment,
) -> dict[str, Any]:
    _require_block_lease(lease, block_id)
    arm, checks = _run_block_d_fixture(block_id, first, second, lease)
    return _finish_block({"fixture": arm})

def _block_e1(lease: EvidenceSink) -> dict[str, Any]:
    _require_block_lease(lease, "E1")
    progress = lease
    expected20 = {"LOW": (Fraction(60), Fraction(40)), "HIGH": (Fraction(20), Fraction(80))}
    aggregate = {name: True for name in BLOCK_CHECK_KEYS["E1"]}
    arms: dict[str, Any] = {}
    expected_transitions = [
        _transition("FORAGE_RLE", "SUCCESS"),
        _transition("REVERSE_RLE_20", "SUCCESS"),
        _transition("REVERSE_RLE_64", "SUCCESS"),
    ]
    for treatment in TREATMENTS:
        memory, parent = _new_isolated(treatment)
        source = DataStream(seed=42, phase_mode="monotonic_rich").generate_packet(0)
        packet = PacketLedger(source.packet_id, Fraction(300), source.max_reducible)
        checkpoints: list[dict[str, Any]] = []
        transitions: list[dict[str, Any]] = []
        initial = [_participant(parent, "parent", treatment.label)]
        _record_checkpoint(progress, "E1", treatment.label, checkpoints, _isolated_checkpoint("INITIAL", "before forage", parent, memory, [packet]))
        compressed = parent.forage_rle(packet, source.data)
        transitions.append(_transition("FORAGE_RLE", "SUCCESS"))
        _record_checkpoint(progress, "E1", treatment.label, checkpoints, _isolated_checkpoint("POST_FORAGE", "after forage", parent, memory, [packet]))
        partial = parent.reverse_rle(packet, compressed, 20)
        transitions.append(_transition("REVERSE_RLE_20", "SUCCESS" if partial else "FAILED"))
        state20 = (packet.budget_remaining, packet.drawn_s, packet.drawn_r)
        _record_checkpoint(progress, "E1", treatment.label, checkpoints, _isolated_checkpoint("POST_REVERSAL", "extent=20", parent, memory, [packet]))
        complete = parent.reverse_rle(packet, compressed, 64)
        transitions.append(_transition("REVERSE_RLE_64", "SUCCESS" if complete else "FAILED"))
        state64 = (packet.budget_remaining, packet.drawn_s, packet.drawn_r)
        _record_checkpoint(progress, "E1", treatment.label, checkpoints, _isolated_checkpoint("POST_REVERSAL", "extent=64", parent, memory, [packet]))
        _record_checkpoint(progress, "E1", treatment.label, checkpoints, _isolated_checkpoint("FINAL", "registered stop", parent, memory, [packet]))
        exp_s, exp_r = expected20[treatment.label]
        aggregate["realised_treatment"] &= _realised_treatment([parent], treatment)
        aggregate["programme_identity"] &= transitions == expected_transitions
        aggregate["allocation_identity"] &= _allocation_events_close([parent])
        aggregate["partial_and_complete_reversal"] &= (source.packet_id == 1 and partial and complete and state20 == (Fraction(200), exp_s, exp_r) and state64 == (Fraction(300), Fraction(0), Fraction(0)))
        aggregate["all_checkpoints_closed"] &= all(cp["closed"] for cp in checkpoints)
        aggregate["no_hidden_gate"] &= parent.reversed_income == Fraction(525, 4)
        arms[treatment.label] = {
            "identity": _identity(initial, [_participant(parent, "parent", treatment.label)]),
            "fixture": {"memory_pool": 8192, "parent_id": "parent", "opening_S": 100, "opening_R": 0, "seed": 42, "generation_tick": 0, "packet_id": 1, "packet_budget": 300, "partial_extent": 20, "complete_extent": 64},
            "checkpoints": checkpoints,
            "transitions": transitions,
            "terminal": {"state_after_20": state20, "state_after_64": state64, "parent_S": parent.s, "parent_R": parent.r, "organisms": [_organism_state(parent, "parent")], "memory_history": memory.history},
        }
    return _finish_block(arms)

def _block_e2(lease: EvidenceSink) -> dict[str, Any]:
    _require_block_lease(lease, "E2")
    progress = lease
    expected = {
        "LOW": (Fraction(52451, 2550), (Fraction(675, 4), Fraction(315, 4), Fraction(105, 2))),
        "HIGH": (Fraction(59563, 1275), (Fraction(675, 4), Fraction(105, 4), Fraction(105))),
    }
    aggregate = {name: True for name in BLOCK_CHECK_KEYS["E2"]}
    arms: dict[str, Any] = {}
    expected_transitions = [
        _transition("FORAGE_RLE", "SUCCESS"), _transition("ALLOC_OFFSPRING", "SUCCESS"),
        _transition("COPY_BLOCK", "SUCCESS"), _transition("DIVIDE", "SUCCESS"),
        _transition("REVERSE_RLE_80", "REVERSAL_ACCOUNT_UNAVAILABLE"),
    ]
    for treatment in TREATMENTS:
        memory, parent = _new_isolated(treatment)
        source = DataStream(seed=43, phase_mode="monotonic_rich").generate_packet(0)
        packet = PacketLedger(source.packet_id, Fraction(300), source.max_reducible)
        checkpoints: list[dict[str, Any]] = []
        transitions: list[dict[str, Any]] = []
        initial = [_participant(parent, "parent", treatment.label)]
        _record_checkpoint(progress, "E2", treatment.label, checkpoints, _isolated_checkpoint("INITIAL", "before programme", parent, memory, [packet]))
        compressed = parent.forage_rle(packet, source.data)
        transitions.append(_transition("FORAGE_RLE", "SUCCESS"))
        _record_checkpoint(progress, "E2", treatment.label, checkpoints, _isolated_checkpoint("POST_FORAGE", "after forage", parent, memory, [packet]))
        allocated = parent.allocate_offspring(64)
        transitions.append(_transition("ALLOC_OFFSPRING", "SUCCESS" if allocated else "R_INSUFFICIENT"))
        _record_checkpoint(progress, "E2", treatment.label, checkpoints, _isolated_checkpoint("POST_ALLOC", "after allocation", parent, memory, [packet]))
        copied = parent.copy_block(11) if allocated else False
        transitions.append(_transition("COPY_BLOCK", "SUCCESS" if copied else "FAILED"))
        _record_checkpoint(progress, "E2", treatment.label, checkpoints, _isolated_checkpoint("POST_COPY", "after copy", parent, memory, [packet]))
        child = parent.divide_and_provision("child") if copied else None
        transitions.append(_transition("DIVIDE", "SUCCESS" if child is not None else "FAILED"))
        _record_checkpoint(progress, "E2", treatment.label, checkpoints, _isolated_checkpoint("POST_DIVIDE", "after divide", parent, memory, [packet]))
        before = (parent.s, parent.r, packet.budget_remaining, packet.drawn_s, packet.drawn_r)
        succeeded = parent.reverse_rle(packet, compressed, 80)
        failure = parent.events[-1]
        transitions.append(_transition("REVERSE_RLE_80", "SUCCESS" if succeeded else failure["reason"]))
        after = (parent.s, parent.r, packet.budget_remaining, packet.drawn_s, packet.drawn_r)
        _record_checkpoint(progress, "E2", treatment.label, checkpoints, _isolated_checkpoint("POST_REVERSAL", "failed extent=80", parent, memory, [packet]))
        _record_checkpoint(progress, "E2", treatment.label, checkpoints, _isolated_checkpoint("FINAL", "registered stop", parent, memory, [packet]))
        expected_r, expected_packet = expected[treatment.label]
        terminal = [_participant(parent, "parent", treatment.label)]
        if child is not None:
            terminal.append(_participant_values(child.organism_id, "descendant", treatment.label, child.a, child.t, child.d))
        aggregate["realised_treatment"] &= _realised_treatment([parent], treatment)
        aggregate["programme_identity"] &= transitions == expected_transitions
        aggregate["allocation_identity"] &= _allocation_events_close([parent])
        aggregate["direct_debit_isolation"] &= _direct_debit_isolated([parent])
        aggregate["spent_credit_atomic_failure"] &= (child is not None and source.packet_id == 1 and succeeded is False and before[1] == expected_r and before[2:] == expected_packet and after[1:] == before[1:] and before[0] - after[0] == Fraction(859, 160) and failure["event"] == "reversal_failed" and failure["reason"] == "REVERSAL_ACCOUNT_UNAVAILABLE")
        aggregate["all_checkpoints_closed"] &= all(cp["closed"] for cp in checkpoints)
        aggregate["no_hidden_gate"] &= succeeded is False
        arms[treatment.label] = {
            "identity": _identity(initial, terminal),
            "fixture": {"memory_pool": 8192, "parent_id": "parent", "opening_S": 100, "opening_R": 0, "seed": 43, "generation_tick": 0, "packet_id": 1, "packet_budget": 300, "failed_reversal_extent": 80, "child_id": "child"},
            "checkpoints": checkpoints,
            "transitions": transitions,
            "terminal": {"before_reversal": before, "after_reversal": after, "failure_event": failure, "organisms": [_organism_state(parent, "parent")], "memory_history": memory.history},
        }
    return _finish_block(arms)

def execute_deterministic_protocol(
    manifest_sha256: str,
    evidence: EvidenceSink | None = None,
) -> tuple[dict[str, Any], EvidenceSink]:
    """Execute Blocks A–E deterministically and return raw evidence in order."""
    if len(manifest_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in manifest_sha256
    ):
        raise ValueError("manifest digest must be lowercase SHA-256")
    evidence = [] if evidence is None else evidence
    if not isinstance(evidence, list) or evidence:
        raise ValueError("evidence sink must be an empty list")
    blocks: dict[str, Any] = {}
    runners: list[tuple[str, Callable[[], dict[str, Any]]]] = [
        ("A", lambda: _block_a(evidence)),
        ("B", lambda: _block_b(evidence)),
        ("C", lambda: _block_c(evidence)),
        ("D1", lambda: _block_d(evidence, "D1", LOW, HIGH)),
        ("D2", lambda: _block_d(evidence, "D2", HIGH, LOW)),
        ("E1", lambda: _block_e1(evidence)),
        ("E2", lambda: _block_e2(evidence)),
    ]
    for block_id, runner in runners:
        _begin_block(evidence, block_id)
        result = runner()
        blocks[block_id] = result
        _complete_block_lease(evidence, block_id, result)
    artifact = {
        "scope": "Stage 7B0 scripted fixed-state mechanism verification",
        "selection_assay_run": False,
        "mutation_enabled": False,
        "mutation_rng_draws": 0,
        "protocol_sha256": PROTOCOL_SHA256,
        "programme_specification_sha256": PROGRAM_SPEC_SHA256,
        "freeze_manifest_sha256": manifest_sha256,
        "blocks": blocks,
    }
    return _jsonable(artifact), evidence
