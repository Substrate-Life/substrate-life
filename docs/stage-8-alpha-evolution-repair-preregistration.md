# Stage 8 Repair Preregistration: Paired Mutation-On/Off Reference Arms on the Allocation Channel

*Superseding repair registration. Date: 2026-08-23. Authorised by: the
owner's standing autonomous-advance order; the binding disposition of
`docs/stage-8-debate-log.md` (commit `8f7bb89`), item 2; the supersession
clauses of `docs/stage-8-alpha-evolution-preregistration.md` §9 read
together with the house supersession precedent (each generation of this
programme has been replaced by registration, never retuned). This document
registers no execution by itself; its implementation window opens on
commit, and no retained execution occurs before its §7 gate passes and its
§8 freeze is committed.*

## 1. Registered reading of what precedes this registration

The pre-freeze adversarial review (`docs/stage-8-debate-log.md`) found,
and this registration ACCEPTS as the operative record:

- **O1:** the prior single-arm direction statistic was a founder-priority
  counter — founders sit ±51 lattice units from `α_ref`, the mover floor
  was 8 units, the mutational cloud SD is single-digit units, and
  winner-take-most exclusion (documented at this exact ecology) means the
  classification would be decided by *which founder won*, not by evolution
  through the channel. A `p_μ = 0` suite would produce nearly the same
  outcome distribution.
- **O2:** mutation *supply* was sized; selection *response* was not —
  no H1 power derivation existed.
- **O3:** the 0.0113 neutral tail assumed replicate exchangeability that
  the retained record already contradicts (21/9 sign split, two-sided
  p ≈ 0.043, implies true LOW-win probability ≈ 0.6–0.7).

Disposition item 1 (binding): the gate → freeze → retained-execution chain
of the prior design **is cancelled**. It was never started: the §6 gate was
never run, no freeze manifest was committed, and no confirmatory run
occurred. Zero executions were consumed. The prior documents remain
historical and are never edited; the additive implementation layer (kernel,
population subclass, fault matrix, measurement layer, runner, reducer,
gate tooling, schema — commits `f753894` … `91986f4`) carries forward
byte-identically as registered infrastructure. The prior seed tables
`{20284617 + i}` and `{20293311 + j}` are retired **unexecuted** and are
never used by any future stage (fresh tables below; retirement removes any
question of one-use discipline).

## 2. Registered question

Under the carried ecology (`N = 48`, `E = 900`, `h = 1/120`, vacancy-bound
admission, `W = 2400`), with the registered dedicated-locus kernel enabled
(Arm **M**) versus the identical configuration with the kernel disabled
(Arm **R0**) at the *same* `hazard_seed`, does the population's allocation
distribution move directionally through the channel — i.e., is the
**paired difference**

`D_i = ᾱ_end(M, s_i) − ᾱ_end(R0, s_i)`

consistently directional across independent pairs beyond the registered
neutral reference of §6?

The founder lottery is common mode across a pair: whichever founder lineage
wins, it wins (to first order) in both arms, because kernel steps are
bounded at ±4 units while the documented exclusion margins are
order-of-magnitude larger. The lottery term therefore cancels in `D_i`,
which is precisely the defect O1 identified in the single-arm statistic.
O3's skew applies to *raw* `ᾱ_end`; the inferential claim of this
registration is conditional symmetry of `D_i` under the null, restored by
pairing. Residual "pair-flip leakage" (seeds where the win margin is so
small the kernel perturbation flips the winner in one arm) is disclosed:
such pairs contribute large `|D_i|` with approximately symmetric sign and
are absorbed by the split-concordance rule, exactly as split outcomes are.

Permitted conclusion space is unchanged (level-2 only): the restricted
architecture does / does not evolve through the channel, in the registered
direction(s), at this ecology and kernel, *relative to its own
mutation-off reference*. No external validation, optimum, ESS,
causal-gradient, open-genome, or cross-hazard claim is licensed.

## 3. Registered design decisions

| Item | Registered value | Rationale (committed before execution) |
|---|---|---|
| Arms | Pairwise: Arm M (kernel `p_μ = 1/2`, steps `±1..±4` clamped, `T/D` frozen — prior registration §3 verbatim) and Arm R0 (kernel absent: the frozen `Stage7B2Population` behaviour, no mutation site, no kernel draws) | The reference arm cancels founder priority and all shared ecological stochasticity up to within-pair divergence; R0 is byte-frozen machinery, so arm asymmetry is exactly the kernel. |
| Pairing | Both arms of pair `i` run `hazard_seed = s_i`; hazard-stream derivation unchanged | Same exogenous draw sequences wherever trajectories coincide; replicate-level pairing is the registered unit. |
| Ecology / founders / window | Carried verbatim: `N=48`, `E=900`, buffer 64, memory 65,536 B, corpse TTL 2, packet rate 5/tick, `S=100`, `R=0`; founders 3×(102,128,255)+3×(204,128,255); `W = 2400` | Unchanged from the cancelled registration; comparability of the demographic skeleton. |
| Endpoint | Per pair: `D_i = ᾱ_end^M − ᾱ_end^{R0}`, each `ᾱ_end` the equal-weight mean of `A/255` over live members at tick-W census close (exact Fractions) | Restates the estimand as the paired difference per disposition item 2. |
| Direction classes | pair moves up iff `D_i ≥ Δ_pair_floor`; down iff `≤ −Δ_pair_floor`; **`Δ_pair_floor = 4/255` lattice units** | Two independent justifications, both committed: (i) `4` equals the maximum kernel step magnitude, so no single mutation event can manufacture a classified pair (mirrors the prior floor logic); (ii) H0 noise sizing (§6): the mutational-cloud mean deviation has SD ≈ 1.6–2.0 units, so 4 units sits at ≥ 2σ of the null paired difference. |
| Eligibility | Pair eligible iff both arms COMPLETE and both have ≥ 1 live member at tick W | Carried extinction convention, applied pairwise. |
| Confirmatory table | `hazard_seed = 20310529 + i`, `i ∈ {0,…,23}` (`k = 24` pairs = 48 runs) | Fresh, disjoint from every prior population table including the retired-unexecuted pair `{20260822+0..31}`, `{20261822+0..31}`, `{20270000+0..23}`, `{20284617+0..23}`, `{20293311+0..11}`. One-use discipline carried. |
| Shakedown table | `hazard_seed = 20421301 + j`, `j ∈ {0,…,11}` (`k = 12` pairs) | Fixed before any execution; disjoint from all tables above; exploratory, unretained. |
| Kernel stream (Arm M) | `random.Random(hazard_seed * 1000003 + 7)`, consumed only at Stage M; rollbacks retain draws | Carried verbatim; Arm R0 constructs no such stream. |
| Telemetry | Arm M: every Stage-M decision recorded and reconciled against admitted births (carried). Arm R0: reducer asserts zero `mutation_decision` events and zero kernel draws | Makes the arm contrast auditable without tuning freedom. |

## 4. Registered endpoint definitions (co-reports)

Per arm, everything in the prior registration §4 carries forward
(trajectory checkpoints at 120…2400, terminal histograms, ancestry
frequencies, recruitment telemetry as mediator-labelled descriptives,
extinction flags, state composition). Added pair-level descriptives:
`D_i` per eligible pair; per-pair terminal live-census sizes in both arms;
the sign-and-magnitude table of `D_i`; count of pairs where the two arms'
terminal founder-ancestry majorities disagree (leakage monitor).
These are context, never endpoints.

## 5. Decision rule (applied exactly once, by the source-frozen reducer)

Let `k_eff` = number of eligible pairs.

1. `DEGENERATE_EVOLUTION` — `k_eff < 16`.
2. `ESTABLISHED_TOWARD_HIGH_ALPHA` — `k_eff ≥ 16` and `#{D_i ≥ +Δ_pair_floor} ≥ 18`.
3. `ESTABLISHED_TOWARD_LOW_ALPHA` — `k_eff ≥ 16` and `#{D_i ≤ −Δ_pair_floor} ≥ 18`.
4. `NO_ESTABLISHED_DIRECTION` — otherwise (including split concordance).

Exactly one class is emitted. Thresholds 16/18/24, the floor `4/255`, both
seed tables, and both arm definitions are frozen by this document;
retuning any of them after any execution is prohibited (§10). Null-tail
arithmetic (design input, conditional on the pairing argument of §2):
under H0 each eligible pair's `D_i` is symmetric about 0 up to clamp
asymmetry (negligible ≥ 51 units from boundaries) and leakage leakage is
sign-symmetric, so the probability that ≥ 18 of 24 eligible pairs concur
in one direction is at most `190051/2²⁴ ≈ 0.01133` one-sided,
`≈ 0.02266` two-sided — the same arithmetic as before, now applied to a
statistic whose exchangeability premise is defended rather than assumed.

## 6. H1 power derivation in α-units (committed before execution)

Response sizing (Lande form): expected displacement of the terminal mean
under per-A-unit selection slope `β` is
`E[Δᾱ] ≈ β · ∫σ²_A dt / 255`, integrating phenotypic variance in
A-units² over the window in turnover units.

- Coexistence phase (founders balanced around 153): deviations ±51 ⇒
  `σ²_A ≈ 2601`. Historically exclusion completes in ~2–4 turnovers.
- Post-exclusion cloud: per-lineage random walk with per-birth second
  moment `½·(2(1²+2²+3²+4²)/8) = 3.75`, ≈ 20 births per lineage ⇒
  `σ²_A ≈ 75`.
- Integral: realistic ≈ `2601·3 + 75·17 ≈ 9.1×10³`; absolute ceiling
  (permanent coexistence) `2601·20 ≈ 5.2×10⁴`.

Detectable slope at floor 4 units: `β_min ≈ 4/9.1×10³ ≈ 4.4×10⁻⁴`
(realistic) down to `≈ 7.7×10⁻⁵` (permanent-coexistence ceiling). For
calibration, the retained cross-sectional record bounds the analogous
slope at `≲ 8×10⁻⁵`.

**Registered consequence, stated plainly:** under the realistic-exclusion
regime the expected outcome is `NO_ESTABLISHED_DIRECTION`; the design is
sensitive to slopes ≈ 5–55× larger than the cross-sectional bound, except
insofar as long-lived coexistence narrows the gap. This is registered as
the design's *purpose*, not its embarrassment: the one authorised
execution converts the founder-lottery-confounded question into a
controlled, paired, one-shot answer whose null branch licenses the
level-2 statement "no redistribution through the channel ≥ 4/255 per 20
turnovers relative to its own mutation-off reference" — closing review
direction (c) at this ecology cleanly — and whose non-null branch would be
genuine discovery at 20× finer longitudinal resolution than any prior
instrument. No further arm, seed, or window may be added to escape a null
(§10); the follow-on decision (strengthened-contrast ecology probe versus
programme closure per review directions (a)/(d)) belongs to the next
registration and reads whatever this one registers.

## 7. Pre-freeze feasibility gate (binding)

Run unretained exploratory shakedowns at the exact registered ecology on
the fixed 12-*pair* shakedown table (stdout only; no retained artifact).
All conditions mandatory:

- **G1 (evolution operates, Arm M only):** ≥ 2/3 of pairs COMPLETE with
  ≥ 1 recorded mutation event, ≥ 2 distinct `A` values among live members
  at tick W (Arm M), and zero non-frozen `T/D` anywhere in either arm's
  event stream.
- **G2 (implementation integrity):** zero `BUFFER_OVERFLOW` /
  `INVALID_IMPLEMENTATION`; every ledger closes at every checkpoint in
  every arm.
- **G3 (kernel audit, Arm M):** every admitted birth carries exactly one
  Stage-M record; bounds and replay checks bit-exact (carried §6-G3 of the
  prior registration, unchanged).
- **G4 (reference-arm integrity):** every Arm R0 record shows zero
  `mutation_decision` events and zero kernel draws; both arms of a pair
  ran the identical `hazard_seed`; the pair table is complete.

If any condition fails: no freeze; a further superseding preregistration
with diagnosis, archived under `failed-designs/`, never deleted.

## 8. Freeze-before-execution and authorised execution class

1. **Implementation window (opens on commit of this document):** additive
   modules only — arm plumbing (R0 constructor path; M path carried),
   runner extension for pairwise execution, new source-frozen paired
   reducer, gate updates for G4, output-schema addendum, tests. The
   existing modules are edited only where the prior registration's own
   §7(1) window left them open (they are not yet frozen by any manifest);
   the Stage 7B frozen stack remains byte-untouched.
2. **Gate:** §7 passes on the shakedown table.
3. **Freeze:** implementation, runner, reducers, tests, schema pinned by
   SHA-256 + byte size at
   `results/stage8-alpha-evolution-paired/pre-execution-manifest.json`,
   committed before any retained run (df7b1f5 precedent).
4. **Authorised execution class:** one seeded confirmatory suite — `k = 24`
   pairs (48 runs), seeds `20310529 + i`, `W = 2400`, executed once; raw
   outputs retained under `results/stage8-alpha-evolution-paired/`;
   reduced exactly once under §5. Any failure retains the run, classifies
   it, and triggers repair policy — archiving, never deletion.

Wall-clock disclosure: ≈ 48 × ~3.5 min sequential ≈ 170 min; ≈ 85 min at
two workers.

## 9. Standing-rules compliance

Exact Fraction arithmetic everywhere (kernel draws integer-only, outside
ledgers); telemetry labels never read by mechanics; trait-isolation gate
(only `A` changes; tempo/length invariant; reducer asserts `T`,`D`
genome-wide in both arms); trait-resolution (lattice, kernel, start,
duration, floors, seeds fixed here, pre-execution); endpoint gates
(primary is the registered paired estimand; recruitment telemetry stays
mediator-labelled); ecology gate (single hazard arm; no mortality-vs-
recruitment separation language); plasticity-scope (genotypic
lifetime-fixed `A` only); no-historical-carry-over (no pre-Stage-7 effect
sizes reused; the power section uses only registered-design arithmetic
and the published retained record); failed designs archived; retained
artifacts immutable; push after every commit; suite kept green.

## 10. Not authorised by this document

Any retained execution before the §7 gate passes and the §8 freeze is
committed; running either arm at any seed outside the registered tables;
reusing the retired tables `20284617+i` / `20293311+j`; editing the
cancelled registration's documents or any retained artifact; adding arms,
windows, floors, thresholds, or loci — now or after execution; promoting
co-reports to endpoints; interpreting a registered null as evidence about
ecologies not tested here; external-validation, optimum, ESS, causal-
gradient, or open-population claims; history rewrites.

## 11. Output schema addendum

Raw artifacts carry one record per RUN with fields `arm ∈ {M, R0}` and
`pair_index`, plus the per-run fields of
`docs/stage8-alpha-output-schema.md` (Arm M exactly as specified there;
Arm R0 omitting kernel-specific blocks). The reduced artifact adds the
pair-level table of §4 and the §5 outcome block. Full field pins land in
the implementation-window schema addendum before the gate runs.
