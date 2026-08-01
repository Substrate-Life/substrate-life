# Independent Audit — Exploratory Host-Compressibility Cheap Gate

## Verdict

**FAIL for provenance/registration; arithmetic `NARROW_STABLE` is correct.**

The independent read-only audit decoded all 300 retained packet hex strings and reimplemented RLE and DIFF without trusting stored outcomes or summaries. All packets were 256 bytes, matched their retained SHA-256 values, reconstructed byte-for-byte from the 3,001 retained raw records, and had valid sequential HST1 headers and windows. All 1,200 stored per-packet transform outcomes matched the independent recomputation.

## Exact recomputed distributions

### Primary 240-byte payload

- Winners: RLE 300, DIFF 0, TIE 0
- Six contiguous 50-packet block majorities: RLE, RLE, RLE, RLE, RLE, RLE
- RLE reduction histogram: `{106: 1, 116: 3, 120: 292, 124: 2, 136: 1, 140: 1}`
- DIFF reduction histogram: `{41: 1, 55: 3, 61: 292, 67: 2, 85: 1, 91: 1}`
- RLE `(min, p10, median, p90, max)`: `(106, 120, 120, 120, 140)`; p90−p10 `0`
- DIFF `(min, p10, median, p90, max)`: `(41, 61, 61, 61, 91)`; p90−p10 `0`

### Secondary 256-byte whole packet

- Winners: RLE 300, DIFF 0, TIE 0
- Six contiguous 50-packet block majorities: RLE, RLE, RLE, RLE, RLE, RLE
- RLE reduction histogram: `{98: 1, 108: 3, 110: 42, 112: 246, 114: 4, 116: 2, 128: 1, 132: 1}`
- DIFF reduction histogram: `{29: 1, 43: 3, 47: 41, 49: 247, 51: 4, 55: 2, 73: 1, 79: 1}`
- RLE `(min, p10, median, p90, max)`: `(98, 110, 112, 112, 132)`; p90−p10 `2`
- DIFF `(min, p10, median, p90, max)`: `(29, 47, 49, 49, 79)`; p90−p10 `2`

Both scopes satisfy the stated arithmetic rule: the dominant class is at least 270/300 and both reduction spans are at most 16 bytes. The 16-byte header did not determine the verdict.

## Blockers and qualifications

1. **High provenance blocker.** The prediction/result, probe, tests, and artifact were uncommitted. The prediction was absent from `HEAD`; prediction and result occupied the same mutable report diff; and the artifact had no commit/source manifest, command line, or first-attempt binding. Therefore “recorded before capture,” “registered,” and “not retuned” cannot be independently established. Session ordering is not an archival control.

2. **Unstable report boundary.** The report changed during audit. Probe and artifact remained stable during audit:
   - probe SHA-256: `8cfca401900e06f5c7884b43422ab9aa9a465ea6b01fce99109e91fd7f815f8a`
   - artifact SHA-256: `a9d4c552a017d804a5687796c4ca04088e2793561bb286936e47d8edb62950a5`

3. **CPU accounting defect.** The capture source used `cpu_total=sum(cpu)`, double-counting Linux guest and guest-nice fields. Guest counters were zero throughout this recording, so the defect had zero numerical effect on this trace. The parser was corrected prospectively after the audit; that correction does not upgrade the retained trace's provenance classification.

4. **Incomplete invalid-attempt provenance.** The artifact lacks an explicit parse-status field and interrupted-capture/`INVALID` record. The permissive parser also does not reject duplicate fields. These defects did not alter this complete trace but would block a fail-closed environmental gate.

5. **Privacy.** No allowlist violation was found. Every record contained only aggregate `cpu`, `ctxt`, `processes`, `pgpgin`, and `pgpgout`; the artifact was mode `0600`. No hostname, wall clock, PID, device, network, or command-line data were retained. Boot-relative monotonic timestamps and aggregate workload remain potentially sensitive telemetry within the declared allowlist.

## Claim boundary

- **Measured:** this retained approximately 30-second, one-host, 10-ms trace under the captured fixed-width mapping was uniformly RLE-favouring and met the stated `NARROW_STABLE` arithmetic.
- **Exploratory inference:** this trace was not switching-capable under the stated criteria.
- **Not established:** prospective confirmation, absence of retuning, behavior across time or hosts, behavior under the corrected mapper, alternative counters or cadences, temporal-null prediction, organisms, fitness, or host-information incorporation.

Nine focused mapping/classifier tests passed during the audit. The auditor modified no files.
