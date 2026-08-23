# Stage 7B Signed-Bracket Output Schema (implementation window)

This document fixes the retained-artifact contract for
`docs/stage-7b-signed-bracket-preregistration.md`. It is written during
the implementation window (prereg §6.1) and will be frozen **together**
with the full-line solver (`stage7b_signed_bracket_solver.py`), the
configuration layer (`stage7b_signed_bracket_config.py`), the gate tooling
(`stage7b_signed_bracket_gate.py`), the runner
(`run_stage7b_signed_bracket.py`), the reducer
(`reduce_stage7b_signed_bracket.py`), and the test matrix, as a
pre-execution manifest at
`results/stage7b-signed-bracket/pre-execution-manifest.json` — committed
before any retained run and only after the §5 feasibility gate passes.
After the freeze these definitions may be corrected only by a further
superseding preregistration. The contract is structurally identical to
`docs/stage7b-endpoint-output-schema.md`; only the solver DOMAIN (full
real line instead of `r >= 0` only), the extra actuarial/exposure fields
already introduced by the denominator-repair generation, the protocol
label, paths, and authorisation references differ.

## Solver-domain extension reflected here

- `solver_certificates."A".status` ranges over
  `{SUPERCRITICAL, CRITICAL, SUBCRITICAL, NO_FINITE_ROOT}` (signed-bracket
  prereg §3), not just `{SUPERCRITICAL, SUBCRITICAL}`.
- For `SUPERCRITICAL`, `CRITICAL`, and `SUBCRITICAL` a full bracket
  `{r_lo, r_hi, width, iterations, rho, certified}` is exported — including
  when the bracket lies entirely below zero (`SUBCRITICAL`) or is the
  exact point `[0, 0]` (`CRITICAL`). `NO_FINITE_ROOT` exports `reason`
  instead of a bracket and is excluded from pairing.
- `cohort_schedules."A"` carries the unchanged two-factor fields
  (`l_actuarial_x`, `m_exposure_x`, `e_x`, `d_x`) verbatim from the
  denominator-repair generation; the endpoint coefficient assembly itself
  is untouched by this document.
- The reduced artifact's `outcome` carries the completed section-3-table
  decision rule: `complete_pairs` now counts replicates where **both**
  genotypes emit any finite-root bracket (not only joint
  supercriticality), and `sign_split` reports the `{positive, negative,
  zero}` counts of paired midpoint differences descriptively.

## Retention-scope decision (carried, disclosed)

The raw artifact retains **full-fidelity estimator inputs** — the member
table, the admitted-births table, the establishment table, and attempt
counters — plus per-replicate digests and counters for all other event
classes, not the complete event stream verbatim, exactly as frozen for
Stage 7B2/7B2-R/endpoint-repair/denominator-repair. The runner asserts
every ledger closure live (per-operation on live state; full
immutable-history rescan at every tick-complete checkpoint), so a
completed artifact implies every checkpoint held; `event_digest` binds
each replicate to its exact stream. This scope is part of the freeze;
widening it later requires a superseding preregistration. No repeat of
the 297 MB artifact incident: retention stays input-fidelity, not
stream-fidelity.

## Raw artifact (`results/stage7b-signed-bracket/stage7b-signed-bracket-result.json`)

Top-level keys:

| Key | Type | Content |
|---|---|---|
| `protocol` | str | `"stage-7b-signed-bracket-preregistration"` |
| `prereg_document` | str | `docs/stage-7b-signed-bracket-preregistration.md` |
| `evidence_class` | str | seeded confirmatory suite description at the carried §3 ecology under the unchanged two-factor endpoint, certified on the full real line |
| `selection_assay_run` | bool | always `false` |
| `mutation_enabled` | bool | always `false` |
| `registered_configuration` | object | binding values echoed (protocol, endpoint, solver-domain note, W=1200, N=48, d=64, r=5, hazard arm, k=32, seed derivation `20261822 + i`, genotypes, founder state, packet energy 900, memory pool, mutation disabled, binding identities, shakedown-table note, supersession chain, generation-3 regression reference) |
| `decision_rule_inputs` | object | carried rule constants: ρ_r = 1/256, Δr_min = 1/100, minimum complete pairs 16 |
| `source_manifest_sha256` | object | SHA-256 per frozen source file (`FROZEN_SOURCES`) |
| `execution_class` | str | signed-bracket prereg §6.3 reference (single suite, post-gate post-freeze) |
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
    strings (the endpoint's estimator inputs).
  - `vital_records.establishments`: `{parent_id, through_offspring, tick,
    parent_age}` — offspring-first-reproduction credit, reported as the
    mediator numerator per carried definitions.
  - `vital_records.attempt_counters`: `shadow_decisions_identity`
    (= `provision_committed + divide_failed` events),
    `no_vacancy_attempts`, `child_memory_unavailable_attempts`,
    `somatic_stalls`.
  - `cohort_schedules."A"`: per genotype `{cohort_size, died, censored,
    exposure_member_ticks, l_x[0..W] (descriptive), d_x[0..W], e_x[0..W],
    l_actuarial_x[0..W] (survivorship FACTOR), m_exposure_x[0..W]
    (fecundity FACTOR), establishment_m_x[0..W] (mediator),
    births_credited, establishments_credited, person_ticks_credited}` as
    exact `num/den` strings / integers.
  - `solver_certificates."A"`: `{status, support, L0_exact}` plus, when
    `status` is `SUPERCRITICAL`, `CRITICAL`, or `SUBCRITICAL`,
    `{r_lo, r_hi, width, iterations, rho, certified}` — endpoints are
    exact rationals with certified containment and width ≤ ρ_r = 1/256;
    when `NO_FINITE_ROOT`, `{reason}` instead. Solver reused
    byte-identically for `r >= 0` from the frozen module; the `r < 0`
    branch is new and additive.
  - `mediators`: intrinsic bout completion, ecological vacancy
    availability, realised recruitment per attempt (reported separately;
    never substituted for the endpoint), shadow counters, first-attempt /
    first-success age ranges.
  - Integrity fields: `shadow_counters`, `admitted_births_total`,
    `hazard_removals_total`, `max_buffered`, `tick_checkpoints`,
    `event_digest` (SHA-256 of the replicate's full event stream),
    `event_counts`.

## Reduced artifact (`results/stage7b-signed-bracket/stage7b-signed-bracket-reduced.json`)

| Key | Content |
|---|---|
| `protocol` | `"stage-7b-signed-bracket-preregistration"`; the reducer refuses any other protocol label |
| `reduction` | present (value `REDUCTION_MISMATCH`) only on recomputation mismatch (including any `l_actuarial_x`, `m_exposure_x`, or mediator `establishment_m_x` divergence, or any solver certificate mismatch); repair policy invoked |
| `verification` | `recomputation_bit_exact`, mismatch count, list of `invalid_implementations` replicate indices |
| `decision_rule_input` | registered Δr_min, ρ_r, minimum-complete-pairs echo |
| `per_replicate` | per-replicate outcome detail (status/L0 per genotype) |
| `outcome.pair_contrast_class` | exactly one of `DEGENERATE_REPLICATION`, `ESTABLISHED_CONTRAST`, `NO_ESTABLISHED_CONTRAST` (rule applied exactly once) |
| `outcome.subcritical_report` | null, `ONE_ARM_SUBCRITICAL`, or `BOTH_SUBCRITICAL`, reported alongside |
| `outcome.complete_pairs` | replicate count with **both** genotypes emitting any finite-root bracket (SUPERCRITICAL/CRITICAL/SUBCRITICAL) |
| `outcome.median_paired_difference` | exact rational median (lower-middle convention) of paired midpoint differences |
| `outcome.sign_split` | descriptive `{positive, negative, zero}` counts of paired midpoint differences over complete pairs; never a directional claim |
| `interpretation_limits` | binding anti-overclaim text incl. mediator-never-endpoint and sign-split/exclusion-never-fitness clauses |
| `consumed_raw_artifact` | path, SHA-256, byte size of the raw artifact |
| `reducer_source_manifest_sha256` | SHA-256 per reducer source file |

## Feasibility-gate summary disclosure (signed-bracket prereg §5.5)

Shakedown executions produce no retained artifact. If — and only if — the
§5 gate passes and a freeze is committed, the factual gate summary (fixed
seed list used, per-condition pass counts G1–G3, per-replicate evidence,
the estimator-layer regression-identity confirmation against the archived
generation-3 `L0_exact` values) is recorded in the freeze manifest's notes
at `results/stage7b-signed-bracket/pre-execution-manifest.json`; the
confirmatory table itself remains untouched until the single retained
run. If the gate fails, no freeze may be committed and a further
superseding preregistration with a new diagnosis is the only correct
action (§5.4).

## Serialisation rules

Exact rationals serialize as `"num/den"` strings everywhere; integers as
JSON numbers; no float appears anywhere in either artifact. Telemetry
labels and ancestry IDs never influence mechanics. The completed
section-3-table rule is applied exactly once, by
`reduce_stage7b_signed_bracket.main`, on one raw artifact; outcomes are
never retroactively reclassified.
