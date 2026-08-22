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
- verified all seven embedded `source_manifest_sha256` entries against the
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

## Re-verification by a second auditor (2026-08-22, later session)

An independent verifier was written that reads only the retained artifact,
the pre-execution manifest, and the current bytes of `src/` — it imports
none of the runner's or builder's code and trusts no `gate_analysis` field.
All 183 checks pass; the verdict above is unchanged. Corrections and
additions relative to the original audit text:

- *Correction.* The source manifest embeds **seven** entries, not six as
  originally stated (the runner hashes itself plus six modules). All seven
  match the current files, as do the four pre-execution-manifest entries.
- *Reversal-charge derivation (new).* From the frozen cost functions:
  `transform_cost(E)=3+(E+63)//64`, giving `4` for extents 20 and 64 and
  `5` for extent 80; ordinary upkeep after the 256→172 forage is
  `1/10 + 172/640 = 59/160`. Each committed E1 reversal therefore nets
  `−699/160` in `S` plus its stored-provenance debits (`75/4` and `25/2`
  LOW; `25/4` and `50` HIGH at extent 20), and the failed extent-80
  attempt costs exactly `5 + 59/160 = 859/160` — the registered E2 charge —
  with `R`, packet, and memory snapshots byte-identical across the failure.
- *Provisioning-law cross-check (new).* The mechanics provision
  `P=(T/D)·R_w` with `R_w` the parent's `R` at DIVIDE, and parent `R`
  carries across cycles. This law reproduces, exactly and without fitting:
  the Block A endowments (`26432/1275`, `60032/1275`); all three Block B
  provisions per arm — LOW `(26432/1275, 10097024/325125, 26432/1275)`,
  HIGH `(60032/1275, 22932224/325125, 60032/1275)` — including the
  second-cycle founder provision, which follows from carried
  `R = 52451/2550` (LOW) and `59563/1275` (HIGH), the very values Block E2
  registers before its reversal attempt; and the grandchild provision,
  which repeats the founder endowment because a newborn starts at
  `R_birth=0`.
- *Token-scan classification (new).* The only hidden-gate token hits in
  the seven frozen sources are: the gate-10 detail strings themselves;
  the registered hazard comparison `hazard_rng.random() < float(rate)`
  (zero hazard configured; no death event in any fixture; hazard is a
  registered mechanism, not a viability rule); `MUTATION_DELETION`, an
  unused legacy-mutation constant (mutation disabled, no mutation RNG
  exists in the executed path); and a literal `"displacements": 0`
  counter. `stage7_slice1.py` and `transforms.py` — the ledger mechanics —
  contain no hits.
- *Recount provenance notes (new).* Successful packet captures are not
  directly logged; the registered Block D capture count is verified
  structurally (one offer per tick, four logged `org-1` failures at ticks
  0–3, four logged `org-0` full-census rejections each requiring a
  completed capture-and-work cycle). Block B newborn identity, order,
  ticks, and provisions were recounted from raw `birth_admitted` events.

## Re-verification by a third auditor (2026-08-22, subsequent session)

A fresh verifier was again written from scratch against the retained
artifact, the pre-execution manifest, frozen git objects, and current
`src/` bytes; it imports none of the runner or builder code and trusts
no `gate_analysis` field. All 225 checks pass; the verdict above is
unchanged. Checks not already listed in the passes above:

- *Programme-spec hash origin.* The registered
  `5ddbf276…c344` was **recomputed** as the SHA-256 of the §2.1
  canonical JSON under compact serialisation (both key orders agree),
  not merely compared to the stored string.
- *Freeze provenance.* Each of the seven manifest sources is
  byte-identical to its blob at freeze commit `e2f580b` (read from git
  objects, not the working tree alone), and all four pre-execution
  manifest entries match current bytes.
- *Per-stage ledger identities (gate 4, structural).* In Block A each
  consecutive checkpoint pair satisfies, exactly: forage step
  `ΔS = (1−A/D)·Y − ΔC_S`, `ΔR = (A/D)·Y − ΔC_R`; ALLOC/COPY steps debit
  only `ΔC_S`/`ΔC_R` on their own accounts; DIVIDE step
  `ΔR = −ΔC_R − P` with `P` equal to the child endowment — direct-debit
  isolation holds without any fitted constant. `R_w` recovered as
  `P·D/T` reproduces the registered `413/10` and `469/5`.
- *Closure recomputation.* The §5.1 equation was recomputed as exact
  `Fraction` at all 22 named checkpoints across A/C/E1/E2 (not by
  trusting `closed` booleans), the memory-pool sum at each of them, and
  the B/D aggregates including founder inputs (`100 + net_income − costs
  = live_reserves + destroyed`). All close exactly.
- *E-block decomposition.* E2: `Δparent_S = −859/160 = −ΔC_S` with
  parent `R` and packet fields identical. E1 extent-20: movement
  reproduces the stored-provenance split plus charge,
  `ΔS = −ΔC_S − (drawn_S share)·125/4`, `ΔR = −(drawn_R share)·125/4`.
- *Block B recount.* Raw-event provisions equal the second auditor's
  triples per arm; the first provision equals the same arm's Block A
  endowment and the grandchild repeats it.
- *Hygiene scans.* Token scan of the frozen sources reproduced (only
  gate-10 detail strings, the legacy `MUTATION_DELETION` constant, the
  registered hazard comparison at `stage7_slice2.py:327`, and a
  `"displacements": 0` counter; ledger files clean). No forbidden
  analysis fields exist anywhere in the artifact; value-level mentions
  of fitness/optimum/ESS occur only inside negated scope prose.