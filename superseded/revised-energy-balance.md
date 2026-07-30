# Substrate — Revised Energy Balance Model

*Addressing Claude's three critiques: energy budget, lossless/lossy rule, atomic REPRODUCE.*

---

## 1. Summary of Changes

| Critique | Problem | Fix |
|----------|---------|-----|
| Energy budget off by ~150× | 0.675 units/tick income vs 100/tick upkeep | Add baseline per-tick influx (0.5/org); scale packet rate with population; lower REPLENISH_DIV to 2 |
| Lossless/lossy rule is hidden fitness | Interpreter decides which transforms are "right kind" | Replenishment follows bytes freed by ANY transform. Irreversible deletion provides structural disincentive. |
| Atomic REPRODUCE eliminates copy loop | L_min=2 with no copy machinery to evolve or parasitise | Decompose REPRODUCE into ALLOC_OFFSPRING, COPY_UNIT, DIVIDE primitives |

---

## 2. Revised Energy Parameters

| Parameter | Old Value | New Value | Rationale |
|-----------|-----------|-----------|-----------|
| ENVIRONMENTAL_INFLUX | 0 (none) | 0.5 per ACTIVE org/tick | Baseline per-organism income to prevent guaranteed extinction during incompressible data phases |
| REPLENISHMENT_DIVISOR | 64 (lossless only) | 2 (all transforms) | Bytes freed per unit of replenishment; applies to ALL transforms — no semantic judgment |
| Packet arrival rate | 1 per 5 ticks (0.2/tick) | max(2, population / 20) per tick | Scales with population; creates shared resource competition |
| Packet buffer depth | 4 | max(4, population / 10) | More organisms need more buffer slots |
| Per-tick replenishment cap | None for Stage 1-2 | None (removed) | No cap needed; transform rate is self-limiting by buffer depth |
| Lossless/lossy rule | Only lossless ops generate replenishment | Removed — all transforms generate replenishment | No evaluator; bytes freed is purely structural |

### 2a. Income Components

Each tick, every ACTIVE organism receives:

```
baseline_income = ENVIRONMENTAL_INFLUX           # 0.5 units
```

Additionally, when an organism applies any transform that reduces byte size:

```
transform_income = (original_size - new_size) / REPLENISHMENT_DIVISOR
```

Where REPLENISHMENT_DIVISOR = 2. For a 256-byte packet compressed to 40 bytes via RLE: (256-40)/2 = 108 units. For a 256-byte region hashed to 32 bytes via HASH_SUM: (256-32)/2 = 112 units.

**Both lossless and lossy transforms generate replenishment.** The interpreter never inspects which transform was applied. It only measures byte sizes. The structural disincentive for lossy transforms is that permanently discarded information cannot be used for other computation or passed to offspring.

### 2b. Packet Scaling with Population

```
packets_per_tick = max(2, current_population / 20)
buffer_depth = max(4, current_population / 10)
```

These values are recomputed each tick. The substrate generates the specified number of packets and adds them to the buffer (respecting the depth limit). This means:

- At pop=10: 2 packets/tick, buffer=4
- At pop=100: 5 packets/tick, buffer=10
- At pop=500: 25 packets/tick, buffer=50

### 2c. Carrying Capacity

Under Phase A data (fully compressible), carrying capacity K ≈ 500 organisms (income ≈ cost at the cap).

Under Phase B data (incompressible), K ≈ 500 × (0.5 / 5.4) ≈ 46 organisms.

Under Phase C (alternating), K fluctuates around ≈ 250 organisms.

The boom-bust cycle: each 2000-tick Phase A+B cycle consumes ~22% of the population's reserve endowment from the founding ancestor. This gives enough time for selection to act before eventual extinction, while keeping density-dependence real and meaningful.