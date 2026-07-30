# Stage 6: Variable Offspring Count — Mechanism Spec

*Minimal mechanism. Mechanism before ESS. ESS defined over this spec.*

## 1. The Constraint

With per-offspring copy loop (current DIVIDE clears gestation buffer), k=1 is always optimal at L=11 because the copy loop adds 26 ticks per extra offspring and ln(1+k) grows sublinearly.

**Fix:** Gestation buffer persists after DIVIDE. One copy loop fills it; k DIVIDEs create k offspring from it. Per-offspring cost drops from 26 to ~2 ticks.

## 2. Mechanism (Minimal Change)

### 2a. DIVIDE semantics change

Current: DIVIDE creates 1 offspring, clears gestation buffer.
New: DIVIDE creates 1 offspring from current gestation buffer. **Buffer persists.** Subsequent DIVIDEs create additional offspring from the same buffer.

### 2b. Transfer fraction from register

DIVIDE reads transfer fraction from R5:
```
transfer_fraction = registers[5] / 256  # heritable, 0-100%
```

Default R5 = 128 (50% — backward compatible with M1).

### 2c. Clamp

```
floor = trough / parent_reserve          # offspring must survive trough
ceiling = 1.0 - trough / parent_reserve  # parent must survive next cycle

if floor >= ceiling:
    # Parent can't fund both offspring and own survival
    DIVIDE FAILS — no offspring created, parent keeps reserve
else:
    effective = clamp(transfer_fraction, floor, ceiling)
    offspring_reserve = parent_reserve * effective
    parent_reserve *= (1 - effective)
```

DIVIDE failure is clean — the parent continues with unchanged reserve.

### 2d. Persistence condition

After DIVIDE, gestation buffer persists if:
- There is still enough reserve in the parent for another DIVIDE (reserve * τ > trough), AND
- The next instruction is a JUMP back to DIVIDE (or another DIVIDE)

The organism controls how many DIVIDEs happen through JUMPZ/JUMPNZ on the loop counter.

### 2e. Example genome (k=3 per cycle)

```
0: MOV R0, 256        # size for buffer
1: ALLOC R0           # allocate buffer → R1 = addr
2: READ R1, 256       # read packet
3: TRANSFORM 0, 1, 256  # RLE transform
4: FREE R1             # free buffer
5: MOV R0, 64         # gestation size
6: ALLOC_OFFSPRING R0  # allocate gestation
7: COPY_UNIT           # copy loop start
8: JUMPZ R2, 7         # until all L instructions copied
9: DIVIDE              # offspring 1 created (gestation persists)
10: MOV R3, 1          # R3 = DIVIDE counter
11: CMP R3, R6         # compare counter with target k
12: JUMPZ R0, 16       # if equal, jump to start
13: ADD R3, 1          # increment counter
14: JUMP 9             # DIVIDE again
15: JUMP 0             # back to start
```

## 3. Fitness Function

```
k = number of successful DIVIDEs per cycle
τ = transfer fraction (R5/256)

T(k) = T_forage + T_copy_once + k * T_per_DIVIDE
     = 4 + 22 + k * 2
     = 26 + 2k     ticks

r(k) = ln(1 + k) / (26 + 2k)

k ∈ [1, k_max] where k_max = floor such that τ * (1-τ)^(k-1) * R* > trough
```

Optimal k at L=11 and R* ≈ 220: k ≈ 5-6 (r peaks near k=5 at T=36, r=ln6/36=0.0498).

## 4. Income→Fitness Channel

Higher income → higher R* → more DIVIDEs before trough constraint binds → higher k → higher r.

```
I = 131 (single rich packet):  R* ≈ 52,  k_max ≈ 2,  r ≈ 0.037
I = 300 (E=300, f=1):          R* ≈ 220, k_max ≈ 6,  r ≈ 0.050
```

Metabolic efficiency enters fitness continuously for the first time in this project.

## 5. Open Questions (for ESS)

1. Does τ evolve as a single-trait optimum at k(τ), or do τ and k decouple through genome structure (multiple copy blocks)?
2. If k is determined by τ and R*, and R* is determined by n (foraging effort), does the minimize-n result from r-max analysis survive?
3. With k>1, the parent's reserve at cycle start is lower (split across offspring). Does this create a fitness valley for the τ→0 transition?