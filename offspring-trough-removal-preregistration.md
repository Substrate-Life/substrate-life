# OFFSPRING_TROUGH Removal: Semantic Registration and Stale-Result Ledger

**Registered:** 2026-07-28, after diagnosis of the threshold-18 defect and before any no-threshold τ competition rerun.

**Displacement amendment:** 2026-07-28, after identifying protected doomed-offspring displacement and before any τ rerun.

## Mechanism change

Remove `OFFSPRING_TROUGH` from the executable substrate. After copied-genome materialisation and gestation release, DIVIDE checks that the shared pool can provide the minimum organism block. Only then does it commit `tau × parent reserve`, and the offspring is instantiated with that exact reserve. No interpreter rule predicts viability from reserve.

An instantiated offspring:

- enters the population and birth log;
- at the cap, samples a victim uniformly over all existing residents, including the reproducing parent;
- holds a 64-byte minimum memory block;
- pays upkeep on its birth tick;
- executes only when reached by the normal scheduler;
- dies through the ordinary reserve ledger if it cannot reach positive extraction;
- moves its memory to the corpse pool until normal expiry.

A failed gestation/materialisation caused by missing copied genome, exhausted parent reserve, or insufficient shared memory remains a DIVIDE materialisation failure. It is not an offspring death. ALLOC/COPY/DIVIDE execution costs and discarded gestation remain sunk, but an insufficient-memory failure occurs before provisioning commitment: parent reserve is not debited and the event has no `transfer_reserve`. The former `stillbirth` category is removed.

## Mechanical verification gates

Before treating the source transition as complete:

1. `OFFSPRING_TROUGH` is absent from executable source and constants.
2. An offspring transferred less than 18 is instantiated when memory permits.
3. At the cap, victim sampling includes the reproducing parent; tests demonstrate both parent and non-parent removal.
4. It receives and retains the minimum memory block, pays birth-tick upkeep, and if under-endowed dies by `reserve exhausted` at the ledger-determined tick.
5. Its ancestry record classifies whether death occurred before first positive extraction.
6. DIVIDE telemetry distinguishes `offspring_instantiated` from `materialization_failure_reason`; it contains no viability `success` or `stillbirth` adjudication.
7. On successful materialisation, parent reserve loss exactly equals offspring birth reserve. On materialisation failure, no transfer is committed or logged.
8. The memory ledger closes through child death and corpse expiry.
9. Every cap event records the causing offspring ID and later resolves whether that offspring reached first positive extraction or died before it.
10. Report `live displacements caused by offspring that die before first extraction / all live displacements`, plus unresolved live-victim outcomes; report dead-vacancy fills separately. A material fraction means the τ result includes a displacement channel and cannot be interpreted as provisioning alone.

Failure of any gate stops the transition.

## Conditional p=1 prediction and interpretation

Because threshold removal does not change the parent's transfer loss, the isolated conditional parent orbit should remain numerically unchanged. It should still instantiate three FULL and two HALF offspring per 17-tick cycle. This is an instantiation schedule, not viable recruitment.

Using the already measured normal-scheduler cost through READ (exactly 20, with exact-arithmetic viability requiring initial reserve >20):

- FULL's steady three transfers exceed 20 and are energy-capable of reaching first positive extraction under p=1.
- HALF's steady first transfer exceeds 20.
- HALF's steady second transfer is about 19.4297 and cannot reach extraction.

The revised steady deterministic bookkeeping contrast is therefore **FULL 3 versus HALF 1 offspring energy-capable of first extraction per 17-tick cycle**. It is explicitly a mixed reproductive-allocation/offspring-viability contrast, not pure fecundity, equilibrium population fitness, or measured established recruitment. No population member is assumed to complete repeated cycles.

## Historical results made parameter-stale

Removing the threshold changes organism instantiation, cap displacement, memory occupancy, corpse timing, age structure, and death-stage counts. The following threshold-18 results remain historical evidence for that source state but cannot be carried forward as estimates for the no-threshold substrate:

- the four-way no-clamp τ competition in `src/tau_noclamp2.txt`, including the coarse claim that τ≈20% dominated the tested {10%,20%,40%,70%} grid;
- the p=0.60–0.95 established-parent capture-response artifacts;
- the p=1 two-bout post-hoc control;
- unconditional and conditional three-bout threshold-18 classifications;
- monomorphic population calibrations and death-stage/stillbirth summaries that used the old rule.

Original files and hashes are preserved under `failed-designs/2026-07-28-offspring-trough-removed/historical-threshold18/` or the earlier conditional reclassification archive. No historical file is silently rewritten as no-threshold evidence.

## Registered τ-landscape hypothesis — not yet an authorized assay

**Primary directional prediction supplied before rerun:** removing the interpreter threshold will make the low-τ demographic penalty more graded because under-endowed offspring now persist for a reserve-dependent duration and bear displacement, upkeep, memory, and corpse costs rather than being blocked at DIVIDE. The interior optimum is predicted to persist but shift modestly upward from the historical coarse τ≈20% result, reflecting greater benefit from provisioning offspring far enough to establish.

**Falsification conditions:**

- The historical interior optimum does not persist: a boundary treatment wins or τ=20% no longer beats both lower and higher coarse treatments.
- A finer grid shows no upward displacement from the old neighborhood.
- Establishment remains effectively cliff-like and the demographic response is not smoother by a preregistered smoothness statistic.
- The apparent optimum is instead driven by displacement from doomed offspring, memory/corpse pressure, or another ecology-specific effect.

**Mechanism amendment before rerun:** under the prior cap rule, low-τ parents could generate doomed offspring that each displaced a resident while the reproducing parent was immune. This made DIVIDE a protected kill attempt and could support a mixed strategy of several doomed births followed by one provisioned birth. Parent protection has therefore been removed: the reproducing parent is now eligible under the same uniform resident-victim sampling as every other incumbent.

This removes the parent-immunity asymmetry but does not prove all displacement weaponization absent. The newborn is not yet in the incumbent victim set, so a doomed birth can still remove another lineage before later dying; the cost to its lineage is frequency-dependent through uniform victim sampling. Consequently the doomed-offspring displacement fraction remains a mandatory mechanism diagnostic. If it is material at any τ, the result is classified as mixed provisioning/displacement rather than a provisioning landscape.

**Post-implementation smoke result — mechanism exercise only:** two mutation-free FULL monomorphic runs, each only one 17-tick cycle, produced 338 cap displacements. Of these, 144 (`0.4260`) were already resolved to causing offspring that died before first extraction; 108 remained unresolved at the short endpoint; one victim was the reproducing parent. This is censored, non-comparative, and not a τ assay or stable estimate. It is sufficient to reject the claim that parent eligibility alone closes the general doomed-birth displacement channel. No τ rerun was performed.

## Terminal closure of the clean τ-landscape hypothesis

The post-implementation displacement result closes this hypothesis without a τ rerun. Parent eligibility removes the protected-parent asymmetry, but the broader channel is structural under a saturated hard cap: offspring instantiation initiates incumbent replacement, so birth imposes mortality before newborn viability is known. The observed `144/338 = 0.4260` doomed-caused live-displacement fraction is censored and not a stable parameter, but it establishes that this channel is materially active.

Removing the cap substitutes scarcity regulation rather than independence. Packet scarcity and reserve exhaustion couple physical removal or loss of reproductive competence to the same reserve that funds parent persistence, provisioning, and offspring establishment. Thus the current substrate offers two regulators—cap displacement and resource scarcity—and both couple the tested allocation to a life-history endpoint. No provisioning-only τ landscape is available under these regulator semantics. The directional optimum/smoothness prediction above remains part of the preregistered record but will not be tested as a clean provisioning hypothesis.

The constructive missing mechanism is census removal exogenous to both birth events and reserve. Strict turnover decoupling requires that this hazard replace active endogenous removal: births cannot displace incumbents and reserve exhaustion cannot remove organisms. A zero-incidence reserve-removal gate is only an empirical approximation. A future turnover-decoupled design could use phenotype-blind density-dependent hazard `h(N)`—exogenous conditional on N but not dynamically independent of reproduction—or constant exogenous removal with non-displacing vacancy-limited recruitment. In the latter design, a full-census DIVIDE fails before transfer, creates no child, and removes no incumbent; ALLOC/COPY/DIVIDE execution costs remain sunk. A constant density-independent hazard alone separates removal causation but does not robustly stabilise N. This does not establish reserve-independent reproductive competence.

Parameterise the exogenous treatment lifespan-first. For per-tick hazard `h`, mean geometric lifetime is `1/h` and survival through `m` cycles of measured length `T` is `(1-h)^(mT)`. Register `m` and a minimum survival `q`, solve `h ≤ 1-q^(1/(mT))`, and verify the realised age distribution before choosing census ceiling, packet supply, or buffer. This prevents the displacement-era failure in which accepted birth timing mechanically determined displacement pressure and the scheduled-birth Euler–Lotka approximation implied a characteristic lifespan shorter than the 17-tick recurrent cycle.

In the vacancy-limited variant, rejected full-census DIVIDEs retain the proposed transfer but not prior ALLOC/COPY work or the ordinary DIVIDE cost. Higher-bout genotypes can therefore pay more rejected-attempt cost. Any effect-size derivation must include attempts, vacancy exposure, accepted offspring, `census_full` rejections, sunk rejection costs, and resulting parent reserve; the isolated-parent birth-rate ratio is a no-rejection reference, not a guaranteed upper bound on the realised contrast.

Vacancies are a contested supply. At tick `t`, `E[D_t|n_t]=h n_t`, not automatically `hN_cap`. With outstanding vacancies `V`, deaths `D`, and admissions `A`, `V_(t+1)-V_t=D_t-A_t`; accepted recruitment equals death openings only as a stationary long-window flow balance with no vacancy-inventory drift. If hazard deaths are the only vacancy source, there are no other admission failures, and realised attempts and hazard exposure use the same organism-time denominator, the asymptotic accepted/attempted flow ratio is `h/b_attempt`. Finite-window acceptance is `ΣA/ΣQ` with vacancy-boundary and hazard-noise terms. Under the stationary assumptions `N` cancels from the flow ratio, but finite N still changes variance, extinction risk, phase exposure, and scheduler effects. The endpoint is vacancy-capture rate, not intrinsic fecundity. Relative accepted-recruitment share may track attempt share only under genotype-blind, exchangeable acceptance probability; this alone does not establish frequency selection.

Register the implicit feasibility overlap before implementation: `s b_attempt ≤ h ≤ min(b_attempt, 1-q^(1/(mT)))`. The lower bound supplies target long-window attempt success `s`; `h≤b_attempt` prevents secular vacancy accumulation; the final bound supplies survival `q` through `m` cycles. Because `b_attempt` can depend on `h`, age structure, and rejection costs, use live attempts per **total-census organism-time** rather than assuming recurrent `k/T`. If the bounds do not overlap, no census retuning can provide both mostly successful attempts and the target age structure. Specify within-tick hazard/admission ordering. Log census at hazard exposure, deaths, outstanding vacancies, attempt phase and scheduler position, contenders, acceptance/rejection, exact sunk cost, and establishment; compare synchronised and phase-randomised starts. Under the current 64-byte/≤64-instruction bout, the prospective nominal instruction charge is 14 units (`6+3+5`) before tick and gestation-memory upkeep; current source has not implemented `census_full` rejection. Since reserve exhaustion cannot remain a death cause in the strict exogenous treatment, preregister the nonlethal consequence of depletion; without an effect on later execution, allocation, provisioning, or reproduction, the rejection charge is not a fitness cost.

An absorbing zero-reserve stall is not substantive separation. Zero is absorbing only if every route back to positive reserve requires an unaffordable cost-bearing READ→TRANSFORM sequence and there is no basal/external credit, passive income, arrears/debt execution, cost-free instruction, or other recovery transition. Under those semantics the stalled organism occupies a census slot until hazard removal but has already suffered functional reproductive death. The continuous-rate approximation additionally assumes all recruitment enters active state `A`; `A→S` is the only stall transition at constant per-active rate `δ_stall`; there is no recovery; hazard `h` applies equally to `A` and `S`; there are no other exits/vacancy sources; and admissions refill removals at constant-census stationarity. Then `S/A≈δ_stall/h` and stalled fraction `≈δ_stall/(δ_stall+h)`; discrete values depend on event ordering. Define `b_total=Q/∫(A+S)dt`, `b_active=Q/∫A dt`, and `f_active=∫A dt/∫(A+S)dt`; under feasible refill `p_accept=h/b_total=h/(f_active b_active)≤1`, otherwise vacancies accumulate. Register active, recoverable-depleted, and absorbing-stalled organism-time and endpoint-complete stall cohorts. A basal recovery trickle or arrears rule is a new substrate mechanism requiring an explicit parameter, conservation ledger, finite time-to-recovery gate, and fresh effect-size analysis.

At long-life benchmark acceptance 0.03–0.10, 90–97% of attempts fail. Fourteen nominal instruction units per bout imply 140–466.67 units per accepted admission, including 126–452.67 failed-attempt units, before upkeep. The avoidable failed-attempt charge could exceed the reserve-scale extraction contrast, depending on the quantified extraction difference, reserve-to-fitness mapping, and realised attempt process; dominance is not established. No current instruction exposes vacancy state, so record vacancy avoidance as a potentially large inaccessible adaptation and scope any no-sensor result accordingly. Adding sensing later changes the selectable mechanism. A non-atomic sensor could reduce rejected attempts probabilistically but cannot guarantee that a vacancy survives until DIVIDE; guaranteed race elimination requires an atomic reservation/permit or proven scheduler persistence through DIVIDE. Such a change invalidates direct comparison with the no-sensor ecology.

**Closure of the hazard-only route:** exogenous turnover removes birth-caused incumbent death and makes physical lifespan settable, but it is insufficient for a clean fecundity assay when depletion causes absorbing loss of reproductive competence. The constructive diagnosis is an expressive limitation: the one-wallet substrate has no independent genomic variable for soma-versus-reproduction income allocation, while historical transfer τ conflates allocation with per-offspring provisioning and establishment. Further hazard-spec elaboration is paused rather than treating recoverable depletion as an unreported convenience. `stage-7-split-reserve-architecture.md` records a prospective semantic redesign that separates somatic reserve `S` from reproductive reserve `R`, routes realised extraction income through a heritable allocation fraction `α`, and keeps per-offspring provisioning `τ_R` distinct from historical transfer τ. Under its strong variant, reproduction-specific work and transfer draw from `R`; merely moving transfer to `R` while retaining ALLOC/COPY/DIVIDE costs in `S` does not solve the shared-wallet problem.

Any future study therefore requires either an explicitly coupled life-history question or a newly reviewed turnover, reserve-ledger, and recruitment architecture. Independent review classified the Stage 7 candidate as **NO-GO for implementation** until its somatic state machine, direct-debit order, exact-rational representation and trait encoding, gestation semantics, storage/death ledger, recruitment ecology, and fitness endpoint are normative. Neither the hazard-only ecology nor the Stage 7 candidate is authorized for implementation or assay execution by this document.
