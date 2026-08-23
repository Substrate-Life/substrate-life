# Stage 7B Endpoint-Repair Output Schema (implementation window)

This document fixes the retained-artifact contract for
`docs/stage-7b-endpoint-repair-preregistration.md`. It is written during
the implementation window (prereg §6.1) and will be frozen **together**
with the runner (`run_stage7b_endpoint.py`), reducer
(`reduce_stage7b_endpoint.py`), gate tooling (`stage7b_endpoint_gate.py`),
the corrected measurement module (`stage7b_endpoint_measure.py`), the
configuration layer (`stage7b_endpoint_config.py`), and the test matrix at
`results/stage7b-endpoint-repair/pre-execution-manifest.json` — committed
before any retained run and only after the §5 feasibility gate passes.
After the freeze these definitions may be corrected only by a further
superseding preregistration. The contract is identical in structure to
`docs/stage7b2r-output-schema.md`; only the endpoint (corrected raw
fecundity per prereg §3), protocol label, paths, and authorisation
references differ.

## Endpoint correction reflected here

- `cohort_schedules."A".m_x` is the **ENDPOINT**: raw age-specific
  fecundity — every admitted birth counted exactly once, credited to its
  immediate parent at the parent's age at the birth tick, divided by
  `|C_g|` (endpoint-repair prereg §3).
- `cohort_schedules."A".establishment_m_x` is the former endpoint
  (offspring-first-reproduction credit), retained **as a reported
  mediator**; it is verified for export fidelity by the reducer and is
  never substituted for the endpoint.
- `vital_records.births` is retained in this cycle because the corrected
  endpoint's estimator inputs are the births themselves (the legacy
  estimator needed only establishments + members).

## Retention-scope decision (carried, disclosed)

The raw artifact retains **full-fidelity estimator inputs** — the member
table, the admitted-births table, the establishment table, and attempt
counters — plus per-replicate digests and counters for all other event
classes, not the complete event stream verbatim, exactly as frozen for
Stage 7B2/7B2-R. The runner asserts every ledger closure live
(per-operation on live state; full immutable-history rescan at every
tick-complete checkpoint), so a completed artifact implies every
checkpoint held; `event_digest` binds each replicate to its exact stream.
This scope is part of the freeze; widening it later requires a superseding
preregistration. No repeat of the 297 MB artifact incident: retention stays
input-fidelity, not stream-fidelity.

## Raw artifact (`results/stage7b-endpoint-repair/stage7b-endpoint-result.json`)

Top-level keys:

| Key | Type | Content |
|---|---|---|
| `protocol` | str | `"stage-7b-endpoint-repair-preregistration"` |
| `prereg_document` | str | `docs/stage-7b-endpoint-repair-preregistration.md` |
| `evidence_class` | str | seeded confirmatory suite description at the carried §3 ecology under the corrected endpoint |
| `selection_assay_run` | bool | always `false` |
| `mutation_enabled` | bool | always `false` |
| `registered_configuration` | object | binding values echoed (`protocol`, corrected endpoint note, mediator note, W=1200, N=48, d=64, r=5, hazard arm, k=32, seed derivation `20261822 + i`, genotypes, founder state, packet energy 900, memory pool, mutation disabled, carried-from note, reused shakedown-table note, supersedes chain) |
| `decision_rule_inputs` | object | carried rule constants: ρ_r = 1/256, Δr_min = 1/100, minimum complete pairs 16 |
| `source_manifest_sha256` | object | SHA-256 per frozen source file (`FROZEN_SOURCES`) |
| `execution_class` | str | endpoint-repair prereg §6.3 reference (single suite, post-gate post-freeze) |
| `replicates` | array | one record per replicate index `0..k-1`, seed `20261822 + i` |
| `integrity` | object | assertion-scheduling disclosure |
| `decision` | str | always `"PENDING_REDUCTION"` in raw artifacts |
| `decision_scope` | str | limits: decision applied only once, by the reducer |

Per-replicate record keys:

- Identification/classification: `replicate_index`, `hazard_seed`,
  `classification` ∈ {`COMPLETE`, `INVALID_IMPLEMENTATION`}, and for
  invalid runs `reason` (`BUFFER_OVERFLOW` or `UNEXPECTED_EXCEPTION`),
  `detail`, optional `traceback`, `ticks_completed`.
- For `COMPLETE` runs:
  - `vital_records.members`: `{organism_id: {genotype_a, born_tick,
    death_tick|null}}`; founders carry measurement birth tick `0`;
    `death_tick` non-null iff a `hazard_death` event exists.
  - `vital_records.births`: `{child_id, parent_id, tick, genotype_a,
    provision}` in log order; exact rationals serialised as `num/den`
    strings (the corrected endpoint's estimator inputs).
  - `vital_records.establishments`: `{parent_id, through_offspring, tick,
    parent_age}` — offspring-first-reproduction credit, reported as the
    mediator numerator per carried definitions.
  - `vital_records.attempt_counters`: `shadow_decisions_identity`
    (= `provision_committed + divide_failed` events),
    `no_vacancy_attempts`, `child_memory_unavailable_attempts`,
    `somatic_stalls`.
  - `cohort_schedules."A"`: per genotype `{cohort_size, died, censored,
    exposure_member_ticks, l_x[0..W], m_x[0..W] (ENDPOINT, raw fecundity),
    establishment_m_x[0..W] (mediator), births_credited,
    establishments_credited}` as exact `num/den` strings / integers.
  - `solver_certificates."A"`: `{status, support, L0_exact}` plus, when
    `SUPERCRITICAL`, `{r_lo, r_hi, width, iterations, rho, certified}`;
    endpoints are exact rationals with certified containment
    `L(r_lo) ≥ 1 > L(r_hi)` and width ≤ ρ_r = 1/256; solver reused
    byte-identically from the frozen module.
  - `mediators`: intrinsic bout completion, ecological vacancy
    availability, realised recruitment per attempt (reported separately;
    never substituted for the endpoint), shadow counters, first-attempt /
    first-success age ranges.
  - Integrity fields: `shadow_counters`, `admitted_births_total`,
    `hazard_removals_total`, `max_buffered`, `tick_checkpoints`,
    `event_digest` (SHA-256 of the replicate's full event stream),
    `event_counts`.

## Reduced artifact (`results/stage7b-endpoint-repair/stage7b-endpoint-reduced.json`)

| Key | Content |
|---|---|
| `protocol` | `"stage-7b-endpoint-repair-preregistration"`; the reducer refuses any other protocol label |
| `reduction` | present (value `REDUCTION_MISMATCH`) only on recomputation mismatch (including any `l_x`, endpoint `m_x`, or mediator `establishment_m_x` divergence); repair policy invoked |
| `verification` | `recomputation_bit_exact`, mismatch count, list of `invalid_implementations` replicate indices |
| `decision_rule_input` | registered Δr_min and ρ_r echoes |
| `per_replicate` | per-replicate outcome detail (status/L0 per genotype) |
| `outcome.pair_contrast_class` | exactly one of `DEGENERATE_REPLICATION`, `ESTABLISHED_CONTRAST`, `NO_ESTABLISHED_CONTRAST` (rule applied exactly once) |
| `outcome.subcritical_report` | null, `ONE_ARM_SUBCRITICAL`, or `BOTH_SUBCRITICAL`, reported alongside |
| `outcome.complete_pairs` | replicate count with both genotypes supercritical |
| `outcome.median_paired_difference` | exact rational median (lower-middle convention) of paired midpoint differences |
| `interpretation_limits` | binding anti-overclaim text incl. mediator-never-endpoint clause |
| `consumed_raw_artifact` | path, SHA-256, byte size of the raw artifact |
| `reducer_source_manifest_sha256` | SHA-256 per reducer source file |

## Feasibility-gate summary disclosure (endpoint-repair prereg §5.5)

Shakedown executions produce no retained artifact. If — and only if — the
§5 gate passes and a freeze is committed, the factual gate summary (fixed
seed list used, per-condition pass counts G1–G4, per-replicate evidence)
is recorded in the freeze manifest's notes at
`results/stage7b-endpoint-repair/pre-execution-manifest.json`; the
confirmatory table itself remains untouched until the single retained run.
If the gate fails, no freeze may be committed and a further superseding
preregistration with a new diagnosis is the only correct action (§5.4).

## Serialisation rules

Exact rationals serialize as `"num/den"` strings everywhere; integers as
JSON numbers; no float appears anywhere in either artifact. Telemetry
labels and ancestry IDs never influence mechanics. The carried §5 rule is
applied exactly once, by `reduce_stage7b_endpoint.main`, on one raw
artifact; outcomes are never retroactively reclassified.
