"""Reproduce deterministic mean-yield thresholds for the efficiency assay.

This is not a competition. Each run follows one parent while removing newborn
organisms before their next executable tick. Scaling packet E represents mean
capture yield f*E; it closes reserve/copy/provisioning ledgers but omits
capture variance.
"""

import argparse

from consts import (
    ALLOC, ALLOC_OFFSPRING, COPY_BLOCK, DIVIDE, FREE, JUMP, MOV,
    PACKET_SIZE, READ, TRANSFORM, TRANSFORM_RLE,
)
from engine import Simulation


def assay_genome(extent: int) -> list[tuple]:
    length = 14
    genome = [
        (MOV, 5, 51),
        (MOV, 6, length),
        (MOV, 0, PACKET_SIZE),
        (ALLOC, 0),
        (READ, 1, PACKET_SIZE),
        (TRANSFORM, TRANSFORM_RLE, 1, extent),
        (FREE, 1),
    ]
    for _ in range(2):
        genome.extend([
            (ALLOC_OFFSPRING, 64),
            (COPY_BLOCK,),
            (DIVIDE,),
        ])
    genome.append((JUMP, 2))
    assert len(genome) == length
    return genome


def isolated_parent(extent: int, effective_energy: float,
                    ticks: int) -> tuple[bool, float, float]:
    sim = Simulation(
        seed=123,
        phase_mode="monotonic_rich",
        packet_e_rich=effective_energy,
        packet_e_lean=effective_energy,
    )
    sim.substrate.add_organism(
        assay_genome(extent), lineage_label="TRACE_PARENT")

    last_pc = 0
    last_divides = 0
    offspring_per_cycle: list[int] = []

    for _ in range(ticks):
        sim.step()
        # Newborns do not enter the next tick's active list and cannot alter
        # packet capture or parent dynamics.
        for oid in [oid for oid in sim.substrate.organisms if oid != 0]:
            sim.substrate.remove_organism(oid, "derivation cleanup")
            del sim.substrate.organisms[oid]

        parent = sim.substrate.organisms.get(0)
        if parent is None or parent.state == "DEAD":
            return False, 0.0, 0.0

        if parent.pc == 2 and last_pc != 2 and sim.tick > 2:
            offspring_per_cycle.append(parent.total_divides - last_divides)
            last_divides = parent.total_divides
        last_pc = parent.pc

    parent = sim.substrate.organisms[0]
    tail = offspring_per_cycle[-50:]
    tail_k = sum(tail) / len(tail) if tail else 0.0
    return True, tail_k, parent.execution_reserve


def cycle_profile(extent: int, assay_energy: float) -> tuple[list[int], int]:
    """Measure recurrent PC=2 returns and peak memory from live execution."""
    sim = Simulation(
        seed=123,
        phase_mode="monotonic_rich",
        packet_e_rich=assay_energy,
        packet_e_lean=assay_energy,
    )
    parent = sim.substrate.add_organism(
        assay_genome(extent), lineage_label="TRACE_PARENT")
    starts: list[int] = []
    peak = parent.get_working_memory_size()
    last_pc = parent.pc
    for _ in range(80):
        sim.step()
        for oid in [oid for oid in sim.substrate.organisms if oid != 0]:
            sim.substrate.remove_organism(oid, "derivation cleanup")
            del sim.substrate.organisms[oid]
        parent = sim.substrate.organisms.get(0)
        if parent is None or parent.state == "DEAD":
            break
        peak = max(peak, parent.get_working_memory_size())
        if parent.pc == 2 and last_pc != 2 and sim.tick > 2:
            starts.append(sim.tick)
        last_pc = parent.pc
    return starts, peak


def first_cycle_discrete_capture(extent: int, captured: bool,
                                 assay_energy: float) -> tuple:
    """Trace one founder through its first cycle with one whole packet or none."""
    sim = Simulation(
        seed=123,
        phase_mode="monotonic_rich",
        packet_e_rich=assay_energy,
        packet_e_lean=assay_energy,
        packet_rate=1,
        buffer_depth=1,
        initial_buffer_packets=int(captured),
        population_cap=100,
    )
    # Freeze arrivals after the explicit initial standing packet treatment.
    sim.substrate.data_stream.packet_rate = 0
    parent = sim.substrate.add_organism(
        assay_genome(extent), lineage_label="TRACE_PARENT")
    for _ in range(14):
        sim.step()
        for oid in [oid for oid in sim.substrate.organisms if oid != parent.id]:
            sim.substrate.remove_organism(oid, "derivation cleanup")
            del sim.substrate.organisms[oid]
    parent_events = [
        row for row in sim.substrate.divide_event_log
        if row["parent_id"] == parent.id
    ]
    return (
        parent.state != "DEAD",
        parent.total_divides,
        parent.divide_attempts,
        sum(row["materialization_failure_reason"] is not None
            for row in parent_events),
        parent.execution_reserve,
    )


def threshold(extent: int, ticks: int, iterations: int,
              target_k: int | None) -> tuple[float, tuple]:
    lo, hi = 50.0, 800.0
    for _ in range(iterations):
        mid = (lo + hi) / 2
        result = isolated_parent(extent, mid, ticks)
        passes = result[0] if target_k is None else (
            result[0] and result[1] >= target_k)
        if passes:
            hi = mid
        else:
            lo = mid
    return hi, isolated_parent(extent, hi, ticks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticks", type=int, default=4000)
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--assay-energy", type=float, default=500.0)
    parser.add_argument("--packet-rate", type=int, default=11)
    parser.add_argument("--buffer-depth", type=int, default=132)
    parser.add_argument("--population-cap", type=int, default=155)
    parser.add_argument("--initial-buffer-packets", type=int, default=132)
    args = parser.parse_args()

    print("DERIVATION isolated_parent=true seed=123 bouts=2 genome_length=14 "
          f"tau_r5=51 ticks={args.ticks} iterations={args.iterations} "
          f"assay_energy={args.assay_energy}")
    design = Simulation(
        seed=123,
        phase_mode="monotonic_rich",
        packet_e_rich=args.assay_energy,
        packet_e_lean=args.assay_energy,
        packet_rate=args.packet_rate,
        buffer_depth=args.buffer_depth,
        population_cap=args.population_cap,
        initial_buffer_packets=args.initial_buffer_packets,
    )
    buffered = len(design.substrate.data_stream.buffer)
    successes = sum(
        design.substrate.data_stream.read() is not None
        for _ in range(args.population_cap))
    print(f"CAP_DESIGN packet_rate={args.packet_rate} "
          f"buffer_depth={args.buffer_depth} population_cap={args.population_cap} "
          f"initial_buffer_packets={args.initial_buffer_packets} "
          f"cycle_supply={buffered} burst_successes={successes} "
          f"f_eq={successes / args.population_cap:.12f}")
    for label, extent in (("FULL", 256), ("HALF", 128)):
        for captured in (True, False):
            alive, instantiations, attempts, materialization_failures, reserve = (
                first_cycle_discrete_capture(
                    extent, captured, args.assay_energy))
            print(f"{label} DISCRETE_CAPTURE captured={captured} "
                  f"alive={alive} instantiations={instantiations} "
                  f"attempts={attempts} "
                  f"materialization_failures={materialization_failures} "
                  f"reserve={reserve:.12f}")
        starts, peak = cycle_profile(extent, args.assay_energy)
        intervals = [b - a for a, b in zip(starts, starts[1:])]
        print(f"{label} cycle_starts={starts[:6]} "
              f"cycle_intervals={intervals[:5]} peak_memory={peak}")
        for name, target in (("parent_survival", None),
                             ("k_ge_1", 1), ("k_ge_2", 2)):
            energy, result = threshold(
                extent, args.ticks, args.iterations, target)
            print(
                f"{label} {name} effective_E={energy:.9f} "
                f"f_at_assay_E={energy / args.assay_energy:.9f} "
                f"alive={result[0]} tail_k={result[1]:.6f} "
                f"reserve={result[2]:.9f}")


if __name__ == "__main__":
    main()
