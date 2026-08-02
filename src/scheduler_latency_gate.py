"""Registered scheduler-latency sensitivity reduction."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path

from consts import TRANSFORM_DIFF, TRANSFORM_RLE
from transforms import can_reconstruct, compute_transform


def zigzag(value: int) -> int:
    return 2 * value if value >= 0 else -2 * value - 1


def encode_uleb128(values: list[int]) -> bytes:
    output = bytearray()
    for original in values:
        if original < 0:
            raise ValueError("ULEB128 requires nonnegative values")
        value = original
        while True:
            byte = value & 0x7F
            value >>= 7
            if value:
                output.append(byte | 0x80)
            else:
                output.append(byte)
                break
    return bytes(output)


def extract_latency_values(
    records: list[dict[str, int]], cadence_ns: int
) -> tuple[list[int], list[int]]:
    if len(records) < 2 or cadence_ns <= 0:
        raise ValueError("at least two records and positive cadence are required")
    lateness = []
    deviation = []
    for before, current in zip(records, records[1:]):
        late = current["wake_monotonic_ns"] - current["scheduled_deadline_monotonic_ns"]
        if late < 0:
            raise ValueError("wake precedes scheduled deadline")
        interval = current["wake_monotonic_ns"] - before["wake_monotonic_ns"]
        if interval <= 0:
            raise ValueError("wake timestamps are not strictly monotonic")
        lateness.append(late)
        deviation.append(interval - cadence_ns)
    return lateness, deviation


def classify_morphology(
    winner_counts: dict[str, int],
    block_winner_counts: list[dict[str, int]],
    block_medians: dict[str, list[Fraction]],
) -> dict[str, bool]:
    rle_majority = any(
        block["RLE"] * 2 > sum(block.values()) for block in block_winner_counts
    )
    diff_majority = any(
        block["DIFF"] * 2 > sum(block.values()) for block in block_winner_counts
    )
    switching = (
        winner_counts["RLE"] >= 3600
        and winner_counts["DIFF"] >= 3600
        and rle_majority
        and diff_majority
    )
    block_drift = any(
        max(values) - min(values) > Fraction(1, 15)
        for values in block_medians.values()
    )
    return {"switching": switching, "block_drift": block_drift}


def classify_gate(passive: dict, loaded: dict) -> dict[str, object]:
    """Apply registered direct and transform-morphology sensitivity rules."""
    directly_responsive = (
        loaded["latency"]["median_ns"] >= 2 * passive["latency"]["median_ns"]
        or loaded["latency"]["p99_ns"] >= 2 * passive["latency"]["p99_ns"]
    )
    changed_within_arm_morphology = (
        loaded["criteria"]["switching"] != passive["criteria"]["switching"]
        or loaded["criteria"]["block_drift"] != passive["criteria"]["block_drift"]
    )
    median_shift = any(
        abs(
            _median(loaded["block_medians"][transform])
            - _median(passive["block_medians"][transform])
        ) > Fraction(1, 15)
        for transform in ("RLE", "DIFF")
    )
    passive_total = sum(passive["winner_counts"].values())
    loaded_total = sum(loaded["winner_counts"].values())
    winner_shift = abs(
        Fraction(loaded["winner_counts"]["RLE"], loaded_total)
        - Fraction(passive["winner_counts"]["RLE"], passive_total)
    ) > Fraction(1, 5)
    morphologically_responsive = changed_within_arm_morphology or median_shift or winner_shift
    if directly_responsive and morphologically_responsive:
        classification = "LOAD_SENSITIVE_LATENCY_MORPHOLOGY"
    elif directly_responsive:
        classification = "LOAD_SENSITIVE_BUT_MORPHOLOGICALLY_FLAT"
    elif morphologically_responsive:
        classification = "MORPHOLOGY_CHANGE_WITHOUT_DIRECT_SHIFT"
    else:
        classification = "NO_DETECTED_LOAD_SENSITIVITY"
    return {
        "directly_responsive": directly_responsive,
        "morphologically_responsive": morphologically_responsive,
        "components": {
            "changed_within_arm_morphology": changed_within_arm_morphology,
            "between_arm_median_shift": median_shift,
            "rle_winner_fraction_shift": winner_shift,
        },
        "tenfold_p99_prediction": (
            loaded["latency"]["p99_ns"] >= 10 * passive["latency"]["p99_ns"]
        ),
        "classification": classification,
    }


def nearest_index_percentile(values: list, numerator: int, denominator: int):
    if not values or denominator <= 0 or not 0 <= numerator <= denominator:
        raise ValueError("invalid percentile input")
    ordered = sorted(values)
    index = (2 * (len(ordered) - 1) * numerator + denominator) // (2 * denominator)
    return ordered[index]


def _median(values: list[Fraction]) -> Fraction:
    return nearest_index_percentile(values, 1, 2)


_PASSIVE_SHA256 = "623f59af1b6dd76a0f050337345881b93059981547ffe96a89eaa8b9a3a57c5f"
_PACKET_COUNT = 36_000
_SLICE_SIZE = 300
_BLOCK_SIZE = 3_000
_TRANSFORMS = {"RLE": TRANSFORM_RLE, "DIFF": TRANSFORM_DIFF}


def _percentile_int(values: list[int], numerator: int, denominator: int) -> int:
    return nearest_index_percentile(values, numerator, denominator)


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _winner_counts(values: list[str]) -> dict[str, int]:
    return {name: values.count(name) for name in ("RLE", "DIFF", "TIE")}


def reduction_sign_counts(values: list[int]) -> dict[str, int]:
    return {
        "positive": sum(value > 0 for value in values),
        "zero": sum(value == 0 for value in values),
        "negative": sum(value < 0 for value in values),
    }


def _group_summaries(
    raw_values: list[int],
    winners: list[str],
    fractions: dict[str, list[Fraction]],
    reductions: dict[str, list[int]],
    packet_group_size: int,
    label: str,
) -> list[dict[str, object]]:
    summaries = []
    for index, packet_start in enumerate(range(0, _PACKET_COUNT, packet_group_size)):
        packet_stop = packet_start + packet_group_size
        raw_start, raw_stop = packet_start * 10, packet_stop * 10
        summaries.append({
            f"{label}_index": index,
            "packet_start": packet_start,
            "packet_stop_exclusive": packet_stop,
            "raw_value_median_ns": _percentile_int(raw_values[raw_start:raw_stop], 1, 2),
            "winner_counts": _winner_counts(winners[packet_start:packet_stop]),
            "reduction_sign_counts": {
                name: reduction_sign_counts(values[packet_start:packet_stop])
                for name, values in reductions.items()
            },
            "median_compression_fraction": {
                name: _fraction_record(_median(values[packet_start:packet_stop]))
                for name, values in fractions.items()
            },
        })
    return summaries


def _analyze_channel(name: str, raw_values: list[int], signed: bool) -> dict[str, object]:
    if len(raw_values) != 360_000:
        raise ValueError(f"{name} requires 360000 values")
    packets = []
    winners = []
    fractions = {transform: [] for transform in _TRANSFORMS}
    reductions = {transform: [] for transform in _TRANSFORMS}
    lengths = []
    for packet_index, start in enumerate(range(0, len(raw_values), 10)):
        values = raw_values[start:start + 10]
        encoded = encode_uleb128([zigzag(value) for value in values] if signed else values)
        lengths.append(len(encoded))
        outcomes = {}
        sizes = {}
        for transform, operation in _TRANSFORMS.items():
            transformed = compute_transform(operation, encoded)
            if not can_reconstruct(operation, encoded, transformed):
                raise ValueError(f"reconstruction failed: {name} {packet_index} {transform}")
            reduction = len(encoded) - len(transformed)
            fraction = Fraction(reduction, len(encoded))
            fractions[transform].append(fraction)
            reductions[transform].append(reduction)
            sizes[transform] = len(transformed)
            outcomes[transform] = {
                "output_length": len(transformed),
                "reduction_bytes": reduction,
                "compression_fraction": _fraction_record(fraction),
                "reconstructs": True,
            }
        if sizes["RLE"] < sizes["DIFF"]:
            winner = "RLE"
        elif sizes["DIFF"] < sizes["RLE"]:
            winner = "DIFF"
        else:
            winner = "TIE"
        winners.append(winner)
        packets.append({
            "packet_index": packet_index,
            "encoded_length": len(encoded),
            "encoded_sha256": hashlib.sha256(encoded).hexdigest(),
            "winner": winner,
            "outcomes": outcomes,
        })
    slices = _group_summaries(
        raw_values, winners, fractions, reductions, _SLICE_SIZE, "slice"
    )
    blocks = _group_summaries(
        raw_values, winners, fractions, reductions, _BLOCK_SIZE, "block"
    )
    block_medians = {
        transform: [
            Fraction(
                block["median_compression_fraction"][transform]["numerator"],
                block["median_compression_fraction"][transform]["denominator"],
            )
            for block in blocks
        ]
        for transform in _TRANSFORMS
    }
    counts = _winner_counts(winners)
    criteria = classify_morphology(
        counts,
        [block["winner_counts"] for block in blocks],
        block_medians,
    )
    positive_support_by_transform = {
        transform: (
            reduction_sign_counts(reductions[transform])["positive"] >= 3_600
            and any(
                block["reduction_sign_counts"][transform]["positive"] * 2 > _BLOCK_SIZE
                for block in blocks
            )
        )
        for transform in _TRANSFORMS
    }
    return {
        "channel": name,
        "packet_count": len(packets),
        "encoded_length": {
            "min": min(lengths),
            "median": _percentile_int(lengths, 1, 2),
            "max": max(lengths),
        },
        "raw_value_distribution_ns": {
            "min": min(raw_values),
            "median": _percentile_int(raw_values, 1, 2),
            "p90": _percentile_int(raw_values, 9, 10),
            "p99": _percentile_int(raw_values, 99, 100),
            "p999": _percentile_int(raw_values, 999, 1000),
            "max": max(raw_values),
        },
        "winner_counts": counts,
        "reduction_sign_counts": {
            name: reduction_sign_counts(values) for name, values in reductions.items()
        },
        "criteria": criteria,
        "positive_compression_support": {
            "supported": any(positive_support_by_transform.values()),
            "by_transform": positive_support_by_transform,
        },
        "five_minute_median_ranges": {
            name: _fraction_record(max(values) - min(values))
            for name, values in block_medians.items()
        },
        "thirty_second_slices": slices,
        "five_minute_blocks": blocks,
        "packets": packets,
    }


def _load_arm(path: Path, expected_sha256: str) -> tuple[bytes, dict[str, object]]:
    encoded = path.read_bytes()
    if hashlib.sha256(encoded).hexdigest() != expected_sha256:
        raise ValueError(f"artifact hash mismatch: {path}")
    artifact = json.loads(encoded)
    if artifact.get("sample_count") != 360_001 or artifact.get("cadence_ns") != 10_000_000:
        raise ValueError(f"registered dimensions mismatch: {path}")
    records = artifact.get("raw_records", [])
    if len(records) != 360_001:
        raise ValueError(f"raw record count mismatch: {path}")
    for index, record in enumerate(records):
        if record.get("sequence") != index:
            raise ValueError(f"sequence mismatch: {path} {index}")
        expected_deadline = records[0]["scheduled_deadline_monotonic_ns"] + index * 10_000_000
        if record.get("scheduled_deadline_monotonic_ns") != expected_deadline:
            raise ValueError(f"deadline sequence mismatch: {path} {index}")
    return encoded, artifact


def _read_journal(path: Path) -> tuple[bytes, list[dict[str, object]]]:
    encoded = path.read_bytes()
    events = [json.loads(line) for line in encoded.splitlines() if line.strip()]
    if not events:
        raise ValueError("empty workload journal")
    return encoded, events


def verify_journal_coverage(events, records, arm: str, mode: str) -> dict[str, object]:
    def unique(kind):
        found = [event for event in events if event.get("event") == kind]
        if len(found) != 1:
            raise ValueError(f"journal requires one {kind}")
        return found[0]
    allowed = {"manager_started", "worker_ready", "invocation_started", "invocation_ended",
               "workload_started", "heartbeat", "capture_started", "capture_completed",
               "workload_stopped"}
    if any(event.get("event") not in allowed for event in events):
        raise ValueError("invalid or failed journal event")
    if any(events[i]["monotonic_ns"] > events[i + 1]["monotonic_ns"] for i in range(len(events) - 1)):
        raise ValueError("nonmonotonic journal")
    unique("manager_started"); unique("capture_started")
    start, complete, stop = unique("workload_started"), unique("capture_completed"), unique("workload_stopped")
    ready = [event.get("worker") for event in events if event.get("event") == "worker_ready"]
    if sorted(ready) != [0, 1] or start.get("arm") != arm or start.get("mode") != mode:
        raise ValueError("arm or worker readiness mismatch")
    first_deadline = records[0]["scheduled_deadline_monotonic_ns"]
    last_read = records[-1]["read_end_monotonic_ns"]
    if start["monotonic_ns"] > first_deadline - 30_000_000_000:
        raise ValueError("workload warmup shorter than 30 seconds")
    if complete["monotonic_ns"] < last_read or stop["monotonic_ns"] < complete["monotonic_ns"]:
        raise ValueError("incomplete workload coverage")
    heartbeats = [event for event in events if event.get("event") == "heartbeat"]
    points = [start["monotonic_ns"]] + [event["monotonic_ns"] for event in heartbeats] + [complete["monotonic_ns"]]
    if len(heartbeats) < 2 or any(b - a > 15_000_000_000 for a, b in zip(points, points[1:])):
        raise ValueError("heartbeat gap")
    if any(event.get("live_workers") != 2 for event in heartbeats):
        raise ValueError("worker liveness failure")
    begins = [event for event in events if event.get("event") == "invocation_started"]
    ends = [event for event in events if event.get("event") == "invocation_ended"]
    if mode == "sham":
        if begins or ends:
            raise ValueError("sham started invocation")
    else:
        for worker in (0, 1):
            starts = [event for event in begins if event.get("worker") == worker]
            finishes = [event for event in ends if event.get("worker") == worker]
            if not starts or len(starts) != len(finishes):
                raise ValueError("invocation pairing failure")
            for begun, ended in zip(starts, finishes):
                if begun.get("invocation") != ended.get("invocation") or ended.get("exit_status") != 0:
                    raise ValueError("compile invocation failure")
            if starts[0]["monotonic_ns"] - start["monotonic_ns"] > 2_000_000_000:
                raise ValueError("late first invocation")
            if any(following["monotonic_ns"] - prior["monotonic_ns"] > 2_000_000_000
                   for prior, following in zip(finishes, starts[1:])):
                raise ValueError("inter-invocation gap")
            if complete["monotonic_ns"] - finishes[-1]["monotonic_ns"] > 2_000_000_000:
                raise ValueError("early final invocation")
    workers = stop.get("workers", [])
    if len(workers) != 2 or stop.get("cleanup_success") is not True or stop.get("live_workers_after_join") != 0:
        raise ValueError("terminal workload failure")
    if mode == "compile" and any(worker.get("completed", 0) <= 0 or worker.get("nonzero") != 0 for worker in workers):
        raise ValueError("terminal compile failure")
    if mode == "sham" and any(worker.get("invocations") != 0 for worker in workers):
        raise ValueError("terminal sham failure")
    return {"warmup_ns": first_deadline - start["monotonic_ns"],
            "coverage_after_last_read_ns": stop["monotonic_ns"] - last_read,
            "heartbeat_count": len(heartbeats), "workers": workers}


def _arm_for_gate(channel: dict[str, object], primary_distribution: dict[str, int]) -> dict:
    block_medians = {
        transform: [
            Fraction(
                block["median_compression_fraction"][transform]["numerator"],
                block["median_compression_fraction"][transform]["denominator"],
            )
            for block in channel["five_minute_blocks"]
        ]
        for transform in _TRANSFORMS
    }
    return {
        "latency": {
            "median_ns": primary_distribution["median"],
            "p99_ns": primary_distribution["p99"],
        },
        "winner_counts": channel["winner_counts"],
        "criteria": channel["criteria"],
        "block_medians": block_medians,
    }


def reduce_gate(
    passive_path: Path,
    compile_path: Path,
    sham_path: Path,
    compile_journal_path: Path,
    sham_journal_path: Path,
    manifest_path: Path,
) -> dict[str, object]:
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    passive_bytes, passive_artifact = _load_arm(passive_path, _PASSIVE_SHA256)
    arm_inputs = {
        "COMPILE": (compile_path, compile_journal_path, "C", "compile"),
        "SHAM": (sham_path, sham_journal_path, "S", "sham"),
    }
    artifacts = {"PASSIVE": passive_artifact}
    sources = {"passive": {"path": str(passive_path), "sha256": hashlib.sha256(passive_bytes).hexdigest()}}
    workload = {}
    for arm_name, (artifact_path, journal_path, arm_code, mode) in arm_inputs.items():
        key = arm_name.lower()
        artifact_bytes, artifact = _load_arm(artifact_path, manifest[f"{key}_artifact_sha256"])
        journal_bytes, events = _read_journal(journal_path)
        if hashlib.sha256(journal_bytes).hexdigest() != manifest[f"{key}_journal_sha256"]:
            raise ValueError("workload journal hash mismatch")
        workload[arm_name] = verify_journal_coverage(events, artifact["raw_records"], arm_code, mode)
        artifacts[arm_name] = artifact
        sources[key] = {"path": str(artifact_path), "sha256": hashlib.sha256(artifact_bytes).hexdigest()}
        sources[f"{key}_journal"] = {"path": str(journal_path), "sha256": hashlib.sha256(journal_bytes).hexdigest()}

    arms = {}
    for arm_name, artifact in artifacts.items():
        lateness, deviation = extract_latency_values(
            artifact["raw_records"], artifact["cadence_ns"]
        )
        arms[arm_name] = {
            "deadline_lateness": _analyze_channel(
                "DEADLINE_LATENESS_ULEB128", lateness, signed=False
            ),
            "cadence_deviation": _analyze_channel(
                "CADENCE_DEVIATION_ZIGZAG_ULEB128", deviation, signed=True
            ),
        }

    distributions = {name: data["deadline_lateness"]["raw_value_distribution_ns"] for name, data in arms.items()}
    primary_gate = classify_gate(
        _arm_for_gate(arms["SHAM"]["deadline_lateness"], distributions["SHAM"]),
        _arm_for_gate(arms["COMPILE"]["deadline_lateness"], distributions["COMPILE"]),
    )
    secondary_gate = classify_gate(
        _arm_for_gate(arms["SHAM"]["cadence_deviation"], distributions["SHAM"]),
        _arm_for_gate(arms["COMPILE"]["cadence_deviation"], distributions["COMPILE"]),
    )
    primary_gate["tenfold_p99_prediction_confirmed"] = distributions["COMPILE"]["p99"] >= 10 * distributions["SHAM"]["p99"]
    sources["manifest"] = {"path": str(manifest_path), "sha256": hashlib.sha256(manifest_bytes).hexdigest()}
    return {
        "result_version": 2,
        "status": "VALID",
        "registered_classification": primary_gate["classification"],
        "primary_gate": primary_gate,
        "secondary_derivative_gate": secondary_gate,
        "historical_passive_is_descriptive_only": True,
        "sources": sources,
        "workload_coverage": workload,
        "arms": arms,
        "claim_boundary": {
            "sensitivity_gate_only": True,
            "matched_single_pair": True,
            "compilation_specific_causality": False,
            "secondary_is_deterministic_first_difference": True,
            "winner_may_only_expand_less": True,
            "not_established": [
                "ordinary-use morphology", "organism exposure", "fitness",
                "adaptation", "selection", "cross-host generality",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("passive", type=Path)
    parser.add_argument("compile", type=Path)
    parser.add_argument("sham", type=Path)
    parser.add_argument("compile_journal", type=Path)
    parser.add_argument("sham_journal", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = reduce_gate(
        args.passive, args.compile, args.sham,
        args.compile_journal, args.sham_journal, args.manifest,
    )
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(encoded)
    print(json.dumps({
        "output": str(args.output),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "classification": result["registered_classification"],
        "primary_gate": result["primary_gate"],
        "secondary_derivative_gate": result["secondary_derivative_gate"],
        "arm_primary_distributions": {
            arm: data["deadline_lateness"]["raw_value_distribution_ns"]
            for arm, data in result["arms"].items()
        },
        "arm_primary_winners": {
            arm: data["deadline_lateness"]["winner_counts"]
            for arm, data in result["arms"].items()
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
