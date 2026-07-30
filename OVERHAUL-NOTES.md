# Substrate — v3 Code Overhaul Notes

Alignment pass of the Python codebase against `project-report.md` (the
authoritative v3 specification). Date: 2026-07-27.

---

## 0. What was actually divergent

The divergence checklist supplied with the task describes the **stale** copies
of the source files. The current `consts.py` and `datastream.py` already match
the report. The real work was in `transforms.py`, `organism.py` and `engine.py`.

| File | Status |
|---|---|
| `consts.py` | Already compliant. **Two additions only** (see §1). |
| `datastream.py` | **No changes required.** Already E=300/300, runs-of-3 rich, sawtooth lean. |
| `transforms.py` | Rewritten — added the reconstruction check. |
| `organism.py` | Rewritten — extraction gate, drawn-cap, expansion write, tau, trough, memory. |
| `engine.py` | Rewritten — MOV destination, COPY_BLOCK, single memory release, cost on failure. |
| `organism (1).py` | Delete. Duplicate. |
| `pyproject.toml` | Unreviewed (not in the uploaded set beyond the stale copy); no code dependency. |

---

## 1. `consts.py` — two additions

Everything else is unchanged.

```python
MAX_OPCODE = COPY_BLOCK        # inclusive bound for mutation; was hardcoded 22
OFFSPRING_TROUGH = 18          # report 1a: under-endowed offspring die
DEFAULT_TRANSFER_R5 = 128      # tau = R5/256, fallback when R5 out of range
```

`MAX_OPCODE` matters: the stale mutation code used `randint(0, 22)`, which
made `COPY_BLOCK` (opcode 23) unreachable by mutation.

---

## 2. `datastream.py` — no changes

Verified against report §1b:

- rich packets: runs of exactly 3 identical bytes, `s_min = 64`
- lean packets: sawtooth `(i*7 + tick) % 256`, `s_min = 15`
- both carry `PACKET_E_RICH = 300`
- constant arrival at `PACKET_RATE = 5`, buffer depth 8

One observation, not a change: `generate_packet()` increments
`next_packet_id` and then calls `_rich_packet()` / `_lean_packet()`, which
each read `self.next_packet_id` *after* the increment. Packet IDs are
therefore still unique (they advance by one per packet) but are offset by one
from the value assigned in `generate_packet`. Nothing depends on the absolute
value, so this is cosmetic. Flagging it rather than changing it, since the
report does not specify ID semantics.

---

## 3. `transforms.py` — reconstruction check

Added `can_reconstruct(op, original, transformed) -> bool`, plus inverse
functions `_rle_decode`, `_diff_decode`, `_base_decode`.

The check is mechanical: attempt to reconstruct the original bytes from the
transformed output, and compare. It never inspects meaning, and there is no
whitelist of approved opcodes — `HASH_SUM` and `FILTER_LOW` fail because they
have no inverse, not because they are named.

`_base_encode` is genuinely ambiguous for some inputs (a packed nibble pair
whose high nibble is 15 collides with the escape marker). Rather than change
the encoder — which would be adding a feature the report does not specify —
the decoder is best-effort and the byte comparison decides. Where BASE is not
invertible for a given input, no energy is granted. This is the correct
structural behaviour.

---

## 4. `organism.py`

### 4a. Extraction gated on losslessness

`apply_transform` now calls `can_reconstruct()` and grants replenishment only
when it returns `True`. A lossy transform may still reduce the memory
footprint — and therefore upkeep — but yields no energy.

### 4b. Expansion charge capped by `packet_drawn`

`packet_drawn: dict[int, float]` is now maintained per packet. On expansion
the charge is `min(|delta|, drawn)`, the packet's budget is credited by the
same amount, and `drawn` is decremented. On a fresh packet nothing has been
drawn, so the charge is zero and the instruction is merely wasted (~7 units of
instruction cost). This is what makes the switcher's RLE probe survivable in
the lean phase.

The per-packet ledger is closed: total extraction over a packet's lifetime
cannot exceed `E_p`, and compress/expand cycling nets zero minus instruction
costs.

### 4c. Expansion leaves the original data intact

On `new_size > length` the handler now writes **nothing**. The original packet
bytes remain in memory so a subsequent transform can process them — this is
the fix that makes the switcher's DIFF fallback operate on the real packet
rather than on RLE-expanded garbage.

`R3` (byte reduction) is therefore `0` on expansion, which is what the
switcher's `JUMPNZ R3` branch depends on. `R4` receives `replenishment × 10`.

### 4d. Heritable transfer fraction

`transfer_fraction()` returns `R5 / 256`, falling back to `128/256` when `R5`
is outside `(0, 256)`. The hardcoded `0.5` is gone.

### 4e. Offspring trough

Offspring endowed with less than `OFFSPRING_TROUGH` (18) units are **not
created**. The parent has already paid the transfer and it is destroyed —
this is deliberate. If the transfer were refunded, low `tau` would be free and
there would be no selection pressure against it, which would remove the
interior optimum reported in §5e. Stillbirths are counted per organism and per
substrate.

There is no clamp. `tau` is whatever `R5` says.

### 4f. Memory: exactly one release path

- `corpse_pool` is now a **list** of `(size, tick)`, not a dict keyed by
  address. The dict silently lost memory whenever two organisms shared an
  address — and every organism has an allocation at address 0, so this was the
  bulk of the leak in §4f of the report.
- `remove_organism()` is the single release point: it moves allocations to the
  corpse pool and clears them. It is idempotent (returns early if already
  dead).
- The displacement path in `reproduce()` no longer adds to
  `shared_memory_pool` directly.
- `allocate_memory()` and `free_memory()` now draw from and return to the
  shared pool, so `MEMORY_POOL` is a real contested resource as §1c specifies.
- `TRANSFORM` returns the bytes it reclaims on compression to the pool.
- The minimum block at address 0 cannot be freed.

Unspent packet budget is destroyed when the last tagged byte leaves memory
(`_forget_absent_packets`).

### 4g. READ is all-or-nothing

`read_packet` requires `PACKET_SIZE` bytes of valid allocated range. A partial
read fails rather than partially succeeding, so an organism cannot forage out
of its 64-byte minimum block.

---

## 5. `engine.py`

### 5a. MOV destination is a literal register index

Report §4e. `dst = args[0]`, not `_get_reg(args[0])`. Source still resolves
through `_get_reg`, so `MOV 5, 51` sets `R5 = 51` and `MOV 0, 1` copies `R1`
into `R0`, per the existing convention.

The same fix is applied to `ADD`/`SUB`/`AND`/`OR`/`XOR`/`READ_GESTATION`,
which had the identical bug.

### 5b. COPY_BLOCK implemented

Copies `n` instructions (from `R6`, defaulting to the whole genome) in one
tick. Cost `2 + n/64`, with `n` clamped to the instructions actually remaining
so the energy charge matches the work done. Substitution mutation is applied
**per instruction copied**, not per invocation, so copy fidelity is neutral
with respect to block size and processivity trades purely on tick cost.

Sets `R2 = 1` when the copy pointer reaches the end of the genome, so the
`JUMPZ R2` loop exits identically to the `COPY_UNIT` version.

### 5c. Cost is paid on failure

Instruction cost is now deducted regardless of whether the instruction
succeeded. Under the old ordering a failed instruction returned before the
deduction, which made failed `READ`s free — that would have removed the
penalty on foraging attempts entirely.

### 5d. Single memory release in `step()`

The reaper loop now only deletes dead organisms from the dict. It no longer
re-adds their allocations to the shared pool, since `remove_organism()` has
already moved them to the corpse pool. Corpse memory returns to the pool once,
on TTL expiry.

### 5e. Gestation buffer does not persist

`DIVIDE` clears the gestation buffer. The persistent-buffer design was
rejected as a free lunch (report §5e, superseded claims) — each offspring
costs its own copy pass. Multiple DIVIDEs per cycle come from the parent
retaining `1 - tau` of its reserve, not from a shared buffer.

### 5f. Seed genomes

- `seed_m1` — L=11 reference metaboliser, `COPY_UNIT` loop
- `seed_m1_block` — L=12, `COPY_BLOCK`, `R5`/`R6` initialised
- `seed_switcher` — L=14, probes RLE and falls through to DIFF on `R3 == 0`
- `seed_bare_replicator` — L=5, no metabolism, dies as expected

`ALLOC_OFFSPRING` resets `divides_this_cycle`, which gives the per-cycle `k`
measurement the report's §5e says is needed (the previous counter was a
per-lifetime artifact). `Simulation.divide_stats()` reports population mean
`k`, the fraction reproducing, and mean `k` among reproducers separately.

---

## 6. What I did not change

- No new instructions beyond `COPY_BLOCK`, which the report specifies.
- No change to the phase schedule, packet structures, or energy budgets.
- No efficiency-assay genotype. §5e lists that assay as an open question, not
  as specification; it is expressible with existing genomes by giving one
  genotype `TRANSFORM ... 128` instead of `256`.
- `_base_encode` left as-is despite its ambiguity (see §3).

---

## 7. Verification I could not run

The Linux sandbox was unavailable during this pass, so the code has not been
executed. Before trusting any run, check:

1. `python transforms.py` — should print, for a rich packet, `RLE` lossless
   with a positive extraction and `DIFF` expanding with zero; for a lean
   packet, the reverse. `HASH_SUM` and `FILTER_LOW` lossless=False in both.
2. `python engine.py` — M1-block should reach a stable population well below
   the 500 cap, with `k_mean_reproducers` above 1 and `shared_memory_pool`
   fluctuating rather than monotonically falling. A monotonically falling pool
   means a release path was missed.
3. Hand-trace one M1 cycle and confirm cycle cost and tick count against
   report §1d (79.3 units over 31 ticks for L=11).

Note that with the memory leak fixed, realised `K` should now rise toward the
mean-field ~423 rather than being capped near 256 — so §2a's measured `K`
values are not directly comparable to new runs, and §1d's caveat about the
leak no longer applies to output generated with this code.