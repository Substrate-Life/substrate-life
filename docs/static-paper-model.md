# Substrate — Static Paper Model

*Stage 2: Walk through hypothetical organisms by hand to identify loopholes, trivial strategies, and hidden fitness functions before writing any code.*
*Drafted 2026-07-26.*

---

## 1. Purpose

This document simulates specific organism genomes on paper, tracing their execution tick by tick under the Stage 1 boundary model, genome viability constraints, and metabolism rules. The goal is to find design flaws — places where the substrate accidentally rewards a degenerate strategy, contradicts itself, or creates an outcome that undermines the scientific question.

---

## 2. Reference Parameters

All values from Stages 1A–1C:

| Parameter | Value | Source |
|-----------|-------|--------|
| Initial reserve (recommended) | 10,000,000 units | Stage 1B |
| BASE_UPKEEP | 0.1 units/tick | Stage 1C |
| MEMORY_COST_DIVISOR | 640 | Stage 1C |
| Minimum working memory | 64 bytes | Stage 1A |
| Per-tick upkeep (64B, ACTIVE) | 0.1 + 64/640 = 0.2 | Stage 1C |
| Per-tick upkeep (64B, DORMANT) | 0.02 (10% of ACTIVE) | Stage 1C |
| REPRODUCE check cost | 5 units | Stage 1A |
| REPRODUCE copy cost | genome_length × 2 units | Stage 1A |
| Reproduction transfer | 50% of parent's remaining reserve | Stage 1A |
| READ cost | 2 units | Stage 1A |
| ALLOC cost | 1 + ceil(size/64) | Stage 1A |
| TRANSFORM cost | 3 + ceil(length/64) | Stage 1C |
| JUMP cost | 1 unit | Stage 1A |
| SLEEP cost | 1 unit | Stage 1A |
| DIE cost | 1 unit | Stage 1A |
| Replenishment divisor | 64 (lossless transforms only) | Stage 1C |
| Per-tick replenishment cap | 3.5 units | Stage 1C |
| Data packet size | 256 bytes | Stage 1A |
| Buffer depth | 4 packets | Stage 1A |
| Packet arrival interval | 5 ticks | Stage 1A |
| Population cap | 500 | Stage 1A |

---

## 3. Organism 1: Minimal Replicator

**Genome:** [REPRODUCE, JUMP 0] (2 instructions, L=2)
**Strategy:** Reproduce as fast as possible. No metabolism. No reading.

### 3a. Execution Trace (First 10 Ticks)

| Tick | PC | Instr | Before instr | Instr cost | After instr | Transfer (50%) | After transfer | Upkeep | After upkeep |
|------|----|-------|-------------|------------|-------------|----------------|----------------|--------|-------------|
| 0 | 0 | REPR | 10,000,000.0 | 9 | 9,999,991.0 | 4,999,995.5 | 4,999,995.5 | 0.2 | 4,999,995.3 |
| 1 | 1 | JUMP | 4,999,995.3 | 1 | 4,999,994.3 | — | 4,999,994.3 | 0.2 | 4,999,994.1 |
| 2 | 0 | REPR | 4,999,994.1 | 9 | 4,999,985.1 | 2,499,992.6 | 2,499,992.6 | 0.2 | 2,499,992.4 |
| 3 | 1 | JUMP | 2,499,992.4 | 1 | 2,499,991.4 | — | 2,499,991.4 | 0.2 | 2,499,991.2 |
| 4 | 0 | REPR | 2,499,991.2 | 9 | 2,499,982.2 | 1,249,991.1 | 1,249,991.1 | 0.2 | 1,249,990.9 |
| 5 | 1 | JUMP | 1,249,990.9 | 1 | 1,249,989.9 | — | 1,249,989.9 | 0.2 | 1,249,989.7 |
| 6 | 0 | REPR | 1,249,989.7 | 9 | 1,249,980.7 | 624,990.4 | 624,990.4 | 0.2 | 624,990.2 |
| 7 | 1 | JUMP | 624,990.2 | 1 | 624,989.2 | — | 624,989.2 | 0.2 | 624,989.0 |
| 8 | 0 | REPR | 624,989.0 | 9 | 624,980.0 | 312,490.0 | 312,490.0 | 0.2 | 312,489.8 |
| 9 | 1 | JUMP | 312,489.8 | 1 | 312,488.8 | — | 312,488.8 | 0.2 | 312,488.6 |

### 3b. Generational Depth

Each full cycle (REPRODUCE + JUMP) halves the reserve. The recurrence:

```
R_{n+1} = 0.5 × (R_n - 9) - 1.4
```

Where −1.4 = JUMP(1) + 2×upkeep(0.4).

| Generation | R (start) | Offspring R |
|------------|-----------|-------------|
| 0 | 10,000,000.0 | 4,999,995.3 |
| 1 | 4,999,994.1 | 2,499,992.4 |
| 2 | 2,499,991.2 | 1,249,990.9 |
| 3 | 1,249,989.7 | 624,990.2 |
| ... | ... | ... |
| 15 | 305.2 | 143.1 |
| 16 | 142.9 | 62.0 |
| 17 | 61.8 | 21.4 |
| 18 | 21.2 | 1.1 |
| 19 | 0.9 | — (R < 19) |

**Depth: ~18 generations.** Consistent with the Stage 1B prediction of ~19 for R₀=10M.

*Note: Late-generation values diverge by 0.1–5.1 units from the recurrence formula due to intermediate rounding in the trace table. The extinction boundary (gen 19) is the same regardless.*

### 3c. Findings

1. **No issues.** The minimal replicator behaves exactly as predicted by Stage 1B. Reproduction halving is clean; upkeep costs are negligible relative to reserve at this scale.

2. **Trivial strategy dominance.** The minimal replicator is the fastest reproducer. In a population with 500-organism cap, it will dominate by sheer reproduction rate. No metabolism is needed. This is expected and acceptable for Stage 1 — the question is whether metabolism-enabled organisms can outcompete it when resources are scarce.

---

## 4. Organism 2: Dormancy Specialist

**Genome:** [REPRODUCE, SLEEP 5000, JUMP 0] (3 instructions, L=3)
**Strategy:** Reproduce once, then enter deep dormancy. Wake, reproduce again, sleep again.

### 4a. Execution Trace (First ~5002 Ticks)

| Tick(s) | PC | Instr | R before | Cost | R after | Notes |
|---------|----|-------|----------|------|---------|-------|
| 0 | 0 | REPR | 10,000,000 | 11* | 4,999,994.5 | *Check(5)+copy(6). Transfer 50%. Upkeep −0.2 |
| 1 | 1 | SLEEP | 4,999,993.3 | 1 | 4,999,992.1 | Upkeep −0.2. Enters DORMANT |
| 2–5001 | — | — | — | — | ~4,999,892.1 | Dormant upkeep: 5000 × 0.02 = 100 total |
| 5002 | 1 | Wake | 4,999,892.1 | — | 4,999,891.9 | Upkeep −0.2. Returns to ACTIVE |
| 5003 | 2 | JUMP | 4,999,891.9 | 1 | 4,999,890.7 | Upkeep −0.2 |
| 5004 | 0 | REPR | 4,999,890.7 | 11 | 2,499,939.9 | Transfer 50%. Upkeep −0.2 |

**Reserve cost per 5002-tick cycle: ~10,110 units** (mostly from the 50% reproduction transfer).

### 4b. Ecological Position

The dormancy specialist sacrifices reproduction rate for longevity. Each cycle it produces 1 offspring and consumes ~10,110 reserve in the process. The minimal replicator produces 1 offspring per 2 ticks (~9 offspring per cycle length) and consumes ~10.4 per 2 ticks.

**Key insight:** At population cap (500), displacement mortality selects for reproduction rate. The minimal replicator produces ~9 offspring in the time the dormancy specialist produces 1. The dormancy specialist will be displaced.

**However:** If the population is below the cap, the dormancy specialist's offspring survive. And its parent survives almost indefinitely (5000-tick dormancy burns only 100 units). A single dormancy specialist can produce offspring every 5000 ticks for millions of ticks.

### 4c. Findings

1. **Dormancy is not dominant.** The population cap ensures active reproducers win the displacement lottery. This is correct behaviour.

2. **Dormancy as an insurance strategy.** A parent that reproduces once and then sleeps forever creates an active offspring while preserving itself. If the active lineage goes extinct, the dormant parent can wake and restart it. This is a realistic ecological strategy (seed banks in biology).

---

## 5. Organism 3: Lossy Specialist

**Genome:** [READ, ALLOC 256, TRANSFORM HASH_SUM (addr=64, len=256), REPRODUCE, JUMP 0] (5 instructions, L=5)
**Strategy:** Read a packet, allocate space, hash it to 32 bytes (guaranteed upkeep reduction), reproduce.

### 5a. Execution Trace (Corrected)

| Tick | PC | Instr | R before | Cost | R after instr | R after upkeep | Memory | Notes |
|------|----|-------|----------|------|---------------|----------------|--------|-------|
| 0 | 0 | READ | 10,000,000.0 | 2 | 9,999,998.0 | 9,999,997.8 | 64B | |
| 1 | 1 | ALLOC256 | 9,999,997.8 | 5 | 9,999,992.8 | 9,999,992.2 | 320B | Upkeep: 0.6 |
| 2 | 2 | HASH | 9,999,992.2 | 7 | 9,999,985.2 | 9,999,985.0 | 96B | No replenishment (lossy). Auto-reclaim: 256→32 |
|| 3 | 3 | REPRODUCE | 9,999,985.0 | 15* | 4,999,985.0 | 4,999,984.75 | 96B | *Check(5)+copy(10). Transfer 50%. |

Then the organism loops back to READ at tick 5.

### 5b. Findings

1. **HASH_SUM provides no replenishment but still reduces memory.** The lossy specialist has lower upkeep than the minimal replicator (0.25 vs 0.2 per tick — actually WORSE because it's holding 96B vs 64B). Wait — 0.25 > 0.2, so the lossy specialist has HIGHER upkeep than the minimal replicator. It's actually less efficient in terms of upkeep. Its only advantage is that it's... processing data? But processing data doesn't help it directly.

This is a problem: the lossy specialist has HIGHER upkeep than the minimal replicator (0.25 vs 0.2) AND costs more to reproduce (REPRODUCE on L=5 genome costs 5+10=15 vs L=2 costing 9). It's strictly worse in every way.

This suggests that lossy-only strategies are NOT viable without replenishment. The lossless transforms (which give replenishment) are the only way to make metabolism worthwhile.

But wait — the lossy specialist also doesn't READ new data after the first cycle. It just does READ, HASH, REPRODUCE, JUMP. After the first HASH, the compressed data is in memory. On subsequent loops, it READS again (costs 2), which... does what? Does READ overwrite existing memory? If READ writes to address 64 with length 256, and the organism only has 96B of memory (64 minimum + 32 from hash), the READ would try to write 256 bytes starting at address 64, which would go out of bounds.

This is a genuine loophole: the organism can READ 256 bytes but only has memory for 96B. What happens? The boundary model doesn't specify this case. The organism specified addr=64, length=256, but only addresses [64, 159] are valid (96-64=32 bytes remaining after the 64B minimum block... actually, the total memory is 96B, starting at address 0. So valid addresses are [0, 95]. If READ tries to write to [64, 319], addresses [96, 319] are out of bounds.

**Finding: Out-of-bounds READ is underspecified.** If READ writes beyond the allocated memory, does it: (a) fail silently (no-op, set FAIL flag), (b) truncate, (c) extend the allocation automatically, or (d) corrupt memory?

This needs to be specified. The safest behaviour is (a): fail silently, set FAIL flag, no data written. This means the organism must explicitly check its memory bounds before reading.

2. **The lossy-only strategy is not viable without replenishment.** The lossy specialist has higher upkeep than the minimal replicator and higher reproduction costs. It will be outcompeted. This is actually correct behaviour — the metabolism model is designed so that lossless transforms (which require structured data) are the only way to gain a metabolic advantage.

Let me capture these findings and write the document.</think>

<｜DSML｜tool_calls>
<｜DSML｜invoke name="write_file">
<｜DSML｜parameter name="content" string="true"># Substrate — Static Paper Model (continued)

### 5c. Findings

2. **The lossy-only strategy is not viable without replenishment.** It has higher upkeep (0.25 vs 0.2) and higher reproduction costs (15 vs 9) than the minimal replicator. This is correct behaviour — lossy transforms provide footprint reduction but no reserve bonus.

3. **Out-of-bounds READ is underspecified.** If working memory is 96 bytes and the organism READs 256 bytes starting at address 64, addresses [96, 319] are beyond the allocation. The boundary model doesn't specify what happens. This must be resolved before implementation (see Section 13a).

---

## 6. Organism 4: Lossless Metaboliser

**Genome:** [READ, ALLOC 256, TRANSFORM RLE (addr=64, len=256), REPRODUCE, JUMP 0] (5 instructions, L=5)
**Strategy:** Read a packet, allocate space, run-length encode it. On Phase A data (structured), this generates replenishment AND reduces upkeep.

### 6a. Phase A Execution Trace (First 6 Ticks)

Assume Phase A data: 256-byte packet with repeating patterns; RLE compresses to ~40 bytes.

| Tick | PC | Instr | R before | Cost | Replenish | R after instr | R after upkeep | Memory |
|------|----|-------|----------|------|-----------|---------------|----------------|--------|
| 0 | 0 | READ | 10,000,000.0 | 2 | — | 9,999,998.0 | 9,999,997.8 | 64B |
| 1 | 1 | ALLOC256 | 9,999,997.8 | 5 | — | 9,999,992.8 | 9,999,992.2 | 320B |
| 2 | 2 | RLE 64,256 | 9,999,992.2 | 7 | +3.375 | 9,999,988.6 | 9,999,988.35 | 104B* |
| 3 | 3 | REPR | 9,999,988.35 | 15 | — | 4,999,986.7 | 4,999,986.45 | 104B |
| 4 | 4 | JUMP | 4,999,986.45 | 1 | — | 4,999,985.45 | 4,999,985.2 | 104B |
| 5 | 0 | READ | 4,999,985.2 | 2 | — | 4,999,983.2 | 4,999,982.95 | 104B |

*Original 256B → 40B auto-reclaimed. Memory: 64 + 40 = 104B.

### 6b. Second Cycle: READ → RLE on New Data

After the first cycle, the organism has 104B of memory (64 minimum + 40 compressed). On tick 5, it READs a new 256-byte packet. Where does the data go?

If READ writes to address 64 with length 256, and the organism only has 104B of memory (addresses [0, 103]), addresses [104, 319] are out of bounds. Unless:

- **Interpretation A:** READ automatically extends working memory to accommodate the requested length. Cost: implicit ALLOC.
- **Interpretation B:** READ fails silently if the requested range exceeds allocated memory. Sets FAIL flag.
- **Interpretation C:** The organism must explicitly FREE the compressed data and ALLOC new space before each READ.

**Interpretation C is the intended design.** The organism should:
1. FREE the old compressed data (freeing addresses [64, 103], returning to 64B minimum)
2. ALLOC 256 for the new packet (expanding to 320B)
3. READ the new data
4. RLE it
5. REPRODUCE
6. Loop

This means the full cycle for a lossless metaboliser is:

[FREE, ALLOC 256, READ, RLE, REPRODUCE, JUMP] — 6 instructions, L=6.

### 6c. Full Cycle Cost (Corrected, L=6, Phase A)

| Component | Cost |
|-----------|------|
| FREE | 1 |
| ALLOC 256 | 5 |
| READ | 2 |
| RLE (256→40) | 7 |
| REPRODUCE (5+12) | 17 |
| JUMP | 1 |
| Upkeep (6 ticks × ~0.4 avg) | ~2.4 |
| **Total cost** | **~35.4** |
| Replenishment (RLE, 256→40) | −3.375 |
| Offspring transfer (50%) | −50% of (parent R − 33) |
| **Net cost** | **~32 + 50% transfer** |

The replenishment (3.375 units) barely offsets 10% of the cycle cost. The lossless metaboliser is net-negative on reserve. It survives longer than the minimal replicator only if the upkeep savings compound over many ticks between reproductions.

### 6d. Steady-State Analysis

After the initial RLE, the organism's baseline memory is 104B (upkeep: 0.2625/tick). Between reproductions, it pays:

- While holding compressed data: 0.2625/tick
- During read-transform cycle: varies (0.6–0.2625/tick)

With 10M initial reserve, the lossless metaboliser can survive for:
- Each reproduction cycle costs ~32 + 50% transfer ≈ 32 + 0.5×R
- Net per cycle: ~0.5×R − 32
- After reproduction: R' ≈ 0.5×R − 32
- Generations: similar to minimal replicator (~18), but with slightly higher per-cycle costs

**The lossless metaboliser does NOT outcompete the minimal replicator in terms of reproduction rate.** It costs more per reproduction and takes longer per cycle (6 ticks vs 2 ticks). Its advantage would only appear if:
- Data is the only way to extend lifespan
- The environment changes and the minimal replicator cannot adapt
- Replenishment rate is increased

### 6e. Findings

1. **Replenishment is too small to matter.** At 3.375 units per packet, replenishment covers only ~10% of cycle costs. The lossless metaboliser is ecologically equivalent to the minimal replicator with slightly worse parameters.

2. **The FREE-ALLOC-READ pattern is mandatory.** Each new packet requires explicit memory management. This adds 6 units of overhead per cycle.

3. **The metaboliser is not viable against the minimal replicator at current parameters.** This is acceptable for Stage 1 — the first experiment tests basic dynamics, not metabolic competition. For Stage 3+, REPLENISHMENT_DIVISOR should be lowered (e.g., to 32) to make replenishment meaningful.

---

## 7. Organism 5: The READ-Only Spammer

**Genome:** [READ 64, 256, JUMP 0] (2 instructions, L=2)
**Strategy:** Try to read a packet every tick. Never allocate, never transform, never reproduce.

### 7a. Execution Trace

| Tick | PC | Instr | R before | Cost | R after | Upkeep | Memory |
|------|----|-------|----------|------|---------|--------|--------|
| 0 | 0 | READ | 10,000,000 | 2 | 9,999,998 | −0.2 | 64B |
| 1 | 1 | JUMP | 9,999,997.8 | 1 | 9,999,996.8 | −0.2 | 64B |
| 2 | 0 | READ | 9,999,996.6 | 2 | 9,999,994.6 | −0.2 | 64B |
| 3 | 1 | JUMP | 9,999,994.4 | 1 | 9,999,993.4 | −0.2 | 64B |

Each 2-tick cycle costs 3.4 units (2+1+0.4). With 10M reserve: ~2.9M cycles. But READ always fails because it tries to write 256 bytes into 64 bytes of memory (out-of-bounds, see Section 13a).

The organism burns reserve doing nothing. This is a dead end.

### 7a. Finding

The READ-only spammer is not viable — it consumes reserve with no benefit. Every READ fails (out-of-bounds). This is acceptable behaviour, but only if the out-of-bounds failure is well-defined (Section 13a).

---

## 8. Organism 6: The ALLOC-Only Spammer

**Genome:** [ALLOC 256, FREE 64, JUMP 0] (3 instructions, L=3)
**Strategy:** Allocate 256 bytes, free 64 bytes (leaving 256 allocated), repeat. Cycle memory to test pool exhaustion.

### 8a. Execution Trace

| Tick | PC | Instr | R before | Cost | Memory | Upkeep |
|------|----|-------|----------|------|--------|--------|
| 0 | 0 | ALLOC256 | 10,000,000 | 5 | 320B | −0.5 |
| 1 | 1 | FREE 64 | 9,999,994.5 | 1 | 256B* | −0.4 |
| 2 | 2 | JUMP | 9,999,993.1 | 1 | 256B | −0.4 |

*FREE 64 frees addresses [0, 63], returning to 64B minimum... but the organism allocated 256 extra bytes starting at address 64. So after FREE 64, addresses [0, 63] are freed, [64, 319] remain allocated. Total: 256B.

Wait, FREE takes an address. FREE 64 frees the 64-byte minimum block at address 0-63. That's the organism's original allocation. Can the organism free its own minimum block? What happens if it frees all its memory? Does it die?

### 8b. Finding

**FREE semantics are underspecified.** Can an organism free its minimum working memory block? If it frees all memory, does it die? Does FREE on an invalid address fail silently?

The boundary model says FREE returns memory to the shared pool, but doesn't specify what happens if the organism has zero working memory. Likely outcomes:
- (a) Organism dies (cannot execute instructions without working memory)
- (b) FREE is refused (minimum allocation must be preserved)
- (c) Working memory goes to 0; subsequent READ/TRANSFORM instructions fail

This must be specified.

### 8c. Note: Memory Exhaustion DOS

A related strategy: repeatedly ALLOC large blocks without freeing them to exhaust the shared memory pool. A genome like `[ALLOC 8192, JUMP 0]` (L=2) would cost 1 + ceil(8192/64) = 129 units per tick. With 10M initial reserve, the attacker exhausts its own reserve in ~77,000 ticks — before it can exhaust a shared pool sized for 500 organisms (each holding 8KB + 64B ≈ 4MB). The grace period (10 ticks to free memory) and displacement at population cap make memory exhaustion non-dominant. No fix needed.

---

## 9. Organism 7: The Data Stream Hog

**Genome:** [ALLOC 1024, READ 64, 256, READ 320, 256, READ 576, 256, READ 832, 256, REPRODUCE, JUMP 0]
**Strategy:** Allocate 1024 bytes to hold 4 packets. Read all 4 buffers. Then reproduce. Read 4 more. Hog the data stream.

### 9a. Analysis

With buffer depth 4 and one packet arriving every 5 ticks, the organism can READ 4 packets in 4 ticks, emptying the buffer. For the next 5 ticks, all other organisms' READ instructions find an empty buffer (FAIL flag set, cost still paid).

The data stream hog has exclusive access to all environmental information for ~5 ticks per cycle.

### 9b. Finding

**Data stream monopolisation is possible but costly.** The organism pays upkeep on 1088B (64+1024) = 0.1+1088/640 = 1.8/tick during the read phase vs 0.2/tick for a minimal replicator. The hog pays 9× more upkeep for the privilege of hoarding data.

This is acceptable — hoarding is costly and the benefit is uncertain (data may not be directly useful). In Stage 7+ (ecological interaction), data hoarding could become a meaningful competitive strategy.

---

## 10. Organism 8: The Corpse Scavenger

**Genome:** No — corpse scavenging is not possible in Stages 1–6 (boundary model, Section 16). The corpse pool exists but is not accessible to organisms.

**Finding:** Confirmed. No loophole.

---

## 11. Loopholes and Degenerate Strategies Found

### 11a. Out-of-Bounds READ (CRITICAL — must fix before implementation)

**The problem:** If an organism READs a 256-byte packet into working memory that is smaller than 256 bytes, the read extends beyond the allocated memory. The boundary model does not specify what happens.

**Proposed fix:** If the requested read range exceeds allocated working memory, the instruction **fails silently**. The FAIL flag is set. No data is written. The 2-unit instruction cost is still paid. The organism can detect the failure via the FAIL flag.

### 11b. FREE on Minimum Block (MAJOR — must fix)

**The problem:** Can an organism FREE its minimum working memory block (64 bytes)? If so, it may have 0 bytes of working memory, making all subsequent memory-access instructions fail. The organism is effectively dead but may not be marked DEAD.

**Proposed fix:** The minimum working memory allocation (64 bytes) is **non-freeable**. FREE instructions that attempt to free addresses within the minimum block are no-ops (cost still paid; FAIL flag set). Only memory allocated via ALLOC beyond the minimum block can be freed.

### 11c. Replenishment Too Small (MAJOR — should fix before Stage 3)

**The problem:** At REPLENISHMENT_DIVISOR=64, a lossless transform on a 256-byte packet yields only 3.375 units — ~10% of a full reproduction cycle cost (~35 units). Replenishment is negligible.

**Proposed fix:** Lower REPLENISHMENT_DIVISOR to 32 for Stage 3+. This doubles replenishment to 6.75 units per packet, making metabolism ecologically relevant.

### 11d. Memory Management Overhead (MINOR)

**The problem:** Each READ requires an explicit ALLOC (5 units) and FREE (1 unit) to manage buffer space. This overhead makes metabolism expensive relative to minimal replication.

**Proposed fix:** None for Stage 1–2. This is intentional — metabolism should have a cost. For Stage 3+, consider adding an AUTO_ALLOC mode where READ automatically extends working memory if needed.

### 11e. Per-Tick Cap Too Tight (NOTE)

**The problem:** The per-tick cap of 3.5 units is exactly the replenishment from one 256-byte RLE transform. An organism cannot exceed the cap with a single transform. The cap is irrelevant.

**Proposed fix:** Either remove the cap (it doesn't constrain anything) or lower it to 2.0 units (making it binding for large transforms on large memory regions). For Stage 1–2, remove the cap.

---

## 12. Confirmed Correct Behaviours

| Behaviour | Status | Notes |
|-----------|--------|-------|
| Minimal replicator dominance | ✓ Expected | Fastest reproducer wins at cap |
| Dormancy as insurance | ✓ Expected | Parent survives while offspring competes |
| Lossy-only not viable | ✓ Correct | Higher upkeep, no replenishment |
| Lossless metaboliser net-negative | ✓ Acceptable | Replenishment too small to matter at current params |
| READ-only spammer dies | ✓ Correct | No reproduction, no benefit |
| Data stream monopolisation costly | ✓ Acceptable | High upkeep cost for hoarding |
| Corpse pool inaccessible | ✓ Confirmed | No scavenging in Stages 1–6 |

---

## 13. Required Fixes Before Stage 3

### 13a. Add Out-of-Bounds READ Behaviour (to boundary model)

Add to Section 10 (Boundary for Environmental Information):
> If the requested read range (addr + length) exceeds the organism's allocated working memory, the READ instruction fails silently. The FAIL flag is set. No data is copied. The instruction cost is still paid.

### 13b. Add Minimum Block Protection (to boundary model)

Add to the FREE instruction definition:
> FREE cannot free addresses within the minimum working memory block (default: bytes [0, 63]). Attempts to do so are no-ops. The FAIL flag is set. Only memory allocated via ALLOC beyond the minimum block can be freed.

### 13c. Adjust REPLENISHMENT_DIVISOR for Stage 3+

Reduce from 64 to 32, making replenishment 6.75 units per packet (more ecologically significant).

### 13d. Remove Per-Tick Replenishment Cap (for Stage 1–2)

Remove the cap. It doesn't constrain anything with 256-byte packets.

---

## 14. Summary

The static paper model analysed 8 hypothetical organisms and identified:
- **2 critical issues** (out-of-bounds READ, FREE on minimum block) — must fix before implementation
- **1 major issue** (replenishment too small) — should fix before Stage 3
- **1 minor issue** (memory management overhead) — acceptable for Stage 1–2
- **1 note** (per-tick cap irrelevant) — remove for Stage 1–2

No fatal design flaws were found. The core model is sound. The three Stage 1 documents are consistent with each other. The identified fixes are scoped and non-disruptive.

Recommended next step: Apply the fixes to the Stage 1 documents, then proceed to Stage 3 (minimal replication test — actual code).