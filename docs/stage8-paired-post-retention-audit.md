# Stage 8 paired-arm post-retention audit

*Independent verification of the retained confirmatory artifacts of
`docs/stage-8-alpha-evolution-repair-preregistration.md`, executed
2026-08-23 by a session other than the one that ran and reduced the suite.
Tool: `src/audit_stage8_post_retention.py` (committed alongside this note;
added AFTER the f1e6880 freeze as read-only verification tooling, imported
by no mechanic, outside every frozen execution path — house precedent
`audit_stage7b_signed_bracket.py`). Exact Fraction arithmetic throughout.
This audit adds nothing to `results/`, reinterprets nothing, and makes no
claim beyond the registered §5 scope.*

## Provenance audited

| Item | Value |
|---|---|
| Freeze | f1e6880, `results/stage8-alpha-evolution-paired/pre-execution-manifest.json` (30 pins, zero drift) |
| Retained execution | launched 14:55 UTC from the f1e6880 tree; finished 17:41 UTC (~2h46m wall, two workers); exit 0 |
| Raw artifact | `confirmatory-paired-20310529.json`, 4,198,845 bytes, SHA-256 `3eb06ecc03cbe044416ac403f59a7f0e2adb6ab2d2d2f4c54cf1f38c6ce660e7` |
| Reduced artifact | `confirmatory-paired-20310529-reduced.json`, 194,193 bytes, SHA-256 `bdb14fbedcfbcc4d3b3194edbfad428ac8869f1f8c75d848a6655147dd284dec` |
| Reduction commit | 9db2f3b (raw + reduced + execution note committed together) |
| Related record | 2139cdb duplicate-rerun disclosure (shakedown-table provenance); 0b37930 Round-4 direction debate |

## Method

Endpoints and the §5 rule were recomputed **from the raw artifact alone**:
each arm's `ᾱ_end` re-derived as the exact equal-weight mean of `A/255`
over live members from `terminal_census.histogram_A`; per-pair differences
`D_i` formed in exact Fractions; classified at `Δ_pair_floor = 4/255`;
rule replayed under thresholds 16/18/24. Cross-checks then compared every
retained reduced field against the independent recomputation. The raw's
embedded `source_manifest_sha256` (14 FROZEN_SOURCES) was matched pin-for-pin
against the freeze manifest.

## Auditor-definition disclosures (first-pass FAILs, all resolved as auditor error)

Three first-pass checks failed before the definitions below were read from
the frozen source; each was an **audit-script misconception**, not an
artifact defect. Recorded so the trail is honest:

1. Per-arm `direction_class` is measured against `α_ref = 3/5` at the
   8/255 floor (`stage8_alpha_measure.direction_class`), not against the
   pair difference `D_i`.
2. The registered leakage monitor is **terminal-census plurality**
   (`terminal_census.live_by_ancestry`), not lifetime `births_by_ancestry`
   (which legitimately diverges between arms when mutation changes division
   timing and vacancy dynamics).
3. `kernel_draw_chain` carries one entry per mutation *decision*
   (`== decision_records == admitted_births + memory_unavailable_failures`,
   the registered supply identity), while `draws_total` counts raw stream
   draws including non-mutating decisions (observed ratio ≈ 1.5 draws per
   birth, exactly what `p_μ = ½` two-draw mutations predict).

## Results — 17/17 checks PASS

| Check | Result |
|---|---|
| Hash binding | raw + reduced hashes recorded above; all 14 embedded source hashes match freeze pins, zero mismatches/unpinned |
| Endpoint recomputation | all 48 arms' `ᾱ_end` bit-exact from terminal histograms (also equals census `alpha_mean`) |
| Per-arm classes | every recorded class equals `direction_class(alpha_end)` vs α_ref 3/5 at floor 8/255 |
| Rule replay | k_eff = 24/24 eligible, up = 9, down = 6, non-mover = 9 → max class 9 < 18 ⇒ `NO_ESTABLISHED_DIRECTION`; matches retained outcome, counts block, and `applied_exactly_once: true` |
| D_i table | all 24 retained paired differences bit-equal to independent values |
| Descriptive medians | `median_abs_D_all_eligible = 437/24480` (= mean of middle pair 109/6120, 73/4080), movers-up `79/4080`, movers-down `−11/360` — all bit-exact |
| Leakage monitor | zero terminal-plurality ancestry disagreements across all 24 pairs; consistent with retained `leakage_pairs: []` |
| R0 integrity | kernel-absence pins hold on all 24 reference arms (empty chain, zero decisions/draws, telemetry passes, births > 0) |
| M reconciliation | chain == decision_records == births + memory-unavailable on all 24 kernel arms; draws_total ≥ chain everywhere |
| Corrected G2 semantics | `tick_checkpoints == W+2 == 2402`, head `['initial','initial','tick_complete:0']`, tail `'tick_complete:2399'` on every COMPLETE arm (both arms, all pairs) |
| Genome freeze | T=128/D=255 audits pass on all 48 arms |
| Window/extinctions | `ticks_completed == W == 2400`, zero extinct arms in all 48 runs |
| Protocol/table echo | protocol string identical across raw/reduced; seeds exactly `20310529 + i`, i = 0..23 |

Suite status at audit time: 423 tests OK (4 skipped).

## Scope

The registered outcome stands exactly as reduced: **rung 2 closes at this
ecology as a registered null (`NO_ESTABLISHED_DIRECTION`)** — the bounded
level-2 negative licensed by §5, with the empirical null-spread descriptives
above feeding the review directions as planned (Round-4 verdict 0b37930).
Nothing here widens, retunes, or reinterprets any closed quantity; both
artifacts are retained immutable.
