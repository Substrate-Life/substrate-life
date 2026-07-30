"""Pre-competition sustained-recruitment calibration for the efficiency assay.

This script produces design predictions, not mixed-population evidence. It runs:
1. paired iid-capture isolated-parent lifetimes; and
2. mutation-free monomorphic cap calibrations in the exact assay ecology.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import random
import statistics
from pathlib import Path

import engine as engine_module
import organism as organism_module
from derive_efficiency_breakpoints import assay_genome
from engine import Simulation


P_CAPTURE = 132 / 155
FIRST_READ_TICK = 4
CYCLE_TICKS = 12


def disable_mutation() -> None:
    engine_module.MUTATION_SUBSTITUTION = 0.0
    organism_module.MUTATION_INSERTION = 0.0
    organism_module.MUTATION_DELETION = 0.0
    organism_module.MUTATION_DUPLICATION = 0.0


def safe_ratio(num: float, den: float) -> float | None:
    return num / den if den else None


def isolated_trial(label: str, extent: int, trial: int,
                   schedule: list[bool], cycles: int,
                   burn_cycles: int) -> dict:
    sim = Simulation(
        seed=1_000_000 + trial,
        phase_mode="monotonic_rich",
        packet_e_rich=500,
        packet_e_lean=500,
        packet_rate=1,
        buffer_depth=1,
        population_cap=100,
    )
    stream = sim.substrate.data_stream
    stream.packet_rate = 0
    stream.buffer.clear()
    parent = sim.substrate.add_organism(
        assay_genome(extent), lineage_label=label)
    parent_id = parent.id
    analysis_start = FIRST_READ_TICK + burn_cycles * CYCLE_TICKS
    final_tick = FIRST_READ_TICK + cycles * CYCLE_TICKS - 1
    read_index = 0
    person_ticks_post = 0
    alive_at_burn = False

    while sim.tick <= final_tick and parent.state != "DEAD":
        if sim.tick == analysis_start:
            alive_at_burn = True
        if sim.tick >= analysis_start:
            person_ticks_post += 1
        if parent.pc == 4:
            capture = schedule[read_index] if read_index < len(schedule) else False
            read_index += 1
            if capture:
                stream.buffer.append(
                    stream.stream.generate_packet(stream.current_tick))
        sim.step()
        # Offspring never execute in this isolated-parent calibration.
        for oid in [oid for oid in sim.substrate.organisms if oid != parent_id]:
            sim.substrate.remove_organism(oid, "calibration cleanup")
            del sim.substrate.organisms[oid]

    events = [event for event in sim.substrate.divide_event_log
              if event["parent_id"] == parent_id]
    events_post = [event for event in events
                   if event["tick"] >= analysis_start]
    reads_post = [row for row in sim.substrate.capture_history
                  if row["tick"] >= analysis_start and
                  row["valid_read_attempts"]]
    death_tick = next(
        (row["death_tick"] for row in sim.substrate.ancestry
         if row["id"] == parent_id), None)
    return {
        "mode": "isolated_iid",
        "realised_parameters": sim.realised_parameters(),
        "trial": trial,
        "label": label,
        "extent": extent,
        "cycles_planned": cycles,
        "cycles_read": read_index,
        "alive_at_burn": alive_at_burn,
        "alive_at_end": parent.state != "DEAD",
        "death_tick": death_tick,
        "person_ticks_postburn": person_ticks_post,
        "attempts_postburn": len(events_post),
        "instantiations_postburn": sum(
            event["offspring_instantiated"] for event in events_post),
        "materialization_failures_postburn": sum(
            event["materialization_failure_reason"] is not None
            for event in events_post),
        "captures_postburn": sum(row["capture_successes"] for row in reads_post),
        "reads_postburn": sum(row["valid_read_attempts"] for row in reads_post),
        "end_reserve": parent.execution_reserve,
    }


def monomorphic_trial(label: str, seed: int, cycles: int,
                      burn_cycles: int,
                      maturation_delay: int) -> dict:
    sim = Simulation(
        seed=seed,
        phase_mode="monotonic_rich",
        packet_e_rich=500,
        packet_e_lean=500,
        packet_rate=11,
        buffer_depth=132,
        population_cap=155,
        initial_buffer_packets=132,
        offspring_maturation_delay=maturation_delay,
    )
    if label == "FULL":
        sim.seed_efficiency_assay_founders(full_count=155, half_count=0)
    else:
        sim.seed_efficiency_assay_founders(full_count=0, half_count=155)

    analysis_start = FIRST_READ_TICK + burn_cycles * CYCLE_TICKS
    final_tick = FIRST_READ_TICK + cycles * CYCLE_TICKS - 1
    organism_ticks = 0
    for _ in range(final_tick + 1):
        tick = sim.tick
        start_population = sum(
            org.state != "DEAD" for org in sim.substrate.organisms.values())
        sim.step()
        if analysis_start <= tick <= final_tick:
            organism_ticks += start_population

    history = [row for row in sim.substrate.capture_history
               if analysis_start <= row["tick"] <= final_tick]
    events = [row for row in sim.substrate.divide_event_log
              if analysis_start <= row["tick"] <= final_tick and
              row["lineage_label"] == label]
    replacements = [row for row in sim.substrate.cap_replacement_log
                    if analysis_start <= row["tick"] <= final_tick and
                    row["parent_lineage_label"] == label]
    read_events = [row for row in sim.substrate.read_event_log
                   if analysis_start <= row["tick"] <= final_tick and
                   row["lineage_label"] == label]
    deaths = [row for row in sim.substrate.ancestry
              if analysis_start <= row["death_tick"] <= final_tick and
              row["lineage_label"] == label]
    instantiations = sum(row["offspring_instantiated"] for row in events)
    materialization_failures = sum(
        row["materialization_failure_reason"] is not None for row in events)
    attempts = len(events)
    nondisplacement = sum(row["cause"] != "displacement" for row in deaths)
    nondisplacement_by_stage = Counter(
        row["death_stage"] for row in deaths
        if row["cause"] != "displacement")
    all_deaths_by_stage = Counter(row["death_stage"] for row in deaths)
    first_read_ages = [row["age"] for row in read_events
                       if row["is_first_valid_read"]]
    recurrent_intervals = [row["read_interval"] for row in read_events
                           if not row["is_first_valid_read"]]
    live_displacements = sum(row["victim_was_live"] for row in replacements)
    vacancy_fills = len(replacements) - live_displacements
    live_replacements = [row for row in replacements if row["victim_was_live"]]
    displacement_outcomes = Counter(
        row["causing_offspring_outcome"] for row in live_replacements)
    doomed_live_displacements = displacement_outcomes[
        "died_before_first_extraction"]
    reserves = [org.execution_reserve for org in sim.substrate.organisms.values()
                if org.state != "DEAD"]
    return {
        "mode": "monomorphic_cap",
        "seed": seed,
        "label": label,
        "cycles": cycles,
        "burn_cycles": burn_cycles,
        "offspring_maturation_delay": maturation_delay,
        "realised_parameters": sim.realised_parameters(),
        "analysis_start": analysis_start,
        "analysis_end": final_tick,
        "organism_ticks": organism_ticks,
        "attempts": attempts,
        "offspring_instantiations": instantiations,
        "materialization_failures": materialization_failures,
        "all_age_nondisplacement_deaths": nondisplacement,
        "nondisplacement_deaths_by_stage": dict(nondisplacement_by_stage),
        "all_deaths_by_stage": dict(all_deaths_by_stage),
        "live_displacements": live_displacements,
        "vacancy_fills": vacancy_fills,
        "parent_victim_displacements": sum(
            row["victim_is_reproducing_parent"] for row in replacements),
        "doomed_offspring_live_displacements": doomed_live_displacements,
        "doomed_offspring_fraction_of_live_displacements": safe_ratio(
            doomed_live_displacements, len(live_replacements)),
        "unresolved_causing_offspring_live_displacements": (
            displacement_outcomes["unresolved"]),
        "causing_offspring_live_displacement_outcomes": dict(
            displacement_outcomes),
        "pending_divides_preempted": sum(
            row["victim_pending_divide"] for row in replacements),
        "captures": sum(row["capture_successes"] for row in history),
        "reads": sum(row["valid_read_attempts"] for row in history),
        "first_read_events": len(first_read_ages),
        "mean_birth_to_first_read": (
            statistics.mean(first_read_ages) if first_read_ages else None),
        "recurrent_read_events": len(recurrent_intervals),
        "mean_recurrent_read_interval": (
            statistics.mean(recurrent_intervals)
            if recurrent_intervals else None),
        "minimum_population": min(row["population"] for row in history),
        "end_population": len(reserves),
        "allocation_failures":
            sim.substrate.memory_allocation_failures_total,
        "mean_end_reserve": statistics.mean(reserves) if reserves else None,
        "median_end_reserve": statistics.median(reserves) if reserves else None,
    }


def aggregate(rows: list[dict], mode: str, label: str) -> dict:
    selected = [row for row in rows
                if row["mode"] == mode and row["label"] == label]
    if mode == "isolated_iid":
        eligible = [row for row in selected if row["alive_at_burn"]]
        person_ticks = sum(row["person_ticks_postburn"] for row in eligible)
        attempts = sum(row["attempts_postburn"] for row in eligible)
        instantiations = sum(
            row["instantiations_postburn"] for row in eligible)
        materialization_failures = sum(
            row["materialization_failures_postburn"] for row in eligible)
        deaths = sum(not row["alive_at_end"] for row in eligible)
        return {
            "mode": mode,
            "label": label,
            "trials": len(selected),
            "survived_to_burn": len(eligible),
            "survival_to_burn_fraction": safe_ratio(len(eligible), len(selected)),
            "postburn_person_ticks": person_ticks,
            "postburn_offspring_instantiations": instantiations,
            "postburn_attempts": attempts,
            "postburn_materialization_failures": materialization_failures,
            "postburn_deaths": deaths,
            "instantiations_per_organism_tick": safe_ratio(
                instantiations, person_ticks),
            "materialization_failure_fraction": safe_ratio(
                materialization_failures, attempts),
            "deaths_per_organism_tick": safe_ratio(deaths, person_ticks),
        }

    organism_ticks = sum(row["organism_ticks"] for row in selected)
    attempts = sum(row["attempts"] for row in selected)
    instantiations = sum(
        row["offspring_instantiations"] for row in selected)
    materialization_failures = sum(
        row["materialization_failures"] for row in selected)
    deaths = sum(row["all_age_nondisplacement_deaths"] for row in selected)
    stage_counts = Counter()
    all_stage_counts = Counter()
    for row in selected:
        stage_counts.update(row["nondisplacement_deaths_by_stage"])
        all_stage_counts.update(row["all_deaths_by_stage"])
    all_live_displacements = sum(
        row["live_displacements"] for row in selected)
    doomed_live_displacements = sum(
        row["doomed_offspring_live_displacements"] for row in selected)
    return {
        "mode": mode,
        "label": label,
        "seeds": len(selected),
        "organism_ticks": organism_ticks,
        "offspring_instantiations": instantiations,
        "attempts": attempts,
        "materialization_failures": materialization_failures,
        "all_age_nondisplacement_deaths": deaths,
        "nondisplacement_deaths_by_stage": dict(stage_counts),
        "all_deaths_by_stage": dict(all_stage_counts),
        "live_displacements": sum(row["live_displacements"] for row in selected),
        "vacancy_fills": sum(row["vacancy_fills"] for row in selected),
        "parent_victim_displacements": sum(
            row["parent_victim_displacements"] for row in selected),
        "doomed_offspring_live_displacements": doomed_live_displacements,
        "doomed_offspring_fraction_of_live_displacements": safe_ratio(
            doomed_live_displacements, all_live_displacements),
        "unresolved_causing_offspring_live_displacements": sum(
            row["unresolved_causing_offspring_live_displacements"]
            for row in selected),
        "pending_divides_preempted": sum(
            row["pending_divides_preempted"] for row in selected),
        "allocation_failures": sum(row["allocation_failures"] for row in selected),
        "instantiations_per_organism_tick": safe_ratio(
            instantiations, organism_ticks),
        "materialization_failure_fraction": safe_ratio(
            materialization_failures, attempts),
        "all_age_nondisplacement_deaths_per_instantiation": safe_ratio(
            deaths, instantiations),
        "established_nondisplacement_deaths_per_instantiation": safe_ratio(
            stage_counts["post_first_offspring_instantiation"],
            instantiations),
        "pre_extraction_nondisplacement_deaths": (
            stage_counts["pre_first_extraction"]),
        "capture_fraction": safe_ratio(
            sum(row["captures"] for row in selected),
            sum(row["reads"] for row in selected)),
        "minimum_population": min(row["minimum_population"] for row in selected),
        "mean_birth_to_first_read": safe_ratio(
            sum(row["mean_birth_to_first_read"] * row["first_read_events"]
                for row in selected if row["first_read_events"]),
            sum(row["first_read_events"] for row in selected)),
        "mean_recurrent_read_interval": safe_ratio(
            sum(row["mean_recurrent_read_interval"] *
                row["recurrent_read_events"]
                for row in selected if row["recurrent_read_events"]),
            sum(row["recurrent_read_events"] for row in selected)),
        "mean_seed_instantiation_rate": statistics.mean(
            row["offspring_instantiations"] / row["organism_ticks"]
            for row in selected),
        "sd_seed_instantiation_rate": statistics.stdev(
            row["offspring_instantiations"] / row["organism_ticks"]
            for row in selected),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--isolated-trials", type=int, default=2000)
    parser.add_argument("--mono-seeds", type=int, default=20)
    parser.add_argument("--cycles", type=int, default=40)
    parser.add_argument("--burn-cycles", type=int, default=10)
    parser.add_argument("--maturation-delay", type=int, default=0)
    parser.add_argument(
        "--output-prefix", default="efficiency-stochastic-calibration")
    parser.add_argument("--output-dir", default="/opt/data/avida-life")
    args = parser.parse_args()
    disable_mutation()

    rows: list[dict] = []
    for trial in range(args.isolated_trials):
        rng = random.Random(8_000_000 + trial)
        schedule = [rng.random() < P_CAPTURE for _ in range(args.cycles)]
        rows.append(isolated_trial(
            "FULL", 256, trial, schedule, args.cycles, args.burn_cycles))
        rows.append(isolated_trial(
            "HALF", 128, trial, schedule, args.cycles, args.burn_cycles))

    for index in range(args.mono_seeds):
        seed = 20_000 + index
        rows.append(monomorphic_trial(
            "FULL", seed, args.cycles, args.burn_cycles,
            args.maturation_delay))
        rows.append(monomorphic_trial(
            "HALF", seed, args.cycles, args.burn_cycles,
            args.maturation_delay))

    summaries = [aggregate(rows, mode, label)
                 for mode in ("isolated_iid", "monomorphic_cap")
                 for label in ("FULL", "HALF")]
    mono = {row["label"]: row for row in summaries
            if row["mode"] == "monomorphic_cap"}
    b_full = mono["FULL"]["instantiations_per_organism_tick"]
    b_half = mono["HALF"]["instantiations_per_organism_tick"]
    p0 = 78 / 155
    logit0 = math.log(p0 / (1 - p0))
    p12 = 1 / (1 + math.exp(-(logit0 + CYCLE_TICKS * (b_full - b_half))))
    delta_p12 = p12 - p0
    census_sd = math.sqrt(p0 * (1 - p0) / 155)
    if abs(delta_p12) >= 3 * 0.0402:
        readiness = "THREE_SD_OR_LARGER"
    elif abs(delta_p12) < 0.0402:
        readiness = "BELOW_ONE_SD_DO_NOT_RUN_60_TICKS"
    else:
        readiness = "ONE_TO_THREE_SD_REQUIRE_POWER_CALIBRATION"

    result = {
        "kind": "precompetition_design_calibration_not_competition_evidence",
        "parameters": {
            "p_capture_iid": P_CAPTURE,
            "isolated_trials": args.isolated_trials,
            "monomorphic_seeds_per_arm": args.mono_seeds,
            "cycles": args.cycles,
            "burn_cycles": args.burn_cycles,
            "analysis_start_tick": FIRST_READ_TICK + args.burn_cycles * CYCLE_TICKS,
            "analysis_end_tick": FIRST_READ_TICK + args.cycles * CYCLE_TICKS - 1,
            "mutation_rates": 0,
            "packet_rate": 11,
            "buffer_depth": 132,
            "initial_buffer_packets": 132,
            "population_cap": 155,
            "offspring_maturation_delay": args.maturation_delay,
        },
        "summaries": summaries,
        "heuristic": {
            "p0": p0,
            "b_full": b_full,
            "b_half": b_half,
            "delta_instantiation_rate": b_full - b_half,
            "p_after_12_ticks": p12,
            "delta_p_12": delta_p12,
            "census_binomial_sd": census_sd,
            "delta_p_12_in_census_sd": delta_p12 / census_sd,
            "readiness": readiness,
        },
    }

    output_dir = Path(args.output_dir)
    raw_path = output_dir / f"{args.output_prefix}-raw.jsonl"
    summary_path = output_dir / f"{args.output_prefix}-summary.json"
    with raw_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    summary_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"RAW_PATH {raw_path}")
    print(f"SUMMARY_PATH {summary_path}")


if __name__ == "__main__":
    main()
