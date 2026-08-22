# Stage 7B2 Preregistration: Confirmatory Parameter Registration — Per-Genotype Invasion Growth under Registered Exogenous Hazard

**Protocol status:** SUPERSEDING preregistration, committed under the post-PASS gate of `stage-7b1-preregistration.md` §9.5. The Stage 7B1 deterministic mechanics verification PASSed 24/24, was retained as `results/stage7b1/stage7b1-result.json` (SHA-256 `d1feb0fd07636b16f54f773c9b75932480c29dec2274134d8e3d95483809bedd`, 6,127 bytes), and carries its classification inline (`decision: PASS` plus the runner-frozen `decision_scope` limiting it to mechanism verification). That satisfies the sole precondition the 7B1 preregistration set for this document. This document fixes the deferred Blocker 3/5/6 parameters — `r`, `d`, `N`, window length `W`, replicate count `k`, minimum contrast `Δr_min`, hazard arms, and solver resolution `ρ_r` — and registers how the §6.1 endpoint definitions of the 7B1 preregistration will first be exercised. It supersedes the deferral itself; corrections require a further superseding preregistration, never edits here.

**Evidence-era disclosure:** observed before this freeze: the Stage 7B0 PASS pair (ten gates, byte-reproducible, `results/stage7b0/stage7b0-result.json` SHA-256 `00315fab…ebddf`) at `A∈{102,204}`, `T=128`, `D=255`; the Slice 2A mechanics harness including a seeded per-member Bernoulli hazard path (`hazard_rate`, `hazard_seed`) alongside scripted schedules; the frozen 7B1 transaction/retirement/death/shadow machinery (`stage7b1_mechanics.py`, pre-execution-manifest-frozen at `62f2672`) with `REGISTERED_PACKET_RATE=5`, `corpse_ttl=2`, and side-effect-free `would_admit` counters. **Never observed anywhere in project history:** any stochastic population execution under split reserves; any invasion-growth or reproductive-value number; any `l_x`/`m_x` measurement; any `would_admit` counter value at population scale; any multi-generation establishment trace. No fitness, selection, optimum, or ESS claim exists in any Stage 7 artifact.

**Authorisation:** this document registers decisions only. It authorises no execution. As with every prior protocol, implementation code may be written after this commit, but the implementation, runner, tests, output schema, reducer, and analysis script must be frozen **together** with a pre-execution manifest (`df7b1f5`/`e2f580b` precedent) at `results/stage7b2/pre-execution-manifest.json`, committed before any retained run. Mutation remains unauthorised in every form; this protocol contains no mutation kernel because no mutation runs.

## 1. Registered question

Under one registered ecology with exogenous phenotype-blind hazard and binding vacancy admission, do the two carried allocation strategies `A=102` (`α=102/255`) and `A=204` (`α=204/255`) differ in per-genotype invasion growth `r_g`, as defined by the 7B1 §6.1 endpoint, by at least the registered minimum contrast `Δr_min` across `k` seeded replicates?

The estimand is the per-genotype replicate **distribution** of certified rational brackets `[r_lo, r_hi]`. No optimum, ESS, background-invariant causal effect of α, or external-validation claim about the textbook mortality–allocation mechanism is registered, tested, or permitted. Single-hazard design: any interpretation of outcomes as a mortality-only α response is prohibited; if hazard-related language is ever used, outcomes must be labelled combined mortality–turnover responses per 7B1 §6.2.

## 2. Registered configuration (Blocker 3 parameters)

| Parameter | Registered value | Registration rationale |
|---|---|---|
| Packet rate `r` | 5 packets/tick | Carries the only packet regime any Stage 7 code has been verified under (`REGISTERED_PACKET_RATE`, frozen 7B1; Slice 2A provisional constant). |
| Buffer depth `d` | 64 packets, uniform in every run | Open-population configurations fall back to no-eviction layers 1–2 per 7B1 §4.2: the `BUFFER_OVERFLOW` runtime guard raises rather than drops, and `buffered ≤ d` is asserted inside the tick-complete closure. Any trigger classifies the run `INVALID IMPLEMENTATION`. `d` is identical across replicates and genotypes; it is an engineering bound, not a treatment. |
| Census capacity `N` | 12 | Exactly twice the founding census, so growth saturates early enough that binding admission and vacancy capture are exercised, symmetrically for both genotypes. |
| Window `W` | 600 ticks | Right-censoring makes `W` a precision knob, not a validity knob. Expected founder lifespan under the registered hazard is 120 ticks, so 600 gives five expected lifetimes of headroom for F1→F2 establishment events. |
| Hazard arms | exactly one: `h = 1/120` per live member per tick | Age-independent, phenotype-blind Bernoulli draw per member per tick from the replicate's seeded stream (the existing Slice 2A mechanism). One level standardises exposure without invoking the deferred multi-arm directional prediction of architecture §9.5, whose gates 1–5 (including factorial separation of hazard exposure and recruitment opportunity) have not been run. |
| Replicates `k` | 32 | Each replicate is one complete population run; runs differ **only** in hazard stream seed. Seed derivation is fixed: `hazard_seed = 20260822 + i` for replicate index `i ∈ {0,…,31}`. Both genotypes are co-resident in every replicate, so contrasts are paired. |
| Solver resolution `ρ_r` | bracket width `1/256` per tick | Far below `Δr_min`, so solver discretisation cannot mask the registered contrast. Analysis-side interval arithmetic only; approximations never enter any ledger (7B1 §8). |
| Minimum contrast `Δr_min` | `1/100` per tick | Registered floor for declaring an allocation-associated invasion-growth difference. Its adequacy is not retuned after seeing data: an observed spread that leaves the contrast undecidable yields the registered outcome class `NO_ESTABLISHED_CONTRAST`, which is a legitimate preregistered result, not a failure to be repaired by widening or narrowing the floor. |
| Genotypes | `(A,T,D) ∈ {(102,128,255), (204,128,255)}` | Exact continuation of the retained 7B0 channel lineage, enabling the mandated calibration of measurement code against retained blocks. The two strategies differ only in `A` (trait-isolation gate); the coarse interior of the `A/D` lattice is deliberately unexplored — this assay makes no claim about landscape shape between or beyond the two registered points, and interior resolution sensitivity remains deferred. |
| Founders | 3 per genotype (6 total), age 0, `S=100`, `R=0` | Opening state is the registered Stage 7B0 INITIAL checkpoint value (`parent_S=100/1`, `R=0`), keeping founder injection continuous with the calibrated lineage. Founder `S` inputs are logged external sources; offspring receive only committed `S_birth=P`, `R_birth=0`. Distinct immutable ancestry IDs. |
| Programme/schedule/tempo | identical scripted equal-tempo programme across genotypes and replicates | Same registered programme family as the 7B0 blocks, extended through the frozen 7B1 DIVIDE transaction stages `G…C`. Scheduler order, packet stream, and admission tie-breaking are deterministic given the hazard stream; the hazard stream is the **only** stochastic source, which makes the replicate definition exact. |
| Corpse TTL | 2 ticks (carried frozen constant) | Unchanged from Slice 2A/7B1 registrations. |

**Implementation-window calibration precondition (pre-freeze, non-retained):** during implementation, exploratory shakedown runs (which produce no retained artifact, per the disclosed 7B1 precedent) must demonstrate within `W`: at least one offspring first-reproduction event, and at least one binding admission under saturated census with a nonzero `would_admit` counter. If the registered parameters cannot exhibit both, a superseding preregistration must revise them **before** the freeze; discovering the problem after freezing invalidates the freeze, not the parameters' post hoc adjustment.

## 3. Registered estimators (Blocker 5 mechanics)

All quantities are exact `Fraction` values derived exclusively from event-ledger records. No imputation of any kind exists.

- **Genotype membership:** mutation is disabled, so `(A,T,D)` is preserved exactly by inheritance; genotype `g` membership is exact by ancestry.
- **Exposure:** member-ticks are attributed to the member's genotype and attained age; deaths contribute exposure up to and including the death tick; right-censored members (alive at window end) contribute exposure through tick `W`.
- **Survival schedule:** with `C_g` the set of genotype-`g` members ever alive in the replicate, `l_x(g) = |{members attaining age ≥ x}| / |C_g|` — an exact fraction of counted individuals.
- **Establishment rule (binding, per 7B1 §6.1):** an establishment event is an offspring's **first reproduction**; the birth of an offspring that never (yet) reproduces confers no `m_x` credit. Credit is assigned to the parent at the tick of each offspring's first reproduction, at parent age `x` equal to the parent's attained age at that tick. `m_x(g) = (# establishment events with a genotype-`g` parent of age exactly x) / |C_g|`.
- **Censoring (binding, per 7B1 §6.1):** right-censor at tick `W`; censored members contribute exposure and survival counts but no `m_x` events; offspring unborn or unreproductive by `W` confer no credit; nothing is projected, weighted, or imputed beyond the window.
- **Mediators (reported, never substituted for the endpoint):** realised `Y`, `Y_S/Y_R` split, age at fundable bout, attempt/vacancy exposure, committed `P`/`S_birth`, first extraction, first reproduction, subsequent reproductive contribution — each separately distinguishable in output per 7B1 §6.1 causal-chain telemetry. Bout-completion rate (intrinsic) and vacancy-capture rate (ecological) are reported separately from `would_admit` shadow counters; their product is realised recruitment (Blocker F decision).

## 4. Registered solver contract

For each replicate × genotype with at least one establishment event:

1. Compute the exact rational coefficient vector `c_x = l_x(g)·m_x(g)` for `x = 0…W`.
2. **Subcritical precondition:** compute `L(0) = Σ c_x` exactly. If `L(0) ≤ 1`, the genotype-replicate is classified `SUBCRITICAL` and emits **no numeric** `r_g`; this is a registered outcome shape, not an error. Persistence without established reproduction confers no endpoint credit (sterile founders and `R` hoarders gain nothing by census presence).
3. Otherwise solve `L(r) = 1`, i.e. `Σ c_x e^{−rx} = 1`, by monotone sign bisection. Monotonicity is structural: `c_x ≥ 0` with finite support and some `c_x > 0` makes `L(r)` strictly decreasing in `r > 0`, so the positive root is unique.
4. Exponential evaluation inside the solver uses rigorous enclosures (directed-rounding interval arithmetic with a registered minimum of 32 decimal guard digits, or rational power-series bounds). Bracket endpoints are emitted as exact rationals with certified containment and width `≤ ρ_r = 1/256`. Every bracket record embeds `{r_lo, r_hi, width, iterations, L0_exact}`. Approximations never feed back into any ledger.
5. Primary statistic per genotype: the median (even-k convention: lower middle of the sorted midpoints) of replicate midpoints `(r_lo+r_hi)/2` over supercritical replicates. Paired differences `Δ_i` are taken over replicates where **both** genotypes are supercritical ("complete pairs").

## 5. Registered decision rule (Blocker 6 contrast)

Applied exactly once, after all 32 replicates reduce; classes are exhaustive:

- `DEGENERATE_REPLICATION` — fewer than 16 of 32 replicates yield complete pairs. No contrast conclusion; distributions reported descriptively; triggers repair-policy review of the registration (a further superseding preregistration), never post hoc reinterpretation.
- `ESTABLISHED_CONTRAST` — at least 16 complete pairs and the absolute median paired difference `|median_i Δ_i| ≥ Δr_min = 1/100`. The sign is reported descriptively. This establishes an allocation-associated invasion-growth difference at or above the registered floor under the registered ecology; it does **not** establish the architecture §9.5 external-validation mechanism, an optimum, or an ESS.
- `NO_ESTABLISHED_CONTRAST` — at least 16 complete pairs and the median paired difference below `Δr_min`. A legitimate preregistered outcome.
- `ONE_ARM_SUBCRITICAL` / `BOTH_SUBCRITICAL` — a genotype with `L(0) ≤ 1` in at least 16 of its 32 replicates is reported subcritical at this ecology; the other class applies when both are. These coexist with the pair-count classes above and are reported alongside them.

Every outcome class is reportable; none is retroactively reclassified. The reducer implementing this rule is source-frozen before execution.

## 6. Calibration/confirmatory separation

Measurement and reduction code is (i) calibrated against the retained 7B0 blocks — replaying their event streams through the new ledger-closure identities must reproduce the registered closures — and (ii) unit-tested against hand-computable known-answer schedules whose Euler–Lotka brackets can be independently bounded. The confirmatory configuration, seed table (`20260822 + i`), schema, runner, reducer, and decision-rule script are frozen and hashed together in `results/stage7b2/pre-execution-manifest.json` before any retained run; analysis is source-frozen. Exploratory shakedown executions during the implementation window remain unretained calibration checks, as disclosed in the 7B1 manifest note.

## 7. Standing-rules compliance and falsification-gate mapping

Exact `Fraction` arithmetic in every ledger; solver enclosure arithmetic is analysis-side only (7B1 §8). Telemetry labels never read by mechanics. Gates engaged by this registration: conservation (all reserve/packet/memory/census/reserve ledgers close at every registered checkpoint of every replicate); packet-sink (7B1 §3 retirement equations hold; `unread_buffer_eviction` never fires); vacancy (recruitment decomposed into intrinsic bout completion and ecological vacancy capture via shadow telemetry; no "fecundity" label on the capture-mediated component alone); endpoint (only the §3–§4 `r_g` distribution is primary; all mediators stay mediators); age-state and somatic-state (active/recoverable-depleted/stalled/removed organism-time reported separately; 7B1 death ordering asserted); trait-isolation (genotypes differ only in `A`); ecology (single hazard level ⇒ combined-response labelling rule of §1); storage (founder inputs logged; exact `death_disposal`; no-decay baseline with hoarding disclosed as an observable, endpoint-neutral strategy); plasticity-scope (fixed-`(A,T)` results say nothing about plasticity); trait-resolution (two-point contrast only; interior lattice claims prohibited); no historical carry-over (no pre-Stage-7 quantity reused).

## 8. Freeze-before-execution and authorised execution class (for the successor session)

1. Implementation window opens on commit of this document; no retained execution occurs during it.
2. Freeze implementation, runner, tests, schema, reducer, and analysis script **together**, with SHA-256 + byte size per file at `results/stage7b2/pre-execution-manifest.json`, committed before any retained run.
3. The authorised execution class is then one seeded, mutation-disabled confirmatory suite: `k = 32` replicate populations under §2, reduced once under §5, raw output retained under `results/stage7b2/` and classified under the repair policy.
4. PASS criterion: every ledger closes at every registered checkpoint in every replicate; every solver certification is valid; the §5 rule is applied exactly once and its outcome recorded. Any failure retains the run, classifies it, and triggers repair — archiving, never deletion.

## 9. Not authorised by this document

Any execution before the §8 freeze; mutation at any locus; open genomes; additional hazard levels or the directional `α*(h)` prediction; factorial separation studies; optimum, ESS, or background-invariant causal claims; endpoint substitution; interior-lattice or extrapolated landscape claims; plasticity interpretations; reuse of pre-Stage-7 quantities; modification of retained artifacts or superseded documents; history rewrites.
