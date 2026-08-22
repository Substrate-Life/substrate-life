# Independent Audit — Stage 7B0 Scripted Allocation-Channel Result Pair

## Verdict

**PASS — valid classified mechanism result.**

The retained artifact `results/stage7b0/stage7b0-result.json`
(SHA-256 `00315fab10217912d1bd02c965bdbc6cd69df9f67f53b95900d01feb791ebddf`,
44,809 bytes) is mechanically valid and independently reproducible from the
frozen source. All ten registered gates of preregistration §7 hold under
independent recomputation, and every registered §6 exact value reproduces
from the raw checkpoints without importing the runner's gate-analysis code.

## Independent reconstruction

Without importing `run_stage7b0.py`'s analysis path, the auditor:

- rehashed the retained artifact and confirmed identity with the recorded
  SHA-256;
- verified all six embedded `source_manifest_sha256` entries against the
  current files in `src/` (all match);
- confirmed the programme-specification hash equals the registered
  `5ddbf276aa0a836672b1b3011e66974ce9ecd6fedb0758a111c95766f534c344` in
  both arms (gate 2);
- reparsed every rational string to exact `Fraction` and recomputed,
  per arm:

### Block A

- `Y = 525/4`, `C_S = 879/40`, `C_R = 56/5` at the registered checkpoints
  (exact in LOW and HIGH);
- child endowments `26432/1275` (LOW) and `60032/1275` (HIGH), with
  `child R_birth = 0` (exact);
- the §5.1 reserve equation
  `parent_S + parent_R + committed_child_S + destroyed =
  opening_S + opening_R + gross_income − reversed_income − C_S − C_R`
  closes exactly in both arms when recomputed independently;
- allocation identity (gate 3): on every live packet state across all
  checkpoints, `drawn_R = (A/D)·(drawn_S+drawn_R)` exactly.

### Block B

Both arms recount identically from tick snapshots and raw events:
3 admitted births, 0 hazard removals, 0 rejected births, 0 evictions,
final census 4; newborn deferral order is `org-1` at tick 0 then two more
at tick 1 — the exact registered two-generation sequence (gate 7).

### Block C

Event sequence contains exactly two `FORAGE_RLE` and two `ALLOC_OFFSPRING`
opportunities with terminal `DIVIDE`; first live-ledger budget is `10`;
failure states are exactly `(6671/80, 7/4)` LOW and `(6531/80, 7/2)` HIGH;
both arms recover without debt or subsidy (gate 6).

### Block D

`org-0`: 4 captures, 4 full-census rejections; `org-1`: 4 capture failures;
0 births, 0 evictions, census 2 — identical counts in D1 and D2, so the
label permutation moves history with scheduler ID `org-0`, not with LOW or
HIGH (gate 8).

### Block E

E1 after extent 20: budget `200`, provenance `60/40` (LOW) and `20/80`
(HIGH); after extent 64: budget fully restored `300`, `drawn_S=drawn_R=0`.
E2: parent `R` and every packet field unchanged across the failed attempt;
parent `S` decreased by exactly `859/160`; failure code
`REVERSAL_ACCOUNT_UNAVAILABLE` (gate 5).

## Gate-claim structural checks

- **Gate 10 (no hidden gate).** A token scan of the frozen sources found no
  clamp, threshold, offspring deletion, displacement, or float viability
  rule participating in any executed path. The literal string
  `OFFSPRING_TROUGH` appears once, inside a *documentation string asserting
  its absence* in the gate-10 detail text (`run_stage7b0.py:256`); it is
  not referenced by any mechanics. No defect.
- **Flags.** `selection_assay_run=false` and `mutation_enabled=false` are
  present at top level and per block.
- **Chronology.** Git history is linear: freeze `e2f580b`
  (13:49:27Z) → retain `a2362d2` (13:51:43Z) → classify/document `36ab24b`
  (14:05:44Z). The freeze precedes the retained execution.
- **Reconciliation.** This audit accepts the `36ab24b` disclosure that an
  earlier 2026-08-01 channel lineage (`7765a59..ac5db2e`) shares thirteen
  registered literals with this run; the present artifact is nonetheless
  the first retained execution across the `f90da66` DIVIDE atomicity fix,
  which is behaviour-neutral here (no memory-blocked DIVIDE arises in any
  registered block).

## Scope

This audit certifies only that the retained artifact was produced by the
frozen sources, satisfies the ten registered gates, and reproduces the
registered calibration values. It establishes nothing about generality
across other `A/T/D` values or programmes, population fitness, selection,
invasion growth, reproductive value, mutation accessibility, plasticity,
optimum, or ESS. Per preregistration §11, a PASS authorises design — not
execution — of Stage 7B1.
