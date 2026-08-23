# Stage 7B-Endpoint Repair Preregistration: Correcting the Establishment-Filtered `m_x` Defect (Blocker E revision)

**Protocol status:** SUPERSEDING preregistration. It supersedes exactly the
`m_x(g)` definition of `docs/stage-7b1-preregistration.md` §6.1 ("`m_x`
counts births established through first reproduction of the offspring"),
which is inherited, binding, and unchanged by every descendant document
(`stage-7b2-preregistration.md` §3, `stage-7b2-repair-preregistration.md`
§3). It carries forward, verbatim and unchanged, every other registered
decision of those three documents: the transaction/retirement/death/shadow
mechanics of `stage7b1_mechanics.py`; the repaired §3 ecology of
`stage-7b2-repair-preregistration.md` (`N=48`, `E=900`, `W=1200`, seed base
`20261822`, genotypes, founders, hazard arm, buffer/memory bounds); the
solver contract (§4 of `stage-7b2-preregistration.md`); the §5 decision
rule and its thresholds (`Δr_min = 1/100`, `ρ_r = 1/256`, minimum 16
complete pairs of 32); the vacancy-capture estimand decision (Blocker F).
Corrections require a further superseding preregistration, never edits
here or in any superseded document.

**Evidence-era disclosure:** observed before this freeze: the retained
Stage 7B2 confirmatory suite (`DEGENERATE_REPLICATION` / `BOTH_SUBCRITICAL`,
committed `e36be84`); the `stage-7b2-repair-preregistration.md` ecology
repair (committed `46c8ccb`); the unretained, non-artifact-producing §6
feasibility-gate execution of that repair over its fixed 24-seed table
(`20270000+j`), archived at
`failed-designs/2026-08-22-stage7b2r-feasibility-gate-no-go/`: **0 of 24**
shakedown replicates reached `L(0) > 1` for **either** genotype (G1 failed
for both arms; G2 failed), while execution integrity was perfect (G3, G4
both passed — zero `BUFFER_OVERFLOW`, zero `INVALID_IMPLEMENTATION`, zero
checkpoint failures). Never observed anywhere in project history: any
supercritical genotype-replicate under the establishment-filtered `m_x`
definition, at any ecology; any complete contrast pair; any numeric `r_g`.
No fitness, selection, optimum, or ESS claim exists in any Stage 7
artifact, including this one.

**Authorisation:** this document registers a decision only. It authorises
no execution. A new, additively-defined measurement module
implementing the corrected `m_x` (§3 below) may be written after this
commit, reusing the unchanged event-ledger extraction of
`stage7b2_measure.py` and the unchanged solver (`stage7b2_solver.py`)
byte-identically; **the existing frozen modules `stage7b2_measure.py`,
`stage7b2_population.py`, `stage7b2_solver.py`, `stage7b2r_population.py`
are never edited in place** — they remain byte-identical to their pinned
hashes in the retained `results/stage7b2/pre-execution-manifest.json` and
the disclosed `stage7b2r_population.py` construction, so the already-
retained Stage 7B2 evidence and its audit trail are never disturbed.
Implementation, runner, tests, output schema, reducer, and analysis script
for any confirmatory execution under the corrected endpoint must be frozen
**together** with a pre-execution manifest, committed before any retained
run, and only after a re-run of the (unretained) §6-style feasibility gate
against the corrected endpoint passes at the carried §3 ecology. Mutation
remains unauthorised in every form.

## 1. Registered reading of the gate outcome

The `stage-7b2-repair-preregistration.md` §6 gate is not reopened,
reinterpreted, or retried at a different ecology by this document: its
`FAILED` classification stands exactly as archived. What this document
repairs is the **endpoint definition** that made the gate's G1/G2
conditions structurally unsatisfiable, independent of the ecology the gate
was testing.

## 2. Structural proof of the defect (derived from the registered definitions themselves)

Registered definitions in force before this document (`stage-7b1-preregistration.md`
§6.1, `stage-7b2-preregistration.md` §3, unchanged by the repair):

- `C_g`: the set of genotype-`g` members ever alive in a replicate,
  including `F_g` founders and every genotype-`g` offspring born during the
  window (mutation disabled ⇒ genotype invariant along a lineage).
- `l_x(g) = |{m ∈ C_g : m attains age ≥ x}| / |C_g|`; by construction
  `l_0(g) = 1` and `0 ≤ l_x(g) ≤ 1` for every `x`.
- **Establishment rule (the defect):** an establishment event exists for
  member `m ∈ C_g` iff `m` is **not** a founder and `m` itself performs at
  least one successful reproduction during the window; exactly one event is
  recorded, at the tick of `m`'s *first* reproduction, crediting `m`'s own
  parent `p` at `p`'s attained age at that tick. `m_x(g) = $(\#$ establishment
  events crediting a genotype-`g` parent at exactly age `x)$ / |C_g|`.
- `c_x = l_x(g)\cdot m_x(g)`; `L(0) = \sum_{x=0}^{W} c_x`.

**Claim.** `L(0) < 1` for every genotype `g` in every replicate, at every
registered ecology, whenever `F_g ≥ 1` (true by construction: 3
founders/genotype in every Stage 7B2/7B2-R registration).

**Proof.** Since `0 ≤ l_x(g) ≤ 1` for all `x`, `c_x ≤ m_x(g)` termwise, so
`L(0) = \sum_x c_x \le \sum_x m_x(g)`. The map from establishment events to
members is injective: the source data structure (`first_reproduction`) is
keyed by the unique reproducing member `m`, and at most one establishment
event is ever recorded per key (the *first* reproduction only). Every such
`m` is, by the establishment rule itself, a **non-founder** member of
`C_g`. Therefore the total establishment-event count for genotype `g` is at
most `|C_g| - F_g`, the number of non-founder members, and
$$\sum_x m_x(g) = \frac{\#\text{establishment events}(g)}{|C_g|} \le \frac{|C_g| - F_g}{|C_g|} = 1 - \frac{F_g}{|C_g|} < 1.$$
Hence `L(0) \le \sum_x m_x(g) < 1`. This bound uses no simulated quantity
except the registered definitions and `F_g ≥ 1`; it holds for **every**
value of `N`, `E`, `W`, hazard rate, packet rate, or buffer depth. ∎

**Empirical corroboration (unretained, archived alongside the failed
gate):** on shakedown seed `20270000` at the repaired `7B2-R` ecology,
genotype A=102 had cohort size 316 with 313 non-founder members against 14
establishment events (`14 ≤ 313`); genotype A=204 had cohort size 215 with
212 non-founder members against 10 establishment events (`10 ≤ 212`),
exactly matching the bound. Both genotypes' census reached full capacity
(48) well inside the window in every spot-checked seed — direct evidence
that the population itself is demonstrably growing while the registered
endpoint reports `L(0)` between `0.01` and `0.11`, confirming the endpoint
measures a different, much stricter quantity than population growth.

## 3. Registered repair decision

| Item | Superseded definition (`stage-7b1-preregistration.md` §6.1) | Registered replacement | Rationale |
|---|---|---|---|
| `m_x(g)` | credits a parent only when the **specific offspring born to that parent** itself later reproduces (two-generation-deep, "established" lineage count) | `m_x(g) = |\{$ births to a genotype-`g` parent of age exactly `x\}| / |C_g|`$ — **raw age-specific fecundity**: every birth counts once, credited to its immediate parent at the parent's age at the birth tick; no requirement that the offspring itself reproduce | Restores the textbook Euler-Lotka correspondence cited by the very equation this endpoint solves (`stage-7b1-preregistration.md` §6.1: `Σ e^{-rx} l_x m_x = 1`), where `m_x` is per-capita fecundity, not a filtered two-generation lineage-survival statistic. Under raw fecundity, `L(0) = R_0` is the standard net reproductive rate and is unbounded above 1 whenever the population is genuinely growing, matching the census-saturation evidence in §2. |
| Establishment / first-reproduction quantity | (was the endpoint numerator) | **retained as a reported mediator**, unchanged in every other respect: "subsequent reproductive contribution" already appears in the registered causal-chain telemetry (`stage-7b1-preregistration.md` §6.1) and continues to be reported exactly as before, now explicitly never substituted for the endpoint | No information is discarded; the two-generation persistence signal remains fully auditable, it is simply no longer conflated with the primary invasion-growth endpoint. |
| `l_x(g)` | unchanged | unchanged | Survivorship measurement is not implicated in the defect (§2 proof uses only `l_x ≤ 1`, which holds under either `m_x` definition). |
| Censoring, exposure, solver contract, decision rule, ecology (`N`, `E`, `W`, seed table), vacancy-capture estimand | unchanged | unchanged, carried verbatim | The defect is isolated to the `m_x` numerator; nothing else in the registered protocol stack is implicated. |

Carried verbatim, restated as binding: every decision of
`stage-7b1-preregistration.md` §§1–5, 6.2–9 not listed above; every
decision of `stage-7b2-preregistration.md` §§1, 3 (solver contract), 4,
5, 6, 7 except the superseded `m_x` line of its §3; every decision of
`stage-7b2-repair-preregistration.md` §§1, 3 (ecology table), 4, 5, 6, 7, 8
except the §6 gate outcome, which stands as archived (§1 above) and is not
retried under the old endpoint.

## 4. Registered question (unchanged form, corrected endpoint)

Under the carried §3 ecology (`stage-7b2-repair-preregistration.md`, `N=48`,
`E=900`, `W=1200`, exogenous phenotype-blind hazard `h=1/120`) with binding
vacancy admission, do the two carried allocation strategies differ in
per-genotype invasion growth `r_g` — now the solution of Lotka's equation
using the corrected raw-fecundity `m_x` of §3 — by at least
`Δr_min = 1/100` across `k = 32` seeded replicates, with the carried §5 rule
applied exactly once? The estimand remains the per-genotype replicate
distribution of certified rational brackets `[r_lo, r_hi]`. No optimum,
ESS, background-invariant causal effect of α, or external-validation claim
is registered, tested, or permitted. The two-generation establishment
signal is reported as a mediator, never as the endpoint.

## 5. Pre-freeze feasibility gate (binding, re-derived from this document's own decision rule)

Per the repair principle registered at `stage-7b2-repair-preregistration.md`
§2 D6 ("every future confirmatory registration's implementation-window gate
must be derived from the statistical preconditions of its own decision
rule"), the carried §5 rule's precondition (≥16 simultaneous both-genotype-
supercritical outcomes of 32) again binds the implementation window:

1. Implement the corrected measurement module (raw-fecundity `m_x`) as new,
   additively-defined code; the existing frozen `stage7b2_measure.py`,
   `stage7b2_population.py`, `stage7b2_solver.py`, and
   `stage7b2r_population.py` are reused **unmodified** for everything else
   (event-ledger extraction of members/births/exposures, the solver, the
   population mechanics, the ecology constants).
2. Run unretained exploratory shakedowns at the exact carried §3
   configuration on the **same fixed 24-seed table already used and
   archived** by the failed gate (`20270000 + j`, `j ∈ {0,…,23}`) — no new
   seed draw is needed or permitted; reusing this table under the corrected
   estimator is the direct, minimal test of whether the repair (not a new
   ecology) resolves the defect.
3. Gate conditions, all mandatory, unchanged from
   `stage-7b2-repair-preregistration.md` §6: **G1** each genotype
   supercritical in ≥2/3 of the 24 replicates; **G2** both genotypes
   jointly supercritical in ≥2/3 of replicates; **G3** zero
   `BUFFER_OVERFLOW`/`INVALID_IMPLEMENTATION`; **G4** every checkpoint
   closes.
4. If any condition fails, no freeze may be committed: the correct action
   is a further superseding preregistration with a new diagnosis (which,
   given the §2 proof, would need to identify a *different* structural
   cause — the `m_x` defect itself is now closed by construction, since raw
   fecundity has no analogous injectivity bound: a single member can be
   credited at multiple ages across multiple births, and `\sum_x m_x(g)`
   is bounded only by total births per cohort member, which is empirically
   in the hundreds per cohort at this ecology per the §2 evidence).
5. Shakedown executions produce no retained artifact. A factual summary of
   the gate outcome must be recorded in the freeze commit's manifest
   directory notes, exactly as `stage-7b2-repair-preregistration.md` §6.4
   requires.

## 6. Freeze-before-execution and authorised execution class (for the successor session)

1. Implementation window opens on commit of this document; no retained
   execution occurs during it.
2. After §5 passes: freeze the new measurement module, the unchanged
   reused modules (by reference to their existing pinned hashes), the
   runner, reducer, tests, and output schema **together**, with SHA-256 +
   byte size per file, committed before any retained run.
3. The authorised execution class is then one seeded, mutation-disabled
   confirmatory suite: `k = 32` replicate populations under the carried §3
   ecology, reduced exactly once under the carried §5 rule using the
   corrected `m_x`, raw output retained under a new results path
   (`results/stage7b-endpoint-repair/`, to avoid any collision with or
   implication about the retained `stage7b2`/`stage7b2-repair` paths).
4. PASS criterion: every ledger closes at every registered checkpoint in
   every replicate; every solver certification is valid; the carried §5
   rule is applied exactly once and its outcome recorded. Any failure
   retains the run, classifies it, and triggers repair — archiving, never
   deletion.

## 7. Standing-rules compliance and falsification-gate mapping

Exact `Fraction` arithmetic in every ledger; solver enclosure arithmetic
analysis-side only. Telemetry labels never read by mechanics. Gates
engaged: conservation, packet-sink, vacancy, endpoint (the corrected
endpoint is the primary fix registered here; mediators, including the
former endpoint's establishment signal, stay mediators and earn nothing on
their own), trait-isolation, trait-resolution, ecology, storage,
plasticity-scope, age-state/somatic-state reporting — all carried
unchanged from the documents this one supersedes in part.

## 8. Not authorised by this document

Any execution before the §5 gate passes and the §6 freeze is committed;
mutation at any locus; open genomes; in-place edits to any existing frozen
module (`stage7b2_measure.py`, `stage7b2_population.py`,
`stage7b2_solver.py`, `stage7b2r_population.py`, or their runners/reducers);
re-litigating the archived §6 gate failure of
`stage-7b2-repair-preregistration.md` under the old endpoint; additional
hazard levels, directional predictions, or factorial separation studies;
endpoint substitution beyond the single correction registered in §3;
`Δr_min`, `ρ_r`, or seed-table changes; optimum, ESS, or background-
invariant causal claims; interior-lattice or extrapolated landscape claims;
plasticity interpretations; reuse of pre-Stage-7 quantities; modification
of retained artifacts or superseded documents; history rewrites.
