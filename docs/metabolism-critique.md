# Metabolism Model — Structured Critique

**Document:** metabolism-model.md (Stage 1C)  
**Reviewer:** Hermes Agent — Project-critical check  
**Date:** 2026-07-26  
**Severity levels:** CRITICAL | HIGH | MEDIUM | LOW | INFO

---

## Summary Verdict

**This document should NOT proceed to Stage 2 without revision.** The replenishment mechanism is conceptually defendable but the document has severe underspecification issues (multiple items) that would produce incompatible implementations. Two items (hidden reward analysis and conservation reconciliation) need substantive reworking.

**Overall score: REVISION REQUIRED** — 2 CRITICAL, 3 HIGH, 3 MEDIUM, 2 LOW, 1 INFO findings.

---

## 1. Hidden Reward Functions — CRITICAL

### 1a. Byte-size reduction as structural property

**Verdict:** The claim that byte-size reduction is structural (not semantic) is **conditionally correct**.

The substrate never inspects content — it only measures (original_size − new_size). This is genuinely structural. However, the document's justification conflates two distinct cases:

| Transform | Output size depends on content? | Replenishment varies with data? |
|-----------|--------------------------------|----------------------------------|
| COMPRESS_RLE | YES — varies with run lengths | YES — proportional to compression |
| COMPRESS_DIFF | YES — varies with gradient smoothness | YES — proportional to compression |
| ENCODE_BASE | YES — varies with byte distribution | YES — proportional to compression |
| FILTER_LOW | **NO** — always 50% of input | **NO** — always (input/2)/64 |
| HASH_SUM | **NO** — always 32 bytes | **NO** — always (input−32)/64 |

FILTER_LOW and HASH_SUM produce **guaranteed replenishment independent of data structure**. This means the environment's phase changes (structured → noisy → alternating) do not affect the reward rate for these transforms. Every data packet is equally valuable.

**Severity: HIGH** — The document acknowledges this (Section 4a: "HASH_SUM... is always beneficial") and defends it as a "guaranteed minimum metabolism strategy." This is an acceptable design choice IF the trade-off is properly justified: HASH_SUM and FILTER_LOW destroy information irreversibly, which has downstream costs (less useful data for offspring, inability to detect phase transitions). The document mentions this trade-off but does not quantify it or prove it dominates the transform's advantage.

### 1b. The FILTER_LOW spam exploit

**Trace:**
1. READ 256-byte packet → working memory 64+256=320B
2. ALLOC cost: 5 units, READ cost: 2 units
3. TRANSFORM FILTER_LOW → 128 bytes
4. Replenishment: (256−128)/64 = **2.0 units**
5. Transform cost: 7 units
6. **Net cost (ALLOC+READ+TRANSFORM−replenish): 5+2+7−2 = 12 units**
7. After transform: working memory = 64+128 = 192B
8. Upkeep: 0.1 + 192/640 = 0.4/tick (vs baseline 0.2/tick)

**Does the per-region cap prevent repeated exploitation?** Partially. After one FILTER_LOW on bytes [64,319], that region is marked harvested with minimum size 128. Applying FILTER_LOW again to the same range bytes [64,191] (now 128 bytes) → 64 bytes = **no additional replenishment** because the region was already harvested.

**But the exploit works across different packets.** Each new 256-byte packet read into a NEW address range is a new region → generates replenishment. With 4-packet buffer depth and one packet arriving every 5 ticks, an organism can harvest 2.0 units per packet × 0.2 packets/tick = 0.4 units/tick average replenishment from FILTER_LOW.

**Verdict: The per-region cap prevents harvesting the same data twice, but does not prevent harvesting every new packet.** This is intentional (organisms should benefit from processing new data) and is not a fatal problem. FILTER_LOW provides a baseline yield that is always available — the question is whether this yield is calibrated to make metabolism sustainable (see Q4).

**Severity: MEDIUM** — The exploit exists but is bounded. The document should acknowledge the guaranteed yield of lossy transforms more explicitly and justify why this does not constitute a hidden subsidy.

### 1c. HASH_SUM exploit

Same pattern as FILTER_LOW but with higher yield:

| Measure | FILTER_LOW | HASH_SUM |
|---------|-----------|----------|
| Transform cost (256B) | 7 | 7 |
| Replenishment (256B) | 2.0 | 3.5 |
| Net transform cost | 5.0 | 3.5 |
| Final size | 128B | 32B |
| Upkeep savings vs 320B | 0.3/tick | 0.45/tick |

HASH_SUM is strictly superior to FILTER_LOW for replenishment purposes. Document acknowledges this but doesn't explain why an organism would ever choose FILTER_LOW over HASH_SUM if both are available.

**Severity: HIGH** — HASH_SUM is a strictly dominant strategy for replenishment. It has the same information-destroying property as FILTER_LOW but higher yield AND smaller footprint. The document's claim that lossy transforms "destroy information that might have been useful" is theoretically true but needs demonstration. In practice, with information destroyed anyway, HASH_SUM dominates. The document should address whether this creates a monoculture problem.

---

## 2. The Replenishment Principle — HIGH

### 2a. HASH_SUM always generates the same replenishment

**Confirmed:** For a 256-byte input, HASH_SUM always produces 32 bytes, always generating (256−32)/64 = 3.5 units of replenishment. This is **independent of both data content and data phase**.

This means:
- In Phase A (structured): COMPRESS_RLE yields 216/64 = 3.375 units (slightly less than HASH_SUM!)
- In Phase B (noisy): COMPRESS_RLE yields ~0 units (expands). HASH_SUM yields 3.5 units.
- In Phase C (alternating): HASH_SUM is consistent; RLE alternates.

**HASH_SUM outperforms COMPRESS_RLE even on the most favourable data for RLE.** On Phase A data where RLE compresses 256→40 bytes, HASH_SUM still produces more replenishment (3.5 vs 3.375). This is a parameter calibration issue — with REPLENISHMENT_DIVISOR=64, the hash "frees" more bytes (256−32=224) than RLE (256−40=216), so it's always better for replenishment.

**Is this a problem?** Yes, because it means the "intelligent" lossless transforms are never superior to the "dumb" lossy ones in terms of immediate replenishment. The only advantage of lossless transforms is that the data remains human-readable/useful for other computation. If no other instruction in the instruction set makes use of decompressed data, lossy transforms dominate unconditionally.

**Severity: HIGH** — This undermines the document's design narrative. The section on predicted dominant strategies (Section 8b) lists "Lossless specialist" as a viable strategy, but the arithmetic shows HASH_SUM dominates RLE even in Phase A. This needs to be addressed before Stage 2, either by:
- Adjusting REPLENISHMENT_DIVISOR so lossless transforms yield more replenishment than HASH_SUM on structured data (e.g., divisor of 80 for HASH_SUM, 64 for RLE), or
- Adding utility for decompressed data beyond just memory footprint (e.g., data-dependent instructions that work on compressed vs uncompressed formats differently), or
- Explicitly accepting that HASH_SUM dominance is the expected outcome and that selection should favour organisms that use it.

### 2b. COMPRESS_RLE on random data

**Confirmed:** On random data, RLE typically expands (~2×). The substrate correctly measures the larger output size → no replenishment → increased upkeep. No exploit possible.

**Severity: LOW** — Handled correctly.

---

## 3. Conservation — CRITICAL

### 3a. Replenishment creates reserve from thin air

The boundary model states (Section 6, invariant 3):
> "Execution reserve is NOT conserved — it is consumed by instruction execution and per-tick upkeep, and discarded on death."

The metabolism model introduces replenishment: reserve is created when data shrinks. This is **not a violation of the boundary model**, because the boundary model explicitly exempts execution reserve from conservation. However, there are three issues:

**Issue 1: The boundary model says not-conserved, the metabolism model says created.**
These are different statements. "Not conserved" means reserve is consumed and discarded but not created. "Replenishment creates reserve" is an addition, not a contradiction. The metabolism model should explicitly note this extension.

**Issue 2: The "information converted to reserve" analogy is defensible but underspecified.**
In thermodynamics, the amount of extractable work from a gradient is bounded by the Gibbs free energy difference. Here, the "extractable work" from a data packet is bounded by (packet_size − 32) / 64 — but 32 is the minimum output size (HASH_SUM), not the Kolmogorov complexity of the data. The actual compressibility limit for 256 bytes is much lower (the algorithmic information content). The divisor 64 was chosen arbitrarily. This makes the "physics analogy" break down: the replenishment does not measure any true physical quantity.

**Issue 3: The Stage 1B analysis explicitly warned against this.**
Genome viability Section 8c: "Do not add a reserve replenishment bonus for compression. This creates a dual reward pathway (lower upkeep + bonus reserve) that violates the dissipative principle and smuggles fitness."

The metabolism model contradicts this recommendation. If this was a deliberate override, the document must explain why. Currently it silently discards the Stage 1B recommendation.

**Severity: CRITICAL** — The document must:
1. Reconcile explicitly with the boundary model's conservation statements
2. Address the Stage 1B warning about replenishment smuggling fitness
3. Justify the "information → reserve" conversion with a clearer physical or mathematical argument

---

## 4. Parameter Tuning — HIGH

### 4a. Breakeven analysis for 256-byte packet in Phase A

**Document's claimed breakeven: ~21 ticks** (transform cost 7 ÷ upkeep savings 0.3375).

**Actual full-cost breakeven: ~31.5 ticks**

| Cost component | Value |
|---------------|-------|
| ALLOC 256 | 5 units |
| READ | 2 units |
| TRANSFORM (RLE, 256→40) | 7 units |
| Replenishment | −3.375 units |
| **Total net cost** | **10.625 units** |
| Ongoing upkeep savings vs 320B | 0.3375/tick |
| **True breakeven** | **10.625 / 0.3375 ≈ 31.5 ticks** |

The document's breakeven of 21 ticks only accounts for the transform cost minus replenishment, ignoring ALLOC and READ costs. This is misleading and may affect viability analysis.

**Additionally:** The organism's upkeep after the transform (0.2625/tick) is **higher** than its upkeep before reading any packet (0.2/tick). The organism is in a strictly worse ongoing position than if it had done nothing. The benefit is only relative to the alternative of holding the full 320B (0.6/tick). This is a narrow framing.

### 4b. Steady-state economics (net loss)

**Best-case steady state (HASH_SUM, 4 compressed packets):**

Working memory: 64 + 4×32 = 192 bytes  
Upkeep: 0.1 + 192/640 = 0.4/tick  
Processing one new packet every 5 ticks:  
- ALLOC + READ + TRANSFORM(256→32) = 5 + 2 + 7 = 14 units
- Replenishment: 3.5 units
- Net per packet: 10.5 units  
- Amortized per tick: 2.1/tick

**Total per-tick cost: 0.4 + 2.1 = 2.5 units/tick (net loss)**

The organism's reserve declines at ~2.5 units/tick. With 10M initial reserve, this gives ~4 million ticks of life — much better than the dissipative model, but still a monotonic decline.

**Note:** This assumes the organism keeps ALLOCating for each new packet. If the organism can reuse existing space (overwrite old compressed data with new unread data), it may eliminate the ALLOC cost. The document does not specify whether this is possible.

### 4c. Is the organism in net gain, net loss, or net zero?

**Net loss (negative balance).** Replenishment partially offsets transform costs but does not cover ALLOC+READ+upkeep. This is probably intentional — the document says replenishment should make the system "not strictly dissipative" but does not aim for self-sustaining growth. However, the document's Open Question 2 states: "This should be tuned so that a well-adapted organism can achieve net-zero reserve depletion (replenishment ≈ costs) during favourable data phases." The current parameters do NOT achieve this.

**Recommended adjustment:** Reduce REPLENISHMENT_DIVISOR to ~40 for net-zero during Phase A, or increase packet arrival rate.

**Severity: HIGH** — The breakeven analysis in the document is incomplete (ignores ALLOC+READ), and the current parameters produce net loss even in the best case. The parameters need to be computed against the full cost model and the open question about net-zero calibration needs resolution before Stage 2.

---

## 5. Per-Region Cap — CRITICAL

### 5a. Tracking mechanism underspecified

The document says: "The substrate tracks which regions have been 'harvested' by recording the byte ranges and the minimum size achieved."

This is **not a specification**. It is a vague description. Consider the overlapping region problem:

**Overlap scenario:** Organism transforms bytes [0, 255] (packet A, 256→128 bytes via FILTER_LOW). Then reads packet B and transforms bytes [128, 383] (packet B, 256→128 bytes).

| Interpretation | Region tracking | Second transform replenishment |
|---------------|----------------|-------------------------------|
| A) Byte-range exclusive | [0,255] harvested. New region [128,383] overlaps by 128 bytes. | Only non-overlapping [256,383] (128 bytes fresh → 1.0 units) |
| B) Byte-range inclusive with per-byte tracking | Each byte can only be harvested once. | Bytes [0,127] previously harvested, bytes [128,255] previously harvested, bytes [256,383] fresh → only 128 fresh bytes → 1.0 units |
| C) Virtual region (logical content tracking) | Each READ+TRANSFORM on distinct packets creates independent virtual regions | Full 256 bytes fresh → 2.0 units |
| D) Single transform per address range ever | Once any byte in a range is harvested, the whole range is marked | Overlap means NO replenishment from [128,255] |

Interpretations A/B vs C give **2× different** replenishment outcomes for the exact same operations. The document does not distinguish between them.

### 5b. Minimum size tracking ambiguity

"Minimum size achieved" suggests: if a region went from 256→128→64 bytes, only the initial reduction (256→128, reduction of 128) generates replenishment, and the second reduction (128→64) does not because the region was already harvested.

But what if the organism ALLOCs new space, copies the 128-byte data to the new space (creating a "new" region), and transforms it there? Is the copied data a new region or the same logical region?

**Verdict:** The per-region cap mechanism is **not implementable as specified**. Two implementers would produce different tracking logic with different reward outcomes.

**Severity: CRITICAL** — Must be specified with precise tracking semantics (byte ranges, minimum sizes, handling of overlap, handling of data movement) before implementation.

---

## 6. Per-Tick Cap (10 units) — MEDIUM

### 6a. Is 10 enough? Can it be reached?

**With 256-byte packets:** Maximum single-transform replenishment is HASH_SUM on 256 bytes = 3.5 units. Since each organism executes one instruction per tick, the cap of 10 is **never reached** with 256-byte packets under normal conditions.

**Input size needed to hit the cap:** (input − 32) / 64 > 10 → input > 672 bytes. An organism would need a 672-byte region and apply HASH_SUM. With ALLOC cost 1 + ceil(672/64) = 12 units, this is expensive but possible.

**With 4 packets of 256 bytes each in one transform:** If the organism could transform all 4 packets as one region (1024 bytes → HASH_SUM → 32 bytes): (1024−32)/64 = 15.5 → capped at 10. The cap would be reached. But can the organism transform a non-contiguous region spanning multiple allocated blocks?

### 6b. Practical impact

**The per-tick cap (10) is irrelevant for single 256-byte packet processing.** It only matters if:
- Packet size increases in future stages
- An organism maintains very large working memory (>704 bytes)
- Multiple transforms can somehow occur in one tick (contradicting the one-instruction-per-tick scheduler)

**Verdict:** The cap should either be removed (since it never triggers) or calibrated to a lower value that is reachable. A cap of 3.5 units (matching a single HASH_SUM on 256 bytes) would create a meaningful constraint between applying many small transforms vs one large one. A cap of 10 is equivalent to no cap.

**Severity: MEDIUM** — Not incorrect, but functionally irrelevant. Needs recalibration or removal.

---

## 7. Interaction with Boundary Model — MEDIUM

### 7a. Memory allocation model

The boundary model defines ALLOC and FREE as separate instructions. The metabolism model appears to assume that transform operations automatically free memory when data shrinks ("working_memory_size is recalculated as the sum of all allocated regions"). This is an **extension** of the boundary model, not a contradiction, but it's unclear whether:

1. The transform instruction implicitly calls FREE on the freed portion, or
2. The freed bytes remain allocated (fragmentation) and the organism must explicitly FREE them

If interpretation 1: the transform instruction now has side effects on memory allocation, which the boundary model does not account for. The instruction cost table would need updating.

If interpretation 2: the organism's working memory does NOT shrink automatically, and the breakeven calculations in the document are wrong (the organism still pays upkeep on the original allocation size).

### 7b. Exclusive-ownership invariant

No violation. All operations are within the organism's own working memory.

### 7c. Reproduction and inheritance

The boundary model specifies offspring get fresh 64-byte working memory. The metabolism model raises this as Open Question 5: "An offspring inherits the parent's compressed data or fresh uncompressed data?" The document says "this may be intentional (prevents inheritance of metabolic 'wealth') or a bug (prevents cumulative adaptation)."

This ambiguity **must be resolved before Stage 2**. If offspring always start fresh, each generation must rediscover compression strategies. If offspring inherit compressed data, metabolic efficiency compound across generations.

### 7d. Status flags

The boundary model defines FAIL flag set when READ has empty buffer. The metabolism model does not mention using this flag. For organisms to adapt to phase transitions, they need some feedback mechanism. The document should specify how organisms detect whether a transform succeeded.

**Severity: MEDIUM** — No contradictions found, but three areas need resolution (automatic memory reclamation, offspring inheritance, transform feedback).

---

## 8. Missing Pieces — HIGH

The following are unspecified or underspecified enough to cause divergent implementations:

### 8a. Transform in-place vs copy (CRITICAL)

When TRANSFORM executes, does it:
(a) Replace the input region in-place with the output (overwriting from the start address)?
(b) Write the output to a new buffer and return a pointer?
(c) Replace in-place, and if output is smaller, leave garbage in the remaining bytes?

The document says "the working memory region contains the transformed output" — suggesting in-place — but the size recalculation mechanism is unclear.

### 8b. Memory reclamation on size reduction (CRITICAL)

When a transform reduces data from 256 to 40 bytes, what happens to the remaining 216 bytes of allocated space? Is it automatically freed (changing working_memory_size), or does it remain allocated (fragmented)?

### 8c. Per-region overlap semantics (CRITICAL)

See Q5 above. Must specify byte-level vs region-level tracking.

### 8d. Minimum size tracking details (HIGH)

"The minimum size achieved" — does this track the minimum size at a specific address range, or the minimum size of the logical data? If the organism compresses bytes [0,255] to 40 bytes, then writes new data to [0,255] and compresses to 64 bytes... is the "minimum size achieved" 40 or 64?

### 8e. Instruction encoding (HIGH)

The transform opcodes are 0-4, but the instruction format (how addr and length operands are encoded) is unspecified. This affects genome length calculations in Stage 1B.

### 8f. Non-contiguous transform (MEDIUM)

Can an organism transform a region that spans two separately allocated blocks? If not, the memory model must prevent this.

### 8g. Replenishment credit for automatic memory reclamation (MEDIUM)

If the organism frees memory via FREE (not TRANSFORM), does it get replenishment? The document implies only transforms generate replenishment, but this should be explicit.

### 8h. COMPRESS_RLE and COMPRESS_DIFF output format (MEDIUM)

The document says these are lossless but doesn't specify the output encoding (header format, count encoding). Two implementers could produce different compression ratios for the same input data, leading to different replenishment amounts.

---

## 9. Dormancy Bypass — LOW

### 9a. Is dormancy a stable or dominant strategy?

**Dormancy calculation:**
- Dormant organism: upkeep = 0.02/tick (10% of 0.2)
- With 10M reserve: lasts ~500M ticks
- Cannot READ, cannot TRANSFORM, cannot replenish reserve
- Cannot reproduce while dormant

**Active organism with metabolism:**
- Upkeep ~0.4-0.6/tick + processing costs
- Net loss ~2.5/tick (see Q4)
- Can reproduce, has offspring

**Key insight: Dormancy is not dominant** because:
1. Dormant organisms cannot reproduce — the lineage goes extinct
2. At population cap (500), dormant organisms are displaced by new offspring from active organisms
3. Displacement mortality is uniform and doesn't favour any strategy

**But:** A parent that reproduces once and then sleeps forever creates an active offspring that can reproduce further. The dormant parent occupies a slot at low cost. This is a viable "stay alive" insurance strategy.

**Is this a problem?** Not in Stage 2. The population dynamics ensure active reproducers dominate the cap slots. Dormancy is a conservation strategy, not a growth strategy, which is exactly how the document frames it.

**Severity: LOW** — Well-reasoned. No revision needed.

---

## Cross-Document Consistency Issues

### Metabolism vs Genome Viability

The genome viability analysis (Stage 1B) explicitly recommends:
> "Do not add a reserve replenishment bonus for compression. This creates a dual reward pathway (lower upkeep + bonus reserve) that violates the dissipative principle and smuggles fitness."

The metabolism model does exactly this. **No justification is given for overriding this recommendation.** This is a serious consistency issue between stages.

### Metabolism vs Boundary Model

The boundary model assumes the strictly dissipative model for Stages 1-2:
> "Replenishment mechanisms may be introduced in Stage 1C for later experiments, but only if the dissipative baseline is understood first."

The metabolism model introduces replenishment in Stage 1C (Stage 2 experiments). This is aligned with the boundary model's timing, but the boundary model says "if the dissipative baseline is understood first" — and the Stage 1B analysis was exactly that baseline. However, the metabolism model doesn't reference this agreement.

---

## Recommended Revisions Before Stage 2

### Must-fix (blocking Stage 2)

1. **Reconcile with Stage 1B recommendation.** Either justify the override or adjust the design. (Section 2 and Section 7c)

2. **Specify per-region cap tracking semantics.** Byte-level tracking with overlap handling, minimum size semantics, and data movement rules. (Section 7d)

3. **Specify transform in-place vs copy and memory reclamation after size reduction.** This affects ALL breakeven calculations. (Section 4c)

4. **Fix breakeven calculation to include ALLOC and READ costs.** (Section 6a)

### Should-fix (strongly recommended before Stage 2)

5. **Address HASH_SUM dominance.** The arithmetic shows HASH_SUM is strictly better than RLE even on Phase A data. Either recalibrate REPLENISHMENT_DIVISOR or accept the dominance explicitly. (Section 4a)

6. **Calibrate per-tick cap to a reachable value** (e.g., 3.5 units) or remove it. (Section 7d)

7. **Resolve offspring inheritance** of compressed data. (Open Question 5)

8. **Specify instruction encoding** for transform operands. (Section 4b)

### Nice-to-fix

9. **Add organism feedback mechanism** for transform outcome (success/failure flag). (Section 13 reference)

10. **Specify COMPRESS_RLE and COMPRESS_DIFF output format** to ensure cross-implementation determinism. (Section 4a)

---

## Conclusion

**Should this document proceed to Stage 2 (static paper model)?**  
**NO — REVISION REQUIRED FIRST.**

The conceptual foundation (byte-size reduction as a structural property) is sound and defensible. The replenishment mechanism can be framed as the computational analogue of energy extraction from chemical gradients. The dormancy analysis is well-reasoned. The transform set is sensible.

However, the document has critical underspecification in three areas (per-region tracking semantics, transform memory model, instruction encoding) that would produce incompatible implementations. It also has a serious consistency problem with the Stage 1B recommendation against replenishment. And the arithmetic in the breakeven analysis misrepresents the true costs by excluding ALLOC and READ.

The document as written would pass a high-level design review but fail an implementation specification review. For Stage 2 (static paper model — reasoning about the system without running code), the underspecifications can be tolerated if they are flagged and resolved in the implementation plan. But the Stage 1B contradiction and the HASH_SUM dominance problem should be fixed before any static analysis is performed, because they affect the conclusions that analysis would draw.