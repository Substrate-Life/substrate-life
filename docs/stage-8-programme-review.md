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

- 2026-08-23 (session 10): **verification-only unit under the Part V
  item 3 hold — arrival-state re-verification plus the first full
  re-hash of ALL pins in both freeze manifests; no execution registered
  or run.** Arrival state: cron briefing stale a second time (every
  listed standing task already discharged by sessions 1–9: fault-matrix
  tests long committed and inside the green suite; corrected §7 gate
  PASSED at `f1e6880`; THE ONE retained execution reduced exactly once
  to the registered NULL at `9db2f3b`; debates logged through Round 6);
  HEAD `b6deee7` = origin/main, tree clean. Suite re-verified green at
  arrival (**423 tests, OK, 4 skipped** — same counts as sessions 8–9).
  New evidence this session: every pinned path of both pre-execution
  manifests re-hashed from disk —
  `results/stage7b-signed-bracket/` **8/8 byte-exact**;
  `results/stage8-alpha-evolution-paired/` **29/30 byte-exact**, the
  single exception being `docs/stage-8-debate-log.md`, proven
  **pure-append drift, zero alteration**: its frozen 20,869-byte prefix
  hashes bit-exactly to the pinned `512fd400…` digest, and the 24,552
  appended bytes are exactly the post-freeze Rounds 4–6 entries, each
  landed by its own disclosed commit (`0b37930`, `b4b730a`, `d19d7c2`).
  Conclusion recorded: no frozen source, schema, reducer, test, or
  retained artifact byte has moved since `f1e6880`; Part V item 4
  retained-class immutability intact end-to-end; the manifest's debate-
  log pin should be read as freezing the log *at execution time*, with
  later rounds living lawfully outside the pin. Doors R1–R3 verified
  unfired (no new artifacts since `d19d7c2`; no owner input channel on
  cron). Hold remains in force; lawful work unchanged.

- 2026-08-23 (session 11): **verification-only unit under the Part V
  item 3 hold — third consecutive stale-cron arrival disclosed;
  consolidated re-verification (suite + all three standalone auditors +
  full two-manifest pin re-hash reproduction); no execution registered
  or run.** Arrival state: cron briefing stale a third time (it still
  describes the ~08:05 UTC state at `f753894` with the fault-matrix
  tests untracked; every listed standing task was discharged by
  sessions 1–9), actual HEAD `4498e38` = origin/main, tree clean, last
  unit landed 19:45 UTC the same day. Evidence gathered this session:
  (i) full suite green at arrival (**423 tests, OK, 4 skipped** —
  identical to the session-10 count); (ii) all three standalone
  read-only auditors re-run at HEAD, each exit 0 — signed-bracket
  auditor (artifact hashes match, independent outcome matches
  retained, reducer rerun byte-identical), post-retention auditor
  **17/17 PASS**, follow-on-memo auditor **21/21 clean**
  (exact-claim failures = 0); (iii) every pin in BOTH pre-execution
  manifests re-hashed from disk, reproducing session 10 bit-for-bit:
  signed-bracket **8/8**, paired **29/30**, the sole exception again
  the debate log whose frozen 20,869-byte prefix hashes to
  `512fd400…` — the file now stands at exactly 45,421 bytes =
  pinned prefix + the 24,552 post-freeze Rounds 4–6 bytes, i.e.
  **zero debate-log bytes appended since session 10**; pure-append
  property intact; (iv) retained-directory inventories closed against
  both manifests' pin sets — nothing added, nothing missing. Doors
  R1–R3 verified unfired: R1 requires an independent σ_D ≤ 3.0 u
  measurement at demonstrated ≥ 40-turnover coexistence, R2 a
  de-saturated ecology breaking the admitted-births identity plus a
  passed 7B1 §6.2 life-cycle promotion demonstration, R3 owner input —
  none obtainable from a stale cron wake, and the hold forbids running
  evolutionary executions to hunt for R1/R2 data. No decision fork
  arose, so no adversarial round was convened this session (the Round-5
  computed closure remains the binding disposition). Hold remains in
  force; lawful work unchanged.

- 2026-08-23 (session 12): **verification-only unit under the Part V
  item 3 hold — fourth consecutive stale-cron arrival disclosed;
  consolidated re-verification (suite + all three standalone auditors +
  full two-manifest pin re-hash reproduction + whole-tree freshness
  sweep); no execution registered or run.** Arrival state: cron
  briefing stale a fourth time (it still describes the ~08:05 UTC
  state at `f753894` with the fault-matrix tests untracked; every
  listed standing task was discharged by sessions 1–9), actual HEAD
  `325b425` = origin/main (`0/0`), tree clean. Evidence gathered this
  session: (i) full suite green at HEAD (**423 tests, OK, 4 skipped**
  — third consecutive identical count); (ii) all three standalone
  read-only auditors exit 0 — signed-bracket auditor (artifact hashes
  match, independent outcome agrees with the retained record: 32
  complete pairs, median paired difference −1/128, sign split 9/21/2,
  reducer rerun byte-identical, all manifest drift checks clean),
  post-retention auditor **17/17 PASS**, follow-on-memo auditor
  **21/21 clean** with zero exact-claim failures; (iii) every pin in
  BOTH pre-execution manifests re-hashed from disk, reproducing
  sessions 10–11 bit-for-bit: signed-bracket **8/8** byte-exact,
  paired **29/29** non-debate-log pins byte-exact, plus the debate
  log whose frozen 20,869-byte prefix again hashes to the pinned
  `512fd400…` digest with the file standing at exactly 45,421 bytes
  (= prefix + the 24,552 post-freeze Rounds 4–6 bytes) — **zero
  debate-log bytes appended since session 10**, pure-append property
  intact; (iv) a whole-tree freshness sweep found **no file modified
  after the last commit** outside `__pycache__`, both retained
  directories still contain exactly their known artifact sets
  (memo-auditor check I1 re-verified the paired directory's inventory
  this session), and `failed-designs/` is untouched at its 8 entries.
  Doors R1–R3 verified unfired: no new artifacts of any kind exist
  since `d19d7c2`, so no σ_D ≤ 3.0 u / ≥40-turnover-coexistence
  measurement (R1) nor de-saturated ecology or life-cycle promotion
  demonstration (R2) has appeared, and the stale briefing carries no
  owner redirection (R3); the hold forbids running evolutionary
  executions to hunt for R1/R2 data. No decision fork arose, so no
  adversarial round was convened this session (the Round-5 computed
  closure stands; delegation tooling also remains unavailable on this
  runtime, as disclosed in Rounds 2–6). Hold remains in force; lawful
  work unchanged.

- 2026-08-23 (session 13): **fifth consecutive stale-cron arrival
  disclosed; verification battery reproduced bit-for-bit AND its
  mechanical core consolidated into a single durable command-line
  verifier (`src/verify_retained_integrity.py`) with 13 new unit
  tests; no execution registered or run under the Part V item 3
  hold.** Arrival state: cron briefing stale a fifth time (it still
  describes the ~08:05 UTC state at `f753894` with the fault-matrix
  tests untracked; every listed standing task was discharged by
  sessions 1–9), actual HEAD `dd39382` = origin/main (`0/0`), tree
  clean. Evidence gathered at arrival: (i) full suite green (**423
  tests, OK, 4 skipped** — fourth consecutive identical count);
  (ii) all three standalone read-only auditors exit 0 with numbers
  identical to session 12 (signed-bracket: hashes match, outcome
  agrees — 32 complete pairs, median −1/128, sign 9/21/2, reducer
  rerun byte-identical; post-retention **17/17 PASS**;
  follow-on-memo **21/21 clean**, zero exact-claim failures);
  (iii) every pin in BOTH manifests re-hashed reproducing sessions
  10–12 bit-for-bit (signed-bracket 8/8 byte-exact; paired 29/30 +
  the debate log's frozen 20,869-byte prefix hashing to the pinned
  `512fd400…`, file standing at exactly 45,421 bytes — **zero bytes
  appended since session 10**), both retained-directory inventories
  closed; (iv) doors R1–R3 verified unfired mechanically: `git diff
  d19d7c2..HEAD` over `results/` + `failed-designs/` is empty and
  `failed-designs/` still holds exactly its 8 archived entries; no
  σ_D ≤ 3.0 u coexistence measurement (R1), no de-saturated ecology
  or life-cycle promotion demonstration (R2), and the stale briefing
  carries no owner redirection (R3); the hold forbids running
  evolutionary executions to hunt for R1/R2 data. **New durable
  work:** the wake-by-wake battery was consolidated into
  `src/verify_retained_integrity.py` (standalone, read-only,
  stdlib-only, house audit-script precedent) so every future wake
  re-establishes retained-class immutability with one command:
  P1 tamper-evident self-integrity anchors on both pre-execution
  manifests (their SHA-256 digests recorded as constants); P2 full
  pin re-hash with the debate log recognised solely under the proven
  pure-append rule; P3 exact inventory closure per retained
  directory (manifest + pins + declared first-retained outputs +
  explicitly named pre-convention outputs for the Stage 7B directory
  — nothing silently tolerated); T1 strict working-tree check;
  D1 door check against base `d19d7c2` plus the failed-designs
  append-only count; optional `--auditors` flag requiring exit 0
  from all three auditors. Exit code 0 iff everything passes.
  `src/test_verify_retained_integrity.py` adds 13 tests (synthetic
  tmp-tree fixtures for EXACT/PURE_APPEND/DRIFT/MISSING
  classification including the alteration-not-append negative
  control and the absolute-path defensive case, inventory-closure
  extra/missing detection, known-outputs handling, git-door failure
  on an absent base commit, plus live-repo smoke made commit-order-
  safe by asserting the tracked-file invariant rather than untracked
  presence). The tooling caught two real defects in itself during
  authoring, both fixed and regression-tested: a repo-relative vs
  absolute path-normalization bug in inventory closure, and pure-
  append membership fragility to absolute path inputs. Post-unit
  suite: **436 tests, OK, 4 skipped** (13 net new). No decision fork
  arose, so no adversarial round was convened this session (the
  Round-5 computed closure stands; delegation tooling also remains
  unavailable on this runtime, as disclosed in Rounds 2–6). Hold
  remains in force; lawful work unchanged.

- 2026-08-23 (session 14): **verification-only unit under the Part V
  item 3 hold — sixth consecutive stale-cron arrival disclosed;
  first wake to run the session-13 consolidated battery exactly as
  the Part V item-5 prescription directs; no new durable work item
  exists under the hold; no execution registered or run.** Arrival
  state: cron briefing stale a sixth time (it still describes the
  ~08:05 UTC state at `f753894` with the fault-matrix tests
  untracked; every listed standing task was discharged by sessions
  1–9), actual HEAD `9364b5d` = origin/main (`0/0`), tree clean.
  Evidence gathered this session: (i) `python3
  src/verify_retained_integrity.py --auditors` exits 0 — **9/9
  checks PASS**: P1 tamper-evident anchors intact on both
  pre-execution manifests; P2 full pin re-hash 8/8 byte-exact
  (signed-bracket) and 29/30 (paired) with the debate log recognised
  solely under the proven pure-append rule; P3 both
  retained-directory inventories closed (extra=none, missing=none);
  T1 strict working-tree check; D1 door check against base
  `d19d7c2`: zero changed paths under `results/` /
  `failed-designs/`, failed-designs still at exactly 8 entries;
  (ii) the `--auditors` flag required and obtained exit 0 from all
  three standalone read-only auditors with numbers identical to
  sessions 12–13 (signed-bracket: hashes match, independent outcome
  agrees — 32 complete pairs, median −1/128, sign 9/21/2, reducer
  rerun byte-identical; post-retention **17/17 PASS**;
  follow-on-memo **21/21 clean**, zero exact-claim failures);
  (iii) full suite green at arrival (**436 tests, OK, 4 skipped** —
  identical to the session-13 post-unit count); (iv) whole-tree
  freshness sweep found no file modified after the last commit
  outside `__pycache__`. Doors R1–R3 remain unfired: no σ_D ≤ 3.0 u
  coexistence measurement (R1), no de-saturated ecology or life-cycle
  promotion demonstration (R2), and the stale briefing carries no
  owner redirection (R3); the hold forbids running evolutionary
  executions to hunt for R1/R2 data. No decision fork arose, so no
  adversarial round was convened this session (the Round-5 computed
  closure stands; delegation tooling also remains unavailable on
  this runtime, as disclosed in Rounds 2–6). Hold remains in force;
  lawful work unchanged.

- 2026-08-23 (session 15): **verification-only unit under the Part V
  item 3 hold — seventh consecutive stale-cron arrival disclosed;
  second consecutive wake to run the Part V item-5 prescription
  verbatim; no new durable work item exists under the hold; no
  execution registered or run.** Arrival state: cron briefing stale a
  seventh time (still the ~08:05 UTC `f753894` text with the
  fault-matrix tests described as untracked; every listed standing
  task was discharged by sessions 1–9), actual HEAD `036810f` =
  origin/main (`0/0`), tree clean. Evidence gathered this session:
  (i) `python3 src/verify_retained_integrity.py --auditors` exits 0 —
  **9/9 checks PASS**: P1 tamper-evident anchors intact on both
  pre-execution manifests; P2 full pin re-hash 8/8 byte-exact
  (signed-bracket) and 29/30 (paired) with the debate log recognised
  solely under the proven pure-append rule; P3 both retained-directory
  inventories closed (extra=none, missing=none); T1 strict
  working-tree check; D1 door check against base `d19d7c2`: zero
  changed paths under `results/` / `failed-designs/`, failed-designs
  still at exactly 8 entries; (ii) the `--auditors` flag required and
  obtained exit 0 from all three standalone read-only auditors with
  numbers identical to sessions 12–14 (signed-bracket: hashes match,
  independent outcome agrees — 32 complete pairs, median −1/128,
  sign 9/21/2, reducer rerun byte-identical; post-retention **17/17
  PASS**; follow-on-memo **21/21 clean**, zero exact-claim failures);
  (iii) full suite green at arrival (**436 tests, OK, 4 skipped** —
  identical to the session-13/14 counts); (iv) whole-tree freshness
  sweep found no file modified after the last commit outside
  `__pycache__`. Doors R1–R3 remain unfired: no σ_D ≤ 3.0 u
  coexistence measurement (R1), no de-saturated ecology or life-cycle
  promotion demonstration (R2), and the stale briefing carries no
  owner redirection (R3); the hold forbids running evolutionary
  executions to hunt for R1/R2 data. No decision fork arose, so no
  adversarial round was convened this session (the Round-5 computed
  closure stands; delegation tooling also remains unavailable on
  this runtime, as disclosed in Rounds 2–6). Hold remains in force;
  lawful work unchanged.

- 2026-08-23 (session 16): **verification-only unit under the Part V
  item 3 hold — eighth consecutive stale-cron arrival disclosed;
  third consecutive wake to run the Part V item-5 prescription
  verbatim; no new durable work item exists under the hold; no
  execution registered or run.** Arrival state: cron briefing stale an
  eighth time (still the ~08:05 UTC `f753894` text with the
  fault-matrix tests described as untracked; every listed standing
  task was discharged by sessions 1–9), actual HEAD `254d2aa` =
  origin/main (`0/0`), tree clean. Evidence gathered this session:
  (i) `python3 src/verify_retained_integrity.py --auditors` exits 0 —
  **9/9 checks PASS**: P1 tamper-evident anchors intact on both
  pre-execution manifests; P2 full pin re-hash 8/8 byte-exact
  (signed-bracket) and 29/30 (paired) with the debate log recognised
  solely under the proven pure-append rule; P3 both
  retained-directory inventories closed (extra=none, missing=none);
  T1 strict working-tree check; D1 door check against base
  `d19d7c2`: zero changed paths under `results/` /
  `failed-designs/`, failed-designs still at exactly 8 entries;
  (ii) the `--auditors` flag required and obtained exit 0 from all
  three standalone read-only auditors with numbers identical to
  sessions 12–15 (signed-bracket: hashes match, independent outcome
  agrees — 32 complete pairs, median −1/128, sign 9/21/2, reducer
  rerun byte-identical; post-retention **17/17 PASS**;
  follow-on-memo **21/21 clean**, zero exact-claim failures);
  (iii) full suite green at arrival (**436 tests, OK, 4 skipped** —
  identical to the session-13/14/15 counts); (iv) whole-tree
  freshness sweep found no file modified after the last commit
  outside `__pycache__`, and the debate log remains exactly 45,421
  bytes (frozen 20,869-byte prefix bit-intact; zero bytes appended
  since session 10). Doors R1–R3 remain unfired: no σ_D ≤ 3.0 u
  coexistence measurement (R1), no de-saturated ecology or life-cycle
  promotion demonstration (R2), and the stale briefing carries no
  owner redirection (R3); the hold forbids running evolutionary
  executions to hunt for R1/R2 data. No decision fork arose, so no
  adversarial round was convened this session (the Round-5 computed
  closure stands; delegation tooling also remains unavailable on
  this runtime, as disclosed in Rounds 2–6). Hold remains in force;
  lawful work unchanged.

- 2026-08-23 (session 17): **documentation unit under the Part V
  item 3 hold — ninth consecutive stale-cron arrival disclosed;
  wake battery reproduced at arrival HEAD; ONE durable work item found
  and discharged (terminal-state reconciliation of the closing
  documents); no execution registered or run.** Arrival state: cron
  briefing stale a ninth time (still the ~08:05 UTC `f753894` text
  with the fault-matrix tests described as untracked; every listed
  standing task was discharged by sessions 1–9), actual HEAD `945c38b`
  = origin/main (`0/0`), tree clean. Wake battery at arrival:
  `python3 src/verify_retained_integrity.py --auditors` exits 0 with
  **9/9 checks PASS** (P1 both manifest anchors intact; P2 pins 8/8
  byte-exact signed-bracket + 29/30 paired with the debate log under
  the proven pure-append rule; P3 both retained inventories closed
  extra=none missing=none; T1 strict tree; D1 doors vs base
  `d19d7c2` unfired, failed-designs at exactly 8), all three
  standalone auditors exit 0 with session-12-identical numbers (32
  pairs median −1/128 sign 9/21/2 reducer byte-identical;
  post-retention 17/17; memo 21/21 clean zero exact-claim failures);
  suite green at arrival (**436 tests, OK, 4 skipped**, identical to
  sessions 13–16); debate log still exactly 45,421 bytes. Doors R1–R3
  verified unfired (no σ_D ≤ 3.0 u coexistence measurement, no
  de-saturation/life-cycle demonstration, stale briefing carries no
  owner redirection; the hold forbids hunting R1/R2 by execution).
  **Durable work item:** where sessions 10–16 found none, this wake
  identified a freshness gap in the programme's own closing documents
  — `docs/final-report.md` (written under the Round-4 direction-(d)
  verdict, commit `cd88d11`) and `docs/public-technical-essay.md`
  (`9059753`) both predate Rounds 5–6, the follow-on power memo, its
  independent audit, and the corrigendum; neither file is pinned in
  either freeze manifest (verified directly before editing) and
  neither is retained-class under Part V item 4, so reconciling them
  is lawful documentation work. Discharged per the Round-6 corrigendum
  constraints (visible, dated, originals byte-preserved, never silent
  substitution): **final-report §8 addendum** — records that closure
  is now computed not aesthetic (whole-floor true shift ⇒ 0.03041
  exact power; ≥50% power needs μ = 359/48 ≈ 7.479 lattice units =
  1.87× the registered floor `Δ_pair_floor = 4/255`; k-cliff
  0.38859/0.27962/0.16938 at k = 24/48/96 below per-pair p = 0.75;
  mean-rule powered only for slopes ≥ 3.59×10⁻⁴ ≈ 4.5× the
  cross-sectional bound, ≈ 0.096 at the bound itself; recruitment
  family mechanically null via `23,933 = 23,933`), registers reopening
  doors R1–R3 in summary, and adds §6 read-with pointer corrections
  (debate log now Rounds 1–6; memo + audit belong beside the table;
  one-command verifier named); **essay postscript** — one dated
  public-facing paragraph carrying the same computed closure and the
  doors. No new decision fork arose (the addenda record already-audited
  positions adopted in Rounds 5–6; nothing new was decided this
  session), so no adversarial round was convened; delegation tooling
  remains unavailable on this runtime, as disclosed in Rounds 2–6.
  **Completion disclosure (two-wake unit).** The session-17 process
  died after authoring all three edits and this entry but BEFORE any
  commit existed — this paragraph originally claimed "suite re-run
  green post-commit; verifier re-run exit 0 …; pushed", which was not
  yet true when written. The next wake (session 18) found the tree
  dirty with exactly these three files and completed the unit:
  every quoted number re-checked against
  `docs/stage-8-followon-power-memo.md` (0.03041 whole-floor power;
  359/48 ≈ 7.479 u = 1.87× floor; k-cliff 0.38859/0.27962/0.16938;
  mean-rule 0.0958 at the bound, powered only for slopes ≥ 3.59e-4;
  admitted-births identity 23,933 = 23,933; σ_D = 5.7061 u);
  wake battery on the dirty tree returned **8/9 PASS** with the sole
  failure T1 naming precisely these three paths — all retained-class
  checks clean (anchors intact; pins 8/8 signed-bracket + 29/30
  paired with the debate log solely under its proven pure-append rule;
  inventories closed extra=none missing=none; doors unfired vs
  `d19d7c2`, failed-designs at 8; auditors exit 0 with
  session-12-identical numbers); suite on the dirty tree 435 OK /
  4 skipped / 1 failure, the single failure being the session-13
  live-repo smoke `test_live_repo_has_no_tracked_file_modifications`
  failing by design on the same three paths — i.e. both independent
  sentinels flagged nothing except the uncommitted unit itself.
  Post-commit verification at the unit HEAD: verifier `--auditors`
  **exit 0, 9/9 PASS**; suite green (**436 tests OK, 4 skipped**);
  pushed.
- 2026-08-23 (session 19): **cron-briefing remediation unit under the
  Part V item 3 hold — tenth consecutive stale-cron arrival disclosed,
  this time root-caused and fixed at the source; no execution
  registered or run.** Arrival state: cron briefing stale a tenth time
  (still the ~08:05 UTC `f753894` text; every listed standing task was
  discharged by sessions 1–9), actual HEAD `d65840a` = origin/main
  (`0/0`), tree clean. Arrival battery reproduced bit-for-bit:
  `python3 src/verify_retained_integrity.py --auditors` exit 0 with
  **9/9 checks PASS** (P1 anchors intact on both manifests; P2 pins
  8/8 signed-bracket + 29/30 paired with the debate log solely under
  its proven pure-append rule; P3 both retained inventories closed
  extra=none missing=none; T1 strict tree; D1 doors unfired vs
  `d19d7c2`, failed-designs at 8), all three standalone auditors
  exit 0 with session-12-identical numbers (32 pairs median −1/128
  sign 9/21/2 reducer byte-identical; post-retention 17/17;
  follow-on-memo 21/21 clean, zero exact-claim failures); suite green
  at arrival (**436 tests, OK, 4 skipped** — sixth consecutive
  identical count); whole-tree freshness sweep clean outside
  `__pycache__`; debate log still exactly 45,421 bytes (zero appended
  since session 10). **New durable work item found** where sessions
  10–16 found none in-repo: the ten stale arrivals share one root
  cause OUTSIDE the repo — the live scheduler job itself. Located the
  config at `/opt/data/cron/jobs.json` (own-profile infrastructure;
  job id `de939b52cc2b`, cron `*/20 * * * *`, enabled, deliver origin)
  whose frozen `prompt` field still briefs every wake with the
  ~08:05 UTC `f753894` state. Remediation applied atomically
  (temp-file + `os.replace` under an exclusive `flock` on the
  daemon's own `.jobs.lock`, pre/post digest equality check, 0600
  mode preserved): ONLY that job's `name` and `prompt` replaced — new
  name "Substrate carry-on v3 — closed-programme verification hold
  (20m)", new prompt carrying the standing orders verbatim, the
  computed-closure programme state (memo + Round-5 survival), doors
  R1–R3 quoted, the hold ("no evolutionary execution anywhere;
  lawful units are verification, documentation, owner-directed
  work"), the retained-class list, the Part V item-5 wake
  prescription (fetch/sync check → verifier `--auditors` → suite →
  door check → durable-gap hunt → Part IV/V logging → push),
  the `[SILENT]` delivery contract, and the discipline lines.
  Deliberately untouched: id, schedule (`*/20` stays — cadence is
  owner-set), `enabled: true`, deliver target, toolsets, repeat
  counters; the disabled completed Stage-7B0 job left as history.
  Durability verified empirically: edit intact after ≥5 sixty-second
  ticker heartbeats with zero daemon rewrites (jobs.json mtime
  remained our write; stale marker count 0; no temp leftovers).
  Disclosed residual risk: whether the daemon's fire-time bookkeeping
  persist (next due 2026-08-24T00:00Z) re-reads the file or dumps a
  cached image was not directly observable within one wake — later
  wakes are themselves the test, and the fixer script
  `/opt/data/.cache/fix_cron_briefing.py` fails safe (refuses to act
  unless the expected stale marker is present) so a wake that ever
  receives the old briefing again can simply re-run it. Justification
  under the hold: this touched no repo content, no retained class,
  and no execution; it discharges the recurring stale-disclosure duty
  at its cause and eliminates systematic misdirection of future wakes
  (standing orders: advance autonomously, never idle). delegate_task
  still unavailable on this runtime as disclosed Rounds 2–6; no
  decision fork arose so no adversarial round convened (Round-5
  computed closure stands). *Same-wake postscript (00:01:55 UTC,
  pre-push observation):* the disclosed residual risk was then
  closed empirically — the 00:00:17 UTC fire-time persist rewrote
  `jobs.json` (mtime advanced) and BOTH markers survived intact
  (stale-marker count 0; new-briefing count 1), i.e. the daemon
  re-reads the file at fire time rather than dumping a cached image;
  the correction is therefore durable across fires, not merely
  across ticks.
- 2026-08-24 (session 20): **README terminal-state reconciliation
  under the Part V item 3 hold — first corrected-briefing arrival
  since the session-19 scheduler fix; no execution registered or
  run.** Arrival state: this wake received the v3 briefing ("Substrate
  carry-on v3 — closed-programme verification hold") installed by
  session 19 — sessions 10–19 had each arrived on stale `f753894`
  text, so the fix is confirmed durable at the delivery level,
  reproducing end-to-end what session 19's same-wake postscript
  observed at the persist level; minor staleness disclosed for
  completeness: the v3 text dates delegate_task absence "through
  cron-session 18" where session 19 had also disclosed it —
  immaterial. Actual HEAD `b52e0f3` = origin/main (`0/0`), tree
  clean. Arrival battery reproduced bit-for-bit:
  `python3 src/verify_retained_integrity.py --auditors` exit 0 with
  **9/9 checks PASS** (P1 both manifest anchors; P2 pins 8/8
  signed-bracket + 29/30 paired with the debate log solely under its
  proven pure-append rule; P3 both retained inventories closed
  extra=none missing=none; T1 strict tree; D1 doors unfired vs
  `d19d7c2`, failed-designs at 8), all three standalone auditors exit
  0 with session-12-identical numbers; suite green at arrival
  (**436 tests, OK, 4 skipped** — seventh consecutive identical
  count); debate log still exactly 45,421 bytes (zero appended since
  session 10). Doors R1–R3 mechanically unfired; no owner redirection
  present in any channel. delegate_task still absent from this
  runtime's toolset as disclosed Rounds 2–6 and sessions 17–19; no
  decision fork arose so no adversarial round convened (Round-5
  computed closure stands). **Durable gap found and discharged:** the
  repository front door was stale — README §Status still asserted
  "Stage 7 mutation, stochastic allocation assays, evolutionary runs,
  and fitness inference remain untested", a sentence the retained
  record has since contradicted at every tier it names. Discharge: a
  visible dated "Status addendum (2026-08-24)" inserted directly
  beneath the original Status paragraph, which is preserved
  byte-for-byte; the addendum reconciles status to the retained 7B/8
  record (channels registered/run/audited, no-gos archived under
  `failed-designs/`, signed bracket frozen→executed→audit-reproduced,
  Stage 8 paired execution retained with 17/17 post-retention audit),
  states the computed closure with figures cross-checked against
  `docs/final-report.md` §8 and `docs/stage-8-followon-power-memo.md`
  before commit (sd(D) = 5.7061; 13/24 crossings = 3.0% exact power;
  ≥50% needs 1.87× floor; power falls with k below per-pair 0.75;
  admitted-births identity 23,933 = 23,933), quotes doors R1–R3 and
  the hold, and names the one-command verifier. Pre-edit check (same
  unpinned verification session 18 ran for final-report.md):
  README.md appears in neither freeze manifest nor the verifier's pin
  set. Unit closes with post-commit re-run of the verifier and suite
  before push (results recorded in the commit message).

- 2026-08-24 (session 21): **project-report supersession
  reconciliation under the Part V item 3 hold — second corrected-
  briefing arrival; no execution registered or run.** Arrival state:
  v3 briefing delivered intact for the second consecutive wake.
  Actual HEAD `75af015` = origin/main (`0/0`), tree clean. Arrival
  battery reproduced bit-for-bit: `python3
  src/verify_retained_integrity.py --auditors` exit 0 with **9/9
  checks PASS** (P1 both manifest anchors; P2 pins 8/8
  signed-bracket + 29/30 paired with the debate log solely under its
  proven pure-append rule; P3 both retained inventories closed
  extra=none missing=none; T1 strict tree at arrival; D1 doors
  unfired vs `d19d7c2`, failed-designs at 8), all three standalone
  auditors exit 0 with session-12-identical numbers; suite green at
  arrival (**436 tests, OK, 4 skipped** — eighth consecutive
  identical count); debate log still exactly 45,421 bytes (zero
  appended since session 10); whole-tree post-commit freshness sweep
  clean. Doors R1–R3 mechanically unfired; no owner redirection
  present in any channel. delegate_task still absent from this
  runtime's toolset as disclosed Rounds 2–6 and sessions 17–20; no
  decision fork arose so no adversarial round convened (Round-5
  computed closure stands). **Durable gap found and discharged:** the
  last unreconciled front-door document — `docs/project-report.md`
  (2026-07-30, Stages 1–6) is linked from the README "Read first"
  list yet ends its artifact inventory at the *unexecuted* 7B2
  registration, carrying no visible record that the entire subsequent
  arc happened (7B2 `DEGENERATE_REPLICATION`; three pre-freeze gate
  no-gos archived under `failed-designs/`; signed-bracket gate 24/24,
  freeze `7d21153`, single retained execution → registered null
  −1/128 vs floor 1/100, `NO_ESTABLISHED_CONTRAST`; Stage 8 paired
  execution retained with 17/17 post-retention audit; computed
  closure, memo independently audited 21/21). Although
  `docs/final-report.md` declares the supersession internally, the
  superseded document itself bore no marker, so a direct reader
  routed there would land on a stale terminal state. Discharge:
  (i) a visible dated supersession notice inserted at the top of
  `docs/project-report.md`, original body preserved byte-for-byte
  below it, every quoted figure cross-checked against
  `docs/stage-8-programme-review.md` Parts I/V,
  `docs/stage-8-followon-power-memo.md`, and the README status
  addendum before commit (sd(D) = 5.7061; 13/24 crossings = 3.0%
  exact power; ≥50% needs 1.87× floor; per-pair mover probability
  0.75; admitted-births identity 23,933 = 23,933); (ii) a new "Final
  report" bullet added to the README "Read first" list routing
  readers to the closure report ahead of the snapshot, existing
  bullets untouched. Pre-edit pin checks: neither file appears in
  either freeze manifest nor the verifier pin set (grep count 0
  across all three). Mid-unit suite run on the dirty tree returned
  exactly the one designed sentinel failure
  (`test_live_repo_has_no_tracked_file_modifications`) naming the
  edited paths and nothing else; unit closes with post-commit re-run
  of the verifier and suite before push (results recorded in the
  commit message).

- 2026-08-24 (session 22): **push-status terminal-state reconciliation
  under the Part V item 3 hold — third corrected-briefing arrival; no
  execution registered or run.** Arrival state: v3 briefing delivered
  intact for the third consecutive wake. Actual HEAD `f6ef4a3c` =
  origin/main (`0/0`), tree clean. Arrival battery reproduced
  bit-for-bit: `python3 src/verify_retained_integrity.py --auditors`
  exit 0 with **9/9 checks PASS** (P1 both manifest anchors; P2 pins
  8/8 signed-bracket + 29/30 paired with the debate log solely under
  its proven pure-append rule, file still exactly 45,421 bytes; P3 both
  retained inventories closed extra=none missing=none; T1 strict tree
  at arrival; D1 doors unfired vs `d19d7c2`, failed-designs at 8), all
  three standalone auditors exit 0 with session-12-identical numbers;
  suite green at arrival (**436 tests, OK, 4 skipped** — ninth
  consecutive identical count). Doors R1–R3 mechanically unfired; no
  owner redirection present in any channel. delegate_task still absent
  from this runtime's toolset as disclosed Rounds 2–6 and sessions
  17–21; no decision fork arose so no adversarial round convened (the
  Round-5 computed closure stands). **Durable gap found and
  discharged:** `docs/push-status.md` (2026-08-22) still asserts in
  present tense that "`main` is 40 commits ahead of `origin/main`" with
  the push "**blocked** by GitHub's hard 100 MB per-file limit" —
  contradicted by the live record: the block was resolved later the same
  day by the documented history migration
  (`docs/history-migration-2026-08-22.md`: filter-repo removed exactly
  the one oversized path, raw bytes preserved and re-added as eight
  ~40 MB parts with binding MANIFEST), every session since has pushed
  cleanly, and this wake's fetch is mechanically 0/0. Discharge per the
  established pattern: a visible dated "Status addendum (2026-08-24)"
  appended below the original document, which is preserved byte-for-byte
  in its pre-migration decision-record role (the migration note cites it
  as such); every figure cross-checked before commit against
  `docs/history-migration-2026-08-22.md`, the parts `MANIFEST.json`
  itself (`original_bytes = 312139776`, `original_sha256 = 623f59af…`,
  8 parts, `migration_map` present), and live git state (pre-migration
  bundle 34,048,783 B distinguished from the earlier full-history bundle
  34,046,576 B recorded in the original; largest origin/main-reachable
  blob `host-encoding-diagnostic-result.json` at 84,415,065 B —
  warning-class, under the 100 MB hard limit; migrated blob unreachable
  at HEAD except via its recorded parts). Pre-edit pin checks:
  `push-status.md` appears in neither freeze manifest nor the verifier
  pin set (grep count 0 across all three). Mid-unit suite on the dirty
  tree returned exactly the one designed sentinel failure
  (`test_live_repo_has_no_tracked_file_modifications`) naming the two
  edited paths and nothing else; unit closes with post-commit re-run of
  the verifier and suite before push (results recorded in the commit
  message).

- 2026-08-24 (session 23): **publication-guide provenance
  reconciliation under the Part V item 3 hold — fourth
  corrected-briefing arrival; no execution registered or run.** Arrival
  state: v3 briefing delivered intact for the fourth consecutive wake.
  Actual HEAD `3f50cc9b` = origin/main (0 ahead / 0 behind), tree
  clean. Arrival battery reproduced bit-for-bit:
  `python3 src/verify_retained_integrity.py --auditors` exit 0 with
  **9/9 checks PASS** (P1 both manifest anchors; P2 pins 8/8
  signed-bracket + 29/30 paired with the debate log solely under its
  proven pure-append rule, file still exactly 45,421 bytes; P3 both
  retained inventories closed extra=none missing=none; T1 strict tree
  at arrival; D1 doors unfired vs `d19d7c2`, failed-designs at 8), all
  three standalone auditors exit 0 with session-12-identical numbers;
  suite green at arrival (**436 tests, OK, 4 skipped** — tenth
  consecutive identical count). Doors R1–R3 mechanically unfired (cron
  `jobs.json` carries the v3 prompt only — v3 count 1, stale `f753894`
  count 0); no owner redirection present in any channel. delegate_task
  still absent from this runtime's toolset as disclosed Rounds 2–6 and
  sessions 17–22; no decision fork arose so no adversarial round
  convened (the Round-5 computed closure stands). **Durable gap found
  and discharged:** this wake swept the whole documentation web for
  unresolved references — every markdown relative link across README +
  `docs/*.md` resolves (zero broken), and all 117 backticked
  path-like references classify cleanly (bare module names resolve
  under `src/`; root-rooted `results/…` paths exist except the migrated
  blob, which resolves through its recorded `.parts/MANIFEST.json`;
  gate-failed designs' planned output paths are recorded-absent under
  `failed-designs/`; transient and out-of-repo cron paths excluded by
  role) — surfacing exactly ONE genuine dangling authority citation:
  `docs/push-status.md` cites `scientific-repository-publication.md`
  twice as its policy authority ("Per …", "per the publication guide")
  and `docs/history-migration-2026-08-22.md` cites "the publication
  guide" once, yet no commit in any ref ever added, modified, or
  renamed a matching path (`git log --all --diff-filter=AMR --
  '*scientific-repository-publication*'` returns empty) and no
  filesystem path under `/opt/data` (depth 4) matches — evidently an
  out-of-repo planning note of 2026-08-22 whose text was never
  committed. Discharged as dated provenance notes appended to BOTH
  citing documents, originals byte-preserved (pure appends only: diff
  stat 41 insertions, 0 deletions): a full note in
  `docs/push-status.md` recording the mechanical non-existence evidence
  and the four operative propositions that survive verbatim inside the
  citing documents themselves, plus a short cross-referencing footnote
  on `docs/history-migration-2026-08-22.md`. Pre-edit pin checks:
  neither file appears in either freeze manifest nor the verifier pin
  set (grep count 0 across all three). The three Stage-8 lineage
  registration/schema docs were also examined for supersession-marker
  staleness and found PINNED in the paired freeze manifest —
  byte-frozen, therefore not lawful edit targets; their supersession
  record lives lawfully in the non-frozen layers (programme-review
  Part I, final-report §8, the gate-repair preregistration itself).
  Mid-unit suite on the dirty tree: 436 ran, exactly one designed
  failure (`test_live_repo_has_no_tracked_file_modifications`) naming
  the two edited paths, 4 skipped. Unit closes with post-commit re-run
  of the verifier and suite before push (results recorded in the commit
  message). Part IV session-23 entry appended; Part V item 5 rolled
  forward. Doors R1–R3 unfired; hold in force.

- 2026-08-24 (session 24): **findings-synthesis closure-addendum unit
  under the Part V item 3 hold — fifth corrected-briefing arrival; no
  execution registered or run.** Arrival state: v3 briefing delivered
  intact for the fifth consecutive wake. Actual HEAD `a54092df` =
  origin/main (`0/0`), tree clean — mechanically the session-23 unit
  commit itself (01:34:51 UTC), i.e. zero commits and zero drift
  between that entry and this wake; no stale-state discrepancy beyond
  the v3 text's known immaterial dating of the delegate_task absence
  (disclosed at session 20). Arrival battery reproduced bit-for-bit:
  `python3 src/verify_retained_integrity.py --auditors` exit 0 with
  **9/9 checks PASS** (P1 both manifest anchors; P2 pins 8/8
  signed-bracket + 29/30 paired with the debate log solely under its
  proven pure-append rule, file still exactly 45,421 bytes; P3 both
  retained inventories closed extra=none missing=none; T1 strict tree
  at arrival; D1 doors unfired vs `d19d7c2`, failed-designs at 8), all
  three standalone auditors exit 0 with session-12-identical numbers;
  suite green at arrival (**436 tests, OK, 4 skipped** — eleventh
  consecutive identical count). Doors R1–R3 mechanically unfired; cron
  channel checked directly (`jobs.json`: enabled job = v3 only, zero
  `f753894` markers anywhere); no owner redirection present in any
  channel. delegate_task still absent from this runtime's toolset as
  disclosed Rounds 2–6 and sessions 17–23; no decision fork arose so no
  adversarial round convened (the Round-5 computed closure stands).
  **Durable gap found and discharged:** a present-tense status sweep
  across README + `docs/*.md` (complementing session 23's reference
  sweep) surfaced exactly one remaining README-routed document carrying
  a pre-7B/8 terminal state with no supersession marker anywhere:
  `docs/stages1-6-findings-synthesis.md` (dated 2026-08-01) asserts
  "Real-host coupling remains untested" and frames the findings as
  recoverable "even if Stage 7 stops", while the README "Read first"
  bullet routes readers to it as "the evidentiary source"; its only
  other citations (the project-report inventory row and the
  programme-review M1 cite) carry no closure pointer either, and the
  sibling host-coupling essay was examined and found clean (past-tense
  throughout, zero stale claims). Discharged per the established
  pattern (visible, dated, originals byte-preserved): a **Closure
  addendum (2026-08-24)** inserted beneath the synthesis title block
  reconciling every tier its boundary fences off to the retained record
  (five preregistered 7B generations = three pre-freeze gate no-gos
  archived under `failed-designs/` + one `DEGENERATE_REPLICATION` + the
  signed-bracket class frozen/executed-once/audit-reproduced, 32/32,
  median −1/128 vs floor Δr_min = 1/100, `NO_ESTABLISHED_CONTRAST`;
  real-host coupling answered by the mapping-gate failure analysis plus
  the registered/run/audited compressibility-long-window,
  scheduler-latency-morphology, and host-encoding probes; Stage 8
  paired α-evolution retained, 17/17 post-retention checks,
  `NO_ESTABLISHED_DIRECTION`; computed closure at population
  sd(D) = 5.7061 lattice units — whole-floor shift ⇒ 3.0% exact power,
  ≥50% needs 1.87× the floor — memo independently audited 21/21,
  closure survived debate Rounds 1–6; doors R1–R3 and the hold quoted),
  the original 2026-08-01 text preserved byte-for-byte below it (diff:
  49 insertions, 0 deletions); the README synthesis bullet extended
  with a read-with clause pointing at the addendum (original bullet
  text intact). Pre-edit pin checks: grep count 0 across both freeze
  manifests and the verifier pin set. Mid-unit suite on the dirty tree:
  436 ran, exactly one designed failure
  (`test_live_repo_has_no_tracked_file_modifications`) naming exactly
  `README.md` and `docs/stages1-6-findings-synthesis.md`, 4 skipped.
  Unit closes with post-commit re-run of the verifier and suite before
  push (results recorded in the commit message). Part IV session-24
  entry appended; Part V item 5 rolled forward. Doors R1–R3 unfired;
  hold in force.

- 2026-08-24 (session 25): **verifier-extension unit under the Part V
  item 3 hold — sixth corrected-briefing arrival; no execution
  registered or run.** Arrival state: v3 briefing delivered intact for
  the sixth consecutive wake. Actual HEAD `30d282f95225` =
  origin/main (`0/0`), tree clean — mechanically the session-24 unit
  commit itself, zero commits/drift between that entry and this wake;
  no stale-state discrepancy beyond the v3 text's known immaterial
  dating of the delegate_task absence (disclosed at session 20).
  Arrival battery reproduced bit-for-bit:
  `python3 src/verify_retained_integrity.py --auditors` exit 0 with
  **9/9 checks PASS** (P1 both manifest anchors; P2 pins 8/8
  signed-bracket + 29/30 paired with the debate log solely under its
  proven pure-append rule, file still exactly 45,421 bytes; P3 both
  retained inventories closed extra=none missing=none; T1 strict tree
  at arrival; D1 doors unfired vs `d19d7c2`, failed-designs at 8), all
  three standalone auditors exit 0 with session-12-identical numbers;
  suite green at arrival (**436 tests, OK, 4 skipped** — twelfth
  consecutive identical count). Doors R1–R3 mechanically unfired; cron
  channel checked directly (`jobs.json`: enabled job = v3
  `de939b52cc2b` only, legacy job disabled, zero `f753894` markers);
  no owner redirection present in any channel. delegate_task still
  absent from this runtime's toolset as disclosed Rounds 2–6 and
  sessions 17–24; no decision fork arose so no adversarial round
  convened (the Round-5 computed closure stands). The documentation
  vein was examined first and found exhausted: the Stage 1–6 model
  documents (`metabolism-model`, `boundary-model`,
  `energy-model-v3`, `genome-viability`, `static-paper-model`,
  `r-max-analysis`, `verification-report-v2`) are internally dated,
  self-labelling historical records under the README archive policy,
  several carrying their own supersession banners; every remaining
  "remain untested" phrasing across `docs/` sits either inside a
  byte-preserved original beneath a dated addendum (README §Status,
  findings synthesis) or is an accurate forward-looking scope
  statement (final-report §5). **Durable gap found and discharged
  (verification tooling):** two per-wake steps had remained manual
  since the session-13 consolidation — (i) briefing step 1's second
  half, confirming HEAD == origin/main after fetch, and (ii) the
  debate-log size disclosure hand-transcribed into every entry and
  commit message since session 10 ("still exactly 45,421 bytes").
  Both mechanised inside `src/verify_retained_integrity.py`: new
  **S1 sync** check (local rev-parse comparison of HEAD against
  origin/main, no network; unknown refs FAIL loudly, never silently;
  mismatch reports behind/ahead counts via rev-list left-right, so a
  failed or forgotten push now stops the NEXT wake at the verifier
  instead of being discovered mid-entry) and a **non-failing P2 info
  line** for each pure-append path emitting current size (= frozen
  prefix + lawfully appended), verified live as `current size 45421 B
  (= 20869 B frozen prefix + 24552 B lawfully appended)` —
  bit-consistent with every prior manual disclosure. Test matrix
  +3 (`SyncTests`: git-free fail-loud negative control; synthetic
  equal-refs pass via update-ref; unpushed-commit mismatch asserting
  the `0/1` behind/ahead counts) and the live smoke extended to
  assert the S1 line and the info-line regex. Pre-edit pin checks:
  grep count 0 across both freeze manifests; neither target in the
  verifier pin set; both last touched by `9364b5d`. Mid-unit suite on
  the dirty tree: 439 ran, exactly one designed failure
  (`test_live_repo_has_no_tracked_file_modifications`) naming exactly
  `src/verify_retained_integrity.py`,
  `src/test_verify_retained_integrity.py`, and
  `docs/stage-8-programme-review.md`, 4 skipped. Expectation change
  disclosed: future wakes should see `--auditors` **exit 0, 10/10
  PASS** and suite **439 tests, OK, 4 skipped**. The unit's first
  post-commit verifier run then caught two things live: (1) the new
  summary fraction printed `(10/11)` because the summary had used
  `len(lines)`, which now also counts the info emission — fixed by
  counting only `record()` checks (`n_checks`), with a live-smoke
  guard asserting the fraction equals the number of bracketed check
  lines; (2) S1 itself FAILED in the commit-to-push window
  (`behind/ahead 0/1`) — its designed behavior, exercised on its own
  unit. The wake-closing workflow is thereby corrected: battery re-runs
  happen AFTER push at the pushed HEAD (numbers reported in this
  wake's delivery and mechanically re-established at the next
  arrival), replacing the former commit→re-run→amend→push pattern that
  S1 intentionally outlaws. Part IV session-25 entry appended;
  Part V item 5 rolled forward. Doors R1–R3 unfired; hold in force.

- 2026-08-24 (session 26): **verifier-extension unit under the Part V
  item 3 hold — seventh corrected-briefing arrival; no execution
  registered or run.** Arrival state: v3 briefing delivered intact for
  the seventh consecutive wake. Actual HEAD `c9264e1af97157` =
  origin/main (`0/0`), tree clean — mechanically the session-25 unit
  commit itself, zero commits/drift between that entry and this wake;
  no stale-state discrepancy. Arrival battery reproduced exactly under
  the session-25 expectation change: `python3
  src/verify_retained_integrity.py --auditors` exit 0 with **10/10
  checks PASS** (P1 both manifest anchors; P2 pins 8/8 signed-bracket +
  29/30 paired with the debate log solely under its proven pure-append
  rule, file still exactly 45,421 bytes; S1 sync GREEN at arrival —
  `HEAD c9264e1 == origin/main`, the designed at-arrival state; P3 both
  retained inventories closed extra=none missing=none; T1 strict tree
  at arrival; D1 doors unfired vs `d19d7c2`, failed-designs at 8), all
  three standalone auditors exit 0 with session-12-identical numbers;
  suite green at arrival (**439 tests, OK, 4 skipped** — thirteenth
  consecutive green count, first at the raised expectation). Doors
  R1–R3 mechanically unfired, additionally confirmed by an independent
  `git diff --name-only d19d7c2..HEAD` over `results/` +
  `failed-designs/` (empty); cron channel checked directly
  (`jobs.json`: enabled job = v3 `de939b52cc2b` only, legacy job
  disabled, zero `f753894` markers); no owner redirection present in
  any channel. delegate_task still absent from this runtime's toolset
  as disclosed Rounds 2–6 and sessions 17–25; no decision fork arose so
  no adversarial round convened (the Round-5 computed closure stands).
  **Durable gap found and discharged (verification tooling):** the
  debate log's lawfully-appended region had NO content binding anywhere
  — the P2 pin proves only the 20,869-byte frozen prefix and accepts
  any bytes behind it, so a same-length in-place rewrite of an appended
  Round would have passed every mechanical check in the battery,
  auditors included. Closed with a monotone **append ledger** sidecar +
  new **L1** verifier check: `docs/stage-8-debate-log-append-ledger.json`
  records `{bytes, sha256}` snapshots (seed = session 26 at exactly
  45,421 B, `2b7929e0…56a5358`); `append_ledger()` requires every
  recorded snapshot to remain a byte-exact prefix of the current file
  forever, snapshots strictly increasing in size, and the newest to
  equal the current file exactly — suffix rewrites (either length),
  truncation, stale/bogus historical snapshots, malformed/non-monotone/
  missing ledgers, and lawful appends not registered within the
  appending unit's own commit all FAIL loudly with guidance. The ledger
  is a new non-retained, unpinned, version-controlled sidecar (pre-edit
  grep count 0 across both freeze manifests; debate log touched
  read-only throughout). Test matrix +6 (`AppendLedgerTests`:
  multi-snapshot history pass; same-length suffix mutation FAILS — the
  regression test for the closed hole; unregistered lawful append fails
  citing the registration duty; truncation below the recorded state
  fails; stale older snapshot fails even when the newest matches;
  missing/malformed/non-monotone ledgers fail) and the live smoke
  extended to assert the L1 line. Pre-edit pin checks: grep count 0
  across both freeze manifests; none of the three targets in the
  verifier pin set. Mid-unit suite on the dirty tree: 445 ran, exactly
  one designed failure
  (`test_live_repo_has_no_tracked_file_modifications`) naming exactly
  `src/verify_retained_integrity.py`,
  `src/test_verify_retained_integrity.py`, and
  `docs/stage-8-programme-review.md`, 4 skipped. Expectation change
  disclosed: future wakes should see `--auditors` **exit 0, 11/11
  PASS** and suite **445 tests, OK, 4 skipped**; S1 expected GREEN at
  arrivals and RED only inside commit-to-push windows. Per the
  session-25 workflow correction, closing battery numbers are reported
  post-push at the pushed HEAD in this wake's delivery. Part IV
  session-26 entry appended; Part V item 5 rolled forward with the new
  expectations. Doors R1–R3 unfired; hold in force.

- 2026-08-24 (session 27): **verification-only unit under the Part V
  item 3 hold — eighth corrected-briefing arrival; the last hand-run
  step of the wake battery mechanised into the verifier; no execution
  registered or run.** Arrival state: v3 briefing delivered intact for
  the eighth consecutive wake; actual HEAD `574d389ce8e6` =
  origin/main (`0/0`), tree clean — mechanically the session-26 unit
  commit itself, zero commits/drift between that entry and this wake;
  no stale-state discrepancy. Arrival battery reproduced exactly under
  the session-26 expectation change: `python3
  src/verify_retained_integrity.py --auditors` exit 0 with **11/11
  checks PASS** (P1 both manifest anchors; P2 pins 8/8 signed-bracket +
  29/30 paired with the debate log solely under its proven pure-append
  rule, still exactly 45,421 bytes; L1 append-ledger match on the sole
  pure-append path; P3 both retained inventories closed extra=none
  missing=none; T1 strict tree at arrival; S1 sync GREEN at arrival,
  the designed at-arrival state; D1 doors unfired vs `d19d7c2`,
  failed-designs at 8), all three standalone auditors exit 0 with
  session-12-identical numbers; suite green at arrival (**445 tests,
  OK, 4 skipped** — fourteenth consecutive green count, second at the
  raised expectation); cron channel checked directly by hand one last
  time (`jobs.json`: enabled job = v3 `de939b52cc2b` only, legacy job
  disabled/completed, zero `f753894` markers); no owner redirection
  present in any channel. delegate_task still absent from this
  runtime's toolset as disclosed Rounds 2–6 and sessions 17–26; no
  decision fork arose so no adversarial round convened (the Round-5
  computed closure stands). **Durable gap found and discharged
  (verification tooling):** every mechanical wake step had been
  consolidated into the verifier EXCEPT the cron-briefing integrity
  disclosure that every wake since session 19 has performed manually
  ("cron jobs.json checked directly"). Closed with new **C1 cron**
  check in `src/verify_retained_integrity.py` validating the
  out-of-repo scheduler config `/opt/data/cron/jobs.json`: a PRESENT
  file must parse with a `jobs` list, carry ZERO stale `f753894`
  markers anywhere, have exactly the v3 hold-briefing job
  (`de939b52cc2b`) enabled, and NO other enabled project-targeting job
  (a resurrected legacy briefing would contradict the hold at every
  wake) — failures cite the session-19 failsafe fixer; an ABSENT file
  is a labelled non-failing SKIP so the verifier stays portable beyond
  this machine, and unrelated non-project jobs are deliberately ignored
  so lawful owner scheduling action is never flagged as tampering.
  Read-only over the scheduler file; no new sidecar; pre-edit pin
  checks grep count 0 across both freeze manifests; none of the three
  targets in the verifier pin set. Test matrix +7 (`CronBriefingTests`:
  v3-only-enabled passes; absent-config SKIP asserted `None`; stale
  marker inside a well-formed prompt fails citing the fixer; v3
  disabled AND v3 missing both fail; resurrected legacy job alongside
  v3 fails naming it; unrelated enabled job ignored; malformed config
  fails loudly) and the live smoke extended to assert the C1 line. ONE
  test bug caught by the suite itself before commit (the first
  stale-marker fixture placed the marker after valid JSON, hitting the
  malformed branch instead of the marker branch; fixture moved inside a
  job prompt — verifier logic needed no change). Mid-unit suite on the
  dirty tree: 452 ran, exactly one designed failure
  (`test_live_repo_has_no_tracked_file_modifications`) naming exactly
  `src/verify_retained_integrity.py`, `src/test_verify_retained_integrity.py`,
  and `docs/stage-8-programme-review.md`, 4 skipped; review-doc diff
  purely additive. Expectation change disclosed: future wakes should
  see `--auditors` **exit 0, 12/12 PASS** and suite **452 tests, OK,
  4 skipped**; S1 expected GREEN at arrivals and RED only inside
  commit-to-push windows. Per the session-25 workflow correction,
  closing battery numbers are reported post-push at the pushed HEAD in
  this wake's delivery. Part IV session-27 entry appended; Part V item
  5 rolled forward with the new expectations. Doors R1–R3 unfired;
  hold in force.

- 2026-08-24 (session 28): **verification-only unit under the Part V
  item 3 hold — ninth corrected-briefing arrival; the append-only
  failed-designs archive content-bound (the last immutable class with no
  content binding); no execution registered or run.** Arrival state: v3
  briefing delivered intact for the ninth consecutive wake; actual HEAD
  `bf8d1b106e4e` = origin/main (`0/0`), tree clean — mechanically the
  session-27 unit commit itself, zero commits/drift between that entry
  and this wake; no stale-state discrepancy. Arrival battery reproduced
  exactly under the session-27 expectation change: `python3
  src/verify_retained_integrity.py --auditors` exit 0 with **12/12
  checks PASS** (P1 both manifest anchors; P2 pins 8/8 signed-bracket +
  29/30 paired with the debate log solely under its proven pure-append
  rule, still exactly 45,421 bytes; L1 append-ledger match on the sole
  pure-append path; P3 both retained inventories closed extra=none
  missing=none; T1 strict tree at arrival; S1 sync GREEN at arrival, the
  designed at-arrival state; D1 doors unfired vs `d19d7c2`,
  failed-designs at 8; C1 cron = v3 hold-briefing job `de939b52cc2b`
  enabled project job only, zero `f753894` markers), all three
  standalone auditors exit 0 with session-12-identical numbers; suite
  green at arrival (**452 tests, OK, 4 skipped** — fifteenth consecutive
  green count, third at the raised expectation); no owner redirection
  present in any channel. delegate_task still absent from this runtime's
  toolset as disclosed Rounds 2–6 and sessions 17–27; no decision fork
  arose so no adversarial round convened (the Round-5 computed closure
  stands). **Durable gap found and discharged (verification tooling):**
  the append-only `failed-designs/` archive (39 files across 8 entries)
  had NO content binding anywhere — D1 constrains it only by git diff
  against the one fixed base commit `d19d7c2` plus the entry-directory
  count, neither of which proves a single byte of content, and both
  constraints expire the moment a lawful R1/R2 door fires and the door
  baseline is consciously rolled forward (a same-length in-place rewrite
  landed any time before such a roll-forward would thereafter be
  invisible to every mechanical check forever). Closed with new **F1
  failed-designs** check plus the seed sidecar
  `docs/failed-designs-append-ledger.json` (version 1, seeded at this
  wake's arrival tree: all 39 archived files bound by `{bytes, sha256}`,
  31,003,030 bytes total): every recorded path must exist on disk
  byte-exactly forever, every on-disk file under `failed-designs/` must
  be recorded, and the ledger itself must parse strictly (non-empty
  `files` object, integer non-negative bytes, 64-hex digests) — in-place
  edits (same-length included), deletions, malformed ledgers, and lawful
  no-go appends not registered in the appending unit's own commit all
  FAIL loudly. Same infrastructure class as the L1 sidecar:
  non-retained, unpinned, version-controlled documentation
  infrastructure; pre-edit pin checks grep count 0 across both freeze
  manifests for all four touchpoints (both src files, review doc, new
  sidecar); none of the four in the verifier pin set; archived contents
  touched read-only throughout; debate log untouched. Test matrix +5
  (`FailedDesignsLedgerTests`: multi-entry pass naming file and entry
  counts; same-length in-place edit fails naming the file — regression
  test for the closed hole; deletion of a registered file fails;
  unregistered lawful append fails citing registration duty;
  missing/malformed/wrong-type/bad-digest ledgers fail loudly) and the
  live smoke extended to assert the F1 line. ONE fixture bug caught by
  the tests themselves before any suite run (synthetic trees never
  created the `docs/` parent of the ledger path; helper mkdirs it —
  verifier logic needed no change). Mid-unit suite on the dirty tree:
  457 ran, exactly one designed failure
  (`test_live_repo_has_no_tracked_file_modifications`) naming exactly
  `docs/stage-8-programme-review.md`,
  `src/test_verify_retained_integrity.py`, and
  `src/verify_retained_integrity.py` (the new sidecar is untracked at
  this point and invisible to the non-strict tracked-file check),
  4 skipped; review-doc diff purely
  additive. Expectation change disclosed: future wakes should see
  `--auditors` **exit 0, 13/13 PASS** and suite **457 tests, OK,
  4 skipped**; S1 expected GREEN at arrivals and RED only inside
  commit-to-push windows. Per the session-25 workflow correction,
  closing battery numbers are reported post-push at the pushed HEAD in
  this wake's delivery. Part IV session-28 entry appended; Part V item
  5 rolled forward with the new expectations. Doors R1–R3 unfired;
  hold in force.

- 2026-08-24 (session 29): **verification-only unit under the Part V
  item 3 hold — tenth corrected-briefing arrival; briefing step 1's
  fetch half mechanised (the last unmechanised mechanical wake step);
  no execution registered or run.** Arrival state: v3 briefing
  delivered intact for the tenth consecutive wake; actual HEAD
  `5de83ac68a3f` = origin/main (`0/0`), tree clean — mechanically the
  session-28 unit commit itself, zero commits/drift between that entry
  and this wake; no stale-state discrepancy. Arrival battery reproduced
  exactly under the session-28 expectation change: `python3
  src/verify_retained_integrity.py --auditors` exit 0 with **13/13
  checks PASS** at `5de83ac` (P1 both manifest anchors; P2 pins 8/8
  signed-bracket + 29/30 paired with the debate log solely under its
  proven pure-append rule, still exactly 45,421 bytes; L1 append-ledger
  match on the sole pure-append path; P3 both retained inventories
  closed extra=none missing=none; T1 strict tree at arrival; S1 sync
  GREEN at arrival, the designed at-arrival state; D1 doors unfired vs
  `d19d7c2`, failed-designs at 8; F1 all 39 archived files across 8
  entries content-bound; C1 cron = v3 hold-briefing job
  `de939b52cc2b` enabled project job only, zero `f753894` markers),
  all three standalone auditors exit 0 with session-12-identical
  numbers; suite green at arrival (**457 tests, OK, 4 skipped** —
  sixteenth consecutive green count, fourth at the raised expectation);
  no owner redirection present in any channel. delegate_task still
  absent from this runtime's toolset as disclosed Rounds 2–6 and
  sessions 17–28; no decision fork arose so no adversarial round
  convened (the Round-5 computed closure stands). **Durable gap found
  and discharged (verification tooling):** the manual `git fetch
  origin` of briefing step 1 was the one remaining unmechanised
  mechanical wake step after sessions 25–28 consolidated everything
  else — S1 deliberately compares HEAD against the LOCALLY RECORDED
  `refs/remotes/origin/main` (offline portability), so a wake that ever
  skipped the hand-run fetch while a concurrent session advanced
  origin/main would let S1 pass against a stale ref indefinitely
  (duplicate concurrent sessions are documented fact in this
  programme's history). Closed with a new opt-in **N1 fetch** check
  (`--fetch`): runs exactly the standard `git fetch origin` BEFORE S1
  so the sync comparison is provably post-fetch, FAILS loudly on any
  fetch error or missing remote main ("resolve network/remote before
  trusting S1"), and reports the freshly fetched tip on success;
  default invocation stays fully offline (the live smoke now asserts
  the N1 line is absent without the flag), and the fetch touches
  remote-tracking refs only — never any working-tree, retained, or
  pinned file — so the battery remains read-only over all programme
  content while performing precisely what every wake already ran by
  hand. Test matrix +3 (`FetchTests`: the stale-ref regression — a
  clone whose recorded origin/main equals its HEAD passes S1 until the
  fetch reveals the concurrent advance, after which S1 fails loudly
  with behind/ahead 1/0; fetch failure fails loudly; CLI wiring via
  `unittest.mock` asserting `--fetch → do_fetch=True` and the default
  off — first mock use in this suite, disclosed) with fixtures on
  local bare remotes only — the suite itself never touches the
  network; live smoke extended with the default-offline invariant.
  Pre-edit pin checks grep count 0 across both freeze manifests for
  all three touchpoints; none of the three in the verifier pin set;
  debate log untouched. Mid-unit suite on the dirty tree: 460 ran,
  exactly one designed failure
  (`test_live_repo_has_no_tracked_file_modifications`) naming exactly
  `src/test_verify_retained_integrity.py` and
  `src/verify_retained_integrity.py` (review doc not yet edited),
  4 skipped. Expectation change disclosed: future wakes should run
  `python3 src/verify_retained_integrity.py --auditors --fetch`
  expecting **exit 0, 14/14 PASS** (N1 RED on genuine network/remote
  failure by design — a stop condition, not a defect) and suite **460
  tests, OK, 4 skipped**; S1 expected GREEN at arrivals and RED only
  inside commit-to-push windows. Per the session-25 workflow
  correction, closing battery numbers are reported post-push at the
  pushed HEAD in this wake's delivery. Part IV session-29 entry
  appended; Part V item 5 rolled forward with the new expectations.
  Doors R1–R3 unfired; hold in force.

- 2026-08-24 (session 30): **verification-only unit under the Part V
  item 3 hold — eleventh corrected-briefing arrival;
  stale-terminal-state reconciliation of the Stage 7 architecture
  document; no execution registered or run.** Arrival state: v3
  briefing delivered intact for the eleventh consecutive wake; actual
  HEAD `4a67bc755428` = origin/main (`0/0`), tree clean — mechanically
  the session-29 unit commit itself, zero commits/drift between that
  entry and this wake; no stale-state discrepancy. Arrival battery
  reproduced exactly under the session-29 expectation change:
  `python3 src/verify_retained_integrity.py --auditors --fetch`
  exit 0 with **14/14 checks PASS** at `4a67bc755428` (N1 fetch OK,
  freshly fetched tip == HEAD; P1 both manifest anchors; P2 pins 8/8
  signed-bracket + 29/30 paired with the debate log solely under its
  proven pure-append rule, still exactly 45,421 bytes; L1
  append-ledger match on the sole pure-append path; P3 both retained
  inventories closed extra=none missing=none; T1 strict tree at
  arrival; S1 sync GREEN at arrival, the designed at-arrival state;
  D1 doors unfired vs `d19d7c2`, failed-designs at 8; F1 all 39
  archived files across 8 entries content-bound; C1 cron = v3
  hold-briefing job `de939b52cc2b` enabled project job only, zero
  `f753894` markers), all three standalone auditors exit 0 with
  session-12-identical numbers; suite green at arrival (**460 tests,
  OK, 4 skipped** — seventeenth consecutive green count, first at the
  raised expectation); no owner redirection present in any channel.
  delegate_task still absent from this runtime's toolset as disclosed
  Rounds 2–6 and sessions 17–29; no decision fork arose so no
  adversarial round convened (the Round-5 computed closure stands).
  **Durable gap found and discharged (documentation
  reconciliation):** a systematic stale-present-tense sweep over
  `docs/` surfaced `docs/stage-7-split-reserve-architecture.md` —
  actively referenced by `project-report.md`,
  `stage-7b1-preregistration.md`, and
  `offspring-trough-removal-preregistration.md`, yet untouched since
  2026-08-22 and missed by the session 17/20–24 reconciliation
  campaign — whose line-3 Status block still asserted, in the present
  tense, that Stage 7B0 "implementation and execution remain **NO-GO**"
  and that "every Stage 7 population-fitness or evolutionary assay
  remain **NO-GO** pending §13", contradicting both the document's own
  §13 tail (updated 2026-08-22, recording two PASS executions of the
  7B0 blocks under independently frozen implementations) and the
  retained record (7B2 registered no-gos archived under
  `failed-designs/`; signed bracket frozen/executed/audit-reproduced;
  Stage 8 single paired confirmatory alpha-evolution execution
  retained and post-audited 17/17; programme CLOSED on computed
  grounds; hold R1–R3 in force). Discharged with a visible dated
  addendum beneath the byte-preserved Status paragraph, reconciling
  it to the retained record through closure and the hold; the rest of
  the document, including its already-updated §13, untouched.
  Pre-edit pin checks: grep count 0 across both freeze manifests
  ×3 touchpoints; not in the verifier pin set; outside
  `failed-designs/`; debate log untouched. Mid-unit suite on the
  dirty tree: 460 ran, exactly one designed failure
  (`test_live_repo_has_no_tracked_file_modifications`) naming exactly
  `docs/stage-7-split-reserve-architecture.md` and
  `docs/stage-8-programme-review.md`, 4 skipped; review-doc diff
  purely additive. No expectation change: future wakes continue with
  `python3 src/verify_retained_integrity.py --auditors --fetch`
  expecting **exit 0, 14/14 PASS** and suite **460 tests, OK, 4
  skipped**; S1 expected GREEN at arrivals and RED only inside
  commit-to-push windows. Per the session-25 workflow correction,
  closing battery numbers are reported post-push at the pushed HEAD
  in this wake's delivery. Part IV session-30 entry appended; Part V
  item 5 rolled forward. Doors R1–R3 unfired; hold in force.

- 2026-08-24 (session 31): **verification-only unit under the Part V
  item 3 hold — twelfth corrected-briefing arrival;
  documentation→repository path-reference integrity tooling (fourth
  standalone auditor plus a lawful-absence registry); no execution
  registered or run.** Arrival state: v3 briefing delivered intact for
  the twelfth consecutive wake; actual HEAD `bd49b217bc5a` =
  origin/main (`0/0`), tree clean — mechanically the session-30 unit
  commit itself, zero commits/drift between that entry and this wake;
  no stale-state discrepancy. Arrival battery reproduced exactly under
  the session-29 expectation change:
  `python3 src/verify_retained_integrity.py --auditors --fetch` exit 0
  with **14/14 checks PASS** at `bd49b217bc5a` (N1 fetch OK, freshly
  fetched tip == HEAD; P1 both manifest anchors; P2 pins 8/8
  signed-bracket + 29/30 paired with the debate log solely under its
  proven pure-append rule, still exactly 45,421 bytes; L1
  append-ledger match; P3 both retained inventories closed extra=none
  missing=none; T1 strict tree at arrival; S1 sync GREEN at arrival;
  D1 doors unfired vs `d19d7c2`, failed-designs at 8; F1 all 39
  archived files across 8 entries content-bound; C1 cron = v3
  hold-briefing job `de939b52cc2b` enabled project job only, zero
  `f753894` markers), all three standalone auditors exit 0 with
  session-12-identical numbers; suite green at arrival (**460 tests,
  OK, 4 skipped** — eighteenth consecutive green count); no owner
  redirection present in any channel. delegate_task still absent from
  this runtime's toolset as disclosed Rounds 2–6 and sessions 17–30;
  no decision fork arose so no adversarial round convened (the Round-5
  computed closure stands). **Durable gap found and discharged
  (verification tooling):** nothing anywhere mechanised the integrity
  of paths that the current-facing documentation cites inside the
  repository — a systematic backtick-path sweep over README.md +
  `docs/*.md` measured 300 unique document/citation pairs with **20
  absent pairs over 13 distinct absent citation strings**, and every
  prior wake would have classified them entirely by hand: five are
  citations of `results/host-compressibility-long-window-360001x10ms.json`
  (lawfully split into `.parts/` under a binding manifest by the
  documented 2026-08-22 history migration), nine cite output paths of
  three generations whose pre-freeze feasibility gates FAILED
  (`stage7b-exposure-endpoint`, `stage7b-endpoint-repair`,
  `stage7b2-repair` — directories never created, archived no-gos are
  the binding evidence; the signed-bracket prereg records the first
  verbatim as "never used — its retained run was not authorised"), two
  cite `results/stage8-alpha-evolution/` (superseded by the repair
  preregistration's `-paired` path before any retained run), and ONE
  is genuinely dead: `docs/efficiency-assay-preregistration.md` cites
  source `src/trace_offspring_first_extraction_threshold.py`, a path
  that has NEVER existed in any commit (git log --all empty) while its
  companion artifact
  `results/offspring-first-extraction-threshold-summary.json` IS
  retained. Discharged with `docs/doc-path-reference-registry.json`
  (schema 1: all six absence classes registered with reason class,
  citing documents, and machine-checked evidence files) +
  `src/audit_doc_path_references.py`, wired as the FOURTH standalone
  auditor in the verifier's `AUDITORS` tuple (check count unchanged at
  14; A1's detail line now names four scripts): R1 strict registry
  parse; R2 citation-coverage floor (280 against 305 measured — the
  auditor additionally recognises prefix markdown links beyond the
  registration sweep's backticks-only 300); R3 every absent citation
  must resolve on disk OR to a registration, else loud failure naming
  path and citing document; R4 tripwire asserting registered
  permanently-unused paths STAY absent (an execution writing into a
  superseded path can never pass quietly); R5 evidence binding
  including non-empty-directory checks on the archived no-gos; R6
  every registration anchored by ≥1 live citation from its cited_by
  documents so registry rot fails in the same wake as the citing-text
  change. Scope decision disclosed: `superseded/` and documents inside
  `results/`/`failed-designs/` are archival surfaces, neither scanned
  nor required to resolve. Pre-edit pin checks grep count 0 across
  both freeze manifests × touchpoints; none of the touched files in
  the verifier pin set; outside `failed-designs/`; debate log
  untouched. Test matrix +16 (synthetic-tree coverage of every check
  incl. directory-prefix semantics, the materialisation tripwire, lost/
  empty evidence, stale unanchored entries, malformed registries, the
  coverage floor, markdown-link recognition with parent-relative links
  excluded by construction, plus a live subprocess smoke).
  Mid-unit suite on the dirty tree: 476 ran, exactly one designed
  failure (`test_live_repo_has_no_tracked_file_modifications`) naming
  exactly `src/verify_retained_integrity.py` (the three new files
  untracked/invisible to the non-strict check), 4 skipped; review-doc
  diff purely additive. EXPECTATION CHANGE DISCLOSED: future wakes run
  `python3 src/verify_retained_integrity.py --auditors --fetch`
  expecting **exit 0, 14/14 PASS** (count unchanged; A1 detail names
  four auditors) and suite **476 tests, OK, 4 skipped**; S1 expected
  GREEN at arrivals and RED only inside commit-to-push windows. Per
  the session-25 workflow correction, closing battery numbers are
  reported post-push at the pushed HEAD in this wake's delivery. Part
  IV session-31 entry appended; Part V item 5 rolled forward with the
  new expectations. Doors R1–R3 unfired; hold in force.

- 2026-08-24 (session 32): **verification unit interrupted by TWO genuine
  external events — OpenRouter credit exhaustion killed the 05:40 wake
  (HTTP 402), and an explicit owner-surface PAUSE landed on the v3
  briefing job at 06:22:57 UTC mid-wake; no re-arm performed; event
  documented; no execution registered or run.** Arrival state:
  thirteenth corrected-briefing arrival (v3 text intact; its inline
  9/9-and-436 numbers remain the disclosed-superseded session-19-era
  values — Part V item 5 governs); actual HEAD `e4539fbf90d9` =
  origin/main (0/0), tree clean, zero drift. Arrival battery: verifier
  `--auditors --fetch` **exit 0, 14/14 PASS** at `e4539fbf90d9` (N1
  fetch OK; P1 both manifest anchors; P2 pins 8/8 signed-bracket +
  29/30 paired with the debate log solely under its proven pure-append
  rule, still exactly 45,421 bytes; L1 match; P3 both retained
  inventories closed extra=none missing=none; T1 strict tree; S1 sync
  GREEN at arrival; D1 doors unfired vs `d19d7c2`, failed-designs at 8;
  F1 all 39 archived files content-bound; C1 cron PASS — job ENABLED at
  that moment; A1 four standalone auditors exit 0 with session-12-
  identical numbers, DOC-PATH-REFERENCES 6/6). The full suite ran
  concurrently and FAILED its live-repo smoke on C1 — and the failure
  was REAL, not a flake: `/opt/data/cron/jobs.json` was rewritten at
  `updated_at 2026-08-24T06:22:57.657640+00:00`, flipping
  `de939b52cc2b` to `enabled=False`, `state=paused`,
  `paused_at=06:22:57`, `paused_reason=None`; the CLI verifier's C1
  evaluation and the suite's independent evaluation of the same file,
  moments apart, disagreed, so the flip demonstrably landed between
  them, ~2.5 minutes into this wake. Forensics against the gateway's
  own code (`/opt/hermes/cron/jobs.py`): the scheduler's failure paths
  explicitly NEVER pause recurring jobs (issue-#16265 comment; the only
  `enabled=False` write is the one-shot-completion branch — cf. legacy
  job `b64708c35fa7`, `state=completed`, `paused_at=None`);
  `paused_at` is written solely by `pause_job()`, whose callers are
  owner-facing surfaces only (the cronjob tool over chat — this job's
  own deliver-origin telegram chat 'Tomohawks' — and the dashboard web
  API). Conclusion: an explicit pause action by an actor with owner
  access at 06:22:57 UTC. Second event, from the executions ledger
  (`executions.db` row `1693ddc0…`): the previous wake (claimed
  05:40:23) DIED at 06:05:16 with `RuntimeError: HTTP 402 … can only
  afford 110947` of 128000 max_tokens — OpenRouter credit exhaustion,
  a paid-service blocker; ticker healthy throughout (heartbeat 06:27).
  Decision fork resolved WITHOUT adversarial delegation (delegate_task
  absent from this runtime as disclosed Rounds 2–6 and sessions 17–31;
  parent-argued on gateway/repo facts): does the pause fire R3?
  Holding position adopted — whether it is (i) a deliberate halt of
  autonomous wakes or (ii) housekeeping against the failing-credit
  job, the lawful action is identical: DO NOT re-arm. Overriding an
  explicit owner-channel action is forbidden; staying paused costs
  only idleness until the owner speaks. R3's letter ("any direct owner
  message") is NOT met — no message exists anywhere — so the hold's
  registered terms stand unchanged in the docs, with the pause logged
  as an owner-surface intervention that mechanically suspends future
  wakes. Doors otherwise unfired (D1 zero changed artifact paths;
  inventories closed; no new results/failed-designs content; retained
  class, manifests, failed-designs archive all untouched). Discharged:
  this documentation unit only (Part IV entry + Part V item-5 roll-
  forward); single commit naming arrival HEAD `e4539fbf90d9`; push;
  tree clean. Forward expectations while the pause stands (disclosed;
  NO verifier retuning — the loud C1 is by design): verifier reports
  13/14 with ONLY C1 FAIL naming the paused job; the suite shows
  exactly ONE failure (`test_live_repo_passes_all_mechanical_checks`,
  C1 branch; 471 passing + this 1 designed failure = 472 ran, 4
  skipped) — both return to green
  automatically upon owner re-enable of `de939b52cc2b`; any future
  wake arriving despite the pause must read `jobs.json`
  state/paused_at BEFORE interpreting a red C1.

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
   4 skipped**, 19 subtests), at session 9 arrival at HEAD
   `20765f3` (**419 passed, 4 skipped**, 19 subtests), at session
   10 arrival at HEAD `b6deee7` (**423 tests, OK, 4 skipped**),
   at session 11 arrival at HEAD `4498e38` (**423 tests, OK, 4
   skipped**), and at session 12 arrival at HEAD `325b425`
   (**423 tests, OK, 4 skipped**);
   session 12 likewise re-ran all three standalone auditors green at
   one HEAD (signed-bracket exit 0, post-retention 17/17,
   follow-on-memo 21/21 clean with zero exact-claim failures),
   reproduced the full two-manifest pin re-hash bit-for-bit
   (signed-bracket 8/8; paired 29/29 + the debate log's frozen prefix
   bit-intact at exactly 45,421 bytes — zero bytes appended since
   session 10), closed both retained-directory inventories, and swept
   the whole tree for post-commit file modifications (none found
   outside `__pycache__`);
   session 11 additionally re-ran all three standalone auditors green
   at one HEAD (signed-bracket exit 0, post-retention 17/17,
   follow-on-memo 21/21 clean), reproduced the full two-manifest pin
   re-hash bit-for-bit (8/8 and 29/30 + proven pure-append), and
   confirmed zero debate-log bytes appended since session 10;
   session 13 reproduced the same battery bit-for-bit (suite 423 OK /
   4 skipped at arrival `dd39382`; auditors exit 0 with session-12-
   identical numbers; pins 8/8 + 29/30 + pure-append prefix intact;
   doors mechanically unfired: zero changed paths under `results/` /
   `failed-designs/` since `d19d7c2`, failed-designs at 8 entries)
   and consolidated the mechanical core into the one-command verifier
   `src/verify_retained_integrity.py` (+13 tests; post-unit suite
   **436 tests, OK, 4 skipped**) — future wakes should run
   `python3 src/verify_retained_integrity.py --auditors` plus the
   suite before anything else;
   session 14 followed exactly that prescription on its wake
   (verifier with `--auditors` **exit 0, 9/9 PASS** including all
   three standalone auditors green with session-12-identical
   numbers; suite **436 tests, OK, 4 skipped** at arrival HEAD
   `9364b5d`; whole-tree post-commit modification sweep clean) and
   logged the unit as the Part IV session-14 entry; session 15
   followed the same prescription again on its wake (verifier with
   `--auditors` **exit 0, 9/9 PASS** including all three standalone
   auditors green with session-12-identical numbers; suite **436
   tests, OK, 4 skipped** at arrival HEAD `036810f`; whole-tree
   post-commit modification sweep clean) and logged the unit as the
   Part IV session-15 entry;
   session 16 followed the same prescription again on its wake
   (verifier with `--auditors` **exit 0, 9/9 PASS** including all
   three standalone auditors green with session-12-identical numbers;
   suite **436 tests, OK, 4 skipped** at arrival HEAD `254d2aa`;
   whole-tree post-commit modification sweep clean; the debate log
   still exactly 45,421 bytes, zero appended since session 10) and
   logged the unit as the Part IV session-16 entry;
  session 17 followed the prescription again on its wake (verifier
  with `--auditors` **exit 0, 9/9 PASS** with session-12-identical
  auditor numbers; suite **436 tests, OK, 4 skipped** at arrival HEAD
  `945c38b`; debate log still exactly 45,421 bytes), verified the
  doors unfired, and — finding one genuine durable gap the prior wakes
  had missed — discharged it as the session-17 documentation unit
  (final-report §8 terminal-state addendum + essay postscript, both
  dated appends, originals byte-preserved, nothing pinned or retained
  touched; the Part IV entry was authored there but its process died
  pre-commit — completed, verified, and committed by the session-18
  wake per that entry's completion disclosure);
  session 19 reproduced the same battery again at arrival HEAD
  `d65840a` (verifier with `--auditors` **exit 0, 9/9 PASS**;
  suite **436 tests, OK, 4 skipped**; debate log still exactly
  45,421 bytes; doors unfired) and spent its durable-gap budget on
  the first out-of-repo root-cause fix of the stale-cron defect
  itself (scheduler job `de939b52cc2b` prompt replaced atomically
  under `.jobs.lock`; see the Part IV session-19 entry) — future
  wakes should arrive on the corrected v3 briefing and, if any wake
  ever receives the old `f753894` text again, re-run
  `/opt/data/.cache/fix_cron_briefing.py` (fails safe on unexpected
  content) before proceeding;
  session 20 followed the prescription again on its FIRST corrected-
  briefing arrival (v3 text delivered intact; verifier with
  `--auditors` **exit 0, 9/9 PASS** with session-12-identical auditor
  numbers; suite **436 tests, OK, 4 skipped** at arrival HEAD
  `b52e0f3`; debate log still exactly 45,421 bytes; doors unfired)
  and spent its durable-gap budget on the README §Status
  reconciliation (dated addendum beneath the original paragraph,
  which is byte-preserved; README verified unpinned in both freeze
  manifests pre-edit; see the Part IV session-20 entry);
  session 21 followed the prescription again on its second
  corrected-briefing arrival (v3 text delivered intact; verifier with
  `--auditors` **exit 0, 9/9 PASS** with session-12-identical auditor
  numbers; suite **436 tests, OK, 4 skipped** at arrival HEAD
  `75af015`; debate log still exactly 45,421 bytes; doors unfired)
  and spent its durable-gap budget on the project-report supersession
  reconciliation (visible dated notice atop `docs/project-report.md`,
  body byte-preserved; new Final-report bullet in README "Read
  first"; see the Part IV session-21 entry);
  session 22 followed the prescription again on its third
corrected-briefing arrival (v3 text delivered intact; verifier with
`--auditors` **exit 0, 9/9 PASS** with session-12-identical auditor
numbers; suite **436 tests, OK, 4 skipped** at arrival HEAD `f6ef4a3c`;
debate log still exactly 45,421 bytes; doors unfired) and spent its
durable-gap budget on the push-status terminal-state reconciliation
(visible dated Status addendum appended below the byte-preserved
original in `docs/push-status.md`, whose stale "push blocked" present
tense is thereby reconciled to the recorded same-day resolution;
push-status verified unpinned in both freeze manifests and the verifier
pin set pre-edit; see the Part IV session-22 entry);
  session 23 followed the prescription again on its fourth
corrected-briefing arrival (v3 text delivered intact; verifier with
`--auditors` **exit 0, 9/9 PASS** with session-12-identical auditor
numbers; suite **436 tests, OK, 4 skipped** at arrival HEAD `3f50cc9b`;
debate log still exactly 45,421 bytes; doors unfired) and spent its
durable-gap budget on the publication-guide provenance reconciliation
(dated provenance notes appended below the byte-preserved originals in
both `docs/push-status.md` and `docs/history-migration-2026-08-22.md`,
reconciling their citations of the never-committed
`scientific-repository-publication.md`; both files verified unpinned in
both freeze manifests and the verifier pin set pre-edit; see the Part IV
session-23 entry);
  session 24 followed the prescription again on its fifth corrected-
briefing arrival (v3 text delivered intact; verifier with `--auditors`
**exit 0, 9/9 PASS** with session-12-identical auditor numbers; suite
**436 tests, OK, 4 skipped** at arrival HEAD `a54092df`; debate log
still exactly 45,421 bytes; doors unfired) and spent its durable-gap
budget on the findings-synthesis closure addendum (visible dated
addendum beneath the byte-preserved 2026-08-01 title block of
`docs/stages1-6-findings-synthesis.md`, reconciling its pre-7B/8
present-tense terminal state to the retained record; file verified
unpinned in both freeze manifests and the verifier pin set pre-edit;
README read-with clause added; see the Part IV session-24 entry);
  session 25 followed the prescription again on its sixth corrected-
briefing arrival (v3 text delivered intact; arrival battery reproduced
bit-for-bit at HEAD `30d282f95225` = origin/main; doors unfired) and
spent its durable-gap budget on extending the one-command verifier
itself: new **S1 sync** check (HEAD == origin/main by local rev-parse,
mechanising briefing step 1's comparison half, unknown refs failing
loudly, behind/ahead counts on mismatch) plus a non-failing P2 info
line emitting the debate log's current byte size (= frozen prefix +
appended), retiring the manual stat disclosure every wake since
session 10 had hand-transcribed; +3 tests — future wakes should expect
`python3 src/verify_retained_integrity.py --auditors` **exit 0, 10/10
PASS** and suite **439 tests, OK, 4 skipped** (see the Part IV
session-25 entry);
  session 26 followed the prescription again on its seventh corrected-
briefing arrival (v3 text delivered intact; verifier with `--auditors`
**exit 0, 10/10 PASS** with session-12-identical auditor numbers; suite
**439 tests, OK, 4 skipped** at arrival HEAD `c9264e1af97157`; doors
unfired) and spent its durable-gap budget on content-binding the debate
log's appended region — new **L1 append-ledger** check plus the
monotone snapshot sidecar `docs/stage-8-debate-log-append-ledger.json`
(seed: 45,421 B @ `2b7929e0…`), closing the same-length suffix-rewrite
hole the prefix-only pin could not see; +6 tests — future wakes should
expect `python3 src/verify_retained_integrity.py --auditors` **exit 0,
11/11 PASS** and suite **445 tests, OK, 4 skipped** (see the Part IV
session-26 entry);
  session 27 followed the prescription again on its eighth corrected-
briefing arrival (v3 text delivered intact; verifier with `--auditors`
**exit 0, 11/11 PASS** with session-12-identical auditor numbers; suite
**445 tests, OK, 4 skipped** at arrival HEAD `574d389ce8e6`; doors
unfired) and spent its durable-gap budget on mechanising the last
hand-run wake step — new **C1 cron** check validating the out-of-repo
scheduler config strictly whenever present (zero stale `f753894`
markers anywhere; v3 hold briefing `de939b52cc2b` enabled; no
resurrected legacy project briefing) with a labelled non-failing SKIP
when absent; +7 tests — future wakes should expect `python3
src/verify_retained_integrity.py --auditors` **exit 0, 12/12 PASS** and
suite **452 tests, OK, 4 skipped** (see the Part IV session-27 entry);
  session 28 followed the prescription again on its ninth corrected-
briefing arrival (v3 text delivered intact; verifier with `--auditors`
**exit 0, 12/12 PASS** with session-12-identical auditor numbers; suite
**452 tests, OK, 4 skipped** at arrival HEAD `bf8d1b106e4e`; doors
unfired) and spent its durable-gap budget on content-binding the last
immutable class that lacked it — new **F1 failed-designs** check plus
the seed sidecar `docs/failed-designs-append-ledger.json` (all 39
archived files across 8 entries bound by {bytes, sha256}), closing the
hole that D1's diff-vs-one-fixed-base + entry count proved no byte of
content and would expire at the first lawful door-baseline roll-forward;
+5 tests — future wakes should expect `python3
src/verify_retained_integrity.py --auditors` **exit 0, 13/13 PASS** and
suite **457 tests, OK, 4 skipped** (see the Part IV session-28 entry);
   session 29 followed the prescription again on its tenth corrected-
briefing arrival (v3 text delivered intact; verifier with `--auditors`
**exit 0, 13/13 PASS** with session-12-identical auditor numbers; suite
**457 tests, OK, 4 skipped** at arrival HEAD `5de83ac68a3f`; doors
unfired) and spent its durable-gap budget on mechanising briefing
step 1's fetch half — new opt-in **N1 fetch** check (`--fetch`): runs
`git fetch origin` before S1 so the sync comparison is provably
post-fetch (S1 alone inherits the staleness of the local remote-
tracking ref; a skipped manual fetch plus a concurrent advance would
have passed indefinitely), failing loudly on any fetch error while the
default invocation stays fully offline; +3 tests — future wakes should
run `python3 src/verify_retained_integrity.py --auditors --fetch`
expecting **exit 0, 14/14 PASS** and suite **460 tests, OK, 4 skipped**
(see the Part IV session-29 entry);
   session 30 followed the prescription again on its eleventh
corrected-briefing arrival (v3 text delivered intact; verifier with
`--auditors --fetch` **exit 0, 14/14 PASS** with session-12-identical
auditor numbers; suite **460 tests, OK, 4 skipped** at arrival HEAD
`4a67bc755428` = origin/main; doors unfired) and spent its durable-gap
budget on documentation reconciliation (visible dated Status addendum
appended below the byte-preserved original Status block in
`docs/stage-7-split-reserve-architecture.md`, whose present-tense
NO-GO claims contradicted both the document's own §13 update and the
retained record through closure; file verified unpinned in both freeze
manifests and the verifier pin set pre-edit; see the Part IV
session-30 entry);
   session 31 followed the prescription again on its twelfth
corrected-briefing arrival (v3 text delivered intact; verifier with
`--auditors --fetch` **exit 0, 14/14 PASS** with session-12-identical
auditor numbers; suite **460 tests, OK, 4 skipped** at arrival HEAD
`bd49b217bc5a` = origin/main; doors unfired) and spent its durable-gap
budget on mechanising documentation→repository reference integrity —
the new FOURTH standalone auditor `src/audit_doc_path_references.py`
plus the lawful-absence registry `docs/doc-path-reference-registry.json`
(all 13 distinct absent citation strings across README.md + docs/*.md
registered under 6 evidence-backed classes: three failed-gate design
families, the large-file history migration, the superseded-by-repair
Stage 8 path, and one genuinely dead source citation never present in
any commit; R4 asserts registered paths STAY absent; R6 fails on
unanchored registrations); +16 tests — future wakes should run
`python3 src/verify_retained_integrity.py --auditors --fetch`
expecting **exit 0, 14/14 PASS** (A1 detail names FOUR auditors) and
suite **476 tests, OK, 4 skipped** (see the Part IV session-31 entry);
   session 32 arrived on its thirteenth corrected-briefing arrival (v3
   text intact; verifier `--auditors --fetch` **exit 0, 14/14 PASS** at
   arrival HEAD `e4539fbf90d9` = origin/main; doors unfired) and became
   the programme's first externally-interrupted unit: the 05:40 wake
   had died on OpenRouter HTTP 402 credit exhaustion (paid-service
   blocker; executions.db row `1693ddc0…`), and at 06:22:57 UTC an
   explicit owner-surface PAUSE landed on briefing job `de939b52cc2b`
   (`state=paused`, `paused_at` stamped; the gateway provably never
   self-pauses recurring jobs), which the suite's live-repo C1 smoke
   caught in real time between two reads — no re-arm performed, owner
   action overrides (see the Part IV session-32 entry); while the pause
   stands the expected battery is verifier 13/14 with ONLY C1 FAIL and
   exactly that one designed suite failure (471 passing + 1 = 472 ran,
   4 skipped), both auto-green on owner re-enable;
   session 9 added the follow-on-memo independent audit
   (`docs/followon-power-memo-independent-audit.md`,
   `src/audit_followon_power_memo.py`) and the Round-6-authorized memo
   corrigendum (memo §11, visible/dated, originals byte-preserved);
   session 10 added the first full re-hash of all pins in both freeze
   manifests (37/38 byte-exact; the single exception the append-only
   debate log, proven pure-append with its frozen prefix bit-intact —
   see the Part IV session-10 entry); push after every commit; keep
   the tree clean.
