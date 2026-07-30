"""Deterministic natural first-extraction ledger under the live VM.

A directly seeded organism with maturation_remaining=1 is scheduler-equivalent
for this purpose to a newborn: it pays one no-execution tick of full upkeep,
then begins at PC 0 on the following tick. No population inference is made.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from consts import PACKET_SIZE
from engine import Simulation, conditional_efficiency_assay_genome

ROOT = Path("/opt/data/avida-life")
OUT = ROOT / "offspring-first-extraction-ledger-summary.json"
RESERVES = [
    18.0,
    19.0,
    19.9,
    math.nextafter(20.0, -math.inf),
    20.0,
    math.nextafter(20.0, math.inf),
    20.1,
    21.0,
    25.0,
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trace(label: str, extent: int, reserve: float) -> dict:
    sim = Simulation(
        seed=90001,
        phase_mode="monotonic_rich",
        packet_e_rich=500,
        packet_e_lean=500,
        packet_rate=1,
        buffer_depth=1,
        population_cap=10,
        initial_buffer_packets=1,
        offspring_maturation_delay=0,
    )
    org = sim.substrate.add_organism(
        conditional_efficiency_assay_genome(extent, tau_r5=51),
        reserve=reserve,
        lineage_label=label,
    )
    if org is None:
        raise RuntimeError("failed to create first-extraction trace organism")
    org.maturation_remaining = 1
    ticks = []
    for _ in range(8):
        before = {
            "tick": sim.tick,
            "pc": org.pc,
            "reserve": org.execution_reserve,
            "state": org.state,
            "maturation_remaining": org.maturation_remaining,
            "memory_bytes": org.get_working_memory_size(),
        }
        sim.step()
        before.update({
            "pc_after": org.pc,
            "reserve_after": org.execution_reserve,
            "state_after": org.state,
            "memory_bytes_after": org.get_working_memory_size(),
        })
        ticks.append(before)
        if org.state == "DEAD" or sim.substrate.transform_event_log:
            break
    death = next((row for row in sim.substrate.ancestry
                  if row["id"] == org.id), None)
    return {
        "label": label,
        "extent": extent,
        "initial_reserve": reserve,
        "valid_read": org.last_valid_read_tick is not None,
        "last_valid_read_tick": org.last_valid_read_tick,
        "reached_extraction": bool(sim.substrate.transform_event_log),
        "transform_event": (sim.substrate.transform_event_log[0]
                            if sim.substrate.transform_event_log else None),
        "endpoint_state": org.state,
        "death_cause": death["cause"] if death else None,
        "death_tick": death["death_tick"] if death else None,
        "tick_trace": ticks,
    }


def main() -> None:
    rows = [
        trace(label, extent, reserve)
        for label, extent in (("FULL", PACKET_SIZE), ("HALF", 128))
        for reserve in RESERVES
    ]
    full_twenty = next(
        row for row in rows
        if row["label"] == "FULL" and row["initial_reserve"] == 20.0
    )
    read_tick = next(
        tick for tick in full_twenty["tick_trace"] if tick["pc"] == 4
    )
    sources = [
        ROOT / "src" / "trace_offspring_first_extraction.py",
        ROOT / "src" / "engine.py",
        ROOT / "src" / "organism.py",
        ROOT / "src" / "consts.py",
    ]
    result = {
        "classification": "deterministic_natural_first_extraction_ledger",
        "population_evidence": False,
        "scheduler_equivalence": (
            "maturation_remaining=1 supplies one no-execution birth tick "
            "with full upkeep before PC0 execution"
        ),
        "analytical_pre_extraction_ledger": {
            "birth_tick_upkeep_64_bytes": 0.2,
            "three_MOV_ticks_each_instruction_plus_upkeep": 3.6,
            "ALLOC_256_instruction_plus_post_alloc_upkeep": 5.6,
            "READ_instruction_plus_upkeep": 10.6,
            "total_through_end_of_READ_tick": 20.0,
            "exact_arithmetic_viability_condition": "initial_reserve > 20.0",
            "current_float_residue_at_literal_20_after_READ_tick": (
                read_tick["reserve_after"]
            ),
            "note": (
                "READ occurs before its cost is charged. TRANSFORM grants "
                "extraction before its own seven-unit cost is charged. "
                "Literal 20.0 reaches TRANSFORM only because current binary "
                "floating arithmetic leaves a tiny positive residue."
            ),
        },
        "interpreter_viability_threshold": None,
        "tested_reserves": RESERVES,
        "rows": rows,
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
        "outcomes": [
            {
                "label": row["label"],
                "initial_reserve": row["initial_reserve"],
                "valid_read": row["valid_read"],
                "reached_extraction": row["reached_extraction"],
                "death_cause": row["death_cause"],
            }
            for row in rows
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
