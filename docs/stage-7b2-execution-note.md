# Stage 7B2 retained execution note

## What ran

The single authorised execution class of `docs/stage-7b2-preregistration.md`
§8.3 was executed once, on 2026-08-22, under the freeze committed at
`27f5700` with `results/stage7b2/pre-execution-manifest.json`:

- `src/run_stage7b2.py` — the seeded, mutation-disabled confirmatory suite,
  `k = 32` replicates (`hazard_seed = 20260822 + i`), registered §2
  configuration (`r=5`, `d=64`, `N=12`, `W=600`, single hazard arm
  `h = 1/120`, genotypes `(102,128,255)` and `(204,128,255)`, founders 3 per
  genotype, corpse TTL 2).
- `src/reduce_stage7b2.py` — the §5 decision rule applied exactly once.

Retained artifacts:

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `results/stage7b2/stage7b2-result.json` | 1,887,200 | `268d37e5bc1be84a5147413b960957b3c14cea3e647fafd6f6cf440648e668aa` |
| `results/stage7b2/stage7b2-reduced.json` | 11,812 | recorded against the raw hash inside the file (`consumed_raw_artifact`) |

## Integrity verification performed before retention

- Freeze intact: every file in the pre-execution manifest re-hashes to its
  registered SHA-256 and byte size immediately before the run.
- Full unittest discovery green at run time: 162 tests OK (4 skipped, the
  same environment-dependent skips as at the freeze commit).
- All 32 replicates classified `COMPLETE`; zero `INVALID_IMPLEMENTATION`
  runs; zero `BUFFER_OVERFLOW` triggers (maximum observed buffered
  occupancy 2 packets against depth 64; the no-eviction guard never fired).
- Ledger conservation asserted after every operation and re-scanned at every
  tick-complete checkpoint (602 checkpoints per replicate); no checkpoint
  failure occurred in any replicate.
- The reducer independently recomputed every estimator from the raw
  artifact's retained records: `recomputation_bit_exact: true`,
  `mismatch_count: 0`.
- The raw artifact's embedded source-manifest hashes match the freeze
  manifest for every shared entry, and the working-tree
  `src/stage7b1_mechanics.py` is byte-identical to commit `62f2672`
  (SHA-256 `61572690…`), as the freeze disclosed.

## Registered outcome (§5 rule, applied once)

- Pair-contrast class: **`DEGENERATE_REPLICATION`** (0 complete pairs of 32;
  fewer than the registered minimum of 16).
- Subcritical report (alongside): **`BOTH_SUBCRITICAL`** — each genotype has
  `L(0) ≤ 1` in all 32 of its replicates.
- Per §5 this yields **no contrast conclusion**. Descriptive distribution
  facts only, exact fractions from the reduced artifact: `L(0)` median
  `17/800` (max `64/1225`, min `0`) for genotype A=102 and `1/100`
  (max `1/6`, min `0`) for A=204; establishment events per replicate
  (both genotypes combined) between 3 and 12. These are descriptions of the
  registered outcome, not fitness, selection, or superiority claims of any
  kind.

## Consequence mandated by the registration

§5 binds this outcome to the repair policy: `DEGENERATE_REPLICATION`
"triggers repair-policy review of the registration (a further superseding
preregistration), never post hoc reinterpretation." Accordingly:

- No parameter of the Stage 7B2 registration is retuned, reinterpreted, or
  widened here.
- The next dependency-ordered step is drafting a superseding
  preregistration under the repair policy (or standing down), which must be
  committed before any new implementation freeze or execution.
- Both artifacts above are retained unchanged; neither may be modified.
