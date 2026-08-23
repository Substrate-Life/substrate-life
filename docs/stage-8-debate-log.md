# Stage 8 Debate Log — pre-freeze adversarial review of the alpha-evolution design

*Date: 2026-08-23. Format: two independent subagents (ADVOCATE,
ADVERSARIAL REVIEWER) briefed on the full repo record; verdict by the
parent agent. Full transcripts:
`cache/delegation/live/deleg_44629ee8/task-{0,1}.log`.*

## The question

Should the registered Stage 8 design (`docs/stage-8-alpha-evolution-preregistration.md`,
commit `f783133`, implementation `f753894`) proceed to its feasibility
gate → freeze → single retained execution as registered?

## Advocate's strongest points (verified)

1. **Identifiability arithmetic:** founder set 3×102 + 3×204 gives
   α_ref = 153 exactly as the neutral barycentre; no N_e registration
   needed for a sign statistic.
2. **Supply sizing:** W=2400 ⇒ ≈960 births/replicate ⇒ ≈480 kernel
   events/replicate, ~11,500 suite-wide; floor 8/255 = 2× max kernel step
   so no single event can manufacture a classified mover.
3. **Rule hygiene:** Σ_{k≥18} C(24,k) = 190051 verified exactly;
   one-shot, source-frozen, split-concordance explicitly registered as
   `NO_ESTABLISHED_DIRECTION`.

## Adversary's objections (checked against repo facts)

- **O1 — the direction statistic is a founder-priority counter.**
  Founders sit ±51 lattice units from α_ref; mover floor is 8; the
  mutational cloud after 20 turnovers has SD ≈ √(20·1.875) ≈ 6.1 units.
  Documented winner-take-most exclusion at this exact ecology (cohorts
  like 479-vs-18; one arm supercritical in 21/24) means ᾱ_end ≈ winning
  founder value ± cloud — classification is decided by *which founder
  won*, and a `p_μ = 0` suite would produce nearly the same outcome
  distribution.
- **O2 — no H1 power; response shortfall ≥130×.** Crossing the floor in
  20 turnovers requires selection slope β ≈ 0.01–0.02 per A-unit; the
  closed signed-bracket line bounds the real β at ≲ 8×10⁻⁵ (median
  bracket difference 1/128 across the *entire* 102-unit founder gap).
  Mutation *supply* was sized; selection *response* never was — a
  category error.
- **O3 — the exchangeability axiom behind the 0.0113 bound is already
  contradicted by the project's own retained record:** 21/9 sign split
  (two-sided p ≈ 0.043) at this ecology implies true LOW-win probability
  ≈ 0.6–0.7, inflating the realistic P(classify toward-LOW) to ≈ 0.09–0.21
  vs the registered 0.0113 — and the likely "significant" branch is
  indistinguishable from the published founder bias.
- **No gate catches any of this:** G1 ("≥1 mutation event and ≥2 distinct
  A values") is satisfied by neutral drift alone; G2/G3 are plumbing.

## Verdict

**ADVERSARY WINS on O1+O2 jointly; execution as registered is blocked.**

Either exclusion completes (~90% of replicates historically) and the
founder lottery decides the classification — or it does not, and real
selection is 2–3 orders of magnitude too weak to move the terminal mean
across the floor. There is no third regime in which the registered
estimand measures evolution through the channel rather than the founder
priority lottery. The advocate's counter — that independent replicates
wash out stochastic priority effects — holds only under win-exchangeability,
which O3 shows the retained data already rejects (p ≈ 0.043). Proceeding
would spend the one authorized execution re-measuring, at k=24, a ~2:1
lottery skew already recorded at k=32, with a realistic ~20% chance of
registering "evolution established toward LOW" that a p_μ=0 control would
have produced identically.

The advocate's structural contributions survive: exact barycentre
arithmetic, honest null-tail computation *conditional on symmetry*, and
clean rule freezing. The defect is not the rule but the **estimand's
failure to decouple from founder priority**, plus the missing H1 sizing.

## Disposition (binding on subsequent sessions)

1. **Do NOT run the feasibility gate → freeze → retained execution chain
   on the design as registered.** The implementation window stays open;
   nothing executed is wasted (kernel tests and the additive layer carry
   forward byte-identically).
2. **Draft a superseding repair preregistration** addressing O1–O3. The
   minimal repair that preserves the registered investment: a **paired
   `p_μ = 0` reference arm at the same seeds** (identical hazard stream ⇒
   identical ecological skeleton ⇒ the founder lottery cancels by
   paired differencing), with the endpoint restated as the paired
   difference `Δᾱ_end(mutation-on) − Δᾱ_end(mutation-off)` and an H1
   power derivation *in α-units* replacing the supply-side rationale.
   Alternatives (within-lineage trajectory endpoint; de-saturated
   ecology) may be registered instead if the paired-power analysis
   rejects the reference-arm design.
3. All three documents' frozen thresholds are untouched; the repair is a
   superseding registration per §9, not a retune.

---

# Round 2 — pre-freeze adversarial review of the PAIRED repair design

*Date: 2026-08-23, before the §7 freeze of
`docs/stage-8-alpha-evolution-repair-preregistration.md`. Format note
(disclosed): the delegation tooling used for Round 1 (subagent transcripts
under `cache/delegation/live/deleg_44629ee8/`) is unavailable in this
session, so the three roles below were argued and cross-examined by the
parent agent against repo facts, with every load-bearing number computed
exactly (Fraction arithmetic, reproducible from the session log). The
section itself is the verbatim record. Nothing here retunes any frozen
quantity.*

## The question

Does the paired repair design (`a7f3866`) proceed to §7 gate → §8 freeze →
one retained execution as registered — specifically, does its neutral
reference (conditional symmetry of the paired difference
`D_i = ᾱ_end(M, s_i) − ᾱ_end(R0, s_i)` beyond floor 4/255) survive its
strongest attack, and is the floor's σ-anchoring sound?

## Advocate's strongest points (verified)

1. **The null-tail arithmetic is exact and floor-free.** Σ_{k≥18} C(24,k)
   = 190051; P(classify | fair signs) ≤ 190051/2²⁴ = 0.0113279 one-sided,
   0.0226558 two-sided — recomputed this session, matches §5 exactly.
   The bound depends only on sign fairness among eligible pairs, not on
   where the floor sits, so floor-placement error could touch power but
   never size.
2. **Pairing structurally cancels the founder lottery (O1's repair).**
   Both arms of a pair run the identical `hazard_seed` on machinery whose
   hazard derivation is unchanged; under the null the two arms share the
   identical demographic skeleton, so winner identity is common-mode and
   cancels in `D_i`. Verified: the R0 factory is the byte-frozen
   `Stage7B2Population` at identical configuration; the shared-prefix
   hazard-stream identity is test-enforced (`test_arms_share_hazard_stream_prefix`).
3. **Leakage is bounded and conservative.** A pair-flip requires an
   exclusion margin comparable to the mutational perturbation (units),
   while recorded exclusions at this ecology are decided by census margins
   orders of magnitude larger (479-vs-18 cohort record). A flipped pair
   contributes large |D_i| with sign fair to first order; even an
   all-flips scenario with fair flip signs yields splits — i.e.
   `NO_ESTABLISHED_DIRECTION`. Leakage biases toward the null, not toward
   false discovery, and the ancestry-plurality disagreement monitor is
   co-reported per pair by the reducer.
4. **H1 honesty is registered, not retrofitted:** §6 commits expected-null
   up front (β_min ≈ 4.4×10⁻⁴ realistic vs recorded cross-sectional bound
   ≈ 8×10⁻⁵); one-shot rule, source-frozen reducer, split ⇒ null.

## Adversarial reviewer's objections (checked against repo facts)

- **A1 — "the floor's ≥2σ claim double-counts arm independence."**
  Initial objection: the null paired-difference SD should be √2 × the
  single-arm cloud SD (two independent mutation clouds), putting floor
  4/255 at 1.41–1.77σ, not "≥2σ" (repair §3(ii)). **REFUTED on check:**
  under the registered null the two arms do NOT carry independent clouds —
  Arm R0 has no mutation site at all, so `ᾱ_end(R0)` is the shared
  demographic skeleton at founder values, and `D_i` *is* the single
  mutation-cloud mean deviation. The registered σ ≈ 1.6–2.0 therefore
  applies to `D_i` directly and 4/255 sits at 2σ–2.5σ as registered. The
  √2 inflation would require arm demographies to decouple — which is
  precisely the β ≠ 0 signal case, not noise. Objection withdrawn; the
  registration's arithmetic stands.
- **A2 — the σ ≈ 1.6–2.0 calibration is a fixed-genotype proxy.** The
  number originates in retained *mutation-free* dispersion (composition
  noise of ᾱ_end around founder values, 7B audit), while the relevant
  null quantity is the mutation-cloud mean deviation, which adds
  trunk-walk variance and has never been measured (no mutation-enabled
  run exists; the shakedown will be the first and may not resize
  anything). If the true null SD of `D_i` is several units rather than
  ~2, most null pairs cross the floor and the rule degenerates to the
  pure sign test — **size still bounded** (point 1: the combinatorial
  bound is floor-free), power story unchanged in direction. So: a real
  but non-binding weakness of the *rationale*, not of the rule.
- **A3 — flip-sign skew is unmeasured.** The registered size leans on
  near-fair signs; sensitivity (computed exactly): per-pair sign
  probability 0.6 ⇒ one-sided 0.0960; 0.65 ⇒ 0.2106; 0.70 ⇒ 0.3886;
  0.75 ⇒ 0.6074. If thin-margin seeds flip with side-dependent rates
  (e.g. LOW-founder wins systematically thinner, flips pushing D_i HIGH),
  the toward-HIGH branch could fire above nominal. No retained estimate
  of flip-rate skew exists. Mitigations: flips need margins ≲ units
  (rare per the lopsided-exclusion record), skew needs to be extreme
  (> ~0.65 with substantial flip mass) to threaten 0.0227, the split
  rule absorbs symmetric leakage, and the leakage monitor will expose
  exactly this signature. Residual risk accepted and disclosed.
- **A4 — gate blindness (recurrent).** G1–G4 audit plumbing and kernel
  integrity; none can detect A2/A3. True — but the repair's answer
  (pairing + floor-free size bound + monitor) addresses the class, and
  the gate was never claimed to test estimand validity.

## Method auditor's findings (preregistration discipline)

1. **Zero-run verification:** no `results/stage8-alpha-evolution*`
   artifact existed before this session's gate launch (directory listing
   checked at session start); the cancelled tables 20284617/20293311 and
   all five retired bases are test-enforced disjoint from the fresh
   tables; the chain was cancelled before any gate run — "retired
   unexecuted" is verified, not merely asserted.
2. **Freezing order intact:** floor 4/255, thresholds 16/18/24, kernel,
   and both seed tables were committed in `a7f3866` before any execution
   at those seeds; nothing executed has touched or can touch them (§10).
3. **Window-discipline slip (disclosed):** the §11 schema addendum was
   owed "before the gate runs"; the duplicate-session handoff
   (`d556358` → this session) left it unwritten, and it landed while the
   shakedown gate was already executing. It pins documentation of
   committed code only — no threshold, table, or behavior — so there is
   no integrity consequence, but the slip is recorded here per house
   honesty convention.
4. **Suite and sources:** 412 tests OK (4 skipped) including the
   completed paired-arm matrix (`ee5c7ca`); Stage 7B frozen stack reused
   byte-identically by import; sources hash-pinned in every artifact
   (`FROZEN_SOURCES`) and to be pinned by the pre-execution manifest.
5. **Rule hygiene:** the §5 rule is applied exactly once by the
   source-frozen reducer with pre-rule validation (protocol, table,
   seeds, double-reduction, histogram-endpoint consistency, per-arm
   kernel evidence); telemetry labels never read by mechanics; kernel
   draws integer-only outside the ledgers.

## Verdict

**ADVOCATE SURVIVES; the design proceeds to gate → freeze → the one
retained execution as registered.** The reviewer's strongest arithmetic
attack (A1) was refuted on inspection — the paired statistic under the
null is the single mutation-cloud mean, exactly as the registration's
floor rationale assumes. Two disclosed caveats travel with the design and
impose obligations, not retunes:

1. **A2 obligation:** the execution note must report the empirical null
   spread of `D_i` (descriptively, alongside the registered outcome)
   so the next registration knows whether the σ ≈ 1.6–2.0 proxy held.
2. **A3 obligation:** the execution note must read and report the
   co-reported leakage monitor (`leakage_pairs`) whatever the outcome
   class; a high flip count with skewed signs alongside an ESTABLISHED
   class must be flagged as candidate leakage-driven even though no
   retune or rerun is permitted.

Frozen quantities remain frozen: floor 4/255, thresholds 16/18/24, both
tables, both arm definitions. Any future change goes through a
superseding registration, never an edit.
