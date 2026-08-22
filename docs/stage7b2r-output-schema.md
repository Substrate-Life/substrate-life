# Stage 7B2-R Output Schema (frozen with the pre-execution manifest)

This document fixes the retained-artifact contract for
`docs/stage-7b2-repair-preregistration.md` §7. It is frozen together with the
runner (`run_stage7b2r.py`), reducer (`reduce_stage7b2r.py`), the unchanged
measurement and solver modules, the configuration layer
(`stage7b2r_population.py`), and the test matrix at
`results/stage7b2-repair/pre-execution-manifest.json`. After the freeze these
definitions may be corrected only by a further superseding preregistration.
The artifact contract is identical in structure to `docs/stage7b2-output-schema.md`
(retention-scope decision carried verbatim); only the registered ecology,
protocol label, paths, and authorisation references differ.

## Retention-scope decision (carried, disclosed)

The raw artifact retains **full-fidelity estimator inputs** — every
event-ledger record the §3 estimators consume (founder registrations,
committed provisions, admissions, hazard deaths, divide attempts/stalls)
plus per-replicate digests and counters for all other event classes — not
the complete event stream verbatim, exactly as frozen for Stage 7B2. The
runner asserts every ledger closure live (per-operation on live state; full
immutable-history rescan at every tick-complete checkpoint), so a completed
artifact implies every checkpoint held; `event_digest` binds each replicate
to its exact stream. This scope is part of the freeze; widening it later
requires a superseding preregistration.

## Raw artifact (`results/stage7b2-repair/stage7b2r-result.json`)

Top-level keys:

| Key | Type | Content |
|---|---|---|
| `protocol` | str | `"stage-7b2r-preregistration"` |
| `evidence_class` | str | seeded confirmatory suite description at the repaired §3 ecology |
| `selection_assay_run` | bool | always `false` |
| `mutation_enabled` | bool | always `false` |
| `registered_configuration` | object | binding repair-§3 values echoed (`protocol`, W=1200, N=48, d=64, r=5, hazard arm, k=32, seed derivation `20261822 + i`, genotypes, founder state, packet energy 900, memory pool, mutation disabled, supersedes note) |
| `decision_rule_inputs` | object | carried rule constants: ρ_r = 1/256, Δr_min = 1/100, minimum complete pairs 16 |
| `source_manifest_sha256` | object | SHA-256 per frozen source file |
| `execution_class` | str | repair-preregistration §7.3 reference (single suite, post-gate post-freeze) |
| `replicates` | array | one record per replicate index `0..k-1`, seed `20261822 + i` |
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
    parent_age}` — offspring-first-reproduction credit per carried §3 /
    7B1 §6.1.
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

## Reduced artifact (`results/stage7b2-repair/stage7b2r-reduced.json`)

| Key | Content |
|---|---|
| `protocol` | `"stage-7b2r-preregistration"`; the reducer refuses any other protocol label |
| `reduction` | present (value `REDUCTION_MISMATCH`) only on recomputation mismatch; repair policy invoked |
| `verification` | `recomputation_bit_exact`, mismatch count, list of `invalid_implementations` replicate indices |
| `decision_rule_input` | registered Δr_min and ρ_r echoes |
| `per_replicate` | per-replicate outcome detail (status/L0 per genotype) |
| `outcome.pair_contrast_class` | exactly one of `DEGENERATE_REPLICATION`, `ESTABLISHED_CONTRAST`, `NO_ESTABLISHED_CONTRAST` (rule applied exactly once) |
| `outcome.subcritical_report` | null, `ONE_ARM_SUBCRITICAL`, or `BOTH_SUBCRITICAL`, reported alongside |
| `outcome.complete_pairs` | replicate count with both genotypes supercritical |
| `outcome.median_paired_difference` | exact rational median (lower-middle convention) of paired midpoint differences |
| `interpretation_limits` | binding anti-overclaim text |
| `consumed_raw_artifact` | path, SHA-256, byte size of the raw artifact |
| `reducer_source_manifest_sha256` | SHA-256 per reducer source file |

## Feasibility-gate summary disclosure (repair preregistration §6.4)

Shakedown executions produce no retained artifact. The factual gate summary
(seed list used, per-condition pass counts G1–G4) is recorded in the freeze
manifest's notes at `results/stage7b2-repair/pre-execution-manifest.json`;
the confirmatory table itself remains untouched until the single retained
run.

## Serialisation rules

Exact rationals serialize as `"num/den"` strings everywhere; integers as
JSON numbers; no float appears anywhere in either artifact. Telemetry labels
and ancestry IDs never influence mechanics. The carried §5 rule is applied
exactly once, by `reduce_stage7b2r.main`, on one raw artifact; outcomes are
never retroactively reclassified.
