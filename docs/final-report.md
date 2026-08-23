# Substrate — Final Report

*Programme summary, Stages 1 → 8. Date: 2026-08-23. Status: closure
report under review direction (d) (debate Round 4 verdict,
`docs/stage-8-debate-log.md`). Supersedes `docs/project-report.md`
(2026-07-30, Stages 1–6), which remains retained unchanged. Owner
redirection supersedes this closure without prejudice.*

---

## 1. The question and the thesis

The programme asked whether a deliberately minimal digital ecology —
conserved packets, serial replication, one allocation decision — can
support a measurable causal chain from extrinsic mortality to
allocation strategy. Its governing thesis, learned by falsification:
**conservation is not an ecology** (`docs/public-technical-essay.md`).
A model can close every ledger perfectly and still implement the wrong
question. The final arc adds the second half: **verified channels are
not selection.** A mechanism can be real, exact, and demographically
expressive, and evolution through it still fail to clear a
preregistered effect floor.

## 2. The method, demonstrated

Every data-producing question after Stage 6 ran under the same
discipline:

1. **Registration before implementation**: question, arms, seed tables,
   window, decision rule, and failure interpretation committed before
   any mechanics exist.
2. **Feasibility gate on a disposable shakedown table**, distinct from
   every confirmatory table, before any retained execution.
3. **Freeze before execution**: implementation, tests, schemas,
   reducers, and gate tooling pinned by SHA-256 + byte size in a
   pre-execution manifest; verified zero-drift immediately before
   reduction.
4. **One authorised execution**, reduced exactly once by the
   source-frozen reducer (which refuses double reduction by
   construction).
5. **Superseding registrations, never retuning**: anything learned the
   hard way becomes a new document that says exactly what changed;
   falsified designs are archived under `failed-designs/`, never
   deleted.

## 3. The arc

### Stages 1–6 — building an ecology worth trusting

Instruction-set VM, energy model, reserve accounting, packet supply.
The decisive failures were ecological, not arithmetic: private cloned
packets made competition impossible while conserving everything; one
wallet coupled fecundity and viability; income had no route to fitness
without a timing/recruitment channel. Full record:
`docs/project-report.md` (retained). Four defective or invalid designs
from this era are archived (`failed-designs/2026-07-28-*`).

### Stage 7 / 7B — does the allocation channel reach population level?

Splitting positive extraction income between somatic reserve `S` and
reproductive reserve `R` by lifetime-fixed `α = A/D` was carried
through six registered generations:

- **7B0 PASS** (all ten gates, independently audited): intervening on
  `A` splits identical income exactly (`Y_R = (A/D)Y`), isolates direct
  debits, produces the registered funding/endowment differences.
- **7B1 PASS**: transaction-safe child publication under fault
  injection; vacancy-capture estimand decided; shadow counters proven
  side-effect-free.
- **7B2 confirmatory**: retained run returned
  `DEGENERATE_REPLICATION` + `BOTH_SUBCRITICAL` (0 complete pairs) —
  honest failure, repair mandated.
- **Three repair attempts, three gate-caught falsifications**: raw-
  fecundity numerator (gate FAILED 0/24), two-factor endpoint
  coefficients (FAILED, ceiling confirmed), denominator identities
  (FAILED one layer out — winner-take-most exclusion anti-correlation
  diagnosed). Each archived; each diagnosis carried forward.
- **Signed bracket (final repair)**: complete the estimand rather than
  substitute it — full-real-line Lotka certification so every
  measurable arm emits a signed bracket. Gate PASSED 24/24 with
  bit-exact estimator regression identity → freeze `7d21153` → single
  retained execution: **32/32 replicates COMPLETE, class
  `NO_ESTABLISHED_CONTRAST`** (median paired difference −1/128 against
  floor Δr_min = 1/100; sign split 21/9/2, descriptive). Rung-1 bound:
  cross-sectional slope ≈ 8×10⁻⁵ allocation units per unit exposure
  contrast.

### Stage 8 — dedicated-locus evolution (rung 2)

First genuine evolution: kernel flips allocation ±1..±4 lattice steps
per birth with p_μ = 1/2 (clamped), T/D frozen, W = 2400, k = 24 paired
replicates against a byte-frozen mutation-off reference at identical
seeds.

- Original registration → implementation window → §7 feasibility gate
  **FAILED G2 only**: tooling expected `W+1` closure entries, the
  frozen stack deterministically writes `W+2`. Diagnosed against frozen
  source, archived (`failed-designs/stage8-paired-gate-g2-checkpoint-
  bookkeeping/`), repaired by superseding registration #3 changing ONLY
  that operationalization.
- Corrected gate PASSED (12/12 pairs; bit-exact stream replay) →
  freeze `f1e6880` (30 files hash-pinned; zero drift re-verified twice)
  → THE ONE retained execution (14:55:41–17:41 UTC, exit 0):
  **48/48 runs COMPLETE, zero extinctions** (n_live = 48 everywhere),
  Arm M 23,933 mutation decisions / 35,981 kernel draws / 0 problems;
  Arm R0 zero-draw kernel absence asserted every run.
- Reduced exactly once: **k_eff = 24/24; movers-up 9, movers-down 6,
  inside-floor 9, versus concordance 18 ⇒ `NO_ESTABLISHED_DIRECTION`**
  (`leakage_pairs` = 0; ancestry-plurality monitor clean 24/24). Median
  |D_i| = 437/24480 (= 4.6/255) sat at floor scale; signs split 13/11/0.
  Rule size is dispersion-free: Σ_{k≥18}C(24,k)/2²⁴ = 190051/16777216,
  0.01133 one-sided / 0.02266 two-sided, recomputed exactly post hoc.
  Licensed bound: no redistribution beyond ±4/255 per pair in either
  direction at this ecology/kernel/window. Measured dispersion left as
  prior: population sd(D) = 0.022377 ᾱ-units ≈ 5.71/255.

## 4. Findings

1. **The allocation channel is real at both levels.** Exact splits from
   identical income; ~2.27× reproductive working reserve for HIGH at
   first bout; certified L(0) up to ≈ 1.5; genotype-level status
   asymmetries (23 vs 11 supercritical replicates). Not a bookkeeping
   fiction — it reaches demography.
2. **Its evolutionary expression did not clear preregistered floors at
   the tested ecologies — twice, at two endpoint families.** Rung 1
   (invasion-growth brackets) and rung 2 (paired terminal-allocation
   direction under active mutation) both closed as registered nulls
   with quantitative bounds.
3. **Coupled-vacancy structure fights paired designs at saturation:**
   arms drawing from one vacancy pool are competitors, not independent
   replicates; joint growth is the rare tail. Any resumption should
   de-saturate or measure within-genotype.
4. **Individual-level effects need population-level power:** a large,
   exact individual contrast (2.27× endowment) is plausibly real yet
   below what 32–48-replicate windows resolve across committed floors.
5. **The discipline worked.** Eight archived falsifications (four
   early-era designs, three infeasible 7B repairs, one gate defect),
   two registered nulls, every confirmatory table executed exactly
   once, zero compromised inferences, zero retunes after data. That is
   the system operating as designed, and it is itself a finding.

## 5. Scope limits (what this programme does NOT claim)

No fitness, selection, optimum, ESS, causal-hazard-gradient, external-
validation, open-genome, other-ecology, or trajectory/frequency claims
are licensed anywhere in the retained record. Unattempted instruments
(frequency trajectories, de-saturated ecologies, open populations)
remain untested; whoever revives them inherits exact measured priors
(sd(D) ≈ 5.71/255 paired at W = 2400; slope bound ≈ 8×10⁻⁵; the 2.27×
individual endowment contrast) and must register independently of the
existing nulls.

## 6. Primary artifacts

| Artifact | Location |
|---|---|
| Essay (public-facing) | `docs/public-technical-essay.md` |
| Stage 1–6 report (retained) | `docs/project-report.md` |
| Stage 8 review/synthesis | `docs/stage-8-programme-review.md` |
| Debate log (Rounds 1–4) | `docs/stage-8-debate-log.md` |
| Stage 8 execution note | `docs/stage-8-paired-execution-note.md` |
| Stage 8 raw artifact | `results/stage8-alpha-evolution-paired/confirmatory-paired-20310529.json` (sha256 3eb06ecc…) |
| Stage 8 reduced artifact | `…/confirmatory-paired-20310529-reduced.json` (sha256 bdb14fbe…) |
| Stage 8 freeze manifest | `…/pre-execution-manifest.json` |
| Stage 7B signed-bracket record | `results/stage7b-signed-bracket/`; note `docs/stage-7b-signed-bracket-execution-note.md` (raw sha256 6268a3da…) |
| Failed-designs archive | `failed-designs/` (eight entries, immutable) |

Repository: <https://github.com/Substrate-Life/substrate-life>

## 7. Closure

The registered statement space of this architecture is complete: the
channel exists; evolution through it did not establish redistribution
beyond the recorded bounds at the tested ecologies; the bounds, the
dispersions, and the method are published and reproducible. The
programme closes here under direction (d). Any revival is a new
registration.
