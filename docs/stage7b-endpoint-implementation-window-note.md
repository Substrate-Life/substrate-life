# Stage 7B Endpoint-Repair Implementation Window — Scope Note

*Date: 2026-08-23. Additive status note; registers nothing, supersedes
nothing, authorises nothing. The binding protocol is
`docs/stage-7b-endpoint-repair-preregistration.md` (committed `17b6aed`),
which this note does not modify.*

## What this window added

Per endpoint-repair prereg §§5.1 and 6.1 (implementation window open;
no retained execution; frozen modules never edited in place), one commit
adds exactly the new, additively-defined tooling the preregistration
calls for:

- `src/stage7b_endpoint_measure.py` — corrected ENDPOINT estimator:
  raw age-specific fecundity `m_x` (every admitted birth credited exactly
  once to its immediate parent at the parent's age at the birth tick,
  divided by `|C_g|`; prereg §3), plus the establishment quantity carried
  unchanged as a reported mediator (`establishment_m_x`). Survivorship
  `l_x`, Lotka coefficient assembly, the certified solver, ledger
  extraction, and population mechanics are reused byte-identically from
  the retained freezes (`stage7b2_measure.py`, `stage7b2_population.py`,
  `stage7b2_solver.py`, `stage7b2r_population.py`; hash-pinned by tests).
- `src/stage7b_endpoint_config.py` — protocol label, output paths, and
  the carried §3 ecology re-exported verbatim; shakedown table reused
  verbatim per §5.2.
- `src/run_stage7b_endpoint.py`, `src/reduce_stage7b_endpoint.py` — the
  confirmatory suite's runner/reducer pair (retention only after gate +
  freeze; reducer verifies `l_x`, endpoint `m_x`, AND mediator
  `establishment_m_x` bit-exactly, then applies the carried §5 rule once).
- `src/stage7b_endpoint_gate.py` — §5 feasibility-gate tooling over the
  fixed 24-seed table `20270000+j`, G1–G4 unchanged, per-replicate
  evidence in stdout only (no retained artifact, §5.5).
- `src/test_stage7b_endpoint_mechanics.py`,
  `docs/stage7b-endpoint-output-schema.md` — test matrix and artifact
  contract, to be frozen together with a pre-execution manifest if the
  gate passes.

Full unittest discovery: **220 tests OK** (skipped=4); tree clean;
pushed after commit.

## Flagged observation for the §5 gate (factual, not a decision)

While implementing the registered §3 numerator, the following exact
identity — a direct consequence of the registered definitions, verified
by property tests on synthetic ledgers and on genuine short-window
population output — came to light:

> Every admitted birth creates exactly one new member of `C_g`
> (founders being the only members not born in-window), so for every
> genotype and every replicate
> `sum_x m_x(g) = B_g / |C_g| = (|C_g| - F_g) / |C_g| = 1 - F_g/|C_g|`.
> Since `0 <= l_x(g) <= 1` termwise (registered), the endpoint satisfies
> `L(0) = sum_x l_x m_x <= sum_x m_x = 1 - F_g/|C_g| < 1` whenever
> `F_g >= 1` (3 founders/genotype in every Stage 7B2/7B2-R registration).

This is the same bound shape as the preregistration's own §2 proof — the
births→members map (each birth is its child) is injective exactly as the
establishments→members map was — applied to the §3 replacement rather
than to the superseded establishment filter. It suggests the §5 gate's
G1/G2 conditions may again be structurally unsatisfiable under the
corrected endpoint, independent of ecology or seeds; prereg §5.4's
observation that "`sum_x m_x(g)` is bounded only by total births per
cohort member, which is empirically in the hundreds" appears to conflate
the birth count `B_g` (hundreds) with the ratio `B_g/|C_g| <= 1`.

Tests recording the underlying facts (definition-level identities on
concrete ledgers; no universal claim is encoded):
`test_births_conservation_identity`, `test_termwise_bound_on_this_ledger`,
`test_many_births_still_bounded`,
`ShortWindowIntegrationTests.test_conservation_identity_holds_on_real_output`,
`ShortWindowIntegrationTests.test_termwise_bound_holds_on_real_output`.

## Consequence for the next session (unchanged from the prereg)

Nothing here changes any registered decision; §5 remains binding as
written. Two compliant paths exist, at the next session's judgement:

1. Execute the §5 gate on its fixed table (sanctioned, unretained). If
   G1/G2 fail — as the observation above predicts — §5.4 applies: no
   freeze; a further superseding preregistration with the new diagnosis
   (the denominator/cohort-normalisation layer, not the birth filter).
   The archived failure evidence would then mirror the 7B2-R precedent.
2. Draft that further superseding preregistration first, registering the
   diagnosis derived from the identity above (a proof, not merely gate
   evidence), before spending the gate run. The 7B1 §2-style proof
   pattern supports a proof-first registration.

Either way: corrections require a further superseding preregistration —
never edits to this note, the endpoint-repair preregistration, or any
superseded document; frozen-module byte-identity continues to be enforced
by the hash-pin tests; mutation remains unauthorised in every form; no
fitness, selection, optimum, or ESS claim exists in any Stage 7 artifact,
including this note.
