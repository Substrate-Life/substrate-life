# Independent verification audit of the follow-on power memo

*Date: 2026-08-23 (session 9). Auditor: `src/audit_followon_power_memo.py`
(standalone, read-only over `results/` and `docs/`, imported by no
mechanic, outside every frozen execution path — house precedent
`audit_stage8_post_retention.py`). Subject:
`docs/stage-8-followon-power-memo.md`, the computed-closure document
whose §9 reopening conditions R1–R3 bind all future sessions (review
Part V item 2). Every memo constant was re-derived from the retained
artifacts and source documents alone, never from the memo's own tables
except as the comparison target: exact Fraction arithmetic for all data
quantities, integer binomial tails via `math.comb`,
`statistics.NormalDist` only where the memo itself labels an
approximation. This unit registers no execution and runs none; the Part
V item 3 hold remains in force throughout.*

## Result

**21/21 checks clean: 19 PASS + 2 labelled-approximation FINDINGS +
zero exact-claim failures** (exit 0). Every quantity the memo states as
exact reproduces bit-exactly from the retained raw/reduced artifacts;
the two findings concern display precision inside passages the memo
itself marks "approximation", plus one final-digit estimate-cell note.
No registered constant, threshold, reopening condition, or conclusion
changes. Disposition per debate Round 6
(`docs/stage-8-debate-log.md`): ADVOCATE SURVIVES narrowly — a dated,
visible corrigendum is appended to the memo in a separate commit after
this document.

## Check table

| # | check | class | verdict |
|---|-------|-------|---------|
| A1 | all five §10 provenance digests match the working tree | EXACT | PASS |
| A2 | memo §10 and post-retention audit agree on retained raw+reduced SHA-256 | EXACT | PASS |
| B1 | 24-value D-table transcription exact (sorted lattice units, min −215/16, max 167/16) | EXACT | PASS |
| B2 | mean −47/73440; pop sd 0.022377 (= 5.7061 lattice); sample sd 0.022858; median \|D\| = 437/24480; movers 9/6/9; sign 13/11; range [−13.44, +10.44] | EXACT | PASS |
| B3 | null anchor Σ_{k≥18} C(24,k) = 190051 → 0.01133 one-sided / 0.02266 two-sided | EXACT | PASS |
| C1 | all 18 concordance tail cells exact to display precision (⌈3k/4⌉ = 18/36/72; k-cliff at p = 0.70 reproduced) | EXACT | PASS |
| D1 | shift-method crossings 9/10/13/15/18/20 of 24 and powers {0.00021, 0.00097, 0.03041, 0.14533, 0.60741, 0.90883} | EXACT | PASS |
| D2 | internal consistency: μ=8 row ≡ §3 k=24 p=0.75 cell (both tail(Bin(24, 3/4) ≥ 18)) | EXACT | PASS |
| D3 | minimal uniform shift 359/48 ≈ 7.479 = 1.87× floor | EXACT | PASS |
| E1 | normal-map 50%-power point vs printed "p_up ≈ 0.73 ⇔ μ\* ≈ 7.5" | EST | **FINDING F-1** |
| E2 | normal-map 80%-power point: p_up = 0.7969, μ\* = 8.739 vs printed "≈ 0.80 / ≈ 8.74" | EXACT | PASS |
| E3a | printed-pair agreement \|7.5 − 7.4792\| = 0.0208 ≤ 0.03 | EXACT | PASS (of printed values) |
| E3b | consistent-σ map gap 0.0512 > 0.03 | EST | **FINDING F-2** |
| F1 | mean-rule sizing μ\*₈₀ = 3.263; bound-slope power 0.0958; powered slopes ≥ 3.59e−4 = 4.48× bound | EXACT | PASS |
| F2 | window-divergence solution T = 401.8, W ≈ 48,220, est wall 55.5 h (memo ~401 / ~48,000 / ~55 h) | EXACT | PASS |
| G1 | four §6 scaling rows reproduce under the declared linear model | EST | PASS with note (F-3) |
| G2 | observation: true-50% rows sit below the memo's rows (see below) | EXACT | informational |
| H1 | admitted-births identity 23,933 = 23,933 per seed AND in total across all 24 pairs; `arm_contrast_is_exactly_the_kernel = true` | EXACT | PASS |
| I1 | no new artifacts since session 8 → R1–R3 doors unfired | EXACT | PASS |
| I2 | wall basis bound to execution note ("≈ 2 h 46 m"; memo's 9960 s conversion exact) | EXACT | PASS |
| I3 | 14/14 frozen source pins still bind the raw artifact's streams | EXACT | PASS |

## Findings and materiality

**F-1 (memo §4, normal cross-check):** the memo prints "50% power ⇔
p_up ≈ 0.73 ⇔ μ\* ≈ 7.5". Exact search gives p_up = 0.7260 and, at the
population σ = 5.7061 used everywhere else in the memo, μ\* = 7.428.
The printed 7.5 corresponds instead to the sample σ (5.8288 lattice
units → 7.51), an undeclared basis switch. *Materiality: none* — the
requirement is ≈ 1.86× the registered floor under either basis and
remains unreachable at bound slope; the headline (whole-floor shift ⇒
3.0% power) is unaffected because it rests on the shift method, which
reproduced exactly.

**F-2 (memo §4, agreement sentence):** "Both maps agree within 0.03
units" is true of the printed rounded pair (0.0208) but not under one
consistent σ (gap 0.051). *Materiality: none for any decision path* —
but as an affirmative verification claim it fails as stated, which is
what triggered the Round-6 corrigendum verdict.

**F-3 (memo §6, ceiling-80% wall cell):** recomputes to 5.849 h vs
printed ≈ 5.9 h — one final-digit rounding-path difference on a labelled
linear extrapolation of a single recorded wall whose own inputs carry
minutes-level uncertainty ("≈ 2 h 46 m"). *Materiality: none.*

**G2 observation (conservative direction of §6 targets):** the "~50%"
target rows correspond to p_up = 0.75, whose exact power at k = 24 is
60.7%; at the true 50% point (μ\* = 7.428) the rows drop slightly
(realistic T = 204.1 turnovers, W = 24,488 ticks, est ≈ 28.2 h;
ceiling T = 35.7, W = 4,284, est ≈ 4.9 h). The closure conclusions are
*a fortiori* strengthened (less wall needed, still far outside any
recorded ecology's regime), and R1's "≈ 5–6 h" band stands unchanged.

## Reopening-door status at audit time

R1–R3 unfired: no measurement artifact newer than session 8 exists
(`results/stage8-alpha-evolution-paired/` holds exactly the three known
files); no owner redirection has been received. The hold (Part V
item 3) remains in force.

## Provenance

Read-only reads performed this session:

- `results/stage8-alpha-evolution-paired/confirmatory-paired-20310529.json`
  SHA-256 `3eb06ecc03cbe044416ac403f59a7f0e2adb6ab2d2d2f4c54cf1f38c6ce660e7`
- `results/stage8-alpha-evolution-paired/confirmatory-paired-20310529-reduced.json`
  SHA-256 `bdb14fbedcfbcc4d3b3194edbfad428ac8869f1f8c75d848a6655147dd284dec`
- `results/stage8-alpha-evolution-paired/pre-execution-manifest.json`
  SHA-256 `c7cec747ab997a0fc9ede498d2e0f050498b24f77db93f6083a46bcb7c9054e7`
- `docs/stage-8-followon-power-memo.md` (audit-time, pre-corrigendum)
  SHA-256 `1e4a65153b75dcce2a878cc6975c0d497dd7a5c72a1b33db64d0af0a7231f347`
- `docs/stage-8-paired-execution-note.md`
  SHA-256 `b3cf080ab9b85443d9d76151bc377457f9c0590df91fd9e78aae818eab0bbb9b`
- `docs/stage-8-alpha-evolution-repair-preregistration.md`
  SHA-256 `669124a2a5db46f09c3757f11932f8d280acdda5824f87f7ea1b2340628d47fa`

Derivation chain: paired differences read from
`outcome_block.descriptive.paired_differences` as exact Fractions
(lattice display ×255); tails via `math.comb` over integers; design
sizing and window scaling recomputed from the declared model constants
(β_bound = 8×10⁻⁵, areas 455 / 2601 A-units²·turnover⁻¹, wall basis
9960 s at W = 2400+2, two workers) — the constants themselves trace to
the cited stage records and were not re-derived here. No file outside
`docs/` and the standalone audit module was touched. Suite state at
HEAD `20765f3`: **419 passed, 4 skipped**, 19 subtests; working tree
clean; origin synced.

Companion records: Round-6 verbatim debate
(`docs/stage-8-debate-log.md`), the audited memo itself, and the
post-retention audit for the underlying run
(`docs/stage8-paired-post-retention-audit.md`).
