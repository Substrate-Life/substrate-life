# Stage 8 Gate-Repair Preregistration: checkpoint-bookkeeping correction to the §7 feasibility gate (paired design otherwise carried verbatim)

*Superseding registration #3 of the Stage 8 alpha-evolution line. Date:
2026-08-23. Authorised by: the owner's standing autonomous-advance order;
the binding failure clause of
`docs/stage-8-alpha-evolution-repair-preregistration.md` §7 ("If any
condition fails: no freeze; a further superseding preregistration with
diagnosis, archived under `failed-designs/`, never deleted"); the archived
diagnosis `failed-designs/stage8-paired-gate-g2-checkpoint-bookkeeping/`.
This document registers no execution by itself beyond the exploratory,
unretained, stdout-only gate re-execution it authorises on the fixed
shakedown table; no retained execution occurs before its §6 gate passes
and its §7 freeze is committed.*

## 1. Registered reading of what precedes this registration

The §7 feasibility gate of the repair registration was executed once
(2026-08-23, ≈ 118 min, 12-pair shakedown table `20421301 + j`, both arms,
`W = 2400`). Outcome: 12/12 pairs both-arms COMPLETE; **G1 PASS** (12/12
pairs ≥ 1 mutation event, ≥ 2 distinct terminal `A` values, zero
genome-freeze violations); **G2 FAIL** with 24 checkpoint-bookkeeping
failures and zero buffer overflows / invalid runs; **G3 PASS** (zero kernel
audit failures; full re-execution replay bit-exact); **G4 PASS** (zero
R0 kernel-absence failures, zero seed mismatches).

The archived diagnosis establishes, with source-line references and a
direct plumbing-scale probe, that:

1. **The registered substance of G2 holds.** Live ledgers are verified
   after every operation and the full immutable history is rescanned at
   every tick-complete checkpoint by byte-frozen machinery; any failure
   would have classified the run `INVALID_IMPLEMENTATION`. Zero occurred.
2. **The tooling's derived expectation is wrong.**
   `len(closure_history)` — recorded as `tick_checkpoints` — is
   deterministically `W + 2`, because `Stage7B1Population.__init__`
   (`stage7_slice2.py:91`) appends an `initial` closure entry and
   `Stage7B2Population.__init__` (`stage7b2_population.py:164`) appends a
   second one, followed by exactly one `tick_complete:<t>` entry per tick
   (`t = 0 … W−1`). The gate required `W + 1`. The wrong expectation
   entered the record through the parenthetical "(closure-history length
   (`W + 1` including `initial`))" in
   `docs/stage8-alpha-output-schema.md` §1.1, which was written from
   docstrings and never validated against a full-window execution until
   this shakedown — the first ever at `W = 2400`.

This registration ACCEPTS that diagnosis as the operative record.

## 2. What is carried verbatim (unchanged by this document)

Every substantive element of the repair registration is carried verbatim
by reference and is reaffirmed as frozen: Arm M (dedicated-locus kernel
`p_μ = 1/2`, steps `±1..±4` clamped, `T = 128` / `D = 255` never drawn);
Arm R0 (byte-frozen stack, kernel absent); pairing at identical
`hazard_seed`; founders, ecology, `W = 2400`; endpoint
`D_i = ᾱ_end(M, s_i) − ᾱ_end(R0, s_i)` in exact Fractions;
`Δ_pair_floor = 4/255`; eligibility pairwise; thresholds 16/18/24; the
§5 decision rule and its floor-free null-tail bound
(`190051/2²⁴ ≈ 0.01133` one-sided); the §6 H1 power derivation and its
registered expected-null consequence; the confirmatory pair table
`20310529 + i` (`k = 24` pairs = 48 runs) — **untouched and unexecuted**,
zero runs consumed through the failed gate; the freeze-before-execution
policy and manifest path; and the standing-rules compliance mapping. No
floor, threshold, kernel, window, arm, endpoint, or confirmatory seed is
changed by this document, and none may be after execution (§8).

## 3. Registered corrections (the only changes)

| Item | Superseded value | Registered value | Rationale |
|---|---|---|---|
| G2 checkpoint check | `tick_checkpoints == window_ticks + 1` | For every COMPLETE arm: `tick_checkpoints == window_ticks + 2` AND closure-history head labels `['initial', 'initial', 'tick_complete:0']` AND tail label `'tick_complete:<W−1>'` | Pins the byte-frozen stack's exact deterministic append semantics (two constructor-layer `initial` entries, one tick-complete entry per tick). Strictly stronger than the superseded count-only check: a scheduling regression that skipped or duplicated a tick-complete assertion now fails on labels as well as count. |
| Measurement record | no closure-label fields | Two descriptive fields on every COMPLETE arm record: `closure_history_head` (first three operation labels) and `closure_history_tail` (last operation label) | Substrate for the corrected G2 check. Descriptive evidence only; read by no mechanic; ignored by the reducer's decision path. |
| Base schema §1.1 `tick_checkpoints` parenthetical | "(closure-history length (`W + 1` including `initial`))" | Superseded BY THIS DOCUMENT to "(closure-history length (`W + 2`: two `initial` entries appended by the two constructor layers, plus one `tick_complete:<t>` entry per completed tick))" | Correction by supersession per house discipline; the base document itself is not edited. |
| Gate stdout | condition counts only | Adds a threshold-free `factual_shakedown_context` block (aggregate mutation-event totals, terminal live-census min/max, Arm-M terminal distinct-`A` min/max, extinct-arm count) satisfying the repair registration §7 disclosure bullet | Factual context only; may not resize anything; contains no endpoint values. |

## 4. Shakedown-table re-authorisation

The corrected gate is authorised to execute **once more**, exploratory and
unretained (stdout only), on the SAME fixed shakedown table
`20421301 + j` (`k = 12` pairs). Disclosure, committed before the rerun:
the table was executed once under the superseded registration; that
execution emitted only condition pass/fail facts, complete-pair counts,
threshold arithmetic, and replay evidence (seed identity, digest equality)
— **no endpoint values, no direction information, and nothing readable as
an outcome of any registered statistic** — so no frozen quantity can have
been tuned against data. One-use discipline binds confirmatory tables;
this exploratory table's reuse is explicit here so the gate PASS on record
comes from the corrected tooling end-to-end.

## 5. Gate conditions (all mandatory, binding)

Identical to repair registration §7 except G2 as corrected in §3 above:

- **G1 (evolution operates, Arm M):** unchanged — ≥ 2/3 of pairs COMPLETE
  with ≥ 1 recorded mutation event, ≥ 2 distinct `A` values among live
  members at tick W in Arm M, zero non-frozen `T/D` anywhere in either
  arm's event stream.
- **G2 (implementation integrity, corrected):** zero `BUFFER_OVERFLOW` /
  `INVALID_IMPLEMENTATION`; every ledger closes at every checkpoint in
  every arm; and for every COMPLETE arm the closure-history semantics of
  §3 hold (`tick_checkpoints == W + 2`, head/tail labels as pinned).
- **G3 (kernel audit, Arm M):** unchanged — per-birth Stage-M record
  reconciliation, bounds, bit-exact stream replay with one full replicate
  re-executed by the gate tooling.
- **G4 (reference-arm integrity):** unchanged — zero R0 mutation events /
  kernel draws, identical within-pair seeds, complete pair table.

If any condition fails: no freeze; further superseding registration with
diagnosis archived under `failed-designs/`, never deleted.

## 6. Freeze-before-execution and authorised execution class

Unchanged from repair registration §8, re-affirmed: implementation window
opens on this commit (gate-tooling amendment, measurement-record fields,
schema-addendum update, tests); then the §5 gate must pass on the
shakedown table as executed by the amended tooling; then a single freeze
commit pins implementation, runner, reducers, tests, schema documents by
SHA-256 + byte size at
`results/stage8-alpha-evolution-paired/pre-execution-manifest.json`;
then ONE retained confirmatory suite (`20310529 + i`, both arms per pair,
48 runs, `W = 2400`) executed once, raw outputs retained under
`results/stage8-alpha-evolution-paired/`, reduced exactly once under the
§5 rule by the source-frozen reducer, whatever class results.

## 7. Standing-rules compliance

Exact Fraction arithmetic everywhere; kernel draws integer-only outside
ledgers; telemetry labels never read by mechanics; trait-isolation,
trait-resolution, endpoint, mediator-currency, ecology, plasticity-scope,
and no-historical-carry-over gates as mapped in repair registration §9;
failed designs archived; retained artifacts immutable; push after every
commit; suite kept green.

## 8. Not authorised by this document

Any retained execution before the §5 gate passes and the §6 freeze is
committed; running either arm at any seed outside the registered tables
(except the single authorised corrected-gate shakedown re-execution of
§4); reusing retired tables; editing any registration document or
retained artifact; changing arms, kernel, floors, thresholds, windows,
endpoints, or the confirmatory table — now or after execution; promoting
co-reports or the factual-context block to endpoints; interpreting a
registered null beyond its scope; external-validation, optimum, ESS,
causal-gradient, or open-population claims; history rewrites.
