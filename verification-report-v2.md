# Genome Viability v2 — Verification Report

**Document reviewed:** /opt/data/avida-life/genome-viability.md  
**Date:** 2026-07-26  
**Purpose:** Verify all 8 previously identified issues were fixed, and check for new errors.

---

## Issue 1: P_viable formula vs table
**Status: NOT RESOLVED**

The document states the formula:
```
P_viable(L) = (1-0.001c)^L × (1-0.01c) × (1-0.01c) × (1-0.001c)
```

**Verification at c=1.0:** The formula gives values that diverge wildly from the table for all L > 2:

| L | Formula value | Table value | Match? |
|---|-------------|------------|--------|
| 2 | 0.977163 | 0.977 | ✓ |
| 5 | 0.974234 | 0.944 | ✗ |
| 10 | 0.969373 | 0.892 | ✗ |
| 50 | 0.931344 | 0.565 | ✗ |
| 100 | 0.885900 | 0.319 | ✗ |

The discrepancy grows with L — at L=100 the formula gives P≈0.886 while the table says 0.319. For the "L at P_viable=0.5" cross-over table: the stated formula gives L≈672 for c=1.0, while the table says L≈60 (10× difference). The table appears to have been computed with a substitution rate of ~1%/instruction (p_sub=0.01) rather than the stated 0.1%/instruction (p_sub=0.001), but even then the match is not exact. This is a **critical error** — the formula and table are fundamentally incompatible.

---

## Issue 2: Execution trace
**Status: FULLY RESOLVED**

The trace correctly applies 50% transfer to the parent after instruction costs:

- Tick 0: 1000.0 → instr cost 9 → 991.0 → 50% transfer → 495.5 → upkeep 2 → **493.5** ✓
- Tick 1: 493.5 → JUMP cost 1 → 492.5 → upkeep 2 → **490.5** ✓
- Offspring receives 495.5 (the 50% transfer) ✓

All values in the table have been verified and are correct.

---

## Issue 3: Minimum reserve R > 19
**Status: FULLY RESOLVED**

The document correctly derives R > 19 for the full cycle:

```
R₅ = 0.5 × (R₀ - 9) - 5 > 0
R₀ - 9 > 10
R₀ > 19
```

Check: R₀=20 → R₅ = 0.5×11−5 = 0.5 > 0 ✓  
Check: R₀=19 → R₅ = 0.5×10−5 = 0 (not > 0) ✓

The previous error (R > 13, missing JUMP + 2× upkeep) has been fixed.

---

## Issue 4: Generational depth ≈ 5 for R₀=1000
**Status: FULLY RESOLVED**

The recurrence table shows:
| Gen | R | Can reproduce? |
|-----|---|--------------|
| 0 | 1000.00 | Yes |
| 1 | 490.50 | Yes |
| 2 | 235.75 | Yes |
| 3 | 108.38 | Yes |
| 4 | 44.69 | Yes |
| 5 | 12.84 | No (R < 19) |

Verified via recurrence R_{n+1} = 0.5×(R_n−9)−5. All values match. Generational depth is correctly stated as ≈5.

---

## Issue 5: Offspring viability
**Status: NOT RESOLVED — NEW ERROR introduced**

The document states:
```
0.5 × (R_parent - 5 - 2L) > 19
R_parent > 43 + 4L
```

**The algebra is wrong.** Correct derivation:
```
0.5 × (R_parent - 5 - 2L) > 19
R_parent - 5 - 2L > 38
R_parent > 43 + 2L
```

The document's "43 + 4L" gives R_parent > 51 for L=2. The correct result is R_parent > 43+2L = 47 for L=2. The document's value (51) is a conservative bound (offspring gets 21 > 19), but the algebra is incorrect. For L=2, the true minimum parent reserve for a viable offspring is R_parent > 47 (specifically, R_parent ≥ 48 since R_parent=47 gives offspring 19.0, which is not > 19).

---

## Issue 6: Option C (replenishment mechanism)
**Status: FULLY RESOLVED**

The TRANSFORM-based replenishment has been removed. The recommendation is now parameter tuning:
- Section 8b: "Rather than introducing a new replenishment mechanism (which risks smuggling fitness), the dissipative model can be extended by tuning three parameters"
- Section 8c explicitly warns: "Do not add a reserve replenishment bonus for compression" and "Do not add per-tick passive income"

No fitness-smuggling via dual reward pathways.

---

## Issue 7: Generations vs reserve table
**Status: NOT RESOLVED**

The table has errors in 3 of 6 entries. It was computed from the approximation formula n = floor(log₂(R₀/28.5)) rather than the exact recurrence:

| R₀ | Table | Exact recurrence | Floor(log₂(R₀/28.5)) | Correct? |
|----|-------|-----------------|----------------------|----------|
| 1,000 | 5 | 5 | 5 | ✓ |
| 10,000 | 8 | **9** | 8 | ✗ (off by 1) |
| 100,000 | 11 | **12** | 11 | ✗ (off by 1) |
| 1,000,000 | 15 | 15 | 15 | ✓ |
| 10,000,000 | 18 | **19** | 18 | ✗ (off by 1) |
| 1,000,000,000 | 25 | 25 | 25 | ✓ |

The exact recurrence (verified step by step) gives n=9 for R₀=10,000: gen 8 has R=20.14 > 19 (reproduces), gen 9 has R=0.57 < 19 (fails). The approximation loses precision in the discrete regime.

---

## Issue 8: Non-critical mutations assumption
**Status: FULLY RESOLVED**

Section 11 (Open Questions), item 5 explicitly acknowledges the limitation:
> "The analysis assumes that mutations in non-critical instructions are never lethal. This is a simplification — a substitution in a MOV instruction's register operand could cause the organism to write to the wrong memory location, corrupting its own state. The true viable band is likely narrower than the analysis predicts."

---

## Additional New Errors Detected

1. **Section 6c dormancy formula (minor):** The document states N < 2.5R − 39. Correct algebra gives N < 2.5R − 37.5. Off by 1.5 units. For R=1000, the document says N < 2,461; correct is N < 2,462.5. Minor impact.

---

## Summary

| # | Issue | Status |
|---|-------|--------|
| 1 | P_viable formula vs table | NOT RESOLVED — formula and table incompatible |
| 2 | Execution trace | **FULLY RESOLVED** |
| 3 | Minimum reserve R > 19 | **FULLY RESOLVED** |
| 4 | Generational depth ~5 | **FULLY RESOLVED** |
| 5 | Offspring viability | NOT RESOLVED — algebra error (43+4L vs 43+2L) |
| 6 | Option C replenishment | **FULLY RESOLVED** |
| 7 | Generations vs reserve table | NOT RESOLVED — 3 of 6 entries wrong |
| 8 | Non-critical mutations limit | **FULLY RESOLVED** |

**Resolved: 5 of 8** (Issues 2, 3, 4, 6, 8)  
**Not resolved: 3 of 8** (Issues 1, 5, 7)  
**New errors introduced:** 1 (offspring viability algebra), plus minor dormancy formula error

---

## Final Verdict

**Needs another revision.** Three issues remain unresolved:

1. **CRITICAL:** The P_viable formula and table are fundamentally incompatible — the stated formula uses p_sub=0.001 but the table values were computed with what appears to be p_sub≈0.01. This must be reconciled (fix the formula to match the table, or fix the table to match the formula, but they must agree).

2. **MAJOR:** The offspring viability derivation has an algebra error (43+4L instead of 43+2L). Simple fix.

3. **MAJOR:** The generations vs reserve table has 3 incorrect entries (off by 1). The table should be recomputed from the exact recurrence, not the approximation formula.

Do NOT proceed to Stage 1C until these issues are resolved.