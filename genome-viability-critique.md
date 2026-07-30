# Genome Viability Analysis — Structured Critique

**Document:** `/opt/data/avida-life/genome-viability.md`
**Critiqued:** 2026-07-26
**Severity scale:** CRITICAL → MAJOR → MINOR → NOTE

---

## 1. Mathematical Correctness

### 1.1 Minimal replicator cost (L=2) — MAJOR

The document states REPRODUCE costs `5 + 2×2 = 9` units. This arithmetic is correct per the boundary model (Section 8e: check=5, copy+mutate=genome_length×2).

**However, the execution trace table (Section 3b) is internally inconsistent.** The document's formula says:

```
After executing REPRODUCE:  R' = R - (5 + 2L)
After transfer:            R'' = 0.5 × R'
After upkeep:              R''' = R'' - 2
```

But the table shows:

| Tick | PC | Instruction | Cost | After instr | After upkeep | Offspring |
|------|----|-------------|------|-------------|-------------|-----------|
| 0    | 0  | REPRODUCE   | 9    | 991         | 989         | 494.5     |

**Contradiction:** The table's "After upkeep" = 989 = 1000 − 9 − 2, which means the 50% transfer was **not applied** to the parent's reserve. The offspring's 494.5 = 989/2 implies the transfer happened **after** upkeep, contradicting the formula that places it before upkeep.

**Correct trace per the stated formula:**

| Tick | PC | Instruction | After instr | After transfer | After upkeep |
|------|----|-------------|-------------|----------------|-------------|
| 0    | 0  | REPRODUCE   | 991         | 495.5          | 493.5       |
| 1    | 1  | JUMP 0      | 492.5       | —              | 490.5       |

The document's table is therefore wrong. The correct parent reserve after the first reproduction cycle (REPRODUCE + JUMP) is ~490.5, not 989.

### 1.2 Minimum reserve for reproduction — MAJOR

The document derives R > 9 + 2L (R > 13 for L=2) as the minimum reserve needed to reproduce. This only checks survival through the REPRODUCE tick itself. It **omits the JUMP instruction and its upkeep** that the minimal replicator must execute between reproductions.

**Full cycle check:**

```
REPRODUCE tick:  pay 9, transfer 50% → 0.5×(R-9), upkeep → 0.5×(R-9)-2
JUMP tick:       pay 1 → 0.5×(R-9)-3, upkeep → 0.5×(R-9)-5
```

For the parent to survive the full cycle: `0.5 × (R - 9) - 5 > 0` → **R > 19**.

The document's threshold of R > 13 is **6 units too low**. This error propagates into:
- The generational depth estimate (more generations appear possible than actually are)
- The L_max(resource) table (overestimates viable genome length)
- The conclusion that generation 6 (R≈15) can reproduce

### 1.3 Generational depth — MAJOR

The document uses an approximate halving model (ignoring instruction costs) to estimate ~7 generations. The precise recurrence (including instruction costs and the corrected R > 19 threshold) gives:

| Generation | Approximate R (doc) | Precise R (start of cycle) | Can reproduce? |
|------------|---------------------|---------------------------|----------------|
| 0 (ancestor) | 1,000 | 1,000.00 | Yes |
| 1 | 500 | 490.50 | Yes |
| 2 | 250 | 235.75 | Yes |
| 3 | 125 | 108.38 | Yes |
| 4 | 62 | 44.69 | Yes |
| 5 | 31 | 12.84 | **No** (R < 19) |
| 6 | 15 | — | No |
| 7 | 7 | — | No |

**The precise model gives ~5 reproductive generations, not ~7.** The document overestimates generational depth by ~40%.

### 1.4 P_viable formula vs. table values — CRITICAL

The document's stated formula:

```
P_viable = (1 - 0.001c)^L × (1 - 0.01c)^2 × (1 - 0.001c)
```

produces values that **do not match the table**.

| L | Table (c=1.0) | Stated formula | Discrepancy |
|---|---------------|----------------|-------------|
| 2 | 0.977 | 0.977 | ✓ |
| 10 | 0.890 | **0.969** | −0.079 |
| 20 | 0.792 | **0.960** | −0.168 |
| 50 | 0.558 | **0.931** | −0.373 |
| 100 | 0.311 | **0.886** | −0.575 |
| 200 | 0.097 | **0.802** | −0.705 |
| 500 | 0.009 | **0.594** | −0.585 |

The table appears to have been computed with a different formula — possibly `P = (1−0.001)^L × (1−0.01)^L × (1−0.001)^L` (i.e., treating insertions/deletions as per-locus rather than per-genome events) — but even that formula doesn't match the table exactly for all values. The L=500 value (0.009) is inconsistent with any plausible per-locus model of the stated rates.

**This is a critical error.** The entire mutation load analysis (Section 4d, 4e, 6, 7) is built on a formula that the document itself does not apply correctly. The conclusion that "mutation load limits genome length to ~50 for c=1.0" is unsupported by the stated formula, which gives P_viable ≈ 0.93 for L=50 — far above the 0.5 threshold.

### 1.5 Lineage half-life — MINOR

The document estimates lineage half-life as `1 / (1 - 0.977) ≈ 43 generations` for L=2. This uses the formula for a geometric distribution with extinction probability = 1 − P_viable. This is correct for a branching process where each generation independently produces 1 offspring with probability P_viable. However, it ignores the resource constraint, which the document itself acknowledges is tighter (generation ~7).

### 1.6 Dormancy cost arithmetic — MINOR

The dormancy analysis (Section 5b) calculates total cycle cost as `17 + 0.2N` and derives `0.5 × (R - 17) - 0.2N > 0`. This inconsistently applies the 50% transfer: it subtracts all instruction costs first, then halves. The correct formula is:

```
0.5 × (R - 9) - 8 - 0.2N > 0   →   N < 2.5R - 40
```

For R=1,000: N < 2,460 (document says 2,457 — close, but the error is ~20 ticks, and the discrepancy grows at lower R).

Additionally, the dormancy analysis assumes a **3-instruction genome** (REPRODUCE, SLEEP, JUMP) but refers to it as "a 2-instruction genome" — an inconsistency that doesn't affect the arithmetic but shows sloppiness.

---

## 2. Assumptions

### 2.1 That JUMP needs an operand — NOTE

The document assumes JUMP takes an operand (address). The boundary model (Section 12) lists JUMP/JUMPZ/JUMPNZ with cost 1 but doesn't specify the operand model. The assumption is reasonable for a typical instruction set but should be explicitly stated, as it affects genome length (a JUMP with an implicit operand would be a single instruction, but the minimal replicator would still need 2 instructions: REPRODUCE + JUMP).

### 2.2 That PC after REPRODUCE is PC+1 — NOTE

The document assumes the parent continues at PC+1 after REPRODUCE. The boundary model (Section 8a) says "Execution continues with the next instruction" on a failed REPRODUCE but doesn't specify the PC after a successful REPRODUCE. This assumption is reasonable but critical — if PC resets to 0 after reproduction (common in some artificial life systems), the minimal replicator would be 1 instruction, changing the entire analysis.

### 2.3 That the minimal replicator works as described — MAJOR

The minimal replicator `[REPRODUCE, JUMP 0]` assumes:
1. The offspring starts at PC=0 with the same genome.
2. The offspring's first instruction is REPRODUCE (at PC=0).
3. The offspring's JUMP 0 loops back to REPRODUCE.

This works, **but it assumes the offspring executes in the same tick as the parent**. The boundary model says "The offspring is added to the scheduler's queue for the next tick" (Section 8d). This means the offspring doesn't execute until the next tick boundary. The parent, however, continues executing immediately. This is fine for the analysis but should be noted.

**More critically, the document assumes the parent reproduces and then continues executing the loop. But the parent's reserve after the 50% transfer is what it has to survive on. The document's table doesn't correctly apply this transfer, as shown in Section 1.1.**

### 2.4 Missing: Offspring execution priority — NOTE

The document doesn't consider whether the offspring executes before or after the parent in the same tick. The round-robin scheduler with randomised order (Section 3) means the offspring might execute before the parent finishes its cycle, potentially affecting the order of resource depletion. This is a minor detail for the analytical model but could affect empirical results.

### 2.5 Missing: The 50% transfer is a cost, not a creation — MAJOR

The document treats the 50% transfer correctly in the formula but incorrectly in the execution trace (Section 1.1). The boundary model explicitly states that the offspring's reserve "comes directly from the parent's reserve" (Section 8c). The document's table showing the parent with 989 after the REPRODUCE tick (without the transfer deducted) violates this principle.

---

## 3. Recommendations

### 3.1 Increase initial reserve to 1,000,000 — MINOR ISSUE

The recommendation is sound in principle but the reasoning is flawed. The document says it provides ~17 generations. With the corrected model (R > 19 threshold, precise recurrence), 1,000,000 units gives:

```
R_0 = 1,000,000
R_1 = 0.5 × (1,000,000 - 9) - 5 = 499,990.5
R_2 = 0.5 × (499,990.5 - 9) - 5 = 249,985.75
...
```

This is still ~log₂(R₀/19) ≈ 16 generations — roughly consistent with the document's claim. The recommendation is valid but addresses a symptom, not the cause.

**However, the document's table of generations vs. initial reserve is wrong.** It says:

| Initial reserve | Generations |
|----------------|-------------|
| 1,000 | 7 |
| 10,000 | 10 |
| 100,000 | 14 |
| 1,000,000 | 17 |

Using the corrected minimum R > 19 (not R > 13):
- Generations = floor(log₂(1000/19)) = floor(5.7) = **5** (not 7)
- Generations = floor(log₂(10000/19)) = floor(9.0) = **9** (not 10)
- Generations = floor(log₂(100000/19)) = floor(12.4) = **12** (not 14)
- Generations = floor(log₂(1000000/19)) = floor(15.7) = **15** (not 17)

### 3.2 Transform-based replenishment (Option C) — MAJOR ISSUE

The recommendation to introduce "transform-based reserve replenishment" (Option C) is in tension with the project's core principle of avoiding hidden reward functions. The boundary model (Section 11d) states:

> "A strictly dissipative system ensures that selection acts on metabolic efficiency (reducing costs) rather than on acquiring external energy subsidies."

Option C introduces an external energy subsidy tied to data compression. The document's own Section 10b of the boundary model already describes how TRANSFORM reduces upkeep by shrinking memory — this is the "reduce costs" path. Adding a direct reserve replenishment for compression creates a **second, independent reward pathway**: organisms are rewarded twice for the same behaviour (lower upkeep AND more reserve).

**This smuggles fitness.** The document's justification ("it couples metabolism to data processing") conflates two distinct mechanisms:
- **Passive efficiency:** Smaller memory → lower upkeep (the legitimate path)
- **Active reward:** Compression → bonus reserve (the smuggled fitness path)

**A better approach:** Keep the dissipative model but increase the MEMORY_COST_DIVISOR so that memory reduction has a more significant impact on upkeep. This rewards efficiency without adding a separate reward channel.

### 3.3 Option A and B — NOTE

**Option A (compression threshold bonus):** Arbitrary threshold introduces hidden semantic judgment. The document correctly rejects this.

**Option B (per-tick passive income):** Universal subsidy dilutes selection pressure. The document correctly identifies this as problematic.

### 3.4 Pre-register the viable band prediction — NOTE

Sound scientific practice. No issue.

---

## 4. Gaps

### 4.1 Offspring may evolve different strategies than the parent — MAJOR

The document assumes the entire population follows the same minimal replicator strategy. It does not consider:
- **Lineage branching:** An offspring might mutate to a different genome length or strategy, potentially out-competing the parent.
- **Metabolic divergence:** Offspring could evolve different transforms, dormancy patterns, or reproduction strategies.
- **Niche partitioning:** Different lineages could occupy different resource niches (e.g., some reproduce fast with short genomes, others slowly with long genomes).

The analysis treats the population as a single lineage with a single strategy, which is a significant limitation for a document that claims to define the "viable band" for evolution.

### 4.2 Shared memory pool is finite — MINOR

The document mentions the shared memory pool (boundary model Section 5) but does not account for:
- If the pool is exhausted, REPRODUCE fails (Section 8a, condition 2).
- A population of 500 organisms × 64 bytes minimum = 32,000 bytes minimum. What is the pool size?
- Competition for memory could be a binding constraint before reserve exhaustion.

The population cap of 500 (with displacement mortality) means memory is recycled, so this may not be a problem in practice. But it should be explicitly addressed.

### 4.3 Cooperation and resource sharing — NOTE (deferred)

The document correctly notes that cooperation is not possible in Stages 1–6 (boundary model Section 16). This is a design choice, not a gap. However, the analysis should acknowledge that the inability to cooperate means the results are bounded by individual-level selection only.

### 4.4 Displacement mortality interaction — MINOR

The boundary model (Section 14) describes displacement mortality at the population cap. The document's analysis assumes all death is metabolic. At the population cap, death by displacement is uniform across lineages, but it interacts with generational depth: a lineage that goes extinct metabolically may be replaced by one that hasn't yet. The document doesn't consider this.

### 4.5 The offspring also needs to survive JUMP — MAJOR

The document's minimum reserve formula (R > 13) only checks survival through the REPRODUCE tick. But the offspring — like the parent — must execute JUMP and pay upkeep before it can reproduce again. The offspring's minimum viable starting reserve is therefore also R > 19, not R > 13. This error is symmetric with Section 1.2.

---

## 5. The 7-Generation Problem

### 5.1 Is it fatal? — MINOR (for Stage 1)

The document correctly identifies that the dissipative model guarantees extinction. The question is whether this is a design flaw. For Stage 1 experiments (testing whether real substrate coupling changes outcomes), 5–7 generations may be sufficient to observe basic replication dynamics and measure the coupling effect. The document's own conclusion — "sufficient for Stage 1" — is reasonable.

**However, the document overestimates the generational depth** (claims ~7, actual ~5 with corrected math). This is a meaningful difference: 5 generations is very little time for selection to act, especially if the first 1–2 generations are dominated by initialisation effects.

### 5.2 Minimal fix that preserves the scientific question — MAJOR

The document's recommended fix (Option C: transform-based replenishment) **does not preserve the scientific question** because it introduces a new reward pathway. The minimal fix that preserves the dissipative principle is:

1. **Increase initial reserve** (as the document recommends, but with corrected math).
2. **Increase the reproduction transfer fraction** from 50% to a higher value (e.g., 75%). This means the parent keeps more reserve, extending the lineage.
3. **Decrease REPRODUCE check cost** from 5 to 1, reducing the fixed overhead per reproduction.

These changes preserve the strictly dissipative model while extending generational depth. Alternatively, the document could accept 5 generations as the experimental window and design Stage 1 experiments accordingly.

---

## 6. Mutation Model

### 6.1 Assumption: substitutions in non-critical instructions are never lethal — MAJOR

The document acknowledges this assumption is "almost certainly false" (Open Question 5) but uses it throughout the analysis. A substitution in a MOV instruction's register operand could cause the organism to write to the wrong memory location, corrupting state. A substitution in a conditional jump's condition register could change control flow fatally.

**A more realistic model would assign a non-zero probability of lethality to ALL instructions, not just "critical" ones.** The critical fraction c should be interpreted as "probability that a given instruction is critical" rather than "fraction of instructions that are critical." Better yet, use a per-position lethal probability model where each instruction has a small probability of being fatal if mutated, with higher probabilities for control-flow instructions.

### 6.2 Insertions/deletions in non-critical regions — MINOR

The document correctly notes that insertions/deletions of NOPs in non-critical regions are harmless. However, it doesn't consider frame-shift effects: an insertion or deletion shifts all subsequent instruction boundaries, which is almost certainly lethal regardless of where it occurs. The document's model assumes instruction boundaries are fixed (or that the genome is a sequence of independent instructions), which is a significant simplification.

### 6.3 Duplication lethality — MINOR

The document is inconsistent about whether duplication is lethal. It says "duplication anywhere... may be OK if it duplicates a non-critical region" but then treats duplication as always lethal for the minimal genome. This is reasonable but should be stated more clearly.

### 6.4 The mutation survival curve table is wrong — CRITICAL

As shown in Section 1.4, the P_viable table values don't match the stated formula. The document's conclusion that "mutation load limits genome length to ~50 for c=1.0" is based on the wrong table values. With the correct formula, P_viable(L=50, c=1.0) ≈ 0.93, which is far above the 0.5 threshold. The actual mutation load limit would be much higher (L > 500 for c=1.0 before P_viable drops below 0.5).

---

## 7. Clarity

### 7.1 Conclusions are generally clear — NOTE

The document's conclusions are stated in plain language and are easy to follow. The "Formal Viable Band Statement" (Section 9) is a good summary.

### 7.2 Leaps in logic — MAJOR

1. **Generational depth from approximate halving model:** The document uses an approximate halving model (ignoring instruction costs) to estimate 7 generations, then uses this estimate as a precise result in the viability band table (Section 4e). The leap from "approximately" to "precisely" is unmarked.

2. **Mutation load as binding constraint:** The document says mutation load limits genome length to ~50, then immediately shows that the resource constraint is tighter (L_max=26 at generation 4). The mutation load analysis is presented as a primary result but is actually irrelevant — the resource constraint dominates. This is acknowledged in Section 6c but the document doesn't restructure the analysis to reflect this.

3. **P_viable ≠ lineage survival:** The document equates P_viable(L) < 0.5 with lineage extinction. This is only true for a lineage producing exactly 1 offspring per parent. If a lineage can produce multiple offspring per parent (by reproducing multiple times before death), the threshold is lower. The document doesn't consider this.

### 7.3 Internal inconsistencies — MAJOR

- Table in Section 3b doesn't apply the 50% transfer to the parent's reserve.
- P_viable formula (Section 4d) doesn't produce the table values (Section 4d tables).
- Dormancy analysis (Section 5b) uses a different cost-ordering than the stated formula.
- The document says "7 generations" but the precise model gives ~5.
- The document says "L_max(mutation) = 50" for c=1.0, but the stated formula gives P_viable(50, 1.0) = 0.93, making the 50 threshold arbitrary.

---

## 8. Summary of Severity Ratings

| # | Issue | Severity |
|---|-------|----------|
| 1 | P_viable formula doesn't match table values | CRITICAL |
| 2 | Execution trace table doesn't apply 50% transfer to parent | MAJOR |
| 3 | Minimum reserve formula (R > 13) misses JUMP+upkeep costs (should be R > 19) | MAJOR |
| 4 | Generational depth overestimated (~5 actual vs ~7 claimed) | MAJOR |
| 5 | Offspring minimum viable reserve also wrong (propagated from #3) | MAJOR |
| 6 | Assumption that non-critical substitutions are never lethal is untenable | MAJOR |
| 7 | Option C recommendation smuggles fitness via dual reward pathway | MAJOR |
| 8 | Lineage branching and strategy divergence not considered | MAJOR |
| 9 | Table of generations vs. initial reserve is wrong (uses R > 13 threshold) | MAJOR |
| 10 | Dormancy analysis uses inconsistent cost-ordering | MINOR |
| 11 | Dormancy analysis calls 3-instruction genome "2-instruction" | MINOR |
| 12 | No consideration of shared memory pool exhaustion | MINOR |
| 13 | Displacement mortality interaction not addressed | MINOR |
| 14 | Generational depth estimate from log₂(R/13) is ~2 generations optimistic | MINOR |
| 15 | JUMP operand assumption not explicitly stated | NOTE |
| 16 | PC after REPRODUCE not explicitly stated | NOTE |
| 17 | Conclusions are clearly written | NOTE (positive) |
| 18 | Open Questions section is thorough and honest | NOTE (positive) |

---

## 9. Verdict

**Should the document proceed to Stage 1C as-is?** **NO.**

**Should it proceed after revision?** **YES, after the top 3 issues are fixed.**

---

### Top 3 Things to Fix

1. **Fix the P_viable formula and table (CRITICAL).** The stated formula and the table values are inconsistent. Either correct the formula to match the table, or recompute the table from the formula. The mutation load analysis is the analytical core of the document and cannot proceed with a formula that the author cannot apply correctly. Recommend: explicitly state the formula, compute it in a script, and verify every value in the table.

2. **Fix the minimum reserve formula (MAJOR).** The document's R > 9 + 2L omits the JUMP instruction and upkeep that the minimal replicator needs between reproductions. The correct threshold is R > 19 for L=2. This error propagates into the generational depth estimate, the viable band table, and the recommendation to increase initial reserve. Fix the formula, recalculate the generational depth (precise model gives ~5 generations, not ~7), and update the recommendations accordingly.

3. **Fix the execution trace table (MAJOR).** The table in Section 3b must correctly apply the 50% reserve transfer to the parent's reserve. Currently it shows the parent with 989 after the REPRODUCE tick, which is inconsistent with the formula. The correct values show the parent with ~493.5 after the first REPRODUCE tick (after transfer and upkeep). This table is the document's primary worked example and must be correct.

---

### Additional Strongly Recommended Fixes

4. **Reconsider Option C.** Either justify why a dual reward pathway (lower upkeep + bonus reserve for the same behaviour) does not constitute smuggled fitness, or select a different replenishment mechanism that preserves the strictly dissipative principle (e.g., increase the reproduction transfer fraction, reduce REPRODUCE overhead, or increase MEMORY_COST_DIVISOR).

5. **Address the non-critical instruction lethality assumption.** The document acknowledges this is false (Open Question 5) but builds the entire analysis on it. Either provide a more realistic model (e.g., each instruction has a probability of being critical, not just a fixed fraction of instructions) or explicitly state that this is a best-case bound and discuss how a more realistic model would tighten the viable band.

6. **Restructure the mutation load analysis.** The document presents mutation load as a primary constraint, then shows it's not binding (resource constraint dominates). The mutation load analysis should be secondary or presented as a context-dependent bound, not as a primary result.