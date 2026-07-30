# Substrate — Genome Viability Analysis

*Stage 1B: Analytical determination of the viable genome length band.*
*Drafted 2026-07-26. Revised 2026-07-26 (v2: corrected execution trace, minimum reserve threshold, P_viable table, generational depth; replaced Option C with parameter tuning).*

---

## 1. Purpose

This document analyses the range of genome lengths that can sustain self-replication under the boundary model's cost structure and mutation rates. The key question is: **how wide is the viable band** between "too short to replicate" and "too long to copy without lethal error or resource exhaustion?"

If the viable band is narrow (e.g., <5 instructions), the system cannot produce interesting evolutionary dynamics regardless of substrate coupling. If it is wide enough (e.g., >20 instructions), there is genuine space for functional variation, specialisation, and ecological interaction.

---

## 2. Reference Parameters

All values from the boundary model (Stage 1A):

| Parameter | Value | Source |
|-----------|-------|--------|
| Initial ancestor reserve | 1,000 units | Sec 14 |
| Minimum working memory | 64 bytes | Sec 8c |
| BASE_UPKEEP | 1 unit/tick | Sec 11a |
| MEMORY_COST_DIVISOR | 64 | Sec 11a |
| Per-tick upkeep (ACTIVE, minimum memory) | 1 + 64/64 = 2 units | Sec 11a |
| Per-tick upkeep (DORMANT) | 0.2 units (10% of ACTIVE) | Sec 7a |
| REPRODUCE check cost | 5 units | Sec 8e |
| REPRODUCE copy cost | genome_length × 2 units | Sec 8e |
| Reproduction transfer | 50% of parent's remaining reserve (after check+copy) | Sec 8c |
| Substitution probability | 0.001 per instruction | Sec 8b |
| Insertion probability | 0.01 per genome | Sec 8b |
| Deletion probability | 0.01 per genome | Sec 8b |
| Duplication probability | 0.001 per genome | Sec 8b |
| Minimum instruction cost | 1 unit (NOP, JUMP, DIE) | Sec 12 |
| Population cap | 500 (default) | Sec 14 |

---

## 3. Minimal Replicator Design

### 3a. Instruction Set Available

From Section 12, the instructions available in Stages 1–6 (excluding Stage 7+ messaging):

| Instruction | Cost | Purpose in minimal replicator |
|-------------|------|------------------------------|
| `NOP` | 1 | No operation; filler only |
| `JUMP addr` | 1 | Unconditional jump to address |
| `JUMPZ reg, addr` | 1 | Jump if register is zero |
| `JUMPNZ reg, addr` | 1 | Jump if register is non-zero |
| `MOV dst, src` | 1 | Copy register value |
| `ADD dst, a, b` | 2 | Arithmetic |
| `SUB dst, a, b` | 2 | Arithmetic |
| `AND dst, a, b` | 2 | Bitwise |
| `OR dst, a, b` | 2 | Bitwise |
| `XOR dst, a, b` | 2 | Bitwise |
| `CMP a, b` | 2 | Compare (sets flags) |
| `READ dst_addr, length` | 2 | Read data packet into working memory |
| `WRITE src_addr, length` | 2 | Write working memory to internal buffer |
| `ALLOC size` | 1 + ceil(size/64) | Allocate additional working memory |
| `FREE addr` | 1 | Free a memory region; cannot free addresses within the minimum working memory block (bytes [0, 63]) |
| `TRANSFORM op, addr, length` | 3 + length | Apply transform to memory region |
| `SLEEP N` | 1 | Enter dormancy for N ticks |
| `REPRODUCE` | 5 + 2×genome_length | Reproduce |
| `DIE` | 1 | Self-terminate |

**Assumptions about instruction semantics:**
- `JUMP addr` takes an immediate operand (address in the genome). Operand is stored as part of the instruction; instruction length is 1 word (address is encoded in the instruction word).
- After a successful `REPRODUCE`, the parent's program counter advances to PC+1 (the next instruction). The offspring starts at PC=0.
- The offspring is added to the scheduler queue for the next tick (Section 8d); it does not execute in the same tick as the parent.
- Each instruction is a fixed-size word; the genome is a linear sequence of such words.

### 3b. The Minimal Self-Replicator

The minimal genome capable of sustained self-replication must:
1. Execute `REPRODUCE` to create an offspring
2. Return to the `REPRODUCE` instruction to repeat

This requires exactly **2 instructions**:

```
Address  Instruction    Notes
0        REPRODUCE     Attempt to produce an offspring
1        JUMP 0        Loop back to REPRODUCE
```

**Is a 1-instruction genome possible?** No. After executing the single instruction (REPRODUCE), the program counter increments to 1. Since the genome has length 1, PC=1 is out of bounds, triggering structural execution failure (Section 9, condition 3) → DEAD. A 1-instruction organism dies after its first action.

**Conclusion: 2 instructions is the absolute minimum.**

### 3c. Execution Trace

For a 2-instruction genome, the cost of one REPRODUCE instruction is:
- Check: 5 units
- Copy + mutate: 2 × 2 = 4 units
- **Total instruction cost: 9 units**

After the instruction cost is deducted, 50% of the remaining reserve is transferred to the offspring. Then per-tick upkeep is deducted at the tick boundary.

**Correct trace (ancestor, R₀ = 1,000):**

| Tick | PC | Instruction | Before instr | After instr | After transfer | After upkeep | Offspring |
|------|----|-------------|-------------|-------------|----------------|-------------|-----------|
| 0 | 0 | REPRODUCE | 1,000.0 | 991.0 | 495.5 | 493.5 | 495.5 |
| 1 | 1 | JUMP 0 | 493.5 | 492.5 | — | 490.5 | — |
| 2 | 0 | REPRODUCE | 490.5 | 481.5 | 240.75 | 238.75 | 240.75 |
| 3 | 1 | JUMP 0 | 238.75 | 237.75 | — | 235.75 | — |

**Key detail:** The parent's reserve after the first full cycle (REPRODUCE + JUMP) is ~490.5, not 989 as a naive halving model would suggest. The instruction costs and upkeep consume ~9.5 units per cycle.

---

## 4. Reserve Requirements for Reproduction

### 4a. Single Tick Survival

For a parent to survive a single REPRODUCE tick (genome length L):

```
After instruction:     R₁ = R₀ - (5 + 2L)
After transfer:        R₂ = 0.5 × R₁
After upkeep:          R₃ = R₂ - 2
```

For survival: R₃ > 0

```
0.5 × (R₀ - 5 - 2L) - 2 > 0
R₀ - 5 - 2L > 4
R₀ > 9 + 2L
```

**Minimum reserve for single REPRODUCE tick (L=2):** R₀ > 13 units.

### 4b. Full Cycle Survival

The parent must also survive the JUMP tick that follows REPRODUCE and returns to the loop start:

```
After REPRODUCE tick:     R₃ = 0.5 × (R₀ - 9) - 2   (for L=2)
After JUMP instruction:   R₄ = R₃ - 1
After JUMP tick upkeep:   R₅ = R₄ - 2
```

For survival through the full cycle:

```
R₅ > 0
0.5 × (R₀ - 9) - 2 - 1 - 2 > 0
0.5 × (R₀ - 9) > 5
R₀ > 19
```

**Minimum reserve for full cycle (L=2):** R₀ > 19 units.

### 4c. Offspring Viability

The offspring starts with R_offspring = 0.5 × (R_parent - 5 - 2L). It must then survive its own full cycle to reproduce.

For the offspring to be viable (able to complete at least one full cycle and reproduce):

```
0.5 × (R_parent - 5 - 2L) > 19
R_parent - 5 - 2L > 38
R_parent > 43 + 2L
```

For L=2: R_parent > 43 + 4 = **47 units**.

This is the true minimum for a sustainable lineage: a parent must have at least 47 units of reserve for its offspring to be capable of reproduction. This is substantially higher than the R > 19 required for the parent's own survival through a full cycle.

### 4d. Generational Depth

The precise recurrence for the minimal replicator (L=2):

```
R_{n+1} = 0.5 × (R_n - 9) - 5
```

The −5 is the combined cost of JUMP (1) and two ticks of upkeep (2 + 2) between reproductions.

| Generation | R (start of cycle) | Can reproduce? | Offspring R |
|------------|-------------------|----------------|-------------|
| 0 (ancestor) | 1,000.0 | Yes | 490.5 |
| 1 | 490.5 | Yes | 235.75 |
| 2 | 235.75 | Yes | 108.38 |
| 3 | 108.38 | Yes | 44.69 |
| 4 | 44.69 | Yes | 12.84 |
| 5 | 12.84 | **No** (R < 19) | — |

**Generational depth ≈ 5 generations**, not 7 as estimated by a naive halving model. The instruction and upkeep costs consume ~9.5 units per cycle, which is significant relative to the reserve available in later generations.

General formula for generational depth (ignoring the −5 constant for an upper bound):

```
R_n ≈ R_0 / 2^n - 9.5 × (2^n - 1) / 2^n
```

For extinction when R_n < 19:

```
R_0 / 2^n < 19 + 9.5
R_0 < 28.5 × 2^n
n > log₂(R_0 / 28.5)
```

| R₀ | n (generations) | Notes |
|----|-----------------|-------|
| 1,000 | 5 | Current default |
| 10,000 | 8 | |
| 100,000 | 11 | |
| 1,000,000 | 15 | |
| 10,000,000 | 18 | |
| 1,000,000,000 | 25 | ~1 billion units |

---

## 5. Viable Genome Length Band

### 5a. Lower Bound: L_min = 2

The shortest possible replicator is 2 instructions. No shorter genome can execute REPRODUCE and return to it.

### 5b. Upper Bound by Resource Constraint

From the survival inequality for a full cycle (Section 4b):

For a parent with reserve R and genome length L:
```
0.5 × (R - 5 - 2L) - 5 > 0
R - 5 - 2L > 10
R > 15 + 2L
L < (R - 15) / 2
```

| Reserve R | Max viable L | Notes |
|-----------|-------------|-------|
| 1,000 (ancestor) | 492 | Generous |
| 490 (gen 1) | 237 | Generous |
| 235 (gen 2) | 110 | Comfortable |
| 108 (gen 3) | 46 | Comfortable |
| 44 (gen 4) | 14 | Tight |
| 12 (gen 5) | — | Below minimum |

**Resource constraint conclusion:** The upper bound declines each generation as reserve is consumed. In early generations (0–2), genomes up to ~100 instructions are viable. By generation 4, only genomes ≤14 instructions can reproduce.

### 5c. Upper Bound by Mutation Load

The probability that a genome of length L survives one reproduction event without a lethal mutation:

```
P_viable(L) = (1 - p_sub × c)^L × (1 - p_ins × c) × (1 - p_del × c) × (1 - p_dup × c)
```

Where:
- p_sub = 0.001, p_ins = 0.01, p_del = 0.01, p_dup = 0.001
- c = probability that a given instruction is critical (i.e., a mutation in it is lethal)

**Note on c:** The fraction of instructions that are "critical" is not a fixed property of the genome — it depends on the specific structure of the genome and the instruction semantics. A substitution in a `NOP` is almost certainly harmless. A substitution in `REPRODUCE` is almost certainly lethal. A substitution in `JUMP 0` that changes the operand to `JUMP 5` might be harmless (if the genome has 6+ instructions) or lethal (if it doesn't). For this analysis, c is treated as a parameter. The minimal replicator (L=2) has c=1.0 because every instruction is critical.

**Tables for P_viable(L) at various c values:**

| L | c=1.0 | c=0.5 | c=0.2 | c=0.1 |
|---|-------|-------|-------|-------|
| 2 | 0.977 | 0.989 | 0.995 | 0.998 |
| 5 | 0.974 | 0.987 | 0.995 | 0.997 |
| 10 | 0.969 | 0.985 | 0.994 | 0.997 |
| 20 | 0.960 | 0.980 | 0.992 | 0.996 |
| 50 | 0.931 | 0.965 | 0.986 | 0.993 |
| 100 | 0.886 | 0.941 | 0.976 | 0.988 |
| 200 | 0.802 | 0.895 | 0.957 | 0.978 |
| 500 | 0.594 | 0.771 | 0.901 | 0.949 |

Computed from the formula above using verified arithmetic. The c=1.0 column represents the worst case (all instructions critical). The c=0.2 column approximates a genome with mostly non-critical padding.

**Threshold for lineage viability:** A lineage requires P_viable > 0.5 to produce at least one viable offspring per parent on average (assuming one offspring per reproduction attempt). If P_viable < 0.5, the lineage contracts.

| c | L at P_viable = 0.5 | Notes |
|---|---------------------|-------|
| 1.0 | ~670 | All instructions critical |
| 0.5 | ~1,360 | Half critical |
| 0.2 | ~3,440 | Mostly non-critical |
| 0.1 | ~6,900 | Mostly non-critical |

**Mutation load is not a binding constraint for any realistic genome length.** Even in the worst case (c=1.0), a genome must exceed 670 instructions before lethal mutation load makes lineage extinction probable. This is far above the resource constraint limit (~60 instructions in early generations).

### 5d. Combined Upper Bound

| Generation | R | L_max (resource) | L_max (mutation, c=1.0) | Effective L_max |
|------------|---|-----------------|------------------------|-----------------|
| 0 | 1,000 | 492 | 670 | 492 |
| 1 | 490 | 237 | 670 | 237 |
| 2 | 235 | 110 | 670 | 110 |
| 3 | 108 | 46 | 670 | 46 |
| 4 | 44 | 14 | 670 | 14 |
| 5 | 12 | — | 670 | 0 (cannot reproduce) |

**The binding constraint is resource exhaustion, not mutation load.** In early generations, the resource constraint allows genomes up to ~100 instructions. By generation 3, it tightens to ~46. By generation 4, only genomes ≤14 instructions are viable. Mutation load is not a binding constraint at any generation — even the worst-case threshold (L > 670 for c=1.0) far exceeds the resource-imposed limits.

---

## 6. The Efficiency Problem

### 6a. Generational Depth is Limiting

The dissipative model guarantees extinction within ~5 generations (for R₀=1,000). Each reproduction halves the parent's reserve, and there is no mechanism to increase total reserve. The population is on a finite timer.

For 5 generations of evolution, the observable dynamics are limited to:
- Mutation and selection on the minimal replicator
- Genome length variation within the 2–60 range (narrowing to 2–14 by generation 4)
- Basic competition for shared memory (if the pool is constrained)
- No opportunity for complex ecological interactions, cooperation, or major transitions

### 6b. Mitigation Strategies Available to Organisms

Organisms can extend their lifespan through:

1. **Dormancy.** SLEEP reduces upkeep to 0.2 units/tick. A dormant organism burns reserve 10× slower. The optimal dormancy strategy: reproduce once, then sleep for as long as possible before the next reproduction.

2. **Reducing effective genome length.** Shorter genomes cost less to copy. Compressing or eliminating non-critical instructions reduces the reproduction cost.

3. **Minimal working memory.** The minimum block is 64 bytes. An organism cannot reduce this below 64 bytes, so upkeep from memory is fixed at 1 unit/tick (the minimum).

4. **Strategic reproduction timing.** An organism that reproduces less frequently preserves more reserve between cycles, but also produces fewer offspring.

### 6c. The Dormancy-Dominant Strategy

Consider a 3-instruction genome [REPRODUCE, SLEEP N, JUMP 0]:

1. REPRODUCE: costs 9, transfers 50%
2. SLEEP N: costs 1, enters dormancy for N ticks (0.2/tick upkeep)
3. JUMP 0: costs 1, loops back
4. Repeat

Total cost per cycle: 9 (REPRODUCE) + 1 (SLEEP) + 1 (JUMP) + 2 (ACTIVE upkeep, 2 ticks) + 0.2N (dormant upkeep)

After instruction costs and transfer: 0.5 × (R - 11) - 2 - 0.2N

For survival: 0.5 × (R - 11) - 2 - 0.2N > 0 → N < 2.5R - 37.5

For R=1,000: N < 2,462 ticks. This allows very long dormancy periods, but does not change the fundamental reserve decay — it merely stretches the timeline.

---

## 7. Mutation Survival Curve

### 7a. Per-Generation Mutation Load

For a genome of length L with critical fraction c:

P_viable(L) = (1 - 0.001c)^L × (1 - 0.01c) × (1 - 0.01c) × (1 - 0.001c)

The insertions and deletions are per-genome events (not per-instruction), so they contribute a fixed factor regardless of L. The substitution probability is per-instruction, so it compounds with L.

### 7b. Effective Mutation Rate

The effective lethal mutation rate per generation is:

μ_eff(L) = 1 - P_viable(L)

| L | μ_eff (c=1.0) | μ_eff (c=0.5) | μ_eff (c=0.2) |
|---|---------------|---------------|---------------|
| 2 | 0.023 | 0.011 | 0.005 |
| 10 | 0.031 | 0.015 | 0.006 |
| 50 | 0.069 | 0.035 | 0.014 |
| 100 | 0.114 | 0.059 | 0.024 |
| 200 | 0.198 | 0.105 | 0.043 |
| 500 | 0.406 | 0.229 | 0.099 |

### 7c. Binding Constraints in Order of Severity

1. **Resource exhaustion** (generation ~5, R < 19 units)
2. **Structural minimum** (L < 2 instructions)
3. **Mutation load** (only relevant for L > ~670 at c=1.0; never binding within the resource-constrained viable band)

For the default parameters (R₀=1,000), **resource exhaustion is the only binding constraint.** The population goes extinct from reserve depletion long before mutation load could become a significant factor. Even at L=500 (far above the resource limit of ~14 in late generations), fewer than half of offspring carry lethal mutations.

---

## 8. Implications and Recommendations

### 8a. The 5-Generation Problem

With the default parameters, the system provides only ~5 generations of observable evolution. This is **sufficient for Stage 1 experiments** (testing whether basic replication occurs, measuring mutation rates, confirming the analytical predictions), but **insufficient for Stage 3+ experiments** (ecology, adaptation, open-ended evolution).

**For Stage 1, the 5-generation limit is acceptable.** The first experiment is not about complex evolution — it is about whether the minimal replicator works at all, and whether real substrate coupling changes the basic dynamics.

### 8b. Parameter Tuning to Extend Generational Depth (Recommended)

Rather than introducing a new replenishment mechanism (which risks smuggling fitness), the dissipative model can be extended by tuning three parameters:

| Parameter | Current | Proposed | Effect |
|-----------|---------|----------|--------|
| Initial reserve | 1,000 | 1,000,000 | R₀/2^n > 19 → 15 generations |
| Reproduction transfer | 50% | 75% | Parent keeps more reserve; lineage extends |
| REPRODUCE check cost | 5 | 1 | Reduces fixed overhead per reproduction |

**Combined effect (R₀=1,000,000, transfer=75%, check=1):**

```
R_{n+1} = 0.25 × (R_n - 3 - 2L) - 5
```

For L=2: R_{n+1} = 0.25 × (R_n - 7) - 5

| Generation | R | Notes |
|------------|---|-------|
| 0 | 1,000,000 | |
| 1 | 249,993 | |
| 2 | 62,491 | |
| 3 | 15,616 | |
| 4 | 3,897 | |
| 5 | 967 | |
| 6 | 235 | |
| 7 | 52 | |
| 8 | 6 | Below minimum |

~8 generations — still limited. The 75% transfer extends depth but not dramatically because the parent keeps more but the offspring gets less.

**Better approach: increase initial reserve AND reduce per-tick upkeep.**

| Parameter | Current | Proposed | Effect |
|-----------|---------|----------|--------|
| Initial reserve | 1,000 | 10,000,000 | ~18 generations |
| BASE_UPKEEP | 1 | 0.1 | 10× less consumption per tick |
| MEMORY_COST_DIVISOR | 64 | 640 | 10× less memory cost |

With R₀=10,000,000, BASE_UPKEEP=0.1, MEMORY_COST_DIVISOR=640:

Per-tick upkeep = 0.1 + 64/640 = 0.1 + 0.1 = 0.2 units/tick

Full cycle cost: 5 + 4 (REPRODUCE) + 1 (JUMP) + 0.2 + 0.2 (upkeep) = 10.4

R_{n+1} = 0.5 × (R_n - 9) - 1.4

| Generation | R | Notes |
|------------|---|-------|
| 0 | 10,000,000 | |
| 1 | 4,999,990 | |
| 2 | 2,499,990 | |
| 3 | 1,249,990 | |
| 4 | 624,990 | |
| 5 | 312,490 | |
| 6 | 156,240 | |
| 7 | 78,115 | |
| 8 | 39,048 | |
| 9 | 19,519 | |
| 10 | 9,755 | |
| 11 | 4,873 | |
| 12 | 2,432 | |
| 13 | 1,212 | |
| 14 | 602 | |
| 15 | 297 | |
| 16 | 145 | |
| 17 | 69 | |
| 18 | 31 | |
| 19 | 12 | Below minimum |

**~19 generations** — a significant improvement. This preserves the strictly dissipative model (no new reward pathways) while providing enough generational depth for meaningful evolutionary observation.

### 8c. What to Avoid

- **Do not add a reserve replenishment bonus for compression.** This creates a dual reward pathway (lower upkeep + bonus reserve) that violates the dissipative principle and smuggles fitness.
- **Do not add per-tick passive income.** This dilutes selection pressure and makes the system less discriminating.
- **Do not change the mutation rates.** The current rates give a reasonable balance between variation and stability. Lower rates reduce variation; higher rates increase lethal load.

### 8d. Recommended Parameter Set for Stage 1 Experiments

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Initial reserve | 10,000,000 | ~19 generations |
| BASE_UPKEEP | 0.1 | 10× less consumption |
| MEMORY_COST_DIVISOR | 640 | 10× less memory cost |
| Reproduction transfer | 50% | Preserves equal parent/offspring split |
| REPRODUCE check cost | 5 | Preserves original cost model |
| Population cap | 500 | Default |
| Minimum working memory | 64 bytes | Default |

This gives ~19 generations of observable evolution while preserving the strictly dissipative model. The reduced upkeep costs make the system less "noisy" (fewer deaths from incidental costs) and allow more headroom for genome growth.

---

## 9. Confirming the Viable Band Empirically

Before running the full evolutionary system, a minimal viability test should:

1. Seed a single organism with the 2-instruction genome [REPRODUCE, JUMP 0]
2. Run for 500 ticks
3. Verify: the organism reproduces, the offspring reproduces, etc.
4. Measure: actual generational depth, reserve trajectory, mutation rate, offspring count
5. Compare: does the empirical depth match the analytical prediction?

If the empirical depth is significantly less than predicted, the analytical model is missing a cost factor. If it is significantly more, there may be an undiscovered resource subsidy.

---

## 10. Formal Viable Band Statement

> The Substrate instruction set has a minimum viable genome length of 2 instructions (REPRODUCE + JUMP). The upper bound is determined by resource availability: L < (R - 15) / 2 for a full cycle, where R is the parent's execution reserve. Under the dissipative model with default parameters (R₀=1,000), the population produces ~5 generations before extinction. Mutation load is not a binding constraint at any point — even the worst-case threshold (L > ~670 for c=1.0) far exceeds the resource-imposed limits. The viable band is therefore determined entirely by resource availability, narrowing from 2–492 in early generations to 2–14 by generation 4. For Stage 1 experiments, the recommended parameter set (R₀=10,000,000, BASE_UPKEEP=0.1, MEMORY_COST_DIVISOR=640) extends generational depth to ~19 while preserving the strictly dissipative model.

---

## 11. Open Questions

1. **Empirical verification.** Does the analytical model match actual simulation results? The cost accounting may miss edge cases (e.g., scheduler overhead, memory allocation latency).

2. **Dormancy equilibrium.** Under what conditions does a dormancy-only strategy outcompete an active strategy? Does the population reach a stable equilibrium or always crash?

3. **Genome growth under mutation.** Insertions and duplications can increase genome length. If the offspring inherits a longer genome, its reproduction cost increases. Does this create a ratchet toward minimal genomes, or can functional instructions accumulate?

4. **Population structure with displacement.** At the population cap (500 organisms), displacement mortality interacts with generational depth. Does displacement select for faster reproduction (more offspring = more displacement slots) or for metabolic efficiency (longer-lived lineages)?

5. **Non-critical instruction lethality.** The analysis assumes that mutations in non-critical instructions are never lethal. This is a simplification — a substitution in a MOV instruction's register operand could cause the organism to write to the wrong memory location, corrupting its own state. The true viable band is likely narrower than the analysis predicts.