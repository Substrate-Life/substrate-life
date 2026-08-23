# Stage 7B denominator-repair feasibility gate — NO-GO archive

Date: 2026-08-23 (execution window ~02:50–03:16 UTC; `--workers 2`, wall
≈ 26 min; exit 0)

## Classification

The
`docs/stage-7b-denominator-repair-preregistration.md` §5 binding
pre-freeze feasibility gate was executed as an unretained,
non-artifact-producing exploratory shakedown (per §5.5) on its fixed
24-seed table (`20270000 + j`, `j ∈ {0,…,23}`, the same table already
used by both predecessor gate generations — a third reuse isolating the
repaired endpoint layer). **The gate FAILED on G1/G2 while G3/G4 stayed
perfect — but with a signature qualitatively different from every
predecessor generation: supercriticality is now plainly reachable
(20/24 on one arm), and the failure is located in the *joint*
complete-pair precondition, not in any ceiling.** Per §5.4, no freeze may
be committed; the correct action is a further superseding preregistration
with a diagnosis supported by new evidence, which has been drafted as
`docs/stage-7b-signed-bracket-preregistration.md`. This directory archives
the failing evidence per the project's "archive failures, never delete"
rule; nothing here is retained evidence of any confirmatory claim.

## Gate outcome (24/24 replicates COMPLETE; G3/G4 passed; G1/G2 failed)

Under the repaired two-factor coefficients (`c_x = l^A_x · m^E_x`,
frozen `build_c_vector` assembly, unchanged solver contract):

- **G1** (each genotype supercritical — `L(0) > 1` under the frozen
  solver — in ≥ 2/3 of 24 replicates): genotype A=102: **20/24**
  supercritical → PASSES; genotype A=204: **7/24** supercritical →
  **FAILED** (needs 16).
- **G2** (both genotypes jointly supercritical in ≥ 2/3 of replicates):
  **3/24** joint (seeds 20270007, 20270008, 20270011). **FAILED**
  (needs 16).
- **G3** (zero `BUFFER_OVERFLOW`, zero `INVALID_IMPLEMENTATION`):
  **PASSED** — execution integrity perfect across all 24 replicates.
- **G4** (every ledger checkpoint closes; all five §3 binding identities
  hold inside the estimator): **PASSED** — zero failures.

Full per-condition counts and per-replicate records are preserved in
`gate-summary.json` (the exact stdout of
`stage7b_exposure_gate.py --workers 2` over the complete fixed table);
`gate-stderr.log` is the run's stderr. A single-seed plumbing check
(`--limit 1 --workers 1`) preceded the full run and reproduced seed
20270000's record bit-exactly against the full-run table (determinism
cross-check).

## Observed magnitudes (the new evidence)

Per-replicate records from `gate-summary.json`:

- **Perfect exclusion anti-correlation.** Exactly one arm is
  supercritical in 21 of 24 replicates (exclusive-102: 17;
  exclusive-204: 4); zero replicates have neither arm supercritical.
  Conditional structure: P(204 super | 102 sub) = 4/4 and
  P(102 sup | 204 sub) = 17/17 — whenever either arm fails to reach
  `L(0) > 1`, the other has already surpassed it.
- **Joint supercriticality ⟺ balanced cohorts.** The three joint
  replicates are exactly those where the loser cohort stays large
  (20270007: cohorts 301/219; 20270008: 305/202; 20270011: 274/220). In
  the remaining replicates one lineage captures the vacancy stream:
  e.g. 20270003 — cohorts 479 vs 18, births credited 476 vs 15.
- **Loser `L(0)` sits just below 1 when the loser is A=102** (range
  0.948–0.970, n=4) **and further below when the loser is A=204**
  (range 0.769–0.986, n=17); exclusive winners sit at 1.19–1.46 (102)
  and 1.32–1.54 (204); joint-replicate values are 1.05–1.14 (102) and
  1.59–2.02 (204).
- **The population is saturated throughout**: aggregate exposure per
  replicate ≈ 58k person-ticks over `W = 1200` ≈ 48.3 member-present
  ticks/tick against registered census capacity `N = 48`.
- **Every arm is measurable**: minimum cohort 13 (A=204), minimum
  births credited 10, minimum person-ticks 1,505 — coefficient vectors
  always exist with support beyond age 0.

## Root-cause diagnosis: complete-pair availability, not an endpoint defect

Unlike both predecessor generations, this failure admits no
definition-level impossibility proof (§5.4 anticipated exactly this:
"no injectivity- or collapse-type structural bound applies to the
two-factor coefficients … so a failure would demand fresh diagnostic
evidence"). The evidence above supports a structural-ecological
diagnosis:

- **D-A. The repaired endpoint behaves as designed.** Supercriticality
  is reachable (20/24 on arm 102; values up to `L(0) = 1.455`), G3/G4
  integrity is perfect, and every binding identity held. Nothing about
  the two-factor coefficients suppresses growth measurement.
- **D-B. The ecology produces winner-take-most exclusion dynamics.**
  With census pinned at capacity and a shared hazard-driven vacancy
  stream, the lineage that first establishes replication dominance
  captures most vacancies; the other persists as a small sliver whose
  measured `R_0` falls below 1 (downward-biased by accepted right-
  censoring at small cohort sizes). Which lineage wins is
  replicate-stochastic (priority effect): 102 wins exclusively 17
  times, 204 four times, and balanced coexistence-at-growth occurs only
  in 3/24 replicates.
- **D-C. The carried decision rule's statistical precondition is there-
  fore misaligned with the ecology it is applied to.** The §5 rule's
  complete-pair requirement ("both genotypes supercritical") was
  inherited from a solver contract that emits **no numeric `r_g` for a
  subcritical arm** (`stage-7b2-preregistration.md` §4 step 2), so
  paired differences exist only where both arms simultaneously grow.
  At this ecology that event is rare (~12.5% on the shakedown table)
  for dynamical reasons, not because either arm is unmeasurable. The
  gate conditions G1/G2 were derived from exactly that precondition
  (per repair principle D6), so their failure is the precondition's
  failure, faithfully detected before any freeze.
- **D-D. Registering another infeasible confirmatory suite is
  prohibited** (`stage-7b2-repair-preregistration.md` §6.3). Running
  the confirmatory suite under the current pair definition would
  project `DEGENERATE_REPLICATION` (~12.5% complete-pair availability
  against the required ≥ 50%). The repair must therefore target pair
  availability itself. The minimal repair consistent with the evidence
  re-grounds the solver contract on the **full real line**: Lotka's
  equation with non-zero age-≥1 support has a unique *real* root
  whether positive or negative, so every measurable arm can emit a
  certified signed bracket, complete pairs become available wherever
  both arms are measurable (all 24 shakedown replicates qualify),
  and the sign of the bracket carries the sub/supercritical
  classification instead of bracket absence. No threshold, seed,
  ecology, estimator, or mechanics change is needed or made.

## Consequence

The pre-freeze feasibility gate did exactly its registered job for the
third time: it caught an infeasible confirmatory design *before* any
freeze or retained execution — and, for the first time, at the level of
statistical design rather than estimator algebra. No freeze was
committed; no ecology parameter was retuned post hoc; the confirmatory
seed table (`20261822,…,20261853`) was never touched. The successor
preregistration `docs/stage-7b-signed-bracket-preregistration.md`
supersedes only the solver-domain line (`stage-7b2-preregistration.md`
§4 steps 1–2, as carried) and the consequent gate-condition derivation,
carrying forward every other registered decision verbatim.

## Preserved files

- `gate-summary.json`: the complete, unmodified stdout of the failing
  gate run (`stage7b_exposure_gate.py --workers 2` over all 24 fixed
  seeds).
- `gate-stderr.log`: the run's stderr (seed-table announcement).

No mutation, open-genome, or fitness/selection execution occurred at any
point. No retained artifact was produced by the gate.
