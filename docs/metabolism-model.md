# Substrate — Metabolism Model

*Stage 1C: Formal definition of the digital metabolism mechanism.*
*Drafted 2026-07-26.*

---

## 1. Purpose

This document defines how a Substrate organism sustains itself — the mechanism by which it converts environmental inputs into continued existence. Metabolism is the central design problem of the project: it must be rich enough to reward adaptation, but structured so that the substrate never judges whether the organism "did the right thing."

The metabolism model answers three questions:
1. **What costs must an organism pay to stay alive?** (upkeep)
2. **How can an organism reduce those costs?** (transforms)
3. **How can an organism acquire new execution capacity?** (replenishment)

Questions 1 and 2 were partially addressed in the boundary model. This document completes and formalises them, and resolves Question 3.

---

## 2. Guiding Principle

The project spec (Section 6) defines metabolism as:

> A sequence of transformations through which an organism converts accessible environmental inputs into the ability to maintain or reproduce itself.

This must be implemented without the substrate inspecting data *content* — only structure (size, compressibility, statistical properties). The rule of thumb: if the interpreter needs to know what a byte *means* to decide whether the organism succeeded, the design is wrong. If the interpreter only measures *byte size* before and after a transform, and the environment naturally contains structured data that shrinks under certain operations, the design is correct.

---

## 3. Cost Model (Formalised)

Every tick, each ACTIVE organism incurs:

```
upkeep = BASE_UPKEEP + memory_upkeep + persistent_upkeep
```

Where:
- `BASE_UPKEEP` = 0.1 units/tick (reduced from 1.0 per Stage 1B recommendation)
- `memory_upkeep` = working_memory_size / MEMORY_COST_DIVISOR
  - `MEMORY_COST_DIVISOR` = 640 (increased from 64 per Stage 1B recommendation)
- `persistent_upkeep` = persistent_store_size / PERSISTENT_COST_DIVISOR
  - `PERSISTENT_COST_DIVISOR` = 640
  - Persistent store is empty at birth; grows only via `STORE` instruction

DORMANT organisms pay upkeep at 10% of the ACTIVE rate.
SUSPENDED organisms pay no upkeep.

**Default minimum upkeep for an ACTIVE organism with 64-byte working memory:**
```
upkeep = 0.1 + 64/640 + 0 = 0.1 + 0.1 = 0.2 units/tick
```

This is 10× lower than the boundary model's original 2.0 units/tick, extending generational depth from ~5 to ~19 (as computed in Stage 1B).

---

## 4. Transform Instructions (Formalised)

Each transform instruction takes three operands:
- `op`: the transform operation code
- `addr`: starting address in working memory
- `length`: number of bytes to process

The substrate applies the transform mechanically. It never checks whether the output is "correct" or "meaningful" — it only measures the byte size of the result. If the result is smaller than the original, the organism may choose to keep the compressed version (reducing future upkeep). If the result is the same size or larger, the organism gains no upkeep benefit.

### 4a. Available Transforms

| Operation | Code | Description | Typical effect on structured data | Typical effect on random data |
|-----------|------|-------------|-----------------------------------|-------------------------------|
| COMPRESS_RLE | 0 | Run-length encode: replace repeated byte sequences with (count, byte) pairs | Significant compression for runs of identical bytes | No compression (expands by ~2×) |
| COMPRESS_DIFF | 1 | Store differences from preceding byte; run-length encode the differences | Good compression for smooth gradients, gradual changes | No compression |
| ENCODE_BASE | 2 | Re-encode with variable-length scheme: common byte values use fewer bits | Modest compression for biased distributions | No compression |
| FILTER_LOW | 3 | Keep only low 4 bits of each byte | Halves effective size (always 50% reduction) | Always 50% reduction (lossy) |
| HASH_SUM | 4 | Replace region with a fixed-size 32-byte hash | Irreversible; up to 32 bytes regardless of input size | Same (lossy; irreversible) |

**Key property:** COMPRESS_RLE, COMPRESS_DIFF, and ENCODE_BASE are *lossless* — the original data can be fully reconstructed from the compressed form. FILTER_LOW and HASH_SUM are *lossy* — information is permanently discarded.

**Why include lossy transforms?** A lossy transform that guarantees a fixed maximum output size (HASH_SUM → 32 bytes) is *always* beneficial for upkeep reduction, regardless of data content. This provides a guaranteed minimum metabolism strategy that any organism can discover. The trade-off is that lossy compression destroys information that might have been useful for other purposes (e.g., detecting environmental patterns, or passing data to offspring).

### 4b. Transform Cost

```
TRANSFORM cost = 3 + length / 64 (rounded up)
```

For a 64-byte region: cost = 3 + 1 = 4 units.
For a 256-byte region: cost = 3 + 4 = 7 units.

The cost is proportional to the region size, so applying transforms to large regions is expensive. An organism must balance the upfront cost of transforming against the ongoing upkeep savings.

### 4c. Keeping Transformed Data

After a transform, the working memory region contains the transformed output, written in-place starting at the original address. If the output is smaller than the input, the excess bytes are **automatically reclaimed** — the organism's working memory shrinks by (input_size − output_size) bytes, and the freed bytes are returned to the shared memory pool. No separate FREE instruction is needed.

The organism does not need to explicitly FREE the reclaimed space, and cannot access the freed bytes. If the output is the same size or larger than the input, working memory size is unchanged (the output may overwrite the input region but does not expand it).

If the organism writes new data over the old location (via WRITE or a subsequent READ), the old data is gone and the tracking for that byte address resets (the byte is now "fresh" for replenishment purposes).

If the organism transforms a 256-byte data packet with COMPRESS_RLE and the result is 40 bytes, the organism can:
- Discard the original and keep only the 40-byte compressed version (reducing future upkeep from 256/640 = 0.4 to 40/640 = 0.0625 per tick)
- Keep both the original and compressed version (paying upkeep on the larger)
- Keep neither (the transform was wasted)

The choice is encoded in the organism's instruction sequence — the substrate does not decide which version to keep. If the organism writes new data over the old location, the old data is gone.

---

## 5. Data Packet Structure (Formalised)

From the boundary model (Section 10a): data packets are 256-byte sequences generated by a deterministic PRNG with structured non-stationary phases. This section defines the exact packet generation algorithm.

### 5a. Abstract Mode (Default)

Packets are generated by a seeded PRNG that cycles through three phases:

**Phase A (structured — ticks 0–1000):**
```
packet[i] = (seed_byte + i * phase_key) mod 256
```
Where `seed_byte` and `phase_key` are derived from the simulation seed. This produces repeating ramp patterns. COMPRESS_DIFF is highly effective on this data.

**Phase B (noisy — ticks 1001–2000):**
```
packet[i] = low_8_bits(seed * (i + 1))  where seed = LCG(simulation_seed, tick)
```
Where LCG is a linear congruential generator. This produces near-random data (low-order bits of multiplicative sequence). COMPRESS_RLE and COMPRESS_DIFF are ineffective. FILTER_LOW or HASH_SUM are the only viable strategies.

**Phase C (alternating — ticks 2001+):**
Every 200 ticks, the sequence alternates between Phase A and Phase B patterns. The transition is deterministic (seed-derived) so it is reproducible across runs.

**Packet arrival:** One packet every 5 ticks. Buffer depth: 4 packets. Arrival is synchronous with the tick boundary (after upkeep deduction, before the next instruction cycle).

### 5b. Real-Coupling Mode

In real-coupling mode, packet content is derived from host telemetry:

```
packet[i] = XOR(low_8_bits(rdtsc() >> (i % 8) * 8), 
                low_8_bits(disk_io_latency_ns % 256),
                tick_number & 0xFF)
```

Where `rdtsc()` is the x86 timestamp counter sampled at the most recent data read, and `disk_io_latency_ns` is a rolling measure of filesystem write latency. This produces data that has short-range structure (from the CPU cycle counter's low-order bits) but is unpredictable at longer ranges.

**If host telemetry is unavailable** (e.g., containerised environment), real-coupling mode falls back to abstract mode with the seed derived from `/dev/urandom` (captured at simulation start, so reproducible for that run).

---

## 6. Upkeep Reduction via Transforms (Formalised)

This is the primary metabolism pathway: the organism pays a one-time transform cost to permanently reduce its ongoing per-tick upkeep.

### 6a. Single Transform Example (Corrected Full-Cost Analysis)

An organism with 64-byte minimum working memory reads a 256-byte data packet. This requires `ALLOC 256` (cost: 1 + 4 = 5 units) to expand its working memory to 320 bytes, then `READ` (cost: 2 units).

Per-tick upkeep before transform:
```
upkeep = 0.1 + 320/640 = 0.1 + 0.5 = 0.6 units/tick
```

The organism applies COMPRESS_RLE to the 256-byte packet. In Phase A (structured data), this typically produces ~40 bytes.

Transform cost: 3 + 256/64 = 7 units.
Replenishment (lossless transform): (256 - 40) / 64 = 3.375 units.

After transform (auto-reclaim: 256→40 bytes):
```
working_memory_size = 64 + 40 = 104 bytes
upkeep = 0.1 + 104/640 = 0.1 + 0.1625 = 0.2625 units/tick
```

**Full cost accounting:**
| Component | Cost |
|-----------|------|
| ALLOC 256 | 5 |
| READ | 2 |
| TRANSFORM (RLE, 256→40) | 7 |
| Replenishment | −3.375 |
| **Total net cost** | **10.625 units** |
| Upkeep savings vs 320B (0.6 → 0.2625) | 0.3375/tick |
| **True breakeven** | **10.625 / 0.3375 ≈ 31.5 ticks** |

If the organism survives more than ~32 ticks after the transform, the upkeep savings exceed the combined ALLOC+READ+TRANSFORM costs.

### 6b. Multiple Transforms

Transforms can be chained and composed. An organism might apply FILTER_LOW (halving the data to 128 bytes) followed by COMPRESS_RLE on the filtered data. The substrate applies each transform in sequence; each one measures the size of its *current* input (which may already have been transformed).

**Important:** FILTER_LOW always produces exactly 50% of the input size. So applying it first guarantees a known reduction, after which COMPRESS_RLE may compress further if the filtered data has structure.

### 6c. Diminishing Returns

The marginal benefit of additional transforms decreases because:
1. Upkeep is proportional to total memory size, not per-region.
2. Once data is compressed, further compression yields smaller absolute reductions.
3. The cost of each transform is proportional to the region size (which shrinks after successful compression).

This creates an economic equilibrium: organisms will evolve to apply the most cost-effective transforms and stop when the marginal benefit of an additional transform is less than its cost.

---

## 7. Execution Reserve Replenishment

This is the critical question deferred from Stage 1B. The genome viability analysis proved that a strictly dissipative system (no replenishment) guarantees extinction within ~5–19 generations, depending on parameters. For Stage 1 experiments this is acceptable, but for Stages 3+ (ecology, adaptation, open-ended evolution), a replenishment mechanism is needed.

The design constraint is: the replenishment mechanism must reward *transformation efficiency*, not reproduction rate or any semantically judged outcome.

### 7a. The Conservation Principle for Replenishment

**Reconciling with Stage 1B:** The genome viability analysis (Stage 1B) recommended against replenishment, warning it would "smuggle fitness." That recommendation was correct for the parameters considered at the time (BASE_UPKEEP=1, MEMORY_COST_DIVISOR=64). However, the Stage 1B analysis also proved that the strictly dissipative model guarantees extinction within ~5 generations. With the reduced upkeep parameters (BASE_UPKEEP=0.1, MEMORY_COST_DIVISOR=640), the dissipative model extends to ~19 generations — still finite.

The replenishment mechanism is introduced here because the project's Stages 3+ (ecology, adaptation, open-ended evolution) require a self-sustaining population. The key design constraint is that replenishment must be **structural, not semantic** — it must depend on properties of the data and the transform, not on whether the organism "did the right thing."

In biology, an organism extracts energy from its environment by exploiting chemical gradients. The "value" of a food molecule is not assigned by an external judge — it's determined by the organism's own metabolic machinery and the energy released when the molecule is broken down.

The computational equivalent: an organism extracts "usable reserve" from data by exploiting statistical structure. The amount of reserve extractable is determined by:
- The compressibility of the data (an objective property)
- The organism's transform repertoire (evolved)
- The match between the data's structure and the organism's transforms (evolved)

### 7b. Replenishment Formula

When an organism applies a **lossless** transform (COMPRESS_RLE, COMPRESS_DIFF, or ENCODE_BASE) that reduces the size of a data region, it receives a replenishment bonus:

```
replenishment = (original_size - new_size) / REPLENISHMENT_DIVISOR
```

Where:
- `original_size` = byte size of the data region before the transform
- `new_size` = byte size after the transform
- `REPLENISHMENT_DIVISOR` = 64 (configurable)
- Only lossless transforms (opcodes 0–2) generate replenishment

**Lossy transforms (FILTER_LOW, HASH_SUM) do not generate replenishment.** They reduce memory footprint (and thus upkeep) but provide no immediate reserve bonus. The rationale: lossy compression destroys information — it reduces memory but does not "extract" usable energy from the data's structure. Only lossless compression, which finds and exploits genuine structure in the data, yields replenishment. This is the computational analogue of extracting energy from a gradient: you can only extract energy once (the unrecoverable destruction of the gradient), and lossy compression destroys the gradient without extracting the energy.

The substrate does not inspect data content to determine whether the transform is lossless or lossy. It checks only the transform opcode (0–2 for lossless, 3–4 for lossy). This is a structural property of the instruction, not a semantic judgment of the output.

This replenishment is added to the organism's execution reserve immediately after the transform instruction completes (before per-tick upkeep).

For a 256-byte packet compressed to 40 bytes:
```
replenishment = (256 - 40) / 64 = 216 / 64 = 3.375 units
```

The transform cost is 7 units. The net cost of the transform is 7 - 3.375 = 3.625 units. The ongoing upkeep savings (0.3375 per tick) are separate and additive.

### 7c. Why This Is Not a Hidden Reward Function

The replenishment is based on a purely structural property: **byte size reduction**. The substrate never inspects the *content* of the data or the transform output. It doesn't know whether the output is a valid compression, a meaningful hash, or random garbage. It only measures: was the region larger before, and is it smaller now?

This satisfies the project's core principle (Section 19 of the spec):
- The substrate supplies the *mechanism* (byte size measurement + replenishment per byte freed)
- The organism must *discover* which transforms work on which data
- The environment provides data with varying compressibility
- No semantic judgment is involved

### 7d. Replenishment Caps

**Per-region cap (byte-level tracking, tied to allocation lifetime):** Each allocated byte in the organism's working memory can generate replenishment at most once during its allocation lifetime. The substrate maintains a shadow structure tracking, for each byte address, the minimum size that byte has ever been part of a compressed region. When a transform is applied:

1. For each byte in the input range, check if that byte has ever been compressed before (minimum size < original size for that byte) *during its current allocation*.
2. If never compressed: the byte contributes to replenishment.
3. Once compressed: any subsequent transform covering the same byte address does not generate additional replenishment for that byte.
4. When a byte is freed (either explicitly via FREE or automatically via transform reclamation), its tracking is reset. When a new allocation occupies that address, the byte starts fresh.
5. If data is explicitly copied or moved to a new allocation (via WRITE or MOV instructions to a freshly allocated region), the tracking resets for the new addresses.

**Example:** An organism reads packet A to bytes [64, 319] and compresses it from 256→40 bytes via COMPRESS_RLE. Bytes [64, 319] are now tracked with minimum size 40. The bytes [104, 319] are automatically reclaimed (freed). Later, it reads packet B — the allocator may give it bytes [104, 359] (reusing reclaimed space). When it compresses bytes [104, 359]:
- Bytes [104, 319]: *fresh* (tracking was reset on reclamation). Replenishment for 216 bytes.
- Bytes [320, 359]: fresh. Replenishment for 40 bytes.

**Per-tick cap:** None for Stage 1–2. With 256-byte packets and one transform per tick, the maximum replenishment from a single lossless transform is ~3.375 units (RLE on 256→40 bytes). A per-tick cap would never be reached under normal conditions. If larger packet sizes are introduced in later stages, a cap can be reinstated.

### 7e. Interaction with Memory Costs

The replenishment mechanism creates a trade-off:
- Compressing data provides immediate replenishment (reserve bonus) AND ongoing benefit (lower upkeep)
- But the transform costs execution reserve upfront
- And holding decompressed data in memory is expensive (upkeep)

The optimal strategy depends on the organism's current reserve level, the compressibility of available data, and the lineage's evolved transform repertoire.

---

## 8. The Full Metabolism Loop

The complete life cycle of an organism, including metabolism:

```
LOOP:
  1. READ data packet into working memory     -- costs 2 + upkeep
  2. TRANSFORM the data (any op)               -- costs 3 + len/64
     -- If size reduces: receive replenishment
     -- If size reduces: future upkeep drops
  3. REPRODUCE if sufficient reserve           -- costs 5 + 2*genome_len
  4. JUMP back to step 1                      -- costs 1
  5. Pay per-tick upkeep at tick boundary      -- costs BASE + memory/640
```

An organism that never reads or transforms data will slowly deplete its initial reserve and die. An organism that reads and transforms efficiently can extend its lifespan significantly.

### 8a. The Dormancy Bypass

An organism that enters dormancy (SLEEP) after reproducing avoids most upkeep costs but also foregoes the opportunity to READ and TRANSFORM new data. Dormancy is a conservation strategy, not a growth strategy. A dormant lineage survives longer but does not accumulate new reserve.

### 8b. The Predicted Dominant Strategies

1. **Minimal replicator + dormancy:** Reproduce once, sleep forever. Simple but vulnerable to displacement at the population cap.

2. **Efficient metaboliser:** READ, TRANSFORM (lossless), REPRODUCE in a loop. Extends lifespan through replenishment plus upkeep reduction. Vulnerable to environmental shifts (data phase changes — lossless transforms fail on noisy data).

3. **Lossy specialist:** Always apply FILTER_LOW or HASH_SUM for guaranteed upkeep reduction. No replenishment from transforms, but memory footprint is minimised. Robust across all data phases, but never gains the reserve bonus of lossless compression.

4. **Lossless specialist:** Apply COMPRESS_RLE or COMPRESS_DIFF for maximum replenishment during favourable data phases. Gains both replenishment AND upkeep reduction. Vulnerable to phase shifts (noisy data yields no compression).

5. **Hybrid:** Detect data phase (via trial-and-error of different transforms or by checking FAIL flags after transforms on noisy data) and switch between lossless (for replenishment) and lossy (for footprint reduction) as conditions change. Most adaptive but requires the largest genome.

---

## 9. Parameter Summary

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| BASE_UPKEEP | 0.1 units/tick | 10× reduction from original; extends generational depth |
| MEMORY_COST_DIVISOR | 640 | 10× increase from original; makes memory cheap enough to hold data |
| PERSISTENT_COST_DIVISOR | 640 | Matches memory divisor for consistency |
| REPLENISHMENT_DIVISOR | 64 | One unit of reserve per 64 bytes freed |
| Per-region cap | One-time per region | Prevents re-compression exploit |
| Per-tick replenishment cap | None (Stage 1–2) | Single-transform limit makes cap unreachable with 256-byte packets; removed for simplicity |
| Dormant upkeep fraction | 10% of ACTIVE | Matches boundary model |
| Minimum working memory | 64 bytes | From boundary model |
| Packet size | 256 bytes | From boundary model |
| Packet arrival interval | 5 ticks | From boundary model |
| Buffer depth | 4 packets | From boundary model |

---

## 10. Formal Metabolism Statement

> A Substrate organism sustains itself by reading data packets from the environment, applying mechanical transforms that reduce the byte size of stored data, and receiving replenishment proportional to the bytes freed. The substrate measures only byte size — never content. Upkeep costs scale with memory footprint, creating an economic pressure for efficient data management. The replenishment mechanism is bounded by per-region and per-tick caps to prevent degenerate strategies. Together, these mechanisms couple data processing to survival without requiring the substrate to evaluate semantic correctness.

---

## 11. Open Questions

1. **Replenishment divisor tuning.** Is REPLENISHMENT_DIVISOR=64 the right value? Too low (e.g., 16) would make replenishment dominate upkeep, reducing selection pressure on memory efficiency. Too high (e.g., 256) would make replenishment negligible, collapsing back to the dissipative model.

2. **Per-tick cap calibration.** Is 3.5 units/tick the right cap? This should be tuned so that a well-adapted organism can achieve net-zero reserve depletion (replenishment ≈ costs) during favourable data phases, but cannot accumulate unlimited reserve.

3. **Phase transition smoothness.** The data stream transitions abruptly between phases (every 1,000 ticks in abstract mode). Abrupt transitions are good for testing adaptation but may produce artefacts (population crashes at phase boundaries). A gradual transition (sine-weighted blend over 100 ticks) might produce more robust dynamics.

4. **Real-coupling data quality.** In real-coupling mode, the XOR of rdtsc() and disk latency may produce data that is genuinely incompressible at all times. If no Phase A equivalent exists in real host conditions, organisms will converge on lossy transforms (FILTER_LOW, HASH_SUM) exclusively. This is a scientifically interesting result but limits the observable dynamics.

5. **Interaction with reproduction.** An offspring inherits the parent's compressed data or fresh uncompressed data? **Resolved: fresh allocation.** Each offspring starts with a fresh 64-byte working memory block (per the boundary model). Compressed data is not inherited. This prevents metabolic "wealth" from compounding across generations, which would create a lineage-level selection pressure distinct from individual-level selection. The trade-off is that each generation must rediscover compression strategies — but this is acceptable for Stages 1–3. If empirical results show that rediscovery prevents cumulative adaptation, offspring inheritance of compressed data can be introduced as a configurable option in Stage 4+.