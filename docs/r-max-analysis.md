# Substrate — Foraging Effort under r-Maximisation

*Settles whether effort escalation is self-limiting, whether the memory pool is load-bearing, and whether the C-vs-D prediction survives. Supersedes §5 of energy-model-v3.md.*

**Current status (2026-07-28):** the population-fitness critique of standing reserve remains useful, but the numerical viability, `B`, `K`, and overshoot calculations below are historical parameterisations. They included a designer-specified offspring trough that has now been removed. Current offspring viability must emerge longitudinally from genome- and scheduler-specific execution; these numerical values require fresh derivation before use.

---

## 0. Results

| Question | Answer |
|---|---|
| Does foraging effort escalate to rent dissipation? | **No.** `r` is maximised by the *minimum* viable foraging effort. Extra effort is pure fitness loss. |
| Is the memory pool the binding regulator? | **No.** It is a safety rail. The regulator is the time budget: ticks spent foraging are ticks not spent copying. |
| Does single-resource Experiment C go extinct? | **Not by this mechanism.** The prediction is unsupported and must not be pre-registered. |
| Is the system therefore safe? | **No — a different instability exists.** Overshoot past N ≈ 286 is unrecoverable. See §5. |

---

## 1. Parametrisation

Let `n` = number of forage attempts per reproductive cycle (the effort trait under selection), `L` = genome length.

**Forage block** (per attempt): ALLOC(5) + READ(10) + TRANSFORM(7) + FREE(1) = **23 units, 4 ticks**.

**Reproduction block**: MOV(1) + ALLOC_OFFSPRING(6) + copy loop `3L` + exit JUMPZ(1) + DIVIDE(5) + JUMP(1) = **14 + 3L units, 5 + 2L ticks**.

```
T(n, L) = 4n + 5 + 2L                    ticks per cycle
C(n, L) = 24.2n + 15.5 + 3.6L            total cost per cycle (instructions + upkeep at ~0.3/tick)
I(n)    = n · f · E                      income per cycle
```

Validation against energy-model-v3 §2a (M1: n=1, L=11): T = 31 ✓, C = 79.3 vs. 79.5 ✓.

---

## 2. The fitness currency

The earlier analysis used steady-state reserve `R* = I − C` as the fitness proxy. That is wrong, and it is the whole source of the false dissipation result. `R*` is standing capital; fitness is the rate of increase.

Under binary fission with one offspring per cycle, the population doubles every `T`:

```
r(n, L) = ln 2 / T(n, L)
```

**`r` contains no income term.** Income does not enter fitness as a magnitude — it enters as a **constraint**. An organism either has enough reserve to complete a cycle or it does not. Above that line, more income buys nothing; below it, the lineage dies.

So the problem is not a smooth trade-off between income and cost. It is:

```
maximise    r = ln 2 / (4n + 5 + 2L)
subject to  I(n) ≥ C(n) + G(genome, scheduler, ecology)
```

`r` is **strictly decreasing in `n`**. Therefore:

> **Selection favours the smallest `n` that satisfies viability. Any foraging effort above the minimum is a direct fitness loss.**

This reverses the earlier conclusion completely. Under `R*`-maximisation, effort escalates without bound because more foraging always means more standing reserve. Under `r`-maximisation, effort is pushed *down* to the viability floor because every extra forage attempt costs four ticks of generation time. There is no rent dissipation, with or without a memory cap.

---

## 3. The minimum viable effort

In the historical parameterisation the viability constraint was written `n·(fE − 24.2) ≥ B`, with

```
B = 15.5 + 3.6L + G
```

`G` must be derived from the actual offspring genome, birth-tick scheduling, allocation path, instruction costs, and upkeep until first positive extraction. It is not an interpreter constant and is not generally fixed across an evolving population. The former substitution of a static `trough` and the resulting **B ≈ 79** value are superseded.

```
n_min = ceil( B / (fE − 24.2) )
```

Net yield per attempt is `fE − 24.2`. Note the hard floor: if `fE ≤ 24.2` — i.e. `f ≤ 24.2/E = 0.188` at `E = 129` — no value of `n` is viable, because each attempt costs more than it returns. Call this **`f_crit = 0.188`**.

### 3a. Equilibrium at K

Capture success is `f = min(1, P·T(n) / (N·n))`.

Solving the two conditions jointly at `E = 129`, `P = 5`, `L = 11`:

| f | fE | net/attempt | n_min | T | N at that f |
|---|---|---|---|---|---|
| 1.00 | 129 | 104.8 | 1 | 31 | 155 |
| 0.86 | 111 | 86.8 | 1 | 31 | **180** |
| 0.60 | 77 | 52.8 | 2 | 35 | 146 |
| 0.39 | 50 | 25.8 | 4 | 43 | 276 |
| 0.25 | 32 | 7.8 | 11 | 49 | 89 |
| ≤0.188 | ≤24.2 | ≤0 | ∞ | — | collapse |

At `f = 0.86`, `n = 1`, `N = 180` — consistent with `K ≈ 180` from energy-model-v3 §4. The equilibrium is **stable against high-effort invaders**: an `n = 2` mutant has `T = 35` against the resident's 31, so `r` is 11% lower, and it gains nothing because `n = 1` already clears viability. It is outcompeted. ✓

---

## 4. Why the memory pool is not load-bearing

Two independent reasons the §5 argument in energy-model-v3 fails:

**Effort doesn't escalate.** Established above. Memory scarcity caps something that selection was never driving up.

**The instruction budget binds first anyway.** One instruction per tick means a forage attempt takes at least 4 ticks, so per-organism attempt rate cannot exceed `1/4` per tick and total `A ≤ N/4`. At `N = 180` that is 45/tick against a dissipation break-even of `P·E/c_read = 64.5`. Structurally unreachable, memory pool or not.

**Recommendation:** keep `MEMORY_POOL = 80 KB` as a containment guarantee and a source of genuine contention between concurrent buffers, but drop the claim that it regulates foraging or that multi-resource design is *necessary for viability*. It is not doing that work.

---

## 5. The real instability: unrecoverable overshoot

The commons problem is real, but it manifests through a different mechanism, has a different threshold, and needs a different fix.

As `N` rises, `f` falls, which raises `n_min`, which lengthens `T`, which lowers `r`. That is a stabilising negative feedback via life history — population growth slows itself by forcing lineages into slower, more foraging-heavy strategies. Damped oscillation, not collapse. Good.

**But the feedback has a cliff.** Once `f < f_crit = 0.188`, *no* strategy is viable, and increasing `n` cannot help because each attempt is net-negative. Total extinction, and it is unrecoverable — the population cannot forage its way out.

Solving for the overshoot threshold with `n` adjusting to its minimum viable value:

```
f = P·T(n) / (N·n) = 0.188   with n → large, T = 4n + 27

N_crit ≈ 286
```

**So: `K ≈ 180`, extinction threshold `≈ 286`, population cap 500.** An overshoot of 60% above carrying capacity is fatal and permanent. Given that the founder population starts far below `K` with `f = 1` and every lineage thriving, overshoot is not a remote scenario — it is the expected behaviour of a population growing into an empty environment with a ~31-tick reproductive lag.

### 5a. Fixes, in preference order

1. **Set the population cap below `N_crit`.** A cap of 250 makes overshoot survivable. Honest caveat: the cap is then load-bearing rather than administrative, and should be reported as an ecological parameter, not a safety limit.

2. **Buffer the resource supply.** Raise buffer depth so unconsumed packets accumulate during low-`N` periods and are drawn down during overshoot. This is a genuine stock-vs-flow fix and is the most biologically honest option — real environments have standing resource stocks. Requires packets to persist across ticks with an expiry.

3. **Reduce `f_crit` by lowering `c_read`.** `f_crit = c_forage/E`, so cheaper foraging widens the viable band. At `c_read = 4`, forage block cost drops to 17 and `f_crit` falls to 0.132, pushing `N_crit` to ~410. Cheap, but weakens the penalty on failed reads.

4. **Do nothing and let the first populations go extinct.** Defensible — extinction is a legitimate result per the original spec §12 — but wasteful if it happens in every run for a reason you already predicted.

I would take (1) and (2) together: cap at 250 and give packets a standing stock with expiry.

---

## 6. Consequences for the experimental protocol

**Withdraw the C-vs-D prediction.** "Single-resource populations dissipate their income and go extinct while multi-resource populations persist" is not supported. If pre-registered it would fail on first test, and it would fail for a reason already knowable from algebra — the worst kind of pre-registration failure.

**What can be pre-registered instead**, all derived and falsifiable:

1. **Minimum-effort selection.** Populations converge to the lowest `n` consistent with viability. Under abundance (`f → 1`) the modal genome carries exactly one forage block per cycle; effort rises stepwise only as `f` declines. Directly measurable as forage-blocks-per-genome versus population density.

2. **Life-history response to density.** `n` and cycle length `T` increase monotonically with `N`, and generation time is a *decreasing* function of resource availability. This is the substantive prediction that replaces the withdrawn one, and it is a real ecological result if it holds.

3. **Overshoot mortality with a threshold.** Populations crossing `N ≈ 286` (at `P=5`, `E=129`, cap ≥ 300) go extinct and do not recover. Populations capped at 250 persist. This *is* a clean pre-registerable dichotomy — and it happens to be a better test of the same underlying idea, since it tests whether the substrate's conservation structure produces genuine ecological limits.

4. **Genome length ceiling.** Modal genome length stays within `[11, 40]`, with the ceiling set by copy cost (`3L` per cycle) rather than mutation load. Distinguishable from the error-threshold prediction, which would put the ceiling near 1000.

---

## 7. What remains unresolved

**Bet-hedging may favour `n = 2`.** The analysis is mean-field. Under stochastic capture, `n = 2` gives two independent draws and lower income variance, which has real value near the viability boundary even at an 11% cost in `r`. The `r`-maximum is `n = 1`; the variance-adjusted optimum could be 2. Bounded and small either way — this does not resurrect dissipation — but it means the modal genome in prediction (1) might carry two forage blocks, and the prediction should be stated as "one or two" rather than exactly one.

**Heritable provisioning (v3 §3b) changes the fitness function.** With transfer fraction fixed at 50%, `r = ln2/T` and the analysis holds. If provisioning becomes an evolvable register value, an organism can produce several under-provisioned offspring per cycle, and `r` gains an offspring-count term. Effort and provisioning then co-evolve and the clean "minimise `n`" result may not survive. I still recommend heritable provisioning — it removes a designer decision — but the effort analysis must be redone in two dimensions `(n, provisioning)` before its conclusions are trusted. Flagging rather than doing, because it needs a proper two-trait ESS and the answer isn't guessable.

**`f` is not a mean field.** Capture is bursty and correlated with cycle phase — organisms that finish a cycle simultaneously contend simultaneously. Real `f` at a given `N` will be lower and more variable than `P·T/(N·n)`, which pushes both `K` and `N_crit` down. Expect `K` in the 120–150 range, as flagged in v3 §8.

---

## 8. Method note

Both errors in this thread's last two passes came from the same source: an accounting rule or fitness proxy that was locally plausible and globally wrong (pay-for-release without charge-for-acquisition; standing reserve instead of rate of increase). Both were invisible at the level of a single organism doing one thing, and obvious once totalled across a population or across a full life cycle.

The check that catches this class of error: **for any proposed rule, close the loop.** Total the flows over a complete cycle and over the whole population, and confirm the books balance with nothing created. Do it before the rule enters a document, not after.