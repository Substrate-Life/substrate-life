# Substrate — Revised Genome Viability (with Composite REPRODUCE)

*Recalculating L_min, generational depth, and viable band with ALLOC_OFFSPRING + COPY_UNIT + DIVIDE.*

---

## 1. Revised Instruction Set

New instructions added to the Stage 1A instruction set:

| Instruction | Opcode | Cost | Effect |
|-------------|--------|------|--------|
| ALLOC_OFFSPRING | 19 | 5 + size/64 | Allocate gestation region in working memory; address stored in R1 |
| COPY_UNIT | 20 | 2 | Copy one instruction from genome to gestation region; R2 = 0 if more, 1 if done |
| DIVIDE | 21 | 5 | Finalise offspring, apply mutations, separate |

REMOVED from the Stage 1A instruction set:
| Instruction | Removal reason |
|-------------|----------------|
| REPRODUCE | Replaced by ALLOC_OFFSPRING + COPY_UNIT + DIVIDE |

All other instructions unchanged.

---

## 2. Minimal Replicator (L_min = 6)

The shortest genome capable of sustained self-replication is 6 instructions:

```
Address  Instruction              Notes
0        MOV R0, 64              Offspring memory size (minimum block)
1        ALLOC_OFFSPRING R0      Allocate gestation region
2        COPY_UNIT               Copy one instruction; R2 = 1 when done
3        JUMPZ R2, 2             If R2 = 0 (not done), jump back to COPY_UNIT
4        DIVIDE                  Finalise offspring
5        JUMP 0                  Loop back to start
```

**Key properties:**
- The copy loop (instructions 2–3) is 2 instructions: COPY_UNIT + JUMPZ
- The loop runs exactly L times per generation (copying all L instructions)
- The FAIL flag is set by COPY_UNIT when P >= genome_length; R2 = 1 triggers loop exit
- L_min = 6 (vs 2 with atomic REPRODUCE)

### 2a. Execution Trace (First Cycle, L=6, R₀=10,000,000)

| Tick | Instr | Cost | R before | R after | After upkeep | After transfer | Notes |
|------|-------|------|----------|---------|--------------|----------------|-------|
| 0 | MOV R0,64 | 1 | 10,000,000.0 | 9,999,998.8 | 9,999,998.6 | — | After 1st instr upkeep |
| 1 | ALLOC_OFFSPRING | 6 | 9,999,998.6 | 9,999,992.6 | 9,999,992.4 | — | 5 + 64/64 = 6 |
| 2 | COPY_UNIT | 2 | 9,999,992.4 | 9,999,990.4 | 9,999,990.2 | — | P=1, R2=0 |
| 3 | JUMPZ R2,2 | 1 | 9,999,990.2 | 9,999,989.2 | 9,999,989.0 | — | R2=0 → jump to 2 |
| 4 | COPY_UNIT | 2 | 9,999,989.0 | 9,999,987.0 | 9,999,986.8 | — | P=2 |
| 5 | JUMPZ R2,2 | 1 | 9,999,986.8 | 9,999,985.8 | 9,999,985.6 | — | Loop continues |
| ... | (repeat for P=3,4,5) | | | | | | |
| 12* | COPY_UNIT | 2 | — | — | — | — | P=6 (done), R2=1 |
| 13 | JUMPZ R2,2 | 1 | — | — | — | — | R2=1 → fall through |
| 14 | DIVIDE | 5 | — | — | — | 50% transfer | |
| 15 | JUMP 0 | 1 | — | — | — | — | |

*Exact tick depends on how many COPY_UNIT + JUMPZ pairs execute.

**Total cycle cost (L=6):**
- MOV: 1 + 0.2 (upkeep) = 1.2
- ALLOC_OFFSPRING: 6 + 0.2 = 6.2
- Copy loop: 6 × (2 + 1 + 0.2 + 0.2) = 6 × 3.4 = 20.4
- Exit JUMPZ: 1 + 0.2 = 1.2
- DIVIDE: 5 + 0.2 = 5.2
- JUMP 0: 1 + 0.2 = 1.2
- **Total: ~35.4 units**

After DIVIDE transfer: R' = 0.5 × (R − 35.4)
Generational depth: log₂(R₀ / 19) ≈ 19 generations. Similar to the atomic REPRODUCE case.

### 2b. Generational Depth

```
R_{n+1} = 0.5 × (R_n - 35.4)
```

| Gen | R start | After cycle | Offspring R |
|-----|---------|-------------|-------------|
| 0 | 10,000,000.0 | 4,999,982.3 | 4,999,982.3 |
| 1 | 4,999,982.3 | 2,499,973.5 | 2,499,973.5 |
| ... | ... | ... | ... |
| 17 | 76.3 | 20.5 | 20.5 |
| 18 | 20.5 | < 19 | — (cannot reproduce) |

**Depth: ~18 generations.** Consistent with the Stage 3 empirical measurement using atomic REPRODUCE.

---

## 3. Viable Band

**L_min = 6** (the 6-instruction replicator above). No shorter genome can implement the copy loop.

**Upper bound** is determined by the resource constraint:

For a genome of length L, the copy loop runs L times:
```
cycle_cost = 1.2 + 6.2 + L × 3.4 + 1.2 + 5.2 + 1.2
           = 15.0 + 3.4 × L
```

After DIVIDE transfer: R' = 0.5 × (R − 15.0 − 3.4 × L)

Parent survives the full cycle if: 0.5 × (R − 15.0 − 3.4L) − 0.2 > 0
→ R > 15.4 + 3.4L

For L=6: R > 15.4 + 20.4 = 35.8 → minimum viable reserve ≈ 36 units.

For the ancestor (R=10M): L < (10M − 15.4) / 3.4 ≈ 2,940,000. Effectively no upper bound from resources.

**Mutation load** is still negligible (as shown in Stage 1B). The copy loop runs L times per generation, and substitution mutations occur at 0.001 per instruction per copy. But the loop itself is a target for mutation: a substitution in COPY_UNIT might copy faster or slower; a substitution in JUMPZ might change the exit condition. This creates evolvable variation that didn't exist with atomic REPRODUCE.

---

## 4. Ecological Implications

| Property | Atomic REPRODUCE | Composite REPRODUCE |
|----------|-----------------|---------------------|
| L_min | 2 | 6 |
| Copy loop in genome? | No | Yes (2 instructions) |
| Parasitism expressible? | No | Yes (hijack COPY_UNIT) |
| Error correction evolvable? | No | Yes (on copy loop) |
| Genome length cost | Fixed (2 × L) | Variable (3.4 per L per cycle) |
| Mutation target for copy machinery | None | COPY_UNIT, JUMPZ can mutate |