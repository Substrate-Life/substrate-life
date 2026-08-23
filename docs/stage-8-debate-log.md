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
