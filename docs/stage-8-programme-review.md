# Stage 8 Programme Review: what Stage 7B established, and where the programme goes next

*Date: 2026-08-23. Status: synthesis and decision memo for the owner. This
document registers no execution and authorises none; every candidate
direction below requires its own superseding preregistration committed
before any implementation freeze or retained run, per the standing
discipline. It is intended to be iterated across sessions as facts change.*

## Part I — What Stage 7B established, generation by generation

Stage 7B asked one question through six registered generations: **does the
acquisition-allocation channel — splitting positive extraction income
between somatic reserve `S` and reproductive reserve `R` by the
lifetime-fixed fraction `α = A/D` — express itself at population level as
an invasion-growth difference between the two carried allocation
strategies `A=102` (α=2/5) and `A=204` (α=4/5)?** The generations:

| Generation | Registered purpose | Outcome |
|---|---|---|
| **7B0** (`stage-7b-fixed-allocation-channel-preregistration.md`) | Scripted state-machine verification that intervening on `A` splits identical income exactly, isolates direct debits, produces the registered reproductive-funding/endowment differences, recovers from an `R`-insufficient attempt, and preserves all closures | **PASS**, all ten gates, Blocks A–E, independently audited |
| **7B1** (`stage-7b1-preregistration.md`) | Transaction-safe child publication (fault-injection matrix), packet retirement equations, proven no-eviction configuration, hazard-death cleanup, endpoint definitions (§6.1) and the vacancy-capture estimand decision (§6.2) | **PASS**, deterministic, mutation-disabled; shadow `would_admit` counters proven side-effect-free |
| **7B2** (`stage-7b2-preregistration.md`) | First confirmatory stochastic contrast at ecology `N=12, W=600, h=1/120` under Euler–Lotka roots with truncated domain (`L(0) ≤ 1` ⇒ subcritical, no numeric root) | Retained run 32/32 COMPLETE → **`DEGENERATE_REPLICATION`** (0 complete pairs of 32) + `BOTH_SUBCRITICAL`; repair-policy review mandated |
| **7B2-R** (`stage-7b2-repair-preregistration.md`) | Repair attempt 1: raw-fecundity numerator `n_x`, repaired ecology `N=48, E=900, W=1200` | Pre-freeze feasibility gate **FAILED** (0/24 G1, G2); archived `failed-designs/2026-08-22-stage7b2r-feasibility-gate-no-go/` |
| **endpoint repair** (`stage-7b-endpoint-repair-preregistration.md`) | Repair attempt 2: two-factor coefficients `c_x = l^A_x · m^E_x` (actuarial survivorship × person-tick fecundity) | Feasibility gate **FAILED** (0/24 both arms; ceiling confirmed); archived `failed-designs/2026-08-23-stage7b-endpoint-feasibility-gate-no-go/` |
| **denominator repair** (`stage-7b-denominator-repair-preregistration.md`) | Repair attempt 3: five binding identities on the two-factor estimator | Gate **FAILED one layer out**: A=102 supercritical 20/24 (first arm ever to pass), A=204 only 7/24; joint pairs 3/24. Diagnosis: perfect exclusion anti-correlation — winner-take-most vacancy dynamics make simultaneous growth rare while *every* arm stays measurable. Archived `failed-designs/2026-08-23-stage7b-denominator-feasibility-gate-no-go/` |
| **signed bracket** (`stage-7b-signed-bracket-preregistration.md`) | Repair attempt 4 (final): complete the estimand rather than substitute it — full-real-line Lotka certification so every measurable arm emits a signed bracket; sign carries sub/supercritical classification; pairing needs two signed numbers, not two positive signs | Gate **PASSED 24/24** with bit-exact estimator-layer regression identity → freeze `7d21153` → single retained execution |

**Final registered outcome** (`results/stage7b-signed-bracket/`, execution
note in `docs/stage-7b-signed-bracket-execution-note.md`):

- 32/32 replicates COMPLETE — zero `NO_FINITE_ROOT`, zero `CRITICAL`,
  zero integrity failures; the availability defect that killed three
  predecessor designs is closed.
- Median paired difference of certified finite-root brackets:
  **−1/128** against the preregistered contrast floor **Δr_min = 1/100**
  → class **`NO_ESTABLISHED_CONTRAST`**.
- Co-report `ONE_ARM_SUBCRITICAL`: genotype A=204 entirely below zero in
  21/32 replicates, A=102 in 9/32 (descriptive).
- Sign split of paired differences: 21 negative / 9 positive / 2 zero —
  direction favours LOW but is not uniform (descriptive).
- Raw artifact 18,828,711 B, SHA-256 `6268a3da…73d3d`; reducer bit-exact,
  applied exactly once; wall ≈ 54 min.

The Stage 7B confirmatory line therefore closes as a **registered null**.

## Part II — The repeated pattern, read honestly

Three facts have now each been established more than once, by different
instrumentation:

1. **The allocation channel is mechanically real at both levels.**
   Individually: 7B0 produced the exact account splits
   (`Y_R = (A/D)Y`), funding and endowment differences, recovery, and
   reversal-provenance behaviour, gate by gate. At population level: the
   same intervention, embedded in the full transaction-safe mechanics,
   produces measurably different cohort schedules — certified `L(0)`
   values up to ≈ 1.5, genotype-level status asymmetries (23 vs 11
   supercritical replicates), real signed brackets everywhere. The
   mechanism is not a bookkeeping fiction; it reaches demography.

2. **Its expression at the tested ecologies is weak relative to the
   registered floor.** The median paired invasion-growth difference
   (−1/128 ≈ −0.0078) is an order of magnitude below Δr_min = 0.01, and
   the sign is not uniform across replicates. Whatever allocation
   difference exists, Euler–Lotka windows at this scale do not resolve
   it above the floor we committed to before looking.

3. **The tested ecology fights the paired design.** At N=48/E=900/W=1200
   the population is saturated end-to-end (~48 member-present ticks per
   tick against capacity): reproduction is vacancy-limited throughout,
   exclusion is winner-take-most (exactly one arm supercritical in 21/24
   shakedown replicates, perfect anti-correlation), and which lineage
   wins is replicate-stochastic priority effect, not allocation. A
   paired-difference design over jointly-growing pairs is thus sampling
   the rare joint-growth tail of its own ecology — the design's
   precondition is the ecology's least representative event.

The structural diagnosis behind fact 3 deserves naming because it
predicts failure of naive versions of direction (a) too: **at
saturation, both arms draw vacancies from one pool, so the arms are not
independent replicates — they are competitors.** Raising E or hazard
changes who wins and how fast, but does not by itself decouple them;
only lower occupancy (higher hazard relative to income, larger N, shorter
effective saturation), non-competing measurement designs, or endpoints
computed within-genotype can do that.

There is also a power diagnosis: **Euler–Lotka on 600-tick-class windows
with k=32 may be underpowered for this effect size by construction.**
One scalar root per genotype-replicate collapses an entire window's
demography into 64 numbers per experiment, then takes paired medians.
A per-capita difference that is real but small — at the individual level
the mechanism is exact and large: from identical income, HIGH reaches
first bout with ~2.27× LOW's reproductive working reserve (`R_w` 469/5 vs
413/10 in Block A), hence ~2.27× the child endowment — is being
asked to move a median of 32 noisy, priority-effect-contaminated
bracket differences across a floor set at 1/100. No post-hoc rescue of
the closed line is permitted or needed — but the next registration
should be sized against these measured dispersions, not against hope.

Finally, the methodological record: **the discipline worked.** Three
infeasible designs were caught by pre-freeze gates on shakedown tables
before touching the confirmatory seed table; the confirmatory table
`20261822 + i` was executed exactly once in the project's history; every
falsified design is archived, never deleted; the one rule application
was source-frozen and bit-exact. Four falsifications (three designs +
one null result) were absorbed without a single compromised inference.
That is the system operating as designed, and it is itself a finding.

## Part III — Decision memo: candidate Stage 8 directions

Four defensible directions exist. They are not mutually exclusive across
sessions, but each needs its own superseding preregistration before any
freeze or retained execution. Costs are stated in session-scale units
(one session ≈ one cron run).

### (a) Stronger-contrast ecology under a superseding preregistration

Re-ask the same closed question at a new ecology chosen for signal:
higher `E` (faster cycles → more generations per window), longer window
(`W = 1200–1800`), possibly higher hazard arm(s), and — critically — a
floor `Δr_min` re-derived from a disclosed power analysis of the
retained bracket dispersions, never retuned after inspection.

- **Cost:** config parametrisation reuses frozen modules additively
  (estimator, solver, mechanics are frozen but importable); new shakedown
  table + feasibility gate (1 session), freeze + 32-replicate retained
  run (1–2 sessions, ~1–4 h wall). Total ≈ 3 sessions.
- **Value:** directly quantifies whether the null was an ecology artefact.
- **Risk:** highest scientific risk of "turning the knob until it
  speaks" — mitigable only by committing the power analysis *into* the
  superseding preregistration before execution. Also inherits the
  coupled-vacancy problem unless the ecology genuinely de-saturates;
  the Part II diagnosis suggests higher hazard (not just higher E) is
  the lever that buys independent arm dynamics.

### (b) Endpoint-family change: realised recruitment / vacancy-capture estimand

The 7B1 registration already decided (§6.2) that binding vacancy capture
is part of the primary estimand, with separately reported bout-completion
rate (intrinsic), vacancy-capture rate (ecology), and their product =
realised recruitment; the shadow `would_admit` counters exist and are
tested side-effect-free. A superseding preregistration could promote a
recruitment-based contrast to primary endpoint — per-birth events give
orders of magnitude more statistical material than one root per
replicate, and within-genotype rates decouple the arms that
Euler–Lotka pairing couples.

- **Cost:** new measurement layer over existing ledgers + gate tooling
  (1 session); freeze + retained run (1 session). Total ≈ 2–3 sessions.
  Cheapest of the executable options.
- **Value:** tests the nearest alternative hypothesis — that allocation
  differences express in recruitment events even when growth-rate roots
  do not separate. If this also nulls, the weak-expression conclusion
  becomes much stronger (two endpoint families).
- **Risk:** establishment-weighted quantities are mediators by default
  (architecture §9.4 / 7B1 §6.1); promotion to endpoint requires the
  registered life-cycle demonstration that first-reproduction
  establishment captures subsequent reproductive contribution. That
  demonstration must be part of the new preregistration, or the result
  inherits a permanent mediator caveat.

### (c) Open the mutation gate: dedicated-locus α evolution

The architecture's evidentiary ladder (findings synthesis M1;
7B0 §11) is: 1. channel exists → 2. restricted architecture evolves
through it → 3. open population outcome. Rung 1 is now established at
both levels, and 7B0 §11's precondition — "only after a separately
preregistered Stage 7B1 result may dedicated-locus mutation be
considered" — has been satisfied since the 7B1 PASS. A Stage 8
registration would fix the mutation kernel on the `A` locus (legal
lattice, step distribution, `D` resolution), starting distribution,
duration in hazard-scaled generations, effective population size, and a
trajectory/frequency endpoint, per architecture §9.5 items 1–5.

- **Cost:** highest. Mutation kernel + RNG-invariance mechanics + new
  test matrix (1–2 sessions); superseding preregistration with full
  kernel specification (1 session); freeze + retained evolutionary runs
  (1–2 sessions). Total ≈ 4–5 sessions.
- **Value:** highest. It is the first actual evolution in Stage 7 and
  the only route to the programme's original external-validation
  question (does extrinsic mortality select allocation speed?). Note
  that rung 2 does **not** require rung 1's confirmatory contrast:
  selection integrates small differences over many births and
  generations, and a frequency trajectory is a fundamentally
  higher-power instrument than 32 paired roots. The registered null
  constrains what fixed-genotype contrast is detectable, not whether
  selection can act.
- **Risk:** a frequency null would be ambiguous between "no selection"
  and "selection too weak at supplied variation" unless the kernel and
  duration are powered generously up front; also the largest new-code
  surface since 7B1.

### (d) Close the programme

Freeze the codebase, extend `docs/public-technical-essay.md`
("Conservation is not an ecology", currently covering Stages 1–6 and the
7B0-era lesson) with the Stage 7B arc — three falsified repairs caught
by gates, then an honest registered null — and issue a final report.

- **Cost:** 1–2 sessions. Lowest.
- **Value:** real. The Stage 7B failure lineage is the strongest
  demonstration of preregistration discipline the project owns, and the
  essay's thesis (conservation ≠ ecology; channels ≠ selection) is
  completed, not contradicted, by the null.
- **Risk:** forecloses (a)–(c); the essay would describe a ladder whose
  second rung was never attempted.

### Recommendation

**(c), with (b)'s telemetry riding along as registered descriptive
co-reports, at an ecology informed by (a)'s power analysis.** Reasons:
rung 2 is the unattempted step the whole architecture was built toward;
it is the only direction that can address the programme's motivating
question rather than re-measuring a known-weak contrast; the mutation
run's *descriptive* recruitment/vacancy telemetry costs almost nothing
because 7B1 already built and tested it; and a well-powered rung-2
result (either sign) plus the existing rung-1 null makes direction (d)
— whichever session it happens — a far stronger essay. If the owner
prefers minimal cost first, (b) is the best standalone next step: it
reuses everything, and either outcome sharpens the interpretation of
every other option. A pure (a) rerun without (b)/(c)'s reframing risks
repeating the coupled-vacancy pattern at higher cost.

**Procedural requirements common to all options:** superseding
preregistration committed before implementation freeze; freeze manifest
before any retained run; frozen modules reused byte-identically or by
verbatim-additive copy, never edited; shakedown tables distinct from any
confirmatory table touched before; failed designs archived; suite kept
green; push after every commit.

## Part IV — Session log

- 2026-08-23 (session 1): this review written and committed. Suite
  green at 293 tests (4 environment skips). Follow-up work that session:
  read-only integrity audit + descriptive dispersion/power scoping of
  the retained signed-bracket artifacts as non-binding design input for
  whichever direction the owner selects — committed as
  `docs/stage-8-signed-bracket-audit.md` with tool
  `src/audit_stage7b_signed_bracket.py` and 10 new tests; audit verdict:
  all hashes match, reducer re-run byte-identical, all four freeze
  manifests drift-free, independent recomputation reproduces the
  registered outcome exactly; key descriptive facts: LOW-arm midpoints
  pile up at the 1/512 resolution floor in ≥24/32 replicates, paired
  differences are heavy-tailed (median |Δ| = 25/32 of floor, 7/16 of
  pairs above floor with mixed signs), consistent with exclusion-
  variance domination rather than a shifted distribution.

- 2026-08-23 (session 2): direction (c) selected under the owner's standing
  autonomous-advance order (no contradicting owner input is possible in a
  cron session; Part V clause 2 applied). Superseding preregistration for
  dedicated-locus α evolution committed as
  `docs/stage-8-alpha-evolution-preregistration.md`: registered kernel
  (`p_μ = 1/2`, `δ ∈ {±1,…,±4}` clamped on `{0..255}`, `T=128`/`D=255`
  frozen), carried ecology and founder pair at `α_ref = 3/5`,
  `W = 2400` (20 hazard turnovers), fresh confirmatory table
  `20284617+i` (`k = 24`) and shakedown table `20293311+j` (`k = 12`),
  primary endpoint = terminal mean `ᾱ_end` vs `α_ref` beyond floor
  `8/255`, decision rule = one-shot concordance classification
  (`≥18/24` ⇒ directional; neutral-reference tail ≤ 0.02266 two-sided,
  conservative by construction), feasibility gate G1–G3, freeze policy.
  Implementation window opens on that commit; no retained execution
  before gate + freeze. Suite green at 303 tests at commit time.

- 2026-08-23 (window session): implementation window completed in two
  units. (1) `d8b2053`: carried 7B1 fault-injection matrix
  re-parameterised onto `Stage8Population`, all seven boundaries, with
  the registered draws-stay-consumed-across-rollbacks assertion (suite
  323). (2) `91986f4`: measurement layer `stage8_alpha_measure` (exact
  census snapshots incl. the registered ᾱ estimator; checkpoint loop
  proven bit-identical to frozen `run_window` with snapshot purity
  asserted; kernel reconciliation identities; genome-freeze T/D audit;
  bit-exact stream replay; ancestry birth counts; terminal α-terciles),
  runner `run_stage8_alpha` (confirmatory/shakedown tables,
  kernel_draw_chain per replicate, retained-directory guard), source-
  frozen reducer `reduce_stage8_alpha` (§5 rule, pre-rule validation),
  gate `stage8_gate` (G1–G3 with in-gate re-execution replay), output
  schema doc; 52 new tests, suite 375.

- 2026-08-23 (same session, mid-flight): a concurrent session committed
  the pre-freeze adversarial review (`docs/stage-8-debate-log.md`,
  `8f7bb89`) BLOCKING the as-registered chain — O1 founder-priority
  confound, O2 missing H1 power, O3 exchangeability contradicted by the
  retained record. The block was honoured before any execution: the §6
  gate was about to run and was NOT run; zero executions consumed;
  tables `20284617+i` / `20293311+j` retired unexecuted (disposition
  item 1 keeps the additive layer byte-identically). Per binding
  disposition item 2, committed this programme's superseding repair
  registration
  `docs/stage-8-alpha-evolution-repair-preregistration.md`:
  **paired mutation-on/off reference arms** at identical seeds (Arm M =
  registered kernel verbatim; Arm R0 = frozen stack, no mutation site),
  endpoint restated as the paired difference
  `D_i = ᾱ_end(M,s_i) − ᾱ_end(R0,s_i)` beyond floor `4/255`
  (= max kernel step AND ≥ 2σ of the null cloud-mean deviation),
  thresholds 16/18/24 carried, fresh tables `20310529+i` (24 pairs) /
  `20421301+j` (12 shakedown pairs), G1–G4 gate with reference-arm
  zero-draw checks, one-shot confirmatory class of 48 runs (~85 min at
  two workers), and the O2-mandated H1 power derivation in α-units:
  detectable slope β ≈ 4.4×10⁻⁴ realistic (7.7×10⁻⁵ permanent-coexistence
  ceiling) vs the recorded cross-sectional bound ≈ 8×10⁻⁵ — expected-null
  registered up front as a clean paired closure of direction (c), with
  non-null as genuine discovery.

## Part V — Next run should pick up

1. **Stage 8 REPAIR implementation window** per
   `docs/stage-8-alpha-evolution-repair-preregistration.md` §8(1):
   additive modules only — R0 constructor path (frozen
   `Stage7B2Population` at the stage-8 configuration/window), runner
   extension for pairwise execution (`arm`, `pair_index`; retained-
   directory guard updated for `results/stage8-alpha-evolution-paired/`),
   NEW source-frozen paired reducer (`reduce_stage8_paired.py`, §5 rule),
   gate updates (G4 reference-arm checks, pair table completeness),
   schema addendum, tests. The existing measurement layer carries over;
   edit only files no freeze manifest has pinned; Stage 7B frozen stack
   byte-untouched.
2. Then, in order: §7 feasibility gate on the 12-pair shakedown table →
   §8 freeze manifest → single retained confirmatory suite
   (`20310529+i`, both arms, `W=2400`) → one-shot reduction under §5 →
   execution note + post-retention audit.
3. Read the outcome per §6's registered interpretation: null ⇒ direction
   (c) closes at this ecology with the paired redistribution bound (feed
   into review directions (a)/(d)); established ⇒ discovery at 20× finer
   longitudinal resolution. Either way the NEXT registration decides the
   follow-on; nothing may be added to escape a null.
4. Keep the suite green; push after every commit; keep the tree clean;
   do not rerun closed lines or touch retained artifacts.
