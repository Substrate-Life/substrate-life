# Stage 7B0 deterministic execution note

## Why the execution protocol changed

The published Stage 7B0 preregistration is preserved unchanged, but its one-use execution machinery is superseded for this stage.

Stage 7B0 is a deterministic, mutation-disabled mechanism trace with fixed treatments, packet identities, packet schedules, and ticks. Selective seed reporting, stochastic fishing, and inferential endpoint choice are absent. The appropriate guarantee is therefore reproducibility: publish the code and raw result, then verify that rerunning the code produces identical bytes.

The one-use lease, filesystem claim, detached digest pin, operator authorization phrase, append-only journal, and custom JSON-Schema engine were removed from the active Stage 7B0 path. Those controls remain appropriate candidates for stochastic Stage 7B1, where seed choice and an inferential endpoint create the threats they address.

The safeguards retained here are:

- the original preregistration and its protocol digest;
- a plain manifest of source-file hashes;
- static mechanics and adversarial reducer tests;
- raw checkpoint, transition, account, packet, memory, census, and identity evidence;
- an independent reducer that reconstructs every reported gate;
- preservation of failed/invalid runs;
- direct byte-for-byte reproduction.

## Retained execution history

No Stage 7B0 block had run before the execution path was simplified.

### Attempt 1 — INVALID instrumentation

- Artifact: `results/stage7b0-channel-result.json`
- SHA-256: `b9eb4b893b1e746cc5361cb26ca8025b0980d9055ef725c547a1a1046eb49613`
- Size: 7,967,420 bytes
- Outcome: `INVALID`
- Diagnostic: `packet state detached from account events A.LOW.0`

The producer's block-level checkpoint retained a live reference to `organism.events`; later events mutated the nominal INITIAL snapshot. The independently retained checkpoint boundary was correct. Snapshot construction was changed to copy the event prefix, and a regression test was added. This was an evidence-construction defect, not a measured mechanism failure.

### Attempt 2 — FAIL under defective reducer

- Artifact: `results/stage7b0-channel-result-attempt2.json`
- SHA-256: `0cbbfd905d11c7d81f0cc50be3edbbf2970ae99c80bed1c3c207de2571f1973f`
- Size: 9,691,866 bytes
- Outcome as retained: `FAIL`

All checks except `direct_debit_isolation` passed. The reducer's S-domain whitelist omitted the ordinary direct charges `READ` and `TRANSFORM_COMPRESS_*`, so it rejected those registered somatic debits in every relevant block. A pure reducer regression was added. The unchanged attempt-2 raw evidence re-reduced to `PASS` on all ten gates after that correction. The retained attempt-2 artifact remains unchanged and records the original reducer result.

### Final canonical result — PASS

- Artifact: `results/stage7b0-channel-result-final.json`
- SHA-256: `4c5cf3d0b4972b6eeb3f5547c01810a0284c8af9ee8ca3091b2af869ce1502e6`
- Size: 3,545,674 bytes
- Scientific source commit: `764615e2aa8fac0b477ea580f15657e1f6226bd8`
- Plain manifest SHA-256: `b4f7f9869199a6b58076fcf3ee75c5aaf406f137ed629733b9680f8abcffd5b2`
- Decision: `PASS`

Every registered block passed: A, B, C, D1, D2, E1, and E2.

Every reconstructed gate passed:

- realised treatment;
- programme identity;
- allocation identity;
- direct-debit isolation;
- reversal provenance;
- recovery;
- lifecycle;
- topology;
- closure;
- no hidden gate.

The D1/D2 label-permutation cross-check also passed. Mutation was disabled and the recorded mutation RNG draw count was zero.

## Reproduction

From the repository root:

```bash
python3 src/run_stage7b0_channel.py \
  --output /tmp/stage7b0-reproduction.json
sha256sum /tmp/stage7b0-reproduction.json
cmp results/stage7b0-channel-result-final.json \
    /tmp/stage7b0-reproduction.json
```

Observed reproduction SHA-256:

```text
4c5cf3d0b4972b6eeb3f5547c01810a0284c8af9ee8ca3091b2af869ce1502e6
```

`cmp` returned success: the independent rerun was byte-identical to the canonical artifact.

## Claim boundary

**Measured:** under the fixed Stage 7B0 fixtures, all registered mechanism checks and closure checks pass for both fixed treatments, and the result is byte-reproducible.

**Not measured:** selection, invasion, evolutionary stability, stochastic capture performance, or comparative fitness. Those remain outside Stage 7B0.
