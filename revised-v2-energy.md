# Substrate — Second Revision: Energy Model

*Addressing Claude's counter-critique: perpetual motion machine, no carrying capacity, founder endowment swamping selection.*

---

## 1. Changes from First Revision

| Issue | First Revision Fix | Second Revision Fix | Why |
|-------|-------------------|---------------------|-----|
| Perpetual motion machine | Replenishment on any byte reduction | Replenishment only on **READ-sourced** data | ALLOC+TRANSFORM on zeros is pure profit |
| No carrying capacity | Both income terms scaled with N | Packet rate is **constant** (independent of pop) | Density-dependent K requires fixed exogenous income |
| Founder endowment | R₀=10M | R₀=500 (3-5× cycle cost) | Organisms must live on income from tick zero |
| Mutation at DIVIDE | All mutations at DIVIDE | **Per-COPY_UNIT** substitution mutations | Makes copy fidelity selectable |

---

## 2. Revised Energy Rules

### 2a. Only Environmental Data Generates Replenishment

The substrate tracks, for each byte in an organism's working memory, whether that byte was sourced from a READ instruction or from an ALLOC instruction.

- Bytes filled by `READ` are tagged as **environmental**.
- Bytes allocated by `ALLOC` (or the minimum working memory block) are tagged as **internal**.
- When `TRANSFORM` is applied to a memory region, only **environmental** bytes contribute to replenishment.
- `REPLENISHMENT_DIVISOR` = 2 (unchanged).
- Total replenishment = (environmental_bytes_before - environmental_bytes_after) / 2.

This eliminates the ALLOC-zeros-RLE exploit: freshly allocated memory is internal, compressing it yields zero replenishment. An organism must READ a data packet to obtain environmental bytes.

**This is structural tracking, not semantic judgment.** The substrate doesn't evaluate whether the data is "good" or "meaningful" — it only records the provenance of each byte (READ vs ALLOC). The READ instruction is the gateway through which environmental energy enters the system.

### 2b. Constant Packet Rate (Density Dependence)

Packet arrival rate is a fixed constant $P$, independent of population size:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Packets per tick | $P$ = 10 (tunable) | Constant exogenous resource |
| Buffer depth | 4 | Fixed, independent of population |
| Packet size | 256 bytes | Unchanged |
| Arrival schedule | 1 packet every 1/P ticks | Evenly spaced |

**Carrying capacity:**
- Income at K: $P \times 108 = 10 \times 108 = 1,080$ units/tick (all packets fully compressed)
- Cost at K: $K \times 5.4$ units/tick
- Equilibrium: $1,080 = K \times 5.4 \implies K \approx 200$

**Density dependence is now real:**
- At pop=50: $1080 - 50 \times 5.4 = 1080 - 270 = +810$ surplus → population grows
- At pop=200: $1080 - 200 \times 5.4 = 1080 - 1080 = 0$ equilibrium
- At pop=500: $1080 - 500 \times 5.4 = 1080 - 2700 = -1620$ deficit → population crashes

The 500-organism cap is now ecologically meaningful — it's only reachable transiently.

**No baseline subsidy.** The per-organism $0.5$ influx is removed entirely. All energy comes from packets.

### 2c. Reduced Founder Endowment

$R_0 = 500$ units (previously 10,000,000). This is ~14× the cycle cost (35.4), giving ~4 generations of buffer before organisms must live entirely on income.

The generational depth recurrence changes from $R' = 0.5 \times (R - 35.4)$ to $R' = 0.5 \times (R - 35.4) + \text{income\_per\_cycle}$.

At equilibrium ($K \approx 200$), income per tick per organism = $1080 / 200 = 5.4$, which exactly covers costs per tick. The population is self-sustaining.

---

## 3. Reproduction: Mutation per COPY_UNIT

In the first revision, all mutations were applied at DIVIDE. This made copy fidelity non-selectable — no genomic strategy could reduce error rate because errors were injected after copying regardless.

**Revised rule:** Substitution mutations are applied per-COPY_UNIT invocation. Each time COPY_UNIT executes:

```
P(single_instruction_substitution) = 0.001
```

A COPY_UNIT that introduces a substitution copies an incorrect instruction into the gestation region. The parent's genome is unaffected (it's read-only during execution).

Insertions, deletions, and duplications are still applied at DIVIDE (they change genome length, which is a structural operation that can't happen mid-copy without corrupting the pointer).

**This makes copy fidelity selectable:**
- A lineage that copies twice and compares (extra COPY_UNIT calls to verify) pays more but catches errors.
- A lineage that copies once and hopes pays less but has higher error rate.
- Mutation in the COPY_UNIT or JUMPZ instructions themselves can change copy speed or accuracy.

---

## 4. Updated Parameter Summary

| Parameter | First Revision | Second Revision |
|-----------|----------------|-----------------|
| ENVIRONMENTAL_INFLUX | 0.5/org/tick (baseline) | **0 — removed entirely** |
| REPLENISHMENT_DIVISOR | 2 | 2 (unchanged) |
| Replenishment source | Any byte reduction | **Only READ-sourced bytes** |
| Packet rate | max(2, pop/20) per tick | **10 per tick (constant)** |
| Buffer depth | max(4, pop/10) | **4 (constant)** |
| Founder endowment (R₀) | 10,000,000 | **500** |
| Mutation timing | At DIVIDE only | **Substitutions per COPY_UNIT; indels at DIVIDE** |
| Carrying capacity K | ~500 (at cap) | **~200 (density-dependent)** |