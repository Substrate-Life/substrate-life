# Substrate — Energy Model v3 (Derived Parameter Set)

*Replaces superseded/revised-v2-energy.md. Parameters derived rather than asserted; every constant traceable to a stated constraint.*

---

## 0. Summary of what changed and why

| Issue in v2 | Resolution |
|---|---|
| Compress/expand pump | Extraction drawn from a **per-packet budget**, signed. Round trips net zero by construction. |
| Tag propagation | Bytes carry a **packet ID**, not a boolean. Copies share the ID and the same budget. |
| Phase B extinction | Lean packets retain a **structural floor** of extractable energy (E_lean > 0), sized so K_lean stays above stochastic-extinction risk. |
| K rests on an asserted 5.4/tick | Per-capita cost **derived from an explicit metaboliser genome**: 2.56 units/tick. |
| Copy-verify inexpressible | `SET_P` instruction added; copy pointer becomes writable. |
| — (new finding) | **Open-access rent dissipation**: with one contested resource and unconstrained foraging effort, the evolutionary equilibrium burns the entire environmental income and the population goes extinct. The shared memory pool must be scarce enough to cap foraging effort. See §5. |

---

## 1. The packet energy ledger

The exploit class in v1 and v2 was the same both times: a rule that pays for a state change in one direction without charging for the reverse. The fix is to make the ledger **per-packet and closed**, so no sequence of organism actions can extract more than the packet contains.

### 1a. Packet construction

The substrate's packet generator creates each packet with known structure. It therefore *knows* the packet's compressible content by construction and does not need to infer it. Each packet `p` is created with:

- `S` = 256 bytes (raw size)
- `S_min(p)` = size under maximal reduction, determined by how much structure the generator injected
- `max_reducible(p)` = S − S_min(p)
- `E_p` = total extractable energy quantum, assigned at generation

This matters for the no-hidden-fitness requirement: nothing in the substrate runs a reference compressor and grades the organism's output. The generator sets `E_p` when it writes the packet; the interpreter only counts bytes.

### 1b. Tagging

Every byte in working memory carries a provenance tag: either `null` (internal) or a **packet ID** `p`. Tags propagate on copy — a duplicate of a `p`-tagged byte is also `p`-tagged. This is what closes the duplication exploit: copying tagged bytes cannot create budget because the budget belongs to the packet, not to the bytes.

### 1c. Extraction

When a `TRANSFORM` changes the count of `p`-tagged bytes from `b_before` to `b_after`:

```
Δ = E_p × (b_before − b_after) / max_reducible(p)
```

- `Δ > 0` (reduction): the organism draws `Δ`, capped at `p`'s remaining budget, which is decremented.
- `Δ < 0` (expansion): the organism is **charged** `|Δ|` and `p`'s budget is credited by the same amount.

Total energy ever extractable from packet `p` is `E_p`, regardless of what any organism does. Compress/expand cycling nets exactly zero minus instruction costs. Duplication yields nothing. When the last `p`-tagged byte leaves memory, any unspent budget is destroyed.

**Invariant to check every future rule against:** acquiring a resource must cost at least what releasing it pays. Both prior exploits violated this.

---

## 2. The reference metaboliser (M1)

All per-capita costs below derive from this genome. It is the simplest organism that both metabolises and reproduces.

```
Addr  Instruction         Cost   Notes
0     MOV R0, 256          1     buffer size
1     ALLOC R0             5     1 + 256/64;  memory 64 → 320 B
2     READ                10     fills buffer with a packet (see §5 for cost derivation)
3     TRANSFORM compress   7     3 + 256/64;  256 → 40 B, draws from packet budget
4     FREE                 1     release buffer;  memory → 64 B
5     MOV R0, 64           1     offspring memory size
6     ALLOC_OFFSPRING R0   6     5 + 64/64;  gestation region, memory → 128 B
7     COPY_UNIT            2     × L
8     JUMPZ R2, 7          1     × L
9     DIVIDE               5     mutate, instantiate offspring, transfer reserve
10    JUMP 0               1
```

`L = 11`.

### 2a. Cycle cost

| Component | Units |
|---|---|
| MOV + ALLOC + READ + TRANSFORM + FREE | 24 |
| MOV + ALLOC_OFFSPRING | 7 |
| Copy loop: 3 × L = 3 × 11 | 33 |
| DIVIDE + JUMP | 6 |
| **Instruction subtotal** | **70** |
| Upkeep (see below) | 9.46 |
| **Total cycle cost C** | **79.5** |

Upkeep tally (0.1 + bytes/640 per tick):

| Ticks | Memory held | Rate | Subtotal |
|---|---|---|---|
| 0 | 64 B | 0.2 | 0.2 |
| 1–2 | 320 B | 0.6 | 1.2 |
| 3 | 104 B | 0.2625 | 0.26 |
| 4–5 | 64 B | 0.2 | 0.4 |
| 6–29 (gestation held) | 128 B | 0.3 | 7.2 |
| 30 | 64 B | 0.2 | 0.2 |
| | | | **9.46** |

**Cycle length: 31 ticks. Per-capita cost: 79.5 / 31 = 2.56 units/tick.**

The copy loop is 42% of instruction cost. Genome length is therefore a real, steep cost — which is the pressure that makes retained complexity a genuine trade-off rather than a free option. Note the corollary: at `3L` units per cycle, a genome of L=40 costs 120 units in copying alone, exceeding the extractable content of a single packet. **The instruction set as specified imposes a hard ceiling near L ≈ 40 for single-packet metabolisers**, independent of mutation load. This is a much tighter ceiling than the error threshold and should replace `1/μ` as the operative upper bound of the viable band.

### 2b. Viable band

- **Floor:** L_min = 6 (bare replicator, no metabolism). But a bare replicator has no income and dies in `R₀ / 2.2 ≈ 45` ticks. **The effective floor is L = 11** — metabolism is now mandatory for persistence, which is the correct property.
- **Ceiling:** L ≈ 40 from copy cost (above), well below the error-threshold ceiling of `1/μ = 1000`.
- **Band: [11, 40]** — 30 instructions wide. Wide enough for structure, narrow enough that length is under real selection.

---

## 3. Steady-state reserve

With reserve `R`, per-cycle cost `C`, per-cycle income `I`, and 50% transfer at DIVIDE:

Income arrives at tick 3, *before* DIVIDE, so it is included in the split:

```
R' = 0.5 × (R − C + I)
```

Fixed point:

```
R* = I − C
```

(Note this differs from the `R* = 2I − C` form I gave earlier, which assumed income landed after the transfer. Placement of income relative to DIVIDE changes the equilibrium by a factor of two — worth fixing deliberately rather than accidentally.)

**Two viability constraints:**

1. **Trough:** reserve must stay positive before income lands at tick 3. Spend to that point is 23 instruction units + 1.6 upkeep = 24.6. So `R* > 24.6`.
2. **Fixed point positive:** `I > C = 79.5`.

Constraint 1 binds: **`I > 104.1`**. Use `I ≥ 110` for margin.

### 3a. Why break-even is not enough

At `I = C` exactly, reserve halves every generation and the lineage dies. Reproduction duplicates the organism but not its reserve — every new individual must be *endowed* out of surplus. Per-capita income must exceed per-capita cost by the amortised endowment, which is why the viability threshold (110) sits ~38% above cost (79.5) rather than at it.

### 3b. Recommendation: make offspring provisioning heritable

The 50% rule makes viability a knife-edge in `E`: at `I = 90` the lineage is marginal, at `I = 130` it is comfortable, and the designer picks which. Better: `DIVIDE` transfers an amount named in a register, subject to a floor of the offspring's first-cycle trough requirement (24.6). Provisioning then becomes an evolvable trait and the r/K trade-off — many cheap offspring vs. few well-endowed ones — is expressed by the genome rather than fixed by the substrate. This is a one-line change that removes a designer decision and adds an evolutionary dimension. Strongly recommended.

---

## 4. Carrying capacity

Each M1 attempts one READ per 31-tick cycle, so per-capita packet demand is `1/31` per tick. With constant supply `P` packets/tick and population `N`, the success fraction is:

```
f = min(1, 31P / N)
```

Effective income per cycle is `f × E`. Setting that to the viability threshold:

```
f × E = 110    →    31 P E / K = 110    →    K = 31 P E / 110
```

**Chosen parameters:**

| Parameter | Value | Derivation |
|---|---|---|
| `P` (packets/tick) | 5 | free choice; sets absolute scale |
| `E_rich` (per packet) | 129 | from K = 31·P·E/110 with target K ≈ 180 |
| `K_rich` | ≈ 180 | target: comfortably below the 500 cap |
| `f` at K | 0.86 | 31 × 5 / 180 |

At K, 86% of foraging attempts succeed; the 14% that fail is the mortality pressure. Global check: income = `P·E` = 645/tick against cost `K × 2.56` = 461/tick. The 184/tick surplus is destroyed at death (corpse reserve is not recycled, per the Stage 1 boundary model), so the books close.

**Density dependence is real:** at N=50, f=1 and every organism thrives. At N=180, f=0.86 and the population is at equilibrium. At N=400, f=0.39, effective income is 50 against a cost of 79.5, and the population crashes. The 500 cap is now reachable only transiently, which is what makes it ecological rather than administrative.

### 4a. Lean phases

Requirement: `K_lean` must stay above the stochastic-extinction threshold (~25–30 for a population of this size).

```
K_lean = 31 P E_lean / 110
```

Setting `K_lean = 35` gives **`E_lean = 25`** — lean packets retain ~19% of rich extractable energy. This is the "structural floor": the generator must always inject some minimum structure, never pure noise. Phase B in the v1 phase model, which zeroed income entirely, is not survivable at any endowment that doesn't reintroduce the founder problem.

Dormancy check: dormant upkeep is 0.02/tick, so a 1000-tick lean phase costs a sleeping organism 20 units against `R* ≈ 50`. **Dormancy is a viable lean-phase strategy** — which is one of the target emergent behaviours, and it is now available without being rewarded. Organisms can in principle detect the phase from low transform yield, but nothing tells them to; whether any lineage discovers this is the experiment.

### 4b. Founder endowment

Set `R₀ = 100` ≈ 2 × R*. Founders start near equilibrium with modest buffer and must live on income within their first two cycles. No unselected early phase.

---

## 5. The dissipation problem, and why memory scarcity is load-bearing

This is the most consequential result in the derivation and it was not visible in any previous pass.

### 5a. The problem

`READ` costs `c_read` and yields, in expectation, `P·E / A` where `A` is the *total* attempt rate across the population. Any organism gains by adding attempts as long as marginal yield exceeds `c_read`. Selection therefore drives the population to:

```
P·E / A* = c_read    →    A* = P·E / c_read
```

Total foraging expenditure at that point is `A* × c_read = P·E` — **exactly the entire environmental income**. Nothing is left for maintenance or reproduction, and the population goes extinct.

This is open-access rent dissipation (the Gordon result from fisheries economics), and it is unavoidable under a pure lottery, because with a lottery the average yield per attempt equals the marginal yield, so there are no diminishing returns to individual effort to stop the escalation.

Setting `c_read = 2` as in v2 makes this acute: with `E = 129`, the break-even attempt rate is 64 attempts/tick against M1's 5.8/tick, so there is a 10× escalation available to any mutant that reads more often. The first lineage to discover READ-spamming collapses the ecosystem.

### 5b. Why this is good news

The escalation is bounded only if foraging effort meets a hard constraint that is *not* economic. The natural candidate is already in the design: **the shared memory pool**. Every READ requires an allocated 256-byte buffer, and buffers are drawn from a finite pool. An organism cannot hold ten buffers if the pool cannot supply them.

This means the multi-resource design is not merely *interesting* — it is **necessary for the system to be viable at all**. A single-resource version (Experiment C in the original grid) should dissipate its income and go extinct, while the multi-resource version (Experiment D) persists. That is a sharp, analytically-derived, pre-registerable prediction that directly tests the project's main hypothesis. It should go in the protocol document as a confirmatory prediction before any run.

### 5c. Sizing the pool

At `K = 180` with M1 peak usage of 384 B (64 baseline + 256 buffer + 64 gestation):

```
MEMORY_POOL = 80 KB    →    455 B per organism at K
```

This is deliberately tight: it permits roughly one buffer per organism and makes a second buffer contested. `MEMORY_POOL` is the primary knob controlling how hard the foraging cap binds — raise it and dissipation reappears, lower it and memory becomes the sole limiting resource.

### 5d. Deriving `c_read`

With effort capped by memory rather than by cost, `c_read` no longer needs to carry the whole regulatory burden. But it should still be high enough that failed reads are meaningfully penalised. Set it at the expected yield per attempt at the *intended* foraging intensity (one attempt per cycle at K):

```
c_read = P·E / A_target,   A_target = K/31 = 5.8/tick
       = 645 / 5.8 ≈ 111
```

That is far too high — it would exceed a full cycle's cost and make a single failed read lethal. The tension is real: `c_read` cannot simultaneously be low enough to survive a failure and high enough to prevent escalation. **This confirms that cost cannot be the regulator and the memory cap must be.** Set `c_read = 10` — enough that spamming is wasteful, low enough that a failed read is survivable, with memory scarcity doing the actual work of bounding effort.

(The M1 cost table in §2a already uses `c_read = 10`.)

---

## 6. Copy fidelity: making the claim true

Per-COPY_UNIT mutation is necessary but insufficient — with a copy pointer `P` that only increments, no genome can re-copy or verify a position, so error rate is not a selectable trait.

**Add:**

```
SET_P Rn        cost 1      sets the internal copy pointer to the value in Rn
READ_GESTATION Rn, Rm   cost 2   reads the instruction at gestation offset Rn into Rm
```

With these, a verify-and-retry loop is expressible: copy, read back, compare, and if they differ, `SET_P` back and re-copy. Such a lineage pays roughly 3 extra units per instruction copied — about 33 extra units per cycle for L=11, over 40% of cycle cost — in exchange for a substantially lower effective mutation rate. Whether that trade is worth paying is exactly the kind of question the system should answer rather than presuppose, and at these numbers it is genuinely close, which is the right place for it to sit.

**Process note:** this claim ("copy fidelity is selectable") has now been asserted in two consecutive revisions without the enabling instruction existing. Worth a standing rule: every claimed evolvable capability must name the specific instruction sequence that expresses it, written out, before the claim goes in a document.

---

## 7. Final parameter set

| Parameter | Value | Source |
|---|---|---|
| `P` (packets/tick, constant) | 5 | §4, free scale choice |
| Packet size `S` | 256 B | unchanged |
| `E_rich` | 129 | §4, from K target |
| `E_lean` | 25 | §4a, from K_lean ≥ 35 |
| Buffer depth | 8 | ≥ P, smooths arrival |
| `MEMORY_POOL` | 80 KB | §5c, caps foraging effort |
| `R₀` | 100 | §4b, ≈ 2 × R* |
| `c_read` | 10 | §5d |
| `c_transform` | 3 + len/64 | unchanged |
| `c_copy_unit` | 2 | unchanged |
| `c_divide` | 5 | unchanged |
| `BASE_UPKEEP` | 0.1/tick | unchanged |
| `MEMORY_COST_DIVISOR` | 640 | unchanged |
| Dormant upkeep | 10% of active | unchanged |
| μ (substitution, per COPY_UNIT) | 0.001 | unchanged |
| Transfer at DIVIDE | 50%, or heritable (§3b) | recommend heritable |
| Population cap | 500 | administrative safety only; K ≈ 180 |
| **Derived: C (M1 cycle cost)** | **79.5 units / 31 ticks** | §2a |
| **Derived: per-capita cost** | **2.56 units/tick** | §2a |
| **Derived: R\*** | **≈ 50** | §3 |
| **Derived: K_rich** | **≈ 180** | §4 |
| **Derived: K_lean** | **≈ 35** | §4a |
| **Derived: viable band** | **L ∈ [11, 40]** | §2b |

---

## 8. What this derivation cannot settle

Three things need simulation, not algebra:

1. **K under contention.** The mean-field calculation assumes every organism attempts one read per cycle at a uniform rate. Real capture is bursty and correlated with cycle phase; variance in capture will kill organisms the mean-field model says are viable. Expect the true K to land **below** 180 — possibly 120–150. Treat 180 as an upper bound.

2. **The evolved equilibrium is not the seeded one.** M1's cost profile is the *starting* condition. Selection will push toward shorter cycles and higher attempt rates until memory binds, which raises per-capita cost and lowers K. The equilibrium parameters must be re-measured after the population has adapted, not read off from the ancestor.

3. **Whether the memory cap actually holds.** §5b is an argument, not a proof. If organisms find a way to forage without holding a buffer — reading directly into the minimum block, or sharing buffers once §7-stage interaction is enabled — dissipation returns. The single-resource control (Experiment C) is the test: if it does *not* go extinct, the dissipation analysis is wrong somewhere and the multi-resource necessity claim fails with it.

**Recommended next step:** a population-level paper trace — 20 organisms, 200 ticks, shared packet buffer and memory pool, tracked per-organism — before writing code. Every error found in the last three passes was invisible at single-organism scale and obvious at population scale.