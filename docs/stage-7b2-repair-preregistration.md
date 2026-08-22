# Stage 7B2-R Preregistration: Repair-Policy Review of the `DEGENERATE_REPLICATION` Outcome — Feasibility-Derived Ecology Revision

**Protocol status:** SUPERSEDING preregistration, committed under the repair policy of `stage-7b2-preregistration.md` §5, which binds the registered outcome class `DEGENERATE_REPLICATION` to "repair-policy review of the registration (a further superseding preregistration), never post hoc reinterpretation." This document registers that review's decisions. It supersedes the *ecology parameters* of the 7B2 registration (`N`, packet energy, window, seed table) and adds a binding pre-freeze feasibility gate; it carries forward every other registration of `stage-7b2-preregistration.md` §§1, 3–5 verbatim. Corrections require a further superseding preregistration, never edits here or in any superseded document.

**Evidence-era disclosure:** observed before this freeze: the entire retained Stage 7B2 confirmatory suite (`results/stage7b2/stage7b2-result.json`, SHA-256 `268d37e5bc1be84a5147413b960957b3c14cea3e647fafd6f6cf440648e668aa`, 1,887,200 bytes; reduced against it by `results/stage7b2/stage7b2-reduced.json`, SHA-256 `68fe9897ed294a9ed7247afc86a127630822fbbd041c531ef865b883e4b0194f`). Aggregates over its 32 `COMPLETE` replicates, all now part of the evidence era: 95,994 admission decisions (`shadow_decisions`), 2,132 wins (`would_admit` = admitted births), 93,862 `NO_VACANCY` failures, 0 `CHILD_MEMORY_UNAVAILABLE` attempts, 1,940 hazard deaths, 186 establishment events, ever-alive members 1,706 (A=102) vs 618 (A=204); per-newborn establishment probability 186/2132; win rate 2132/95994; `L(0)` maxima 64/1225 (A=102) and 1/6 (A=204) against the supercritical threshold 1. Never observed anywhere in project history: any supercritical genotype-replicate; any complete contrast pair; any numeric `r_g`; any multi-hazard-arm result; any mutation run. No fitness, selection, optimum, or ESS claim exists in any Stage 7 artifact, including this one.

**Authorisation:** this document registers decisions only. It authorises no execution. Implementation code may be written after this commit, but the implementation, runner, tests, output schema, reducer, and analysis script must be frozen **together** with a pre-execution manifest (`df7b1f5`/`e2f580b`/`27f5700` precedent) at `results/stage7b2-repair/pre-execution-manifest.json`, committed before any retained run, and only after the §6 feasibility gate has passed. Mutation remains unauthorised in every form.

## 1. Registered reading of the retained outcome

The Stage 7B2 outcome stands exactly as classified by its source-frozen reducer: pair-contrast class `DEGENERATE_REPLICATION` (0 complete pairs of 32; registered minimum 16) alongside `BOTH_SUBCRITICAL` (each genotype `L(0) ≤ 1` in all 32 replicates). Both classes are legitimate registered results and are not reopened, reinterpreted, or relabelled here. The retained artifacts are immutable. What this document repairs is the **registration**, not the outcome.

## 2. Binding diagnosis

Recorded as design input, derived exclusively from the retained telemetry above and the frozen cost constants:

- **D1 — Admission was the sole failure stage.** Every one of the 93,862 failed DIVIDE attempts failed at the vacancy-reservation stage (`no_vacancy_attempts`); child-memory reservation never failed; the layer-1 `BUFFER_OVERFLOW` guard never fired in any replicate (per-replicate maximum buffered occupancy ≤ 3 packets against depth 64). Execution integrity was perfect: all ledgers closed at every checkpoint of every replicate; the reducer's recomputation was bit-exact.
- **D2 — Realised recruitment equalled the vacancy supply.** Census saturated in every replicate: all 32 end at the full census of 12 (2,324 ever-alive − 1,940 hazard deaths = 384 = 12×32), and the aggregate identity closes exactly — 2,132 admitted births = 1,940 hazard deaths + 384 alive at window end − 192 founders. Once saturated, a completed bout admits only when hazard opens a vacancy; admission is the bottleneck, exactly as the Blocker F decomposition anticipated.
- **D3 — Attempt pressure is packet-limited, vacancy supply is hazard-limited.** Attempts averaged 95,994/32/600 ≈ 5 per tick because each active member runs at most one reproductive cycle per tick and packets arrive at the frozen `REGISTERED_PACKET_RATE = 5`; vacancy supply at saturation is `N·h = 12/120 = 0.1` per tick. Per-attempt win rate: 2.22%.
- **D4 — Establishment per newborn was rare.** Of 2,132 admitted births, 186 ever reproduced (8.7%). Cohort-level `L(0)` — the expected establishments per newborn — therefore sat two orders of magnitude below the supercritical threshold 1 in every replicate and genotype.
- **D5 — Structural guarantee, not biological finding.** With a hard census cap reached almost immediately, non-displacing admission, and the binding first-reproduction establishment rule, cohort supercriticality requires lineage-expansion headroom that the registered ecology does not provide beyond its single initial doubling (6 founders, capacity 12). Under D1–D4, `BOTH_SUBCRITICAL` and zero complete pairs were structurally guaranteed for **any** allocation pair at this ecology. The degenerate outcome is a replication-feasibility defect of the registered design; it is not an observed allocation effect, nor evidence of the absence of one, and must never be cited as either.
- **D6 — Methodological root cause.** The 7B2 §2 calibration precondition demanded only "at least one offspring first-reproduction event" and "one binding admission" from shakedown, while its own §5 required both genotypes supercritical in ≥16 of 32 replicates for any contrast. The precondition was not derived from the decision rule. **Registered repair principle:** every future confirmatory registration's implementation-window gate must be derived from the statistical preconditions of its own decision rule. This principle applies to this document's own §6.

## 3. Registered repair decisions

| Parameter | Superseded value | Registered value | Registration rationale |
|---|---|---|---|
| Census capacity `N` | 12 | **48** | Vacancy supply at saturation scales ∝ `N·h` (48/120 = 0.4/tick) while attempt supply stays packet-limited at ≤ 5/tick, raising the per-attempt win-rate ceiling ≈ 4× (≈ 8%). Expansion headroom: 42 initial vacancies ≈ three doublings before saturation, so early cohorts can establish without death competition — the structural ingredient D5 found missing. |
| Packet energy `E` | 300 | **900** | Required by D2/D3 arithmetic so both arms stay somatically positive at `N = 48` (§4 table). Chosen from frozen cost constants only; the observed demographic asymmetry (ever-alive 1706 vs 618) independently motivates protecting the thin-somatic-share arm. |
| Window `W` | 600 | **1200** | Right-censoring precision knob (unchanged role). Ten expected founder lifetimes at `h = 1/120`; room for the expansion phase plus continued late-window establishment (observed establishments as late as tick 592 of 600 show activity is not founder-bound). |
| Buffer depth `d` | 64 | **64 (unchanged)** | Engineering bound; layers 1–2 of 7B1 §4.1 remain armed; larger consumer pools can only lower occupancy; any trigger classifies a run `INVALID_IMPLEMENTATION`. |
| Shared memory pool | 65,536 B | **65,536 B (unchanged)** | Upper bound on obligation: `N·(working 64 B + gestation 64 B) + corpse_ttl·128 B ≤ 48·256 B ≈ 12 KB ≪ 65,536 B`. |
| Seed table | `20260822 + i` | **`20261822 + i`, `i ∈ {0,…,31}`** | Deterministic offset (+1000) fixed before any run at this ecology, giving streams disjoint from the 7B2 table; no outcome-based selection of seeds is possible or permitted. |
| Replicates `k`, minimum pairs | 32 / 16 | **32 / 16 (carried)** | Unchanged; the repair targets pair *feasibility*, not the evidential floor. |

Carried verbatim from `stage-7b2-preregistration.md`, unchanged and restated as binding: the two genotypes `(102,128,255)`, `(204,128,255)`; founders 3 per genotype, age 0, `S=100`, `R=0`; single hazard arm `h = 1/120` per live member per tick; corpse TTL 2; `Δr_min = 1/100`; solver resolution `ρ_r = 1/256`; the §3 estimators, §4 solver contract, and §5 decision rule (all outcome classes and thresholds, applied exactly once by a source-frozen reducer); §6 calibration/confirmatory separation; §7 standing-rules compliance; mutation disabled with structural zero-draw M stage.

## 4. Disclosed somatic-economy arithmetic for `(N, E)`

Frozen constants: failed capture charges 10 `S` (`READ_EMPTY`); income split `(1−A/D)·E` to `S`; each active member cycles once per tick; capture succeeds iff a packet is buffered (supply `r = 5` shared). Mean per-member somatic balance per tick at full activity, ordinary upkeep excluded (it worsens both rows equally):

| Arm | `S` income/tick = `(r/N)(1−A/D)E` | Expected charge/tick = `(1−r/N)·10` | Margin/tick |
|---|---|---|---|
| A=102 (share 153/255) | `(5/48)·540 = 56.25` | `430/48 ≈ 8.96` | `+2270/48 ≈ +47.29` |
| A=204 (share 51/255) | `(5/48)·180 = 18.75` | `430/48 ≈ 8.96` | `+470/48 ≈ +9.79` |

Counterfactual check: at `E = 300`, `N = 48`, the A=204 margin is `(300 − 430)/48 < 0` — mass stalling of the thin arm would be guaranteed, which is why energy must rise with `N`. These are population-mean balances over the whole window, not per-organism guarantees; stochastic viability is asserted empirically by §6, never by this table. Reproductive-side affordability is comfortable at both arms (`R` income per capture 360 and 720 against prepaid `C_R ≈ 11` plus gestation upkeep and committed `P`), and leftover `R` persists across discarded bouts.

## 5. Registered question (form unchanged, ecology revised)

Under the §3 ecology with exogenous phenotype-blind hazard `h = 1/120` and binding vacancy admission, do the two carried allocation strategies differ in per-genotype invasion growth `r_g` (7B1 §6.1 endpoint; 7B2 §3–§4 estimators and solver) by at least `Δr_min = 1/100` across `k = 32` seeded replicates, with the §5 rule applied exactly once? The estimand remains the per-genotype replicate distribution of certified rational brackets `[r_lo, r_hi]`. No optimum, ESS, background-invariant causal effect of α, or external-validation claim about the textbook mortality–allocation mechanism is registered, tested, or permitted. Single-hazard design: any hazard-related language about outcomes is restricted to combined mortality–turnover labelling. Vacancy capture remains part of the primary estimand (Blocker F), decomposed against shadow counters.

## 6. Pre-freeze feasibility gate (binding)

Derived from the carried §5 rule's own statistical precondition (≥16 simultaneous both-genotype-superreplicate outcomes), per D6. During the implementation window and before any freeze commit:

1. Run unretained exploratory shakedowns at the exact §3 configuration on **at least 24 distinct hazard seeds drawn outside the registered confirmatory table** `{20261822,…,20261853}`.
2. Gate conditions, all mandatory:
   - **G1** each genotype is supercritical (`L(0) > 1`) individually in at least two-thirds of shakedown replicates;
   - **G2** both genotypes are simultaneously supercritical in at least two-thirds of shakedown replicates (projecting ≥16/32 complete-pair availability);
   - **G3** zero `BUFFER_OVERFLOW` triggers and zero `INVALID_IMPLEMENTATION` classifications;
   - **G4** every ledger checkpoint closes in every shakedown run.
3. If any condition fails, **no freeze may be committed**: the correct action is a further superseding preregistration revising the §3 decisions with a new diagnosis. Registering another infeasible confirmatory suite is prohibited.
4. Shakedown executions produce no retained artifact (7B1/7B2 disclosed precedent). A factual summary of the gate outcome (seed list used, per-condition pass counts) must be recorded in the freeze commit's manifest directory notes, disclosing that the confirmatory table itself remained untouched until the single retained run.

## 7. Freeze-before-execution and authorised execution class (for the successor session)

1. Implementation window opens on commit of this document; no retained execution occurs during it.
2. After §6 passes: freeze implementation, runner, tests, schema, reducer, and analysis script **together**, with SHA-256 + byte size per file at `results/stage7b2-repair/pre-execution-manifest.json`, committed before any retained run. Frozen 7B1 transaction mechanics (`stage7b1_mechanics.py`, SHA-256 `61572690…` as disclosed at the 7B2 freeze) are expected to be reused byte-identically behind a thin configuration layer; any file whose hash changes relative to the 7B2 manifest must be listed with the change justified against this document.
3. The authorised execution class is then one seeded, mutation-disabled confirmatory suite: `k = 32` replicate populations under §3, reduced exactly once under the carried §5 rule, raw output retained under `results/stage7b2-repair/`.
4. PASS criterion: every ledger closes at every registered checkpoint in every replicate; every solver certification is valid; the carried §5 rule is applied exactly once and its outcome recorded. Any failure retains the run, classifies it, and triggers repair — archiving, never deletion.

## 8. Standing-rules compliance and falsification-gate mapping

Exact `Fraction` arithmetic in every ledger; solver enclosure arithmetic analysis-side only. Telemetry labels, ancestry IDs, and genotype hashes are never read by mechanics. Gates engaged: conservation (all ledgers close at every checkpoint of every replicate); packet-sink (7B1 §3 retirement equations hold; unread budgets intact at window end); vacancy (realised recruitment decomposed into intrinsic bout completion and ecological capture via side-effect-free shadow counters); endpoint (only the carried `r_g` distribution is primary; mediators stay mediators; sterile persistence earns nothing); trait-isolation (genotypes differ only in `A`); trait-resolution (two-point contrast only; interior-lattice claims prohibited); ecology (single hazard level ⇒ combined-response labelling; architecture §9.5 items 1–5 remain unrun); storage (founder inputs logged; exact death disposal; hoarding disclosed as endpoint-neutral); plasticity-scope (fixed-`(A,T)` results say nothing about plasticity); age-state and somatic-state reporting carried; no historical carry-over.

## 9. Not authorised by this document

Any execution before the §6 gate passes and the §7 freeze is committed; mutation at any locus; open genomes; additional hazard levels, the directional `α*(h)` prediction, or factorial separation studies; endpoint substitution, `Δr_min` retuning, threshold changes, or seed replacement — now or after the repaired suite runs; optimum, ESS, or background-invariant causal claims; interior-lattice or extrapolated landscape claims; plasticity interpretations; citing the retained 7B2 subcriticality as an allocation effect or as evidence of the absence of one; reuse of pre-Stage-7 quantities; modification of retained artifacts or superseded documents; history rewrites.
