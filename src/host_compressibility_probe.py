"""Exploratory non-organism compressibility probe for the current host mapping."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Iterable

from consts import TRANSFORM_DIFF, TRANSFORM_RLE
from host_telemetry_channel import HostSample, packet_from_samples, parse_aggregate_counters
from transforms import can_reconstruct, compute_transform


_TRANSFORMS = {"RLE": TRANSFORM_RLE, "DIFF": TRANSFORM_DIFF}


def _percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def analyze_payloads(payloads: Iterable[bytes], block_size: int = 50) -> dict[str, object]:
    """Apply the live lossless transforms and classify registered variation."""
    payload_list = list(payloads)
    if not payload_list or block_size <= 0:
        raise ValueError("payloads and block size must be positive")
    if len(payload_list) % block_size:
        raise ValueError("payload count must be divisible by block size")

    reductions = {name: [] for name in _TRANSFORMS}
    winners: list[str] = []
    for payload in payload_list:
        sizes = {}
        for name, operation in _TRANSFORMS.items():
            transformed = compute_transform(operation, payload)
            if not can_reconstruct(operation, payload, transformed):
                raise AssertionError(f"{name} failed live reconstruction")
            sizes[name] = len(transformed)
            reductions[name].append(len(payload) - len(transformed))
        if sizes["RLE"] < sizes["DIFF"]:
            winners.append("RLE")
        elif sizes["DIFF"] < sizes["RLE"]:
            winners.append("DIFF")
        else:
            winners.append("TIE")

    counts = {name: winners.count(name) for name in ("RLE", "DIFF", "TIE")}
    block_majorities = []
    for start in range(0, len(winners), block_size):
        block = winners[start:start + block_size]
        block_counts = {name: block.count(name) for name in counts}
        greatest = max(block_counts.values())
        leaders = [name for name, count in block_counts.items() if count == greatest]
        block_majorities.append(leaders[0] if len(leaders) == 1 else "MIXED_TIE")

    spans = {
        name: _percentile(values, 0.90) - _percentile(values, 0.10)
        for name, values in reductions.items()
    }
    n = len(winners)
    switching = (
        counts["RLE"] >= 0.10 * n
        and counts["DIFF"] >= 0.10 * n
        and "RLE" in block_majorities
        and "DIFF" in block_majorities
    )
    stable = max(counts.values()) >= 0.90 * n and all(span <= 16 for span in spans.values())
    classification = (
        "SWITCHING_CAPABLE" if switching else "NARROW_STABLE" if stable else "AMBIGUOUS"
    )
    return {
        "classification": classification,
        "packet_count": n,
        "block_size": block_size,
        "winner_counts": counts,
        "block_majorities": block_majorities,
        "reduction_bytes": {
            name: {
                "min": min(values),
                "p10": _percentile(values, 0.10),
                "median": _percentile(values, 0.50),
                "p90": _percentile(values, 0.90),
                "max": max(values),
            }
            for name, values in reductions.items()
        },
        "reduction_p90_minus_p10": spans,
    }


def _allowlisted_lines(text: str, keys: tuple[str, ...]) -> list[str]:
    selected = []
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] in keys:
            selected.append(line)
    return selected


def capture(sample_count: int, cadence_ns: int) -> tuple[list[HostSample], list[dict[str, object]]]:
    """Capture exact allowlisted aggregate lines on absolute monotonic deadlines."""
    samples = []
    raw_records = []
    first_deadline = time.monotonic_ns()
    for sequence in range(sample_count):
        deadline = first_deadline + sequence * cadence_ns
        remaining = deadline - time.monotonic_ns()
        if remaining > 0:
            time.sleep(remaining / 1_000_000_000)
        wake = time.monotonic_ns()
        read_start = time.monotonic_ns()
        proc_stat = Path("/proc/stat").read_text(encoding="ascii")
        vmstat = Path("/proc/vmstat").read_text(encoding="ascii")
        read_end = time.monotonic_ns()
        stat_lines = _allowlisted_lines(proc_stat, ("cpu", "ctxt", "processes"))
        vm_lines = _allowlisted_lines(vmstat, ("pgpgin", "pgpgout"))
        sample = parse_aggregate_counters(
            read_end, "\n".join(stat_lines), "\n".join(vm_lines)
        )
        samples.append(sample)
        raw_records.append({
            "sequence": sequence,
            "scheduled_deadline_monotonic_ns": deadline,
            "wake_monotonic_ns": wake,
            "read_start_monotonic_ns": read_start,
            "read_end_monotonic_ns": read_end,
            "proc_stat_allowlisted_lines": stat_lines,
            "proc_vmstat_allowlisted_lines": vm_lines,
            "parsed": sample.to_record(),
        })
    return samples, raw_records


def build_artifact(sample_count: int, cadence_ns: int) -> dict[str, object]:
    samples, raw_records = capture(sample_count, cadence_ns)
    packets = []
    full_packets = []
    for index, start in enumerate(range(0, sample_count - 1, 10)):
        packet = packet_from_samples(index, samples[start:start + 11])
        full_packets.append(packet)
        outcomes = {}
        for name, operation in _TRANSFORMS.items():
            for scope, data in (("payload", packet[16:]), ("whole_packet", packet)):
                transformed = compute_transform(operation, data)
                outcomes[f"{name}_{scope}"] = {
                    "output_size": len(transformed),
                    "reduction": len(data) - len(transformed),
                    "reconstructs": can_reconstruct(operation, data, transformed),
                }
        packets.append({
            "index": index,
            "sample_start": start,
            "sample_stop_inclusive": start + 10,
            "sha256": hashlib.sha256(packet).hexdigest(),
            "data_hex": packet.hex(),
            "outcomes": outcomes,
        })
    return {
        "artifact_version": 1,
        "scope": "exploratory host compressibility only; no organisms or ecology",
        "sample_count": sample_count,
        "cadence_ns": cadence_ns,
        "mapping": "current HST1 mapping; payload bytes 16:256 primary",
        "observation_effect": "recorder CPU and final artifact write perturb the observed host",
        "raw_records": raw_records,
        "packets": packets,
        "primary_payload_summary": analyze_payloads(
            [packet[16:] for packet in full_packets]
        ),
        "secondary_whole_packet_summary": analyze_payloads(full_packets),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--sample-count", type=int, default=3001)
    parser.add_argument("--cadence-ms", type=int, default=10)
    args = parser.parse_args()
    if args.sample_count < 11 or (args.sample_count - 1) % 10:
        parser.error("sample count must be at least 11 and 1 modulo 10")
    artifact = build_artifact(args.sample_count, args.cadence_ms * 1_000_000)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(artifact, indent=2, sort_keys=True) + "\n").encode()
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(encoded)
    print(json.dumps({
        "output": str(args.output),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "primary": artifact["primary_payload_summary"],
        "secondary": artifact["secondary_whole_packet_summary"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
