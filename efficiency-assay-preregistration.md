# Efficiency Assay Pre-registration

**Initial registration:** 2026-07-27T17:39:18+00:00  
**Ecological-regime amendment:** 2026-07-27T18:05:01+00:00  
**Direct-cap/queue amendment after independent review:** 2026-07-27T18:54:40+00:00  
**Discrete-capture/turnover amendment:** 2026-07-27T20:05:45+00:00  
**Sustained-recruitment calibration/no-go amendment:** 2026-07-27T20:25:35+00:00  
**Mixed-ecology/timing-closure amendment:** 2026-07-27T20:37:37+00:00  
**Seven-tick substrate-maturation amendment:** 2026-07-27T20:50:56+00:00  
**Maturation tick-semantics correction:** 2026-07-27T20:53:36+00:00  
**Maturation-calibration rejection:** 2026-07-27T20:57:16+00:00  
**Empirical capture-response amendment:** 2026-07-27T21:08:52+00:00  
**Capture-response result:** 2026-07-27T21:20:37+00:00  
**Miss-tolerance interpretation and no-miss control:** 2026-07-28T17:03:47+00:00  
**Three-bout p=1 capacity-trace registration:** 2026-07-28T17:12:19+00:00  
**Three-bout result and conditional-trace registration:** 2026-07-28T17:14:59+00:00  
**Conditional-trace treatment-verification failure:** 2026-07-28T17:18:05+00:00  
**Bit-test conditional trace registration:** 2026-07-28T17:27:18+00:00  
**Bit-test conditional trace result:** 2026-07-28T17:29:06+00:00  
**Threshold-audit reclassification:** 2026-07-28  
**OFFSPRING_TROUGH removal / prospective invalidation:** 2026-07-28  
**Status:** CLOSED HISTORICAL DESIGN — no mixed-population efficiency run was performed. All results below were generated under threshold-18 semantics and are parameter-stale for the current no-threshold substrate.

## Prospective source-state amendment: no offspring trough

The executable substrate no longer evaluates offspring reserve against `OFFSPRING_TROUGH`. Every materially allocatable copied offspring is instantiated with the exact parent transfer, then pays ordinary upkeep, instruction, displacement, memory, and corpse costs. Failure to reach positive extraction is recorded longitudinally as death before first extraction. `stillbirth` below refers only to the historical threshold-18 telemetry and is not a current organism category.

This source change invalidates the historical τ≈20% optimum, response sweep, p=1 control, and conditional population design prospectively. Their raw observations remain preserved for the old source state; none is reinterpreted as no-threshold evidence. The no-threshold mechanism, deterministic mixed capacity/viability prediction, τ-landscape hypothesis, falsification conditions, and required future registration are recorded in `offspring-trough-removal-preregistration.md`. No τ or mixed-population rerun is authorized here.

A second prospective amendment removes reproducing-parent protection during cap replacement. Victims are now sampled uniformly over all incumbents, including the parent. Every cap event carries the causing offspring ID and is later classified by that offspring's first-extraction outcome. The historical non-parent-victim and parent-protection descriptions below remain accurate only for their archived source state. The subsequent `144/338 = 0.4260` censored smoke finding establishes that doomed-birth displacement remains materially active: parent eligibility removed an asymmetry, not the hard-cap birth→mortality channel. Together with reserve-mediated mortality under uncapped scarcity, this closes the clean provisioning-assay line under the current regulator set. Any future capped life-history study must still report the fraction of live displacements caused by offspring that later die before first extraction, unresolved live-victim outcomes, dead-vacancy fills separately, and parent-victim fraction.

## 0. Superseded Pre-run Design

The initially registered L=20/E=300 design had four forced copy-and-DIVIDE bouts. Closing the complete reproduction ledger showed that it was non-viable even with certain capture (`f=1`): FULL died at tick 59 and HALF at tick 34 in isolated-parent traces. Its first-cycle result (three versus one live offspring) was transient founder-capital spending, not a sustainable rate benchmark.

Deterministic mean-yield survival required the equivalent of `f=1.11643` for FULL and `f=2.20438` for HALF, both above the physical maximum. Raising packet rate cannot repair a genotype that fails at `f=1`. The L=20 benchmark and its `s=1` prediction are withdrawn before the assay. No mixed-population result exists under that design.

## 1. Question

In one population sharing one packet stream, does greater lossless extraction create a graded relative-fitness advantage while both phenotypes continue reproducing? The confirmatory question is explicitly **not** whether the more efficient phenotype eventually excludes a competitor from one limiting resource.

## 2. Amended Treatments

Both genomes are length 14 and identical except for the resolved extent of one `TRANSFORM RLE` instruction:

- **FULL:** `TRANSFORM RLE, R1, 256`
- **HALF:** `TRANSFORM RLE, R1, 128`

Both arms:

1. set `R5=51` (nominal τ = 51/256 ≈ 19.92%);
2. set `R6=14`, exactly the genome length;
3. allocate and READ the complete 256-byte packet;
4. execute their assigned transform extent;
5. free the allocation;
6. execute two unrolled real-copy bouts, each `ALLOC_OFFSPRING 64`, `COPY_BLOCK`, `DIVIDE`;
7. jump back to the forage block.

Every offspring requires a new gestation allocation and a new 14-instruction copy. There is no persistent copied-genome reuse.

## 3. Assay-Specific Environment

Required live values:

- `phase_mode=monotonic_rich`
- `packet_e_rich=500`
- `packet_e_lean=500`
- `packet_rate=11`
- `buffer_depth=132`
- `initial_buffer_packets=132`
- `population_cap=155`
- initial shared memory pool = 81920 bytes
- 78 FULL and 77 HALF founders seeded directly at the cap in the same `Simulation`
- seeds 201, 202, 203, 204, 205
- maximum observation time t=600

E=500 is an assay-specific energy level, not a change to the project's default E=300 ecology. It is required because at E=300 a two-bout HALF lineage is not reproductively sustainable even at `f=1`; that would make the assay demographic culling from inception.

The recurring cycle duration was measured from live PC returns: cycle starts occurred at ticks 14, 26, 38, 50, 62, and 74, so `T_cycle=12`. Peak live working memory was 320 bytes in both arms: the 256-byte forage allocation and 64-byte baseline overlap, while forage and 64-byte gestation allocations do not. The nominal synchronized active-organism ceiling is therefore `floor(81920/320)=256`, before corpse-TTL occupancy and phase dispersion.

The earlier P=11/cap=500 design would only transit N=146.67...165 in about 1.29 ticks. The subsequent grow-from-40/cap=155 design is also superseded before any mixed run: a full 132-packet queue drains at only `155/12-11=1.9167` packets/tick at cap and needs about 68.9 ticks to clear, so a 24-tick burn-in would remain backlog-dominated.

The registered cap is the ecological regulator. At N=155, one valid READ per organism per 12-tick cycle gives 155 attempts against 132 arrivals, predicting `f_eq=(11×12)/155=0.851613`. This lies inside `[0.80,0.90)`, above HALF parent survival (0.65826) and k≥1 (0.77226), and above FULL k=2 (0.46185). The active-organism all-at-peak allocation is `155×320=49,600` bytes, leaving 32,320 bytes before corpse-TTL occupancy; memory is intended to remain non-binding.

The population is therefore seeded directly at N=155 with an explicit standing buffer of 132 packets. The 78/77 founder split is the closest integer allocation to 50/50. All founders begin with the same reserve and phase; under the engine's zero-based event timestamps their first READ occurs at tick 4, after which recurrent READs occur every 12 ticks. Starting the queue at one cycle's supply makes the first and subsequent synchronized bursts target 132 successes among 155 attempts without a growth or queue-drain history.

Buffer depth is the full cycle supply, `11×12=132`, not merely the per-tick rate. A depth of 11 would make realised supply depend on accidental phase dispersion. Before a run, constructor readback must show 132 standing packets and a mechanical 155-read burst on a disposable verification instance must yield exactly 132 successes.

At cap, a birth event samples a random non-parent dictionary entry. If it is live, this is Moran-like displacement; if it is a same-tick DEAD entry awaiting the next reaper pass, the birth fills a vacancy without another live death. Both cases are logged separately. Victim choice is phenotype-blind among eligible entries, but the reproducing parent is protected. Cap replacement is therefore not described as wholly non-differential.

Each output starts with `Simulation.realised_parameter_header()` and `Simulation.realised_memory_capacity_header(320)`. Required readback includes `population_cap=155`, `packet_rate=11`, `buffer_depth=132`, `initial_buffer_packets=132`, `memory_pool_bytes=81920`, `peak_bytes_per_organism=320`, and `synchronous_peak_population_ceiling=256`. Assert 78/77 live founders, all at reserve 100 and PC=0, plus a rich packet budget of 500. Abort on mismatch. Per-tick output retains free/committed memory and cumulative allocation failures; any allocation failure from seeding through the primary endpoint invalidates the intended cap-regulated regime.

The immutable treatment ancestry label and unique `founder_lineage_id` are lineage measurements only. Phenotype is classified from the resolved transform execution.

## 4. Required Pre-run Regression

Run:

```text
python3 -m unittest -v \
  test_transform_memory_accounting.py \
  test_gestation_memory_accounting.py \
  test_realised_parameters.py \
  test_assay_instrumentation.py
```

For HALF, the 128-byte transform must leave the enclosing allocation at 256 bytes, return no pool capacity at transform time, retain untouched tags, and return exactly 256 bytes on FREE. Successful and stillborn DIVIDEs must both release the parent's gestation allocation.

## 5. Energetic Contrast at E=500

For the current rich packet (`max_reducible=192`):

- FULL: 256→172, reduction 84, draw = 218.75;
- HALF: 128→86, reduction 42, draw = 109.375.

FULL pays two additional TRANSFORM instruction units but saves `84/640=0.13125` upkeep units after shrinking its allocation. Its net energetic advantage is:

`218.75 - 109.375 - 2 + 84/640 = 107.50625` units per successful forage cycle.

This energy difference is not itself a selection coefficient.

## 6. Fractional-Mean Counterfactual and Discrete-Capture Correction

The following deterministic isolated-parent thresholds scale packet energy to `fE`. They close that fractional-energy ledger, but organisms actually receive one whole E=500 packet or none. The table is therefore retained as a **counterfactual mean-energy diagnostic**, not a partition of the live queue-mediated dynamics.

Executable derivation: `src/derive_efficiency_breakpoints.py`. Preserved output: `efficiency-breakpoints.txt` (seed 123, 2000 ticks per test, 25 bisection iterations).

| Phenotype | Parent survival | ≥1 live offspring/cycle | 2 live offspring/cycle |
|---|---:|---:|---:|
| FULL | f≈0.33767 | f≈0.39467 | f≈0.46185 |
| HALF | f≈0.65826 | f≈0.77226 | f≈0.90661 |

The former interpretation—FULL k=2 versus HALF k=1 at f≈0.852, giving a 3:2 multiplication contrast—is withdrawn before any competition run. Exact first-cycle whole-packet traces give:

| Phenotype | Whole packet captured | Live births | Stillbirths | End reserve |
|---|---:|---:|---:|---:|
| FULL | yes | 2 | 0 | 161.7355 |
| HALF | yes | 2 | 0 | 92.7970 |
| FULL | no | 0 | 2 | 21.6302 |
| HALF | no | 0 | 2 | 22.6602 |

Thus cycle-1 live-birth count is equal conditional on capture. The immediate treatment contrast is post-cycle reserve after a capture; any recruitment difference must emerge through subsequent capture/miss sequences, reserve buffering, survival, or stillbirths. This may be a smaller effect or a mixed recruitment/viability effect. It is not assigned a pre-run `s`.

Capture is discrete and queue-mediated. In a synchronized 155-READ burst with 132 queued packets, scheduler shuffling assigns 132 successes without replacement; later phase dispersion makes success depend on queue occupancy. The `[0.80,0.90)` gate is retained as the registered supply-exposure regime, not called a proven coexistence or k=2:k=1 window.

The operational large-effect threshold `Δlog-odds≥ln(1.5)` remains a minimum effect-size decision rule over the full five-block endpoint; it is no longer presented as a one-cycle mechanistic prediction.

## 7. Drift and Mutation

The value `sqrt(p(1-p)/155)=0.0402` is a **census-binomial reference only**, not an effective-population drift estimate. Cap replacement, parent protection, same-tick pre-emption of scheduled DIVIDEs, newborn displacement, and overlapping ages can make `N_e` substantially lower than 155.

For each block, report per-parent live births and the number of each block-start parent's descendants alive at the next block boundary, with their means and variances. Also report `N/(1+V_k/k̄)` using each definition of k as a descriptive heuristic only. Because generations overlap and survivors contribute directly, this formula is not treated as a formal pre-run `N_e` or used in the confirmation rule.

### Pre-competition sustained-recruitment calibration

Before any mixed run, execute and preserve two mutation-free design calibrations at `p=132/155`, 40 capture cycles, and a fixed 10-cycle burn-in:

1. **Paired iid-capture isolated-parent lifetimes:** 2,000 paired capture schedules per arm, R0=100, offspring removed immediately. Report survival to burn-in, post-burn person-ticks, live births/person-tick, stillbirths/attempt, and death/person-tick. Post-burn rates are explicitly survivor-conditioned and cannot by themselves represent the population age/reserve distribution.
2. **Monomorphic cap calibration:** 20 seeds per arm, N=155, P=11, depth/standing stock=132, otherwise exact assay ecology. Report the same rates plus turnover, pre-emption, memory failures, and reserve distribution. This retains transferred newborn reserves and overlapping ages but is a treatment calibration, not competition evidence.

Let `b_F` and `b_H` be aggregate monomorphic live births per organism-tick after burn-in. Compute the heuristic one-block shift

`Δp_12 = logistic(logit(78/155) + 12(b_F-b_H)) - 78/155`.

This Moran-style conversion is a design approximation, not a measured selection coefficient. Compare `|Δp_12|` with the census reference 0.0402:

- `≥3×0.0402=0.1206`: the 60-tick large-effect assay may proceed if all other gates pass;
- `<0.0402`: do not run the 60-tick confirmatory assay; extend duration or redesign the contrast;
- between 1× and 3×: require a separately preserved simulation-based power calibration before deciding duration.

If either monomorphic arm ceases recruitment or established-organism non-displacement deaths reach 10% of its live births, do not preregister the mixed assay as a clean recruitment-rate test.

#### Registered calibration result and decision

The preregistered calibration was executed before any mixed run. Mutation-free monomorphic results over ticks 124–483 were:

| arm | births / organism-tick | stillbirths / attempt | all-age non-displacement deaths / birth | established-reproducer non-displacement deaths / birth | f | READs / tick |
|---|---:|---:|---:|---:|---:|---:|
| FULL | 0.0880233 | 0.101996 | 0.097682 | 0.003243 | 0.807164 | 13.6299 |
| HALF | 0.0650117 | 0.427677 | 0.657837 | 0.154454 | 0.721890 | 15.2378 |

The heuristic gives `Δp_12=0.0685361`, or 1.7066 census-reference SD, placing duration in the registered power-calibration band. HALF violates the preregistered monomorphic exposure and established-reproducer mortality robustness gates, so P=11 is **NO-GO** and no power calibration or confirmatory seed is launched. “Established reproducer” is now operationally defined as having completed at least one live birth before death. This does not mean HALF would have `f=0.721890` in competition: a mixed population has one shared queue-level f set by combined, composition-dependent demand. The correct diagnosis is that the mixed ecology has not been calibrated and P=11 is not justified by `N/12`.

A mechanistically supported explanation is age-structured demand. Event-level telemetry now measures birth→first valid READ=5.0 ticks and recurrent READ→READ=12.0 ticks in both monomorphic arms. The calibration is consistent with the resulting feedback because HALF makes 15.2378 READ attempts/tick versus FULL's 13.6299 under nearly identical packet supply. No timing-neutral intervention has yet isolated how much of the treatment difference this timing asymmetry causes, so the feedback remains a measured timing asymmetry plus data-consistent causal hypothesis, not a completed causal decomposition. The nominal identity `11×12/155=0.8516` is exact for the initialized first burst but is not the measured sustained ecology.

Extending duration alone cannot repair the present exposure-gate failure. Making birth-to-first-READ timing commensurate with recurrent timing is the cleanest candidate redesign, but it is not proven to be the only one; a different contrast, supply, or cap might reduce turnover demand enough to pass both monomorphic gates. Every alternative requires a fresh calibration and preregistration. Neither 256-versus-192 nor a wider contrast is selected at this stage.

A simple 50:50 average of the two monomorphic demands is 14.4338 READs/tick, implying `f≈11/14.4338=0.7621`; this is only a rough diagnostic because demand changes with composition. It suggests P≈12.27 for f=0.85. With integer P=12, the monomorphic endpoint approximations span f≈0.880 for FULL and ≈0.788 for HALF, so tuning supply alone would produce an f that drifts as composition changes. No P change is adopted from this interpolation.

### Registered timing-closure and mixed-ecology gates for any redesign

Before another confirmatory registration:

1. Instrument age at every valid READ and directly measure birth→first-READ and recurrent READ→READ intervals.
2. In at least 20 mutation-free monomorphic calibration seeds per arm, require:
   - absolute READ demand per organism-tick within 5% of `1/12` in each arm;
   - between-arm READ-demand difference no greater than 5% of `1/12`;
   - realised aggregate f in `[0.80,0.90)` in each arm;
   - allocation failures zero and the population regulator functioning as specified.
3. Then run a disjoint, explicitly non-confirmatory mutation-free 78:77 mixed ecological calibration under the finalized P/cap/timing design. Its seeds and outputs cannot enter the confirmatory evidence set. Require every post-burn F24 estimate to remain in `[0.80,0.90)` and report f against composition by block. If f drifts systematically out of range as ancestry changes, the ecology remains moving and the design is rejected.

Two candidate timing fixes remain unselected. Moving forage to the end of the loop is invalid without a startup guard because newborns would traverse reproduction machinery before first income. Inheriting parental PC is invalid without phase-safe, idempotent initialization because offspring could skip R5/R6 setup or enter mid-bout. Any implementation must pass the gates above rather than being accepted from code structure alone.

#### Tested timing fix: substrate maturation

The tested treatment adds `offspring_maturation_delay=7` as an explicit substrate parameter. It applies identically to every successful offspring and does not alter founders, genomes, PC, registers, provisioning, or ancestry. Native scheduling already prevents execution on the birth tick; the parameter adds seven complete maturation ticks after birth. A newborn remains ACTIVE, owns its 64-byte minimum block, and pays full normal upkeep on the birth tick and seven added ticks, but executes no instruction through `birth_tick+7`. Its first instruction executes at `birth_tick+8`; starting at PC=0, it reaches first READ at age 12, matching the 12-tick recurrent interval.

This is a deliberate ecological design addition, not an implementation convenience. The live parameter header and birth records echo the delay, per-tick telemetry reports the maturing population, and tests prove full upkeep with no premature execution. The original delay-0 calibration is preserved separately.

An initial implementation decremented maturation on the birth tick and therefore produced first READ age 11 and f=1.0 in both monomorphic arms. It is superseded as an off-by-one implementation failure; its raw output is retained under the `efficiency-stochastic-calibration-delay7-offbyone-*` prefix. More generally, equal first/recurrent intervals do not prove demand exactly `1/12` under random pre-READ displacement; realised demand remains an empirical gate.

The corrected 20-seed calibration achieved first READ age=12.0 and recurrent interval=12.0 in both arms but failed the demand and f gates:

| arm | READs / organism-tick | fraction of 1/12 | realised f | all deaths before first valid READ |
|---|---:|---:|---:|---:|
| FULL | 0.0534884 | 0.641860 | 1.000000 | 43,631 / 76,954 = 0.566975 |
| HALF | 0.0657972 | 0.789567 | 1.000000 | 22,526 / 60,219 = 0.374068 |

The lifespan identity `n/(12n-7)` assumes each organism survives to at least one READ and that its lifetime consists of complete READ cycles. Cap displacement violates both assumptions: organisms can contribute upkeep/person-time and then be removed before first READ or between scheduled READs. Using realised organism-time rather than cap slots, the baseline inversion would give effective n≈9.71 FULL and 3.10 HALF, not 11.2 and 3.8, but these are not interpretable mean lifespans under zero-READ and mid-cycle censoring.

Delay 7 is therefore **rejected as a regulator fix**. It remains implemented as an explicit experimental substrate option and its failed calibration is preserved, but it is not part of an approved mixed assay. No common supply repairs it at the registered monomorphic gate: FULL requires `6.6326 ≤ P < 7.4616`, whereas HALF requires `7.9944 ≤ P < 8.9938`; the intervals are disjoint. No mixed ecological calibration is run. A successful redesign must control or analytically include pre-first-demand displacement rather than equalizing intervals alone.

### Empirical capture-response replacement for the withdrawn f gate

The `[0.80,0.90)` target and monomorphic-demand-equality requirement are withdrawn. The former came from a deterministic fractional-energy threshold table that is invalid for all-or-none packet capture; the latter is stronger than a shared-queue mixed assay requires. Delay 0 is restored as the reference implementation for this calibration, not because its regulator is accepted, but because the delay class was falsified.

Before any mixed ecological or competition run, execute a mutation-free paired established-parent response sweep at `p ∈ {0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95}`. For each p use 2,000 paired trials, common Bernoulli capture schedules within each FULL/HALF pair, 40 planned cycles, and a 10-cycle burn-in. Offspring are removed before execution; therefore this calibration measures established-parent recruitment and mortality only—not offspring establishment, population equilibrium, or competition.

For every p and arm report total post-burn live births / total post-burn parent person-ticks, DIVIDE attempts, stillbirths, capture fraction, survival to burn/end, post-burn parent deaths/live birth, and paired bootstrap 95% intervals for `Δb=b_FULL-b_HALF` using trial pair as the resampling unit. A candidate recruitment operating point must have positive Δb and post-burn established-parent deaths/live birth `<0.10` in both arms. Among qualifying grid points, the provisional candidate is the p with largest Δb; ties within numerical precision choose the lower p. This rule chooses a response location, not P: a later queue calibration must map shared rolling f to composition and test population-level established mortality with disjoint seeds.

If no p qualifies, conclude only that no recruitment-dominated operating point was found on this registered established-parent grid. Do not generalize to offspring viability or the entire continuous f range without cohort/ecological calibration. No contrast change, P selection, mixed calibration, or competition is authorized by this sweep alone.

#### Registered response-sweep result

| p | b FULL | b HALF | Δb | paired-bootstrap 95% CI | parent deaths/live birth FULL; HALF |
|---:|---:|---:|---:|---:|---:|
| 0.60 | 0.140163 | 0.092397 | 0.047766 | [0.034729, 0.064668] | 0.05224; 0.57292 |
| 0.65 | 0.146530 | 0.104698 | 0.041832 | [0.032834, 0.053059] | 0.03582; 0.42308 |
| 0.70 | 0.151650 | 0.112051 | 0.039599 | [0.032895, 0.048247] | 0.02361; 0.32857 |
| 0.75 | 0.156297 | 0.118371 | 0.037926 | [0.032987, 0.043774] | 0.01376; 0.24764 |
| 0.80 | 0.160085 | 0.130641 | 0.029443 | [0.026183, 0.033252] | 0.00732; 0.15909 |
| 0.85 | 0.163232 | 0.138757 | 0.024475 | [0.022556, 0.026721] | 0.00317; 0.10865 |
| 0.90 | 0.165302 | 0.147954 | 0.017348 | [0.016252, 0.018599] | 0.00098; 0.06495 |
| 0.95 | 0.166363 | 0.157498 | 0.008865 | [0.008340, 0.009425] | 0.00014; 0.02821 |

By the registered rule, p=0.90 is the provisional response point; p=0.95 also qualifies but has smaller Δb. This does not establish a clean population regime: HALF survival to burn/end at p=0.90 was 0.5085/0.0205 despite deaths/live birth passing, showing that the ratio is diluted by births from the surviving parent-time. The rough delay-0 mixed band p≈0.76–0.81 has a clear positive recruitment contrast but lies in the registered viability-mediated region because HALF parent deaths/live birth exceeds 0.10 at p=0.75 and 0.80. A population/cohort calibration must therefore test offspring establishment and established survival near p=0.90 before any P choice or mixed assay.

The response shape identifies miss tolerance as the measured mechanism: FULL b changes only 0.140163→0.166363 across p=0.60→0.95, HALF changes 0.092397→0.157498, and Δb declines monotonically 0.047766→0.008865. This supports a coupled recruitment–viability channel in which reserve shortfall after misses can cause both skipped births and death. It does not prove inseparability over every continuous p: the grid is finite and offspring cohorts were not followed.

The reported post-burn rates are survivor-conditioned. A trial that died before burn contributes zero births and zero person-time; among HALF trials, survival to burn ranged from 0.0275 at p=0.60 to 0.731 at p=0.95. Capture-fortunate survivors are therefore overrepresented, plausibly attenuating the FULL−HALF contrast, especially at low p, but the direction and magnitude of that bias are not identified by this sweep. All inception-cohort survival fractions must accompany b; do not call b an unconditional cohort rate.

Add p=1.00 as an explicitly post-hoc no-miss mechanism control using the same 2,000 paired trials, 40 cycles, 10-cycle burn, mutation-off settings, and all-capture schedule. It is not eligible to change the registered p=0.90 selection rule. Falsification condition: if FULL and HALF recruitment do not converge at p=1.00, miss tolerance alone is insufficient and a residual treatment difference must be diagnosed.

**Post-hoc control result:** FULL and HALF both produced exactly b=1/6 live births/parent-tick, Δb=0 with paired-bootstrap interval [0,0], zero stillbirths/deaths, and survival to burn/end=1.0. Together with monotonic Δb→0 as p increased, this confirms miss tolerance as the established-parent recruitment mechanism over the tested capture process. It does not by itself establish that recruitment and viability are inseparable in reproducing populations or offspring cohorts.

### Three-bout architectural capacity trace

The p=1 equality is conditional on the two-bout genome ceiling. Before any population design, test whether surplus extraction can fund an additional complete reproduction bout. Use the same FULL/HALF treatment, E=500, τ R5=51, mutation off, one isolated parent, deterministic capture of every READ, and 200 cycles. Replace the two-bout genome with three fresh `ALLOC_OFFSPRING→COPY_BLOCK→DIVIDE` sequences. The genome length becomes 17, R6 must equal 17 after initialization, and the recurrent interval becomes 15 ticks. Offspring are removed before execution; this is an architectural capacity trace, not selection evidence.

Report every DIVIDE attempt's reserve before transfer, transfer, reserve after transfer, success/stillbirth, cycle, peak committed memory, parent death, and allocation failures. Primary gate on the last 50 complete cycles: FULL exactly 3 live births/cycle and HALF exactly 2. Also report whether HALF makes a third live birth or attempts a third stillbirth. If FULL does not sustain three or HALF also sustains three, the proposed 3-vs-2 contrast is falsified at τ=51. If the unconditional HALF third attempt stillbirths, do not call the resulting genome clean fecundity; a separate preregistered equal-tempo conditional third-bout genome is required before population calibration.

**Result:** the primary and clean-fecundity gates failed. Across every one of the last 50 cycles, FULL made 3/3 live births with zero stillbirths, while HALF attempted three but made 1 live birth and 2 stillbirths. Both parents survived, f=1, allocation failures were zero, and steady cycle-end reserves were 129.419 FULL and 15.946 HALF. The unconditional third attempt drains HALF enough to suppress its next cycle's second birth; this is not clean 3-vs-2 recruitment.

Register one conditional capacity trace before any population work. Both treatments receive the same 23-instruction genome. The following values were the registered expectation and are retained as a failed-design record, but were numerically wrong for E=500: after two complete bouts, compute `R7=R4−656`; expected HALF R4=656 would take a JUMPZ branch through three executed NOPs, while expected FULL R4=1312 would execute a fresh third `ALLOC_OFFSPRING→COPY_BLOCK→DIVIDE`. Each intended path has exactly 17 recurrent ticks, and both copy the same 23-instruction genome, so tempo and **per-copy genome-length cost** are matched; FULL intentionally pays one additional copy per cycle. Use E=500, τ=51, p=1, mutation off, 200 isolated-parent cycles, and the same last-50-cycle gate: FULL exactly 3, HALF exactly 2, zero stillbirths/deaths/allocation failures, identical recurrent intervals. If this fails, stop; do not tune τ or thresholds post hoc.

**Treatment-verification failure:** the conditional trace used incorrect E=300-scale expectations. At live E=500, HALF expressed R4=1093 rather than 656 and FULL expressed R4=2187 rather than 1312. HALF therefore computed `R7=437`, bypassed JUMPZ, and executed the third bout. HALF then produced 1–2 live births with 1–2 stillbirths and died after nine complete cycles, while FULL sustained 3 live births. This run does not test the intended conditional architecture. Per the registered stop rule, threshold 1093 was not substituted into the equality design and the trace was not rerun in that form. The failed artifact is retained. Current evidence at this historical checkpoint established only that FULL surplus could fund a third complete bout and that the unconditional genome was not clean; the later bit-test registration and result supersede that design status.

**New user-directed structural correction:** the equality test itself is rejected, not retuned. `SUB` followed by `JUMPZ` implements exact equality and cannot express a robust threshold; unsigned wrap also does not supply an ordering branch. Replace instruction 13 with `AND R7,R4,2048`, retain `JUMPZ R7,19`, and otherwise leave the 23-instruction equal-tempo genome unchanged. At the intended E=500 rich treatment, bit 11 should be set for FULL R4≈2187 and clear for HALF R4≈1093. Before accepting the fecundity gate, log R4 min/max and unique values over all 200 cycles and require `(FULL R4 & 2048)=2048` on every cycle and `(HALF R4 & 2048)=0` on every cycle. Also require measured recurrent READ intervals exactly 17 ticks in both arms, FULL 3 and HALF 2 live births in every last-50 cycle, and zero stillbirths/deaths/allocation failures. Failure stops the design; no mask, τ, or contrast tuning follows.

**Result as originally classified:** all registered isolated-parent gates passed under the implemented `OFFSPRING_TROUGH=18`. Across all 200 cycles, FULL R4 was exactly 2187 with bit 2048 set and HALF R4 exactly 1093 with that bit clear. Both measured recurrent READ intervals were exactly 17 ticks. FULL instantiated 600/600 offspring (3 every cycle); HALF instantiated 400/400 (2 every cycle); neither arm had a code-classified stillbirth, parent death, or allocation failure. End reserves were 123.823 FULL and 57.900 HALF. An independent source/raw-event audit verified the path lengths, recomputed the unconditional event tails, and closed the per-step memory ledger exactly (`committed = live allocations + corpse allocations`; peak 384 FULL and 320 HALF). The cleaned runner requests the realised stream rate 1 directly; removing its earlier redundant manual packet injection left corrected artifacts byte-identical.

**Post-hoc threshold audit and reclassification:** `OFFSPRING_TROUGH=18` does not cover the live cost to first extraction under normal newborn scheduling. The exact spend through the READ tick is 20.0, so exact arithmetic requires initial reserve strictly greater than 20 because death occurs at `<=0`. Literal 20.0 reaches extraction in the current Python-float implementation only because a positive residue of about `3.22e-15` remains; it is an implementation-measured boundary, not a robust mathematical threshold. Reserves 18.0–19.9 execute a valid READ but die before TRANSFORM. FULL's 600 transfers were all ≥29.870. HALF's 400 instantiations included 195 second-bout transfers <20 (cycles 6–200; steady 19.4297), including every second bout in the final 50 cycles. The prior `1/17` clean viable-fecundity interpretation is withdrawn. The artifact measures differential instantiation/reproductive allocation under the configured threshold, not established recruitment. Raising the implemented threshold to 20 would create 195 HALF stillbirths and, under a cap, remove corresponding displacement events; therefore it is a mechanism change requiring rerun, not a retrospective relabeling. Source and output: `src/trace_offspring_first_extraction_threshold.py` and `offspring-first-extraction-threshold-summary.json`.

### Mutation-free capped-population calibration for the conditional genome

This stage measures turnover, lifetime reproductive variance, and memory safety before any mixed-population selection run. It is monomorphic calibration only and cannot establish ancestry selection.

**Treatments and fixed seeds:** five FULL monocultures with seeds 61001–61005 and five HALF monocultures with seeds 62001–62005. Each starts directly at N=155 with 155 founders carrying the same 23-instruction conditional genome except for audited transform extent 256 versus 128. Use E=500 monotonic-rich packets, τ R5=51, mutation rates zero, offspring maturation delay zero, population cap 155, P=20 packets/tick, buffer depth 340, initial queue 340, and 2,040 ticks. No mixed seed is authorized by this calibration registration.

**Timing sanity check, not a gate:** seeded founders in the isolated trace execute at tick 0 and place successful bouts at logged ages 9, 12, and 15 for FULL and 9 and 12 for HALF. A population-born offspring cannot join the scheduler snapshot in its birth tick, so the nonregistered runner smoke test places its corresponding bouts at ages 10, 13, and 16 or 10 and 13, recurring every 17 ticks. The cohort-relevant constant independent-hazard approximation therefore solves `(exp(-10d)+exp(-13d)+exp(-16d))/(1-exp(-17d))=1` for FULL and `(exp(-10d)+exp(-13d))/(1-exp(-17d))=1` for HALF, giving d≈0.10187 and 0.08455 (mean lifetimes ≈9.82 and 11.83 ticks). These replace the inapplicable assumption that first reproduction occurs at age 17. They are not predictions to be fitted: parent protection, discrete within-cycle bouts, newborn displacement, and same-tick ordering violate the independent-hazard model.

**Cohort:** exclude founders. Include every organism born in ticks `[170,340)`, then follow through fixed tick 2,040. Classify each as death with complete lifetime or right-censored alive at endpoint. No adaptive extension is allowed. The calibration is lifecycle-inconclusive if either treatment has >1% unresolved cohort members or fewer than 1,000 cohort births across its five seeds.

For each seed and pooled by treatment, retain and report:

- logged age at first valid READ and first live birth;
- death age/cause/stage and fraction ever completing a live birth;
- complete-lifetime live births `k`, mean k, population variance `V_k`, and its full empirical distribution;
- mean/median lifetime and censoring fraction;
- live births, DIVIDE attempts, and stillbirths per organism-tick;
- live-birth probability conditional on DIVIDE attempt;
- live cap displacements, non-displacement deaths, and parent-protection/victim events;
- the descriptive variance heuristic `Ne_var = 155/(1 + V_k/mean(k))`, only when mean(k)>0. This is not a formal overlapping-generation effective population size or a power result;
- per-tick N, queue occupancy, valid READ attempts/captures, free shared pool, live allocation bytes, corpse allocation bytes, total committed bytes, and cumulative allocation failures.

**Mechanical validity gates, applied independently to every seed:**

1. realised packet energy/rate/buffer/cap/mutation/treatment values match this registration;
2. N=155 after every completed tick;
3. every valid READ captures a whole packet (`f=1`) and invalid READ attempts are zero;
4. stillbirths and non-displacement deaths are zero;
5. memory allocation failures are zero, minimum free pool is at least 8,192 bytes, and the per-tick ledger closes exactly: `initial_pool = free_pool + live_allocations + corpse_allocations`;
6. realised FULL R4 always has bit 2048 set and HALF R4 always has it clear;
7. all raw birth, DIVIDE, death/ancestry, cap-replacement, READ, and per-tick memory records are preserved with source hashes and realised parameters.

Failure of any mechanical gate is NO-GO for a mixed assay. Passing permits design of—not execution of—a separately preregistered mixed selection/power calibration using measured cohort `V_k`, censoring, and turnover. The isolated-parent capacity claim and any later population-selection claim remain separate.

**Status: INVALIDATED / NO-GO before the planned standalone run.** During independent design review, the reviewer executed exploratory one-seed diagnostics using FULL seed 61001 and HALF seed 62001. Those seeds are consumed and cannot be reused as blind registered seeds. At f=1, FULL/61001 had 401 reserve-exhaustion deaths over 2,040 ticks. HALF/62001 had 6,387 reserve-exhaustion deaths, 12,040 stillbirths, and endpoint N=150. Gates 2 and 4 therefore fail; the current conditional architecture does not yield a pure fecundity population process. The mechanism is a lifecycle difference absent from the isolated-founder trace: offspring do not enter the scheduler snapshot on their birth tick but do pay birth-tick upkeep, then face a variable pre-first-READ reserve trajectory. No remaining registered seeds were run, and no mixed run is authorized. The failed protocol, draft runner, available review evidence, and seed-contamination record are preserved under `failed-designs/2026-07-28-conditional-population-calibration-no-go/`.

The review also found that the proposed end-of-tick memory record would miss within-tick low-water marks; ecology-wide end-of-tick census is not an execution-opportunity denominator; mutation-off is not yet a first-class runtime/readback parameter; cohort completeness must pass per seed; and `155/(1+V_k/mean(k))` must be called an ad hoc variance-discount index rather than Ne. These defects cannot rescue the failed lifecycle gates. The later threshold audit further shows that HALF's nominally successful second offspring were commonly below the true first-extraction requirement. Together with the shorter-than-cycle equilibrium lifespan and earlier capture-response coupling, this terminates the clean-fecundity assay program under current reserve/transfer/cap semantics. The isolated-parent record is retained only as reproductive-allocation capacity. No threshold, τ, supply, cap, or mixed-population retuning is authorized.

### Legitimate viability-mediated outcome

After timing and exposure gates pass, differential non-displacement mortality is a substantive result, not a null. Classify the outcome as:

- **recruitment/fecundity-dominated** only if both arms remain exposure-valid, live recruitment differs, and established-organism non-displacement mortality remains below 10% of live births in each arm;
- **viability/survival-mediated** if exposure is valid but differential reserve-related non-displacement mortality accounts for the ancestry change;
- **mixed recruitment and viability** if both components materially differ.

Telemetry now stratifies deaths as pre-first-READ, post-READ/pre-first-live-birth, and post-first-live-birth (established reproducer), and records age/interval for every valid READ. Income→survival is an affirmative mechanism outcome consistent with the §5e hypothesis, not evidence that the treatment had no effect.

For L=14:

- probability of at least one copied-instruction substitution = 0.013909;
- probability of any substitution/insertion/deletion/duplication = 0.034499 per offspring.

At every TRANSFORM, log resolved opcode and extent after register lookup. Classify the latest execution as FULL only for `(RLE,256)`, HALF only for `(RLE,128)`, MUTANT/OTHER otherwise, and UNCLASSIFIED before any transform. Report phenotype, treatment ancestry, and ancestry→phenotype conversion separately.

## 8. Direct-Cap Primary Endpoint

For each tick, define:

`F24(t) = sum(successful captures) / sum(valid READ attempts)`

over ticks `t-23...t`; it is undefined when the denominator is zero.

The population is already at cap at t=0. All synchronized founders execute their first READ at tick 4, before any TRANSFORM or DIVIDE. Define the fixed primary interval:

- `t_start=4`, immediately after the first READ and before the first treatment expression;
- `t_end=63`;
- five cycle-aligned blocks: 4–15, 16–27, 28–39, 40–51, and 52–63.

This gives five complete ecological READ→TRANSFORM→two-bout blocks with no growth-to-cap or queue-drain history. They are **not assumed to be five discrete generations**. Births within a block can displace founders, older descendants, newborns, or organisms scheduled to DIVIDE later in the same tick; parent protection applies only during the parent's own birth event. Generational overlap and realised turnover are measured below. The interval is never shifted.

### Frequency definitions

The confirmatory intention-to-treat frequency is `p_FULL_ancestry = living FULL-ancestry / all living`; its registered starting value is 78/155. The realised-phenotype frequency is `FULL/(FULL+HALF)` among living organisms whose latest executed phenotype is one of those two; MUTANT/OTHER and UNCLASSIFIED are excluded from that denominator but reported separately as fractions of all living organisms. Ancestry→phenotype conversion is always reported.

For counts F and H, define the fixation-safe Haldane log odds `L_H=ln((F+0.5)/(H+0.5))`. The confirmatory endpoint is always `ΔL_H=L_H(t=63)-L_H(t=4)`, including fixation; it is not moved to an earlier favourable tick. Also report the last tick at which both ancestries are present and the corresponding `L_H` as a predeclared secondary coexistence descriptor.

### Run-validity gate

A seed tested the intended regime only if all conditions hold:

1. live readback before tick 0 shows N=155, 78 FULL and 77 HALF founders, all reserve=100 and PC=0, with 132 queued packets;
2. N remains 155 through tick 5 and all founders have expressed their registered transform by tick 5;
3. aggregate captures/valid READs over ticks 4–63 lie in `[0.80,0.90)`;
4. F24 lies in `[0.80,0.90)` on at least 36 of the 41 ticks 23–63;
5. N is at least 150 on at least 54/60 primary ticks;
6. both realised FULL and HALF phenotypes are present at tick 5;
7. the cumulative memory-allocation-failure counter remains zero through tick 63.

A seed failing any gate is a **regime failure**, not evidence for or against the efficiency channel. Realised f, rather than `132/155`, is authoritative.

Primary measurements are:

1. Haldane-corrected change in FULL-ancestry log odds from ticks 4 to 63, plus raw counts/frequency;
2. realised-phenotype frequency and ancestry→phenotype conversion;
3. attempted DIVIDEs, live births, and stillbirths per 100 phenotype-specific organism-ticks;
4. live-birth recruitment-rate ratio FULL/HALF;
5. live displacement, dead-vacancy fill, reserve-exhaustion, and other deaths;
6. F24, N, queue depth, free/committed memory, and allocation failures;
7. births, live displacements, vacancy fills, block-start survival, and newborn-to-next-boundary survival in every block.

**Support for a large realised-recruitment advantage:** at least 4/5 seeds pass the validity gate; in at least 4/5 total seeds Haldane-corrected FULL-ancestry `ΔL_H` is at least `ln(1.5)=0.4055`, the realised FULL/HALF live-birth-rate ratio is at least 1.2, and the mechanism conditions below hold.

**Absence of the registered large advantage:** in at least 4/5 valid seeds Haldane-corrected `ΔL_H` is at most `ln(1.1)=0.0953`, the live-birth-rate ratio is at most 1.1, and both phenotypes continue producing live offspring. This rejects the operational large-effect criterion, not every possible small channel.

Anything else is inconclusive.

## 9. Mechanism Audit Within the Capped Regime

### Timestamped events

Every DIVIDE attempt is logged with tick, parent ID, immutable ancestry, founder lineage, resolved latest transform, attempt number, success, stillbirth status, offspring ID, reserve before/after transfer, and realised transfer. Every cap event logs the parent and victim plus whether the victim was live or an already-DEAD dictionary entry.

### Recruitment decomposition

The two founders execute DIVIDEs at the same genome positions. The observed live-birth rate is decomposed as:

`live births / organism-tick = DIVIDE attempts / organism-tick × P(live birth | attempt)`.

A contrast in the second factor is expected to operate through reserve transfer and the hard offspring trough. If differential stillbirth probability drives the result, describe the mechanism as **income→offspring viability→realised recruitment**, not pure DIVIDE tempo or viability-independent fecundity. Stillbirths are therefore a measured mediator, not silently omitted from the mechanism audit.

For each 12-tick block and realised phenotype, report organism-ticks, valid READs, captures, DIVIDE attempts, live births, stillbirths, live displacement deaths, dead-vacancy fills, reserve-exhaustion deaths, and other deaths.

### Turnover and pre-emption

For every block, identify the living IDs at block start and report: fraction still alive at block end; fraction displaced live; fraction dying otherwise; total live births; fraction of within-block newborns alive at the next boundary; and scheduled DIVIDE attempts lost because the organism was removed before execution. The founder survival fraction is reported after block 1. A block is called a complete generational turnover only descriptively if no block-start organisms survive; this is not assumed from births exceeding N.

A block is HALF-exposed with at least 60 HALF-phenotype organism-ticks. The result is recruitment-rate-resolved only if:

- HALF produces at least one live offspring in every HALF-exposed block up to and including its last HALF-exposed block;
- the FULL/HALF live-birth-rate ratio is at least 1.2 over the primary interval;
- non-displacement deaths of established organisms are fewer than 10% of live births for each phenotype;
- Haldane-corrected FULL ancestry log odds rise by at least ln(1.5).

HALF loss is classified as **rate-driven displacement** if HALF produced live offspring in every HALF-exposed block through its last such block, established-organism non-displacement deaths remained below 10% of HALF live births through disappearance, and the terminal HALF-ancestry losses were live cap displacements rather than reserve/other deaths. Later blocks with fewer than 60 HALF organism-ticks do not fail the gate merely because HALF is already too rare or absent.

If HALF stops producing live offspring while still present with at least 60 organism-ticks in a block, classify that interval as reproductive exclusion. If established-organism non-displacement deaths reach 10% of births, classify the mechanism as mixed recruitment/established viability. Always report attempt-rate and stillbirth-probability contrasts separately.

### Cohort

Define a primary cohort from live births during ticks 4–27. Follow each to death or first successful DIVIDE. Living unresolved organisms at t=600 are censored, not failures. Report survival, time to DIVIDE, reserve/trough ratio, and pre-DIVIDE deaths by cause separately by realised phenotype and ancestry.

## 10. Secondary Checkpoints

Report t=200 and t=600 ancestry and realised-phenotype frequencies, F24, attempt/live-birth/stillbirth rates, live displacement versus vacancy fill, and established deaths by cause. Later loss of HALF can result from differential recruitment under cap even while its remaining organisms are physiologically viable.

For continuity, report whether FULL ancestry is ≥0.90 at t=200 and ≥0.95 at t=600, but keep these secondary. They cannot replace a failed primary regime-validity gate.

### Saturation-triggered follow-up

Define early saturation as FULL-ancestry fixation by the end of block 3 (tick 39) in at least 4/5 valid seeds. If this occurs through the registered rate-driven-displacement path, interpret the current assay as establishing only a coarse treatment contrast. Before additional confirmatory replication, design a narrower extraction contrast; FULL 256 versus partial 192 is a candidate, not a pre-approved treatment. It requires a fresh exact transform/energy ledger, whole-packet capture/miss traces, effect-size registration, and its own hashes before any run.

## 11. Reporting

Save the exact runner and raw output under `/opt/data/avida-life/`, including source hashes, mtimes, seeds, live headers, per-tick capture/queue records, phenotype and ancestry counts, timestamped DIVIDE records, cap replacement/vacancy records, birth records, and death records. Report this as seeded direct competition, never de novo convergence.

The separate τ competition remains limited to: τ≈20% defeated seeded 10%, 40%, and 70%, bracketing an interior optimum between 10% and 40%. It neither demonstrates convergence nor locates the optimum.
