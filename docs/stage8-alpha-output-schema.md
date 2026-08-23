# Stage 8 Alpha-Evolution Output Schema

*Fixed before any execution at the registered ecology
(`docs/stage-8-alpha-evolution-preregistration.md` §7(1) implementation
window). This document pins the field-level content of raw artifacts written
by `src/run_stage8_alpha.py` and reduced artifacts written by
`src/reduce_stage8_alpha.py`, plus the exact descriptive definitions of every
co-reported quantity. Nothing here may change after the confirmatory suite
runs; the descriptive definitions below are committed pre-execution so no
co-report has post hoc freedom.*

All exact quantities are serialised canonically as `"num/den"`
(Fraction arithmetic end-to-end). Kernel draws are integers on the dedicated
stream and never enter ledgers.

## 1. Raw artifact (`results/stage8-alpha-evolution/<name>.json`)

| Field | Type | Content |
|---|---|---|
| `protocol` | string | Constant `stage-8-alpha-evolution-preregistration`. |
| `evidence_class` | string | Fixed scope sentence; defers all interpretation to the reducer. |
| `seed_table` | string | `"confirmatory"` or `"shakedown"`. |
| `seed_table_derivation` | string | e.g. `hazard_seed = 20284617 + i, i in 0..23`. |
| `mutation_enabled` | bool | Always `true` (this stage's treatment). |
| `registered_configuration` | object | Echo of §2-3 binding values from `stage8_population.registered_configuration()`. |
| `source_manifest_sha256` | map filename → sha256 | Every file listed in `run_stage8_alpha.FROZEN_SOURCES`; the freeze manifest pins these hashes. |
| `execution_class` | string | Registered execution class of the run. |
| `replicates` | array of objects | One per replicate, in registered table order (§2). |
| `integrity` | object | Carried ledger-integrity statements; kernel-draw rollback semantics asserted. |
| `decision` | string | Literal `PENDING_REDUCTION`. |
| `decision_scope` | string | Fixed deferral statement. |

### 1.1 Per-replicate record

Common fields (all classifications):

| Field | Content |
|---|---|
| `seed_table`, `replicate_index`, `hazard_seed` | Table membership and registered seed. |
| `classification` | `COMPLETE` or `INVALID_IMPLEMENTATION` (carried classifier; `reason` ∈ `BUFFER_OVERFLOW`, `UNEXPECTED_EXCEPTION`). |
| `ticks_completed` | Steps finished before classification. |

Additional fields when `COMPLETE`:

| Field | Content |
|---|---|
| `window_ticks` | Registered `W = 2400`. |
| `alpha_end` | **Primary endpoint** `ᾱ_end = mean(A/255)` over live members at tick-W census close, exact Fraction; equal weight over active and stalled members alike. |
| `direction_class` | `mover_up` / `mover_down` / `non_mover` per §4 floor `8/255` vs `α_ref = 153/255` (`stage8_alpha_measure.direction_class`). |
| `extinct` | True iff zero live members at tick W (such a replicate is direction-ineligible and outside `k_eff`). |
| `terminal_census` | Full tick-W snapshot (§1.2). |
| `trajectory_checkpoints` | 20 entries `{tick, n_live, alpha_mean, distinct_A_values}` at ticks 120…2400 step 120. |
| `mutation_telemetry` | Kernel reconciliation block (§1.3). |
| `kernel_draw_chain` | Ordered entries `{stream_position, mutated, delta, draws_consumed}`, one per Stage-M decision; the G3 replay substrate. |
| `genome_freeze_audit` | Trait-isolation evidence (§1.4). |
| `mediators` | Carried 7B1 §6.2 mediator definitions via `stage7b2_measure.mediator_summary`: bout completion (intrinsic), vacancy availability (ecological), realised recruitment per attempt, shadow counters, first-attempt/success ages. **Mediator-labelled; never endpoints.** |
| `births_by_ancestry` | Admitted births per immutable founder-ancestry tag `F0…F5` (descriptive). |
| `terminal_alpha_terciles` | Terminal-census α-tercile composition (definition §3.2). |
| `shadow_counters` | `shadow_decisions`, `shadow_would_admit`. |
| `admitted_births_total`, `hazard_removals_total` | Population counters. |
| `mutation_stream_seed_derivation` | Documented stream derivation string. |
| `max_buffered`, `tick_checkpoints` | Buffer high-water mark; closure-history length (`W + 1` including `initial`). |
| `event_digest` | SHA-256 of the full event log (determinism witness). |
| `event_counts` | Event-kind histogram. |

### 1.2 Census snapshot (`terminal_census`, and checkpoint snapshots internally)

`{tick, n_live, sum_A, alpha_mean, distinct_A_values, histogram_A,
states, live_by_ancestry, T_values_present, D_values_present}` where
`histogram_A` maps every observed `A` value to its live occupancy,
`states` is the active/STALLED composition, and `T_values_present` /
`D_values_present` are sorted distinct locus values among live members
(must be `[128]` / `[255]`).

### 1.3 Kernel reconciliation (`mutation_telemetry`)

Computed by `stage8_alpha_measure.kernel_reconciliation`; carries
`{decision_records, admitted_births, memory_unavailable_failures,
draws_total, problems[], passes}`. Registered identities verified:

- every admitted birth appears in exactly one Stage-M decision record;
- per-record validity: lattice bounds; `delta` present iff `mutated`;
  `delta` off-support impossible; `child_a == clamp(parent_a + delta, 0, 255)`
  when mutating; `child_a == parent_a` otherwise; draw consumption 2/1;
- stream positions form the contiguous chain `pos_{k+1} = pos_k + draws_k`
  from 0 (draws retained across rollbacks; supply ties to published-birth
  candidates only);
- `#decisions == #admitted_births + #CHILD_MEMORY_UNAVAILABLE failures`.

### 1.4 Genome-freeze audit (`genome_freeze_audit`)

Scans `founder_registered`, `provision_committed`, and `birth_admitted`
records: `T/D == 128/255` and `0 ≤ A ≤ 255` in every genotype-bearing
record; reports `{records_checked, violations[], frozen_td, passes}`.
This is G1/G3's "zero non-frozen loci anywhere in the event stream"
evidence.

## 2. Seed-table discipline

Confirmatory: `20284617 + i`, `i ∈ 0..23`, exactly k = 24, executed once for
retention after gate + freeze. Shakedown: `20293311 + j`, `j ∈ 0..11`,
stdout-only summaries, never retained. The runner refuses artifacts under
the retained results directory unless the full confirmatory table is being
executed. Mutation stream: `random.Random(hazard_seed * 1000003 + 7)`.

## 3. Descriptive co-report definitions (committed pre-execution)

### 3.1 Recruitment telemetry

Exactly the carried 7B1 §6.2 definitions computed by
`stage7b2_measure.mediator_summary` over the Stage 8 event log:
`bout_completion_rate_intrinsic = admitted/shadow_decisions`,
`vacancy_availability_rate_ecological = shadow_would_admit/shadow_decisions`,
`realised_recruitment_per_attempt = admitted/shadow_decisions`, plus shadow
counters and first-attempt/first-success age ranges. Per-founder-ancestry
birth counts come from `birth_admitted.ancestry_id`. All mediator-labelled.

### 3.2 Terminal α-terciles

Live members ordered by ascending `A`; boundaries at indices
`floor(n/3)` and `floor(2n/3)` of the sorted vector (remainders accrue to
upper terciles; exact thirds when `3 | n`). Per tercile: `size`, `min_A`,
`max_A`, exact `mean_A`. Purely descriptive composition context.

## 4. Reduced artifact (`<raw-stem>-reduced.json`)

Written once by the source-frozen reducer:

| Field | Content |
|---|---|
| `protocol`, `source_artifact` | Provenance. |
| `decision_rule` | Pointer to preregistration §5. |
| `outcome_block.outcome` | Exactly one of `DEGENERATE_EVOLUTION`, `ESTABLISHED_TOWARD_HIGH_ALPHA`, `ESTABLISHED_TOWARD_LOW_ALPHA`, `NO_ESTABLISHED_DIRECTION`. |
| `outcome_block.rule_constants` | `α_ref=153/255`, `Δα_floor=8/255`, thresholds 16/18/24, `W=2400`, k=24. |
| `outcome_block.applied_exactly_once` | true. |
| `outcome_block.counts` | `eligible_k_eff`, movers up/down/non, ineligible with reasons, extinct replicate list. |
| `outcome_block.descriptive` | Median `|ᾱ_end − α_ref|` among movers each way; per-seed `ᾱ_end`, terminal histograms, trajectories, recruitment telemetry, ancestry birth counts, terciles. |
| `outcome_block.scope` | Level-2 statement-space limitation, verbatim. |

Reducer validation before the rule (any failure aborts without a class):
protocol match; `seed_table == "confirmatory"`; decision still
`PENDING_REDUCTION` (double reduction refused); exact seed set in order; per
COMPLETE record — terminal snapshot at W, 20 checkpoints agreeing with the
terminal census, histogram mass equal to live census, `alpha_end` equal to
its independent recomputation from the histogram, extinction flag
consistent, kernel-audit and genome-freeze passes present and passing,
recorded direction class matching the endpoint value.
