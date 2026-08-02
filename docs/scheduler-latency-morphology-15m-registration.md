# Registration — Fifteen-Minute Scheduler-Latency Morphology Characterisation

## Status and purpose

This protocol is frozen after the exploratory sixty-second pilot and before either fifteen-minute acquisition or any reduction of its raw latency samples.

This is a morphology characterisation, not another physical-sensitivity gate. The withdrawn one-hour protocol and acquisition authorization must not be reused.

No independent static audit is required before execution. The previous audit loop became slower than the implementation it was intended to control. This protocol therefore fixes a small design, retains raw timing values, runs once, and reports every registered endpoint.

## Prior exploratory evidence and falsified prediction

The unregistered pilot measured 3,000 samples per phase at 10 ms cadence:

- idle median deadline lateness: `110,510 ns`;
- loaded median: `80,532 ns`;
- idle p99: `479,359 ns`;
- loaded p99: `1,867,253 ns`;
- p99 ratio: approximately `3.8953`;
- idle maximum: `1,453,835 ns`;
- loaded maximum: `2,903,135 ns`.

The proposal author's prediction that p99 would increase by at least tenfold was falsified. The observed increase was approximately 3.9-fold.

The lower loaded median and higher loaded tail are consistent with two opposing mechanisms: reduced idle-state exit latency on busy cores and increased contention in the tail. CPU C-state residency was not measured, so the warm-core explanation is a mechanism hypothesis rather than an established explanation on this host.

P99 movement alone does not establish that exactly 1% of samples changed. The pilot did not retain p90, p95, or raw sample occupancy. Those are mandatory diagnostics below.

## Registered prediction

> The compile arm will remain physically distinguishable in upper-tail deadline lateness, but the registered ten-sample packet encoding will show no meaningful RLE/DIFF morphology shift relative to the sham arm.

Specifically predicted:

1. compile-arm median deadline lateness is lower than sham-arm median lateness;
2. compile-arm p99 is at least twice sham-arm p99;
3. the primary packet-morphology classification is `PHYSICALLY_RESPONSIVE_MORPHOLOGY_FLAT`;
4. neither arm/channel has registered positive-compression support.

A registered morphology response is the surprise outcome and must be investigated rather than dismissed.

## Arms and order

Run once in fixed order:

1. **S — sham/idle:** two waiting supervisor workers; no compile child processes;
2. **C — compile:** two workers continuously force Python byte-compilation of the live repository `src` tree into separate temporary caches.

Each arm contains exactly `90,001` samples at nominal 10 ms cadence. The 90,000 post-initial values form `9,000` packets and span nominally fifteen minutes. Each arm has a 30-second worker warm-up before its first deadline. There is a 60-second no-workload interval between completed S and the start of C.

This fixed sequential design characterises two host periods under specified conditions. It does not isolate compilation causally or estimate cross-time variability.

## Raw acquisition

For every sample retain only:

- sequence number;
- scheduled absolute monotonic deadline in ns;
- actual wake monotonic timestamp in ns.

Primary value for sample `i = 1..90,000`:

`L_i = wake_i - deadline_i`.

Mandatory derivative value:

`D_i = (wake_i - wake_(i-1)) - 10,000,000 = L_i - L_(i-1)`.

No process identity, PID, path, command output, environment dump, `/proc` counter, packet transform, or feature summary enters the raw scientific artifact. The artifact may retain arm labels, cadence, sample count, worker compile-cycle totals, and phase monotonic boundaries as provenance.

Acquisition and reduction are separate. No transform is computed until both raw arms are complete.

## Packet mappings

For each arm and channel, group the 90,000 registered values in order into 9,000 non-overlapping packets of ten consecutive values.

- **Primary:** canonical unsigned LEB128 of ten `L_i` values.
- **Derivative:** zigzag each signed `D_i`, then canonical unsigned LEB128.

No padding, normalization, clipping, sorting, max, p95, p99, histogram, or other feature extraction enters the packet bytes.

Apply the existing live `RLE` and `DIFF+RLE` transforms losslessly. For each packet retain encoded length, transformed lengths, exact compression fractions, reconstruction checks, `RLE`/`DIFF`/`TIE` winner, and positive/zero/negative reduction signs.

## Registered temporal summaries

Per arm/channel report:

- 30 nominal thirty-second slices of 300 packets;
- 3 nominal five-minute blocks of 3,000 packets;
- overall 9,000-packet summary.

For every scope report latency median, each transform's median exact compression fraction, winner counts, and reduction-sign counts.

A block has an RLE or DIFF majority only when that transform wins strictly more than half of all 3,000 packets. Plurality is not majority.

`SWITCHING` is true only if at least one five-minute block has strict RLE majority and another has strict DIFF majority.

`BLOCK_DRIFT` is true when either transform's range across the three five-minute median compression fractions is strictly greater than `1/15`.

## Primary between-arm morphology gate

`MORPHOLOGY_RESPONSIVE` is true if any condition holds for the primary deadline-lateness channel:

1. `SWITCHING_C != SWITCHING_S`;
2. `BLOCK_DRIFT_C != BLOCK_DRIFT_S`;
3. either transform's arm-level median of the three block-median compression fractions differs by strictly more than `1/15` between C and S;
4. overall RLE unique-winner fractions differ by strictly more than `1/5` between C and S.

`PHYSICALLY_RESPONSIVE` is true when compile p99 is at least twice sham p99. Median direction is reported separately and does not determine this flag.

Primary classification:

- physical true, morphology false: `PHYSICALLY_RESPONSIVE_MORPHOLOGY_FLAT`;
- physical true, morphology true: `PHYSICALLY_AND_MORPHOLOGICALLY_RESPONSIVE`;
- physical false, morphology true: `MORPHOLOGY_SHIFT_WITHOUT_REGISTERED_PHYSICAL_SHIFT`;
- both false: `NO_REGISTERED_RESPONSE`;
- integrity failure: `INVALID`.

The derivative mapping is mandatory and descriptive; it does not change the primary classification.

## Positive compression

For each arm/channel/transform report total positive, zero, and negative reductions.

`POSITIVE_COMPRESSION_SUPPORT` requires one transform to satisfy both:

- positive reduction in at least 900/9,000 packets;
- strict positive-reduction majority in at least one five-minute block.

A transform winner may only expand less. No morphology result is called a usable ecology without positive-compression support.

## Tail-concentration diagnostics

These diagnostics do not alter the primary classification:

For each arm report exact nearest-index half-up median, p90, p95, p99, p99.9, and maximum deadline lateness.

Using the pilot idle p99 threshold fixed at `479,359 ns`, report per arm:

- fraction of samples above threshold;
- fraction of packets containing zero, one, or at least two above-threshold values;
- longest run of above-threshold samples;
- fraction of thirty-second slices containing at least one above-threshold sample.

These determine whether the response is actually confined to rare values and how often the fixed ten-value packets encounter them. They are observational diagnostics, not organism-visible feature extraction.

## Terminal interpretation

If physical response is present but morphology is flat, the registered conclusion is:

> Scheduler latency varied physically, but the tested direct, order-preserving ten-value packet encoding did not convert that variation into transform morphology. Under this mapping, aggregation is the barrier.

No max/quantile/order-statistic packet redesign follows. Such a redesign would be an analyst-selected feature extractor intended to surface known tail structure and would no longer count as finding the environmental morphology in the direct sequence.

If morphology responds under the registered direct mapping, that is surprising and warrants independent reconstruction and mechanism analysis before any organism exposure.

Neither outcome establishes adaptation, fitness effects, lifetime exposure, or cross-host generality.
