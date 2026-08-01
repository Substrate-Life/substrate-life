# Independent Audit — Registered One-Hour Host-Compressibility Probe

## Verdict

**PASS — valid registered result.**

**Registered classification: `LONG_WINDOW_NARROW_STABLE`.**

The completed capture is mechanically valid and independently reproducible. The preregistered `TIMESCALE_SEPARATED_DRIFT` hypothesis fails because neither transform's five-minute median range exceeds 16 bytes. Attempt 1 remains correctly classified `INVALID`.

## Independent reconstruction

Without importing the reducer, the auditor:

- parsed all 360,001 raw records from retained allowlisted `/proc` lines;
- confirmed every parsed counter record matched those lines;
- reconstructed all 36,000 HST1 packets from eleven-sample windows;
- verified all packet indices, sample boundaries, 256-byte lengths, headers, SHA-256 hashes, and stored packet bytes;
- independently implemented RLE, DIFF+RLE, and the nearest-index percentile rule; and
- found zero packet, metadata, transform-outcome, source-line, sequence, or deadline-sequence mismatches.

### Primary 240-byte payload

- Overall winners: RLE 36,000; DIFF 0; TIE 0.
- All 120/120 nominal 30-second slices had exactly:
  - winners: RLE 300; DIFF 0; TIE 0;
  - median reductions: RLE 120; DIFF 61 bytes;
  - `p90 − p10`: RLE 0; DIFF 0 bytes;
  - local rule: PASS.
- All twelve five-minute blocks had exactly:
  - winners: RLE 3,000; DIFF 0; TIE 0;
  - median reductions: RLE 120; DIFF 61 bytes.
- Five-minute median ranges: RLE 0 bytes; DIFF 0 bytes.
- Drift criterion (`range > 16`): FAIL.
- Final registered classification: `LONG_WINDOW_NARROW_STABLE`.

Thus:

- Capture/integrity gate: PASS / VALID.
- Every-slice narrow/stable gate: PASS.
- Minute-scale drift hypothesis: FAIL.
- `TIMESCALE_SEPARATED_DRIFT` prediction: FAIL.
- Registered decision-rule result: PASS — `LONG_WINDOW_NARROW_STABLE`.

The secondary whole-packet result also had RLE 36,000; DIFF 0; TIE 0 and could not override the primary classification.

## Provenance and chronology

Git establishes a linear pre-capture freeze:

1. `e8d2f515e69cf4c8871e729ca93534e36f253e85` — protocol/recorder registration, `2026-08-01T21:53:04Z`.
2. `3dfb70c0ce6fa4e49538c096b068849973f6cff3` — pre-execution manifest, `21:53:40Z`.
3. `097623957f9c240682633c0ef207d3782a5b0851` — retained invalid attempt record, `21:54:20Z`.
4. Completed raw artifact creation time: `22:54:45Z`.

All 8/8 manifest source hashes matched both the inspected files and exact `e8d2f51` Git blobs. Key identities:

- Manifest: `e9dea1b823ad5d17ce3537f7f14ad3b96460a84ed02edcaf8a5f5da89c96dd6f`.
- Raw capture: `623f59af1b6dd76a0f050337345881b93059981547ffe96a89eaa8b9a3a57c5f`.
- Gate result: `755bb9c720c04d0d49b7539580abba97f0cef4269129f6d3ea1ecef295281319`.
- Integrity diagnostics: `24096be1d9a117f0980c1153029adba77ee1287083375660167d049a36567d6f`.

Attempt 1 is `INVALID`, not scientific FAIL. It produced no raw artifact because the recorder writes only after successful completion. The manually retained invalid record correctly discloses that retention defect.

At the auditor's initial workspace inspection, the completed raw artifact and reducer outputs had not yet been committed, and the raw artifact did not embed manifest/source hashes. During the read-only audit, those exact stable bytes were committed at `30753c9` without modification. The audit's numerical and hash verdict applies to the committed artifacts. The absence of an embedded manifest remains a weaker command-to-artifact binding than a self-contained artifact, but Git proves the protocol and manifest existed before capture.

## Timing and missed deadlines

- Nominal deadline span: 3,600,000,000,000 ns.
- First-to-last read-end elapsed: 3,599,999,816,288 ns.
- Wake lateness min/median/p90/max: 1,800 / 108,654 / 147,408 / 587,245,508 ns.
- Samples waking at least one 10 ms cadence late: 187.
- Longest consecutive late run: 59 samples.
- Read-end interval min/median/p90/max: 103,741 / 9,999,151 / 10,107,039 / 606,801,359 ns.
- Intervals below 1 ms: 193.
- Intervals above 20 ms: 7.
- Individual packet-window duration range: 1,251,118–617,875,204 ns.
- Actual 300-packet slice spans: 29,999,345,180–30,000,610,966 ns.
- Actual 3,000-packet block spans: 299,999,802,162–300,000,222,874 ns.

Absolute deadlines correctly caused catch-up sampling after delays. Because the frozen protocol did not register deadline misses as an invalidity condition, this is a PASS with timing limitation, not `INVALID`.

## Privacy, workload, and scope

- Privacy gate: PASS.
- Exact raw schemas were uniform.
- Only aggregate `cpu`, `ctxt`, `processes`, `pgpgin`, and `pgpgout` lines were retained.
- No hostname, machine ID, PID, command line, path, network/device identifier, credential, or organism state was present.
- Artifact permissions were `0600`.
- Boot-relative monotonic timing and aggregate workload counters remain sensitive telemetry, though not direct host identifiers.
- CPU guest/guest-nice were zero in all samples; `sum(cpu[:8])` excluded the separate guest fields.
- Aggregate activity was measured: context-switch delta 2,385,332; process starts 113; page-ins 2,412; page-outs 64,192. There is no controlled workload provenance.

Therefore one passive host trace is established. “Under real load,” controlled workload dependence, organisms, sensing, logical-tick exposure, fitness, adaptation, selection, and cross-host generality are not established.

Focused tests passed 12/12. The auditor created or modified no files. The disclosed pre-existing `src/test_stage7_slice1.py` modification was ignored and remained unchanged.
