# Registered Scheduler-Latency Sensitivity Gate

## Purpose and evidential status

This protocol is frozen before any RLE/DIFF reduction of the retained scheduler timestamps and before any loaded-arm capture.

It asks two ordered questions:

1. **Direct sensitivity:** does sustained host compilation move the recorder's own scheduler-latency distribution relative to the retained passive hour?
2. **Morphological sensitivity:** does that movement alter transform ranking or five-minute compression morphology under one fixed unpadded latency encoding?

The loaded arm is a controlled **sensitivity gate**, not an ecology test. Continuous compilation is an imposed treatment. A positive result establishes that the direct-experience channel responds to host contention; it does not establish that ordinary host use supplies naturally alternating regimes. A later passive ordinary-use arm is authorized only if sensitivity is established and must receive its own prospective registration.

No organisms, population, fitness, adaptation, identities, paths from other processes, payloads, or per-process telemetry enter either arm.

## Pre-registration prerequisite observations

These observations were computed before this protocol solely to determine whether the retained timestamp field has sufficient resolution and whether gross lateness is sparse; no transform was applied:

- Retained source artifact SHA-256: `623f59af1b6dd76a0f050337345881b93059981547ffe96a89eaa8b9a3a57c5f`.
- Clock field: integer `time.monotonic_ns` scheduled deadlines and wake timestamps.
- Live monotonic clock reported 1 ns resolution; empirical GCD of retained wake intervals and deadline lateness was 1 ns.
- Distinct deadline-lateness values: 96,909/360,001.
- Retained median deadline lateness: 108,654 ns.
- Retained p99: 516,279 ns; p99.9: 1,532,719 ns; maximum: 587,245,508 ns.
- Wake lateness at least one 10 ms cadence: 187/360,001 (0.051944%).
- Only 10/360,000 inter-wake intervals were exactly 10 ms; there were 125,410 distinct intervals.

These checks establish that latency was not quantized away. They do not establish temporal morphology.

## Arms

### Arm P — retained passive hour

Use the already audited artifact `results/host-compressibility-long-window-360001x10ms.json`. It contains 360,001 samples on absolute 10 ms deadlines and the exact timestamps required below. It is observational and had no controlled workload provenance.

### Arm C — continuous-compile sensitivity hour

Capture 360,001 samples at the same nominal 10 ms cadence with the same `host_compressibility_probe.build_artifact` recorder, exact allowlisted counter reads, absolute deadlines, timestamp schema, packet windows, and artifact serialization.

Before the first deadline, start exactly two workload workers because pre-registration discovery found two online CPUs (`nproc = 2`). Each worker repeatedly executes:

`PYTHONPYCACHEPREFIX=<worker-specific temporary directory> python3 -m compileall -q -f -j 1 src`

Requirements:

- worker-specific cache paths prevent concurrent output collision and repository modification;
- both workers begin at least 30 seconds before capture;
- both run continuously until after the last retained read and artifact write;
- every compile invocation exit status is counted;
- any nonzero compile exit, worker death, absent start/stop/heartbeat provenance, fewer than two live workers during capture, or workload interval failing to cover the complete capture makes Arm C `INVALID`;
- the manager retains an append-only JSONL workload journal during execution so interruption evidence survives;
- the capture output and journal use exclusive mode-0600 creation;
- temporary bytecode is workload exhaust and is not a scientific artifact.

This treatment intentionally drives the host. It is not “ordinary use,” natural exposure, or evidence of an undirected environment.

## Direct latency variables

For sample `i`:

### Primary: deadline lateness

`L_i = wake_monotonic_ns_i − scheduled_deadline_monotonic_ns_i`

Require `L_i >= 0`. This is the recorder's direct delay relative to its intended absolute wake deadline.

### Mandatory secondary: cadence deviation

For `i >= 1`:

`D_i = (wake_monotonic_ns_i − wake_monotonic_ns_(i−1)) − 10,000,000`

This includes the absolute-deadline catch-up policy and is secondary for that reason. It is retained as a cross-check, not substituted for deadline lateness.

## Packet grouping and encoding

For both variables and both arms:

- discard primary sample 0 so both channels use values indexed 1 through 360,000;
- preserve acquisition order;
- group every ten consecutive values into 36,000 non-overlapping packets;
- add no header, packet index, field label, padding, timestamp, or analyst-authored framing.

### Primary encoding

Encode each nonnegative `L_i` independently using canonical unsigned LEB128, then concatenate ten encodings.

### Secondary encoding

Zigzag-map signed `D_i` to a nonnegative integer:

- `Z(D) = 2D` when `D >= 0`;
- `Z(D) = -2D - 1` when `D < 0`.

Canonical-ULEB128 encode each `Z(D_i)` and concatenate ten encodings.

Both encodings are online, causal, self-delimiting, unpadded, and fixed before inspection. No quantization, normalization, clipping, whitening, smoothing, binning, or alternative integer representation is permitted in this gate.

## Transform endpoints

Apply the existing live lossless RLE and DIFF+RLE transforms to every encoded packet. Require exact reconstruction. Retain per packet:

- encoded length and SHA-256;
- transform output lengths;
- byte reductions and exact rational compression fractions;
- positive/zero/negative reduction;
- unique smaller-output winner or `TIE`.

Partition each arm/channel into 120 non-overlapping 300-packet nominal 30-second slices and twelve non-overlapping 3,000-packet nominal five-minute blocks. Report exact nearest-index medians of latency, packet compression fractions, winner counts, and positive-compression counts.

## Registered within-arm morphology rules

For each arm and channel:

- `SWITCHING` requires RLE and DIFF each to win at least 3,600/36,000 packets and each to hold a strict majority (`winner_count * 2 > block_total`) in at least one five-minute block.
- `BLOCK_DRIFT` requires either transform's range across twelve exact five-minute median compression fractions to be strictly greater than `1/15`.

Report both booleans independently.

## Registered between-arm sensitivity rules

### Direct distribution response

Arm C is `DIRECTLY_RESPONSIVE` when either:

- its median deadline lateness is at least twice Arm P's median; or
- its p99 deadline lateness is at least twice Arm P's p99.

The directional prediction stated before capture is stronger and is evaluated separately:

> Continuous two-worker compilation will increase Arm C's p99 deadline lateness to at least ten times Arm P's retained p99 (at least 5,162,790 ns).

Failure of the tenfold prediction does not erase a registered twofold sensitivity response.

### Transform-morphology response

For a channel, Arm C is `MORPHOLOGICALLY_RESPONSIVE` when at least one holds:

1. loaded-arm `SWITCHING` or `BLOCK_DRIFT` is true while the corresponding passive-arm property is false;
2. for either transform, the absolute difference between the two arms' medians of their twelve five-minute median compression fractions is strictly greater than `1/15`;
3. the absolute between-arm change in overall RLE winner fraction is strictly greater than `1/5`.

Primary and secondary channels are classified separately; the primary deadline-lateness channel controls the final gate.

## Final gate classification

Return exactly one:

- `LOAD_SENSITIVE_LATENCY_MORPHOLOGY`: primary deadline lateness is both `DIRECTLY_RESPONSIVE` and `MORPHOLOGICALLY_RESPONSIVE`.
- `LOAD_SENSITIVE_BUT_MORPHOLOGICALLY_FLAT`: primary is directly responsive but not morphologically responsive.
- `MORPHOLOGY_CHANGE_WITHOUT_DIRECT_SHIFT`: primary is morphologically responsive but not directly responsive.
- `NO_DETECTED_LOAD_SENSITIVITY`: primary is neither directly nor morphologically responsive.
- `INVALID`: acquisition, provenance, workload coverage, timestamp, encoding, reconstruction, sample/packet count, or mandatory-output validation fails.

All outcomes and both channels are reportable. No mapping, threshold, workload, arm, transform, or temporal resolution may be changed after inspection and included in this gate.

## Stop rules and next step

- If Arm C is not directly responsive, stop: this direct scheduler-latency channel failed even a sustained-contention sensitivity treatment.
- If Arm C is directly responsive but primary morphology remains flat, stop before organisms: the host moved the physical variable, but this encoding/transform ecology did not expose it.
- Only if primary morphology is responsive may a new passive ordinary-use arm be registered. That later arm asks whether natural host use supplies trackable regimes; it cannot reuse the controlled sensitivity result as an ecology result.

## Claim boundary

- **Measured:** self-timed deadline lateness and cadence deviation, encoded bytes, transform outcomes, and controlled between-arm response.
- **Inferred if sensitive:** sustained compilation causally changes this direct-experience latency channel under the tested host and recorder.
- **Not established:** naturally occurring regimes, ordinary-use prevalence, organismal observability in logical ticks, fitness effects, adaptation, selection, or cross-host generality.

Independent review must recompute both retained and loaded timestamp channels without trusting producer summaries, verify workload coverage, and audit the final classification.
