# Stage 7B1 Preregistration: Transaction-Safe Publication, Terminal Retirement, Death Cleanup, and Registered Endpoint Definitions

**Protocol status:** SUPERSEDING preregistration. This document registers binding decisions for the six Stage 7B1 blockers identified against `stage-7-split-reserve-architecture.md` §11 falsification gates: (a) atomic child-publication transaction semantics and the injected-exception rollback test matrix; (b) packet retirement equations; (c) a proven no-eviction configuration; (d) hazard-death-with-live-gestation cleanup; (e) the invasion-growth/reproductive-value endpoint with cohort mediators and censoring rules; (f) the vacancy-capture estimand decision. It supersedes the design-only status of `stage-7b1-design.md`; that document is now a superseded design record and is immutable. Corrections to any decision registered here require a further superseding preregistration, not edits to either prior document.

**Evidence-era disclosure:** before this freeze, the following had been observed: the Stage 7B0 PASS result pair (`results/stage7b0/stage7b0-result.json`, SHA-256 `00315fab…ebddf`) under the scripted acquisition-allocation channel; the Slice 1/2A mechanics traces including the atomic `CHILD_MEMORY_UNAVAILABLE` DIVIDE pre-check (commit `7ab6dba`, formerly `f90da66`); the Slice 2A `unread_buffer_eviction` retirement path; and hazard removal with gestation release in `_hazard_remove`. The following had **not** been run at population level: any fault-injected DIVIDE transaction; retirement of a partially returned packet on holder death; any `would_admit` shadow counter; any raising buffer-overflow guard; any corpse-closure assertion beyond the existing 20-tick trace. No fitness, selection, invasion-growth, reproductive-value, or evolutionary observation exists in any Stage 7 artifact.

**Authorisation:** this document registers decisions and authorises exactly one execution class: a deterministic, mutation-disabled mechanics verification of the registered test matrix, after the freeze required by §9. It authorises no stochastic or inferential execution, no mutation, no open-genome evolution, and no fitness claim beyond the endpoint definitions of §6. The Blocker 3/5/6 parameters for any open-population or stochastic assay (`r`, `d`, `N`, window length, replicate count `k`, `Δr_min`, hazard arms, resolution `ρ_r`) are explicitly **deferred** to a later superseding preregistration that may be committed only after the deterministic verification PASSes and is retained and classified.

## 1. Registered question

For the transaction, retirement, cleanup, and guard decisions registered here:

1. does a DIVIDE publication implemented as the staged transaction of §2 leave every ledger exactly closed after **every** injected exception, with no partial child observable by census, scheduler, or any ledger;
2. does terminal packet retirement satisfy the §3 equations exactly once per packet, with physical destruction and provenance retirement kept separate;
3. does the registered configuration make buffer eviction impossible by construction and loud (run-invalidating) if the construction is violated;
4. does hazard death with a live gestation release every obligation exactly once and close census, reserve, memory, and packet ledgers at the registered checkpoints;
5. are the registered endpoint definitions of §6 well-posed on event-ledger data, with censoring rules that introduce no imputation; and
6. do shadow admission counters remain side-effect-free?

This is a mechanism-verification registration. It tests no evolutionary hypothesis and makes no fitness or selection claim.

## 2. Blocker A — atomic child-publication transaction

### 2.1 Registered stages

The DIVIDE publication path is a single transaction with named stages. Stage order is fixed; no stage may be reordered or merged:

| Stage | Act | Registered failure behaviour |
|---|---|---|
| `G` | validate the registered complete-gestation condition | fail: no child, no draw; bout retention/discard follows gestation semantics |
| `V` | atomically reserve one census vacancy (`vacancy_reserved` counter; invariant `live_census + vacancy_reserved ≤ capacity` at all times) | none available → reason `NO_VACANCY`; no provisioning computed |
| `M` | DIVIDE-level insertion/deletion/duplication draws build the post-indel candidate | exception: candidate discarded; consumed RNG stays consumed |
| `R` | release parent gestation; atomically reserve the child's full memory obligation from the post-indel candidate basis into the new `child_reserved` bucket | insufficient → reason `CHILD_MEMORY_UNAVAILABLE`; vacancy released; prepaid work retained |
| `P` | compute exact `P=(T/D)R_w`, debit provisionally, construct the provisional child (invisible to census, scheduler, and memory owners) | exception: refund `P` exactly; destroy provisional child |
| `C` | single commit point: publish child, convert reservations to ownership, emit `provision_committed` then `birth_admitted` | commit is atomic; no partial commit exists; no observable state lies between `P` and `C` |

Mutation remains disabled throughout Stage 7B1; the `M` stage draws are registered as structural (zero-draw) so the RNG-consumption invariants remain testable with the injection harness alone.

### 2.2 Registered rollback rule

For **any** injected exception after `V` and before `C`: release the vacancy reservation and the child-memory reservation; refund `P` exactly if it was provisionally debited; remove or never publish any partial child; discard candidate and gestation state; omit `P` from telemetry. Prepaid work (`C_S`/`C_R`) and consumed RNG are **not** refunded. The refund of `P` is the exact stored `Fraction` value, never recomputed.

### 2.3 Registered invariants (asserted after every rolled-back transaction)

- **I1** census unchanged; hazard/admission counters unchanged except the failure-stage record.
- **I2** memory ledger closes exactly: `free_pool + somatic_active + gestation + child_reserved + corpse_reserved = initial_memory_pool`. `SharedMemoryLedger` gains the explicit `child_reserved` bucket; `totals()` and `assert_closed()` include it.
- **I3** no census-, scheduler-, or ledger-visible reference to a partial child exists.
- **I4** parent `R` equals its pre-`P` value exactly (exact refund, not recomputation).
- **I5** prepaid work is retained: `c_s + c_r` is monotonically non-decreasing across the attempt and strictly greater than at transaction start once `G..P` charges occurred.
- **I6** the RNG counter equals its value at the injection point; no replay, no extra draw.
- **I7** the event log contains exactly one failure-stage record — event name `divide_failed`, fields `{tick, phase, organism_id, stage, reason}` — carrying no `provision` field and no successful-event fields. Registered `reason` values: `NO_VACANCY`, `CHILD_MEMORY_UNAVAILABLE`, `FAULT_INJECTED`.
- **I8** reserve, packet, memory, and census closures all close immediately after rollback.

### 2.4 Registered fault-injection matrix

A deterministic `FaultInjector` hook raises at each registered boundary; one fault per run; no in-run retry. Each faulted run is paired against a byte-identical clean control and asserts I1–I8:

| Test | Injection boundary |
|---|---|
| `test_rollback_after_vacancy` | post-`V` |
| `test_rollback_in_mutation` | mid-`M` |
| `test_rollback_after_mutation` | post-`M` |
| `test_rollback_in_child_memory` | mid-`R` |
| `test_rollback_after_child_memory` | post-`R` |
| `test_rollback_in_provisioning` | mid-`P` |
| `test_rollback_before_commit` | post-`P`, pre-`C` |
| `test_commit_is_atomic` | structural: no observable interleaving state exists between `P` and `C` |
| `test_no_stale_bout_retry` | after any failed attempt, a fresh `DIVIDE` cannot consume released/discarded gestation |
| `test_rng_consumption_survives_failure` | a subsequent unrelated draw observes the advanced counter |
| `test_child_memory_unavailable_is_atomic` | population-level regression lock for the `7ab6dba` behaviour |

This discharges architecture §12 trace 17.

## 3. Blocker B — packet retirement equations

### 3.1 Live identity and cumulative draws

Every packet ledger keeps the live identity `B(p) + D_S(p) + D_R(p) = B_init(p)` at all times. Registered cumulative-draw definitions: `D_S = Σδ_s − Σρ_s`, `D_R = Σδ_r − Σρ_r`, where returns `ρ` are split by **stored** provenance shares only.

### 3.2 Registered retirement event

When a packet loses its final tag (holder death or explicit destruction), emit exactly one `packet_retired` event `{tick, packet_id, holder_id, reason, destroyed_budget, retired_drawn_S, retired_drawn_R}` with `reason ∈ {HOLDER_DEATH, EXPLICIT_DESTROY}`, `destroyed_budget = B(p)⁻`, `retired_drawn_S = D_S(p)⁻`, `retired_drawn_R = D_R(p)⁻` (values at retirement). Decision: in every Stage 7B1 configuration the registered reason set is exactly `{HOLDER_DEATH, EXPLICIT_DESTROY}`. The legacy Slice 2A `unread_buffer_eviction` retirement path is unreachable under the §4 no-eviction configuration (the §4.1 guard raises before any eviction can occur); it is retained only in the unregistered Slice 2A 20-tick trace and is asserted never to fire in any 7B1 configuration.

### 3.3 Registered closure equations

1. `Σ_retired destroyed_budget` equals the total terminal packet destruction credited to the population `destroyed` sink — physical destruction is an energy sink exactly once.
2. Retired `drawn_S`/`drawn_R` are provenance bookkeeping only; they never re-enter reserve, memory, or packet ledgers and are never summed with `destroyed_budget`.
3. After retirement the `packet_id` belongs to a retired set; any later draw, return, or re-capture referencing it raises.
4. Unread buffered packets at window end retain `e_budget = e_initial` and are listed, not retired.

Registered tests: `test_retire_on_holder_death` (mid-cycle, partially returned provenance), `test_destroyed_budget_exact`, `test_double_retirement_raises`, `test_retired_provenance_not_a_sink`.

## 4. Blocker C — proven no-eviction configuration

### 4.1 Three registered layers

1. **Runtime guard:** `PacketBuffer.advance_tick()` raises (`BUFFER_OVERFLOW`) rather than silently discards on overflow; a triggered guard classifies the run `INVALID IMPLEMENTATION`.
2. **Per-tick assertion:** `buffered ≤ depth` checked inside the tick-complete closure.
3. **Static bound:** the registered configuration fixes `(packet_rate r, buffer depth d, capacity N, capture policy)` together with a written induction showing `cumulative_generated − cumulative_consumed ≤ d` is invariant.

### 4.2 Registered configuration for the deterministic verification

For the Stage 7B1 deterministic suite only: `r = 5` packets/tick (Slice 2A provisional constant), bounded registered window `W` ticks, `d = 5W + d_0` where `d_0` is the initial buffered count, and a fixture guaranteeing at least one live, unstalled member attempts capture on every tick (asserted per tick). The no-eviction proof for this configuration is then doubly redundant: (i) pigeonhole — even with zero consumption, `cumulative_generated = 5W ≤ d − d_0`, so the §4.1 guard cannot trigger; (ii) induction — with the per-tick capturer guarantee, whenever the buffer is non-empty at least one capture is attempted, so `cumulative_generated − cumulative_consumed` never exceeds the pigeonhole bound. Configurations that admit stalls breaking this bound may **not** be registered as no-eviction; open-population configurations fall back to layers 1–2 and are invalid on trigger, and their parameters are deferred per the Authorisation header.

Registered tests: `test_overflow_raises_not_drops`, `test_bound_holds_for_registered_fixture`, `test_all_stalled_triggers_guard` (a fixture with the capturer guarantee deliberately removed must trip layer 1 or 2, never drop silently).

## 5. Blocker D — hazard death with live gestation

Registered death ordering within tick `t`, extending the registered tick order (packet arrival → hazard → survivor snapshot/execution → corpse expiry → tick-complete):

1. mark member dead; exclude from the survivor snapshot;
2. retire any held packet per §3 with reason `HOLDER_DEATH`;
3. release live gestation bytes to `free_pool`, logged as `gestation_released` with `release_reason=HAZARD_DEATH`. No gestation upkeep is charged at the death tick: per architecture §5.3 an allocation released before the upkeep boundary is not charged;
4. terminal disposal: dissipate exact `S_o` and `R_o` into the population `destroyed` sink with one `death_disposal` event `{tick, organism_id, s_disposed, r_disposed}` carrying both exact amounts (no `S↔R` rescue, no inheritance);
5. create the corpse reservation (`corpse_reserved`) for the registered TTL (Slice 2A provisional `corpse_ttl = 2`); expiry returns the bytes to `free_pool` with a `corpse_expired` event;
6. update the census closure `founders + admitted_births − hazard_removals = live_census` and the reserve closure, whose RHS now includes terminal disposal inside `destroyed`.

Registered tests: `test_death_between_alloc_and_copy` (gestation live, work already sunk in `R`), `test_death_holding_packet`, `test_corpse_expiry_restores_memory_closure`, `test_death_disposal_exact`, `test_dead_member_not_scheduled`.

## 6. Blockers E and F — registered endpoint definitions and estimand decision

### 6.1 Genotype and primary endpoint (Blocker E)

- **Genotype:** heritable state `(A, T, D)` lineage; realised traits logged per event per architecture §9.6.
- **Primary endpoint:** per-genotype invasion growth `r_g`, the solution of Lotka's equation `Σ_x e^{−r·x} l_x(g) m_x(g) = 1`, reported as a certified rational bracket `[r_lo, r_hi]` with width below the registered resolution `ρ_r`. All ledger inputs (`l_x`, `m_x`, exposures) are exact `Fraction` quantities; the bracket is located by monotone sign bisection with certified rational error bounds. The replicate **distribution** of `r_g` is the estimand. No optimum, ESS, or background-invariant causal claim is registered or permitted.
- **Survival decomposition:** `l_x` measured separately for active, recoverable-depleted, and stalled states; sterile persistent founders and `R` hoarders accrue no `m_x` credit merely by census persistence.
- **Establishment rule:** `m_x` counts births established through **first reproduction** of the offspring. First-extraction establishment and age-at-fundable-bout are registered **mediators**, promoted to endpoints only if a registered life-cycle trace demonstrates they capture subsequent reproductive contribution (architecture §11 Endpoint gate).
- **Causal-chain telemetry:** realised `Y → Y_S/Y_R → age at fundable bout → attempt/vacancy exposure → P/S_birth → first extraction → first reproduction → subsequent reproductive contribution`, each stage distinguishable in output.
- **Censoring rules (binding):** right-censor at the registered window end; censored individuals contribute exposure time to `l_x` denominators and no `m_x` events; no imputation of any kind.
- **Power/effect size:** minimum contrast `Δr_min` and replicate count `k` are fixed in the executing preregistration before any execution; no post hoc endpoint substitution.
- **Calibration/confirmatory separation:** measurement code is calibrated against the retained 7B0 scripted blocks; the confirmatory configuration, seeds, and analysis script are frozen and hashed in the execution manifest; analysis is source-frozen.

These definitions are registered now and **exercised only after** their own superseding preregistration.

### 6.2 Vacancy-capture estimand decision (Blocker F)

**Decision:** binding vacancy capture **is part of the primary estimand** — it is realised recruitment under binding admission, which is the population question the Stage 7B1 machinery ultimately serves. To keep intrinsic and capture-mediated components separable:

- every admission decision also records a **nonbinding shadow outcome** (`would_admit`): whether the birth would have been admitted had capacity been available. Shadow counters are pure telemetry; they touch no census, memory, packet, or reserve state (enforced by construction and by `test_shadow_counters_side_effect_free`);
- reported separately: bout-completion rate (intrinsic), vacancy-capture rate (ecology), and their product as realised recruitment;
- any hazard-gradient external-validation claim additionally satisfies architecture §9.5 items 1–5, including factorial separation of hazard exposure and recruitment opportunity; failing that, outcomes are labelled combined mortality–turnover responses.

## 7. Cross-cutting telemetry obligations

Implementations must extend event payloads to the architecture §9.6 minimum set: inherited `A/D` and `T/D`, ancestry ID, genotype hash, realised `Y`, pre/post `S` and `R`, required vs debited `C_S`/`C_R` separately, exact gestation upkeep, failure stage/reason, gestation bytes and release reason, vacancy reservation, post-indel candidate memory basis and child-memory reservation, COPY- and DIVIDE-stage RNG-consumed flags, `R_w`, child initial `S/R`; draw/reversal payloads carry packet ID, lifetime `A/D`, exact pre/post budget and `drawn_S/drawn_R`, requested vs debited amounts, transform codes, and commitment flags. `P` appears **only** on committed provisioning; failed events omit it rather than reporting a numeric zero. All rationals serialise as exact `num/den` strings. Telemetry labels (`LOW`, `HIGH`, ancestry IDs) are never read by reserve, packet, memory, transition, scheduler, hazard, admission, or cost logic.

## 8. Standing-rules compliance

Exact `Fraction` arithmetic in every ledger; the §6.1 solver's interval arithmetic is analysis-side and must certify rational brackets without ever feeding approximations back into a ledger. No pre-Stage-7 optimum, carrying capacity, lifespan, or effect size is reused (architecture §10 invariant 9). Failed designs are archived under `failed-designs/`, never deleted. Retained artifacts and superseded documents are immutable.

## 9. Freeze-before-execution and authorised execution class

1. **Implementation window (authorised now):** implement Blockers 1–4 mechanics and the full registered test matrix of §§2–5 plus `test_shadow_counters_side_effect_free`, as unexecuted code. No registration is needed for unexecuted code; this preregistration is that registration once the code runs.
2. **Freeze:** implementation, runner, tests, output schema, and analysis are frozen **together** in one commit carrying a pre-execution manifest (SHA-256 + byte size per frozen file, `df7b1f5` precedent) at `results/stage7b1/pre-execution-manifest.json`, committed before any retained execution.
3. **Authorised execution class:** one deterministic, mutation-disabled verification suite covering the fault-injection matrix, retirement equations, death/corpse cleanup, and no-eviction guards, with all ledgers asserted closed at every registered checkpoint. Raw output is retained under `results/stage7b1/` and classified under the architecture §9 repair policy.
4. **PASS criterion:** every registered assertion of §§2–5 holds on every registered run; any failure classifies the run and triggers the repair policy; a failed design is archived, not deleted.
5. **Post-PASS gate:** only after a retained, classified PASS may a separate superseding preregistration fix the Blocker 3/5/6 parameters (`r`, `d`, `N`, window, `k`, `Δr_min`, hazard arms, `ρ_r`) for any stochastic or inferential execution.

## 10. Not authorised by this document

Dedicated-locus mutation; open-genome evolution; any stochastic or inferential execution; any fitness, selection, optimum, or ESS claim beyond the §6.1 definitions; reuse of pre-Stage-7 effect sizes (§10.9); modification of retained artifacts or superseded documents; history rewrites.
