"""Registered mutation-free capped-population calibration for p=1 fecundity.

Monomorphic design calibration only. This runner does not execute a mixed assay.
"""

from __future__ import annotations

from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import statistics

import engine as engine_module
import organism as organism_module
from consts import PACKET_SIZE, SHARED_MEMORY_POOL
from derive_stochastic_efficiency import disable_mutation
from engine import Simulation, conditional_efficiency_assay_genome

ROOT = Path("/opt/data/avida-life")
OUT_DIR = ROOT / "efficiency-conditional-population-calibration-raw"
PREFIX = "efficiency-conditional-population-calibration"
TICKS = 2040
COHORT_START = 170
COHORT_STOP = 340
CAP = 155
PACKET_RATE = 20
BUFFER_DEPTH = 340
INITIAL_QUEUE = 340
TAU_R5 = 51
SEEDS = {
    "FULL": list(range(61001, 61006)),
    "HALF": list(range(62001, 62006)),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_manifest() -> dict:
    paths = [
        ROOT / "src" / "run_conditional_population_calibration.py",
        ROOT / "src" / "test_population_calibration_runner.py",
        ROOT / "src" / "engine.py",
        ROOT / "src" / "organism.py",
        ROOT / "src" / "consts.py",
        ROOT / "src" / "transforms.py",
        ROOT / "src" / "datastream.py",
        ROOT / "efficiency-assay-preregistration.md",
    ]
    return {
        str(path.relative_to(ROOT)): {
            "sha256": sha256(path),
            "mtime_ns": path.stat().st_mtime_ns,
            "size": path.stat().st_size,
        }
        for path in paths
    }


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def json_safe(value):
    """Recursively convert telemetry to deterministic JSON-compatible values."""
    if isinstance(value, dict):
        return {
            (key if isinstance(key, str) else repr(key)): json_safe(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def mutation_readback() -> dict:
    names = [
        "MUTATION_SUBSTITUTION", "MUTATION_INSERTION",
        "MUTATION_DELETION", "MUTATION_DUPLICATION",
    ]
    return {
        module.__name__: {name: getattr(module, name) for name in names}
        for module in (engine_module, organism_module)
    }


def build_cohort(sim: Simulation) -> list[dict]:
    births = {
        row["id"]: row for row in sim.substrate.birth_log
        if row["parent"] != -1 and
        COHORT_START <= row["birth_tick"] < COHORT_STOP
    }
    deaths = {row["id"]: row for row in sim.substrate.ancestry}
    first_reads = {
        row["organism_id"]: row for row in sim.substrate.read_event_log
        if row["is_first_valid_read"] and row["organism_id"] in births
    }
    rows = []
    for oid, birth in sorted(births.items()):
        death = deaths.get(oid)
        living = sim.substrate.organisms.get(oid)
        if death is not None:
            k = death["divides"]
            attempts = death["divide_attempts"]
            first_divide_tick = death["first_divide_tick"]
            endpoint = "death"
            death_tick = death["death_tick"]
            cause = death["cause"]
            death_stage = death["death_stage"]
        elif living is not None and living.state != "DEAD":
            k = living.total_divides
            attempts = living.divide_attempts
            first_divide_tick = living.first_divide_tick
            endpoint = "censored_alive"
            death_tick = None
            cause = None
            death_stage = None
        else:
            k = None
            attempts = None
            first_divide_tick = None
            endpoint = "unaccounted"
            death_tick = None
            cause = None
            death_stage = None
        first_read = first_reads.get(oid)
        rows.append({
            "id": oid,
            "parent": birth["parent"],
            "generation": birth["generation"],
            "lineage_label": birth["lineage_label"],
            "birth_tick": birth["birth_tick"],
            "birth_reserve": birth["birth_reserve"],
            "endpoint": endpoint,
            "death_tick": death_tick,
            "death_age": (death_tick - birth["birth_tick"]
                          if death_tick is not None else None),
            "death_cause": cause,
            "death_stage": death_stage,
            "first_valid_read_tick": (first_read["tick"]
                                      if first_read else None),
            "first_valid_read_age": (first_read["age"]
                                     if first_read else None),
            "first_live_birth_tick": first_divide_tick,
            "first_live_birth_age": (
                first_divide_tick - birth["birth_tick"]
                if first_divide_tick is not None else None),
            "lifetime_live_births": k,
            "lifetime_divide_attempts": attempts,
        })
    return rows


def summarize_cohort(rows: list[dict]) -> dict:
    completed = [row for row in rows if row["endpoint"] == "death"]
    censored = [row for row in rows if row["endpoint"] == "censored_alive"]
    unaccounted = [row for row in rows if row["endpoint"] == "unaccounted"]
    k = [row["lifetime_live_births"] for row in completed]
    lifetimes = [row["death_age"] for row in completed]
    first_read_ages = [row["first_valid_read_age"] for row in completed
                       if row["first_valid_read_age"] is not None]
    first_birth_ages = [row["first_live_birth_age"] for row in completed
                        if row["first_live_birth_age"] is not None]
    k_mean = mean(k)
    k_var = statistics.pvariance(k) if k else None
    ne_var = (
        CAP / (1 + k_var / k_mean)
        if k_mean is not None and k_mean > 0 and k_var is not None
        else None)
    return {
        "cohort_n": len(rows),
        "complete_deaths": len(completed),
        "censored_alive": len(censored),
        "unaccounted": len(unaccounted),
        "unresolved_fraction": (
            (len(censored) + len(unaccounted)) / len(rows) if rows else None),
        "ever_live_birth_fraction_complete": (
            sum(value > 0 for value in k) / len(k) if k else None),
        "first_valid_read_fraction_complete": (
            len(first_read_ages) / len(completed) if completed else None),
        "lifetime_live_births_mean": k_mean,
        "lifetime_live_births_variance_population": k_var,
        "lifetime_live_births_distribution": {
            str(key): value for key, value in sorted(Counter(k).items())
        },
        "Ne_variance_heuristic": ne_var,
        "death_age_mean": mean(lifetimes),
        "death_age_median": median(lifetimes),
        "first_valid_read_age_mean_among_readers": mean(first_read_ages),
        "first_valid_read_age_median_among_readers": median(first_read_ages),
        "first_live_birth_age_mean_among_reproducers": mean(first_birth_ages),
        "first_live_birth_age_median_among_reproducers": median(first_birth_ages),
        "death_causes": dict(sorted(Counter(
            row["death_cause"] for row in completed).items())),
        "death_stages": dict(sorted(Counter(
            row["death_stage"] for row in completed).items())),
    }


def run_seed(label: str, seed: int, manifest: dict) -> tuple[dict, list[dict]]:
    extent = PACKET_SIZE if label == "FULL" else 128
    sim = Simulation(
        seed=seed,
        phase_mode="monotonic_rich",
        packet_e_rich=500,
        packet_e_lean=500,
        packet_rate=PACKET_RATE,
        buffer_depth=BUFFER_DEPTH,
        population_cap=CAP,
        initial_buffer_packets=INITIAL_QUEUE,
        offspring_maturation_delay=0,
    )
    genome = conditional_efficiency_assay_genome(extent, tau_r5=TAU_R5)
    for _ in range(CAP):
        org = sim.substrate.add_organism(genome, lineage_label=label)
        if org is None:
            raise RuntimeError("failed to seed direct-cap founder")
    realised_initial = sim.realised_parameters()
    tick_rows = []
    ledger_failures = []
    for _ in range(TICKS):
        sim.step()
        capture = dict(sim.substrate.capture_history[-1])
        live_allocations = sum(
            org.get_working_memory_size()
            for org in sim.substrate.organisms.values())
        corpse_allocations = sum(size for size, _tick in
                                 sim.substrate.corpse_pool)
        ledger_total = (
            sim.substrate.shared_memory_pool + live_allocations +
            corpse_allocations)
        if ledger_total != sim.substrate.initial_shared_memory_pool:
            ledger_failures.append({
                "tick": capture["tick"],
                "ledger_total": ledger_total,
            })
        capture.update({
            "live_allocation_bytes": live_allocations,
            "corpse_allocation_bytes": corpse_allocations,
            "ledger_total": ledger_total,
        })
        tick_rows.append(capture)

    cohort = build_cohort(sim)
    cohort_summary = summarize_cohort(cohort)
    organism_ticks = sum(row["population"] for row in tick_rows)
    births = [row for row in sim.substrate.birth_log if row["parent"] != -1]
    divide_events = sim.substrate.divide_event_log
    transform_events = sim.substrate.transform_event_log
    r4_values = sorted(set(row["r4"] for row in transform_events))
    non_displacement = [row for row in sim.substrate.ancestry
                        if row["cause"] != "displacement"]
    cap_events = sim.substrate.cap_replacement_log
    capture_attempts = sim.substrate.capture_attempts_total
    capture_successes = sim.substrate.capture_successes_total
    min_free_pool = min(row["shared_memory_pool"] for row in tick_rows)
    valid = {
        "population_always_cap": all(row["population"] == CAP
                                     for row in tick_rows),
        "capture_fraction_one": (
            capture_attempts > 0 and capture_attempts == capture_successes),
        "invalid_reads_zero": sim.substrate.invalid_read_attempts_total == 0,
        "stillbirths_zero": sim.substrate.stillbirths == 0,
        "non_displacement_deaths_zero": len(non_displacement) == 0,
        "allocation_failures_zero":
            sim.substrate.memory_allocation_failures_total == 0,
        "free_pool_margin": min_free_pool >= 8192,
        "memory_ledger_exact": len(ledger_failures) == 0,
        "r4_mask_correct": (
            bool(r4_values) and
            all((value & 2048) == (2048 if label == "FULL" else 0)
                for value in r4_values)),
        "parent_never_victim": all(
            row["parent_id"] != row["victim_id"] for row in cap_events),
    }
    summary = {
        "label": label,
        "seed": seed,
        "valid": all(valid.values()),
        "validity_gates": valid,
        "realised_parameters_initial": realised_initial,
        "realised_parameters_final": sim.realised_parameters(),
        "mutation_readback": mutation_readback(),
        "source_manifest": manifest,
        "genome_length": len(genome),
        "tau_r5": TAU_R5,
        "ticks": TICKS,
        "cohort_window": [COHORT_START, COHORT_STOP],
        "organism_ticks": organism_ticks,
        "offspring_live_births": len(births),
        "live_births_per_organism_tick": len(births) / organism_ticks,
        "divide_attempts": len(divide_events),
        "successful_divides": sum(row["success"] for row in divide_events),
        "stillbirth_divides": sum(row["stillbirth"] for row in divide_events),
        "divide_attempts_per_organism_tick": len(divide_events) / organism_ticks,
        "p_live_birth_given_attempt": (
            sum(row["success"] for row in divide_events) / len(divide_events)
            if divide_events else None),
        "deaths_total": len(sim.substrate.ancestry),
        "non_displacement_deaths": len(non_displacement),
        "live_cap_displacements": sum(row["victim_was_live"]
                                      for row in cap_events),
        "vacancy_fills": sum(not row["victim_was_live"]
                             for row in cap_events),
        "capture_attempts": capture_attempts,
        "capture_successes": capture_successes,
        "capture_fraction": capture_successes / capture_attempts,
        "r4_values": r4_values,
        "minimum_queue_occupancy_after_tick": min(
            row["buffer_occupancy"] for row in tick_rows),
        "minimum_free_pool": min_free_pool,
        "maximum_committed_memory": max(
            row["committed_memory"] for row in tick_rows),
        "maximum_live_allocation_bytes": max(
            row["live_allocation_bytes"] for row in tick_rows),
        "maximum_corpse_allocation_bytes": max(
            row["corpse_allocation_bytes"] for row in tick_rows),
        "allocation_failures": sim.substrate.memory_allocation_failures_total,
        "ledger_failure_count": len(ledger_failures),
        "cohort": cohort_summary,
    }
    raw = {
        "summary": summary,
        "cohort_records": cohort,
        "tick_records": tick_rows,
        "birth_log": sim.substrate.birth_log,
        "death_ancestry_log": sim.substrate.ancestry,
        "read_event_log": sim.substrate.read_event_log,
        "transform_event_log": transform_events,
        "divide_event_log": divide_events,
        "cap_replacement_log": cap_events,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = OUT_DIR / f"{label.lower()}-seed-{seed}.json.gz"
    with raw_path.open("wb") as binary_handle:
        with gzip.GzipFile(fileobj=binary_handle, mode="wb", mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8") as handle:
                json.dump(json_safe(raw), handle, sort_keys=True,
                          separators=(",", ":"))
    summary["raw_artifact"] = {
        "path": str(raw_path.relative_to(ROOT)),
        "sha256": sha256(raw_path),
        "size": raw_path.stat().st_size,
        "mtime_ns": raw_path.stat().st_mtime_ns,
    }
    return summary, cohort


def aggregate(label: str, seed_summaries: list[dict],
              cohorts: list[dict]) -> dict:
    cohort_summary = summarize_cohort(cohorts)
    return {
        "label": label,
        "seeds": [row["seed"] for row in seed_summaries],
        "all_seeds_mechanically_valid": all(row["valid"]
                                             for row in seed_summaries),
        "cohort": cohort_summary,
        "cohort_size_gate": cohort_summary["cohort_n"] >= 1000,
        "cohort_resolution_gate": (
            cohort_summary["unresolved_fraction"] is not None and
            cohort_summary["unresolved_fraction"] <= 0.01),
        "seed_metrics": seed_summaries,
    }


def main() -> None:
    disable_mutation()
    manifest = source_manifest()
    summaries = []
    cohorts_by_label = {"FULL": [], "HALF": []}
    for label in ("FULL", "HALF"):
        for seed in SEEDS[label]:
            summary, cohort = run_seed(label, seed, manifest)
            summaries.append(summary)
            cohorts_by_label[label].extend(cohort)
            print(json.dumps({
                "label": label, "seed": seed,
                "valid": summary["valid"],
                "cohort_n": summary["cohort"]["cohort_n"],
                "min_free_pool": summary["minimum_free_pool"],
            }, sort_keys=True), flush=True)

    treatment = [
        aggregate(label,
                  [row for row in summaries if row["label"] == label],
                  cohorts_by_label[label])
        for label in ("FULL", "HALF")
    ]
    result = {
        "kind": "mutation_free_monomorphic_capped_design_calibration",
        "mixed_population_run": False,
        "parameters": {
            "ticks": TICKS,
            "cohort_window": [COHORT_START, COHORT_STOP],
            "cap": CAP,
            "packet_rate": PACKET_RATE,
            "buffer_depth": BUFFER_DEPTH,
            "initial_queue": INITIAL_QUEUE,
            "tau_r5": TAU_R5,
            "seeds": SEEDS,
        },
        "source_manifest": manifest,
        "treatments": treatment,
        "overall_go_for_mixed_design_only": all(
            row["all_seeds_mechanically_valid"] and
            row["cohort_size_gate"] and row["cohort_resolution_gate"]
            for row in treatment),
    }
    summary_path = ROOT / f"{PREFIX}-summary.json"
    text_path = ROOT / f"{PREFIX}.txt"
    index_path = ROOT / f"{PREFIX}-seed-index.jsonl"
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    summary_path.write_text(rendered, encoding="utf-8")
    text_path.write_text(rendered, encoding="utf-8")
    with index_path.open("w", encoding="utf-8") as handle:
        for row in summaries:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    print(rendered, end="")


if __name__ == "__main__":
    main()
