# Independent Audit — Retained-Trace Encoding Diagnostic

## Verdict decomposition

- **Artifact integrity:** PASS / VALID.
- **Independent numeric reconstruction:** PASS.
- **Registered classification:** `NO_SIGNAL_UNDER_REGISTERED_ALTERNATIVES`, independently reproduced.
- **General implementation conformance at the audited commit:** FAIL.

The reducer at result commit `9e0b94e` implemented “strict majority” as plurality over `RLE`, `DIFF`, and `TIE`. A block with counts 1,200/1,000/800 would therefore have been incorrectly treated as an RLE-majority block, although 1,200 is not more than half of 3,000.

This defect had **zero effect on the retained result** because every observed block had zero ties. Reapplying the registered `>1,500` rule independently leaves every mapping criterion and the final classification unchanged.

## Independent reconstruction

The auditor did not import the producer reducer. From all 360,001 retained records it independently recomputed:

- 360,000 intervals;
- 2,160,000 nonnegative field deltas;
- 36,000 packets under each of three mappings;
- 108,000 encoded packets total;
- 216,000 transform outcomes.

There were zero discrepancies in encoded lengths, packet SHA-256 hashes, RLE and DIFF output lengths, byte reductions, exact rational compression fractions, reconstruction, packet winners, all 360 thirty-second summaries, all 36 five-minute summaries, nearest-index medians, median ranges, observed criteria, or final classification. All retained parsed records also matched their exact allowlisted `/proc/stat` and `/proc/vmstat` lines.

Normalization bounds matched:

| Field | Minimum | Maximum |
|---|---:|---:|
| `cpu_total` | 0 | 121 |
| `cpu_idle` | 0 | 61 |
| `context_switches` | 0 | 396 |
| `processes_started` | 0 | 7 |
| `pages_in` | 0 | 128 |
| `pages_out` | 0 | 1680 |

## Exact scientific result

### `NORMALIZED_U8`

- Length: 60 bytes for all packets.
- Winners: RLE 14,472; DIFF 21,528; ties 0.
- DIFF was strict-majority winner in all twelve five-minute blocks; RLE in none.
- RLE positive compression: 24 packets; expansion: 35,976.
- DIFF positive compression: 22 packets; expansion: 35,978.
- RLE block median: `-1/3` throughout; range 0.
- DIFF block medians: `-19/60` or `-17/60`; range `1/30`.
- No registered switching and no block drift.

Packet-level winner diversity therefore indicates mostly which transform expanded less, not alternating positively compressible regimes.

### `ULEB128`

- Lengths: 60 bytes × 35,842; 61 × 146; 62 × 7; 63 × 5.
- Winners: RLE 36,000; DIFF 0; ties 0.
- RLE positive/zero/negative reduction: 14,083 / 7,350 / 14,567.
- DIFF positive/negative: 19 / 35,981.
- RLE block median: 0 throughout; DIFF range `1/30`.
- No switching and no block drift.

### `LOW_U8`

- Length: 60 bytes throughout.
- Winners: RLE 36,000; DIFF 0; ties 0.
- RLE positive/zero/negative reduction: 14,080 / 7,372 / 14,548.
- DIFF positive/negative: 19 / 35,981.
- RLE block median: 0 throughout; DIFF range `1/30`.
- No switching and no block drift.

## Provenance

The immutable parent chain is:

`d340e08` registration → `13e46cb` implementation → `9ccb36b` manifest → `9e0b94e` result.

Hashes verified:

- Source trace: `623f59af1b6dd76a0f050337345881b93059981547ffe96a89eaa8b9a3a57c5f`
- Pre-execution manifest: `5f21091a33c04b402a1693afb5cc8b023e04404c708c77e81be1530cda4cfe16`
- Result: `81180c2da5264bd2d00ea66d78e3763df301b50e059fc2e97dd5363c402bd884`

## Post-audit correction

The implementation now defines strict majority as `winner_count * 2 > total_block_count`, with a regression covering the auditor’s tie-rich counterexample. Running the corrected reducer on the retained source produced a byte-identical result with the same SHA-256 as the historical artifact. The historical source manifest remains a record of the original reducer; current tests verify the corrected current implementation without pinning the working tree to that historical hash.

## Claim boundary

**Measured:** three registered projections removed or altered the fixed-width morphology, but none met the registered sustained-switching or practical block-drift endpoint.

**Inferred:** fixed-width zero padding caused the original positive RLE richness; removing it did not reveal sustained positively compressible transform regimes under these three projections.

**Not established:** intrinsic absence of host structure, suitability of any projection as an online coupling, lagged predictability, organismal use, fitness effects, or cross-host generality.
