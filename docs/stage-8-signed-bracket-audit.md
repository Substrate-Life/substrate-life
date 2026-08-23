# Stage 7B Signed-Bracket Post-Retention Audit

*Date: 2026-08-23. Tool: `src/audit_stage7b_signed_bracket.py` (read-only;
writes nothing inside the repository). Companion to
`docs/stage-8-programme-review.md`. Evidence class: post-retention audit
of already-classified artifacts; makes no new contrast, fitness, or
selection claim and registers no execution.*

## Verdict

| Check | Result |
|---|---|
| Raw artifact SHA-256 vs execution-note record (`6268a3da…73d3d`, 18,828,711 B) | **MATCH** |
| Raw artifact hash vs value embedded in the retained reduced file | **MATCH** |
| Frozen reducer re-executed on the retained raw artifact, output redirected outside the repo | **BYTE-IDENTICAL** to the retained reduced file (16,690 B; no divergence offset) |
| Independent recomputation of the outcome from raw solver certificates (fresh implementation, exact `Fraction`) | **AGREES**: 32 complete pairs; median paired difference `−1/128`; sign split 21 negative / 9 positive / 2 zero; `ONE_ARM_SUBCRITICAL` |
| Pre-execution-manifest drift, all four Stage 7B generations (4+4+8+8 pinned files re-hashed) | **ZERO DRIFT** |
| Full test suite at audit time | 303 tests OK (293 prior + 10 new audit-helper tests) |

The byte-identical re-reduction simultaneously re-verifies the reducer's
internal claims (estimator recomputation bit-exact against cohort
schedules, zero mismatches, rule applied to identical inputs) and that
every source file feeding the reduction is still byte-for-byte the
freeze-state content.

## Descriptive dispersion scoping (non-binding design input)

Computed over the same 32 complete pairs. Per the closed registration,
nothing here retunes any registered parameter; no threshold is
recommended, and none may be inferred from this section. Any future
floor or design choice belongs to the owner-chosen direction's own
superseding preregistration, disclosed before its freeze.

**Per-genotype bracket midpoints** (lower-middle conventions):

| Genotype | n | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| A=102 | 32 | −3/512 | 1/512 | 1/512 | 1/512 | 1/512 |
| A=204 | 32 | −53/512 | −5/512 | −3/512 | 1/512 | 1/512 |

**Paired differences** `Δ_i = mid(204) − mid(102)`:

| statistic | value |
|---|---|
| min | −27/256 |
| Q1 | −3/256 |
| median | −1/128 |
| Q3 | +1/256 |
| max | +1/128 |
| median \|Δ\| | 1/128 (= 25/32 of the floor `1/100`) |
| share of pairs with \|Δ\| ≥ 1/100 | 7/16 |

Three observations refine the programme-review diagnosis without
changing any conclusion:

1. **The LOW arm sits at the measurement floor.** In ≥ 24/32 replicates
   the A=102 certificate is exactly `[0, 1/256]` — barely supercritical,
   with the certified root within one solver-resolution unit of zero.
   Most windows show near-critical dynamics for both arms, so the
   contrast is being taken between two quantities both close to the
   resolution limit.
2. **The paired differences are heavy-tailed, not shifted.** The median
   |Δ| is *below* the floor while 7/16 of individual pairs exceed it —
   with mixed signs. The distribution's mass is in a few large-
   magnitude exclusion-shaped pairs (min −27/256), not in a consistent
   small displacement. This quantifies the priority-effect
   contamination diagnosed qualitatively in the signed-bracket
   preregistration §2 (D-B): pair-level magnitudes are large but
   direction-inconsistent, which is precisely the shape a
   winner-take-most ecology produces.
3. **Consequence for design (not a parameter recommendation):** any
   future paired design at an ecology with this correlation structure
   inherits a signal-to-noise profile dominated by exclusion variance.
   Designs that decouple the arms (within-genotype endpoints, de-
   saturated ecologies, trajectory-integrating endpoints) attack the
   noise source rather than enlarging the sample.

## Reproduction

```
cd src && python3 -m unittest test_audit_stage7b_signed_bracket   # 10 tests
cd src && python3 audit_stage7b_signed_bracket.py                 # summary JSON
```

Runtime ≈ 40 s (dominated by parsing the 18.8 MB raw artifact and the
reducer re-execution). The reducer subprocess writes only to a system
temporary directory; the repository tree is untouched.
