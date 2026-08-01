"""Tests for the non-organism real-host telemetry channel."""

from __future__ import annotations

import unittest

from host_telemetry_channel import (
    HostSample,
    artifact_from_samples,
    packet_from_samples,
    parse_aggregate_counters,
)


PROC_STAT = """cpu  100 2 30 400 5 6 7 8 9 10
cpu0 50 1 15 200 2 3 4 4 4 5
intr 999
ctxt 12345
btime 1700000000
processes 678
"""

VMSTAT = """nr_free_pages 1000
pgpgin 2468
pgpgout 1357
pswpin 0
pswpout 0
"""


class HostTelemetryChannelTests(unittest.TestCase):
    def test_parse_aggregate_counters_uses_no_identifying_fields(self):
        sample = parse_aggregate_counters(42, PROC_STAT, VMSTAT)

        self.assertEqual(
            sample,
            HostSample(
                monotonic_ns=42,
                cpu_total=558,
                cpu_idle=405,
                context_switches=12345,
                processes_started=678,
                pages_in=2468,
                pages_out=1357,
            ),
        )
        self.assertEqual(
            set(sample.to_record()),
            {
                "monotonic_ns",
                "cpu_total",
                "cpu_idle",
                "context_switches",
                "processes_started",
                "pages_in",
                "pages_out",
            },
        )

    def test_eleven_samples_map_deterministically_to_one_packet(self):
        samples = [
            HostSample(
                monotonic_ns=1_000_000 * i,
                cpu_total=100 + 10 * i,
                cpu_idle=50 + 4 * i,
                context_switches=1000 + 7 * i,
                processes_started=20 + i,
                pages_in=200 + 3 * i,
                pages_out=300 + 2 * i,
            )
            for i in range(11)
        ]

        first = packet_from_samples(3, samples)
        second = packet_from_samples(3, samples)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 256)
        self.assertEqual(first[:4], b"HST1")

    def test_packet_mapping_rejects_counter_reversal(self):
        samples = [
            HostSample(i, 100 + i, 50 + i, 1000 + i, 20 + i, 200 + i, 300 + i)
            for i in range(11)
        ]
        samples[7] = HostSample(7, 90, 57, 1007, 27, 207, 307)

        with self.assertRaisesRegex(ValueError, "counter reversal"):
            packet_from_samples(0, samples)

    def test_packet_mapping_rejects_nonmonotonic_time(self):
        samples = [
            HostSample(i, 100 + i, 50 + i, 1000 + i, 20 + i, 200 + i, 300 + i)
            for i in range(11)
        ]
        samples[7] = HostSample(6, 107, 57, 1007, 27, 207, 307)

        with self.assertRaisesRegex(ValueError, "monotonic"):
            packet_from_samples(0, samples)
    def test_artifact_retains_raw_samples_and_hashed_packets_without_host_identity(self):
        samples = [
            HostSample(
                monotonic_ns=1_000_000 * i,
                cpu_total=100 + 10 * i,
                cpu_idle=50 + 4 * i,
                context_switches=1000 + 7 * i,
                processes_started=20 + i,
                pages_in=200 + 3 * i,
                pages_out=300 + 2 * i,
            )
            for i in range(21)
        ]

        artifact = artifact_from_samples(samples, cadence_ns=1_000_000)

        self.assertEqual(artifact, artifact_from_samples(samples, cadence_ns=1_000_000))
        self.assertEqual(artifact["artifact_version"], 1)
        self.assertEqual(artifact["scope"], "host channel only; no organisms")
        self.assertEqual(artifact["sample_count"], 21)
        self.assertEqual(artifact["samples"], [sample.to_record() for sample in samples])
        self.assertEqual(len(artifact["packets"]), 2)
        self.assertEqual([packet["window_index"] for packet in artifact["packets"]], [0, 1])
        self.assertTrue(all(len(packet["data_hex"]) == 512 for packet in artifact["packets"]))
        self.assertTrue(all(len(packet["sha256"]) == 64 for packet in artifact["packets"]))
        self.assertNotIn("hostname", artifact)
        self.assertNotIn("wall_clock", artifact)

    def test_producer_requires_complete_packet_windows(self):
        samples = [
            HostSample(i, 100 + i, 50 + i, 1000 + i, 20 + i, 200 + i, 300 + i)
            for i in range(12)
        ]

        with self.assertRaisesRegex(ValueError, "1 modulo 10"):
            artifact_from_samples(samples, cadence_ns=1)


if __name__ == "__main__":
    unittest.main()
