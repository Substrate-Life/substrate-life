# Stage 7B Denominator Repair Preregistration: Independent Two-Factor Euler–Lotka Coefficients (closing the shared-denominator normalisation defect)

**Protocol status:** SUPERSEDING preregistration. It supersedes exactly
the **endpoint coefficient assembly** registered at
`docs/stage-7b-endpoint-repair-preregistration.md` §3 — the scalar
cohort normalisation `m_x(g) = n_x(g)/|C_g|` together with its product
form `c_x = l_x · m_x`, whose survivorship and fecundity factors share a
single denominator set. It carries forward, verbatim and unchanged,
every other registered decision of that document's carried set: the
raw-fecundity *numerator* `n_x` (every admitted birth credited exactly
once to its immediate parent at the parent's attained age at the birth
tick); the establishment / first-reproduction quantity retained strictly
as a reported mediator; the reported descriptive survivorship `l_x` in
its existing reporting role; censoring and exposure conventions; the
solver contract (`stage-7b2-preregistration.md` §4); the §5 decision rule
and its thresholds (`Δr_min = 1/100`, `ρ_r = 1/256`, minimum 16 complete
pairs of 32); the vacancy-capture estimand decision (Blocker F); the
Stage 7B1 transaction/retirement/death/shadow mechanics; and the repaired
`stage-7b2-repair-preregistration.md` §3 ecology (`N=48`, `E=900`,
`W=1200`, seed base `20261822`, genotypes `(102,128,255)`/`(204,128,255)`,
3 founders/genotype, founder `S=100`/`R=0`, hazard arm `h=1/120`, corpse
TTL 2, buffer depth 64, shared memory pool 65,536 B, mutation disabled).
Corrections require a further superseding preregistration, never edits
here or in any superseded document.

**Evidence-era disclosure:** observed before this freeze: the retained
Stage 7B endpoint-repair implementation window (commits `3986aac`,
`cb6f9ce`) whose scope note flagged, as an exact definition-level
identity, that every admitted birth creates exactly one new member of
`C_g`; and the unretained, non-artifact-producing §5 feasibility-gate
execution of the endpoint-repair preregistration over its fixed 24-seed
table (`20270000 + j`), archived at
`failed-designs/2026-08-23-stage7b-endpoint-feasibility-gate-no-go/`
(results registered in §1 below). Additionally observed before this
commit: while constructing unit-scale synthetic test ledgers for the
repair conceived in an early draft of this document (pure
exposure-normalisation with the frozen `l_x` retained as the survivorship
factor), the definition-level collapse registered below as Lemma C came
to light — that conceived form is algebraically identical to the
superseded scalar endpoint — and the registered repair was widened to the
two-factor form of §3 **prior** to this document's commit. No execution
of any registered ecology occurred during that work; all evidence is
synthetic-ledger or gate-run material disclosed here. No fitness,
selection, optimum, or ESS claim exists in any Stage 7 artifact,
including this one.

**Authorisation:** this document registers decisions only. It authorises
no retained execution. A new, additively-defined measurement module
implementing the two-factor endpoint (§3 below) may be written after this
commit, reusing the unchanged event-ledger extraction of
`stage7b2_measure.py`, the unchanged solver (`stage7b2_solver.py`), the
unchanged population mechanics, and the unmodified raw-fecundity counting
of `stage7b_endpoint_measure.py`, all byte-identically. The existing
frozen modules `stage7b2_measure.py`, `stage7b2_population.py`,
`stage7b2_solver.py`, `stage7b2r_population.py` (and the frozen
`stage7b1_mechanics.py`) are never edited in place; neither are the
committed endpoint-repair generation modules, which remain exactly as
committed evidence of that window. Implementation, runner, reducer,
tests, output schema, and analysis tooling for any confirmatory execution
under the repaired coefficients must be frozen **together** with a
pre-execution manifest, committed before any retained run, and only after
a re-run of the §5-style feasibility gate against the repaired endpoint
passes at the carried §3 ecology. Mutation remains unauthorised in every
form.

## 1. Registered reading of the second gate outcome

The `stage-7b-endpoint-repair-preregistration.md` §5 gate was executed
this session as an unretained shakedown on its fixed 24-seed table, with
the following outcome (full evidence archived;
`failed-designs/2026-08-23-stage7b-endpoint-feasibility-gate-no-go/gate-summary.json`):

- **G1/G2 FAILED**: **0 of 24** replicates supercritical for either
  genotype under the raw-fecundity endpoint; 0 joint-supercritical pairs.
  All 48 certified values sat strictly below the structural ceiling:
  the largest was `L(0) = 5/6` (seed 20270020, A=204).
- **G3/G4 PASSED**: 24/24 replicates COMPLETE; zero `BUFFER_OVERFLOW`;
  zero `INVALID_IMPLEMENTATION`; every checkpoint closed.

This classification stands exactly as archived; it is not reopened or
retried here. What it establishes, together with the implementation-
window identity note, is that the endpoint-repair preregistration removed
only the *first* of two compounding structural defects. Its §2 proof
correctly showed the establishment filter forces `L(0) < 1`; its own
§5.4 then predicted that raw fecundity escapes the bound because
"`sum_x m_x(g)` is bounded only by total births per cohort member" —
that prediction conflated the birth count `B_g` (hundreds per replicate)
with the ratio `B_g / |C_g|` (≤ 1 identically), because **every admitted
birth is itself one new member of `C_g`**. The bound survived the
numerator repair untouched, and the gate confirmed it empirically at
0/24 on both arms with perfect execution integrity.

## 2. Structural diagnosis: shared-denominator collapse (derived from the registered definitions)

Registered definitions in force immediately before this document
(`stage-7b-endpoint-repair-preregistration.md` §3, binding):

- `n_x(g)`: number of admitted births credited to genotype-`g` parents at
  parent attained age exactly `x`; `sum_x n_x(g) = B_g`.
- Endpoint: `m_x(g) = n_x(g) / |C_g|` — a single genotype-level scalar
  denominator; `c_x = l_x · m_x`; `L(0) = sum_x c_x`; `0 ≤ l_x ≤ 1`.

**Lemma A (admitted-birth ↔ member correspondence).** Every admitted
birth creates exactly one new member of `C_g` (the child), founders being
admitted without birth; hence `B_g = |C_g| − F_g`. Verified empirically
to bit-exactness on real population output (implementation-window tests
and gate seed 20270000: cohorts 316/215 with births credited 313/212).

**Theorem B (scalar-denominator ceiling).** For the registered
normalisation `Q = |C_g|`:

$$L(0) = \sum_x l_x\,\frac{n_x}{Q} \le \sum_x \frac{n_x}{Q} = \frac{B_g}{Q} = 1 - \frac{F_g}{|C_g|} < 1$$

whenever `F_g ≥ 1` (true by construction: 3 founders/genotype). No
simulated quantity enters; supercriticality is unsatisfiable for every
genotype, replicate, ecology, and seed table under any endpoint whose
fecundity numerators are divided by one genotype-level headcount,
regardless of what filter produced the numerators. ∎

**Lemma C (collapse of single-denominator re-grounding).** Let `E_x(g)`
denote the genotype-`g` person-ticks lived at exact age `x`. Under the
carried exposure convention (one tick spent at each attained age),
`E_x(g)` equals the number of members attaining age `x` — precisely the
frozen numerator `l_counts[x]` of `l_x(x) = l_counts[x]/|C_g|`. Any
endpoint of the form

$$c_x = l_x\cdot\frac{n_x}{E_x} = \frac{l_{counts}[x]}{|C_g|}\cdot\frac{n_x}{l_{counts}[x]} = \frac{n_x}{|C_g|}$$

is therefore algebraically identical, term-for-term, to the superseded
scalar-cohort endpoint, and Theorem B binds it unchanged: `L(0) =
B_g/|C_g| < 1`. Merely moving the denominator from a headcount to
person-ticks *without changing the survivorship factor* is a no-op.
(Recorded as exact regression tests on concrete synthetic ledgers, where
the collapsed form yields exactly `B_g/|C_g|` on ledgers that genuinely
grow.) ∎

**Diagnosis.** The defect is not which single denominator normalises the
fecundity numerators; it is that both Euler–Lotka factors are normalised
over **one shared denominator set**, so their product cannot carry more
information than the raw counts over cohort size. Lotka's equation
requires two *independent* empirical curves: survival conditioned on
death risk sets, and fecundity conditioned on person-time at risk.

## 3. Registered repair decision

|| Item | Superseded definition (`stage-7b-endpoint-repair-preregistration.md` §3) | Registered replacement | Rationale |
|---|---|---|---|
| Fecundity factor | `m_x(g) = n_x(g)/|C_g|` | `m^E_x(g) = n_x(g)/E_x(g)`, person-tick fecundity conditional on being alive at age x; where `E_x(g) = 0`, `m^E_x(g) := 0`. `E_x(g)` recovered bit-exactly as `l_counts[x] = l_x[x]·|C_g|` from the frozen schedule integers. | Restores the units of the Euler–Lotka fecundity term (per-capita rate at age x). |
| Survivorship factor (endpoint role) | descriptive `l_x(g) = l_counts[x]/|C_g|` used directly as the Lotka factor | `l^A_0(g) := 1`; `l^A_{x+1}(g) := l^A_x(g)·(E_x(g) − d_x(g))/E_x(g)`, where `d_x(g)` is the number of genotype-g deaths at exact attained age x; right-censored members contribute exposure but no death; beyond the last attained age (`E_x = 0`) `l^A` is exactly 0. The descriptive `l_x` itself is unchanged and continues to be reported; it simply no longer enters the endpoint product. | Risk-set-conditioned (actuarial) survivorship is independent of cohort size and of birth timing, so the two factors carry distinct information; `L(0) = Σ l^A_x m^E_x` becomes the standard net reproductive rate `R_0`, unbounded above 1 exactly when the population genuinely grows. Under stationarity the estimator reference point is ≈ 1 (design rationale only, no claim). |
| Coefficient assembly | `c_x = l_x · m_x` | `c_x = l^A_x · m^E_x` assembled by the unchanged frozen `build_c_vector` (which accepts any exact survivorship vector); solved by the unchanged certified solver contract (`ρ_r = 1/256`, per-tick units throughout). | Form of the equation unchanged; only the two empirical curves feeding it are re-grounded. |
| Binding identities | (new) | Every artifact/reduction must satisfy exactly: (i) `Σ_x E_x(g) = exposure_member_ticks(g)`; (ii) `Σ_x n_x(g) = |C_g| − F_g`; (iii) `n_x(g) ≤ E_x(g)` ∀x; (iv) `Σ_x d_x(g) + censored_g = |C_g|`; (v) `l^A_0 = 1`, `l^A` non-increasing, `0 ≤ l^A ≤ 1`. Violation fails the run loudly. | Cheap exact integrity gates tying both new factors to already-frozen quantities. |
| Censoring & exposure conventions | carried verbatim | carried verbatim, now binding for both `E_x` and `d_x`: exposure accrues only within `[0, W]` (including the death tick); members alive at `W` contribute no death anywhere; **no extrapolation or imputation of any kind**. Right-censoring of unfinished careers biases `R_0` downward; this bias is accepted and registered rather than corrected. | The protocol measures windows, not lifetimes beyond them. |
| Numerator `n_x`, establishment mediator, reported descriptive `l_x`, solver contract, decision rule, thresholds, ecology, confirmatory seed table, vacancy-capture estimand | unchanged | carried verbatim | Isolated to the coefficient assembly layer; nothing else changes meaning. |

Carried verbatim, restated as binding: every decision of
`stage-7b-endpoint-repair-preregistration.md` §§1–2, 4–8 except its §3
endpoint line and its §5 gate outcome (archived, §1 above); and through
it every decision of `stage-7b1-preregistration.md` §§1–5, 6.2–9,
`stage-7b2-preregistration.md` §§1, 3 (solver contract), 4, 5, 6, 7, and
`stage-7b2-repair-preregistration.md` §§1–8 except as already superseded
downstream.

## 4. Registered question (unchanged form, repaired coefficients)

Under the carried ecology (`N=48`, `E=900`, `W=1200`, exogenous
phenotype-blind hazard `h=1/120`) with binding vacancy admission, do the
two carried allocation strategies differ in per-genotype invasion growth
`r_g` — now the solution of Lotka's equation using the two-factor
coefficients `c_x = l^A_x m^E_x` of §3 — by at least `Δr_min = 1/100`
across `k = 32` seeded replicates, with the carried §5 rule applied
exactly once? The estimand remains the per-genotype replicate
distribution of certified rational brackets `[r_lo, r_hi]`. No optimum,
ESS, background-invariant causal effect of α, or external-validation
claim is registered, tested, or permitted. The establishment signal
continues to be reported as a mediator, never as the endpoint.

## 5. Pre-freeze feasibility gate (binding, re-derived from this document's own decision rule)

Per the registered repair principle (`stage-7b2-repair-preregistration.md`
§2 D6), the carried §5 rule's precondition (≥ 16 simultaneous
both-genotype-supercritical outcomes of 32) again binds the
implementation window:

1. Implement the two-factor estimator as new, additively-defined code
   reusing the frozen modules byte-identically (§3 recovery routes;
   `stage7b_endpoint_measure.py` reused unmodified for the numerator).
2. Run unretained exploratory shakedowns at the exact carried ecology on
   the **same fixed 24-seed table** (`20270000 + j`, `j ∈ {0,…,23}`) used
   by both prior gate generations — no new draw is needed or permitted.
   A third reuse is what isolates the repaired layer: three endpoint
   generations evaluated on identical seeds differ *only* in the
   endpoint definition.
3. Gate conditions, all mandatory, unchanged:
   **G1** each genotype supercritical in ≥ 2/3 of the 24 replicates;
   **G2** both genotypes jointly supercritical in ≥ 2/3 of replicates;
   **G3** zero `BUFFER_OVERFLOW` / `INVALID_IMPLEMENTATION`;
   **G4** every checkpoint closes.
4. If any condition fails, no freeze may be committed: the correct action
   is a further superseding preregistration with a diagnosis supported by
   new evidence. Unlike both predecessor generations, no injectivity- or
   collapse-type structural bound applies to the two-factor coefficients
   (Lemmas A/C do not reach them: the factors' denominator sets are
   independent by construction), so a failure would demand fresh
   diagnostic evidence, not another definition-level impossibility proof.
5. Shakedown executions produce no retained artifact (stdout only). If
   the gate passes, a factual summary must be recorded in the freeze
   commit's manifest directory notes, as before.

## 6. Freeze-before-execution and authorised execution class

1. Implementation window opens on commit of this document; no retained
   execution occurs during it.
2. After §5 passes: freeze the new estimator, configuration label layer,
   gate tooling, runner, reducer, tests, and output schema **together**
   with the reused modules pinned by hash, as a pre-execution manifest
   with SHA-256 + byte size per file, committed before any retained run.
3. The authorised execution class is then one seeded, mutation-disabled
   confirmatory suite: `k = 32` replicate populations under the carried
   ecology, reduced exactly once under the carried §5 rule using the
   repaired coefficients, raw output retained under a new results path
   (`results/stage7b-exposure-endpoint/`; no collision with, or
   implication about, any earlier retained path).
4. PASS criterion: every ledger closes at every registered checkpoint in
   every replicate; every solver certification is valid; every §3 binding
   identity holds in every reduction; the carried §5 rule is applied
   exactly once and its outcome recorded. Any failure retains the run,
   classifies it, and triggers repair — archiving, never deletion.

## 7. Standing-rules compliance and falsification-gate mapping

Exact `Fraction` arithmetic in every ledger; `E_x`/`d_x` recovery and all
coefficient assembly in exact integer/Fraction arithmetic; solver
enclosure arithmetic analysis-side only. Telemetry labels never read by
mechanics. Gates engaged: conservation, packet-sink, vacancy, endpoint
(the two-factor coefficients are the primary fix registered here),
trait-isolation, trait-resolution, ecology, storage, plasticity-scope,
age-state/somatic-state reporting — all carried unchanged from the
documents this one supersedes in part.

## 8. Not authorised by this document

Any retained execution before the §5 gate passes and the §6 freeze is
committed; mutation at any locus; open genomes; in-place edits to any
existing frozen module (`stage7b1_mechanics.py`, `stage7b2_measure.py`,
`stage7b2_population.py`, `stage7b2_solver.py`,
`stage7b2r_population.py`) or to the committed endpoint-repair generation
modules (`stage7b_endpoint_measure.py`, `stage7b_endpoint_config.py`,
`stage7b_endpoint_gate.py`, `run_stage7b_endpoint.py`,
`reduce_stage7b_endpoint.py`), which remain as committed evidence;
re-litigating either archived gate failure under superseded endpoints;
additional hazard levels, directional predictions, or factorial
separation studies; endpoint substitution beyond the single
coefficient-assembly repair registered in §3; changes to `Δr_min`,
`ρ_r`, either seed table, or the ecology; optimum, ESS, or
background-invariant causal claims; interior-lattice or extrapolated
landscape claims; plasticity interpretations; reuse of pre-Stage-7
quantities; modification of retained artifacts or superseded documents;
history rewrites.
