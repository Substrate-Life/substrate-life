"""Verify the direct-cap efficiency-assay initialization; stop before DIVIDE."""

from collections import Counter

from engine import Simulation


def main() -> None:
    sim = Simulation(
        seed=201,
        phase_mode="monotonic_rich",
        packet_e_rich=500,
        packet_e_lean=500,
        packet_rate=11,
        buffer_depth=132,
        population_cap=155,
        initial_buffer_packets=132,
    )
    ids = sim.seed_efficiency_assay_founders()
    labels = Counter(sim.substrate.organisms[oid].lineage_label for oid in ids)
    print(sim.realised_parameter_header())
    print(sim.realised_memory_capacity_header(320))
    print(
        "INITIAL"
        f" population={len(ids)} FULL={labels['FULL']} HALF={labels['HALF']}"
        f" queue={len(sim.substrate.data_stream.buffer)}"
        f" free_memory={sim.substrate.shared_memory_pool}"
        f" allocation_failures={sim.substrate.memory_allocation_failures_total}"
    )

    for _ in range(6):
        sim.step()

    reads = [row for row in sim.substrate.capture_history
             if row["valid_read_attempts"]]
    extents = Counter(org.last_transform_extent
                      for org in sim.substrate.organisms.values())
    print(
        "PRE_DIVIDE"
        f" simulation_ticks={sim.tick} population={len(sim.substrate.organisms)}"
        f" FULL_expressed={extents[256]} HALF_expressed={extents[128]}"
        f" divide_events={len(sim.substrate.divide_event_log)}"
        f" cap_events={len(sim.substrate.cap_replacement_log)}"
        f" allocation_failures={sim.substrate.memory_allocation_failures_total}"
    )
    for row in reads:
        print(
            "READ"
            f" tick={row['tick']} attempts={row['valid_read_attempts']}"
            f" captures={row['capture_successes']}"
            f" f={row['capture_fraction']:.12f}"
            f" queue_after={row['buffer_occupancy']}"
        )

    assert len(ids) == 155 and labels == {"FULL": 78, "HALF": 77}
    assert len(reads) == 1
    assert reads[0]["tick"] == 4
    assert reads[0]["valid_read_attempts"] == 155
    assert reads[0]["capture_successes"] == 132
    assert extents[256] == 78 and extents[128] == 77
    assert len(sim.substrate.divide_event_log) == 0
    assert sim.substrate.memory_allocation_failures_total == 0


if __name__ == "__main__":
    main()
