# Stage 8 Paired-Arm Output Schema Addendum

*Implementation-window obligation of
`docs/stage-8-alpha-evolution-repair-preregistration.md` §11 ("full field
pins land in the implementation-window schema addendum before the gate
runs"). Committed before any retained execution and before the §7 gate
completes; nothing here may change after the confirmatory suite runs.
Extends `docs/stage8-alpha-output-schema.md`, which remains authoritative
for every per-run field it defines; this addendum pins only the paired
layer (`src/stage8_paired.py`, `src/run_stage8_paired.py`,
`src/reduce_stage8_paired.py`). All exact quantities are serialised
canonically as `"num/den"` (Fraction end-to-end); kernel draws are
integers on the dedicated stream and never enter ledgers.*

## 1. Raw paired artifact

Written by `run_stage8_paired.py --table confirmatory` to
`results/stage8-alpha-evolution-paired/<name>.json`. Top-level fields:

| Field | Type | Content |
|---|---|---|
| `protocol` | string | Constant `stage-8-alpha-evolution-repair-preregistration`. |
| `evidence_class` | string | Fixed scope sentence; defers all interpretation to the reducer. |
| `seed_table` | string | `"confirmatory"` or `"shakedown"`. The retained directory accepts confirmatory at exactly k = 24 pairs only (runner guard, §10). |
| `seed_table_derivation` | string | `hazard_seed = 20310529 + i, i in 0..23` for the registered table. |
| `mutation_enabled_arms` | list | Exactly `["M"]`. |
| `reference_arms` | list | Exactly `["R0"]`. |
| `registered_configuration` | object | Echo from `stage8_paired.registered_configuration()`: keys `protocol`, `prereg_document`, `arms{M,R0}`, `pairing`, `window_ticks_W=2400`, `expected_lifespans_per_window=20`, `census_capacity_N`, `buffer_depth_d`, `packet_rate_r`, `packet_energy_E`, `hazard_rate_h`, `pairs_k=24`, `runs_total=48`, `confirmatory_seed_derivation`, `shakedown_seed_derivation`, `genotypes_ATD`, `founders_per_genotype=3`, `founder_S`, `frozen_loci{T:128,D:255}`, `direction_floor_paired="4/255"`, `decision_thresholds{minimum_eligible_k_eff:16, concordance:18}`, `retired_tables_never_reused[]` (all five bases incl. the retired-unexecuted 20284617/20293311). |
| `source_manifest_sha256` | map filename → sha256 | Every file in `run_stage8_paired.FROZEN_SOURCES`; the freeze manifest pins these hashes. |
| `execution_class` | string | `"one seeded confirmatory pair suite executed once"` (confirmatory) or `"exploratory unretained execution (section 7)"` (shakedown). |
| `pairs` | array of objects | One per pair, in registered table order (§1.1). |
| `integrity` | object | `ledgers_asserted_every_operation` (carried machinery statement), `any_checkpoint_failure_aborts_retention=true`, `kernel_draws_retained_across_rollbacks=true`, `arm_contrast_is_exactly_the_kernel=true`. |
| `decision` | string | Literal `PENDING_REDUCTION` (double-reduction guard). |
| `decision_scope` | string | Fixed deferral statement naming the source-frozen reducer. |

### 1.1 Pair object

`{pair_index, hazard_seed, arms: {M: <run record>, R0: <run record>}}`.
Both arms carry the identical `hazard_seed` (G4 condition); `pair_index`
ranges over `0..23` for the confirmatory table.

### 1.2 Per-run arm record

Exactly the per-replicate record of `docs/stage8-alpha-output-schema.md`
§1.1–§1.3 (classification, window, `alpha_end`, `direction_class`,
extinction flag, terminal census, trajectory checkpoints, mutation
telemetry, kernel draw chain, genome-freeze audit, mediators,
births-by-ancestry, terciles, shadow counters, counters, stream-seed
derivation, buffer high-water, closure history, event digest/counts),
with these paired-layer pins:

| Field | Pin |
|---|---|
| `arm` | `"M"` or `"R0"`; must equal its key in `arms` (reducer-validated). |
| Arm M kernel blocks | Carried verbatim: one Stage-M record per admitted birth; bit-exact replay substrate. |
| Arm R0 kernel blocks | `kernel_draw_chain == []`; `mutation_telemetry.decision_records == 0`; `mutation_telemetry.draws_total == 0`; `mutation_telemetry.passes == true`; `admitted_births > 0`. Structural witness: `stage8_paired.assert_kernel_absent` refuses any population carrying `mutation_rng`/`mutation_draws`. |
| `direction_class` (per arm) | Carried at the single-arm floor `8/255` vs `α_ref = 3/5` **as a descriptive co-report only**; the repair §5 rule reads `alpha_end` exclusively. The reducer still validates recorded classes against endpoint values (no silent drift). |
| `closure_history_head` | Descriptive only (gate-repair registration §3): first three operation labels of the arm's closure history, i.e. exactly `["initial", "initial", "tick_complete:0"]` for every COMPLETE arm. Read by the corrected G2 check and by no mechanic; ignored by the reducer's decision path. |
| `closure_history_tail` | Descriptive only (gate-repair registration §3): last operation label, i.e. exactly `tick_complete:<W−1>` = `tick_complete:2399` for every COMPLETE arm at `W = 2400`. Same read-by/no-mechanics status as `closure_history_head`. |
| Guarded failure record | `{seed_table, replicate_index, hazard_seed, arm, classification: "INVALID_IMPLEMENTATION", reason: "UNEXPECTED_EXCEPTION", detail, traceback}` — per-arm guarding retains the twin's evidence. |

## 2. Reduced artifact

Written by `reduce_stage8_paired.py <raw>` (default `<stem>-reduced.json`
beside the input). Fields:

| Field | Content |
|---|---|
| `protocol` | Constant `stage-8-alpha-evolution-repair-preregistration`. |
| `source_artifact` | Path of the reduced raw artifact. |
| `decision_rule` | Fixed pointer to repair registration §5, applied exactly once by this source-frozen reducer. |
| `outcome_block` | Object pinned in §2.1. |

Pre-rule validation refusals (exit 1, no class emitted): protocol
mismatch; `seed_table != "confirmatory"`; `decision !=
"PENDING_REDUCTION"` (double reduction); pair count ≠ 24; seed sequence ≠
registered derivation; `arms` keys ≠ `{M, R0}`; arm-label mismatch;
missing tick-2400 snapshot; checkpoint ticks incomplete; final checkpoint
vs terminal census disagreement; histogram mass ≠ live census;
`alpha_end` ≠ exact histogram recomputation; extinction-flag
inconsistency; kernel evidence absent/failing on either arm; recorded
per-arm direction class ≠ endpoint value.

### 2.1 Outcome block

| Field | Content |
|---|---|
| `outcome` | Exactly one of `DEGENERATE_EVOLUTION` (`k_eff < 16`), `ESTABLISHED_TOWARD_HIGH_ALPHA` / `ESTABLISHED_TOWARD_LOW_ALPHA` (`k_eff ≥ 16` and ≥ 18 pairs beyond the floor on that side), `NO_ESTABLISHED_DIRECTION` (otherwise, including splits). |
| `rule_constants` | `direction_floor_paired="4/255"`, `alpha_ref_per_arm="3/5"`, `minimum_eligible_k_eff=16`, `concordance_threshold=18`, `pairs_k=24`, `window_ticks_W=2400`. |
| `applied_exactly_once` | `true`. |
| `counts.pairs` | Pairs in the raw artifact (24). |
| `counts.eligible_k_eff` | Pairs with both arms COMPLETE and ≥ 1 live member at tick W in both arms. |
| `counts.movers_up_pairs` / `counts.movers_down_pairs` / `counts.non_mover_pairs` | Eligible pairs with `D_i ≥ +4/255`, `≤ −4/255`, strictly inside, respectively (`D_i` an exact Fraction). |
| `counts.ineligible_pairs` | `{pair_index, hazard_seed, reason}` with reasons `M:<class>` / `R0:<class>` / `<arm>:extinct_at_W`. |
| `counts.extinct_pairs` | Pairs with any extinct arm. |
| `counts.leakage_pairs` | Descriptive leakage monitor: pairs where the two arms' terminal-census plurality founder ancestries disagree — `{pair_index, hazard_seed, M_plurality, R0_plurality}`. **Descriptive only; never an endpoint** (repair §4). |
| `descriptive.paired_differences` | Map `hazard_seed → D_i` as `"num/den"` (or `null` if ineligible). |
| `descriptive.median_D_among_movers_up` / `_down`, `median_abs_D_all_eligible` | Exact-Fraction medians (mean of middle two when even), `null` when empty. |
| `descriptive.alpha_end_by_arm_and_seed` | Per seed, per arm, the serialised `ᾱ_end` (null when not COMPLETE). |
| `descriptive.trajectories_by_arm_and_seed` | Per-arm 20-checkpoint trajectories. |
| `descriptive.recruitment_telemetry_by_arm_and_seed` | Mediator-labelled per-arm telemetry; never promoted to endpoints. |
| `descriptive.births_by_ancestry_by_arm_and_seed` | Founder-ancestry birth counts per arm (descriptive). |
| `scope` | Fixed level-2 statement space relative to the mutation-off reference at the same seeds; null licenses exactly the bounded-negative sentence. |

CLI summary line (stdout): `{outcome, eligible_k_eff, movers_up_pairs,
movers_down_pairs, non_mover_pairs, leakage_pairs, wrote}`.

## 3. Registered file names (retained class)

Raw: `results/stage8-alpha-evolution-paired/confirmatory-paired-20310529.json`;
reduced:
`results/stage8-alpha-evolution-paired/confirmatory-paired-20310529-reduced.json`;
freeze manifest:
`results/stage8-alpha-evolution-paired/pre-execution-manifest.json`;
execution note: `docs/stage-8-paired-execution-note.md`. Shakedown runs
produce no files anywhere under `results/` (stdout only).

## 4. Gate-repair amendment (2026-08-23)

Added by the implementation window of
`docs/stage-8-alpha-evolution-gate-repair-preregistration.md` (superseding
registration #3), after the first shakedown execution exposed a
checkpoint-bookkeeping mismatch between the gate tooling's derived
expectation (`W + 1`) and the byte-frozen stack's deterministic closure
semantics (`W + 2`; diagnosis archived at
`failed-designs/stage8-paired-gate-g2-checkpoint-bookkeeping/`):

1. The two descriptive fields `closure_history_head` /
   `closure_history_tail` are pinned in §1.2 above, exactly as registered
   by the gate-repair registration §3.
2. The parenthetical "(closure-history length (`W + 1` including
   `initial`))" in `docs/stage8-alpha-output-schema.md` §1.1 is
   **superseded** to read "(`W + 2`: two `initial` entries appended by the
   two constructor layers, plus one `tick_complete:<t>` entry per completed
   tick)" — correction by supersession only; the base document itself is
   not edited.
3. Nothing else in this addendum changes: arms, kernel, floor 4/255,
   thresholds 16/18/24, windows, seed tables, file names, and all other
   field pins stand exactly as committed at 8958763.
