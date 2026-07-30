"""Registered equal-tempo conditional third-bout p=1 capacity trace."""

from __future__ import annotations

import json
from pathlib import Path

from consts import PACKET_SIZE
from derive_stochastic_efficiency import disable_mutation
from trace_efficiency_three_bout_p1 import CYCLES, TAIL_CYCLES, trace

OUTPUT_DIR = Path("/opt/data/avida-life")
PREFIX = "efficiency-conditional-third-bout-p1"


def main() -> None:
    disable_mutation()
    summaries = []
    all_events = []
    for label, extent in (("FULL", PACKET_SIZE), ("HALF", 128)):
        summary, events = trace(label, extent, conditional=True)
        summaries.append(summary)
        all_events.extend(events)

    by_label = {row["label"]: row for row in summaries}
    gate_pass = (
        by_label["FULL"]["tail_births_per_cycle_values"] == [3] and
        by_label["HALF"]["tail_births_per_cycle_values"] == [2] and
        by_label["FULL"]["tail_stillbirths_per_cycle_values"] == [0] and
        by_label["HALF"]["tail_stillbirths_per_cycle_values"] == [0] and
        by_label["FULL"]["parent_alive"] and
        by_label["HALF"]["parent_alive"] and
        by_label["FULL"]["allocation_failures"] == 0 and
        by_label["HALF"]["allocation_failures"] == 0 and
        by_label["FULL"]["recurrent_interval_expected"] == 17 and
        by_label["HALF"]["recurrent_interval_expected"] == 17)
    result = {
        "kind": "equal_tempo_conditional_capacity_not_selection_evidence",
        "parameters": {
            "capture_probability": 1.0,
            "packet_energy": 500,
            "tau_r5": 51,
            "genome_length": 23,
            "recurrent_interval_both_paths": 17,
            "half_r4_threshold": 656,
            "cycles": CYCLES,
            "tail_cycles": TAIL_CYCLES,
            "mutation_rates": 0,
            "offspring_execute": False,
        },
        "summaries": summaries,
        "primary_clean_fecundity_gate": gate_pass,
        "expected_rate_contrast_if_pass": 1 / 17,
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
