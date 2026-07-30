"""Historical paired established-parent response runner, updated for no-threshold semantics.

This is design calibration, not population or competition evidence. Offspring are
removed before execution by isolated_trial(), so outputs are instantiations and
parent survival—not offspring establishment. Historical threshold-18 artifacts
are parameter-stale and are not silently reinterpreted by this source update.
"""

from __future__ import annotations

from collections import defaultdict
import json
import random
from pathlib import Path

from derive_stochastic_efficiency import disable_mutation, isolated_trial, safe_ratio

P_GRID = (0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)
TRIALS = 2000
CYCLES = 40
BURN_CYCLES = 10
BOOTSTRAPS = 5000
OUTPUT_DIR = Path("/opt/data/avida-life")
PREFIX = "efficiency-capture-response"


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def arm_summary(rows: list[dict], label: str, p: float) -> dict:
    selected = [row for row in rows if row["label"] == label]
    person_ticks = sum(row["person_ticks_postburn"] for row in selected)
    instantiations = sum(row["instantiations_postburn"] for row in selected)
    attempts = sum(row["attempts_postburn"] for row in selected)
    materialization_failures = sum(
        row["materialization_failures_postburn"] for row in selected)
    captures = sum(row["captures_postburn"] for row in selected)
    reads = sum(row["reads_postburn"] for row in selected)
    postburn_deaths = sum(row["death_postburn"] for row in selected)
    return {
        "p_capture_target": p,
        "label": label,
        "paired_trials": len(selected),
        "postburn_parent_person_ticks": person_ticks,
        "postburn_offspring_instantiations": instantiations,
        "postburn_divide_attempts": attempts,
        "postburn_materialization_failures": materialization_failures,
        "postburn_parent_deaths": postburn_deaths,
        "instantiations_per_parent_tick": safe_ratio(
            instantiations, person_ticks),
        "materialization_failure_fraction": safe_ratio(
            materialization_failures, attempts),
        "realised_capture_fraction": safe_ratio(captures, reads),
        "survival_to_burn_fraction": sum(
            row["alive_at_burn"] for row in selected) / len(selected),
        "survival_to_end_fraction": sum(
            row["alive_at_end"] for row in selected) / len(selected),
        "postburn_parent_deaths_per_instantiation": safe_ratio(
            postburn_deaths, instantiations),
    }


def paired_bootstrap(rows: list[dict], p_index: int) -> dict:
    by_label = {
        label: {row["trial"]: row for row in rows if row["label"] == label}
        for label in ("FULL", "HALF")
    }
    trial_ids = sorted(by_label["FULL"])
    if trial_ids != sorted(by_label["HALF"]):
        raise RuntimeError("FULL/HALF trial pairing mismatch")
    rng = random.Random(91_000_000 + p_index)
    deltas = []
    for _ in range(BOOTSTRAPS):
        sampled = [rng.choice(trial_ids) for _ in trial_ids]
        rates = {}
        for label in ("FULL", "HALF"):
            instantiations = sum(
                by_label[label][trial]["instantiations_postburn"]
                for trial in sampled)
            person_ticks = sum(
                by_label[label][trial]["person_ticks_postburn"]
                for trial in sampled)
            rates[label] = (
                instantiations / person_ticks if person_ticks else 0.0)
        deltas.append(rates["FULL"] - rates["HALF"])
    return {
        "bootstrap_replicates": BOOTSTRAPS,
        "delta_instantiation_rate_ci95": [
            quantile(deltas, 0.025), quantile(deltas, 0.975)],
    }


def main() -> None:
    disable_mutation()
    rows: list[dict] = []
    by_p: dict[float, list[dict]] = defaultdict(list)

    # Common uniforms couple both arms and all p-grid points within a trial.
    uniforms = []
    for trial in range(TRIALS):
        rng = random.Random(9_000_000 + trial)
        uniforms.append([rng.random() for _ in range(CYCLES)])

    for p_index, p in enumerate(P_GRID):
        for trial in range(TRIALS):
            schedule = [value < p for value in uniforms[trial]]
            for label, extent in (("FULL", 256), ("HALF", 128)):
                row = isolated_trial(
                    label, extent, trial, schedule, CYCLES, BURN_CYCLES)
                row["p_capture_target"] = p
                row["schedule_seed"] = 9_000_000 + trial
                analysis_start = 4 + BURN_CYCLES * 12
                row["death_postburn"] = (
                    row["death_tick"] is not None and
                    row["death_tick"] >= analysis_start)
                rows.append(row)
                by_p[p].append(row)

    points = []
    for p_index, p in enumerate(P_GRID):
        full = arm_summary(by_p[p], "FULL", p)
        half = arm_summary(by_p[p], "HALF", p)
        delta = (full["instantiations_per_parent_tick"] -
                 half["instantiations_per_parent_tick"])
        bootstrap = paired_bootstrap(by_p[p], p_index)
        qualifies = (
            delta > 0 and
            full["postburn_parent_deaths_per_instantiation"] < 0.10 and
            half["postburn_parent_deaths_per_instantiation"] < 0.10)
        points.append({
            "p_capture_target": p,
            "FULL": full,
            "HALF": half,
            "delta_instantiations_per_parent_tick": delta,
            **bootstrap,
            "qualifies_as_provisional_response_point": qualifies,
        })

    qualifying = [point for point in points
                  if point["qualifies_as_provisional_response_point"]]
    candidate = None
    if qualifying:
        candidate = sorted(
            qualifying,
            key=lambda point: (-point["delta_instantiations_per_parent_tick"],
                               point["p_capture_target"]))[0]

    result = {
        "kind": "paired_established_parent_response_not_population_evidence",
        "parameters": {
            "p_grid": list(P_GRID),
            "paired_trials_per_p": TRIALS,
            "cycles": CYCLES,
            "burn_cycles": BURN_CYCLES,
            "bootstrap_replicates": BOOTSTRAPS,
            "mutation_rates": 0,
            "offspring_execute": False,
            "offspring_maturation_delay": 0,
            "packet_energy": 500,
        },
        "points": points,
        "provisional_candidate_p": (
            candidate["p_capture_target"] if candidate else None),
        "candidate_rule": (
            "largest positive FULL-HALF instantiation-rate difference among "
            "grid points with parent deaths/instantiation <0.10 in both arms; "
            "numeric ties choose lower p"),
        "scope": (
            "Requires separate queue/composition and offspring-cohort "
            "calibration before any mixed competition."),
    }

    raw_path = OUTPUT_DIR / f"{PREFIX}-raw.jsonl"
    summary_path = OUTPUT_DIR / f"{PREFIX}-summary.json"
    text_path = OUTPUT_DIR / f"{PREFIX}.txt"
    with raw_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    summary_path.write_text(rendered, encoding="utf-8")
    text_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
