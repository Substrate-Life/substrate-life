"""Registered deterministic p=1 three-bout architectural capacity trace."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

from consts import PACKET_SIZE
from derive_stochastic_efficiency import disable_mutation
from engine import (
    Simulation,
    conditional_efficiency_assay_genome,
    efficiency_assay_genome,
)

CYCLES = 200
TAIL_CYCLES = 50
OUTPUT_DIR = Path("/opt/data/avida-life")
PREFIX = "efficiency-three-bout-p1-capacity"


def trace(label: str, extent: int,
          conditional: bool = False) -> tuple[dict, list[dict]]:
    sim = Simulation(
        seed=31_000 if label == "FULL" else 32_000,
        phase_mode="monotonic_rich",
        packet_e_rich=500,
        packet_e_lean=500,
        packet_rate=1,
        buffer_depth=1,
        population_cap=100,
    )
    genome = (
        conditional_efficiency_assay_genome(extent, tau_r5=51)
        if conditional else
        efficiency_assay_genome(extent, tau_r5=51, offspring_bouts=3))
    recurrent_interval = 17 if conditional else 15
    parent = sim.substrate.add_organism(genome, lineage_label=label)
    if parent is None:
        raise RuntimeError("failed to seed capacity-trace parent")
    parent_id = parent.id
    current_cycle = 0
    event_cursor = 0
    events: list[dict] = []
    r4_values: list[int] = []
    cycle_end_reserve: dict[int, float] = {}
    peak_parent_memory = parent.get_working_memory_size()
    peak_committed_memory = (
        sim.substrate.initial_shared_memory_pool -
        sim.substrate.shared_memory_pool)

    while current_cycle <= CYCLES:
        parent = sim.substrate.organisms.get(parent_id)
        if parent is None or parent.state == "DEAD":
            break
        if parent.pc == 4:
            if current_cycle >= CYCLES:
                cycle_end_reserve[current_cycle] = parent.execution_reserve
                break
            if current_cycle:
                cycle_end_reserve[current_cycle] = parent.execution_reserve
            current_cycle += 1
        if parent.pc == 6:
            # TRANSFORM executed on the previous tick.
            r4_values.append(parent.registers[4])

        sim.step()
        parent = sim.substrate.organisms.get(parent_id)
        if parent is not None:
            peak_parent_memory = max(
                peak_parent_memory, parent.get_working_memory_size())
        peak_committed_memory = max(
            peak_committed_memory,
            sim.substrate.initial_shared_memory_pool -
            sim.substrate.shared_memory_pool)

        new_events = sim.substrate.divide_event_log[event_cursor:]
        for event in new_events:
            if event["parent_id"] == parent_id:
                enriched = dict(event)
                enriched["cycle"] = current_cycle
                enriched["bout"] = 1 + sum(
                    prior["cycle"] == current_cycle for prior in events)
                events.append(enriched)
        event_cursor = len(sim.substrate.divide_event_log)

        # Isolate parent capacity. Newborns never execute.
        for oid in [oid for oid in sim.substrate.organisms
                    if oid != parent_id]:
            sim.substrate.remove_organism(oid, "capacity trace cleanup")
            del sim.substrate.organisms[oid]

    per_cycle = defaultdict(lambda: {"attempts": 0, "instantiations": 0,
                                     "materialization_failures": 0})
    for event in events:
        row = per_cycle[event["cycle"]]
        row["attempts"] += 1
        row["instantiations"] += int(event["offspring_instantiated"])
        row["materialization_failures"] += int(
            event["materialization_failure_reason"] is not None)

    completed = sorted(cycle for cycle in per_cycle if cycle <= CYCLES)
    tail = completed[-TAIL_CYCLES:]
    parent = sim.substrate.organisms.get(parent_id)
    read_ticks = [row["tick"] for row in sim.substrate.capture_history
                  if row["valid_read_attempts"]]
    read_intervals = [b - a for a, b in zip(read_ticks, read_ticks[1:])]
    tail_instantiations = [per_cycle[cycle]["instantiations"]
                           for cycle in tail]
    tail_attempts = [per_cycle[cycle]["attempts"] for cycle in tail]
    tail_failures = [per_cycle[cycle]["materialization_failures"]
                     for cycle in tail]
    all_instantiations = [per_cycle[cycle]["instantiations"]
                          for cycle in completed]
    all_attempts = [per_cycle[cycle]["attempts"] for cycle in completed]
    all_failures = [per_cycle[cycle]["materialization_failures"]
                    for cycle in completed]
    summary = {
        "label": label,
        "extent": extent,
        "cycles_registered": CYCLES,
        "complete_cycles": len(completed),
        "tail_cycles": len(tail),
        "genome_length": len(parent.genome) if parent else len(genome),
        "r6_after_initialization": parent.registers[6] if parent else None,
        "recurrent_interval_expected": recurrent_interval,
        "recurrent_interval_values": sorted(set(read_intervals)),
        "r4_min": min(r4_values) if r4_values else None,
        "r4_max": max(r4_values) if r4_values else None,
        "r4_values": sorted(set(r4_values)),
        "r4_bit_2048_values": sorted(set(
            value & 2048 for value in r4_values)),
        "tail_instantiations_per_cycle_values": sorted(
            set(tail_instantiations)),
        "tail_attempts_per_cycle_values": sorted(set(tail_attempts)),
        "tail_materialization_failures_per_cycle_values": sorted(
            set(tail_failures)),
        "all_instantiations_per_cycle_values": sorted(
            set(all_instantiations)),
        "all_attempts_per_cycle_values": sorted(set(all_attempts)),
        "all_materialization_failures_per_cycle_values": sorted(
            set(all_failures)),
        "total_offspring_instantiations": sum(all_instantiations),
        "total_materialization_failures": sum(all_failures),
        "tail_mean_instantiations_per_cycle": (
            sum(tail_instantiations) / len(tail)),
        "tail_mean_instantiations_per_tick": (
            sum(tail_instantiations) /
            (recurrent_interval * len(tail))),
        "parent_alive": parent is not None and parent.state != "DEAD",
        "parent_end_reserve": parent.execution_reserve if parent else None,
        "cycle_end_reserve_tail": [cycle_end_reserve.get(cycle)
                                   for cycle in tail],
        "peak_parent_memory": peak_parent_memory,
        "peak_committed_memory": peak_committed_memory,
        "allocation_failures":
            sim.substrate.memory_allocation_failures_total,
        "valid_reads": sim.substrate.capture_attempts_total,
        "captures": sim.substrate.capture_successes_total,
        "realised_capture_fraction": (
            sim.substrate.capture_successes_total /
            sim.substrate.capture_attempts_total),
        "realised_parameters": sim.realised_parameters(),
    }
    return summary, events


def main() -> None:
    disable_mutation()
    summaries = []
    all_events = []
    for label, extent in (("FULL", PACKET_SIZE), ("HALF", 128)):
        summary, events = trace(label, extent)
        summaries.append(summary)
        all_events.extend(events)

    by_label = {row["label"]: row for row in summaries}
    gate_pass = (
        by_label["FULL"]["tail_instantiations_per_cycle_values"] == [3] and
        by_label["HALF"]["tail_instantiations_per_cycle_values"] == [2] and
        by_label["FULL"]["parent_alive"] and
        by_label["HALF"]["parent_alive"] and
        by_label["FULL"]["allocation_failures"] == 0 and
        by_label["HALF"]["allocation_failures"] == 0)
    result = {
        "kind": "isolated_architectural_capacity_not_selection_evidence",
        "parameters": {
            "capture_probability": 1.0,
            "packet_energy": 500,
            "tau_r5": 51,
            "offspring_bouts": 3,
            "genome_length": 17,
            "recurrent_interval": 15,
            "cycles": CYCLES,
            "tail_cycles": TAIL_CYCLES,
            "mutation_rates": 0,
            "offspring_execute": False,
        },
        "summaries": summaries,
        "historical_instantiation_gate_full_3_half_2": gate_pass,
        "clean_fecundity_gate": False,
    }

    raw_path = OUTPUT_DIR / f"{PREFIX}-divide-events.jsonl"
    summary_path = OUTPUT_DIR / f"{PREFIX}-summary.json"
    text_path = OUTPUT_DIR / f"{PREFIX}.txt"
    with raw_path.open("w", encoding="utf-8") as handle:
        for event in all_events:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    summary_path.write_text(rendered, encoding="utf-8")
    text_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
