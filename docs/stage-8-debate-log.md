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

---

# Round 5 — 2026-08-23 (session 8): strengthened-contrast follow-on versus programme closure

## Question put to the round

The repair registration (`stage-8-alpha-evolution-repair-preregistration.md`
§6) left the follow-on decision explicitly to "the next registration",
reading whatever rung 2 registered: a strengthened-contrast ecology probe
(the review direction (a) form) versus programme closure (direction (d),
since discharged as documentation at `cd88d11`/`9059753`). Rung 2
registered `NO_ESTABLISHED_DIRECTION` **with measured dispersions**:
mean `D = −47/73440` ᾱ-units, population `sd(D) = 0.022377` ᾱ-units
(`= 5.71/255` lattice units), movers up/down/non = 9/6/9 against
concordance threshold 18, sign split 13/11. This round therefore decides,
on numbers rather than aesthetics, whether **any** further registration
is defensible, or whether the programme closes *computed*.

*Disclosure (continuity with Rounds 2–4):* subagent delegation tooling is
unavailable in this session; the three roles below are parent-argued
against repository facts. All probabilities are exact binomial tails;
all data quantities are exact Fractions read from the retained reduced
artifact this session; the single continuous approximation used
(normal quantile map for design sizing) is labelled as such wherever it
appears. Inputs re-verified against
`results/stage8-alpha-evolution-paired/confirmatory-paired-20310529-reduced.json`
(SHA-256 `bdb14fbedcfbcc4d3b3194edbfad428ac8869f1f8c75d848a6655147dd284dec`)
and `docs/stage-8-paired-execution-note.md`.

## ADVOCATE — for one more registration: a coexistence-regime paired probe

**A1. The sizing mandate has never once been exercised.** Review Part II
binds future work to be "sized against these measured dispersions, not
against hope". Both executed nulls were *expected*-null by construction
and said so before executing; consequently no instrument with
non-trivial power for any plausible effect has ever been run. A null
from a *powered* design is a different epistemic object from a null
from a deliberately blind one. Closure now would freeze the record with
the powered experiment still unattempted.

**A2. A session-scale ceiling-regime design exists on paper.** At
permanent-coexistence phenotypic variance (`∫σ²_A dt ≈ 2601` A-units²
per turnover, the prereg §6 ceiling density) the displacement needed
for the concordance rule to reach even coin-flip (≈50%) power under
the *measured* dispersion is `μ ≈ 7.9` lattice units (R1's own map;
≈80% needs `μ ≈ 8.7`). At the
cross-sectional-bound slope `β ≈ 8×10⁻⁵` that integral corresponds to
`T ≈ 38` turnovers, `W ≈ 4,527` ticks. Scaling the single recorded
retained wall (≈2 h 46 m for 48 runs at W = 2400, two workers)
linearly: ≈5.2 h — one overnight-class retained suite converts
direction (a) from "unattempted" to "answered with power".

**A3. The rule is not frozen across registrations.** §10 freezes
thresholds *within* a registration; a NEW registration may carry a
different (pre-declared) statistic. A mean-based paired rule on
`n = 24` with `σ = 5.71` reaches ≈80% power at `μ ≈ 3.3` lattice units
by normal approximation — near the floor itself. Re-running the SAME
ecology under a mean-rule registration is nearly free relative to (A2)
and directly powered for effects 4–5× the cross-sectional bound.

## ADVERSARIAL REVIEWER — attacking the weakest assumption

*The advocate's load-bearing assumption is dispersion transfer: that
`σ_D ≈ 5.71`, measured once at W = 2400 under winner-take-most
exclusion, describes the noise of the alternative regimes the advocate
wants to buy power in.*

**R1. Assumption-light power computed on the retained sample itself
kills the same-ecology family outright.** Shift method: add a true
uniform shift `μ` to each of the 24 exact `D_i` and count floor
crossings (no distributional assumption beyond shift-invariance):

| true shift μ (lattice units) | movers-up | exact power `P(Bin(24,·)≥18)` |
|---|---|---|
| 0 | 9/24 | 0.00021 |
| 2 | 10/24 | 0.00097 |
| **4 (= whole floor)** | 13/24 | **0.03041** |
| 6 | 15/24 | 0.14533 |
| 8 | 18/24 | 0.60741 |
| 10 | 20/24 | 0.90883 |

A true displacement equal to the *entire registered floor* yields 3.0%
power. ≈50% power needs `μ ≈ 7.5`; ≈80% needs `μ ≈ 8.7` (normal-approx
map agrees: 50% ⇔ `p_up ≈ 0.73`, `μ* ≈ 7.5`; 80% ⇔ `p_up ≈ 0.80`,
`μ* ≈ 8.7`; `σ = 5.7061`). The
minimal uniform shift that lets ≥18/24 pairs cross the floor at all is
`359/48 ≈ 7.48` units — **1.87× the floor**.

**R2. The k-cliff: concordance power is k-*invariant* below per-pair
p ≈ 0.75.** Exact tails `P(Bin(k,p) ≥ ⌈3k/4⌉)` at `p = 0.70`:
`0.38859 / 0.27962 / 0.16938` for `k = 24/48/96`. Below `p = 0.75`,
adding replicates *reduces* power. The rule's entire power lives in
per-pair signal beyond the floor; no affordable k rescues an instrument
whose per-pair SNR is below 1 — and R1 shows it is far below.

**R3. Where the advocate's 5-hour estimate actually comes from — and
why its premise contradicts every recorded ecology.** The ceiling-density
integral (2601 A-units²·turnover⁻¹) presupposes *permanent coexistence*
of both lineages for ~38 turnovers. The retained record shows the
opposite regime: winner-take-most exclusion completes in 2–4 turnovers,
R0 distinct-A collapses to 1..2, terminal censuses are single-lineage.
Manufacturing coexistence means inventing frequency-dependent regulation
mechanics — the largest new code surface since 7B1 — breaking the
additive-reuse economy and importing unmeasured mediator risk. Under the
*recorded* realistic-exclusion regime (∫ ≈ 455 per turnover), the
static-σ requirement is `W ≈ 25,900` ticks (≈30 h wall); pricing in the
mutation-cloud random walk (`σ_D ∝ √W`: both arms' clouds drift
independently, so pairing does not cancel cloud drift) makes the
requirement diverge — solving `0.0364·T = 3.264·√(T/20)` gives
`T ≈ 402` turnovers, `W ≈ 48,000` ticks, ≈2.3 days wall, to test
exactly the bound with zero margin and an extrapolated σ.

**R4. A3's cheap mean-rule dies on the same arithmetic.** At the bound
slope the expected 20-turnover displacement is `μ_bound = 8e-5·9.1e3 ≈
0.73` lattice units ⇒ noncentrality `0.73/(5.71/√24) ≈ 0.63` ⇒ power
≈12%: the mean-rule at this ecology is powered only for slopes ≥
`3.26/9.1e3 ≈ 3.6×10⁻⁴` — **4.5× the cross-sectional bound**. Long-window
variants hit R3's divergence. So the mean-rule buys either another
expected-null or a multi-day extrapolation.

**R5. Multiplicity debt without a candidate effect.** A third
confirmatory-family test of the same substantive question (direction of
α-redistribution through the channel), undertaken when the post-prior
odds favour null and *every* candidate effect size sits below what
session-scale instruments can express above measured noise, purchases
inferential risk without a mechanism plausibly at detectable magnitude.

## METHOD AUDITOR

**M1.** Neither branch touches a closed line; Round-4 binding item 4 is
respected by both (the probe would be a fresh registration/table/ecology,
not a rerun).
**M2.** Reading dispersion and rule arithmetic off the retained reduced
artifact is instrumentation output expressly permitted by repair-prereg
§6 ("reads whatever this one registers"); the proposed closing unit is
documentation-only and requires no execution registration (Part V item 3
precedent: the common procedural requirements bind implementations and
retained runs, neither of which occurs).
**M3.** Inputs re-verified this session against the reduced artifact:
exact `D_i` table recomputed; mean `−47/73440` ✓; population sd
`0.022377` ᾱ (`= 5.7061` lattice units) matching the execution note to
4 s.f. ✓; median `|D| = 437/24480` ᾱ `= 4.551` lattice (note reports 4.6
rounded) ✓; movers 9/6/9 ✓; sign split 13/11 ✓. Registered null size
anchor re-derived exactly: `Σ_{k≥18} C(24,k)/2²⁴ = 190051/16777216 =
0.01133` one-sided ✓.
**M4.** Housekeeping: suite green this session (**419 passed, 4
skipped**, 19 subtests — 423 total as previously counted); tree clean;
origin synced 0/0 at `8ebe36d`.
**M5.** Discipline favours registering explicit reopening conditions
over a third adjacent confirmatory test.

## Verdict

**CLOSURE SURVIVES — the programme closes on computed grounds.** The
advocate's A2/A3 designs are not wrong in intent but fail on R1–R4:
their power premises contradict either the measured dispersion (same
ecology) or every recorded population dynamic (coexistence regimes), and
no affordable k, rule, or window escapes the cliff while the candidate
effect scale sits ≈1–2 orders of magnitude below what windows of
feasible length can express above the measured noise. Binding
obligations carried forward:

1. **O1:** commit `docs/stage-8-followon-power-memo.md` reproducing every
   table above with exact arithmetic, provenance digests, and the
   derivation chain — so that closure rests on computation any reader
   can re-run, not on fatigue.
2. **O2:** register the reopening conditions (binding triggers for any
   future session): **R1** — an independently justified measurement
   establishing per-pair `σ_D ≤ 3.0` lattice units at demonstrated
   coexistence persistence ≥ 40 turnovers (which would make a
   ceiling-regime `W ≈ 4.5k` paired design ≥ 80% powered at bound slope
   for ≈5 h wall); **R2** — a validated phenotype-informative recruitment
   endpoint family, which must first break the vacancy-blindness
   identity (recorded: admitted births identical across arms,
   `23,933 = 23,933`) via genuine de-saturation AND pass the 7B1 §6.2
   life-cycle promotion demonstration; **R3** — owner redirection, which
   supersedes without prejudice as always.
3. **O3:** until a reopening condition fires, no evolutionary execution
   is authorised anywhere in this programme; the next session's lawful
   units are verification, documentation, and owner-directed work.
4. **O4:** programme review Part V is rewritten to point at this verdict
   and the memo, replacing the open follow-on question with the closed,
   computed answer.
