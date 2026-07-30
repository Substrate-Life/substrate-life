# Substrate — Revised Reproduction and Instruction Set

*Decomposing REPRODUCE into primitives: ALLOC_OFFSPRING, COPY_UNIT, DIVIDE.*

---

## 1. Motivation

Atomic REPRODUCE collapses L_min to 2 and eliminates the copy loop. In both Tierra and Avida, the copy loop was where a large share of interesting evolution happened: parasites evolved by hijacking a host's copy machinery, error-correction strategies emerged on the copy loop, and genome length mattered because copying cost scaled with what had to be copied. With REPRODUCE as a single instruction, none of these dynamics are expressible.

---

## 2. New Instructions

### 2a. ALLOC_OFFSPRING

Allocates space for a future offspring within the parent's working memory. Does not create a separate organism yet; it merely reserves a "gestation region."

```
ALLOC_OFFSPRING R0       # R0 = size to allocate (in bytes)
```

**Cost:** 5 + (size / 64) instruction units.
**Effect:**
- Allocates a block of `R0` bytes in the parent's working memory (or a default minimum of 64 bytes if R0 = 0).
- Stores the start address of the gestation region in register R1.
- Sets the internal byte-copy pointer P to 0 (pointing to genome position 0).
- The gestation region is part of the parent's working memory until DIVIDE is called.
- If insufficient memory is available, the FAIL flag is set and R1 is set to 0.

### 2b. COPY_UNIT

Copies one unit (instruction word) from the parent's genome to the gestation region.

```
COPY_UNIT                # no explicit operands; uses internal pointers
```

**Cost:** 2 instruction units.
**Effect:**
- Reads the instruction at genome position P (where P is the internal copy pointer).
- Writes that instruction into the gestation region at the current write position.
- Increments P by 1.
- Increments the internal write pointer by the instruction word size.
- If P >= genome_length, the COPY_UNIT succeeds but the FAIL flag is set (indicating the entire genome has been copied — the organism should proceed to DIVIDE).
- If no gestation region has been allocated (R1 = 0), the FAIL flag is set and no copy occurs.

**Note:** COPY_UNIT copies the instruction as data, not by executing it. Mutations (substitutions, insertions, deletions, duplications) are applied during DIVIDE, not during COPY_UNIT.

### 2c. DIVIDE

Finalises reproduction: applies mutations, creates the offspring organism, separates it from the parent.

```
DIVIDE                   # no explicit operands
```

**Cost:** 5 instruction units.
**Effect:**
1. Checks that a gestation region exists (R1 ≠ 0) and that at least one instruction was copied (P > 0).
2. Copies the contents of the gestation region to form the offspring's genome.
3. **Applies mutations:** substitutions (per-instruction), then insertions, deletions, and duplications (per-genome).
4. Creates a new organism structure with:
   - The mutated genome
   - Registers zeroed, PC = 0, stack empty
   - Working memory: minimum block (64 bytes) from the shared memory pool
   - Execution reserve: **50% of the parent's current reserve** (transferred)
   - State: ACTIVE
5. Frees the gestation region (returns memory to the shared pool).
6. Resets R1 to 0 and P to 0.
7. The offspring is added to the scheduler queue for the next tick.

**Failure conditions:** If no gestation region exists or no instructions were copied, DIVIDE is a no-op. The FAIL flag is set. The cost is still paid.

---

## 3. Minimal Replicator

With decomposed reproduction, the minimal genome that can sustain self-replication is longer than 2 instructions. It must:

1. ALLOC_OFFSPRING — allocate space for the offspring
2. LOAD genome length into a register (to know when copying is done)
3. CMP — compare copy counter with genome length
4. JUMPNZ — if not done, go to COPY_UNIT
5. COPY_UNIT — copy one instruction
6. ADD — increment copy counter
7. JUMP — loop back to CMP
8. DIVIDE — finalise offspring
9. JUMP — loop back to start

**Revised minimal replicator (9 instructions, L=9):**

```
Address  Instruction         Notes
0        MOV R0, 64          Offspring memory size (minimum block)
1        ALLOC_OFFSPRING R0  Allocate gestation region
2        MOV R1, 0           Clear copy counter
3        CMP R1, 9           Compare counter with genome length (L=9)
4        JUMPZ 7             If done, go to DIVIDE
5        COPY_UNIT           Copy one instruction
6        ADD R1, 1           Increment counter
7        JUMP 3              Loop back to CMP
8        DIVIDE              Finalise offspring
9        JUMP 0              Loop back to start
```

Wait — this has a problem. The genome includes the COPY_UNIT instruction, which needs to be copied. But when COPY_UNIT executes, it reads the instruction at genome position P. If the counter isn't tracking which instruction to copy...

Let me reconsider. The COPY_UNIT instruction uses an internal pointer P that advances automatically each time COPY_UNIT is called. The organism doesn't need a separate counter — it just calls COPY_UNIT repeatedly until P >= genome_length, at which point COPY_UNIT sets the FAIL flag.

**Simplified minimal replicator (5 instructions, L=5):**

```
Address  Instruction         Notes
0        MOV R0, 64          Offspring memory size
1        ALLOC_OFFSPRING R0  Allocate gestation region
2        COPY_UNIT           Copy one instruction (P increments automatically)
3        JUMPNZ 2            If FAIL flag not set (copy still in progress), loop
4        DIVIDE              Finalise offspring
5        JUMP 0              Loop back to start
```

But wait — JUMPNZ checks a REGISTER, not the FAIL flag. Let me re-think. The FAIL flag is set by COPY_UNIT when P >= genome_length. But the organism can't check the FAIL flag directly with JUMPNZ (which checks a register).

Alternative: COPY_UNIT returns the value of P in a register after each call. When P >= genome_length, the FAIL flag is set AND register R2 is set to 1.

Hmm, this is getting complicated. Let me simplify further. Maybe COPY_UNIT sets a status register.

Actually, the simplest approach: COPY_UNIT copies one instruction per tick. The internal pointer P starts at 0 and increments each time. When P >= genome_length, the next COPY_UNIT sets the FAIL flag. The organism checks the FAIL flag via a JUMPZ/JUMPNZ on a flag register.

Let me add a flag register. Or better: after COPY_UNIT completes and P >= genome_length, register R2 is set to 1. The organism checks R2.

**Even simpler:** COPY_UNIT outputs to R2: 0 if more to copy, 1 if done.

**Revised minimal replicator (6 instructions, L=6):**

```
Address  Instruction         Notes
0        MOV R0, 64          Offspring memory size
1        ALLOC_OFFSPRING R0  Allocate gestation region
2        COPY_UNIT           Copy one instruction; sets R2=1 when done
3        JUMPZ 2             If R2=0 (not done), continue copying
4        DIVIDE              Finalise offspring
5        JUMP 0              Loop back to start
```

Wait, JUMPZ checks R2. If R2=0 (not done), JUMPZ jumps to address 2 (COPY_UNIT). If R2=1 (done), JUMPZ falls through to DIVIDE. This works!

But JUMPZ takes (register, target). So:
- `COPY_UNIT` — copies one instruction, returns R2=0 if more, R2=1 if done
- `JUMPZ R2, 2` — if R2=0, jump to address 2 (COPY_UNIT); if R2=1, continue
- `DIVIDE` — finalises
- `JUMP 0` — loop

That's 6 instructions. L_min = 6. The copy loop is 2 instructions (COPY_UNIT, JUMPZ) which is exactly the kind of compact loop that can be parasitised, optimised, or broken by mutation.

Let me also compute the per-cycle cost for this 6-instruction genome.

Cycle (excluding DIVIDE for a moment):
- Tick 0: MOV R0, 64 (cost 1)
- Tick 1: ALLOC_OFFSPRING R0 (cost 5 + 1 = 6)
- Tick 2: COPY_UNIT (cost 2) — copies instruction 0
- Tick 3: JUMPZ R2, 2 — R2=0, jump to 2 (cost 1)
- Tick 4: COPY_UNIT (cost 2) — copies instruction 1
- Tick 5: JUMPZ R2, 2 — R2=0, jump (1)
- ...repeat 6 times for 6 instructions...
- After 6 COPY_UNITs: P=6, R2=1
- Tick N: JUMPZ R2, 2 — R2=1, fall through (cost 1)
- Tick N+1: DIVIDE (cost 5)
- Tick N+2: JUMP 0 (cost 1)
- Transfer 50% of parent's remaining reserve

Total: 6 (first MOV+ALLOC) + 6 × (2+1) (copy loop) + 1 (exit JUMPZ) + 5 (DIVIDE) + 1 (JUMP 0) = 6 + 18 + 1 + 5 + 1 = 31 instruction cost + upkeep (let's say ~12 ticks × 0.2 = 2.4) ≈ 33.4 units per cycle.

With 50% transfer: R_after = 0.5 × (R_before - 33.4). Generational depth ≈ log2(R₀/19) ≈ 19. Similar to before!

Actually the cycle is longer but the cost per cycle is higher too. Let me compute properly in the next section.