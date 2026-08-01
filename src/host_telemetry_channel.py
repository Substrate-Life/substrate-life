"""Privacy-limited host telemetry to deterministic packet mapping.

This module does not couple telemetry to organisms. It accepts only aggregate
Linux counters and maps ordered samples into inspectable 256-byte records.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import struct


_COUNTER_FIELDS = (
    "cpu_total",
    "cpu_idle",
    "context_switches",
    "processes_started",
    "pages_in",
    "pages_out",
)
_PACKET_SAMPLE_COUNT = 11
_PACKET_DELTA_COUNT = _PACKET_SAMPLE_COUNT - 1


@dataclass(frozen=True)
class HostSample:
    monotonic_ns: int
    cpu_total: int
    cpu_idle: int
    context_switches: int
    processes_started: int
    pages_in: int
    pages_out: int

    def to_record(self) -> dict[str, int]:
        return asdict(self)


def _keyed_integers(text: str) -> dict[str, list[int]]:
    rows: dict[str, list[int]] = {}
    for line in text.splitlines():
        fields = line.split()
        if not fields:
            continue
        try:
            rows[fields[0]] = [int(value) for value in fields[1:]]
        except ValueError:
            continue
    return rows


def parse_aggregate_counters(
    monotonic_ns: int,
    proc_stat: str,
    vmstat: str,
) -> HostSample:
    """Parse aggregate counters; never retain per-CPU or device identifiers."""
    stat = _keyed_integers(proc_stat)
    vm = _keyed_integers(vmstat)
    required_stat = ("cpu", "ctxt", "processes")
    required_vm = ("pgpgin", "pgpgout")
    if any(key not in stat or not stat[key] for key in required_stat):
        raise ValueError("missing aggregate /proc/stat counter")
    if any(key not in vm or not vm[key] for key in required_vm):
        raise ValueError("missing aggregate /proc/vmstat counter")
    cpu = stat["cpu"]
    if len(cpu) < 5:
        raise ValueError("incomplete aggregate cpu counter")
    return HostSample(
        monotonic_ns=int(monotonic_ns),
        cpu_total=sum(cpu[:8]),
        cpu_idle=cpu[3] + cpu[4],
        context_switches=stat["ctxt"][0],
        processes_started=stat["processes"][0],
        pages_in=vm["pgpgin"][0],
        pages_out=vm["pgpgout"][0],
    )


def packet_from_samples(window_index: int, samples: list[HostSample]) -> bytes:
    """Map eleven samples (ten counter deltas) to one 256-byte packet."""
    if len(samples) != _PACKET_SAMPLE_COUNT:
        raise ValueError("exactly eleven samples are required")
    if not 0 <= window_index <= 0xFFFFFFFF:
        raise ValueError("window index is outside uint32 range")
    duration_ns = samples[-1].monotonic_ns - samples[0].monotonic_ns
    if duration_ns <= 0:
        raise ValueError("sample times must be strictly monotonic")
    duration_us = duration_ns // 1000
    if duration_us > 0xFFFFFFFF:
        raise ValueError("sample window duration is outside uint32 range")

    body = bytearray()
    for before, after in zip(samples, samples[1:]):
        if after.monotonic_ns <= before.monotonic_ns:
            raise ValueError("sample times must be strictly monotonic")
        for field in _COUNTER_FIELDS:
            delta = getattr(after, field) - getattr(before, field)
            if delta < 0:
                raise ValueError(f"counter reversal: {field}")
            if delta > 0xFFFFFFFF:
                raise ValueError(f"counter delta outside uint32 range: {field}")
            body.extend(struct.pack("<I", delta))

    header = struct.pack("<4sIII", b"HST1", window_index, duration_us,
                         _PACKET_DELTA_COUNT)
    packet = header + bytes(body)
    if len(packet) != 256:
        raise AssertionError("host packet mapping must produce 256 bytes")
    return packet


def artifact_from_samples(
    samples: list[HostSample],
    cadence_ns: int,
) -> dict[str, object]:
    """Build a raw-only, identity-free host-channel artifact."""
    if cadence_ns <= 0:
        raise ValueError("cadence must be positive")
    if len(samples) < _PACKET_SAMPLE_COUNT or (len(samples) - 1) % 10:
        raise ValueError("sample count must be 1 modulo 10 and at least 11")
    packets = []
    for window_index, start in enumerate(range(0, len(samples) - 1, 10)):
        packet = packet_from_samples(
            window_index, samples[start:start + _PACKET_SAMPLE_COUNT])
        packets.append({
            "window_index": window_index,
            "sample_start": start,
            "sample_stop_inclusive": start + 10,
            "data_hex": packet.hex(),
            "sha256": hashlib.sha256(packet).hexdigest(),
        })
    return {
        "artifact_version": 1,
        "scope": "host channel only; no organisms",
        "source": {
            "clock": "time.monotonic_ns",
            "proc_stat": "/proc/stat aggregate cpu, ctxt, processes only",
            "proc_vmstat": "/proc/vmstat pgpgin, pgpgout only",
        },
        "mapping": "HST1: 16-byte header plus ten six-counter uint32 delta vectors",
        "cadence_ns": cadence_ns,
        "sample_count": len(samples),
        "samples": [sample.to_record() for sample in samples],
        "packets": packets,
    }
