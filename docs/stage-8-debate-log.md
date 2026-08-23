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

---

# Round 3 — pre-freeze debate on the GATE-REPAIR design (registration #3): proceed through corrected gate → freeze → the one retained execution?

*Conducted 2026-08-23 ≈ 11:35–11:55 UTC, after the implementation window
of `docs/stage-8-alpha-evolution-gate-repair-preregistration.md`
completed (`8392963`) and while the single authorised corrected-gate
shakedown re-execution (registration §4, table `20421301 + j`) was
running in this session. Adoption of any verdict is deferred until the
gate result exists; nothing below reads gate endpoint data. **Delegation
disclosure:** the delegation tooling was again unavailable in this
session (Round 1's subagent transcripts remain archived under
`cache/delegation/live/deleg_44629ee8/`), so per standing orders the
three roles were argued and cross-examined by the parent agent against
repo facts, with every check re-verified against source or artifacts
rather than asserted.*

**Proposition:** accept the checkpoint-bookkeeping repair as sufficient
and proceed — corrected-gate PASS → freeze commit → ONE retained
confirmatory suite (`20310529 + i`, 48 runs) → one-shot reduction.

## Advocate's case

1. **The failure was bookkeeping, not machinery.** Across all 24 arms of
   the first full-window execution ever run in this programme
   (12 pairs × {M, R0}, `W = 2400`, wall ≈ 118 min): zero
   `BUFFER_OVERFLOW`, zero `INVALID_IMPLEMENTATION`. The byte-frozen
   assertion machinery verifies live ledgers after *every* operation and
   rescans full immutable history at every tick-complete checkpoint;
   had the registered substance of G2 been violated anywhere, the run
   would have raised. The wrong quantity was a *derived expectation*
   (`W + 1` from a docstring-derived schema parenthetical), now
   superseded by a strictly stronger pin: count `W + 2` AND head labels
   `['initial', 'initial', 'tick_complete:0']` AND tail label
   `tick_complete:<W−1>` on every COMPLETE arm.
2. **Decision-path fields are multiply validated end-to-end.** (a)
   Corrected G2 pins closure semantics on every COMPLETE arm; (b)
   G3 re-executes one full Arm M replicate and verifies event digest,
   admitted births, draw totals, and kernel chain bit-exactly against
   the shakedown twin, plus documented-stream replay; (c)
   `test_stage8_paired.py` drives the real population + measurement
   layer at plumbing scale (`W = 120`) on both arms; (d) the
   source-frozen reducer refuses ≥ 15 classes of malformed input
   pre-rule (protocol echo, table membership, double reduction,
   histogram↔endpoint inconsistency, kernel-evidence reconciliation,
   seed identity), so no silent inconsistency reaches the §5 rule.
3. **Shakedown reuse is uncontaminated.** Verified from the archived
   first-run summary: it emitted only condition pass/fail facts,
   complete-pair counts, threshold arithmetic, and replay identity
   evidence — no endpoint values, no direction information, nothing
   readable as an outcome statistic (the factual-context block did not
   exist yet). No frozen quantity can have been tuned.
4. **Cost discipline.** 48 runs ≈ 4 h at two workers buys the registered
   one-shot answer either way — expected-null closure of direction (c)
   at ~20× finer longitudinal resolution than the closed cross-sectional
   bound, or discovery.

## Adversarial reviewer's attacks

- **A1 (strongest) — "one proven miss implies unknown misses":** the
  `W + 1 → W + 2` episode proves the measurement layer carried
  docstring-derived expectations never validated against a full-window
  execution. Any *other* unvalidated derived field detonates only AFTER
  the retained run — burning the one-shot confirmatory table into a
  refused reduction and forcing a further repair registration. A prudent
  agent audits every recorded field at full window BEFORE spending the
  table.
- **Advocate's response:** the audit was performed, field class by field
  class. Exactly two recorded quantities are W-derived *counts*:
  `ticks_completed` (= W, trivially) and `tick_checkpoints`
  (closure-history length — the field that failed, now pinned with
  label substrates). The trajectory grid is a module constant asserted
  to be exactly the registered 20 points (`CHECKPOINT_TICKS`,
  test-pinned). Every remaining decision-path field is either
  W-independent arithmetic on a recorded object (histogram ↔ mean
  consistency), replay-verified at full W by G3 (digests, births, draw
  chain), or exercised end-to-end by the W = 120 plumbing tests whose
  code paths are identical at W = 2400. Residual risk is therefore NOT
  zero — disclosed as such — but the adversary's proposed alternative
  (a further full-window exploratory audit suite) is authorised by NO
  registration and would itself consume exploratory executions outside
  the standing rules; and the reducer/§7(5) backstop retains, archives,
  and classifies rather than silently misclassifies if anything does
  surface.
- **A2 — shakedown reuse contamination:** refuted on the archived
  artifacts (advocate point 3).
- **A3 — "expected-null prior makes the run foregone":** registering the
  expected-null up front IS the O2-repaired honest design; discovery
  remains live at the registered thresholds; declining to execute leaves
  direction (c) unclosed while burning nothing — pure loss under the
  programme's advance mandate.

## Method auditor's findings

1. **Freezing order intact for the rerun:** registration #3 was
   committed (`06e03a1`, 11:21:55 UTC) before the second shakedown
   execution launched (~11:33 UTC); the rerun is the single execution
   §4 authorises on `20421301 + j`.
2. **Zero retained artifacts:** `results/stage8-alpha-evolution-paired`
   absent from the tree at session start (verified); shakedown output is
   stdout-only under `/tmp`.
3. **Suite green at `8392963`:** 423 tests OK (4 pre-existing skips),
   including new pins that the superseded `W + 1` count FAILS corrected
   G2, both closure-label pins, factual-context aggregates, and the
   freeze-manifest builder's refusal/happy-path/digest matrix.
4. **Duplicate-session handoff disclosed:** `06e03a1`'s message described
   both-gate fixes whose files were still unstaged when that session
   exited; the mismatch and its completion are recorded in the `8392963`
   commit message per house precedent.
5. **Rule hygiene unchanged:** telemetry labels unread by mechanics;
   kernel draws integer-only outside ledgers; exact Fractions in every
   ledger; frozen stack imported byte-identically.

## Verdict

**ADVOCATE SURVIVES — proceed: corrected-gate PASS → freeze commit →
the ONE retained confirmatory execution → one-shot reduction, exactly as
registered.** The adversary's A1 survives in weakened form as a
disclosed residual risk with obligations, not retunes:

1. **A1 obligation (new):** the freeze-commit note must state the
   decision-path-field validation substrate (corrected G2 labels, G3
   bit-exact re-execution, W = 120 plumbing coverage, ≥15 pre-rule
   reducer refusals) and disclose the nonzero residual risk for
   W-derived counts explicitly.
2. **Carried obligations:** Round 2's A2/A3 stand — the execution note
   must report the empirical null spread of `D_i` descriptively and read
   the co-reported leakage monitor (`leakage_pairs`, ancestry-plurality)
   whatever the outcome class.

If the corrected gate FAILS: no freeze; further superseding
registration with diagnosis archived under `failed-designs/`; this
verdict lapses. Frozen quantities remain frozen.


---

# Round 4 — post-null direction debate: what does the follow-on registration pursue?

*Date: 2026-08-23 (session 7), conducted after the ONE retained
execution reduced exactly once to `NO_ESTABLISHED_DIRECTION`
(commit `9db2f3b`). DISCLOSED: the delegation tool used in Round 1 was
unavailable again this session (no `delegate_task` in the session
toolset), so as in Rounds 2–3 the three roles were argued and
cross-examined by the parent agent against repo facts with exact
Fraction arithmetic; transcripts therefore live in this file and the
commit message, not under `cache/delegation/`.*

## The question

Stage 8 rung 2 is closed as a registered bounded negative. The next
registration alone decides the follow-on. Candidates from the programme
review: (a) ecology/power reframing of the weak contrast; (b)-family
recruitment/establishment endpoints (mediator-caveat precondition);
a frequency-trajectory instrument (unrun by any stage); (d) programme
close-out (essay extension + final report). Which should the next
registration pursue?

## Advocate's position (design: proceed to close-out, direction (d))

1. **The review's own condition for (d)'s value has been met.** The
   review recommended (c) partly because "a well-powered rung-2 result
   (either sign) plus the existing rung-1 null makes direction (d) —
   whichever session it happens — a far stronger essay." That result now
   exists: k = 24 paired replicates at W = 2400, zero extinctions,
   23,933 kernel events on Arm M, closed by the frozen rule.
2. **(d)'s stated risk is void.** The only risk recorded against (d)
   was that it "forecloses (a)–(c); the essay would describe a ladder
   whose second rung was never attempted." The second rung WAS
   attempted and closed with a measured bound. Foreclosure now costs
   the project nothing it has not already banked.
3. **Marginal values collapsed for the alternatives.** (a) has no
   effect-size target to power for — the null supplies an upper bound,
   not a candidate β; powering for arbitrary small effects is
   unbounded cost for unbounded ambiguity. (b) still carries its
   permanent-mediator-caveat precondition (architecture §9.4 / 7B1 §6.1
   demonstration must precede any endpoint promotion). The trajectory
   instrument would be a fourth new-code surface adopted AFTER two
   nulls at two endpoint families, with no candidate effect size and
   the review's own warning that an underpowered frequency null is
   ambiguous between "no selection" and "selection too weak".
4. **The answerable questions are answered.** Within the fixed level-2
   statement space, the ladder reads: channel exists (7B0/7B1 PASS);
   restricted architecture evolves through it beyond ±4/255 per pair at
   this ecology — NOT ESTABLISHED (Stage 8). The scope sentence forbids
   exactly the level-3+ claims (external validation, optimum, ESS) that
   the trajectory instrument would nominally chase; no registration can
   license them inside this architecture.
5. **Close-out transfers knowledge instead of burying it** if — and the
   advocate accepts this as binding — the essay records the unattempted
   trajectory instrument as an explicit scope limit TOGETHER WITH the
   measured dispersion prior sd(D) ≈ 5.71/255 at W = 2400, so any
   future resumption inherits quantified, desk-computable power
   arithmetic rather than a bare "we stopped".

## Adversarial reviewer's objections (checked against repo facts)

A1. **"Stopping on a null is results-shopping in reverse."** A
    discipline that ends when answers disappoint optimises narrative,
    not knowledge; the motivating question (does extrinsic mortality
    select allocation speed?) remains unanswered, and the trajectory
    instrument is qualitatively different evidence (temporal
    integration over ~10⁴ births vs a terminal endpoint). — CHECKED:
    partially survives as an obligation, fails as an override. The
    motivating question lives outside the licensable statement space
    (scope sentence, verbatim in the execution note §6); Stage 8's
    design WAS the registered operationalization of rung 2, selected
    before any confirmatory data existed (f783133/f753894/f1e6880 all
    precede first retained observation). Switching instruments after
    seeing the null would need independent justification, and none
    exists beyond preference for a different answer — precisely the
    fork the preregistration discipline exists to block. What survives:
    the essay must state the non-answer plainly, and the closure must
    be framed as completion of the registered statement space, not
    termination of the science.
A2. **"Was the test even powered as planned? Observed sd(D) = 5.71/255
    exceeds the Round-2 proxy band σ ≈ 1.6–2.0/255 — maybe realised
    power diverged from the registered power model."** — CHECKED:
    refuted as a defect, confirmed as a fact already discharged. The
    §5 rule is count-based: size is dispersion-free at
    Σ_{k≥18}C(24,k)/2²⁴ = 190051/16777216 ≈ 0.01133 one-sided,
    0.02266 two-sided (recomputed exactly this session), whatever the
    spread. Wider dispersion raises per-pair floor-crossing
    probability (floor fixed at 4/255), so magnitude scarcity was NOT
    the failure mode — sign balance was (13/11). Power for a true
    positive effect requires per-pair same-side floor-crossing ≳ 0.75;
    with no candidate β post-null, "underpowered" is not demonstrable
    and retuning is forbidden anyway (§10).
A3. **"The identical birth totals across arms (23,933 = 23,933) look
    like an implementation bug — are arms actually different?"** —
    CHECKED: explained by construction, and independently pinned.
    Hazard is exogenous and phenotype-blind; both arms at a seed share
    the demographic skeleton, so equal admitted-birth totals at equal
    seeds are the expected determinism signature, not contamination.
    Arm difference is pinned elsewhere and audited every run: Arm M
    carries 23,933 decision records / 35,981 draws / problems = 0;
    Arm R0 has zero decisions, zero draws, empty chain, telemetry
    passing (`arm_contrast_is_exactly_the_kernel: true` in the raw
    integrity block), and terminal distinct-A M 9..17 vs R0 1..2.

## Method auditor's findings

1. **Freeze-before-execution held:** freeze commit `f1e6880` at
   14:54:44 UTC precedes runner launch at 14:55:41 UTC; manifest pins
   verified zero-drift twice this session (pre-launch, pre-reduction).
2. **One-shot reduction held:** raw artifact `decision` field is flipped
   by the reducer's write path; a second reduction refuses
   (`PENDING_REDUCTION` check, covered by the reducer test matrix);
   artifacts committed once at `9db2f3b` and untouched since.
3. **Suite green:** 423 tests OK (4 skipped) this session, including
   the fault matrix re-parameterised onto the kernel subclass.
4. **Round hygiene:** telemetry labels unread by mechanics; exact
   Fractions throughout ledgers and the D_i table; no fitness,
   selection, ESS, or external-validation claim appears in the
   execution note beyond the fixed scope sentence.
5. **Disclosure completeness:** wall-clock overrun, delegation
   unavailability, and the proxy-band underestimate are all recorded;
   nothing was retuned, rerun, or added to the closed line.

## Verdict

**ADVOCATE SURVIVES — the next registration pursues direction (d):
programme close-out.** Binding obligations carried forward:

1. The essay extension (`docs/public-technical-essay.md`) must present
   BOTH registered nulls with their bounds (rung-1 cross-sectional
   bound ≈ 8×10⁻⁵ slope units; rung-2 paired redistribution bound
   ±4/255 per pair, best side 9/24, median |D| = 4.6/255, sd(D) ≈
   5.71/255), the three falsified repairs caught by gates plus the G2
   bookkeeping repair lineage, and the gate→freeze→execute→reduce
   discipline itself as the demonstrated method.
2. The essay must state explicitly what was NOT tested — trajectory/
   frequency instruments, other ecologies, open populations, level-3+
   claims — as scope limits carrying the measured dispersion prior for
   any future resumption, not as promises.
3. A final report summarises the programme arc Stages 1 → 8 with the
   failed-designs lineage cited, never deleted.
4. No further evolutionary execution is authorised on any closed line;
   a future trajectory-style registration, if ever revived, must be a
   superseding registration justified independently of this null.

If the owner redirects, the standing orders' escalation path applies
(owner input supersedes; this verdict then lapses without prejudice).
