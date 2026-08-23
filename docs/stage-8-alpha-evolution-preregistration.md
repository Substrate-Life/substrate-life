# Stage 8 Alpha-Evolution Preregistration: Dedicated-Locus Mutation on the Allocation Channel (evidentiary rung 2)

*Superseding preregistration. Date: 2026-08-23. Authorised by: owner's
standing order to carry on with the whole project autonomously; the
programme review `docs/stage-8-programme-review.md` (recommendation (c));
Stage 7B0 §11 ("only after a separately preregistered Stage 7B1 result may
dedicated-locus mutation be considered" — satisfied by the retained 7B1
PASS); architecture §9.3 evidential levels and §9.5 items 1–5; findings
synthesis M1 level 2. This document registers no execution by itself; its
implementation window opens on commit, and no retained execution occurs
before its §6 gate passes and its §7 freeze is committed.*

## 1. Registered reading of what precedes this registration

The Stage 7B signed-bracket line closed as a registered null:
32/32 COMPLETE, median paired difference −1/128 against floor 1/100,
class `NO_ESTABLISHED_CONTRAST`, co-report `ONE_ARM_SUBCRITICAL`
(`results/stage7b-signed-bracket/`). The post-retention audit
(`docs/stage-8-signed-bracket-audit.md`) verified every artifact and
scoped the dispersions descriptively. Nothing in that closure is re-run,
retuned, or re-litigated here.

What the closed line establishes for present purposes:

1. **Channel exists (rung 1), both levels.** Scripted exactness (7B0
   PASS) and population-level cohort-schedule differences reaching
   demography (certified brackets, genotype-level status asymmetry).
2. **Rung-2 precondition satisfied.** 7B0 §11 gates dedicated-locus
   mutation on a separately preregistered Stage 7B1 result; the 7B1
   retained PASS exists.
3. **A fixed-genotype contrast instrument at this ecology is
   exclusion-noise-dominated** (audit observation 3). A frequency
   trajectory integrates selection over many births and generations and
   is therefore the registered instrument for the next question — not a
   rerun of the paired-root contrast.

## 2. Registered question (rung 2 only)

Under the carried ecology (`N = 48`, `E = 900`, exogenous phenotype-blind
hazard `h = 1/120`, binding vacancy admission) with mutation enabled at
the dedicated `A` locus under the registered kernel of §3, does the
restricted architecture **evolve directionally through the allocation
channel** — i.e., does the population's allocation distribution move
beyond the registered floor toward HIGH α (`A/D → 4/5` side) or LOW α
(`→ 2/5` side) across independent replicates more consistently than the
registered neutral reference predicts?

The estimand is the per-replicate terminal mean allocation
`ᾱ_end = mean(A/255 over live members at tick W)` compared against the
founder reference `α_ref = 153/255 = 3/5`, aggregated by the §5 direction
statistic. Per findings M1 the permitted conclusion is exactly the
level-2 statement ("the restricted architecture does / does not evolve
through the channel, in the registered direction(s), at this ecology and
kernel"). **Not registered, tested, or permitted:** external validation
of the extrinsic-mortality prediction (single hazard arm; architecture
§9.5 items 1–4 are unverified here); any optimum, ESS, invasion-growth,
background-invariant causal effect of α, or open-genome claim.

## 3. Registered design decisions

| Item | Registered value | Rationale (committed before execution) |
|---|---|---|
| Legal lattice | `A ∈ {0, …, 255}` integers; `T = 128` and `D = 255` frozen constants | Carried `D` resolution; `A` remains a data operand inside an unchanged genome block, so execution tempo and genome length cannot change (trait-isolation gate). |
| Mutation site | Stage M of `divide_publish` only, after vacancy reservation (post-V), before child-memory reservation | The existing structural zero-draw point. Failed admissions (`NO_VACANCY`) discard before M and consume no kernel draws: mutation supply ties to realised births only. |
| Kernel | With probability `p_μ = 1/2` per published-birth candidate, `δ` uniform on `{−4,−3,−2,−1,+1,+2,+3,+4}`, child `A' = clamp(A + δ, 0, 255)`; else `A' = A`. Zero step excluded from support. | Generous supply (review (c) risk note): expected ≥ ~480 mutation events per replicate (§3 supply row). Symmetric, unimodal, max step 4 < floor 8 so no single event can manufacture a registered shift. Clamped boundaries disclosed up front. |
| Non-mutating loci | `T`, `D` never drawn; asserted constant genome-wide by the reducer | Architecture §9.5 item 5; trait-isolation gate. |
| Starting distribution | Founders carried verbatim: 3 × `(102,128,255)` + 3 × `(204,128,255)`, age 0, `S = 100`, `R = 0`; `α_ref = 3/5` | Extends the two carried strategies into evolutionary time; both extremes present at t=0, so the direction statistic measures which side the channel favours rather than mutation-walk speed from one point. |
| Ecology (carried verbatim) | `N=48`, packet rate 5/tick, `E=900`, buffer depth 64, shared memory 65,536 B, corpse TTL 2, hazard `h = 1/120` | Single arm ⇒ outcome is labelled an evolution-through-channel result at fixed ecology; no mortality-vs-recruitment separation claim arises (architecture §9.5 labelling rule not triggered because no cross-hazard contrast is registered). |
| Window | `W = 2400` ticks = 20 expected lifespans (`1/h = 120`) ≈ 20 census turnovers; expected realised births ≈ `N·h·W = 960` per replicate | Duration stated in hazard-scaled generations (architecture §9.5 item 5). Doubles the closed line's window; wall ≈ 24 × ~3.5 min ≈ 85 min sequential, less under the existing `--workers` runner. |
| Effective population size | No `N_e` claim is registered. Census cap 48; the neutral reference below is calibrated by exchangeability across replicates, not by an `N_e` approximation. Realised per-replicate turnover and census trajectories are co-reported descriptively. | Overlapping generations under vacancy capture make a scalar `N_e` a model choice; registering one would be spurious precision. The sign-based reference needs only between-replicate independence and within-replicate symmetry (§4). |
| Confirmatory seed table | `hazard_seed = 20284617 + i`, `i ∈ {0,…,23}` (`k = 24`) | Fresh table, disjoint by construction from every prior population table: `{20260822+0..31}`, `{20261822+0..31}`, `{20270000+0..23}`. One-use confirmatory discipline carried. |
| Shakedown seed table | `hazard_seed = 20293311 + j`, `j ∈ {0,…,11}` (`k = 12`) | Fixed before any execution; disjoint from all tables above. Exploratory, unretained (§6). |
| Mutation RNG stream | `random.Random(hazard_seed * 1000003 + 7)`, consumed only at Stage M | Deterministic, documented derivation; disjoint stream ⇒ hazard realisations at a given seed are identical to those of prior-generation runs, keeping the demographic skeleton comparable. Rolled-back transactions retain consumed draws (§7 semantics carried). |
| Mutation supply accounting | Every Stage-M decision emits a telemetry record (parent `A`, `δ` or no-mutation flag, child `A'`, stream position); reducer reconciles records against admitted births | Makes the kernel auditable post hoc without any tuning freedom. |

**Disclosed power rationale (design input, committed before execution).**
Under the neutral reference — symmetric kernel, no α-linked demographic
effect, independent replicates — each eligible replicate's terminal mean
is symmetric around `α_ref` up to clamping asymmetry, which is negligible
while mass stays ≥ 51 lattice units from the boundaries and strictly
reduces false-positive risk once it does not (the floor requirement makes
a classified replicate harder than a sign flip, so the binomial tail is
an upper bound on the null classification rate). The probability that ≥
18 of 24 eligible replicates concur in one direction is at most
`190051/2²⁴ ≈ 0.01133` one-sided, `≈ 0.02266` two-sided. Supply side:
~960 births × `p_μ = 1/2` ≈ 480 kernel events per replicate, ~11,500
across the suite, over 20 turnovers — generous relative to the review's
"powered generously up front" requirement. These numbers size the test;
they are not measurements and predict no outcome.

## 4. Registered endpoint definitions

- **Primary (per replicate):** terminal mean allocation `ᾱ_end`, equal
  weight over live members at the tick-W census close (active and
  recoverable-depleted/stalled alike; state composition co-reported).
- **Direction classes (per replicate, eligibility in §5):** mover-up iff
  `ᾱ_end − α_ref ≥ Δα_floor`; mover-down iff `≤ −Δα_floor`;
  `Δα_floor = 8/255` (= twice the maximum kernel step, so only
  accumulated directional change can cross it).
- **Trajectory checkpoints (co-report):** `ᾱ` at ticks 120, 240, …, 2400
  (20 points), same estimator.
- **Terminal histogram (co-report):** full lattice occupancy of `A` at
  tick W; founder-ancestry frequencies via the immutable ancestry tags
  (`F0…F5`), descriptive only.
- **Recruitment telemetry (co-report, mediator-labelled per architecture
  §9.4 and 7B1 §6.2):** bout-completion rate (intrinsic),
  vacancy-capture rate (ecology), realised recruitment (product), per
  founder ancestry and per α-tercile of the live census; shadow
  `would_admit` counters as recorded. These are never promoted to
  endpoints by this document.
- **Extinction:** a replicate with zero live members at tick W is
  COMPLETE (ledgers closed, window finished) but direction-ineligible;
  extinction count is co-reported. Sterile persistence earns no credit
  anywhere: census presence alone is not fitness language, and no
  fitness word appears in any classification label of this registration.

## 5. Decision rule (applied exactly once, by the source-frozen reducer)

Let `k_eff` = number of **eligible** replicates: COMPLETE with ≥ 1 live
member at tick W. Classes:

1. `DEGENERATE_EVOLUTION` — `k_eff < 16` (carried two-thirds-of-table
   floor convention).
2. `ESTABLISHED_TOWARD_HIGH_ALPHA` — `k_eff ≥ 16` and
   `#{mover-up} ≥ 18`.
3. `ESTABLISHED_TOWARD_LOW_ALPHA` — `k_eff ≥ 16` and
   `#{mover-down} ≥ 18`.
4. `NO_ESTABLISHED_DIRECTION` — otherwise (including split concordance).

Exactly one class is emitted. Thresholds 16/18/24, the floor 8/255, the
kernel, and both seed tables are frozen by this document; retuning any
of them after any execution is prohibited (§9). Co-reported alongside,
descriptively: concordance counts, median `|ᾱ_end − α_ref|` among movers,
trajectory shapes, histograms, recruitment telemetry, extinctions.

## 6. Pre-freeze feasibility gate (binding)

Run unretained exploratory shakedowns at the exact registered ecology,
kernel, and window on the fixed 12-seed shakedown table (stdout only; no
retained artifact). All conditions mandatory:

- **G1 (evolution operates):** ≥ 2/3 of shakedown replicates COMPLETE
  with ≥ 1 recorded mutation event, ≥ 2 distinct `A` values among live
  members at tick W, and zero `T`/`D` values other than 128/255 anywhere
  in the event stream.
- **G2 (implementation integrity):** zero `BUFFER_OVERFLOW` /
  `INVALID_IMPLEMENTATION`; every ledger closes at every checkpoint in
  every replicate (inherited assertion machinery, unchanged).
- **G3 (kernel audit):** every admitted birth carries exactly one
  Stage-M record; every recorded child satisfies `0 ≤ A ≤ 255`,
  `T = 128`, `D = 255`; replaying the documented stream derivation
  reproduces the recorded draw sequence bit-exactly on one full
  replicate re-executed by the gate tooling.
- Shakedown summaries (turnover counts, mutation counts, terminal
  spreads, wall clock) are reported **without thresholds** as factual
  context in the freeze-commit notes; they may not resize anything.

If any condition fails: no freeze; a further superseding preregistration
with diagnosis, archived under `failed-designs/`, never deleted.

## 7. Freeze-before-execution and authorised execution class

1. **Implementation window (authorised on commit of this document):**
   new additive modules only — population subclass overriding Stage M
   (the overridden method being a verbatim copy of the frozen
   `divide_publish` body with only the registered M-stage substitution),
   configuration layer, gate tooling, runner, reducer, output schema,
   tests — including re-running the carried 7B1 fault-injection matrix
   against the subclass with the added assertion that consumed kernel
   draws stay consumed across rollbacks. Frozen modules
   (`stage7b1_mechanics.py`, `stage7b2_population.py`,
   `stage7b2r_population.py`, and their dependencies) are reused
   byte-identically by import and never edited.
2. **Gate:** §6 passes on the shakedown table.
3. **Freeze:** implementation, runner, reducer, tests, schema, and the
   reused modules pinned by SHA-256 + byte size in a pre-execution
   manifest at `results/stage8-alpha-evolution/pre-execution-manifest.json`,
   committed before any retained run (df7b1f5 precedent).
4. **Authorised execution class:** one seeded confirmatory suite —
   `k = 24` replicate populations, seeds `20284617 + i`, `i ∈ {0,…,23}`,
   `W = 2400`, executed once; raw outputs retained under
   `results/stage8-alpha-evolution/`; reduced exactly once under the §5
   rule by the frozen reducer; outcome classified whatever class results,
   including `NO_ESTABLISHED_DIRECTION` or `DEGENERATE_EVOLUTION`, which
   are legitimate registered results.
5. PASS criterion: every ledger closes at every checkpoint in every
   replicate; G3-style kernel audit passes on the confirmatory artifacts;
   the rule is applied exactly once and recorded. Any failure retains the
   run, classifies it, and triggers repair policy — archiving, never
   deletion.

## 8. Standing-rules compliance and falsification-gate mapping

Exact `Fraction` arithmetic in every ledger (carried machinery,
unchanged); kernel draws are integer-lattice operations outside the
ledgers and never feed approximations into them. Telemetry labels never
read by mechanics. Gates engaged: trait-isolation (only `A` mutates;
tempo/length invariant; reducer asserts `T`,`D` genome-wide),
trait-resolution (lattice, kernel, start, duration, seeds all fixed here,
pre-execution), endpoint (primary is the registered trajectory/direction
estimand of the mutation-enabled rung-2 design per §9.3/M1; §9.4
mediator-currency rules respected by labelling recruitment telemetry as
mediators), vacancy/storage/packet-sink (carried machinery unchanged),
ecology (single arm; no hazard-gradient language permitted), plasticity-
scope (genotypic lifetime-fixed `A` only; no plasticity interpretation),
no-historical-carry-over (no pre-Stage-7 effect size reused; the power
rationale uses only arithmetic of the registered design and the already-
published null). Failed designs archived; retained artifacts immutable;
push after every commit; suite kept green.

## 9. Not authorised by this document

Any retained execution before the §6 gate passes and the §7 freeze is
committed; mutation at `T`, `D`, or any genomic locus beyond the
registered Stage-M `A` step; plastic or within-lifetime allocation
changes; additional hazard arms or any factorial/recruitment-separation
study; open genomes or length/tempo evolution; changing the ecology,
window, kernel, floor, thresholds, or either seed table — now or after
the confirmatory suite runs; rerunning or retuning any closed Stage 7B
line; promoting recruitment/vacancy/capture telemetry to endpoints;
external-validation, optimum, ESS, causal-gradient, or open-population
(rung 3) claims; interpreting `NO_ESTABLISHED_DIRECTION` as evidence of
absent selection strength beyond the registered instrument; in-place
edits to any frozen module or committed prior-generation file; reuse of
pre-Stage-7 quantities; modification of retained artifacts or superseded
documents; history rewrites.
