# Stage 8 Paired Confirmatory Execution Note

*The ONE authorised retained execution of
`docs/stage-8-alpha-evolution-repair-preregistration.md` §8(4), reduced
exactly once under §5 by the source-frozen reducer, as required by the
freeze `f1e6880` and the pre-execution manifest
`results/stage8-alpha-evolution-paired/pre-execution-manifest.json`.
This note is a registered retained output (schema addendum §3). It
reports; it never re-opens, re-weights, or re-interprets.*

## 1. Provenance and freeze binding

- Freeze commit: `f1e6880` (implementation + tests + schemas + reducers +
  gate tooling pinned by SHA-256 and byte size in the manifest after the
  corrected §7 gate passed on the fixed 12-pair shakedown table
  `20421301+j`; Round-3 debate verdict executed).
- Runner invocation (2026-08-23 14:55:41 UTC):
  `python3 run_stage8_paired.py --table confirmatory --workers 2 --out
  results/stage8-alpha-evolution-paired/confirmatory-paired-20310529.json`
  from `src/`. Per the manifest execution-disclosure, `--workers 2` is
  authorised: pairs are isolated seeded populations and pool.map
  preserves registered index order.
- Completion: runner log tail `wrote …confirmatory-paired-20310529.json`,
  `RUN_EXIT_CODE=0`; artifact mtime 17:41 UTC ⇒ wall ≈ 2 h 46 m.
  Factual disclosure: the preregistration's §8 wall estimate was
  ≈ 85 min at two workers; actual was ≈ 166 min. No consequence — event
  digests and kernel draw chains bind the exact streams, not the clock.

## 2. Pre-reduction integrity verification (performed twice: before
launch and immediately before reduction)

- All 30 manifest-pinned files matched their frozen SHA-256 + byte size
  in the working tree on both checks: zero drift.
- The raw artifact's embedded `source_manifest_sha256` over the 14
  runner-relevant sources matches the manifest entries exactly.

Runner stdout summary: `{"table": "confirmatory", "pairs_run": 24,
"pairs_both_arms_complete": 24, "runs_total": 48, "runs_complete": 48,
"decision": "PENDING_REDUCTION"}`.

## 3. The single reduction

```
python3 src/reduce_stage8_paired.py \
  results/stage8-alpha-evolution-paired/confirmatory-paired-20310529.json \
  --out results/stage8-alpha-evolution-paired/confirmatory-paired-20310529-reduced.json
```

The reducer's pre-rule validation passed silently (no refusal); the
reduced artifact is the one §5 application (`applied_exactly_once:
true`). Raw and reduced artifacts are retained immutable;
`raw sha256/4198845B = 3eb06ecc…`, `reduced sha256/194193B = bdb14fbe…`
(short prefixes for prose; full hashes live with the artifacts).

## 4. Outcome and its registered reading

**`NO_ESTABLISHED_DIRECTION`.**

- Eligible pairs `k_eff = 24/24` (all arms COMPLETE; zero extinctions;
  terminal census `n_live = 48` on every one of the 48 runs).
- Movers up (`D_i ≥ +4/255`): **9**. Movers down (`D_i ≤ −4/255`): **6**.
  Non-movers (strictly inside): **9**. Concordance threshold is 18 of
  k_eff ≥ 16: neither side approaches it. The failure is concordance,
  not magnitude — median |D_i| over all eligible pairs is 437/24480
  (= 4.6/255 lattice units), right at floor scale, but signs split
  13 positive / 11 negative / 0 zero.
- Registered reading (§5 / Part V item 3): direction (c) closes **at
  this ecology, kernel, and window**, with the paired redistribution
  bound below. The licensed statement is exactly the reducer's fixed
  scope sentence, quoted verbatim in §6. Nothing may be added to escape
  a null; no retune, re-run, or supplementary endpoint is authorised on
  this line.

Exact paired-difference table (D_i = ᾱ_end(M) − ᾱ_end(R0), exact
Fractions; also in the reduced artifact):

| seed | D_i | | seed | D_i |
|---|---|---|---|---|
| 20310529 | +13/2448 | | 20310541 | −47/1360 |
| 20310530 | −41/4080 | | 20310542 | −65/2448 |
| 20310531 | −167/12240 | | 20310543 | +79/4080 |
| 20310532 | −47/1360 | | 20310544 | +37/6120 |
| 20310533 | +73/4080 | | 20310545 | +197/12240 |
| 20310534 | +11/612 | | 20310546 | −53/3060 |
| 20310535 | +167/4080 | | 20310547 | −43/816 |
| 20310536 | +23/6120 | | 20310548 | +239/12240 |
| 20310537 | −263/12240 | | 20310549 | +31/1530 |
| 20310538 | +1/80 | | 20310550 | −41/3060 |
| 20310539 | −77/12240 | | 20310551 | −1/170 |
| 20310540 | +17/720 | | 20310552 | +109/6120 |

Paired redistribution bound (descriptive, threshold-free): mean
D = −47/73440 ᾱ-units (= −0.16/255 lattice units); population sd(D) =
0.022377 ᾱ-units (= 5.71/255); max |D_i| = 13/255; best single-side
floor-crossing count 9/24 against a required 18. At this ecology the
kernel moves individual pair endpoints across the ±4/255 floor in both
directions without any consistent redistribution of terminal allocation.

## 5. Obligations discharged (debate Rounds 2–3)

1. **Empirical null spread of D_i, reported descriptively whatever the
   class (A2 obligation).** Given above: mean −47/73440, population sd
   0.022377 (sample sd 0.022858), median |D| = 4.6/255, range
   ±13/255. The observed spread is ≈ 2.9–3.6× the Round-2 fixed-genotype
   composition-noise proxy band (σ ≈ 1.6–2.0/255). Recorded as fact: the
   proxy underestimated pair-endpoint dispersion at W = 2400. The rule
   is count-based with frozen thresholds, so test size is unaffected;
   the ≥ 2σ anchoring argument from Round 2 was a floor-calibration
   consideration only and no quantity derived from it entered the §5
   path.
2. **Leakage monitor read and reported (A3 obligation).**
   `leakage_pairs = 0`: the two arms' terminal founder-ancestry
   pluralities agreed in all 24 pairs. The A3 sensitivity table
   (sign-probability skew ⇒ one-sided leakage 0.096–0.6074 over sign
   probabilities 0.60–0.75) stands recorded in the debate log; with the
   ancestry-plurality monitor clean and the observed sign split 13/11,
   there is no indication of flip-sign leakage in this run.
3. **Residual-risk pointer (freeze-commit obligation, f1e6880).** The
   disclosed nonzero residual risk for W-derived counts stands: such
   counts are read by no mechanic and sit outside the §5 decision path.

## 6. Scope sentence (verbatim from the reduced artifact)

> Level-2 statement space only, relative to the mutation-off reference
> at the same seeds: 'the restricted architecture does / does not
> redistribute allocation through the channel, in the registered
> direction(s), beyond Δ_pair_floor = 4/255, at this ecology, kernel,
> and window'. A null licenses exactly that bounded-negative statement;
> no external validation, optimum, ESS, causal-gradient, open-genome,
> or other-ecology claim is licensed.

Applied here: **the restricted architecture does not redistribute
terminal allocation through the dedicated-locus channel beyond
±4/255 per pair, in either registered direction, at this ecology,
kernel p_μ = 1/2 δ ∈ {±1..±4} clamped, T = 128/D = 255, W = 2400.**

## 7. Factual context (threshold-free, non-binding)

- Arm M kernel telemetry totals: mutation decision records 23,933;
  kernel draws 35,981; problems 0; memory-unavailable failures 0.
- Admitted births: Arm M 23,933; Arm R0 23,933 (identical — the shared,
  phenotype-blind demographic skeleton at equal seeds).
- Arm R0 integrity: 0 decisions, 0 draws, empty draw chain,
  telemetry `passes = true` on every run (kernel absence pinned).
- Terminal distinct-A: Arm M 9..17 of 48 live; Arm R0 1..2 (the
  mutation-off reference collapses toward founder genotypes, consistent
  with the carried drift-to-boundary behaviour of the byte-frozen stack).
- Closure-history pins verified on export: head
  `['initial','initial','tick_complete:0']`, tail `tick_complete:2399`.

## 8. What this closes and what it feeds

Stage 8 rung 2 closes as a **registered null** alongside rung 1's null:
two endpoint families, no established channel effect at this ecology.
Per Part V item 3 this feeds review directions (a) (ecology/power
reframing, now with a measured paired-dispersion prior:
sd(D) ≈ 5.7/255) and (d) (programme close-out essay, which gains its
second honest registered null). Direction (c)'s bounded-negative result
does not license claims about frequency-trajectory instruments,
other ecologies, or open populations — those would be new registrations,
decided by the next registration cycle, not additions to this one.
