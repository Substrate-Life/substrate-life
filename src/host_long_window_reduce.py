"""Fail-closed reducer for the registered one-hour host-compressibility trace."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path

from consts import TRANSFORM_DIFF, TRANSFORM_RLE
from host_telemetry_channel import HostSample, packet_from_samples
from transforms import can_reconstruct, compute_transform


_TRANSFORMS = {"RLE": TRANSFORM_RLE, "DIFF": TRANSFORM_DIFF}
_EXPECTED_SAMPLES = 360_001
_EXPECTED_PACKETS = 36_000
_SLICE_PACKETS = 300
_BLOCK_PACKETS = 3_000


def _percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def classify_registered(
    local_stability: list[bool], block_medians: dict[str, list[int]]
) -> str:
    """Apply the frozen long-window classification without reinterpretation."""
    if not all(local_stability):
        return "WITHIN_30S_VARIATION"
    drift = any(max(values) - min(values) > 16 for values in block_medians.values())
    return "TIMESCALE_SEPARATED_DRIFT" if drift else "LONG_WINDOW_NARROW_STABLE"


def _scope_series(packets: list[bytes], payload_only: bool) -> dict[str, object]:
    reductions = {name: [] for name in _TRANSFORMS}
    winners = []
    for packet in packets:
        data = packet[16:] if payload_only else packet
        sizes = {}
        for name, operation in _TRANSFORMS.items():
            transformed = compute_transform(operation, data)
            if not can_reconstruct(operation, data, transformed):
                raise ValueError(f"{name} reconstruction failed")
            sizes[name] = len(transformed)
            reductions[name].append(len(data) - len(transformed))
        if sizes["RLE"] < sizes["DIFF"]:
            winners.append("RLE")
        elif sizes["DIFF"] < sizes["RLE"]:
            winners.append("DIFF")
        else:
            winners.append("TIE")
    return {"reductions": reductions, "winners": winners}


def _slice_summaries(series: dict[str, object]) -> list[dict[str, object]]:
    reductions = series["reductions"]
    winners = series["winners"]
    summaries = []
    for index, start in enumerate(range(0, _EXPECTED_PACKETS, _SLICE_PACKETS)):
        stop = start + _SLICE_PACKETS
        counts = {name: winners[start:stop].count(name) for name in ("RLE", "DIFF", "TIE")}
        spans = {}
        medians = {}
        for name in _TRANSFORMS:
            values = reductions[name][start:stop]
            spans[name] = _percentile(values, 0.90) - _percentile(values, 0.10)
            medians[name] = _percentile(values, 0.50)
        stable = max(counts.values()) >= 270 and all(value <= 16 for value in spans.values())
        summaries.append({
            "slice_index": index,
            "packet_start": start,
            "packet_stop_exclusive": stop,
            "winner_counts": counts,
            "median_reduction": medians,
            "p90_minus_p10": spans,
            "locally_narrow_stable": stable,
        })
    return summaries


def _block_summaries(series: dict[str, object]) -> list[dict[str, object]]:
    reductions = series["reductions"]
    winners = series["winners"]
    summaries = []
    for index, start in enumerate(range(0, _EXPECTED_PACKETS, _BLOCK_PACKETS)):
        stop = start + _BLOCK_PACKETS
        summaries.append({
            "block_index": index,
            "packet_start": start,
            "packet_stop_exclusive": stop,
            "winner_counts": {
                name: winners[start:stop].count(name) for name in ("RLE", "DIFF", "TIE")
            },
            "median_reduction": {
                name: _percentile(reductions[name][start:stop], 0.50)
                for name in _TRANSFORMS
            },
        })
    return summaries


def reduce_artifact(input_path: Path, manifest_path: Path) -> dict[str, object]:
    encoded = input_path.read_bytes()
    artifact = json.loads(encoded)
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if artifact.get("sample_count") != _EXPECTED_SAMPLES:
        raise ValueError("registered sample count mismatch")
    raw = artifact.get("raw_records", [])
    retained_packets = artifact.get("packets", [])
    if len(raw) != _EXPECTED_SAMPLES or len(retained_packets) != _EXPECTED_PACKETS:
        raise ValueError("retained record count mismatch")
    if manifest.get("expected_packet_count") != _EXPECTED_PACKETS:
        raise ValueError("manifest packet count mismatch")

    samples = [HostSample(**record["parsed"]) for record in raw]
    packets = []
    for index, retained in enumerate(retained_packets):
        start = index * 10
        packet = packet_from_samples(index, samples[start:start + 11])
        if packet.hex() != retained["data_hex"]:
            raise ValueError(f"packet reconstruction mismatch: {index}")
        if hashlib.sha256(packet).hexdigest() != retained["sha256"]:
            raise ValueError(f"packet hash mismatch: {index}")
        packets.append(packet)

    primary = _scope_series(packets, payload_only=True)
    secondary = _scope_series(packets, payload_only=False)
    primary_slices = _slice_summaries(primary)
    primary_blocks = _block_summaries(primary)
    secondary_slices = _slice_summaries(secondary)
    secondary_blocks = _block_summaries(secondary)
    block_medians = {
        name: [block["median_reduction"][name] for block in primary_blocks]
        for name in _TRANSFORMS
    }
    classification = classify_registered(
        [item["locally_narrow_stable"] for item in primary_slices], block_medians
    )

    fields = (
        "cpu_total", "cpu_idle", "context_switches",
        "processes_started", "pages_in", "pages_out",
    )
    counter_deltas = {}
    for field in fields:
        values = [getattr(after, field) - getattr(before, field)
                  for before, after in zip(samples, samples[1:])]
        frequencies = Counter(values)
        counter_deltas[field] = {
            "zero_intervals": frequencies[0],
            "nonzero_intervals": len(values) - frequencies[0],
            "unique_values": len(frequencies),
            "min": min(values),
            "median": _percentile(values, 0.50),
            "max": max(values),
        }

    wake_lateness = [
        record["wake_monotonic_ns"] - record["scheduled_deadline_monotonic_ns"]
        for record in raw
    ]
    return {
        "result_version": 1,
        "status": "VALID",
        "registered_classification": classification,
        "input": {
            "path": str(input_path),
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "manifest_path": str(manifest_path),
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "sample_count": len(raw),
            "packet_count": len(packets),
        },
        "timing": {
            "first_read_end_monotonic_ns": raw[0]["read_end_monotonic_ns"],
            "last_read_end_monotonic_ns": raw[-1]["read_end_monotonic_ns"],
            "elapsed_read_end_ns": (
                raw[-1]["read_end_monotonic_ns"] - raw[0]["read_end_monotonic_ns"]
            ),
            "wake_lateness_ns": {
                "min": min(wake_lateness),
                "median": _percentile(wake_lateness, 0.50),
                "p90": _percentile(wake_lateness, 0.90),
                "max": max(wake_lateness),
            },
        },
        "counter_deltas": counter_deltas,
        "primary_payload": {
            "winner_counts": {
                name: primary["winners"].count(name) for name in ("RLE", "DIFF", "TIE")
            },
            "thirty_second_slices": primary_slices,
            "five_minute_blocks": primary_blocks,
            "five_minute_median_ranges": {
                name: max(values) - min(values) for name, values in block_medians.items()
            },
        },
        "secondary_whole_packet": {
            "winner_counts": {
                name: secondary["winners"].count(name)
                for name in ("RLE", "DIFF", "TIE")
            },
            "thirty_second_slices": secondary_slices,
            "five_minute_blocks": secondary_blocks,
        },
        "claim_boundary": {
            "measured": "one retained one-hour host channel under the frozen mapping",
            "not_established": [
                "controlled workload dependence", "organismal sensing",
                "wall-clock to logical-tick exposure", "fitness", "generality",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = reduce_artifact(args.input, args.manifest)
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(encoded)
    print(json.dumps({
        "output": str(args.output),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "classification": result["registered_classification"],
        "primary_winners": result["primary_payload"]["winner_counts"],
        "stable_30s_slices": sum(
            item["locally_narrow_stable"]
            for item in result["primary_payload"]["thirty_second_slices"]
        ),
        "five_minute_median_ranges": result["primary_payload"]["five_minute_median_ranges"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
