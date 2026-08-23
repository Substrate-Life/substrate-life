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

- 2026-08-23 (sessions 3–5, incl. a concurrent duplicate): the binding
  §7 gate ran on `20421301+j` (first full-window execution in the
  programme; ≈118 min) and **FAILED G2 only** — 12/12 pairs COMPLETE,
  G1/G3/G4 clean, zero overflows/invalid runs, but all 24 arms recorded
  `tick_checkpoints = W+2` against the tooling's derived expectation
  `W+1`. Diagnosis verified against frozen source: two constructor
  layers each append an `initial` closure entry
  (`stage7_slice2.py:91`, `stage7b2_population.py:164`) plus one
  `tick_complete:<t>` per tick. Archived
  `failed-designs/stage8-paired-gate-g2-checkpoint-bookkeeping/`;
  superseding registration #3
  (`docs/stage-8-alpha-evolution-gate-repair-preregistration.md`)
  carries every substantive element verbatim and changes ONLY the G2
  operationalization (W+2 + head/tail label pins), the schema §1.1
  parenthetical (by supersession), and re-authorises ONE corrected-gate
  execution on the same shakedown table (first run emitted no endpoint
  data — uncontaminated). A duplicate-session handoff left part of the
  window uncommitted (`06e03a1` message/content mismatch, disclosed);
  this session completed it (`8392963`): corrected G2 in BOTH gate
  modules, threshold-free `factual_shakedown_context` block, freeze-
  manifest builder + its test matrix, fixtures aligned — suite **423
  OK** (4 skipped). Round-3 pre-freeze debate recorded (ADVOCATE
  SURVIVES; new A1 obligation on the freeze note). The single authorised
  corrected-gate rerun is executing as this entry is committed.

- 2026-08-23 (session 6): **corrected gate PASSED — freeze `f1e6880`
  committed; the ONE retained execution is in flight.** Disclosure
  first: session 5's in-flight rerun died with that session before its
  process emitted anything observable (no stdout capture, no file, no
  transcript); zero observations were consumed or seen, so registration
  #3 §4's "execute once more" is discharged by exactly ONE observed
  corrected-gate execution — this session's (~2 h 05 m wall, two
  workers, stdout-only/unretained, transcript under `/tmp` only).
  Result: **12/12 pairs both arms COMPLETE** (threshold 8); G1 PASS
  12/12 with zero genome-freeze violations; G2 PASS zero overflows,
  zero checkpoint failures under the corrected semantics (`W + 2`,
  head `['initial','initial','tick_complete:0']`, tail
  `'tick_complete:2399'`); G3 PASS zero kernel-audit failures plus
  bit-exact full-replicate re-execution replay of seed 20421301 (1034
  records, 1574 draws; digest/births/draw-chain identical); G4 PASS
  zero R0 mutation events or draws, zero seed mismatches. Factual
  shakedown context (threshold-free): Arm-M mutation decisions 12023,
  kernel draws 18037, terminal live census 48..48 on all 24 complete
  arms (zero extinctions), Arm-M distinct-A range 8..15. The
  pre-execution freeze manifest was built by the registered builder
  from this gate summary: 30 files pinned SHA-256 + byte size, ZERO
  hash drift versus every prior retained manifest, full factual gate
  summary embedded. Single freeze commit `f1e6880` carries the Round-3
  A1 obligation in its message: decision-path-field validation
  substrate (corrected G2 labels, G3 bit-exact re-execution, W = 120
  plumbing coverage, reducer ≥ 15 pre-rule refusals) and the disclosed
  nonzero residual risk for W-derived counts (read by no mechanic;
  outside the §5 decision path). Immediately after the push, the ONE
  authorised retained confirmatory suite was launched
  (`20310529+i`, k = 24 pairs = 48 runs, W = 2400, two workers) toward
  `results/stage8-alpha-evolution-paired/confirmatory-paired-20310529.json`
  — executing as this entry is committed.

- 2026-08-23 (session 7): **THE ONE retained confirmatory suite
  executed and reduced exactly once — registered NULL
  (`NO_ESTABLISHED_DIRECTION`); Stage 8 rung 2 closes at this ecology.**
  Execution: launched 14:55:41 UTC immediately after this entry's
  predecessor was pushed, `--workers 2`, exit 0, wall ≈ 2 h 46 m (the
  prereg §8 estimate was ≈ 85 min; disclosed as fact — event digests
  and draw chains bind streams, not clocks). Pre-reduction integrity
  checked twice: all 30 manifest pins matched the working tree both
  before launch and before reduction (zero drift), and the raw
  artifact's embedded `source_manifest_sha256` over its 14 sources
  matched the freeze manifest exactly. Runner summary: 24/24 pairs both
  arms COMPLETE, 48/48 runs COMPLETE, `PENDING_REDUCTION`. The
  source-frozen reducer applied §5 exactly once (pre-rule validation
  silent pass): k_eff = 24/24 eligible, movers-up **9**, movers-down
  **6**, non-movers 9 against concordance 18 ⇒ **NO_ESTABLISHED_DIRECTION**;
  `leakage_pairs = 0`. Obligations from debate Rounds 2–3 discharged in
  `docs/stage-8-paired-execution-note.md`: empirical null spread of D_i
  reported descriptively (mean −47/73440 ᾱ-units ≈ −0.16/255 lattice
  units; population sd ≈ 5.71/255 — ≈ 2.9–3.6× the Round-2
  composition-noise proxy band; recorded as proxy-underestimation,
  size unaffected under the frozen count-based rule); ancestry-
  plurality monitor clean so A3 flip-sign leakage is not indicated
  (sign split 13 positive / 11 negative); residual W-derived-count risk
  pointer restated. Factual threshold-free context: Arm M 23,933
  mutation decisions / 35,981 kernel draws / 0 problems; Arm R0
  zero-decision, zero-draw, empty chain, telemetry passing on every run;
  admitted births identical across arms (23,933 each — the shared
  phenotype-blind demographic skeleton at equal seeds); terminal
  distinct-A M 9..17 vs R0 1..2; zero extinctions, n_live = 48 on all
  48 runs. Reading per §5 / former Part V item 3: direction (c) closes
  AT THIS ECOLOGY with the paired redistribution bound (best side 9/24
  < 18; median |D| = 4.6/255 at floor scale but signs split), feeding
  review directions (a)/(d). Nothing added to escape the null. Raw +
  reduced artifacts, the execution note, and this entry are committed
  together; retained artifacts immutable henceforth.

- 2026-08-23 (session 8): **the deferred follow-on question is ANSWERED
  — computed closure.** The cron briefing snapshot was already stale on
  arrival: every listed standing task had been discharged by sessions
  1–7 (fault-matrix tests tracked and passing within the suite; §G-gate
  lineage closed through registration #3; freeze `f1e6880` → THE ONE
  retained execution → one-shot reduction `NO_ESTABLISHED_DIRECTION` →
  post-retention audit 17/17 PASS at `8ebe36d`; direction (d)
  close-out at `cd88d11`/`9059753`). Session verification pass first:
  origin synced 0 ahead / 0 behind at `8ebe36d`, tree clean, suite
  green (**419 passed, 4 skipped**, 19 subtests, via
  `uv run --with pytest python -m pytest src -q`). The one genuinely
  open item was repair-prereg §6's deferred follow-on fork, so Round 5
  of the adversarial debate was conducted on exact arithmetic
  (delegation tooling unavailable again — disclosed in-log;
  parent-argued against repo facts). The ADVOCATE's coexistence-regime
  probe fell to measured-number attacks: assumption-light shift-method
  power on the retained 24 `D_i` gives **3.0% power for a true shift
  equal to the whole floor**; ~50% power needs μ ≈ 7.48 lattice units
  (1.87× floor); the concordance k-cliff means adding replicates
  *reduces* power below per-pair p = 0.75; realistic-regime window
  requirements reach W ≈ 26k ticks static-σ and diverge (T ≈ 400
  turnovers) once σ_D ∝ √W cloud drift is priced; the mean-rule
  alternative is powered only for slopes ≥ 4.5× the cross-sectional
  bound; the recruitment family is mechanically null at saturation
  (admitted-births identity `23,933 = 23,933`). Verdict **CLOSURE
  SURVIVES** (commit `b4b730a`); obligations executed same session:
  `docs/stage-8-followon-power-memo.md` committed with every constant
  program-verified, reopening conditions R1–R3 registered (memo §9),
  an explicit no-evolutionary-execution hold in force until one fires,
  and this Part V rewritten to point at the computed answer.
  Housekeeping repair in the same unit: stripped 69 stray literal '+'
  diff-marker prefixes that an earlier session's malformed append had
  committed into the session 6–7 entry text of this file (verified
  byte-exact: no other lines touched).

- 2026-08-23 (session 9): **follow-on power memo independently audited
  — 21/21 clean, zero exact-claim failures; Round-6-authorized visible
  corrigendum appended to the memo (§11).** Verification-only unit under
  the Part V item 3 hold; no execution registered or run. Arrival state
  verified first: cron briefing stale again (every listed standing task
  already discharged by sessions 1–8), HEAD `20765f3` = origin/main,
  tree clean, suite green (**419 passed, 4 skipped**, 19 subtests).
  New standalone auditor `src/audit_followon_power_memo.py`
  (read-only, imported by no mechanic) re-derived every constant of the
  binding closure memo from the retained raw/reduced artifacts and
  source docs alone: all 24 exact D_i, mean −47/73440, pop sd 0.022377
  (= 5.7061 lattice units), sample sd 0.022858, median |D| = 437/24480,
  movers 9/6/9, sign split 13/11, null anchor 190051/2²⁴, all 18
  concordance tail cells including the k-cliff at p = 0.70,
  shift-method counts/powers, minimal shift 359/48 = 1.87× floor,
  mean-rule sizing, divergence solution T ≈ 401.8 / W ≈ 48,220 /
  ≈ 55.5 h, admitted-births identity 23,933 = 23,933 per seed AND in
  total, five §10 provenance digests, 14/14 frozen source pins.
  Findings confined to self-labelled approximation passages: F-1 §4
  μ\*₅₀ printed ≈ 7.5 recomputes to 7.428 at the population σ (sample-σ
  basis switch undeclared); F-2 "both maps agree within 0.03 units"
  holds only for the printed rounded pair (consistent gap 0.051); F-3
  ceiling-80% wall cell 5.849 vs ≈ 5.9 h (final-digit estimate
  rounding). Materiality: none — R1's operative threshold derives from
  sd(D) = 5.7061 which reproduced bit-exactly; true-50% rows sit below
  the memo's conservative rows (28.2 h realistic / 4.9 h ceiling;
  R1's ≈ 5–6 h band unchanged); doors R1–R3 verified unfired. Debate
  Round 6 conducted on the disposition fork amend-vs-append
  (delegation unavailable again — disclosed in-log): **ADVOCATE
  SURVIVES narrowly** for a dated, visible corrigendum over a silent
  errata layer, subject to adversarial constraints + auditor conditions
  (audit committed first as authority `d19d7c2`; originals
  byte-preserved; correction marked and citing its pre-corrigendum
  digest `1e4a6515…`). Executed same session: audit document
  `docs/followon-power-memo-independent-audit.md` + memo §11
  corrigendum; this entry; Part V housekeeping line updated.

## Part V — Next run should pick up

1. **The programme is CLOSED on computed grounds (session 8).** The
   Round-4 open question ("the NEXT registration decides the
   follow-on") was answered by Round 5 of the adversarial debate
   (`docs/stage-8-debate-log.md`): **CLOSURE SURVIVES**. The full
   derivation is `docs/stage-8-followon-power-memo.md`: a true shift
   equal to the whole registered floor yields 3.0% exact power on the
   frozen concordance rule at the measured sd(D) = 5.7061 lattice
   units (~50% needs μ ≈ 1.87× floor); rule power *decreases* with k
   below per-pair p = 0.75, so no replicate count rescues it;
   realistic-regime window extension is ≈ 26k ticks static-σ and
   diverges once σ_D ∝ √W cloud drift is priced; the mean-rule
   alternative reaches only slopes ≥ 4.5× the cross-sectional bound;
   recruitment endpoints are mechanically null at saturation
   (phenotype-blind admission identity `23,933 = 23,933`). Stage 8
   rung 2 therefore closes as a registered bounded negative whose
   "no established direction" reading is now complemented by a
   computed demonstration that no affordable instrument of this family
   could have returned otherwise.
2. **Reopening conditions R1–R3 are the only lawful doors back**
   (memo §9; binding on future sessions): **R1** — an independently
   justified measurement establishing σ_D ≤ 3.0 lattice units at
   demonstrated coexistence persistence ≥ 40 turnovers (revives the
   ceiling-regime strengthened probe, review direction (a), at an
   estimated ≈ 5–6 h wall); **R2** — a genuinely de-saturated ecology
   that breaks the phenotype-blind admitted-births identity AND a
   passed 7B1 §6.2 life-cycle promotion demonstration (revives the
   recruitment-endpoint family, direction (b)); **R3** — owner
   redirection, which supersedes without prejudice as always.
3. **Hold:** until one fires, no evolutionary execution is authorised
   anywhere in this programme; lawful units are verification,
   documentation, and owner-directed work.
4. **Retained-class immutability unchanged:** everything under
   `results/stage7b-signed-bracket/` and
   `results/stage8-alpha-evolution-paired/`, both freeze manifests,
   and `docs/stage-8-paired-execution-note.md` are never rerun, never
   edited, and accept no supplementary endpoints; `failed-designs/`
   remains untouched append-only history; closed lines stay closed.
5. **Housekeeping:** suite green re-verified session 8 (**419 passed,
   4 skipped**, 19 subtests) and again at session 9 arrival at HEAD
   `20765f3` (**419 passed, 4 skipped**, 19 subtests); session 9 added
   the follow-on-memo independent audit
   (`docs/followon-power-memo-independent-audit.md`,
   `src/audit_followon_power_memo.py`) and the Round-6-authorized memo
   corrigendum (memo §11, visible/dated, originals byte-preserved);
   push after every commit; keep the tree clean.
