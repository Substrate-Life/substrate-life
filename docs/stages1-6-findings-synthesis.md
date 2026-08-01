# Substrate: Consolidated Findings Synthesis

*Consolidated result ledger for Stages 1–6 and four methodological findings*
*Date: 2026-08-01*

## Status and dependency boundary

The nine findings below are complete at the level stated here. The five substrate and life-history findings derive from Stages 1–6. The four methodological findings derive from the project's design and verification history through deterministic Stage 7B0. None requires a stochastic Stage 7 allocation assay, an evolved allocation response, or a completed real-host coupling experiment.

Further Stage 7 work may provide a cleaner architecture for asking new questions. It cannot retroactively create, erase, or strengthen the evidence summarized below. Historical artifacts remain evidence only for the source semantics under which they were generated; superseded mechanisms are not silently reclassified as current-mechanism results.

## Executive synthesis

Substrate did not fail because selection was absent. It exposed a hierarchy of architectural constraints on what selection could express and what an assay could identify.

1. **Fitness currency is lifecycle- and regulator-specific.** Energetic surplus, nominal offspring capacity, attempted births, and first reproduction are not interchangeable with population fitness.
2. **Instruction-by-instruction copying structurally suppresses fecundity.** Processive copying is required before surplus can be expressed as multiple offspring without copy time dominating the lifecycle.
3. **The reserve margin relative to pre-income spending controls the observable selection regime.** Tight margins turn small costs into threshold culling; wider margins permit graded frequency change.
4. **Income has no architecture-independent fitness meaning.** Surplus matters only through an implemented route to timing, persistence, provisioning, establishment, or subsequent reproduction.
5. **A shared reserve makes fecundity and viability causally coupled.** Reproductive work, parental persistence, offspring provisioning, and offspring establishment compete through the same account.
6. **Interpretability and evolutionary openness are in tension.** Freezing backgrounds and ecology identifies channels while narrowing the open-ended evolutionary claim.
7. **Specification review and executable validation are asymmetric.** Review made conservation requirements legible; the smallest complete execution exposed mechanism defects that additional wording review had not.
8. **Conservation closure is necessary but not sufficient for ecological validity.** Exact ledgers can certify honest bookkeeping while the implementation omits the resource interaction the experiment is meant to study.
9. **Verification apparatus must match the experiment's threat model.** Deterministic fixed-input traces obtain their anti-selection guarantee from exact reproduction; one-use execution and prospective seed controls are proportionate when stochastic or inferential degrees of freedom exist.

---

## Finding 1 — Fitness currency must follow the complete population lifecycle

**Claim.** The relevant fitness currency is population growth under the registered ecology—normally invasion growth or reproductive value. Age-specific lifetime established recruitment is a required pathway measure and can be a conditional proxy only when the lifecycle demonstrates that it captures subsequent reproductive contribution. Isolated-parent reproductive capacity, nominal births per cycle, reserve, energetic income, first extraction, and first reproduction are not population fitness by themselves.

**Basis.** In the pre-COPY_BLOCK binary-fission architecture, `r=ln(2)/T` is a valid benchmark only under equal cycle time, survival, establishment, and subsequent contribution. Once generations overlap and census regulation acts through displacement, hazard, memory, or vacancies, fitness depends on survival to each bout, offspring establishment, age structure, victim/admission rules, and later reproduction. The shortcut `ln(1+k)/T(k)` therefore does not describe the capped overlapping-generation process merely because an isolated parent can produce `k` offspring.

**Measured/inferred boundary.** Birth, first extraction, first DIVIDE, realised bout count, and established recruitment are measurable lifecycle events. Their relationship to invasion growth must be demonstrated under the registered regulator rather than assumed.

**Does not establish.** It does not privilege one universal scalar endpoint for every ecology. It establishes that the endpoint must be derived from the actual population process and that intermediate energetic or demographic quantities cannot be converted directly into a selection coefficient.

## Finding 2 — Replication cost is an architectural constraint, not a tuning detail

**Claim.** Under one-instruction-per-tick execution with instruction-by-instruction genomic copy loops, copy time structurally suppresses a multiple-offspring fecundity route. A processive replication primitive is required to decouple elapsed copy time from genome length while retaining a length-dependent energetic cost.

**Basis.** At genome length `L=11`, the original copy loop consumed 26 ticks per offspring. Even at the floor of one tick per instruction, the registered comparison gave `k=1` a growth benchmark of `0.0210` versus `0.0193` for `k=2`, an approximately 8% advantage. Parameter retuning could not open a substantial fecundity advantage while the serial copy loop remained the dominant time cost. `COPY_BLOCK` changed the architecture: copying became processive in time while energetic work still scaled with copied length.

**Evidential class.** Structural derivation plus executable implementation evidence that processive copying permits multi-DIVIDE behavior.

**Scope.** The result applies to this instruction scheduler and to analogous systems where reproduction executes a genome serially and copy time dominates the lifecycle. It is not a claim that every digital-evolution platform must implement the same opcode.

**Does not establish.** Enabling multiple offspring does not establish that higher isolated-parent `k` is favored in a regulated population. It creates an expressible route; population fitness still depends on survival, provisioning, establishment, and regulation.

## Finding 3 — The reserve-margin/trough ratio controls whether selection appears graded or threshold-like

**Claim.** The ratio between post-cycle reserve margin `R*` and spending required before the next positive extraction is a control parameter for the observable selection regime. Tight margins convert incremental costs into demographic failure; wider margins permit graded frequency change.

**Basis.** At `E=129`, the registered model had `R*=49.7`, pre-income spending near `18.4`, and a ratio around `2.7`; added costs pushed lineages into Phase-B failure and produced threshold culling. At `E=300`, the margin was around five times the pre-income spend at the tested run density, and the waste-TRANSFORM treatment showed a graded decline: its frequency was 32.1% at the preregistered `t=1000` checkpoint (inconclusive by the registered pass/fail rule) and 13.7% in the explicitly post-hoc `t=2000` extension.

**Evidential class.** Measured regime contrast with a structural energy-ledger explanation.

**Scope.** The observations support the direction that wider reserve margins expose graded cost differences and tight margins produce viability cliffs. They do not identify a universal threshold, a smooth functional form, or a context-free selection coefficient. The original static `OFFSPRING_TROUGH=18` interpreter gate is not part of this finding and was removed; actual pre-income spending is path-, genome-, memory-, and scheduler-dependent.

## Finding 4 — Income is architecturally contingent

**Claim.** Energetic surplus has no architecture-independent mapping to fitness. It matters only if the organism and population process expose a route through which income changes cycle time, survival, reproductive work, offspring provisioning, establishment, or later reproductive contribution.

**Basis.** In the original obligate one-offspring architecture, once both competitors cleared the viability gate and had equal cycle time and establishment, earning 300 rather than 100 had no continuous expression route: both followed the same binary-fission benchmark. `COPY_BLOCK` later demonstrated an organism-level route by allowing surplus to fund additional copied offspring when a third bout was encoded. That deterministic capacity trace did not establish equilibrium population fitness.

The withdrawn `E=300` versus `E=500` monoculture comparison illustrates the ecological side of the same result. Under density regulation at carrying capacity, increasing environmental supply primarily changes carrying capacity; per-capita income is driven back toward per-capita cost. Separate monocultures therefore cannot identify an organism-level efficiency advantage, and the saved treatment artifact also failed live-treatment verification.

**Evidential class.** Structural mechanism result, supported by deterministic capacity traces and by failure analysis of an invalid assay.

**Scope.** This is not a claim that metabolic efficiency is generally unselectable. It is a claim that the channel must be implemented and verified rather than inferred from income alone. A valid efficiency test requires competing genotypes in one population and packet stream, with genotype-specific lifecycle outcomes.

## Finding 5 — The shared reserve couples fecundity and viability

**Claim.** In the Stage 6 one-wallet architecture, fecundity and viability cannot be interpreted as independent axes. Reproductive work, parental persistence, offspring provisioning, and offspring establishment all debit or depend on the same reserve.

**Basis.** `COPY_BLOCK` successfully enabled multiple DIVIDEs: a historical threshold-18 population snapshot found realised bout count `k≈3` among reproducers. This remains evidence that `COPY_BLOCK` enabled multi-DIVIDE behaviour in that source state; it is not a current no-threshold fecundity estimate. The same reserve funded continued execution, copy/DIVIDE work, transfer to offspring, and the offspring's pre-income runway. Changing transfer or bout count therefore altered offspring quality, parental runway, and establishment together.

Removing the hidden offspring threshold made the coupling visible instead of interpreter-adjudicated. Every materially allocatable copied offspring was instantiated with its actual transfer. Cheap under-provisioned offspring could still consume memory and, under the Stage 6/current hard-cap regulator, remove live incumbents before dying. Parent immunity was removed, yet two-seed, mutation-free, one-cycle censored smoke runs recorded 338 live displacements, of which 144 were resolved as caused by offspring that died before first extraction; 108 causing-offspring outcomes remained unresolved at the trace boundary, and one victim was a reproducing parent. This established that the displacement channel was materially active; it did not establish dominance or an evolutionary optimum.

Analytically and prospectively, a constant exogenous hazard can separate one component—physical removal—from births, but cannot by itself separate reproductive competence from reserve depletion. An organism unable to fund the recovery path can remain alive yet reproductively stalled. The correct architectural diagnosis was therefore not that fecundity and viability should be made independent, but that the one-wallet system lacked an explicit evolvable allocation vocabulary between them.

**Evidential class.** Conservation-ledger mechanism result plus regulator smoke evidence.

**Does not establish.** The historical threshold-era `τ≈20%` competition is not a current estimate of an optimum; the no-threshold FULL-monomorphic displacement smoke is non-comparative and not selection evidence; and the snapshot non-reproducer fraction is censored, not cohort mortality.

---

## Methodological finding 1 — Constraint and openness are in tension

**Claim.** Assays become interpretable by freezing genomes, loci, schedules, mediators, or ecology, but those controls narrow the open evolutionary claim that motivated the system.

**Basis.** Fixed-genotype contrasts identified transform costs and capacity routes. Restricted-locus designs can identify whether a specified channel is expressible. Neither alone establishes what an open population will evolve when extraction, timing, provisioning, genomic background, and ecological exposure coevolve.

**Required evidential separation.**

1. **Channel exists:** the mechanism can alter a registered lifecycle quantity.
2. **Restricted architecture evolves through it:** evolution under a constrained genotype/trait space uses that channel.
3. **Open population outcome:** replicate populations under a specified mutation kernel and ecology produce a distribution of joint outcomes in which the channel participates.

Evidence at one level cannot substitute for the next. Open evolution need not converge to a unique strategy or ESS, and descriptive selection on `α` would not by itself identify the direct causal effect of `α` with mediators and ecological exposure held fixed.

## Methodological finding 2 — Review and execution have asymmetric strengths

**Claim.** Once conservation, atomicity, causal intent, and explicit provisional defaults were coherent, the smallest dependency-complete execution found material mechanism errors that further specification review had not found.

**Measured first use of the stop-rule.** The Stage 7 transaction specification passed independent review. Slice 1 execution then exposed three defects:

1. extraction and reversal quantities were synthetic rather than derived from live transform geometry;
2. reversal reconstructed debits from current `α` rather than stored original-account provenance;
3. transform memory and state-dependent costs were absent from the ledger.

After correction, the isolated reserve, packet-provenance, and shared-memory ledgers closed exactly and the final-hash independent audit passed.

**Interpretation.** This validates the project's stop-rule on its first use: after analytic invariants and provisional normative choices are explicit, implement the smallest complete vertical slice and reopen a choice when execution exposes a contradiction, exploit, unintended coupling, or changed estimand.

**Limitation.** The result does not show that specification review is dispensable. Review supplied the invariants that made executable failure diagnosable. Nor does a passing ledger establish evolutionary or scientific validity. Review and execution answer different questions; the methodological error was allowing further wording review to substitute for running a coherent mechanism.

## Methodological finding 3 — Conservation does not establish that the intended ecology exists

**Claim.** Exact conservation is necessary for an energetically interpretable simulation, but it cannot establish that the implemented interaction topology matches the scientific ecology. A model can close every resource ledger while deleting the competition or exposure process that gives the proposed measurement meaning.

**Measured case.** The first Slice 2A population harness generated a fresh rich packet inside each organism's cycle. Its population reserve ledger, per-packet provenance ledgers, and shared-memory ledger all closed exactly. Nevertheless, packet supply scaled with the number of scheduled organisms: no organism consumed from a common finite queue, later organisms could not encounter resource depletion caused by earlier organisms, and the intended capture competition was absent. The harness was therefore non-diagnostic for population resource competition despite being perfectly conserved.

The correction reused one globally consumptive packet buffer with five exogenous arrivals per tick. Successful READ removed a packet from that shared buffer; scheduler order and prior capture could leave a later organism with no packet. The corrected mechanics trace then recorded packet-capture failures while reserve, provenance, unread-buffer, and memory closure still held.

**Interpretation.** Conservation and ecological validity are orthogonal verification axes. Closure asks whether the implemented boundaries create, lose, or double-count resources. Ecological validation asks whether resource arrival is exogenous where intended, supply is shared rather than cloned, consumption is exclusive, interactions occur at the registered population scale, and organisms experience the intended contention and scheduler exposure. Both must pass before a population result is scientifically interpretable.

**Limitation.** This does not weaken the conservation requirement: without closure, even the intended ecology is energetically uninterpretable. Nor does the cloned harness measure literally nothing; it still exercises isolated per-organism mechanics. The narrower result is that exact bookkeeping alone cannot validate the intended ecological estimand. A conservation proof certifies honesty about the implemented system, not relevance of that system to the scientific question.

## Methodological finding 4 — Verification apparatus must match the experiment's threat model

**Claim.** Verification controls are rigorous only when they address researcher degrees of freedom that the specific experiment actually has. Preregistration, seed freezes, one-use execution, and prospective digest authorization guard against selective reporting, post-hoc tuning, and repeated stochastic sampling. A deterministic trace with fixed inputs and endpoints has no seed or outcome-selection freedom; its primary threat is that the implementation or reducer does not do what it claims.

**Measured case.** Stage 7B0 fixed both treatments, packet identities, packet schedules, ticks, programme, and mutation-off execution. Before any block ran, three increasingly elaborate freeze designs accumulated one-use leases, filesystem claims, detached digest authorization, Git-blob checks, a partial schema engine, and append-only journal machinery. Simplifying the path deleted 2,234 lines and added 195 replacement lines. The first two direct executions then exposed two material defects: a checkpoint retained a live reference to a mutable event list, and the independent reducer's debit whitelist rejected registered somatic operations. The former authorization apparatus checked identity and execution exclusivity; it neither exercised nor semantically reconstructed those paths. Both defective artifacts were retained, the defects were corrected with focused regressions, and the final trace passed all reconstructed gates and reproduced byte-for-byte.

**Interpretation.** Protection should be selected from the experiment's actual failure modes. For deterministic fixed-input work, source hashes, raw evidence, semantic reduction, adversarial tests, preservation of failures, and exact reruns directly test the live risks. Ceremony that only prevents rerunning cannot add an anti-selection guarantee when every rerun must produce the same bytes. For stochastic Stage 7B1, by contrast, seed choice, capture variance, repeated sampling, and inferential endpoints restore the threats for which prospective freezes and one-use controls are proportionate.

**Limitation.** Determinism does not establish correctness: it can reproduce the same bug indefinitely. The guarantee is useful only with inspectable source, raw evidence, independent reconstruction, and tests aimed at semantic failure. Nor does this finding argue against preregistration generally. It argues that each control must name the degree of freedom or adversary it constrains, and that its cost should be justified against that threat.

---

## What remains outside this write-up

- Stage 7 split-reserve population mechanics and deterministic Stage 7B0 verification inform the methodological findings; they do not establish an evolutionary result.
- No stochastic allocation-versus-hazard assay is reported here.
- No claim is made about evolved `α`, dominance, ESS, convergence, or a causal allocation gradient.
- Real-host coupling remains untested.

The findings above remain recoverable even if Stage 7 stops. Future work can add evidence, but it must not rewrite these scoped results as stronger claims than the retained measurements and mechanisms support.
