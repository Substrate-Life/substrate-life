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
    instantiation_schedule_gate = (
        by_label["FULL"]["tail_instantiations_per_cycle_values"] == [3] and
        by_label["HALF"]["tail_instantiations_per_cycle_values"] == [2] and
        by_label["FULL"][
            "tail_materialization_failures_per_cycle_values"] == [0] and
        by_label["HALF"][
            "tail_materialization_failures_per_cycle_values"] == [0] and
        by_label["FULL"]["parent_alive"] and
        by_label["HALF"]["parent_alive"] and
        by_label["FULL"]["allocation_failures"] == 0 and
        by_label["HALF"]["allocation_failures"] == 0 and
        by_label["FULL"]["recurrent_interval_values"] == [17] and
        by_label["HALF"]["recurrent_interval_values"] == [17] and
        by_label["FULL"]["r4_bit_2048_values"] == [2048] and
        by_label["HALF"]["r4_bit_2048_values"] == [0])
    below_pre_extraction_ledger = {
        label: sum(
            event["offspring_instantiated"] and
            event["transfer_reserve"] < 20.0
            for event in all_events if event["lineage_label"] == label
        )
        for label in ("FULL", "HALF")
    }
    establishment_gate = (
        instantiation_schedule_gate and
        below_pre_extraction_ledger == {"FULL": 0, "HALF": 0}
    )
    result = {
        "kind": "equal_tempo_conditional_capacity_not_selection_evidence",
        "parameters": {
            "capture_probability": 1.0,
            "packet_energy": 500,
            "tau_r5": 51,
            "genome_length": 23,
            "recurrent_interval_both_paths": 17,
            "r4_bit_mask": 2048,
            "cycles": CYCLES,
            "tail_cycles": TAIL_CYCLES,
            "mutation_rates": 0,
            "offspring_execute": False,
        },
        "summaries": summaries,
        "current_no_threshold_instantiation_schedule_gate": (
            instantiation_schedule_gate),
        "primary_clean_fecundity_gate": establishment_gate,
        "posthoc_pre_extraction_ledger": {
            "exact_spend_through_READ": 20.0,
            "exact_arithmetic_condition": "initial_reserve > 20.0",
            "successful_instantiations_below_20": below_pre_extraction_ledger,
            "interpretation": (
                "offspring were removed before execution; instantiation is "
                "not established recruitment"
            ),
        },
        "superseded_expected_instantiation_rate_contrast": 1 / 17,
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
