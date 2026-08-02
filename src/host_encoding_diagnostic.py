"""Registered diagnostic projections for retained host-counter deltas."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path

from consts import TRANSFORM_DIFF, TRANSFORM_RLE
from transforms import can_reconstruct, compute_transform


def encode_normalized_u8(
    intervals: list[tuple[int, ...]],
    bounds: tuple[tuple[int, int], ...],
) -> bytes:
    """Encode interval-major per-field full-trace min-max normalization."""
    output = bytearray()
    for interval in intervals:
        if len(interval) != len(bounds):
            raise ValueError("field count mismatch")
        for value, (minimum, maximum) in zip(interval, bounds):
            if not minimum <= value <= maximum:
                raise ValueError("value outside registered normalization bounds")
            extent = maximum - minimum
            if extent == 0:
                output.append(0)
            else:
                output.append((255 * (value - minimum) + extent // 2) // extent)
    return bytes(output)


def encode_uleb128(intervals: list[tuple[int, ...]]) -> bytes:
    """Encode interval-major nonnegative integers as canonical unsigned LEB128."""
    output = bytearray()
    for interval in intervals:
        for value in interval:
            if value < 0:
                raise ValueError("ULEB128 requires nonnegative integers")
            while True:
                byte = value & 0x7F
                value >>= 7
                if value:
                    output.append(byte | 0x80)
                else:
                    output.append(byte)
                    break
    return bytes(output)


def encode_low_u8(intervals: list[tuple[int, ...]]) -> bytes:
    """Encode only each nonnegative delta's low-order byte."""
    output = bytearray()
    for interval in intervals:
        for value in interval:
            if value < 0:
                raise ValueError("low-byte projection requires nonnegative integers")
            output.append(value & 0xFF)
    return bytes(output)


def classify_mapping(
    winner_counts: dict[str, int],
    block_winner_counts: list[dict[str, int]],
    block_medians: dict[str, list[Fraction]],
) -> dict[str, bool]:
    """Apply the registered switching and exact block-drift criteria."""
    rle_majority = any(
        block["RLE"] * 2 > sum(block.values())
        for block in block_winner_counts
    )
    diff_majority = any(
        block["DIFF"] * 2 > sum(block.values())
        for block in block_winner_counts
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


def classify_diagnostic(mapping_results: list[dict[str, bool]]) -> str:
    """Return the registered all-mapping diagnostic classification."""
    if any(result["switching"] or result["block_drift"] for result in mapping_results):
        return "MAPPING_DEPENDENT_SIGNAL"
    return "NO_SIGNAL_UNDER_REGISTERED_ALTERNATIVES"


_SOURCE_SHA256 = "623f59af1b6dd76a0f050337345881b93059981547ffe96a89eaa8b9a3a57c5f"
_FIELDS = (
    "cpu_total", "cpu_idle", "context_switches",
    "processes_started", "pages_in", "pages_out",
)
_OPERATIONS = {"RLE": TRANSFORM_RLE, "DIFF": TRANSFORM_DIFF}
_PACKET_COUNT = 36_000
_SLICE_SIZE = 300
_BLOCK_SIZE = 3_000


def _median(values: list[Fraction]) -> Fraction:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * 0.5)]


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _winner_counts(winners: list[str]) -> dict[str, int]:
    return {name: winners.count(name) for name in ("RLE", "DIFF", "TIE")}


def _summaries(
    winners: list[str],
    fractions: dict[str, list[Fraction]],
    group_size: int,
    label: str,
) -> list[dict[str, object]]:
    summaries = []
    for index, start in enumerate(range(0, _PACKET_COUNT, group_size)):
        stop = start + group_size
        summaries.append({
            f"{label}_index": index,
            "packet_start": start,
            "packet_stop_exclusive": stop,
            "winner_counts": _winner_counts(winners[start:stop]),
            "median_compression_fraction": {
                name: _fraction_record(_median(values[start:stop]))
                for name, values in fractions.items()
            },
        })
    return summaries


def _analyze_mapping(
    name: str,
    packet_intervals: list[list[tuple[int, ...]]],
    encoder,
) -> dict[str, object]:
    packet_records = []
    winners = []
    fractions = {transform: [] for transform in _OPERATIONS}
    lengths = []
    for index, intervals in enumerate(packet_intervals):
        encoded = encoder(intervals)
        if not encoded:
            raise ValueError(f"empty encoded packet: {name} {index}")
        lengths.append(len(encoded))
        outcomes = {}
        sizes = {}
        for transform, operation in _OPERATIONS.items():
            output = compute_transform(operation, encoded)
            reconstructs = can_reconstruct(operation, encoded, output)
            if not reconstructs:
                raise ValueError(f"transform reconstruction failed: {name} {index} {transform}")
            reduction = len(encoded) - len(output)
            fraction = Fraction(reduction, len(encoded))
            fractions[transform].append(fraction)
            sizes[transform] = len(output)
            outcomes[transform] = {
                "output_length": len(output),
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
        packet_records.append({
            "packet_index": index,
            "encoded_length": len(encoded),
            "encoded_sha256": hashlib.sha256(encoded).hexdigest(),
            "winner": winner,
            "outcomes": outcomes,
        })

    slices = _summaries(winners, fractions, _SLICE_SIZE, "slice")
    blocks = _summaries(winners, fractions, _BLOCK_SIZE, "block")
    block_medians = {
        transform: [
            Fraction(
                block["median_compression_fraction"][transform]["numerator"],
                block["median_compression_fraction"][transform]["denominator"],
            )
            for block in blocks
        ]
        for transform in _OPERATIONS
    }
    counts = _winner_counts(winners)
    criteria = classify_mapping(
        counts,
        [block["winner_counts"] for block in blocks],
        block_medians,
    )
    return {
        "mapping": name,
        "packet_count": len(packet_records),
        "encoded_length": {
            "min": min(lengths),
            "median": sorted(lengths)[round((len(lengths) - 1) * 0.5)],
            "max": max(lengths),
        },
        "winner_counts": counts,
        "criteria": criteria,
        "five_minute_median_ranges": {
            transform: _fraction_record(max(values) - min(values))
            for transform, values in block_medians.items()
        },
        "thirty_second_slices": slices,
        "five_minute_blocks": blocks,
        "packets": packet_records,
    }


def reduce_trace(source_path: Path, manifest_path: Path) -> dict[str, object]:
    source_bytes = source_path.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    if source_hash != _SOURCE_SHA256:
        raise ValueError("source artifact hash mismatch")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("source_artifact_sha256") != _SOURCE_SHA256:
        raise ValueError("manifest source binding mismatch")
    artifact = json.loads(source_bytes)
    raw = artifact.get("raw_records", [])
    retained_packets = artifact.get("packets", [])
    if len(raw) != 360_001 or len(retained_packets) != _PACKET_COUNT:
        raise ValueError("registered source record count mismatch")

    parsed = [record["parsed"] for record in raw]
    packet_intervals = []
    field_minima = [None] * len(_FIELDS)
    field_maxima = [None] * len(_FIELDS)
    for packet_index in range(_PACKET_COUNT):
        retained = retained_packets[packet_index]
        start = packet_index * 10
        if (
            retained.get("index") != packet_index
            or retained.get("sample_start") != start
            or retained.get("sample_stop_inclusive") != start + 10
        ):
            raise ValueError(f"packet-window metadata mismatch: {packet_index}")
        intervals = []
        for before, after in zip(parsed[start:start + 10], parsed[start + 1:start + 11]):
            values = tuple(after[field] - before[field] for field in _FIELDS)
            if any(value < 0 for value in values):
                raise ValueError(f"counter reversal: {packet_index}")
            intervals.append(values)
            for field_index, value in enumerate(values):
                current_min = field_minima[field_index]
                current_max = field_maxima[field_index]
                field_minima[field_index] = value if current_min is None else min(current_min, value)
                field_maxima[field_index] = value if current_max is None else max(current_max, value)
        packet_intervals.append(intervals)

    bounds = tuple(zip(field_minima, field_maxima))
    mappings = [
        _analyze_mapping(
            "NORMALIZED_U8", packet_intervals,
            lambda intervals: encode_normalized_u8(intervals, bounds),
        ),
        _analyze_mapping("ULEB128", packet_intervals, encode_uleb128),
        _analyze_mapping("LOW_U8", packet_intervals, encode_low_u8),
    ]
    classification = classify_diagnostic([mapping["criteria"] for mapping in mappings])
    return {
        "result_version": 1,
        "status": "VALID",
        "registered_classification": classification,
        "source": {
            "path": str(source_path),
            "sha256": source_hash,
            "manifest_path": str(manifest_path),
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        },
        "normalization_bounds": {
            field: {"minimum": minimum, "maximum": maximum}
            for field, (minimum, maximum) in zip(_FIELDS, bounds)
        },
        "audited_fixed_width_reference": {
            "winner_counts": {"RLE": 36_000, "DIFF": 0, "TIE": 0},
            "switching": False,
            "block_drift": False,
        },
        "mappings": mappings,
        "claim_boundary": {
            "diagnostic_only": True,
            "not_authorized": [
                "encoding selection", "online coupling", "organism assay",
                "lagged prediction", "fitness", "cross-host inference",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = reduce_trace(args.source, args.manifest)
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(encoded)
    print(json.dumps({
        "output": str(args.output),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "classification": result["registered_classification"],
        "mappings": [
            {
                "mapping": mapping["mapping"],
                "winner_counts": mapping["winner_counts"],
                "criteria": mapping["criteria"],
                "five_minute_median_ranges": mapping["five_minute_median_ranges"],
            }
            for mapping in result["mappings"]
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
