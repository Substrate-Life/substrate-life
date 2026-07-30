"""Post-hoc p=1 no-miss control for the capture-response mechanism."""

from __future__ import annotations

import json
from pathlib import Path

from derive_efficiency_capture_response import (
    BURN_CYCLES,
    CYCLES,
    TRIALS,
    arm_summary,
    paired_bootstrap,
)
from derive_stochastic_efficiency import disable_mutation, isolated_trial

OUTPUT_DIR = Path("/opt/data/avida-life")
PREFIX = "efficiency-capture-response-p1-posthoc"


def main() -> None:
    disable_mutation()
    schedule = [True] * CYCLES
    rows = []
    analysis_start = 4 + BURN_CYCLES * 12
    for trial in range(TRIALS):
        for label, extent in (("FULL", 256), ("HALF", 128)):
            row = isolated_trial(
                label, extent, trial, schedule, CYCLES, BURN_CYCLES)
            row["p_capture_target"] = 1.0
            row["schedule_kind"] = "all_capture_posthoc_control"
            row["death_postburn"] = (
                row["death_tick"] is not None and
                row["death_tick"] >= analysis_start)
            rows.append(row)

    full = arm_summary(rows, "FULL", 1.0)
    half = arm_summary(rows, "HALF", 1.0)
    delta = (full["live_births_per_parent_tick"] -
             half["live_births_per_parent_tick"])
    result = {
        "kind": "posthoc_no_miss_mechanism_control_not_selection_evidence",
        "parameters": {
            "p_capture": 1.0,
            "paired_trials": TRIALS,
            "cycles": CYCLES,
            "burn_cycles": BURN_CYCLES,
            "mutation_rates": 0,
            "offspring_execute": False,
            "schedule": "all captures",
        },
        "FULL": full,
        "HALF": half,
        "delta_live_births_per_parent_tick": delta,
        **paired_bootstrap(rows, 100),
        "falsification_condition": (
            "A nonzero residual recruitment contrast at p=1 means miss "
            "tolerance alone is insufficient."),
        "scope": (
            "Post-hoc established-parent mechanism control; not eligible "
            "to alter the registered p-grid candidate rule."),
    }

    raw_path = OUTPUT_DIR / f"{PREFIX}-raw.jsonl"
    summary_path = OUTPUT_DIR / f"{PREFIX}-summary.json"
    with raw_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    summary_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
