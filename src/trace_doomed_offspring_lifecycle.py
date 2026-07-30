"""Deterministic normal-scheduler trace of a doomed instantiated offspring."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from consts import CORPSE_POOL_TTL, DIVIDE, JUMP, NOP, SHARED_MEMORY_POOL
from engine import Simulation

ROOT = Path("/opt/data/avida-life")
OUT = ROOT / "doomed-offspring-lifecycle-trace.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def memory_snapshot(sim: Simulation, label: str) -> dict:
    substrate = sim.substrate
    active = sum(
        sum(org.memory_allocations.values())
        for org in substrate.organisms.values()
    )
    corpse = substrate.corpse_allocated_bytes()
    total = substrate.shared_memory_pool + active + corpse
    return {
        "label": label,
        "tick": sim.tick,
        "shared_memory": substrate.shared_memory_pool,
        "active_memory": active,
        "corpse_memory": corpse,
        "accounted_total": total,
        "pool_capacity": SHARED_MEMORY_POOL,
        "ledger_closes": total == SHARED_MEMORY_POOL,
    }


def main() -> None:
    sim = Simulation(seed=0, phase_mode="monotonic_rich", population_cap=2)
    parent = sim.substrate.add_organism(
        [(DIVIDE,), (JUMP, 0)], reserve=100, lineage_label="PARENT")
    resident = sim.substrate.add_organism(
        [(NOP,)], reserve=100, lineage_label="RESIDENT")
    parent.registers[5] = 1
    gestation = parent.allocate_memory(64)
    parent.gestation_region = gestation
    parent.gestation_size = 64
    parent.gestation_buffer = [(NOP,)]

    memory = [memory_snapshot(sim, "before_birth")]
    sim.step()
    memory.append(memory_snapshot(sim, "after_birth_tick"))

    birth = next(row for row in sim.substrate.birth_log
                 if row["parent"] == parent.id)
    child_id = birth["id"]
    child = sim.substrate.organisms[child_id]
    displacement = sim.substrate.cap_replacement_log[-1]
    birth_state = {
        "birth": birth,
        "child_state": child.state,
        "child_reserve_after_birth_tick_upkeep": child.execution_reserve,
        "child_memory_bytes": sum(child.memory_allocations.values()),
        "displaced_resident_id": displacement["victim_id"],
        "expected_resident_id": resident.id,
        "victim_was_live": displacement["victim_was_live"],
        "victim_is_reproducing_parent":
            displacement["victim_is_reproducing_parent"],
    }

    sim.step()
    memory.append(memory_snapshot(sim, "after_child_death"))
    child_death = next(row for row in sim.substrate.ancestry
                       if row["id"] == child_id)
    displacement_after_death = next(
        row for row in sim.substrate.cap_replacement_log
        if row["causing_offspring_id"] == child_id)
    diagnostic = sim.substrate.displacement_viability_summary()

    for _ in range(CORPSE_POOL_TTL + 1):
        sim.step()
        memory.append(memory_snapshot(sim, "corpse_expiry_followup"))

    assert birth["birth_reserve"] < 18
    assert child_death["cause"] == "reserve exhausted"
    assert child_death["death_stage"] == "pre_first_extraction"
    assert not child_death["reached_first_positive_extraction"]
    assert displacement_after_death["causing_offspring_outcome"] == (
        "died_before_first_extraction")
    assert diagnostic[
        "live_displacements_caused_by_offspring_dying_before_first_extraction"] == 1
    assert diagnostic[
        "doomed_offspring_fraction_of_live_displacements"] == 1.0
    assert diagnostic[
        "unresolved_causing_offspring_live_displacements"] == 0
    assert all(row["ledger_closes"] for row in memory)
    assert memory[-1]["corpse_memory"] == 0
    assert memory[-1]["shared_memory"] + memory[-1]["active_memory"] == (
        SHARED_MEMORY_POOL)

    sources = [
        ROOT / "src" / "trace_doomed_offspring_lifecycle.py",
        ROOT / "src" / "engine.py",
        ROOT / "src" / "organism.py",
        ROOT / "src" / "consts.py",
    ]
    result = {
        "classification": "deterministic_normal_scheduler_lifecycle_trace",
        "population_inference": False,
        "birth_state": birth_state,
        "child_death": child_death,
        "causing_displacement": displacement_after_death,
        "displacement_diagnostic": diagnostic,
        "memory_ledger": memory,
        "reserve_semantics": (
            "terminal child reserve is not refunded or recycled; reserve is not "
            "a conserved substrate pool on death"
        ),
        "source_manifest": {
            str(path.relative_to(ROOT)): {
                "sha256": sha256(path),
                "mtime_ns": path.stat().st_mtime_ns,
                "size": path.stat().st_size,
            }
            for path in sources
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps({
        "output": str(OUT),
        "sha256": sha256(OUT),
        "birth_reserve": birth["birth_reserve"],
        "death_tick": child_death["death_tick"],
        "death_stage": child_death["death_stage"],
        "terminal_reserve": child_death["terminal_reserve"],
        "displacement_outcome": displacement_after_death[
            "causing_offspring_outcome"],
        "doomed_fraction": diagnostic[
            "doomed_offspring_fraction_of_live_displacements"],
        "memory_ledger_closed_every_snapshot": all(
            row["ledger_closes"] for row in memory),
        "final_corpse_memory": memory[-1]["corpse_memory"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
