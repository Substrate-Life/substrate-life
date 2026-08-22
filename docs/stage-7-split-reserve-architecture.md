# Stage 7 Candidate Architecture: Split Somatic and Reproductive Reserves

**Status:** isolated Slice 1 and mechanics-only population Slice 2A are implemented under explicit provisional defaults. The scripted fixed-state Stage 7B0 mechanism protocol is registered separately, but its implementation and execution remain **NO-GO**. Mutation and every Stage 7 population-fitness or evolutionary assay remain **NO-GO** pending §13.

**Decision point:** evaluate before any further work on the hazard-only vacancy ecology.

**Boundary:** this document defines candidate semantics and falsification gates; it is not an implementation specification.

**Historical compatibility:** none. This is a substrate-semantic break. All pre-Stage-7 τ landscapes, carrying capacities, age structures, and effect sizes are parameter-stale for this architecture.

## 1. Why this redesign exists

The terminal Stage 6 diagnosis is a shared-wallet and substrate-vocabulary problem. One reserve currently pays:

1. somatic upkeep and ordinary execution;
2. reproductive copying and allocation work;
3. offspring provisioning;
4. offspring survival to first income.

Hard-cap displacement additionally makes birth cause incumbent death. Exogenous hazard plus non-displacing recruitment removes that birth-causes-death channel and makes physical lifespan settable. It does not, by itself, separate reproductive competence from reserve: if depletion creates an absorbing stalled state, reserve still determines functional reproductive death and the hazard merely removes stalled organisms later.

Historical transfer `τ` was the only available reproductive-allocation-like control, but it governed per-offspring provisioning from the same wallet that funded parental persistence. The architecture could not independently express “route less acquired income to reproduction and more to persistence.” Allocation, provisioning quality, reproductive work, and establishment were therefore conflated.

The Stage 7 candidate attacks that expressive limitation directly by separating somatic and reproductive accounts and adding a genomic allocation vocabulary. The scientific target is no longer a “clean fecundity assay” in which reproduction and survival are independent. It is an explicit, conserved life-history allocation problem in which the route from acquired income to somatic maintenance versus reproductive investment is heritable and measurable. The trade-off remains because it is biological; the gain is that it becomes an organism-expressible trait rather than an emergent consequence of an overloaded wallet.

## 2. Claims this architecture may support

If implemented and verified, the architecture may support these scoped claims:

- Birth need not cause physical removal; turnover can remain exogenous.
- Reproductive capital can be exhausted without directly exhausting the parent’s somatic account.
- For `α>0`, reproductive capital can be recoverable through later extraction under an executed control flow and somatic runway that actually reach positive income.
- A heritable allocation rule can trade somatic maintenance against reproductive investment through explicit ledgers rather than one overloaded state variable.

It does **not** automatically establish:

- reproduction–mortality independence;
- a provisioning-only or fecundity-only fitness landscape;
- somatic survival independent of allocation, because routing more income to reproduction leaves less for soma;
- freedom from vacancy scramble at a saturated census;
- comparability with historical τ results.

## 3. State variables and terminology

Each organism has at least:

- `S`: **somatic reserve** — pays upkeep, ordinary execution, and non-reproductive metabolism;
- `R`: **reproductive reserve** — pays reproductive work and offspring endowment under the strong split described below;
- `D>0`: common registered denominator;
- `α=A/D ∈ [0,1]`, with integer `0≤A≤D`: **acquisition-allocation fraction** — fraction of realised extraction income routed to `R`; `A` is inherited but fixed for the organism's lifetime;
- `τ_R=T/D ∈ [0,1]`, with integer `0≤T≤D`: **per-offspring provisioning parameter** of one preregistered map `P=g(R_w,τ_R)`, evaluated from reproductive reserve `R_w` remaining after reproductive work and after gestation validation, vacancy reservation, and child-memory reservation succeed; `T` is inherited but fixed for the organism's lifetime. The recommended first map is the exact rational fraction `P=(T/D)R_w`. Validate or reject inherited/mutated `A,T,D` before organism creation and again before computing `P`; clipping an invalid mutation would be a separate registered mutation rule. A fixed-amount or rounded map would be a different treatment and may not be mixed into the same assay.

Historical `τ` was a fraction of the single current reserve transferred at DIVIDE. `α` is not that trait. Renaming `α` to τ would conceal a semantic break. The first Stage 7 assay should vary either `α` or `τ_R`, not both, unless a two-trait design is explicitly registered.

### 3.1 Scope decision: genotypic allocation, not plastic allocation

Lifetime-constant `A` and `T` are a deliberate first-implementation simplification. Stage 7 initially expresses **heritable genotypic allocation strategies**, not condition-dependent allocation rules. Organisms cannot increase reproductive allocation near expected death, restrain reproduction under low `S`, plastically alter `T` or the provisioning rule under stress, or respond plastically to current hazard, age, reserve, packet state, or offspring condition; realised provisioning `P` nevertheless varies mechanically with available `R_w`. A null result therefore bears only on evolution among fixed allocation fractions in the registered ecology; it is not evidence that plastic allocation cannot evolve or that the substrate cannot support it. Any later plastic design must specify sensed state, reaction-norm encoding, update timing, costs, and packet-provenance consequences and must be treated as a new architecture.

## 4. Conserved income split

For positive realised extraction income `Y > 0`:

- `ΔS_income = (1-α)Y`
- `ΔR_income = αY`
- `ΔS_income + ΔR_income = Y`

Stage 7 must use exact non-negative rational reserve arithmetic in the reference semantics, with `D>0` and `0≤A,T≤D`. Credit `Y_R=(A/D)Y` and `Y_S=Y-Y_R` exactly; there is no allocation remainder or per-draw rounding. An optimized fixed-point implementation is acceptable only after proving bit-exact equivalence for every legal packet energy, cost, `A`, `T`, and reversal. Binary floating-point “exact conservation” is not an acceptable substitute. The denominator and trait encoding remain §13 blockers.

`D` is a scientific parameter, not an arithmetic convenience. With every integer numerator `0…D` legal it gives `D+1` fixed allocation strategies and adjacent values differ by `1/D`; more generally `1/D` is the base lattice increment, while the preregistered legal subset sets actual cardinality and minimum realised spacing. Together with the mutation kernel on `A` and `T`, it determines the distribution of phenotypic step sizes. Coarse grids can create threshold jumps or alias an apparent optimum; fine grids change mutational neighbourhoods and the time needed to explore the landscape. Before evolution, preregister and justify `D`, legal `A/T` values, initial distributions, mutation step kernel, boundary behavior, and expected phenotypic resolution. If conclusions may depend on discretization, register a resolution-sensitivity comparison rather than selecting `D` for implementation convenience.

No **within-organism** transfer between `S` and `R` exists unless separately specified. In particular, reproductive reserve may not silently rescue soma, and soma may not silently subsidise reproductive transfer. The sole recommended cross-account conversion is the atomic intergenerational transaction `parent R → child S_birth` at successful DIVIDE.

### 4.1 Signed extraction and reversal provenance

The current packet ledger is signed: a later expansion can return previously drawn energy to the source packet. Stage 7 must therefore retain exact packet-level account provenance. For each positive packet draw `q`, increment that packet's `drawn_S` by `(1-A/D)q` and `drawn_R` by `(A/D)q`. Because `A` is fixed for the organism's lifetime, a partial reversal `0<q_rev≤drawn_S+drawn_R` debits the exact ratio `(1-A/D)q_rev` from `S` and `(A/D)q_rev` from `R`, decrements the packet's two provenance accounts by those amounts, and restores `q_rev` to the packet. No FIFO/LIFO convention or mutable rounding state is required. If lifetime-changing `A` is later proposed, each draw must instead be a separate immutable provenance lot and that is a different design.

Recommended first semantics: compute and precheck the reversal atomically **before applying the transform**. If either account no longer contains the required provenance-matched amount because credited units were spent, the entire transform is a transform-state no-op. Working-memory bytes, byte tags, allocation extents, packet energy/provenance counters, `S`, and `R` remain unchanged except for ordinary instruction charge and normal tick upkeep; no transform-success event or replenishment is emitted. The program counter advances, the VM failure flag is set, and result registers `R3` and `R4` receive the registered failure values `0,0`; all other registers and carry/control state remain unchanged. Log `REVERSAL_ACCOUNT_UNAVAILABLE`. On success, debit both accounts and update packet budget/provenance atomically before committing bytes, tags, extents, result registers, and transform output. A complete draw followed by complete return restores packet budget/provenance and `S/R` exactly to their pre-draw values, apart from explicit instruction/upkeep costs. On a fresh packet with no prior draw, expansion remains energetically zero and merely wastes the instruction, matching the current conservation rule. An alternative explicit debt ledger would be a separate design requiring bounded debt and repayment semantics; it is not assumed here.

## 5. Critical cost-allocation fork

### 5.1 Weak split — insufficient for the stated fix

Under a transfer-only split:

- offspring transfer is paid from `R`;
- ALLOC_OFFSPRING, COPY_BLOCK, DIVIDE, and their memory/upkeep consequences are paid from `S`.

This leaves extra reproductive attempts able to deplete soma. The current minimum-block sequence has nominal instruction charge 14 units before tick and gestation-memory upkeep. A high-attempt genotype can therefore still become somatically stalled through reproduction. This variant does not resolve the shared-wallet diagnosis and must not be described as soma-protected reproduction.

### 5.2 Strong split — candidate implementation

The strong split removes reproduction-specific variable work and offspring provisioning from the parent’s somatic ledger. It does not make additional reproductive bouts somatically free: each bout still incurs common `S`-paid tick/dispatch costs and may alter extraction timing.

- basal tick upkeep and ordinary opcode execution overhead are paid from `S`;
- reproduction-specific allocation, gestation-memory, offspring-copy mutation, copying, and DIVIDE work are paid from `R`;
- offspring provisioning is deducted from `R` only after gestation validation, vacancy reservation, and child-memory reservation succeed;
- an `R`-insufficient reproductive operation fails without drawing its variable reproductive cost from `S`.

**Provisional baseline preserving the current total instruction charges:**

| Opcode | Somatic dispatch `C_S` | Reproductive work `C_R` |
|---|---:|---:|
| `ALLOC_OFFSPRING(size)` | 1 | `4+ceil(size/64)` |
| `COPY_UNIT` | 1 | 1 |
| `COPY_BLOCK(n)` | 1 | `1+ceil(n/64)` |
| `DIVIDE` | 1 | 4 |
| `SET_P` | 1 | 0 |
| `READ_GESTATION` | 1 | 1 |

Normal somatic upkeep is additional. `C_S` is checked and debited before any instruction semantics. If it is unaffordable, the instruction has no effect and the still-unresolved somatic-depletion rule in §13 applies. Next check the entire `C_R`. If `R<C_R`, no reproductive state changes and no mutation/random draw occurs; `C_S` remains sunk and `R` is unchanged. If affordable, debit `C_R` before applying the operation. Neither account may become negative. Work already debited remains sunk on later allocation, admission, memory, or instantiation failure. Mutation generated causally during offspring copying is included in COPY work; constitutive parent repair or maintenance remains somatic unless separately added and justified.

This table is a candidate normative choice, not a measured biological decomposition. It preserves current nominal totals while assigning one common dispatch unit to soma. It requires an equal-tempo control to quantify the residual somatic burden. If all 14 minimum-bout units remain somatic, the strong split has not been implemented.

Operand resolution precedes cost computation and preserves current rules. For ALLOC_OFFSPRING, the first encoded operand is resolved once from the pre-instruction snapshot using the current `_get_reg` rule: integer `0…7` names register `R0…R7`, an integer outside that range is a literal, a non-integer uses the default, and an omitted operand defaults through operand `0` to `R0`. If the resolved value is not a positive integer, use `MIN_WORKING_MEMORY`. The same resolved snapshot determines both allocation semantics and `C_R`. COPY_BLOCK uses `n=R6` only when it is a positive integer and otherwise requests the genome length, then caps `n` at the remaining uncopied genome instructions. The resolved `size/n` determine `C_R`. A semantically invalid operation still pays those resolved prepaid costs unless a distinct failure cost is later explicitly registered.

The strong split provides **direct-debit isolation**, not unconditional somatic protection. At fixed realised extraction, fixed `α`, and a preregistered matched basal execution schedule, parent `S` may contain only somatic income and common somatic costs; no reproduction-specific variable work or provisioning may appear there. In unconstrained evolution, reproductive instructions still consume scheduler ticks and somatic upkeep/dispatch, and repeated `R`-insufficient attempts can replace READ/TRANSFORM opportunities. These residual life-history couplings must be measured separately.

### 5.3 Gestation allocation and upkeep blockers

The implementation-ready specification must partition shared memory into somatic and gestation allocations, define instruction bytes and enforce `gestation_capacity=floor(bytes/INSTRUCTION_BYTES)`. COPY must not exceed that capacity, and DIVIDE must require a registered completeness condition. After ALLOC_OFFSPRING work is prepaid, any previous gestation allocation and copied buffer are unconditionally invalidated and freed before the new block is requested; failed reallocation leaves no stale bout available to DIVIDE. At every ordinary upkeep boundary for which the gestation allocation is live, compute the exact rational base `gestation_bytes/MEMORY_COST_DIVISOR` and apply the current organism-state factor: `1` while active, `DORMANT_UPKEEP_FRACTION=1/10` while dormant, and `0` while suspended. Charge the result to `R`; this preserves the current state-dependent gestation-memory upkeep magnitude while moving its payer. The allocation made earlier in the tick is live at that tick's upkeep boundary; an allocation released before the boundary is not charged. The exact response when `R` cannot fund this charge—recommended candidate: dissipate remaining `R`, free the gestation block, and clear the bout without charging `S`—remains a §13 normative blocker. Genome-storage ownership for founders, parents, and offspring must also be uniform and explicit.

## 6. Reproductive depletion and recovery

`R=0` should stop or limit reproduction without stopping ordinary somatic execution, but account separation alone does not guarantee recovery. For `α>0`, recovery requires an `S`-funded executed control-flow path to READ and positive TRANSFORM income, enough somatic runway to complete that path, net subsequent income sufficient to accumulate a full reproductive cost, and failure handling that exits or bypasses an `R`-insufficient reproduction loop. `α=0` is intentionally non-recoverable as a reproductive allocation strategy.

Required trace gate:

1. Begin at the genome's normal entry point with `S` above a preregistered runway, `R=0`, and `α>0`; do not inject execution directly onto a foraging instruction.
2. Show the executed control flow handles any `R`-insufficient reproductive opcode and reaches positive extraction using only `S`-funded work.
3. Record cumulative `S` cost to first positive income, the net `S` trajectory during accumulation, and exact rational `Y_S/Y_R` allocation.
4. Show `R` becomes sufficient for the complete registered reproductive work and provisioning rule before somatic failure.
5. Show a later complete bout can execute and verify no hidden within-organism `S→R` transfer or packet-budget violation.

This does not solve an absorbing **somatic** state at `S=0`. If high `α` leaves insufficient somatic income, soma may still stall or die depending on the separately specified somatic-depletion semantics. That is an intended allocation trade-off if registered, not evidence of fecundity–survival independence.

## 7. Offspring endowment

A successful DIVIDE converts parent reproductive capital into offspring state. The conversion must be explicit.

Recommended first design:

- reproductive work is deducted from parent `R` before each reproductive opcode takes effect;
- after all work in the bout, successful admission uses exact rational `R_w` and `P=(T/D)R_w`;
- committed provisioning `P` is deducted only after gestation, vacancy, and child-memory feasibility are secured;
- the offspring receives `S_birth=P` and `R_birth=0`;
- the offspring must earn its own reproductive reserve through extraction.

This treats parental reproductive reserve as capital used to construct and somatically endow a child. Alternative splits of `P` between offspring `S` and `R` add another allocation parameter and should be deferred.

**Prospective DIVIDE transaction, after `C_S` and `C_R` have been prepaid:**

Every operation after successful vacancy reservation is inside one transaction guard. Until the final commit point, vacancy, child-memory, provisioning, candidate genome, and any child object are provisional and invisible to the population.

1. Validate the registered complete gestation condition. Failure creates no child and no new random draw; failure-state retention versus discard must be fixed with the gestation semantics.
2. Atomically reserve one census vacancy. If none exists, report `NO_VACANCY`, commit no provisioning, make no DIVIDE-level insertion/deletion/duplication draw, and discard/free the completed gestation bout. COPY-time substitution draws and work have already occurred and remain sunk.
3. Construct the provisional candidate genome from the copied buffer and apply the registered DIVIDE-level insertion/deletion/duplication draws. Consumed RNG remains consumed even if a later step fails.
4. Immediately release/discard the completed gestation allocation and copied buffer. This cleanup also occurs on `NO_VACANCY`, child-memory failure, success, and unexpected exception; a completed DIVIDE attempt can never be retried from stale gestation.
5. From the post-indel candidate genome, compute the child's complete memory obligation: registered genome storage, minimum working memory, and every other child-owned allocation under the uniform ownership rule. Atomically reserve that amount. No further mutation or candidate-state change may occur after reservation. On failure, release the vacancy, report `CHILD_MEMORY_UNAVAILABLE`, and retain all prepaid work/RNG consumption. No provisioning is computed, emitted, reserved, or debited; parent `R` is unchanged except for prepaid reproductive work and already-incurred gestation upkeep.
6. Revalidate `D>0` and `0≤T≤D`, compute exact `P=(T/D)R_w`, and provisionally debit `P`. Construct the provisional child with `S_birth=P`, `R_birth=0`. The commit point atomically publishes the complete child, converts the vacancy and child-memory reservations to ownership, and commits `P`; only then emit `P` and a successful birth event.
7. On **any** exception after vacancy reservation and before commit—including mutation, candidate construction, gestation cleanup, memory sizing/reservation, provisioning, or child construction—release vacancy and child-memory reservations, refund `P` if provisionally debited, remove or never publish any partial child, discard candidate and gestation state, and omit `P` from telemetry. Prepaid work and consumed RNG are not refunded. No exception path may leave a census-visible child or resource reservation.

Birth never removes an incumbent. Within-tick hazard/admission/scheduler ordering remains an ecology blocker in §13. Failed census admission therefore creates no child and commits no transfer, while already executed reproductive work remains deducted from `R`. This preserves vacancy-scramble cost without a direct reproductive-variable debit to soma.

**Reproductive budget closure:** over a registered accounting window, opening parent `R` plus credited `Y_R` equals closing parent `R` plus reproductive work, committed provisioning, gestation upkeep, and explicit terminal dissipation. On successful birth, committed provisioning equals child `S_birth` one-for-one unless a separately preregistered conversion loss exists.

## 8. Turnover remains a separate mechanism

Split reserves do not regulate population size. A turnover mechanism is still required.

The hazard-only result should therefore be retained but narrowed:

- exogenous hazard removes birth-triggered incumbent death and sets physical lifespan;
- the split ledger prevents reproductive work and provisioning from directly draining soma under the strong variant;
- non-displacing vacancy admission still measures contested recruitment at saturation;
- `h`, census occupancy, attempt rates, synchrony, and vacancy inventory still require the accounting already derived in §4l of the project report.

The hazard is no longer asked to create the entire separation. It controls physical turnover; the split ledger controls which physiological account reproductive investment depletes.

## 9. Scientific target and first-stage decomposition

The primary Stage 7 target is fixed: **an explicit conserved life-history allocation landscape**. A `τ_R` treatment is only a reproductive-capital provisioning subdesign; it is not “clean fecundity,” especially under saturated vacancy admission.

The first programme must be staged:

1. **Mechanism verification:** fixed equal-length/equal-tempo genome, fixed foraging and attempt schedule, fixed `τ_R`; externally set `α` values verify ledgers, viability, timing, and establishment.
2. **Restricted `α` evolution:** only a dedicated `α` encoding mutates; foraging instructions, `τ_R`, cycle logic, and ancestry marker are fixed and treatment-verified.
3. **Open evolution—the motivating target, deferred only until mechanism gates pass:** once acquisition effort, timing, provisioning, and ecological exposure can coevolve, trajectories may still estimate α-associated fitness differences, selection differentials, or descriptive multivariate gradients. Without additional interventions or structural assumptions they do not identify the **direct causal effect or causal selection gradient of α while holding coevolving genomic background, mediators, and ecological exposure fixed**. This stage answers the project's open-evolution question by analysing joint genotype–phenotype–ecology outcomes with context-specific mediation, reciprocal invasion, and controlled counterfactual assays; it must not relabel an α association or frequency change as direct or isolated causal selection on α.

These stages answer different questions rather than progressively cleaner versions of one question. Stage 1 asks whether the substrate implements the proposed channel. Stage 2 asks how a fixed-allocation locus evolves under a deliberately restricted genetic architecture. Only Stage 3 restores the openness that motivated the project. Passing Stages 1–2 supports mechanism and constrained evolvability but cannot substitute for the open result.

Two one-dimensional questions must not be conflated:

### 9.1 Acquisition-allocation question

Hold `τ_R`, genome length, realised foraging programme, attempt schedule, and turnover fixed; first vary `α`, then permit mutation only at its dedicated equal-tempo encoding.

Interpretation: conditional allocation of acquired income between soma and reproduction. Expected outcomes may include somatic failure at high `α`, slow reproductive accumulation at low `α`, and an interior life-history optimum. This is not clean fecundity; it is the intended survival–reproduction trade-off. Once foraging effort or timing evolves, the estimand becomes the joint allocation–acquisition strategy rather than α in isolation.

### 9.2 Per-offspring provisioning question

Hold `α` fixed inside a somatically viable range; vary/evolve `τ_R`.

Interpretation: allocation of reproductive capital among offspring number, timing, and endowment. In a single-bout matched trace, `τ_R` must not directly alter parent `S`. Over a life history it may indirectly alter `S` by changing the number/timing of fundable bouts and their common somatic overhead. This is a provisioning-specific assay, not clean fecundity; vacancy capture and offspring establishment remain part of realised fitness.

A two-trait `(α, τ_R)` evolutionary analysis is deferred until each one-dimensional mechanism has independently passed conservation, viability, recovery, and exposure gates; any later open-stage result must report the preregistered replicate distribution and must not presume a unique optimum or ESS.

### 9.3 Methodological result: the constraint–openness tension

The Stage 7 review exposes a measurement-level companion to the project's mechanism-coupling result. Mechanistically, substrate currencies and regulators can couple reproduction, persistence, provisioning, and recruitment. Inferentially, unconstrained coevolution couples a focal trait to its genomic background, acquisition rate, timing, expression, mediators, and ecological exposure. Trajectories can reveal trait–fitness associations and descriptive selection patterns, but they do not by themselves identify the focal trait's direct causal effect with those coevolving quantities held fixed. Adding controls can identify a channel, but every fixed genome, frozen locus, matched schedule, or standardised ecology narrows the open evolutionary question.

This is not an impossibility theorem and does not mean traits are unobservable. `A/D` is directly logged; α-associated frequency change, selection differentials, and descriptive gradients may be estimable. The non-identified quantity is the direct causal effect or causal selection gradient of α under a fixed coevolving background and exposure. Identification may be strengthened by interventions, reciprocal-invasion/common-garden contrasts, explicit structural models, or mediation assumptions, but these provide context-specific or assumption-dependent decompositions and do not automatically convert the open trajectory into a background-invariant α effect. The practical rule is to report three evidential levels separately: **channel exists**, **restricted architecture evolves through the channel**, and **open populations evolve joint outcomes in which the channel participates**. Do not promote evidence from the first two levels into the third.

The open-stage estimand is the preregistered replicate distribution of invasion growth/reproductive value and of joint genotype–phenotype–ecology outcomes under the specified mutation kernel, initial conditions, and ecology. It is not necessarily a unique strategy, an ESS, or a background-invariant effect of α.

### 9.4 Fitness endpoint and mediation

The primary fitness endpoint is preregistered invasion growth or reproductive value, with active, recoverable-depleted, and stalled survival reported separately. Age-specific establishment through first reproduction is a required life-history component or mediator and may serve as a fitness endpoint only if the registered life cycle demonstrates that it captures subsequent reproductive contribution. Reserve, attempts, materialised births, accepted admissions, first extraction, first reproduction alone, or endpoint ancestry frequency are not otherwise fitness substitutes. In particular, sterile persistent founders and `R` hoarders must not count as successful merely because they remain in census.

Record the causal chain separately: realised extraction `Y` → `Y_S/Y_R` → age at fundable bout → attempt and vacancy exposure → `P`/child `S_birth` → first extraction → first reproduction → subsequent reproductive contribution. Offspring establishment is an intrinsic pathway of α, not a nuisance to remove, but each stage must remain distinguishable. Saturated results are allocation-under-vacancy-capture outcomes; they cannot identify intrinsic fecundity.

### 9.5 External-validation prediction: hazard and allocation

**External prior, not derived from Substrate:** standard life-history reasoning predicts that greater phenotype-blind extrinsic mortality discounts late somatic returns and can favour faster reproductive investment. Under the first Stage 7 encoding, this is specifically a prediction about evolution among lifetime-constant **genotypic allocation fractions**, not terminal investment, reproductive restraint, or any within-lifetime plastic response. The prospective directional prediction is that, after the mechanism and ecology gates below pass, the evolved fixed-allocation optimum or stationary distribution shifts toward higher `α` as hazard increases: for registered `h_low < h_mid < h_high`, `α*(h)` is nondecreasing, with a preregistered positive low-to-high contrast.

This is not a universal theorem that mortality always selects faster life histories. Before registering the directional assay, verify:

1. increasing `α` actually advances age-specific established reproduction over a registered viable range while reducing later somatic persistence or future reproductive opportunity;
2. hazard is phenotype-blind and age-independent at exposure;
3. packet/resource exposure is comparable across hazard treatments;
4. the admission process does not introduce an unmeasured `h×α` interaction through attempt timing, phase, or rejection;
5. `D`, the mutation kernel in `A`, mutation supply, starting α distribution, run duration in hazard-scaled generations, and effective population size are preregistered and controlled or reported.

At saturated vacancy-limited census, increasing `h` also increases vacancy openings and attempt acceptance. In that ecology `h` is **not** a clean lifespan-only knob. A shift in α could reflect shorter expected future life, increased recruitment opportunity, or their interaction. For external validation, use either nonbinding/independently standardised admission or a factorial design that separately identifies hazard exposure and recruitment opportunity. If that separation is unavailable, label the outcome a combined mortality–turnover response and do not present it as confirmation of the textbook mechanism.

Prospective falsification is an ordered null or reversal at the preregistered endpoint: no minimum positive low-to-high α shift, or a reliably downward shift, after the mechanism and ecological gates pass. Failure before those gates diagnoses an assay that cannot test the prediction, not a biological counterexample. Passing would provide external validation that the substrate expresses a recognisable **fixed genotypic-allocation** response; failure after all gates would identify a substantive departure worth analysing through age-specific survival, income allocation, and established recruitment. Neither outcome tests allocation plasticity.

### 9.6 Minimum event telemetry

Every reproductive event must log inherited lifetime-fixed `A/D` and `T/D`, immutable ancestry ID, explicit current genotype ID/hash, realised `Y`, pre/post `S`, pre/post `R`, required and actually debited `C_S/C_R` separately, exact gestation upkeep, failure stage/reason, gestation bytes before/after and release reason, vacancy reservation, post-indel candidate-genome memory basis and child-memory reservation, whether COPY- and DIVIDE-stage mutation RNG was consumed, `R_w`, and child initial `S/R`. Emit `P` only when provisioning commits; failed events omit it rather than reporting a numeric zero.

Every positive draw and reversal must additionally log packet ID, lifetime `A/D`, exact pre/post packet budget, exact pre/post `drawn_S/drawn_R`, requested and actually debited `S/R`, transform failure code, and whether bytes, tags, extents, result registers, and transform output committed. Every death/final-tag sink event must identify tick, organism ID, packet ID, release reason, exact residual packet budget physically destroyed, and exact `drawn_S/drawn_R` reversal provenance retired. Physical energy destruction and provenance retirement are separate fields and may not be summed as two energy sinks. Population output must distinguish active, recoverable-depleted, stalled, and removed organism-time and report age-specific first extraction, first reproduction, and established descendants.

## 10. Core invariants

1. **Income conservation:** every positively extracted unit enters exactly one of `S` or `R`; every signed packet-energy reversal debits the provenance-matched accounts before restoring the packet budget.
2. **No silent within-organism cross-subsidy:** no implicit `S↔R` rescue; the sole recommended conversion is committed `parent R→child S_birth`.
3. **Reproductive budget closure:** opening `R` plus credited `Y_R` equals closing `R` plus reproductive work, gestation upkeep, committed provisioning, and explicit terminal dissipation.
4. **Failure ordering:** gestation, vacancy, child-memory, and instantiation failures cannot destroy uncommitted provisioning; work already prepaid remains sunk and every reservation/RNG consequence follows §7.
5. **Direct-debit isolation:** at fixed realised extraction, fixed `α`, and a matched basal schedule, no reproductive variable work or provisioning appears in parent `S`; indirect effects through income allocation, time, extraction, dispatch, and upkeep are reported separately.
6. **Conditional reproductive recovery:** for `α>0`, `R=0` permits later recovery only when the executed `S`-funded control flow reaches sufficient positive income before somatic failure.
7. **Turnover separation:** birth never removes an incumbent; all physical removals are separately attributed.
8. **Trait distinction:** `α`, `τ_R`, immutable ancestry, and realised transfers are logged separately.
9. **No historical carry-over:** no pre-Stage-7 optimum, K, lifespan, or effect size is reused as evidence.
10. **Boundary sinks/sources:** founder `S/R` are logged external inputs; every removal dissipates and logs terminal `S/R`; offspring never receive founder defaults. Death or loss of the final packet tag separately logs physically destroyed residual packet budget and retired `drawn_S/drawn_R` reversal provenance without double counting.
11. **Storage economics declared:** `R` upkeep/decay and terminal disposal are explicit. A no-decay baseline is allowed only if reserve hoarding is registered as a candidate strategy rather than ignored.

## 11. Falsification gates before implementation or assay

Stop or redesign if any gate fails:

- **Direct-debit gate:** any reproduction-specific variable charge or provisioning appears in parent `S`; separately quantify differences from unmatched ticks, dispatch, or extraction.
- **Recovery gate:** under `α>0` and a preregistered sufficient somatic runway, the full executed genome cannot exit an `R`-insufficient path, reach positive extraction, and fund a complete later bout.
- **Conservation gate:** exact rational `ΔS+ΔR` differs from positive extraction minus explicit costs/transfers and provenance-matched signed reversals.
- **Semantic gate:** `α` and historical transfer τ are treated as the same phenotype.
- **Vacancy gate:** a proposed “fecundity” endpoint is actually vacancy-capture rate under binding admission.
- **Age-state gate:** the equilibrium active population does not occupy the recurrent `S,R` orbit used in paper predictions.
- **Somatic-state gate:** `S=0` death/stall/recovery and its ordering relative to instruction effects and hazard remain unspecified.
- **Trait-isolation gate:** the α treatment changes genome length, execution tempo, foraging programme, `τ_R`, or ancestry marker, or mutation is not restricted as claimed.
- **Trait-resolution gate:** `D`, legal `A/T` values, initial distribution, mutation step kernel, and boundary behavior are chosen post hoc, justified only by arithmetic convenience, or too coarse to resolve the registered contrast.
- **Plasticity-scope gate:** a fixed-`A/T` result is interpreted as evidence about terminal investment, stress-dependent restraint, or any condition-dependent allocation reaction norm.
- **Acquisition/timing gate:** realised `Y`, foraging effort, cycle time, attempt phase, and scheduler exposure are neither matched nor modelled as mediators.
- **Endpoint gate:** reserve, births, first extraction, first reproduction alone, accepted admission, or endpoint census substitutes for invasion growth/reproductive value without a registered demonstration that the proxy captures subsequent reproductive contribution.
- **Storage gate:** `R` upkeep/decay/death disposal and founder injection are absent from the population ledger.
- **Ecology gate:** hazard and recruitment opportunity are confounded in an assay interpreted as a mortality-only α response.
- **Packet-sink gate:** death or loss of the final tag silently discards residual packet energy or reversal provenance, fails to identify the packet/reason/exact amounts, or double-counts provenance retirement as an additional energy sink.

## 12. Required static paper traces

Before code, trace at least:

1. viable `S`, `R=0`, then extraction and reproductive recovery;
2. high `R`, repeated reproduction, and `R` exhaustion while separating direct `S` debits from dispatch/time effects;
3. high `α` causing somatic underfunding;
4. low `α` causing slow reproductive accumulation;
5. failed full-census DIVIDE with reproductive work sunk, provisioning uncommitted, and no direct reproductive-variable debit to `S`;
6. successful child creation with exact parent `R` loss and child `S_birth` gain;
7. mutation changing `α` but not `τ_R`, and vice versa;
8. positive packet draw split across `S/R`, followed by an exact provenance-matched reversal;
9. attempted reversal after credited `R` has been spent, proving atomic failure without cross-subsidy or packet-budget creation, with bytes, tags, allocation extent, packet provenance, non-result registers, carry/control state, and output unchanged, and only registered `R3/R4=0,0` plus failure code committed;
10. repeated `R`-insufficient reproductive attempts, separating direct ledger protection from somatic opportunity cost;
11. multiple exact-rational draws followed by partial and complete reversals at `A=0`, an interior `A`, and `A=D`, closing both packet provenance accounts exactly;
12. organism death and final-tag removal with packet identity/reason, residual energy destruction, and `drawn_S/drawn_R` provenance retirement logged separately;
13. multi-cycle active organism under exogenous turnover and split reserves;
14. inherited and mutated boundary values `A,T∈{0,D}`, plus invalid `D≤0`, `A<0`, `A>D`, `T<0`, and `T>D`, proving rejection before income split or provisioning;
15. ALLOC_OFFSPRING with omitted operand, each register operand `0…7`, positive/negative integer literals, and a non-integer operand, proving allocation size and `C_R` use one identical pre-instruction resolved value;
16. a live gestation allocation crossing upkeep while active, dormant, and suspended, proving exact factors `1`, `1/10`, and `0`;
17. injected exceptions at every post-vacancy transaction stage, proving no vacancy/memory leak, no published partial child, refunded provisional `P`, omitted transfer telemetry, discarded gestation/candidate state, and retained work/RNG consumption;
18. an open-stage replicate summary reporting a distribution of invasion growth/reproductive value and joint outcomes rather than a unique ESS or isolated α effect.

Each trace must close packet, somatic, reproductive, memory, and census ledgers.

## 13. Decision status

The hazard-only vacancy ecology is insufficient for a clean fecundity assay when reserve depletion remains an absorbing loss of competence. Further elaboration of that route should pause.

The primary target is now fixed as an explicit conserved life-history allocation landscape. The implementation gate is partitioned rather than global. Isolated Slice 1 fixes the strong cost split, exact `Fraction` arithmetic with `D=255`, parent-owned gestation, and recoverable `R=0` reproductive failure. Mechanics-only Slice 2A provisionally fixes the population choices at the point where they become executable:

1. insufficient somatic reserve causes a nonexecuting `STALLED` state, including failures reached mid-cycle after committed READ/upkeep work; residual `S` is retained and only phenotype-blind hazard physically removes the organism;
2. hazard runs at tick start; survivors run in stable organism-ID order; newborns first enter the following tick's scheduler snapshot;
3. hazard deaths are the only vacancy source, admission never displaces an incumbent, and full-census rejection commits no provisioning while completed reproductive work remains sunk;
4. one globally consumptive packet buffer receives five exogenous rich packets per tick; captured and unread-buffer packet budgets are both asserted closed from each packet's live `e_initial`;
5. shared memory is partitioned exactly among active soma, parent-owned gestation, corpse reservation, and free pool; reproductive and memory-failure paths release transient gestation exactly once, and corpse TTL returns memory exactly once;
6. `A`, `T`, and `D` inherit exactly and mutation is disabled; the mechanics trace therefore measures no evolutionary response and contains no scientific treatment contrast.

The retained 20-tick trace exercises hazard death, vacancy admission, full-census rejection, packet misses, pre/mid-cycle stalls, and corpse expiry while all reserve, packet, and memory checkpoints close. Focused regressions separately force gestation-upkeep/COPY/DIVIDE reproductive failures and shared-memory pressure, including their cleanup and ordinary-upkeep paths. Together these establish executable mechanics under the provisional choices, not their scientific optimality and not a fitness result.

`stage-7b-fixed-allocation-channel-preregistration.md` now freezes a narrower scripted mechanism verification at `A∈{102,204}`, `T=128`, and `D=255`. It explicitly discloses prior deterministic calibration and contains no fitness endpoint. It authorised no execution by itself; its implementation, runner, tests, schema, analysis, and hashes were frozen before execution, and the registered blocks have since executed to PASS twice under independent frozen implementations (2026-08-01 canonical channel lineage; 2026-08-22 blocks implementation — see `docs/stage-7b0-deterministic-execution-note.md` and `docs/project-report.md` §6b). Before any later population-fitness assay, separately resolve and preregister: (a) the legal `A/T` strategy set, starting distribution, mutation kernel, boundaries, and resolution sensitivity; (b) whether `R` storage has upkeep or decay on longer timescales; (c) whether vacancy capture is part of the estimand or admission is independently standardised/nonbinding; (d) the primary invasion-growth/reproductive-value endpoint and cohort mediators; and (e) the treatment contrast, falsification gates, and source-frozen analysis plan. Slice 1 and Slice 2A mechanism code and traces are authorized, as is Stage 7B0 mechanism verification; Stage 7B1 design is authorized but its execution, evolutionary simulation, confirmatory population inference, and every scientific assay remain unauthorized.
