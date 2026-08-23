# Stage 7B Signed-Bracket Execution Note

*Date: 2026-08-23. The single authorised execution class of
`docs/stage-7b-signed-bracket-preregistration.md` §6.3 ran once under the
`7d21153` freeze; raw artifact reduced exactly once by the source-frozen
reducer.*

## Registered outcome

- **Pair-contrast class: `NO_ESTABLISHED_CONTRAST`.**
- Complete certified pairs: **32/32** (gate required ≥ 16 — the
  complete-pair availability defect that killed the three predecessor
  designs is closed: zero `NO_FINITE_ROOT`, zero `CRITICAL`).
- Median paired difference of finite-root upper brackets: **−1/128**,
  below the registered contrast floor `Δr_min = 1/100`.
- Subcritical report: `ONE_ARM_SUBCRITICAL`.

## Bracket status split (descriptive, per §3 table)

| Pair class (102/204) | Replicates |
|---|---|
| SUPERCRITICAL / SUBCRITICAL | 21 |
| SUBCRITICAL / SUPERCRITICAL | 9 |
| SUPERCRITICAL / SUPERCRITICAL | 2 |

Per-genotype supercritical counts: A=102 → 23/32; A=204 → 11/32. The sign
of the median paired difference favours LOW (A=102) but at 1/128 it does
not clear the registered floor, and the sign split across pairs (21 vs 9)
shows the direction is not uniform. Both facts are descriptive context;
the decision rule admits no gradient language.

## Integrity

- Raw artifact: 18,828,711 B,
  SHA-256 `6268a3dab1db878e72af565863b3d1a11831df02f3b3407693e8586d13273d3d`;
  32/32 `COMPLETE`; ledgers asserted after every operation with full
  immutable-history rescans at every tick-complete checkpoint.
- Reducer recomputed all estimators independently from cohort schedules
  and verified bit-exactly before applying the registered rule once.
- Execution wall time ≈ 54 min (`--workers 2`, two ~27-min worker
  processes); payload is seed-deterministic with no timestamps.

## Permitted conclusion (§8 scope)

At the carried ecology (N=48, E=900, W=1200) under the unchanged
two-factor endpoint with full-line solver certification: intervening on
the acquisition-allocation numerator between A=102 and A=204 produced a
median paired invasion-growth bracket difference of −1/128, which does
not meet the preregistered contrast floor; classification
`NO_ESTABLISHED_CONTRAST`. This establishes nothing about an optimum, an
ESS, a background-invariant causal effect, allocation plasticity, or any
external-validation mechanism.

## What this closes and what it opens

The Stage 7B confirmatory line closes here as a **registered null**: the
allocation channel exists mechanically (Stage 7B0), but at this ecology
its population-level expression in Euler–Lotka growth-rate terms is below
the registered detection floor. Three predecessor endpoint designs were
falsified en route and remain archived. Any stronger-contrast question
requires a new superseding preregistration (different ecology pressure,
longer windows, or a different endpoint family), never a re-run of this
one.

The `RUN-IN-PROGRESS.json` coordination marker is deleted by this commit
per its own instruction.
