# Stage 7B1 Design: Transaction Safety, Retirement Accounting, Death Cleanup, and Endpoint Definitions

**Status:** design only. This document registers *how* each preregistration §11 blocker will be met. It authorises no implementation-freeze and no execution. Per the Stage 7B0 PASS scope, a superseding Stage 7B1 preregistration must be committed before any registered block runs, and any stochastic or inferential execution requires its own separate freeze.

**Inputs:** the classified Stage 7B0 result pair (`results/stage7b0/stage7b0-result.json`, SHA-256 `00315fab…ebddf`, independent audit PASS with second-auditor addendum) establishes the scripted acquisition-allocation channel at the registered treatment points. It does not establish exception-safe child publication, terminal packet/provenance retirement, general death/corpse cleanup, or any fitness endpoint.

**Standing rules:** exact `Fraction` arithmetic everywhere; telemetry labels (`LOW`, `HIGH`, ancestry IDs) are never read by reserve, packet, memory, transition, scheduler, hazard, admission, or cost logic; failed designs are archived under `failed-designs/`, never deleted; retained artifacts and superseded documents are immutable.

## 1. Blocker 1 — atomic child-publication transaction

The DIVIDE publication path is redesigned as a single transaction with named stages, following architecture §7 steps 1–7:

| Stage | Act | Failure behaviour |
|---|---|---|
| `G` | validate the registered complete-gestation condition | fail: no child, no draw, bout retention/discard fixed with gestation semantics |
| `V` | atomically reserve one census vacancy | none available → `NO_VACANCY`; no provisioning computed |
| `M` | DIVIDE-level insertion/deletion/duplication draws build the post-indel candidate | exception: candidate discarded, consumed RNG stays consumed |
| `R` | release parent gestation; atomically reserve the child's full memory obligation from the post-indel candidate basis | insufficient → `CHILD_MEMORY_UNAVAILABLE`; vacancy released; prepaid work retained |
| `P` | compute exact `P=(T/D)R_w`, debit provisionally, construct the provisional child (invisible to census, scheduler, and memory owners) | exception: refund `P` exactly, destroy provisional child |
| `C` | single commit point: publish child, convert reservations to ownership, emit `provision_committed` then `birth_admitted` | commit is atomic; no partial commit exists |

Registered rollback rule for **any** injected exception after `V` and before `C`: release the vacancy and child-memory reservations, refund `P` if it was provisionally debited, remove or never publish any partial child, discard candidate and gestation state, omit `P` from telemetry. Prepaid work (`C_S`/`C_R`) and consumed RNG are **not** refunded.

### 1.1 Invariants asserted after every rolled-back transaction

- I1 census unchanged; hazard/admission counters unchanged except the failure-stage record.
- I2 memory ledger closes exactly: `free_pool + somatic_active + gestation + child_reserved + corpse_reserved = initial_memory_pool`, with a new explicit `child_reserved` bucket so provisional reservations are visible without being ownership.
- I3 no census-, scheduler-, or ledger-visible reference to a partial child exists.
- I4 parent `R` equals its pre-`P` value exactly (refund is exact, not recomputed).
- I5 prepaid work is retained: `c_s + c_r` is monotonically non-decreasing across the attempt and strictly greater than at transaction start once `G..P` charges occurred.
- I6 the RNG counter equals its value at the injection point; no replay, no extra draw.
- I7 the event log contains exactly one failure-stage record carrying the stage reason code and **no** `provision` field; successful-event fields absent.
- I8 reserve, packet, memory, and census closures all close immediately after rollback.

### 1.2 Registered fault-injection test plan

A deterministic `FaultInjector` hook raises at each registered boundary (one fault per run, no in-run retry). Each test pairs a faulted run against a byte-identical clean control:

- `test_rollback_after_vacancy`, `test_rollback_in_mutation`, `test_rollback_after_mutation`, `test_rollback_in_child_memory`, `test_rollback_after_child_memory`, `test_rollback_in_provisioning`, `test_rollback_before_commit` — each asserts I1–I8;
- `test_commit_is_atomic` — no observable interleaving state exists between `P` and `C`;
- `test_no_stale_bout_retry` — after any failed attempt a fresh `DIVIDE` cannot consume released/discarded gestation;
- `test_rng_consumption_survives_failure` — a subsequent unrelated draw observes the advanced counter;
- `test_child_memory_unavailable_is_atomic` — regression lock for the existing `f90da66` behaviour at population level.

This satisfies architecture §12 trace 17 (no vacancy/memory leak, no published partial child, refunded provisional `P`, omitted transfer telemetry, discarded gestation/candidate state, retained work and RNG consumption).

## 2. Blocker 2 — packet retirement equations

Every packet ledger keeps the live identity `B(p) + D_S(p) + D_R(p) = B_init(p)` at all times (already gate-checked in 7B0). New registered quantities:

- cumulative draws: `D_S = Σδ_s − Σρ_s`, `D_R = Σδ_r − Σρ_r`, where returns `ρ` split by **stored** provenance shares only;
- terminal retirement: when a packet loses its final tag (holder death or explicit destruction), emit exactly one `packet_retired` event `{tick, packet_id, holder_id, reason ∈ {HOLDER_DEATH, EXPLICIT_DESTROY}, destroyed_budget = B(p)⁻, retired_drawn_S = D_S(p)⁻, retired_drawn_R = D_R(p)⁻}`.

Registered closure equations:

1. `Σ_retired destroyed_budget` equals the total terminal packet destruction credited to the population `destroyed` sink — physical destruction is an energy sink exactly once.
2. Retired `drawn_S/drawn_R` are provenance bookkeeping only; they are never re-entered into reserve, memory, or packet ledgers, and never summed with `destroyed_budget`.
3. After retirement the `packet_id` belongs to a retired set; any later draw, return, or re-capture referencing it raises.
4. Unread buffered packets at window end retain `e_budget = e_initial` and are listed, not retired.

Tests: `test_retire_on_holder_death` (mid-cycle, partially returned provenance), `test_destroyed_budget_exact`, `test_double_retirement_raises`, `test_retired_provenance_not_a_sink`.

## 3. Blocker 3 — no-eviction configuration

Three registered layers, so that either eviction is impossible or it is loud and invalidating:

1. **Runtime guard:** buffer `advance_tick()` raises rather than silently discards on overflow; the run is classified `INVALID IMPLEMENTATION`.
2. **Per-tick assertion:** `buffered ≤ depth` checked inside the tick-complete closure.
3. **Static bound:** the eventual preregistration fixes `(packet_rate r, buffer depth d, capacity N, capture policy)` together with a written induction showing `cumulative_generated − cumulative_consumed ≤ d` is invariant — consumption is at least `generated − d` each tick because whenever the buffer is non-empty at least one live, unstalled member attempts capture under the stable-ID scheduler. Configurations that admit stalls breaking the bound may not be registered as no-eviction; they fall back to layer 1/2 and are invalid on trigger.

Tests: `test_overflow_raises_not_drops`, `test_bound_holds_for_registered_fixture`, `test_all_stalled_triggers_guard`.

## 4. Blocker 4 — hazard death with live gestation

Death ordering within tick `t`, extending the registered tick order (packet arrival → hazard → survivor snapshot/execution → corpse expiry → tick-complete):

1. mark member dead; exclude from the survivor snapshot;
2. retire any held packet per Blocker 2 with reason `HOLDER_DEATH`;
3. release live gestation bytes to `free_pool`, logged `release_reason=HAZARD_DEATH`. No gestation upkeep is charged at the death tick: per architecture §5.3 an allocation released before the upkeep boundary is not charged;
4. terminal disposal: dissipate exact `S_o` and `R_o` into the population `destroyed` sink with one `death_disposal` event carrying both exact amounts (no `S↔R` rescue, no inheritance);
5. create the corpse reservation (`corpse_reserved`) for the registered TTL; expiry returns the bytes to `free_pool` with a `corpse_expired` event;
6. update census closure `founders + admitted_births − hazard_removals = live_census` and the reserve closure, whose RHS now includes terminal disposal inside `destroyed`.

Tests: `test_death_between_alloc_and_copy` (gestation live, work already sunk in `R`), `test_death_holding_packet`, `test_corpse_expiry_restores_memory_closure`, `test_death_disposal_exact`, `test_dead_member_not_scheduled`.

## 5. Blocker 5 — invasion-growth / reproductive-value endpoint

Definition staged now; exercised only after its own preregistration:

- **Genotype:** heritable state `(A, T, D)` lineage; realised traits logged per event (§9.6).
- **Primary endpoint:** per-genotype invasion growth `r_g`, the exact solution of Lotka's equation `Σ_x e^{−r·x} l_x(g) m_x(g) = 1`, reported as a rational bracket `[r_lo, r_hi]` with width below the registered resolution; the replicate **distribution** of `r_g` is the estimand. No optimum, ESS, or background-invariant causal claim.
- **Survival decomposition:** `l_x` measured separately for active, recoverable-depleted, and stalled states; sterile persistent founders and `R` hoarders accrue no `m_x` credit merely by census persistence.
- **Establishment rule:** `m_x` counts births established through **first reproduction** of the offspring. First-extraction establishment and age-at-fundable-bout are registered mediators, promoted to endpoints only if a registered life-cycle trace demonstrates they capture subsequent reproductive contribution.
- **Causal chain telemetry:** realised `Y → Y_S/Y_R → age at fundable bout → attempt/vacancy exposure → P/S_birth → first extraction → first reproduction → subsequent reproductive contribution`, each stage distinguishable in output.
- **Censoring:** right-censor at the registered window end; censored individuals contribute exposure time to `l_x` denominators and no `m_x` events; no imputation.
- **Power/effect size:** minimum contrast `Δr_min` and replicate count `k` fixed in the preregistration before execution; no post hoc endpoint substitution.
- **Calibration/confirmatory separation:** measurement code is calibrated against the retained 7B0 scripted blocks; the confirmatory configuration, seeds, and analysis script are frozen and hashed in the execution manifest; analysis is source-frozen.

## 6. Blocker 6 — vacancy-capture estimand decision

**Decision:** binding vacancy capture **is part of the primary estimand** — it is realised recruitment under binding admission, which is the population question Stage 7B1 machinery ultimately serves. To keep intrinsic and capture-mediated components separable:

- every admission decision also records a **nonbinding shadow outcome** (`would_admit`): whether the birth would have been admitted had capacity been available. Shadow counters are pure telemetry — they touch no census, memory, packet, or reserve state (enforced by construction and by `test_shadow_counters_side_effect_free`);
- reported separately: bout-completion rate (intrinsic), vacancy-capture rate (ecology), and their product as realised recruitment;
- any hazard-gradient external-validation claim additionally satisfies architecture §9.5 items 1–5, including factorial separation of hazard exposure and recruitment opportunity; failing that, outcomes are labelled combined mortality–turnover responses.

## 7. Cross-cutting telemetry obligations

Implementations must extend event payloads to the §9.6 minimum set: inherited `A/D` and `T/D`, ancestry ID, genotype hash, realised `Y`, pre/post `S` and `R`, required vs debited `C_S`/`C_R` separately, exact gestation upkeep, failure stage/reason, gestation bytes and release reason, vacancy reservation, post-indel candidate memory basis and child-memory reservation, COPY- and DIVIDE-stage RNG-consumed flags, `R_w`, child initial `S/R`; draw/reversal payloads carry packet ID, lifetime `A/D`, exact pre/post budget and `drawn_S/drawn_R`, requested vs debited amounts, transform codes, and commitment flags; `P` appears **only** on committed provisioning. All rationals serialise as exact `num/den` strings.

## 8. Sequencing and authorisation boundary

1. Implement Blockers 1–4 mechanics and the full test register above (no registration needed for unexecuted code).
2. Freeze implementation + runner + tests + schema + manifest; execute a **deterministic, mutation-disabled** verification suite analogous to Stage 7B0 covering the new paths (fault-injection matrix, retirement, death/corpse); retain and classify the raw artifact under the §9 repair policy.
3. Only after that PASS may a separate, superseding preregistration fix the Blockers 3/5/6 parameters (`r`, `d`, window, `k`, `Δr_min`, hazard arms) for any stochastic or inferential execution.

Nothing here authorises dedicated-locus mutation, open-genome evolution, fitness claims beyond the registered endpoint definitions, or reuse of pre-Stage-7 effect sizes (invariant §10.9).
