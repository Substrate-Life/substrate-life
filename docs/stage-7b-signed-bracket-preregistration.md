# Stage 7B Signed-Bracket Preregistration: Full-Line Euler–Lotka Roots (closing the complete-pair availability defect)

**Protocol status:** SUPERSEDING preregistration. It supersedes exactly
the **solver-domain restriction** registered at
`stage-7b2-preregistration.md` §4 steps 1–2 as carried through
`stage-7b2-repair-preregistration.md` §3 and
`stage-7b-denominator-repair-preregistration.md` §3 — the rule that a
genotype-replicate with `L(0) ≤ 1` is classified `SUBCRITICAL` and emits
**no numeric** `r_g`, together with the consequent definition of
"complete pairs" (both genotypes simultaneously supercritical) and the
consequent feasibility-gate condition derivation. It carries forward,
verbatim and unchanged, every other registered decision of the carried
set: the two-factor endpoint coefficients `c_x = l^A_x · m^E_x`
(`stage-7b-denominator-repair-preregistration.md` §3, including its five
binding identities); the raw-fecundity numerator `n_x`; the establishment
mediator; the reported descriptive `l_x`; censoring and exposure
conventions; the carried §5 decision-rule classes, thresholds
(`Δr_min = 1/100`, minimum 16 complete pairs of 32, applied exactly once
by a source-frozen reducer) and solver resolution `ρ_r = 1/256`; the
repaired ecology (`N=48`, `E=900`, `W=1200`, seed base `20261822`,
genotypes `(102,128,255)`/`(204,128,255)`, 3 founders/genotype, founder
`S=100`/`R=0`, hazard arm `h=1/120`, corpse TTL 2, buffer depth 64,
shared memory pool 65,536 B, mutation disabled); the Stage 7B1
transaction/retirement/death/shadow mechanics; and the vacancy-capture
estimand decision. Corrections require a further superseding
preregistration, never edits here or in any superseded document.

**Evidence-era disclosure:** observed before this freeze: the unretained,
non-artifact-producing §5 feasibility-gate execution of the denominator-
repair preregistration over its fixed 24-seed table (`20270000 + j`),
archived at `failed-designs/2026-08-23-stage7b-denominator-feasibility-gate-no-go/`
(results registered in §1 below; a single-seed plumbing check preceded it
and reproduced seed 20270000's record bit-exactly); and the entire prior
failure lineage it supersedes part of (7B2-R 0/24; endpoint-repair 0/24),
both archived. Additionally observed before this commit, from the same
gate records: the perfect exclusion anti-correlation and balanced-cohort
structure diagnosed in §2, and the fact that every arm-replicate carries
births ≥ 10 and person-ticks ≥ 1,505 (measurability). **Never observed
anywhere in project history:** any numeric negative `r_g` bracket; any
signed contrast pair; any CRITICAL classification; any execution at the
ecology of this document on the confirmatory table `{20261822,…,20261853}`
under any endpoint generation. No fitness, selection, optimum, or ESS
claim exists in any Stage 7 artifact, including this one.

**Authorisation:** this document registers decisions only. It authorises
no retained execution. A new, additively-defined solver module implementing
the full-line contract (§3 below) may be written after this commit,
reusing byte-identically: the frozen estimator (`stage7b_exposure_measure.py`),
the frozen configuration layer (`stage7b_exposure_config.py`), the event-
ledger extraction (`stage7b2_measure.py`), the population mechanics
(`stage7b2_population.py`), and the unchanged positive-half-line bisection
machinery where applicable. The existing frozen modules —
`stage7b1_mechanics.py`, `stage7b2_measure.py`, `stage7b2_population.py`,
`stage7b2_solver.py`, `stage7b2r_population.py`, `stage7b_endpoint_measure.py`,
`stage7b_endpoint_config.py`, `stage7b_endpoint_gate.py`,
`run_stage7b_endpoint.py`, `reduce_stage7b_endpoint.py`,
`stage7b_exposure_measure.py`, `stage7b_exposure_config.py`,
`stage7b_exposure_gate.py` — are never edited in place and remain exactly
as committed evidence. Implementation, runner, reducer, tests, output
schema, and analysis tooling for the confirmatory execution must be frozen
**together** with a pre-execution manifest (SHA-256 + byte size per file,
frozen-module pins), committed before any retained run, and only after the
§5 feasibility gate passes. Mutation remains unauthorised in every form.

## 1. Registered reading of the third gate outcome

The `stage-7b-denominator-repair-preregistration.md` §5 gate was executed
this session as an unretained shakedown on its fixed 24-seed table, with
the following outcome (full evidence archived;
`failed-designs/2026-08-23-stage7b-denominator-feasibility-gate-no-go/gate-summary.json`):

- **G1 FAILED for arm A=204**: 7/24 replicates supercritical (required
  ≥ 16); arm A=102 PASSED at 20/24 — the first time any arm has passed
  a supercritical reachability condition in Stage 7B history.
- **G2 FAILED**: 3/24 joint-supercritical replicates (seeds 20270007,
  20270008, 20270011; required ≥ 16).
- **G3/G4 PASSED**: 24/24 replicates COMPLETE; zero `BUFFER_OVERFLOW`;
  zero `INVALID_IMPLEMENTATION`; every checkpoint closed; all five §3
  binding identities held inside the estimator in every reduction.

This classification stands exactly as archived; it is not reopened or
retried here. What it establishes: the two-factor repair succeeded in
its registered purpose — supercriticality is reachable and the ceiling
defect is gone — and the remaining failure is located one layer further
out, in the statistical design inherited from the original solver
contract, not in the endpoint algebra.

## 2. Binding diagnosis (from the archived per-replicate records)

Recorded as design input, derived exclusively from the archived gate
records and the carried definitions:

- **D-A. The repaired endpoint behaves as designed.** Per-arm
  supercriticality 20/24 and 7/24, certified `L(0)` values up to
  ≈ 1.455, perfect execution integrity, all binding identities exact.
  No structural bound suppresses growth measurement under the two-factor
  coefficients.
- **D-B. The ecology produces winner-take-most exclusion dynamics.**
  Aggregate exposure per replicate ≈ 58k person-ticks over `W = 1200`
  (≈ 48.3 member-present ticks/tick against capacity `N = 48`): the
  population is saturated throughout, so reproduction is vacancy-limited
  end-to-end. Exactly one arm is supercritical in 21 of 24 replicates
  (exclusive-102: 17; exclusive-204: 4); P(204 super | 102 sub) = 4/4
  and P(102 sup | 204 sub) = 17/17 — a perfect anti-correlation. The
  three joint-supercritical replicates are exactly those whose cohorts
  stay balanced (loser cohort ≥ 199). Exclusive winners certify
  `L(0)` = 1.19–1.46 (A=102) and 1.32–1.54 (A=204); losers certify
  0.948–0.970 (A=102, n=4) and 0.769–0.986 (A=204, n=17). Which lineage
  wins is replicate-stochastic (priority effect). These are dynamical
  facts of the registered ecology under binding vacancy admission —
  reported descriptively; they are not allocation-effect, fitness, or
  selection findings and must never be cited as such.
- **D-C. The failure point is the complete-pair precondition, not
  measurement.** The carried §5 rule computes paired differences only
  over replicates where **both** genotypes are supercritical, because
  the superseded solver contract emits no numeric `r_g` when
  `L(0) ≤ 1`. At this ecology, simultaneous growth is rare (~12.5% on
  the shakedown table) for the D-B reasons — while **every** arm is
  measurable (minimum cohort 13, minimum births credited 10, minimum
  person-ticks 1,505; coefficient support always exists beyond age 0).
  The gate conditions G1/G2 were derived from precisely this
  precondition (per repair principle D6 of
  `stage-7b2-repair-preregistration.md` §2), so their failure is the
  precondition failing, faithfully detected before any freeze.
- **D-D. Registering another infeasible confirmatory suite is
  prohibited** (`stage-7b2-repair-preregistration.md` §6.3). Projected
  complete-pair availability ≈ 12.5% against the required ≥ 50% would
  make `DEGENERATE_REPLICATION` near-certain. The minimal repair
  consistent with the evidence targets pair availability itself: Lotka's
  equation with non-zero support at some age `x ≥ 1` has a unique
  **real** root whether positive, zero, or negative (`L` is continuous
  and strictly decreasing, with `lim_{r→−∞} L(r) = +∞` and
  `lim_{r→+∞} L(r) = c_0`), so every measurable arm can emit a
  certified signed bracket. The sign of the bracket then carries the
  sub/supercritical classification instead of bracket absence, complete
  pairs become available wherever both arms are measurable, and the
  registered question — a two-sided contrast — becomes evaluable in
  every replicate without touching any threshold, seed, ecology,
  estimator, or mechanic.

## 3. Registered repair decisions

| Item | Superseded definition | Registered replacement | Rationale |
|---|---|---|---|
| Solver domain (`stage-7b2-preregistration.md` §4 step 2, as carried) | `L(0) ≤ 1` ⇒ status `SUBCRITICAL`, **no numeric `r_g` emitted** | Full-line certification. With `S₊ := Σ_{x≥1} c_x` and `c_0 := c[0]`: (i) `L(0) > 1` ⇒ `SUPERCRITICAL` with certified bracket ⊂ `[0, ∞)`, exactly as before; (ii) `L(0) = 1` (exact `Fraction` equality) ⇒ `CRITICAL`, bracket exactly `[0, 0]`; (iii) `L(0) < 1` and `S₊ > 0` ⇒ `SUBCRITICAL` **with certified negative bracket**: expand a candidate `r_lo` downward from `−ρ_r` by doubling until `L(r_lo) ≥ 1` is certified, then bisect monotonically to width ≤ `ρ_r`; the certificate proves containment of the unique real root; (iv) `S₊ = 0` with `c_0 ≠ 1`, or `c_0 ≥ 1` with `S₊ > 0` (rootless cases, impossible while `c_0 = 0` holds mechanically) ⇒ loud `NO_FINITE_ROOT` classification, excluded from pairing and counted against §5 G1. | Completes rather than substitutes the estimand: the registered quantity remains the certified bracket of Lotka's root; only its domain stops being truncated at 0. |
| Exponential enclosures | Directed alternating-series enclosure of `e^{−t}`, `t ≥ 0` | Carried unchanged for `r ≥ 0`; added rigorous enclosure of `e^{+t}` for `t > 0` (positive-term Taylor partial sums are exact-rational lower bounds; geometric remainder bound `≤ term_K · t/(K+1−t)` once `K+1 > t`) raised to integer powers by the unchanged interval-squaring. All arithmetic analysis-side; approximations never enter any ledger. | Negative-root evaluation requires `e^{|r|x}` with certified containment; magnitudes are large (age support up to `W`) but exact rationals make width control routine. |
| Bracket records | `{r_lo, r_hi, width, iterations, L0_exact}` for supercritical arms only | Same fields for every certified arm, plus `status ∈ {SUPERCRITICAL, CRITICAL, SUBCRITICAL, NO_FINITE_ROOT}`; subcritical midpoints are legitimate signed values | Pairing needs both arms' midpoints; classification needs the sign. |
| Complete pairs (`stage-7b2-preregistration.md` §4 step 5, as carried) | Replicates where both genotypes are `SUPERCRITICAL` | Replicates where **both genotypes emit certified finite-root brackets** (any of `SUPERCRITICAL`/`CRITICAL`/`SUBCRITICAL`). `Δ_i = mid₂₀₄,i − mid₁₀₂,i` (order convention carried). | The contrast requires two signed numbers, not two positive signs; D-C/D-D. |
| Decision rule (`stage-7b2-preregistration.md` §5, as carried) | Classes keyed to joint supercriticality | Class names, thresholds, and application-exactly-once unchanged: `DEGENERATE_REPLICATION` (< 16 complete pairs), `ESTABLISHED_CONTRAST` (≥ 16 ∧ `|median_i Δ_i| ≥ Δr_min`), `NO_ESTABLISHED_CONTRAST` (≥ 16 ∧ below). Co-reported classes re-based on bracket sign: a genotype is "subcritical at this ecology" iff its bracket lies entirely below 0 in ≥ 16 of its 32 replicates (must agree exactly with `L(0) < 1`, both computed); `ONE_ARM_SUBCRITICAL` / `BOTH_SUBCRITICAL` co-reported alongside as before. Sign split of `{Δ_i > 0, Δ_i < 0}` over complete pairs reported descriptively. | Preserves every evidential floor; removes only the coexistence assumption embedded in pair availability. |
| Feasibility-gate conditions (denominator-repair prereg §5.3) | G1 per-arm supercriticality ≥ 2/3; G2 joint ≥ 2/3; G3/G4 integrity | Re-derived from the repaired rule's own precondition (D6): **G1** ≥ 2/3 of shakedown replicates yield complete certified bracket pairs (any `NO_FINITE_ROOT` fails G1 and demands diagnosis); **G2** zero `BUFFER_OVERFLOW`/`INVALID_IMPLEMENTATION`; **G3** every checkpoint closes and all five binding identities hold. Per-arm positive-bracket counts, sign splits, and cohort-balance statistics are reported alongside **without thresholds**. | Gate conditions must derive from the decision rule they guard (registered repair principle D6); growth-direction requirements were proxies for measurability under the truncated domain and are retired as conditions, retained as reports. |
| Confirmatory output path | `results/stage7b-exposure-endpoint/` (registered by the denominator-repair prereg; never used — its retained run was not authorised) | `results/stage7b-signed-bracket/` (fresh path; no collision with, or implication about, any earlier retained path) | One retained path per registration, named for the registration. |

Carried verbatim, restated as binding: every decision of
`stage-7b-denominator-repair-preregistration.md` §§1–8 except its §5 gate
outcome (archived, §1 above) and its §6.3 output path (table above);
and through it every decision of `stage-7b-endpoint-repair-preregistration.md`
§§4–8, `stage-7b2-preregistration.md` §§1, 3, 6, 7,
`stage-7b2-repair-preregistration.md` §§1–8, and
`stage-7b1-preregistration.md` §§1–5, 6.2–9, except as already superseded
downstream.

## 4. Registered question (form unchanged; estimand completed)

Under the carried ecology (`N=48`, `E=900`, `W=1200`, exogenous
phenotype-blind hazard `h = 1/120`) with binding vacancy admission, do
the two carried allocation strategies differ in per-genotype invasion
growth `r_g` — the signed real solution of Lotka's equation under the
two-factor coefficients `c_x = l^A_x m^E_x` — by at least
`Δr_min = 1/100` across `k = 32` seeded replicates, with the repaired
rule applied exactly once? The estimand is the per-genotype replicate
distribution of certified rational brackets `[r_lo, r_hi] ⊂ ℝ` (signed;
brackets may lie entirely below zero, and the sign is outcome, not
missingness). No optimum, ESS, background-invariant causal effect of α,
or external-validation claim is registered, tested, or permitted. The
establishment signal continues to be reported as a mediator, never as
the endpoint. Exclusion/priority-effect observations (D-B) are
descriptive context about the ecology, never registered conclusions of
the confirmatory suite.

## 5. Pre-freeze feasibility gate (binding, re-derived from the repaired rule)

Per the registered repair principle (D6):

1. Implement the full-line solver as new, additively-defined code reusing
   the frozen modules byte-identically (Authorisation list; the
   positive-half-line machinery of `stage7b2_solver.py` is reused by
   import or by verbatim-additive copy into the new module — the frozen
   file itself is never edited).
2. Run unretained exploratory shakedowns at the exact carried ecology on
   the **same fixed 24-seed table** (`20270000 + j`, `j ∈ {0,…,23}`) —
   a fourth reuse. Justification: population runs are deterministic in
   the hazard seed, so the underlying ledgers, coefficient vectors, and
   `L(0)` values are bit-identical across all four generations; reuse
   isolates the solver-domain layer exactly, as the third reuse isolated
   the endpoint layer. The gate summary must therefore additionally
   verify the **estimator-layer regression identity**: every
   genotype-replicate's `L0_exact` equals the archived generation-3
   value bit-exactly; any mismatch fails G3 and demands diagnosis.
3. Gate conditions, all mandatory: **G1** ≥ 2/3 of replicates yield
   complete certified bracket pairs (both arms finite-root; any
   `NO_FINITE_ROOT` fails); **G2** zero `BUFFER_OVERFLOW` /
   `INVALID_IMPLEMENTATION`; **G3** every checkpoint closes, all five
   binding identities hold, and the regression identity holds.
4. If any condition fails, no freeze may be committed: the correct
   action is a further superseding preregistration with a diagnosis
   supported by new evidence, archived, never deleted.
5. Shakedown executions produce no retained artifact (stdout only). If
   the gate passes, a factual summary (seed list, per-condition pass
   counts, regression-identity confirmation) must be recorded in the
   freeze commit's manifest directory notes.

## 6. Freeze-before-execution and authorised execution class

1. Implementation window opens on commit of this document; no retained
   execution occurs during it.
2. After §5 passes: freeze the new solver, configuration label layer,
   gate tooling, runner, reducer, tests, and output schema **together**
   with the reused modules pinned by hash, as a pre-execution manifest
   with SHA-256 + byte size per file at
   `results/stage7b-signed-bracket/pre-execution-manifest.json`,
   committed before any retained run.
3. The authorised execution class is then one seeded, mutation-disabled
   confirmatory suite: `k = 32` replicate populations under the carried
   ecology on the untouched confirmatory table
   (`hazard_seed = 20261822 + i`, `i ∈ {0,…,31}`), reduced exactly once
   under the repaired rule using the two-factor coefficients and
   full-line solver, raw output retained at
   `results/stage7b-signed-bracket/`.
4. PASS criterion: every ledger closes at every registered checkpoint in
   every replicate; every solver certification is valid; every §3
   binding identity holds in every reduction; the repaired rule is
   applied exactly once and its outcome recorded — whatever class it
   produces, including `NO_ESTABLISHED_CONTRAST` or
   `DEGENERATE_REPLICATION`, is a legitimate registered result. Any
   failure retains the run, classifies it, and triggers repair —
   archiving, never deletion.

## 7. Standing-rules compliance and falsification-gate mapping

Exact `Fraction` arithmetic in every ledger; `E_x`/`d_x` recovery,
coefficient assembly, and full-line bracket certification in exact
integer/Fraction arithmetic; solver enclosure arithmetic analysis-side
only. Telemetry labels never read by mechanics. Gates engaged:
conservation, packet-sink, vacancy, endpoint (the full-line signed
bracket is the primary fix registered here; mediators stay mediators),
trait-isolation, trait-resolution, ecology (single hazard level ⇒
combined mortality–turnover labelling), storage, plasticity-scope,
age-state/somatic-state reporting — all carried unchanged. The
sign-split report is descriptive; no directional prediction is
registered, and no exclusion observation may be promoted to an
allocation, fitness, or selection claim.

## 8. Not authorised by this document

Any retained execution before the §5 gate passes and the §6 freeze is
committed; mutation at any locus; open genomes; in-place edits to any
frozen module listed in the Authorisation section or to any committed
prior-generation file; re-litigating any archived gate failure under
superseded endpoints or domains; additional hazard levels; factorial
separation studies; retuning `Δr_min`, `ρ_r`, the 16-pair floor, the
two-thirds gate fraction, either seed table, or the ecology — now or
after the confirmatory suite runs; endpoint substitution beyond the
single solver-domain extension registered in §3; directional claims
from the sign split; optimum, ESS, background-invariant causal, or
external-validation claims; interior-lattice or extrapolated landscape
claims; plasticity interpretations; citing exclusion/priority dynamics
as fitness or selection evidence; reuse of pre-Stage-7 quantities;
modification of retained artifacts or superseded documents; history
rewrites.
