# Registered Retained-Trace Encoding Diagnostic

## Status and purpose

This diagnostic is frozen before any alternative encoding is computed. It uses only the retained, independently audited one-hour trace at `results/host-compressibility-long-window-360001x10ms.json`; no new acquisition, workload intervention, organisms, ecology, or transform choice is introduced.

The fixed-width HST1 payload remained uniformly RLE-favouring despite measured host activity. This diagnostic separates two explanations:

1. **mapping-dominated morphology:** fixed-width little-endian zero padding suppresses transform-accessible variation that appears under prospectively specified alternative projections of the same deltas; or
2. **no detected morphology under the registered alternatives:** none of the three fixed alternatives reveals switching or practical block drift.

Both outcomes are reportable. All three alternatives are mandatory and will be reported regardless of result. No fourth encoding, changed threshold, changed grouping, or selected subset may be added after inspection and included in this diagnostic.

These are diagnostic projections, not candidate organism couplings. Full-trace normalization uses future information; low-byte projection is lossy; and variable-width encoding changes packet length. A positive result would localize the fixed-width null to the mapping. It would not authorize an organism assay or establish an online, biologically open encoding.

## Frozen source and packet grouping

- Source artifact SHA-256: `623f59af1b6dd76a0f050337345881b93059981547ffe96a89eaa8b9a3a57c5f`.
- Source records: 360,001 retained parsed samples, already independently matched to exact allowlisted `/proc` lines.
- Counter order: `cpu_total`, `cpu_idle`, `context_switches`, `processes_started`, `pages_in`, `pages_out`.
- Interval order: ten adjacent sample deltas per packet, preserving the original 36,000 packet windows and acquisition order.
- Each mapping receives the same 60 nonnegative counter deltas per packet before encoding.
- Counter reversal, record-count mismatch, source hash mismatch, or packet-window mismatch is `INVALID`.
- Primary transforms: existing live lossless RLE and DIFF+RLE implementations, applied to the encoded bytes with reconstruction required.
- The original fixed-width 240-byte payload is retained as the audited reference and is not recomputed into the diagnostic classification.

## Mandatory alternative mappings

### A. Full-trace per-field min–max normalization (`NORMALIZED_U8`)

For each of the six fields, compute `min_f` and `max_f` across all 360,000 retained interval deltas. For delta `x`:

- if `max_f == min_f`, encode byte `0`;
- otherwise encode nearest-integer half-up
  `floor((255 * (x - min_f) + floor((max_f - min_f)/2)) / (max_f - min_f))`.

Emit one byte per delta in interval-major, field-minor order: exactly 60 bytes per packet. Retain every field's fitted minimum and maximum. This is a hindsight diagnostic and cannot be called an online mapping.

### B. Canonical unsigned LEB128 (`ULEB128`)

Encode each nonnegative integer delta independently as canonical unsigned LEB128: seven payload bits per byte, low group first, high continuation bit set on every nonfinal byte; integer zero is one byte `0x00`. Concatenate the 60 self-delimiting encodings in interval-major, field-minor order. No header, field label, length table, packet index, or padding is added. Packet lengths may vary.

### C. Low-order byte projection (`LOW_U8`)

Encode each delta as `x mod 256`, one byte per delta in interval-major, field-minor order: exactly 60 bytes per packet. This intentionally discards higher bits and is diagnostic only.

## Frozen endpoints

For every packet and mapping, retain:

- encoded length and SHA-256;
- exact RLE and DIFF output lengths;
- successful reconstruction of the encoded bytes;
- byte reduction by transform;
- exact compression fraction `(input_length - output_length) / input_length`;
- unique smaller-output winner or `TIE`.

Partition each mapping in acquisition order into the existing:

- 120 non-overlapping 30-second slices of 300 packets; and
- twelve non-overlapping five-minute blocks of 3,000 packets.

For every slice and block, report winner counts and exact median compression fractions using the existing nearest-index median rule after exact rational ordering.

### Switching criterion

A mapping is `SWITCHING` only when:

1. RLE and DIFF each uniquely win at least 3,600 of 36,000 packets; and
2. RLE is the strict majority winner in at least one five-minute block; and
3. DIFF is the strict majority winner in at least one five-minute block.

### Block-drift criterion

A mapping is `BLOCK_DRIFT` when, for either transform, the range across the twelve exact five-minute median compression fractions is strictly greater than `1/15` (the fixed-width practical threshold `16/240`).

A mapping may satisfy neither, one, or both criteria. Thirty-second summaries and rare tails are descriptive and cannot override these rules.

## Diagnostic classification

After all three mappings are reduced, return exactly one:

- `MAPPING_DEPENDENT_SIGNAL`: at least one alternative satisfies `SWITCHING` or `BLOCK_DRIFT` while the audited fixed-width reference satisfied neither.
- `NO_SIGNAL_UNDER_REGISTERED_ALTERNATIVES`: none of the three alternatives satisfies either criterion.
- `INVALID`: integrity, source binding, transform reconstruction, mapping contract, packet count, or mandatory-output completeness fails.

No best encoding is selected. Results for all mappings, including failures and expansions, remain in the artifact.

## Claim boundary

- **Measured:** morphology of three fixed diagnostic projections of one retained trace.
- **Inferred if positive:** the original fixed-width null is mapping-dependent under at least one registered diagnostic projection; the retained host deltas contain structure that the fixed mapping did not expose at the registered endpoint.
- **Inferred if negative:** no switching or practical five-minute drift was detected under these three registered projections.
- **Not established:** that the host intrinsically has or lacks exploitable structure; that any alternative is causal, online, invertible to source counters, biologically open, or suitable for organisms; lagged predictability; fitness; adaptation; cross-host generality.

An independent reducer must verify the source hash, recompute all three mappings and transforms without trusting producer summaries, and audit the final classification.
