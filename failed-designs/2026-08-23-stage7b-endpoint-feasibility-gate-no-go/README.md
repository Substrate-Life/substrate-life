# Stage 7B endpoint-repair feasibility gate — NO-GO archive

Date: 2026-08-23

## Classification

The `docs/stage-7b-endpoint-repair-preregistration.md` §5 binding
pre-freeze feasibility gate was executed as an unretained,
non-artifact-producing exploratory shakedown (per §5.5) on its fixed
24-seed table (`20270000 + j`, `j ∈ {0,…,23}`, the same table already
used and archived by the failed 7B2-R gate). **The gate FAILED.** Per
§5.4, no freeze may be committed; the correct action is a further
superseding preregistration, which has been drafted as
`docs/stage-7b-denominator-repair-preregistration.md`. This directory
archives the failing evidence per the project's "archive failures, never
delete" rule; nothing here is retained evidence of any confirmatory
claim.

## Gate outcome (24/24 replicates COMPLETE; G3/G4 passed; G1/G2 failed)

- **G1** (each genotype supercritical in ≥2/3 of 24 shakedown replicates,
  under the corrected raw-fecundity `m_x`): genotype A=102: **0/24**
  supercritical; genotype A=204: **0/24** supercritical. **FAILED for
  both arms.**
- **G2** (both genotypes jointly supercritical in ≥2/3 of replicates):
  **0/24** joint. **FAILED.**
- **G3** (zero `BUFFER_OVERFLOW`, zero `INVALID_IMPLEMENTATION`):
  **PASSED** — execution integrity perfect across all 24 replicates.
- **G4** (every ledger checkpoint closes in every replicate): **PASSED**
  — zero checkpoint failures.

Full per-condition counts are preserved in `gate-summary.json` (the exact
stdout of `stage7b_endpoint_gate.py --workers 2` over the complete fixed
table).

## Observed magnitudes

Across all 48 genotype-replicates, certified `L(0)` ranged from
`10102/…` ≈ 0.10 up to **5/6 ≈ 0.833** (seed 20270020, A=204) — every
value strictly below 1 and below the structural ceiling `1 − F_g/|C_g|`
(the largest ceilings occur in the smallest cohorts). Cohorts ranged
58–522 (A=102) and 13–491 (A=204); admitted births credited per replicate
were in the hundreds for at least one genotype in every replicate
(e.g. seed 20270000: births credited 313/212 against cohorts 316/215 =
`|C_g|` with `F_g = 3` — the births↔members identity of the
implementation-window note, visible to bit-exactness).

## Root-cause diagnosis: the scalar-cohort denominator layer

The endpoint-repair preregistration's own §2 proof correctly showed the
establishment filter forces `L(0) < 1`; its §5.4 then predicted raw
fecundity escapes the bound because "`sum_x m_x(g)` is bounded only by
total births per cohort member". That prediction conflated the birth
count `B_g` (hundreds here) with the ratio `B_g / |C_g|`: **every
admitted birth is itself one new member of `C_g`**, so
`sum_x n_x(g) = |C_g| − F_g` identically, and with `l_x ≤ 1` termwise,

$$L(0) = \sum_x l_x \frac{n_x}{|C_g|} \le \frac{B_g}{|C_g|} = 1 - \frac{F_g}{|C_g|} < 1.$$

The bound survived the numerator repair untouched; this gate run
confirms it empirically at 0/24 on both arms while execution integrity
stayed perfect — the same signature as the archived 7B2-R failure,
located one layer deeper. The defect is therefore not the numerator
filter (closed by `17b6aed`) but the **scalar-cohort normalisation**: any
endpoint whose fecundity numerators are divided by a single
genotype-level headcount cannot certify supercritically in this closed
admission world, regardless of ecology or seeds.

A sharper definition-level fact, registered as Lemma C of the successor
preregistration: even replacing the scalar denominator by per-age
person-ticks `E_x` is insufficient *by itself*, because the frozen
survivorship factor shares that same count (`E_x ≡ l_counts[x]`), so the
product collapses algebraically: `l_x · (n_x/E_x) = n_x/|C_g|`
term-for-term. The repair registered in
`docs/stage-7b-denominator-repair-preregistration.md` therefore re-grounds
**both** Euler–Lotka factors in independent denominator sets:
risk-set-conditioned window-actuarial survivorship `l^A_{x+1} =
l^A_x(E_x − d_x)/E_x` times person-tick fecundity `m^E_x = n_x/E_x`,
making `L(0) = Σ l^A_x m^E_x` the standard net reproductive rate `R_0`.
On synthetic unit-scale ledgers with juvenile mortality and sustained net
growth, the repaired coefficients certify `L(0) > 1` (e.g. `41/27`)
while both predecessor endpoints certify subcriticality on the *same*
ledgers — recorded as exact regression tests, not claims about any
registered ecology.

## Consequence

The pre-freeze feasibility gate did exactly its registered job for the
second time: it caught an infeasible confirmatory design *before* any
freeze or retained execution. No freeze was committed; no registered
ecology parameter was retuned post hoc; the confirmatory seed table
(`20261822,…,20261853`) was never touched. The repair now targets the
normalisation/coefficient-assembly layer itself, superseding only the
endpoint decision of `stage-7b-endpoint-repair-preregistration.md` §3
and carrying forward every other registered decision verbatim.

## Preserved files

- `gate-summary.json`: the complete, unmodified stdout of the failing
  gate run (`stage7b_endpoint_gate.py --workers 2` over all 24 fixed
  seeds).

No mutation, open-genome, or fitness/selection execution occurred at any
point. No retained artifact was produced by the gate.
