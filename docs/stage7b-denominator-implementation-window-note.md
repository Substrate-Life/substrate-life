# Stage 7B Denominator-Repair Implementation Window — Scope Note

*Date: 2026-08-23. Additive status note; registers nothing, supersedes
nothing, authorises nothing. The binding protocol is
`docs/stage-7b-denominator-repair-preregistration.md`, which this note
does not modify.*

## What this window added

Per the denominator-repair prereg Authorisation section and §6.1
(implementation window open; no retained execution; frozen modules never
edited in place), one commit adds exactly the new, additively-defined
tooling the preregistration calls for:

- `src/stage7b_exposure_measure.py` — repaired two-factor ENDPOINT
  estimator: person-tick fecundity `m^E_x = n_x/E_x` (numerator reused
  byte-identically from `stage7b_endpoint_measure.raw_fecundity_counts`;
  denominators recovered bit-exactly as `l_counts[x] = l_x[x]·|C_g|`
  from the frozen schedule) times risk-set window-actuarial survivorship
  `l^A_{x+1} = l^A_x(E_x − d_x)/E_x` with exact deaths-by-age extraction;
  coefficients assembled by the frozen `build_c_vector`. All five binding
  identities are enforced loudly inside the estimator. The reported
  descriptive `l_x` and the establishment mediator are carried unchanged.
- `src/stage7b_exposure_config.py` — protocol label
  (`stage-7b-denominator-repair-preregistration`), retained-output paths
  (`results/stage7b-exposure-endpoint/`), and the carried §3 ecology
  re-exported verbatim from the unchanged `stage7b2r_population.py`.
- `src/stage7b_exposure_gate.py` — the §5 feasibility-gate tooling over
  the fixed 24-seed table `20270000+j`, G1–G4 unchanged across
  generations, per-replicate evidence in stdout only (no retained
  artifact). To be executed next session; a pass unblocks the §6 freeze.
- `src/test_stage7b_exposure_mechanics.py` — 28 tests: frozen-module hash
  pins (inherited verbatim), configuration echo, hand-computed two-factor
  schedules on synthetic ledgers, all binding identities plus loud-failure
  paths, the Lemma-C collapse regression, and supercriticality
  reachability with an independent first-principles oracle.

Runner/reducer/output-schema for the confirmatory suite deliberately
wait for the freeze session (they freeze together per §6.2).

Full unittest discovery: **248 tests OK** (skipped=4); tree clean;
pushed after each commit.

## Definition-level facts recorded en route (factual, not decisions)

1. **Theorem B confirmed empirically at 0/24**: the archived gate run of
   the superseded raw-fecundity endpoint failed G1/G2 on both arms while
   G3/G4 stayed perfect — the same signature as the 7B2-R failure, one
   layer deeper. Every certified value sat below the ceiling
   `1 − F_g/|C_g|`; the largest was `5/6`.
2. **Lemma C (collapse)**: because `E_x ≡ l_counts[x]`, the naive repair
   `c_x = l_x·(n_x/E_x)` equals `n_x/|C_g|` term-for-term — algebraically
   identical to the superseded scalar endpoint. Recorded as an exact
   regression test (`CollapseRegressionTests`) on a concrete growing
   ledger where the collapsed form yields exactly `B_g/|C_g| = 80/81`.
3. **Reachability restored by the registered two-factor form**: on the
   same ledger, the repaired coefficients certify `L(0) = 41/27 > 1`
   (module and independent oracle agree bit-exactly) while both
   predecessor endpoints certify subcriticality. This is a property of
   one synthetic ledger family, not a claim about any registered ecology;
   whether G1/G2 can be met at the carried ecology is precisely what the
   §5 gate will decide next session.

## Consequence for the next session

Execute the §5 gate over the fixed table with
`stage7b_exposure_gate.py` (sanctioned, unretained, ~30 min at
`--workers 2`). If it passes: freeze estimator + config + gate + runner +
reducer + tests + schema together with a pre-execution manifest (§6.2),
then the single retained confirmatory suite is authorised (§6.3). If it
fails: further superseding preregistration with diagnosis supported by
new evidence (§5.4). Either way: corrections require a further superseding
preregistration — never edits to this note, the binding preregistration,
or any superseded document; frozen-module byte-identity continues to be
enforced by the hash-pin tests; mutation remains unauthorised in every
form; no fitness, selection, optimum, or ESS claim exists in any Stage 7
artifact, including this note.
