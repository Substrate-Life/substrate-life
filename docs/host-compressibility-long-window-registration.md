# Registered Long-Window Host-Compressibility Probe

## Status and question

This protocol is frozen before capture. It extends the exploratory 30-second observation without changing counters, cadence, packet mapping, transform implementations, or primary payload boundary.

Question: does the same host channel remain structurally narrow over one hour of ordinary host activity, or does compressibility drift on minute-scale blocks while remaining stable inside 30-second slices?

The capture is observational. No workload is started, stopped, selected, or labelled as a treatment. Ordinary concurrent host activity may occur, but “under real load” is not a controlled claim unless separately retained workload provenance establishes it.

## Registered hypothesis

The host channel may vary in wall-clock time while remaining locally constant at the 30-second scale. Specifically, the primary 240-byte payload is predicted to satisfy the existing narrow/stable rule in every non-overlapping 30-second slice, while at least one transform's median byte reduction changes by more than 16 bytes across non-overlapping five-minute blocks.

This would establish wall-clock scale separation in the recorded environmental channel. It would not by itself establish that variation is inaccessible within an organism lifetime. The current simulation has no frozen, validated wall-clock-to-logical-tick coupling, and the 17-tick cycle belongs to a particular superseded conditional programme rather than a universal organism lifetime. A biological timescale-mismatch claim requires a later explicit mapping from recorded packet time/arrival to organism-visible logical ticks, plus realised organism lifetimes and lineage exposure. No such organism assay is authorised here.

## Fixed capture

- Duration: one hour.
- Cadence: 10 ms absolute monotonic deadlines.
- Samples: 360,001.
- Packets: 36,000, each from eleven samples with boundary-only overlap.
- Host fields: aggregate CPU total excluding Linux guest and guest-nice, CPU idle plus iowait, context switches, process starts, page-ins, and page-outs.
- Packet mapping: current HST1 fixed-width mapping.
- Primary bytes: packet offsets `[16:256]`, excluding the analyst-authored header.
- Secondary bytes: full 256-byte packet.
- Lossless transforms: the existing live RLE and DIFF implementations.
- Scope: host channel only; no organisms, population, mutation, reserve, fitness, temporal-null test, or workload intervention.

Exact capture command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 src/host_compressibility_probe.py results/host-compressibility-long-window-360001x10ms.json --sample-count 360001 --cadence-ms 10
```

A pre-execution sidecar records the registration commit, working-tree status, command, and SHA-256 hashes of this protocol, recorder, mapper, transforms, constants, and tests. The unrelated pre-existing modification to `src/test_stage7_slice1.py` is disclosed and excluded from this registration. The first capture attempt and any failure are retained; no overwrite is permitted by the recorder.

## Fixed reduction

Partition the 36,000 packets in acquisition order into:

- 120 non-overlapping 30-second slices of 300 packets;
- 12 non-overlapping five-minute blocks of 3,000 packets.

For each packet and scope, record RLE and DIFF output sizes, byte reductions, and unique winner or tie.

A 30-second slice is **locally narrow/stable** only when:

1. one winner or tie occupies at least 90% of its 300 packets; and
2. both transforms have `p90 − p10 <= 16` reduction bytes, using the probe's fixed nearest-index percentile rule.

Minute-scale **drift** is present only when, across the twelve five-minute blocks, at least one transform's block-median reduction range is greater than 16 bytes. Winner changes are reported but are not required for drift.

Classify the primary result exactly once:

- `TIMESCALE_SEPARATED_DRIFT`: all 120 30-second slices are locally narrow/stable and minute-scale drift is present.
- `LONG_WINDOW_NARROW_STABLE`: all 120 slices are locally narrow/stable and minute-scale drift is absent.
- `WITHIN_30S_VARIATION`: one or more 30-second slices fail the local rule, regardless of longer drift.
- `INVALID`: capture, reconstruction, provenance, packet count, source hash, or parsing fails.

Secondary whole-packet analysis cannot override the primary classification.

## Claim boundary

- **Measured:** retained aggregate counters, timing, packet bytes, transform reductions, winners, and registered block summaries.
- **Inferred if `TIMESCALE_SEPARATED_DRIFT`:** this host channel varied across five-minute blocks while remaining locally narrow in every tested 30-second slice.
- **Inferred if `LONG_WINDOW_NARROW_STABLE`:** no practically large drift was detected over this one-hour trace under the fixed mapping.
- **Not established:** controlled workload dependence, universal host behavior, organismal sensing, lifetime inaccessibility, lineage constancy, fitness, selection, adaptation, or transferability to other host-coupled systems.

No cadence, counter, packet mapping, threshold, transform, slice duration, or block duration is retuned from this trace. Unexpected outcomes remain retained and are classified by the rules above.
