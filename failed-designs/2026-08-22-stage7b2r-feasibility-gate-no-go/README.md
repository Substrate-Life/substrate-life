# Stage 7B2-R feasibility gate — NO-GO archive

Date: 2026-08-22

## Classification

The `docs/stage-7b2-repair-preregistration.md` §6 binding pre-freeze
feasibility gate was executed as an unretained, non-artifact-producing
exploratory shakedown (per §6.4) on its fixed 24-seed table
(`20270000 + j`, `j ∈ {0,…,23}`, disjoint from every confirmatory table).
**The gate FAILED.** Per §6.3, no freeze may be committed at the repaired
§3 ecology (`N=48`, `E=900`, `W=1200`, seed base `20261822`); the correct
action is a further superseding preregistration, which has been drafted as
`docs/stage-7b-endpoint-repair-preregistration.md`. This directory archives
the failing evidence per the project's "archive failures, never delete"
rule; nothing here is retained evidence of any confirmatory claim.

## Gate outcome (24/24 replicates COMPLETE; G3/G4 passed; G1/G2 failed)

- **G1** (each genotype supercritical in ≥2/3 of 24 shakedown replicates):
  genotype A=102: **0/24** supercritical; genotype A=204: **0/24**
  supercritical. **FAILED for both arms.**
- **G2** (both genotypes jointly supercritical in ≥2/3 of replicates):
  **0/24** joint. **FAILED.**
- **G3** (zero `BUFFER_OVERFLOW`, zero `INVALID_IMPLEMENTATION`): **PASSED**
  — execution integrity was perfect across all 24 replicates.
- **G4** (every ledger checkpoint closes in every replicate): **PASSED**
  — zero checkpoint failures.

Full per-condition counts are preserved in `gate-summary.json` (the exact
stdout of `stage7b2r_gate.py --workers 2` over the complete fixed table).

## Root-cause diagnosis: the endpoint definition, not the ecology

`docs/stage-7b2-repair-preregistration.md` diagnosed the prior `7B2`
`DEGENERATE_REPLICATION`/`BOTH_SUBCRITICAL` outcome as a vacancy/census
feasibility defect (D1–D5) and repaired `N`, `E`, `W` accordingly. The §6
gate result falsifies that diagnosis as *sufficient*: even with roughly 4×
the census headroom, 3× the packet energy, and 2× the window, **zero of 48
genotype-replicates across the shakedown table reached `L(0) > 1`.**
`diagnostic-magnitudes.json` (5 spot-check seeds, unretained) shows why:
establishment counts (19–31 per replicate, both genotypes combined) are two
orders of magnitude below admitted births (~470–540 per replicate) — the
same qualitative shortfall D4 found in the original `7B2` run, essentially
unchanged by the ecology repair.

A structural proof (registered formally in
`docs/stage-7b-endpoint-repair-preregistration.md` §2) shows this is not a
tuning problem at all: given the registered establishment rule ("`m_x`
counts births established through first reproduction of the offspring",
`stage-7b1-preregistration.md` §6.1, binding on every descendant
registration), `L(0) < 1` is **mathematically guaranteed for every
genotype in every replicate at any ecology**, as long as at least one
founder exists per genotype (true by construction: 3 founders/genotype in
every Stage 7B2/7B2-R registration). No value of `N`, `E`, `W`, or the
hazard rate can ever satisfy G1/G2 under this endpoint definition. The
`7B2-R` ecology repair was a legitimate, well-reasoned response to the
evidence available at the time, but it targeted the wrong layer of the
protocol.

## Consequence

The pre-freeze feasibility gate did exactly its registered job: it caught
an infeasible confirmatory design *before* any freeze or retained
execution, exactly as `stage-7b2-repair-preregistration.md` §6.3 intends.
No freeze was committed; no registered ecology parameter was retuned post
hoc; the confirmatory seed table (`20261822,…,20261853`) was never touched.
The repair now targets the Blocker E endpoint definition itself, registered
as a further superseding preregistration
(`docs/stage-7b-endpoint-repair-preregistration.md`), which supersedes only
`stage-7b1-preregistration.md` §6.1's `m_x` definition and carries forward
every other registered decision (7B1 transaction/retirement/death/shadow
mechanics, 7B2-R's `N/E/W`/seed-table repair, the solver contract, the
decision rule) verbatim.

## Preserved files

- `gate-summary.json`: the complete, unmodified stdout of the failing gate
  run (`stage7b2r_gate.py --workers 2` over all 24 fixed seeds).
- `diagnostic-magnitudes.json`: unretained exploratory recovery of
  per-replicate `L(0)`, establishment counts, and census/vacancy magnitudes
  on 5 spot-check seeds from the same fixed table, used only to derive the
  numbers cited above; not confirmatory evidence of any kind.

No mutation, open-genome, or fitness/selection execution occurred at any
point. No retained artifact was produced by the gate or the diagnostic.
