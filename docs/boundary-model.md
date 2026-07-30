# Substrate — Boundary Model

*Stage 1A: Formal definition of the organism/environment boundary.*
*Drafted 2026-07-26. Revised 2026-07-26 (v2: fixed state machine, added metabolism placeholder, removed init budget exploit, added seeding, defined scheduler tick).*

---

## 1. Purpose

This document defines what constitutes an individual organism in the Substrate system — specifically, where the boundary between organism and environment is drawn, what can cross it, and what happens at the edges. The boundary model is the single most consequential design decision because it determines what kinds of individuality, ecology, and evolution are expressible. Getting it wrong means discovering properties of our design choices, not properties of evolution on a computational substrate.

---

## 2. Guiding Principle

The boundary must arise from *resource accounting*, not from semantic judgment. A membrane in biology is not a rule that says "this molecule belongs in the cell" — it is a semi-permeable physical barrier across which concentration gradients do thermodynamic work. The computational equivalent is a ledger boundary: operations inside are accounted to one entity; operations outside are not. Where the ledger boundary is drawn is what we mean by "individual."

---

## 3. Scheduler Tick (Definition)

A **scheduler tick** is the fundamental time unit of the simulation. One tick consists of:

1. Each ACTIVE organism executes exactly one instruction (in round-robin order, with the order randomised each tick).
2. After all ACTIVE organisms have executed one instruction, the following bookkeeping occurs atomically:
   - Data stream packets may arrive (scheduled independently; see Section 15).
   - Per-tick upkeep costs are deducted from each organism's execution reserve (see Section 11).
   - The substrate re-evaluates death conditions (see Section 9).
   - The next tick begins.

A tick is not a wall-clock time interval. It is a logical time step. In real-coupling mode, the *length* of a tick in wall-clock time varies with host conditions; in abstract mode, it is a fixed logical step.

**All timing parameters in this document (SLEEP duration, grace period, corpse decay) are expressed in scheduler ticks unless otherwise noted.**

---

## 4. Organism Anatomy

Each organism is a single addressable entity comprising:

| Component | Volatility | Description |
|-----------|-----------|-------------|
| **Genome** | Durable | A linear sequence of instructions (read-only during execution; copied with variation during reproduction) |
| **Register file** | Working | A small fixed set of general-purpose data registers (R0–R7) |
| **Program counter** | Working | Index into the genome indicating next instruction to execute |
| **Stack** | Working | Bounded operand stack (depth: 16 entries) |
| **Working memory** | Working | A contiguous byte array allocated at birth, readable and writable during execution |
| **Execution reserve** | Working | A scalar representing remaining execution capacity; decremented by each instruction AND by per-tick upkeep; when zero, the organism is marked DEAD at the next tick boundary |
| **Persistent store** | Durable | A small fixed-size byte array that survives across execution suspension |
| **Resource account** | Working | A record of current memory allocation size, persistent store size, and accumulated resource costs |
| **State flag** | Transient | One of: `ACTIVE`, `DORMANT`, `SUSPENDED`, `DEAD` |

An organism is *instantiated* when the substrate allocates the above structures and initialises them. An organism is *destroyed* when the substrate deallocates them and returns the resources to the shared pool.

**State transitions:**
- `ACTIVE` → `SUSPENDED`: scheduler pre-emption between instructions
- `ACTIVE` → `DORMANT`: organism executes `SLEEP` instruction
- `DORMANT` → `ACTIVE`: sleep timer expires, or (Stage 7+) external trigger
- `SUSPENDED` → `ACTIVE`: scheduler resumption at next turn
- `ACTIVE` / `DORMANT` / `SUSPENDED` → `DEAD`: any death condition met (Section 8)
- `DEAD` is terminal; no transitions out

---

## 5. The Substrate Boundary

The substrate is the runtime environment that hosts organisms. It maintains:

| Component | Description |
|-----------|-------------|
| **Shared memory pool** | Total allocatable working memory across all organisms. A hard upper bound prevents runaway allocation. |
| **Shared persistent store pool** | Total allocatable persistent storage across all organisms. |
| **Scheduler** | Decides which organism executes next and for how long. Round-robin with randomised order each tick; each organism executes exactly one instruction per tick. Stochastic pre-emption (interrupting an organism mid-instruction) is drawn from measured host scheduling jitter in real-coupling mode, or from a synthetic distribution in abstract mode. |
| **Data stream buffer** | A sliding window of incoming data packets (size: 256 bytes per packet, buffer depth: configurable, default: 4). New packets arrive at intervals determined by host telemetry or a synthetic schedule. |
| **Corpse pool** | Memory blocks left behind by dead organisms, available for reallocation. Remains for a configurable number of ticks (default: 5) before being reclaimed to the shared pool. |
| **Death register** | A chronological log of recent deaths: genome hash, cause of death, resource holdings at time of death. Not accessible to organisms; recorded only for analysis. |
| **Seeder** | Mechanism for initialising the first population (see Section 14). |

**What crosses the substrate→organism boundary (inbound):**
- Data packets, one at a time, via a `READ` instruction
- Resource allocations (memory blocks, execution slots) granted by the scheduler
- Nothing else. No filesystem, no network, no system calls, no host process access.

**What crosses the organism→substrate boundary (outbound):**
- A new organism, via a `REPRODUCE` instruction (see Section 7)
- Released memory, via a `FREE` or `DEALLOC` instruction
- State flag changes (ACTIVE → DORMANT, etc.)
- Nothing else. No writes to files, no messages to other processes, no system calls.

---

## 6. Boundary Invariants

The following invariants are enforced by the substrate and are not modifiable by any organism:

1. **Exclusive ownership.** Each organism's genome, register file, stack, working memory, and persistent store are accessible only to that organism. No instruction can read or write another organism's state. (Messaging is introduced as a separate, explicit mechanism in Stage 7; it is absent in Stages 1–6.)

2. **No self-modifying genome during execution.** The genome is read-only during execution of an organism. Genome modification (mutation) occurs only during the `REPRODUCE` instruction, and only on the *copy* destined for the offspring, never on the parent's genome.

3. **Resource conservation (partial).** All shared-pool resources (working memory, persistent store) are conserved: allocations subtract from the pool, deallocations add back. Execution reserve is NOT conserved — it is consumed by instruction execution and per-tick upkeep, and discarded on death. Data stream packets are created by the environment and consumed by READ (not conserved). This is not a violation of the ledger model; it reflects the fact that metabolic energy (execution reserve) and environmental information (data packets) have different thermodynamics from structural resources.

4. **No persistent state across substrate restart.** The entire organism population is ephemeral. There is no serialization or checkpointing of organism state. (The *analysis logs* are persistent, and the *substrate itself* is deterministic and restartable — but the population starts fresh.)

5. **Death is irreversible.** A `DEAD` organism cannot be revived. Its resources enter the corpse pool; its genome is logged and then discarded.

---

## 7. Boundary During Execution Suspension

The substrate may suspend an organism between instructions due to scheduler pre-emption. During suspension (state = `SUSPENDED`):

- **Working memory, registers, stack, program counter, and resource account are preserved** in the organism's allocation. These are not reclaimed.
- **The execution reserve is frozen** at its current value.
- **No instructions execute.** The organism cannot be mutated, read, or influenced by the environment while suspended.
- **Per-tick upkeep costs are NOT deducted** while suspended. (Upkeep is a cost of being ACTIVE or DORMANT; suspended organisms incur no costs.)
- **On resumption**, the organism continues from the saved program counter with all state intact.

This is analogous to pre-emptive multitasking. It is *not* the same as dormancy (Section 7a).

### 7a. Dormancy

A DORMANT organism is distinct from a SUSPENDED organism:

- **Dormancy is voluntary.** The organism executes a `SLEEP N` instruction where N is a number of scheduler ticks.
- **Resource costs are reduced but not zero.** A dormant organism consumes per-tick upkeep at a reduced rate (default: 10% of the ACTIVE per-tick cost). See Section 12 for the full upkeep model.
- **The organism cannot be mutated, copied, or interacted with** while dormant.
- **The organism wakes** automatically after N ticks (state returns to ACTIVE). In Stage 7+, it may also be woken by external triggers.
- **Working memory and persistent store persist** during dormancy.

The distinction between suspension and dormancy is: suspension is imposed by the substrate and costs nothing; dormancy is chosen by the organism as a strategy to conserve resources, at the cost of forfeited execution opportunity.

---

## 8. Boundary During Reproduction

Reproduction is the most boundary-sensitive operation. It proceeds in steps:

### 8a. Initiation
The organism executes `REPRODUCE`. This instruction:
1. Checks that the parent has sufficient execution reserve to complete the operation (cost: a fixed number of instruction-equivalent units; default: 5 for the check, plus genome_length × 2 for copy+mutate).
2. Checks that the shared memory pool has sufficient remaining allocation for a new organism's minimum working memory block (default: 64 bytes).

If either check fails, the instruction is a no-op. The cost of the check itself is already deducted from the parent's execution reserve. Execution continues with the next instruction.

### 8b. Genome Copying
The substrate copies the parent's genome into a temporary buffer (not yet attached to any organism). During copying, mutation is applied:
- Per-instruction substitution probability: configurable (default: 0.001)
- Per-genome insertion probability: configurable (default: 0.01)
- Per-genome deletion probability: configurable (default: 0.01)
- Per-genome duplication probability: configurable (default: 0.001)

Mutation rates are a parameter of the substrate, not of the organism (in Stages 1–6; heritable mutation rates may be introduced in Stage 9).

### 8c. Offspring Initialisation
The substrate creates a new organism structure (Section 4) with:
- The copied (and mutated) genome
- Registers zeroed
- Program counter set to 0
- Stack empty
- Working memory: a newly allocated block of minimum size (default: 64 bytes) drawn from the shared memory pool
- Execution reserve: **50% of the parent's current execution reserve**, transferred from the parent to the offspring (the parent loses this amount)
- Persistent store: empty
- Resource account: initialised to reflect the new allocations
- State flag: ACTIVE

**Key design choice — resource transfer, not creation.** The offspring's execution reserve comes directly from the parent's reserve. No separate init budget exists. This means:
- Reproduction has a real, non-trivial metabolic cost.
- A starving parent cannot reproduce (it has no reserve to give).
- A parent that reproduces too often leaves itself vulnerable to death.
- Selection favours parents that accumulate and manage reserves efficiently.

### 8d. Offspring Release
The offspring is added to the scheduler's queue for the next tick. Neither parent nor offspring has any remaining connection to each other. The substrate does not record parentage in any form accessible to organisms (only in the analysis log).

### 8e. Total Resource Cost to Parent
| Component | Cost (instruction-equivalent units) |
|-----------|--------------------------------------|
| Check | 5 |
| Copy + mutate | genome_length × 2 |
| Offspring execution reserve | 50% of parent's current reserve (transferred) |
| Offspring working memory | drawn from shared pool (not from parent's allocation) |
| Offspring persistent store | 0 (offspring starts with empty persistent store) |

The parent's working memory and persistent store are not affected. The parent continues execution with 50% of its previous execution reserve.

---

## 9. Boundary During Death

Death occurs when any of the following conditions is met:

1. **Execution reserve reaches zero** at a tick boundary (checked after per-tick upkeep deductions). The organism is marked DEAD.
2. **Memory allocation failure.** The organism attempts an instruction that requires memory allocation (`ALLOC` or the working-memory portion of `REPRODUCE`) and the shared memory pool is exhausted. The organism does not die immediately; the instruction fails, and the organism has a configurable grace period (default: 10 ticks) to free sufficient memory (via `FREE` or `DEALLOC`). If it cannot, it is marked DEAD. During the grace period, the instruction is a no-op each time it is encountered (the failure is visible to the organism via a status flag, Section 13).
3. **Structural execution failure.** The program counter points to a location outside the genome, or the stack overflows, or an instruction operand is out of bounds. The organism is marked DEAD immediately. These are purely structural conditions — no semantic interpretation of instruction meaning is involved.
4. **Voluntary self-termination.** The `DIE` instruction (included in the instruction set from Stage 1) marks the organism DEAD.

When an organism dies:
- Its working memory block is moved to the corpse pool (Section 5)
- Its persistent store is reclaimed to the shared persistent store pool
- Its execution reserve is discarded (not conserved — see Section 6, invariant 3)
- Its genome is logged (for analysis) and discarded
- The organism structure is deallocated

The corpse pool persists for a configurable number of ticks (default: 5). After that, the memory is returned to the shared memory pool. This creates a window during which other organisms *cannot* access the corpse's contents (no cross-organism access in Stages 1–6) but the memory is unavailable for fresh allocation. In Stage 7, the corpse pool may become accessible via scavenging instructions.

---

## 10. Boundary for Environmental Information

Data packets flow through the shared data stream buffer. An organism reads one packet at a time via the `READ` instruction:

1. The organism specifies a destination in its working memory (address + length).
2. If the buffer is non-empty, the oldest packet is copied into the specified region of the organism's working memory.
3. The packet is then removed from the buffer.
4. If the buffer is empty, the instruction is a no-op (execution cost still paid; the organism can detect this via a status flag — see Section 13).

The organism has no way to inspect the buffer length, peek at packets without consuming them, or control the rate of packet arrival. The data stream is a shared resource: one organism's read consumes the packet, making it unavailable to others. This creates implicit competition for information.

**Boundary check:** If the requested read range (addr + length) exceeds the organism's allocated working memory, the READ instruction fails silently. The FAIL flag is set. No data is copied. The instruction cost is still paid. The organism can detect the failure via the FAIL flag and adjust its behaviour.

### 10a. Packet Content
Data packets are byte strings generated by a deterministic PRNG seeded per simulation run. Each packet is 256 bytes. The PRNG is configured to produce *structured but non-stationary* sequences:
- **Phase A (ticks 0–1000):** Packets contain repeating patterns (e.g., runs of identical bytes, short cycles). High compressibility.
- **Phase B (ticks 1001–2000):** Packets shift to low-order-bit noise derived from a linear congruential generator. Low compressibility.
- **Phase C (ticks 2001+):** Alternating phases of structured and noisy data, with the transition points determined by the simulation seed.

This means:
- The data stream has exploitable regularities, but they change over time.
- An organism that evolves to exploit one phase's structure must adapt when the pattern shifts.
- No single compression or transformation strategy works permanently.
- The substrate never judges whether the organism used the data "correctly" — it only supplies bytes.

In real-coupling mode, the packet generation may incorporate measured host telemetry (e.g., low-order bits of CPU cycle counter XORed with disk I/O timing). In abstract mode, the PRNG-driven sequence is used directly.

### 10b. Why Read? — The Metabolism Coupling
Reading a data packet costs execution reserve (the `READ` instruction itself). But the data acquired is relevant to metabolism:

Organisms incur a **per-tick upkeep cost** proportional to the size of their working memory (see Section 11). By applying `TRANSFORM` instructions (compression, pattern extraction, encoding) to data in working memory, an organism can reduce the effective size of stored data — and thereby reduce its per-tick upkeep. Data from the environment that is *more compressible* or *more amenable to the organism's specific transform repertoire* yields larger upkeep reductions.

Thus:
- Reading costs execution reserve but provides data that may reduce ongoing costs.
- The organism is never told which data is valuable or which transform to use.
- Different lineages may evolve different transform strategies, specialising on different kinds of data structure.
- There is no semantic judgment: the substrate only measures the output size of a transform; it never evaluates whether the organism "understood" the data.

---

## 11. The Metabolism Model (Placeholder for Stage 1C)

This section provides a minimal metabolism mechanism so that the boundary model is complete enough for Stage 1B (genome viability analysis). A full metabolism model will be developed in Stage 1C.

### 11a. Upkeep Cost
Each tick, every ACTIVE organism pays an upkeep cost deducted from its execution reserve:

```
upkeep_cost = BASE_UPKEEP + memory_size / MEMORY_COST_DIVISOR
```

Where:
- `BASE_UPKEEP` = 1 instruction-equivalent unit per tick
- `memory_size` = current allocated working memory in bytes
- `MEMORY_COST_DIVISOR` = configurable (default: 64, so 64 bytes of memory costs 1 extra unit per tick)

DORMANT organisms pay upkeep at 10% of this rate. SUSPENDED organisms pay no upkeep.

### 11b. Transform and Upkeep Reduction
The `TRANSFORM` instruction applies a lossless compression operation to a specified region of the organism's working memory. If the compressed representation is smaller than the original, the organism may:
- Discard the original and keep only the compressed version, OR
- Keep both (paying upkeep on the larger of the two)

The substrate makes no judgment about whether the compression is "good" or "meaningful." It only measures the byte size of the result. An organism that applies a transform that happens to compress the data structure it holds will reduce its upkeep. An organism that applies a transform that expands data or leaves it unchanged gains no benefit.

### 11c. Transform Operations
Proposed transform instructions (subject to revision in Stage 1C):

| Instruction | Operation |
|-------------|-----------|
| `COMPRESS_RLE` | Run-length encode a memory region |
| `COMPRESS_DIFF` | Store differences from a reference pattern |
| `ENCODE_BASE` | Re-encode with a variable-length scheme |
| `FILTER_LOW` | Keep only low-order bits of each byte |
| `HASH_SUM` | Replace a region with a fixed-size hash (lossy; irreversible) |

Each transform operates on a memory region and produces a result of a given size. The substrate makes no judgment about the result — it only measures byte size. Transforms may be lossless (the original can be fully reconstructed) or lossy (information is discarded and cannot be recovered). The choice of which transform to apply — and whether lossy or lossless strategies are more adaptive — is left to evolution.

Proposed transform instructions (subject to revision in Stage 1C):

### 11d. Execution Reserve Replenishment
Execution reserve is **not** replenished by any automatic mechanism. The only way to acquire execution capacity is:
- Start with the amount received from the parent at birth.
- Reduce per-tick costs by keeping working memory small (via transforms).
- Avoid costly instructions when possible.
- Reproduce strategically (offspring receive 50% of the parent's reserve; this does not create new reserve for the lineage, merely redistributes it).

This means the system is *strictly dissipative*: total execution reserve across the population monotonically decreases unless offset by external events (in real-coupling mode, host scheduling pre-emptions might extend available execution — this is one of the measurable differences between abstract and real-coupling modes).

**This is a deliberate design choice for Stages 1–2.** A strictly dissipative system ensures that selection acts on metabolic efficiency (reducing costs) rather than on acquiring external energy subsidies. The absence of automatic replenishment means the population has a finite total lifetime measured in cumulative instruction-execution capacity. This limits the generational depth of experiments but avoids smuggling in a hidden "food source" that could mask degenerate strategies. Replenishment mechanisms may be introduced in Stage 1C for later experiments, but only if the dissipative baseline is understood first.

---

## 12. Instruction Cost Model (Placeholder)

Every instruction costs at least 1 execution unit. Additional costs:

| Instruction | Base cost | Variable cost |
|-------------|-----------|---------------|
| `NOP` | 1 | — |
| `READ` | 2 | — |
| `WRITE` | 2 | — |
| `TRANSFORM` | 3 | memory_region_size × 1 |
| `ALLOC` | 1 | allocated_size / 64 (rounded up) |
| `FREE` | 1 | — | Cannot free minimum block [0,63]; sets FAIL on attempt |
| `SLEEP` | 1 | — |
| `REPRODUCE` | 5 (check) | genome_length × 2 (copy+mutate) |
| `DIE` | 1 | — |
| `JUMP` / `JUMPZ` / `JUMPNZ` | 1 | — |
| `MOV` (register) | 1 | — |
| `ADD` / `SUB` / `AND` / `OR` / `XOR` | 2 | — |
| `CMP` | 2 | — |
| `SEND` / `RECV` | 3 (Stage 7+) | — |

All costs are in instruction-equivalent units and are deducted from the executing organism's execution reserve upon instruction completion.

---

## 13. Organism-Accessible Status Flags

Each organism has a small set of status flags that provide feedback about instruction outcomes:

| Flag | Set when | Cleared when |
|------|----------|--------------|
| `CARRY` | Last arithmetic overflowed | Next arithmetic instruction |
| `FAIL` | Last instruction was a no-op (empty buffer on READ, failed REPRODUCE, etc.) | Next instruction execution |
| `SLEEP_WOKE` | Organism wakes from dormancy | Next instruction execution |

These flags are the *only* way an organism can detect environmental conditions. They provide minimal feedback — enough for conditional behaviour, but not rich enough to replace evolved sensing.

---

## 14. Initial Population (Seeding)

The simulation begins with a seeded population:

1. A single **ancestor genome** is provided as a parameter. The ancestor is hand-designed to contain the minimum machinery for self-replication (a few instructions: `NOP`, `JUMP`, `REPRODUCE` loop) and nothing more — no efficient strategies, no sensing behaviour, no data processing capability.
2. The ancestor is instantiated once with:
   - Execution reserve: 1,000 units
   - Working memory: minimum block (64 bytes)
   - All registers zeroed
   - Program counter: 0
3. On tick 0, the ancestor executes. From this single organism, the population grows through reproduction.
4. Population size is capped at a configurable maximum (default: 500). When the cap is reached, new offspring replace randomly selected existing organisms (mortality by displacement), maintaining constant population pressure.

   **Design note on displacement mortality:** Displacement is a deliberate exception to the ledger-based death model (Section 9). Its purpose is to maintain constant selective pressure regardless of population density — a lineage cannot escape competition by filling a niche and then stagnating. The trade-off is that displacement introduces a death path unrelated to metabolic efficiency. This is acceptable because displacement only activates at the population cap; below the cap, all death is metabolic. The displacement rate is uniform across lineages, so it does not differentially reward any strategy. Alternative mortality models (carrying capacity, resource-mediated culling) may be substituted in controlled experiments.

**Alternative seeding modes** (configurable for specific experiments):
- **Single ancestor** (default): one genome, one organism.
- **Diverse pool**: several distinct ancestor genomes are seeded simultaneously to increase initial diversity.
- **Scrambled inheritance**: reproduction copies the genome but applies no mutation (control condition).

---

## 15. Data Stream Scheduling

Packets arrive on a schedule independent of organism execution:

| Parameter | Default | Notes |
|-----------|---------|-------|
| Packet size | 256 bytes | Fixed |
| Buffer depth | 4 packets | Configurable |
| Arrival interval | Every 5 ticks | Configurable; may be periodic (abstract) or drawn from host timing distributions (real-coupling) |
| Content source | PRNG with seed | Structured non-stationary sequences (Section 10a) |
| Overwrite policy | Oldest packet discarded if buffer full | — |

In real-coupling mode, the arrival interval may vary with host I/O latency measures. In abstract mode, it is exactly every 5 ticks.

---

## 16. Boundary and Individuality: What This Model Permits and Prevents

### Permitted in Stages 1–6:
- **Independent self-maintenance.** Each organism manages its own resources.
- **Competitive reproduction.** Organisms that reproduce faster or more reliably dominate the population.
- **Resource specialization.** Lineages may evolve to use different data transforms or target different data structures.
- **Death-driven turnover.** Resource scarcity culls less efficient lineages.
- **Dormancy as a strategy.** `SLEEP` as a response to resource scarcity.

### Not Permitted until Stage 7+:
- **Communication.** No cross-organism messaging.
- **Parasitism.** Cannot exploit another organism's state or resources.
- **Cooperation.** Cannot exchange resources or divide labour.
- **Scavenging.** Cannot use corpse contents.
- **Distributed individuality.** Two organisms cannot merge or share a resource account.
- **Predation.** Cannot appropriate another organism's allocations.

### Not Permitted ever:
- Cross-organism memory reads/writes
- Access to filesystem, network, or host processes
- Self-modifying genome during execution
- Persistent state across substrate restarts

---

## 17. Formal Boundary Statement

> A Substrate organism is a bounded computation that maintains an exclusive resource account and a mutable internal state, separated from all other organisms by an opaque substrate-enforced membrane. Information crosses this membrane in exactly three ways: (1) environmental data enters via `READ`, (2) an offspring exits via `REPRODUCE`, and (3) resource costs exit via instruction execution and per-tick upkeep. No other transfers are possible. The organism's boundary is therefore defined not by any structure within the organism but by the substrate's commitment to enforce these three transfer channels and no others.

---

## 18. Open Questions (for Stage 1B discussion)

1. **Memory fragmentation.** If organisms are allocated variable-size blocks and freed blocks return to a corpse pool, will the shared pool fragment over time? Should allocation be fixed-size or variable-size?

2. **Minimum viable genome length.** What is the smallest genome that can express a working reproduction loop given the instruction cost model? This must be computed analytically before Stage 1B.

3. **Upkeep divisor tuning.** The MEMORY_COST_DIVISOR (default 64) determines how sharply memory size affects survival. What value produces interesting trade-off dynamics without being either negligible or crippling?

4. **Corpse pool decay.** Is corpse pool memory returned to the shared pool gradually (e.g., one byte per tick) or all at once? Gradual decay prevents sudden population booms after mass death events.