# Stage 7B2 Output Schema (frozen with the pre-execution manifest)

This document fixes the retained-artifact contract for
`docs/stage-7b2-preregistration.md` §8. It is frozen together with the
runner (`run_stage7b2.py`), reducer (`reduce_stage7b2.py`), measurement and
solver modules, population module, and test matrix at
`results/stage7b2/pre-execution-manifest.json`. After the freeze these
definitions may be corrected only by a further superseding preregistration.

## Retention-scope decision (disclosed)

The raw artifact retains **full-fidelity estimator inputs** — every
event-ledger record the §3 estimators consume (founder registrations,
committed provisions, admissions, hazard deaths, divide attempts/stalls)
plus per-replicate digests and counters for all other event classes — not
the complete event stream verbatim. Rationale: the estimators are defined
exclusively over those records; retaining them plus SHA-256 digests of the
full streams keeps every number auditable and recomputable while avoiding a
repeat of the 297 MB artifact incident recorded in
`docs/history-migration-2026-08-22.md`. The runner asserts every ledger
closure live (per-operation on live state; full immutable-history rescan at
every tick-complete checkpoint), so a completed artifact implies every
checkpoint held; `event_digest` binds each replicate to its exact stream.
This scope is part of the freeze; widening it later requires a superseding
preregistration.

## Raw artifact (`results/stage7b2/stage7b2-result.json`)

Top-level keys:

| Key | Type | Content |
|---|---|---|
| `protocol` | str | `"stage-7b2-preregistration"` |
| `evidence_class` | str | seeded confirmatory suite description |
| `selection_assay_run` | bool | always `false` |
| `mutation_enabled` | bool | always `false` |
| `registered_configuration` | object | binding §2 values echoed (W, N, d, r, hazard arm, k, seed derivation, ρ_r, Δr_min, genotypes, founder state) |
| `source_manifest_sha256` | object | SHA-256 per frozen source file |
| `execution_class` | str | preregistration §8.3 reference |
| `replicates` | array | one record per replicate index `0..k-1` |
| `integrity` | object | assertion-scheduling disclosure |
| `decision` | str | always `"PENDING_REDUCTION"` in raw artifacts |
| `decision_scope` | str | limits: decision applied only by the reducer |

Per-replicate record keys:

- Identification/classification: `replicate_index`, `hazard_seed`,
  `classification` ∈ {`COMPLETE`, `INVALID_IMPLEMENTATION`}, and for invalid
  runs `reason` (`BUFFER_OVERFLOW` or `UNEXPECTED_EXCEPTION`), `detail`,
  optional `traceback`, `ticks_completed`.
- For `COMPLETE` runs:
  - `vital_records.members`: `{organism_id: {genotype_a, born_tick,
    death_tick|null}}` — genotype from the `a_over_d` field of
    `founder_registered` events or the `inherited_a_over_d` field of the
    paired `provision_committed` event; founders carry measurement birth
    tick `0`; `death_tick` non-null iff a `hazard_death` event exists.
  - `vital_records.births`: `{child_id, parent_id, tick, genotype_a,
    provision}` in log order (exact rationals as `num/den` strings).
  - `vital_records.establishments`: `{parent_id, through_offspring, tick,
    parent_age}` — offspring-first-reproduction credit per preregistration
    §3 / 7B1 §6.1.
  - `vital_records.attempt_counters`: `shadow_decisions_identity`
    (= `provision_committed + divide_failed` events), `no_vacancy_attempts`,
    `child_memory_unavailable_attempts`, `somatic_stalls`.
  - `cohort_schedules."A"`: per genotype `{cohort_size, died, censored,
    exposure_member_ticks, l_x[0..W], m_x[0..W]}` as exact `num/den`
    strings.
  - `solver_certificates."A"`: `{status, support, L0_exact}` plus, when
    `SUPERCRITICAL`, `{r_lo, r_hi, width, iterations, rho, certified}`;
    endpoints are exact rationals with certified containment
    `L(r_lo) ≥ 1 > L(r_hi)` and width ≤ ρ_r = 1/256.
  - `mediators`: intrinsic bout completion, ecological vacancy availability,
    realised recruitment per attempt (reported separately; never
    substituted for the endpoint), shadow counters, first-attempt /
    first-success age ranges.
  - Integrity fields: `shadow_counters`, `admitted_births_total`,
    `hazard_removals_total`, `max_buffered`, `tick_checkpoints`,
    `event_digest` (SHA-256 of the replicate's full event stream),
    `event_counts`.

## Reduced artifact (`results/stage7b2/stage7b2-reduced.json`)

| Key | Content |
|---|---|
| `reduction` | present (value `REDUCTION_MISMATCH`) only on recomputation mismatch; repair policy invoked |
| `verification` | `recomputation_bit_exact`, mismatch count, list of `invalid_implementations` replicate indices |
| `decision_rule_input` | registered Δr_min and ρ_r echoes |
| `per_replicate` | per-replicate outcome detail (status/L0 per genotype) |
| `outcome.pair_contrast_class` | exactly one of `DEGENERATE_REPLICATION`, `ESTABLISHED_CONTRAST`, `NO_ESTABLISHED_CONTRAST` |
| `outcome.subcritical_report` | null, `ONE_ARM_SUBCRITICAL`, or `BOTH_SUBCRITICAL`, reported alongside |
| `outcome.complete_pairs` | replicate count with both genotypes supercritical |
| `outcome.median_paired_difference` | exact rational median (lower-middle convention) of paired midpoint differences |
| `interpretation_limits` | binding anti-overclaim text |
| `consumed_raw_artifact` | path, SHA-256, byte size of the raw artifact |
| `reducer_source_manifest_sha256` | SHA-256 per reducer source file |

## Serialisation rules

Exact rationals serialize as `"num/den"` strings everywhere; integers as
JSON numbers; no float appears anywhere in either artifact. Telemetry labels
and ancestry IDs never influence mechanics. The §5 rule is applied exactly
once, by `reduce_stage7b2.main`, on one raw artifact; outcomes are never
retroactively reclassified.
