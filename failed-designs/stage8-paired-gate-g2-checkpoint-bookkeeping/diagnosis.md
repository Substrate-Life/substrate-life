# FAILED DESIGN RECORD — Stage 8 paired-arm §7 gate, G2 checkpoint-bookkeeping mismatch

*Archived 2026-08-23 per `docs/stage-8-alpha-evolution-repair-preregistration.md`
§7 ("If any condition fails: no freeze; a further superseding preregistration
with diagnosis, archived under `failed-designs/`, never deleted"). This record
is permanent; the design it describes is superseded, not deleted.*

## What ran

The binding §7 feasibility gate (`src/stage8_paired_gate.py --workers 2`) on
the fixed 12-pair shakedown table `20421301 + j`, both arms per pair,
`W = 2400` — the first full-window execution of the Stage 8 measurement layer
(the cancelled generation's chain was blocked before its gate ever ran, so no
full-window execution had ever occurred). Wall clock ≈ 1 h 58 m. Artifacts:
`gate-summary.json` (the gate's complete stdout summary) and `gate-stdout.log`
in this directory. Nothing was retained under `results/`; the shakedown is
exploratory and stdout-only by registration.

## Outcome

- `pairs_both_arms_complete`: **12/12**; zero `INVALID_IMPLEMENTATION`; zero
  `BUFFER_OVERFLOW`.
- **G1 PASS** — 12/12 pairs with ≥ 1 recorded mutation event and ≥ 2 distinct
  `A` values at tick W in Arm M; zero genome-freeze violations anywhere.
- **G2 FAIL** — `checkpoint_failures = 24` (every arm): the tooling requires
  `tick_checkpoints == window_ticks + 1` (= 2401); every arm recorded a
  different count.
- **G3 PASS** — zero kernel audit failures; full re-execution of seed
  20421301 Arm M bit-identical (`reexecution_identical: true`).
- **G4 PASS** — R0 kernel-absence clean on all arms; zero seed mismatches.

## Diagnosis (verified against source and by direct probe)

**The registered condition holds; the tooling's operationalization of it is
wrong.** G2's substance is "every ledger closes at every checkpoint in every
arm". The byte-frozen assertion machinery verifies live ledgers after *every*
operation and rescans the full immutable history at every tick-complete
checkpoint; any failure would have raised and classified the run
`INVALID_IMPLEMENTATION`. None did. What failed is a derived bookkeeping
expectation:

1. `Stage7B2Population.__init__`
   (`src/stage7b2_population.py:164`) calls `self.assert_all_ledgers("initial")`.
2. Its parent `Stage7B1Population.__init__`
   (`src/stage7_slice2.py:91`) has already called it once.
3. `assert_all_ledgers` appends one closure entry at every operation named
   `initial` or `tick_complete:<t>`
   (`src/stage7b2_population.py:225-262`), and the population steps emit
   exactly one `tick_complete:<t>` per tick (`t = 0 … W−1`).

Therefore `len(closure_history)` — recorded as `tick_checkpoints` by
`src/run_stage8_alpha.py:226` — is deterministically **`W + 2`**
(two `initial` entries + one entry per completed tick), not `W + 1`.
Empirical probe at plumbing scale (`window_ticks = 5`, seed 20421301, both
arms): length 7 with operation sequence
`['initial', 'initial', 'tick_complete:0', …, 'tick_complete:4']`.

**Why it escaped until now:** the parenthetical "(closure-history length
(`W + 1` including `initial`))" in `docs/stage8-alpha-output-schema.md` §1.1
was derived from module docstrings ("only tick-complete checkpoints are
appended") without accounting for the parent-class constructor's own
`initial` append, and was never validated against a real execution: the
committed tests assert this field only via synthetic fixtures
(`test_stage8_gate.py` constructs passing records with 2401), and the
plumbing-scale smoke tests do not assert it. Today's shakedown was the first
execution that could expose the mismatch, which is precisely what the gate
exists for.

## Dispositions executed

1. **No freeze.** The confirmatory table `20310529 + i` remains untouched and
   unexecuted (zero runs consumed, verified by the absence of any retained
   artifact).
2. This archive (never to be deleted).
3. A superseding registration
   (`docs/stage-8-alpha-evolution-gate-repair-preregistration.md`) carrying
   the paired design verbatim — arms, kernel, founders, ecology, window,
   floor 4/255, thresholds 16/18/24, both seed tables — and changing ONLY:
   (i) G2's checkpoint operationalization, pinned to the frozen stack's exact
   deterministic semantics (`tick_checkpoints == window_ticks + 2`, head
   labels `['initial', 'initial', 'tick_complete:0']`, tail label
   `tick_complete:<W−1>`, with the two small descriptive record fields needed
   to check the labels); (ii) explicit correction of the base schema doc's
   §1.1 `tick_checkpoints` parenthetical BY SUPERSESSION (the base document
   itself is not edited); (iii) explicit re-authorisation of one corrected
   gate execution on the same shakedown table `20421301 + j`, disclosing that
   the table was executed once under the superseded registration with only
   condition pass/fail facts emitted (no endpoint values, no direction
   information, nothing that could tune any frozen quantity).
4. Gate-tooling amendment committed under the new registration's
   implementation window, including the threshold-free factual-context block
   (`factual_shakedown_context`) that §7's disclosure bullet always required.

## Non-runs and non-edits

No retained execution occurred; no frozen module was edited; no registration
document was edited; no threshold, floor, kernel, window, or seed table was
changed; the failed gate left no artifact under `results/`.
