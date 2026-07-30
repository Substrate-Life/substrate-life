# Substrate — Stage 3 Completion Report

*Current model, empirical findings, and superseded claims.*
*Date: 2026-07-26*

---

## 1. Current Model

### 1a. Instruction Set

| Instruction | Opcode | Base Cost | Notes |
|-------------|--------|-----------|-------|
| NOP | 0 | 1 | |
| JUMP | 1 | 1 | Literal target address |
| JUMPZ | 2 | 1 | Check register, literal target |
| JUMPNZ | 3 | 1 | Check register, literal target |
| MOV | 4 | 1 | dst, src registers |
| ADD/SUB/AND/OR/XOR | 5-9 | 2 | |
| CMP | 10 | 2 | |
| READ | 11 | 10 | Reads packet into working memory; 256 bytes required |
| WRITE | 12 | 2 | |
| ALLOC | 13 | 1 + size/64 | Allocates memory; address stored in R1 |
| FREE | 14 | 1 | Frees allocation; cannot free minimum block [0,63] |
| TRANSFORM | 15 | 3 + len/64 | Applies transform. Byte reduction → R3. Replenishment → R4. |
| SLEEP | 16 | 1 | Enter dormancy for N ticks |
| DIE | 17 | 1 | |
| ALLOC_OFFSPRING | 18 | 5 + size/64 | Allocates gestation region |
| COPY_UNIT | 19 | 2 | Copies one instruction per tick; R2=1 when done |
| DIVIDE | 20 | 5 | Finalises offspring, applies indels, transfers 50% reserve |
| SET_P | 21 | 1 | Sets copy pointer to register value |
| READ_GESTATION | 22 | 2 | Reads instruction at gestation offset into register |

**REPRODUCE removed (replaced by ALLOC_OFFSPRING + COPY_UNIT + DIVIDE).**

### 1b. Energy Model

**Income:** Packets arrive at constant rate P=5/tick. Each packet carries an extractable energy budget (E=300). Extraction is granted only for **lossless** transforms (reconstruction check: original bytes must be recoverable from the transformed output). HASH_SUM and FILTER_LOW are lossy — they reduce memory footprint but do not extract energy. Rich and lean phases differ in data structure (runs of 8 vs sawtooth) but share the same budget — no separate E_lean constant.

**Costs:** Per-tick upkeep = 0.1 + memory_bytes/640. Instruction costs as listed. Cycle cost for reference metaboliser M1 (L=11): 79.3 units over 31 ticks.

**Signed extraction:** Compressing tagged bytes draws from the packet budget. Expanding tagged bytes charges the organism's reserve. The per-packet budget is closed — total extraction over the packet's lifetime cannot exceed E_p.

**Tagging:** Bytes carry a packet ID. Copies share the same ID and budget. Memory freed via transform reclamation resets tracking.

### 1c. Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| P (packets/tick) | 5 | Constant, independent of population |
| Buffer depth | 8 | |
| E_rich | 300 | |
| E_lean | 300 (same budget, different structure — see §4) | Structure, not budget, distinguishes phases |
| MEMORY_POOL | 80 KB | Safety rail, not foraging regulator |
| R₀ (founder reserve) | 100 | |
| μ (substitution per COPY_UNIT) | 0.001 | |
| μ (indels per DIVIDE) | 0.01 | |
| Transfer at DIVIDE | 50% | |
| Population cap | 500 | At K≈423, the cap is likely binding — no longer purely administrative. Report as ecological parameter. |

### 1d. Derived Quantities (at E=300)

| Quantity | Value | Notes |
|----------|-------|-------|
| M1 cycle cost C | 79.3 units / 31 ticks | Verified |
| Per-capita cost | 2.56 units/tick | |
| R* (at f=1) | ~220 | I - C = 300 - 79.3 |
| R* (at f=0.86, K ≈ 180) | ~179 | At K density; margin ≈ 10× trough |
| R* (at f=0.58, N=268) | ~94 | Typical competition-run density |
| Trough spend | ~18.4 | Costs before extraction arrives |
| Viable band | L ∈ [11, 40] | Ceiling set by copy cost (3L), not mutation |
| K (mean-field) | ≈ 423 | K = 31·P·E/110; actual K lower due to contention |
| f_crit | 0.081 | f_crit = 24.2/E = 24.2/300 |
| N_crit (overshoot) | ≈ 660 | Beyond this, f < f_crit — unrecoverable |
| Note: K ≈ 423 and N_crit ≈ 660 are derived from the mean-field model and have not been empirically verified at E=300. The competition run reached N=286 without crashing, which is consistent with N_crit > 286 but does not validate the specific value.

---

## 2. Empirical Findings

### 2a. Substrate Validation

All findings in this section were measured at the parameters specified. The model evolved through multiple parameter revisions; §3 lists superseded claims.

- **Population self-sustaining** through Phase A/B/C cycles at E=300/105 (E_lean=105, later raised to 270). No founder-decay extinction. [Parameters: E_rich=300, E_lean=105/270, P=5, R₀=100]
- **Density dependence** measured at E_rich=129: K ≈ 144-173 (below administrative cap of 500). At E=300, expected K ≈ 423 by mean-field but not yet empirically verified. [Parameters: E=129 for measurement; E=300 for prediction]
- **Boom-bust cycles** at phase transitions at E_rich=129, E_lean=25: population dropped from ~150 to ~14 during lean phase, recovered. At E_lean=105, the trough was ~84 (higher floor). At E=300/270, the trough is expected to be much shallower (~300 income vs 80 cost, so organisms stay viable throughout). [Parameters: E=129/25 or E=129/105 — not E=300]
- **0/20 extinction rate** across random seeds at E=300/105. Single-organism bottleneck occasionally but always recovers. [Parameters: E_rich=300, E_lean=105]

### 2b. Graded Selection (50/50 Competition Assay)

Two genotypes: M1 (clean, 1 TRANSFORM) and waste-TRANSFORM (M1 + extra TRANSFORM on depleted buffer, cost ~7 units/cycle). Seeded 50/50, E=300, N≈268 at t=1000 where R* ≈ 94, margin ≈ 5× trough.

| Checkpoint | Waste frequency | Status |
|-----------|----------------|--------|
| t=500 | 29.9% | |
| t=1000 | 32.1% | Pre-registered checkpoint — inconclusive (between 30% pass, 40% fail) |
| t=2000 | 13.7% | Post-hoc extension — clear downward trend |

**Conclusion:** Graded selection is real at a ~5× R*/trough margin (the margin during the assay). The pre-registered t=1000 checkpoint was inconclusive; the trend continued to 13.7% at t=2000. Realised selection was roughly half the predicted rate (cost-to-s conversion off by ~2×, likely because the 7-unit cost is a smaller fraction of the higher cycle cost at E=300, and the 1-tick cycle-length difference compounds).

### 2c. Selection Cliff

At tight margins, cost-adding traits are lethal rather than graded. The observable outcome is threshold culling plus mutational drift, with no regime in which small fitness differences accumulate.

**Measured at:** E=129, M1 L=11, no NOPs. R* = 129 - 79.3 = 49.7. Trough = 18.4. Ratio ≈ 2.7×. With three cost-1 NOPs in the execution path (L=14), R* dropped to ~40.5, which is still above trough. The cliff only appeared when NOPs were placed after DIVIDE (adding 3 ticks and 3 units per cycle), pushing R* close to trough. The true R*/trough ≈ 1 regime was not directly measured — it was inferred from the NOP test where the population crashed at the Phase B transition because the extra cost pushed cycle cost past the viability threshold.

This is the **R*/trough ratio as control parameter** — a genuine finding about computational substrates, not a tuning note. The data supports the direction (higher ratio → graded selection visible) but not a functional form.

### 2d. NOP Padding Assay

Zero-cost NOPs (no selection coefficient) and cost-1 NOPs (~0.3% per NOP) erode at identical rates (~2.96 → 2.67 over 1000 ticks). The erosion is pure mutation load filtering — deletions that land in non-lethal positions survive to be counted, deletions in coding sequence vanish with their lineage. The assay had no statistical power at s≈0.3% over 30 generations with N≈120 and ~0.3 mutation events per lineage.

---

## 3. Superseded Claims

| Claim | Document | Status | Reason |
|-------|----------|--------|--------|
| Lossless-only replenishment rule | v2 energy model | Removed | Replaced by reconstruction check — structural, not designer-favoured |
| Memory pool regulates foraging | v3 §5 | Withdrawn | Instruction budget binds first (1 instr/tick); effort doesn't escalate under r-maximisation |
| C-vs-D prediction (single-resource goes extinct) | v3 §5 | Withdrawn | Not supported by r-max analysis; effort minimises to viability floor, no dissipation |
| Prediction (2): life-history response to density | r-max §6 | Retracted as untestable | Adding a forage block requires 4 coordinated instructions — unreachable at μ=0.001 |
| Wasteful-ancestor test (2-forage seeding) | Discussion | Never ran | Fitness valley; second block is net profitable, not wasteful |
| Trough-of-1 measurement artifact | Stage 3 test | Corrected | Sampled fresh simulation (tick 0, N=1), not Phase B bottleneck |
| N=1 dose-response on discriminative test | Stage 3 test | Corrected | Two arms demographically incomparable; zero-cost NOP discriminator returned null |
| Mutation-dominated substrate | Stage 3 draft | Corrected | At tight margins, cost-adding traits are lethal rather than graded |
| HASH as universal transform | Stage 3 discussion | Removed | Reconstruction check denies extraction to lossy transforms |
| R* = 2I − C form | v3 §3 | Corrected | Income placement relative to DIVIDE changes equilibrium by 2×; correct form is R* = I − C |
| Pre-registration checkpoint shift | This report | Acknowledged | t=1000 (32.1%) inconclusive; t=2000 (13.7%) reported as post-hoc extension |
| s-estimate ~2× too high | This report | Acknowledged | Cost-to-s conversion off — 7-unit cost is smaller fraction of higher cycle cost at E=300 |
| Stage 4 functionally complete | Discussion | Confirmed | Continued existence requires ongoing READ engagement; dormancy is conservation, not loophole |

---

## 4. Project Files

All files at `/opt/data/avida-life/`:

| File | Content |
|------|---------|
| `boundary-model.md` | Organism definition, state machine, instructions |
| `genome-viability.md` | Viable band [11, 40], cycle cost 79.3 |
| `metabolism-model.md` | Per-packet budgets, signed extraction, reconstruction check |
| `energy-model-v3.md` | Derived parameter set |
| `r-max-analysis.md` | Foraging effort, overshoot threshold N_crit ≈ 286 |
| `src/engine.py` | Main simulation loop |
| `src/organism.py` | Organism VM and substrate |
| `src/datastream.py` | Packet generation with phased energy budgets |
| `src/transforms.py` | Transform functions and reconstruction check |
| `src/consts.py` | Constants and parameters |

## 5. Pending Items (for Stage 5)

| Item | Status | Notes |
|------|--------|-------|
| E_lean = 300 same-budget-different-structure | Not implemented | datastream.py needs lean packets where RLE fails but DIFF succeeds. RLE extraction ≈ 0, DIFF extraction ≈ 300. |
| Lean-packet verification | Not run | Verify empirically: RLE-only organism gets near-zero extraction on lean packets; DIFF organism gets most of E. |
| Phase-sensing TRASNFORM (R3 register) | Implemented | TRANSFORM stores byte reduction in R3. Verified: HASH generates R3=224 with zero extraction. |
| Three-arm competition (RLE, DIFF, switcher) | Not run | Pre-condition for Stage 5. Tests whether switchers outcompete specialists under alternation. |
| Re-run validation at E=300 | Not run | §2a findings are from E=129/105 era. K, density dependence, boom-bust cycles need re-measurement at E=300. |