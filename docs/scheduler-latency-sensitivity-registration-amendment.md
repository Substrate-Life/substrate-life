# Pre-Execution Amendment — Scheduler-Latency Sensitivity Gate

## Status

This amendment responds to the independent `BLOCK` verdict on registration commit `b1e5616`. It is committed before any latency transform reduction and before either new scientific capture. Where it conflicts with `docs/scheduler-latency-sensitivity-registration.md`, this amendment controls.

The original retained passive hour remains a mandatory descriptive arm, but it is not the causal control for compilation because it occurred historically under a different supervisor and host period.

## Matched contemporaneous control and frozen order

Add two new one-hour arms using the same current recorder, manager, journaling, warm-up, cadence, sample count, output construction, and two worker-supervisor threads:

- **Arm C — compile treatment:** each of two workers continuously runs the registered immutable compile corpus.
- **Arm S — sham control:** each of two workers follows the identical supervisor lifecycle but waits without starting compilation or any child process.

A single local random bit was drawn once before this amendment and before either acquisition:

- draw time: `2026-08-02T13:09:29+00:00`;
- bit: `1`;
- frozen order: **Arm C first, then Arm S**.

After Arm C terminates, impose a minimum ten-minute no-workload washout before Arm S's workload/sham start event. The manager/journal overhead is matched; compilation remains the intended treatment difference. With one realization per arm, randomized order reduces deliberate order selection but does not eliminate all period, thermal, background-workload, or carryover confounding.

The gate may establish a contemporaneous **C-versus-S difference under the registered protocols**. It does not by itself prove that compilation uniquely caused the difference. Wording such as “compilation causally changes the channel” is withdrawn. Strong attribution would require replication and counterbalancing.

## First-attempt rule

The first authorized Arm C launch and first authorized Arm S launch are the sole inferential attempts under this registration.

- Every journal is opened exclusively before workers start and retained whether the arm succeeds or fails.
- A completed artifact is retained regardless of result.
- If either first arm is interrupted, malformed, or `INVALID`, the paired gate is `INVALID`; no rerun may replace it.
- A rerun requires a new prospective registration and is descriptive or part of a new experiment.
- If Arm C is invalid, Arm S is not launched under this gate. If Arm C is valid but Arm S is invalid, both retained records remain and the paired gate is invalid.

The existing in-memory recorder cannot retain partial raw samples after process failure without adding per-sample I/O absent from the historical arm. This limitation is explicit. The append-only workload/capture journal is the retained first-attempt interruption record; lack of partial raw records prevents scientific use and therefore yields `INVALID`.

## Frozen acquisition and workload surface

Before Arm C, commit an acquisition manifest containing:

- amendment and original protocol commits/hashes;
- exact current commits and SHA-256 hashes for the loaded/sham manager, recorder, telemetry parser, transforms, constants, tests, and all transitive local source files;
- Python version, cwd, `nproc = 2`, kernel identification, exact commands, arm order, output paths, journal paths, sample count, cadence, worker count, warm-up, heartbeat period, and washout;
- disclosed unrelated working-tree state;
- an immutable compile corpus materialized from a named Git commit, with relative-path/SHA-256 manifest and file count;
- repository and corpus hashes immediately before and after each arm.

Arm C compiles only that immutable materialized corpus. It must not compile mutable live `src` bytes. Arm S receives the same manager and worker count but no corpus reads after preflight.

A second reduction manifest is committed after both raw captures and before any latency transform reduction. It binds both new artifact hashes, both journal hashes, the retained passive hash, reducer/tests/transforms, and the exact reduction command.

## Journal schema and coverage

Journal format is append-only mode-0600 JSONL. Its allowlisted event types and fields are:

- `manager_started`: arm label, mode, worker count, monotonic timestamp;
- `worker_ready`: worker ordinal and monotonic timestamp;
- `invocation_started` (Arm C only): worker ordinal, invocation ordinal, monotonic timestamp;
- `invocation_ended` (Arm C only): worker ordinal, invocation ordinal, monotonic timestamp, exit status, duration ns;
- `workload_started`: arm label, mode, worker count, monotonic timestamp;
- `heartbeat`: arm label, mode, monotonic timestamp, live supervisor-worker count, per-worker completed/nonzero/active invocation state;
- `capture_started`: arm label, sample count, cadence, warm-up and monotonic timestamp;
- `capture_completed` or `capture_failed`: arm label, monotonic timestamp and, on success, artifact hash/size;
- `workload_stopped`: arm label, mode, monotonic timestamp, terminal per-worker counts and cleanup success.

Forbidden journal content: PIDs, command strings, absolute paths, source filenames, stdout/stderr, environment values, process identities outside worker ordinals, hostnames, machine IDs, or cache contents.

Operational rules:

- JSONL lines are flushed immediately; start/stop/capture events and every heartbeat are fsynced.
- Heartbeat target period is 10 seconds; any monotonic heartbeat gap strictly greater than 15 seconds during the registered coverage interval is `INVALID`.
- Arm C records every invocation boundary and exit status. Any nonzero exit is `INVALID`.
- For each compile worker, the gap from one invocation end to the next invocation start must be at most 2 seconds throughout coverage. Every heartbeat must report two live supervisor workers; Arm C must also report an active invocation or an invocation boundary gap within 2 seconds for each worker.
- Arm S must report two live waiting workers and zero invocation events.
- Required coverage begins at least 30 seconds before the first scheduled capture deadline and ends after the last retained read and artifact completion.
- Any journal write/fsync failure is fatal and makes the arm `INVALID`.
- Temporary parent and worker cache directories are mode `0700`. Cache contents are never retained. Only non-identifying cleanup success is journaled.

Worker ordinals and compile exit status are permitted treatment provenance. No per-process field enters the latency bytes, transforms, or organism-visible channel.

## Exact arithmetic

For an ordered list of length `n`, percentile `p` uses zero-based index:

`floor((n - 1) * p + 1/2)`

with exact rational arithmetic for `p ∈ {1/2, 9/10, 99/100, 999/1000}`. This is nearest index with half-up ties.

Compression fraction is exactly:

`(encoded_length - transformed_length) / encoded_length`.

Each nominal 30-second slice contains 300 packets and 3,000 latency values. Each nominal five-minute block contains 3,000 packets and 30,000 latency values.

For every slice and block, report separately:

- latency-value median;
- each transform's median packet compression fraction;
- `RLE`, `DIFF`, and `TIE` counts;
- each transform's positive, zero, and negative reduction counts.

Overall RLE winner fraction is `RLE_unique_wins / 36,000`.

## Corrected primary comparison and symmetric morphology

`DIRECTLY_RESPONSIVE` now compares Arm C against contemporaneous Arm S, not historical Arm P:

- `median_C >= 2 * median_S`, or
- `p99_C >= 2 * p99_S`.

Directional prediction:

> Arm C p99 deadline lateness will be at least ten times Arm S p99 deadline lateness.

Historical Arm P ratios are mandatory descriptive outputs only.

Morphological responsiveness compares C with S. Criterion 1 is symmetric:

- `SWITCHING_C != SWITCHING_S`, or
- `BLOCK_DRIFT_C != BLOCK_DRIFT_S`.

The other frozen criteria remain symmetric by absolute difference:

- either transform's arm-level median of twelve block-median compression fractions differs by more than `1/15`; or
- overall RLE winner fractions differ by more than `1/5`.

## Secondary-channel identity

Under exact absolute 10 ms deadlines:

`D_i = L_i - L_(i-1)`.

Cadence deviation is therefore a deterministic first difference of deadline lateness, not independent corroboration. It remains a mandatory derivative/descriptive view and does not independently strengthen evidential confidence.

## Ranking versus positive compression

A transform winner is only the shorter of two outputs and may merely expand less. `MORPHOLOGICALLY_RESPONSIVE` describes byte-length ranking/magnitude response, not a usable compression ecology.

Report separately for each arm/channel/transform:

- positive, zero, and negative reduction counts;
- whether at least 3,600/36,000 packets have positive reduction;
- whether any five-minute block has a strict majority of positively compressed packets.

Define descriptive `POSITIVE_COMPRESSION_SUPPORT` for an arm/channel only when at least one transform satisfies both positive conditions. This does not alter the registered sensitivity classification, but no result may be called an exploitable or usable ecology without it.

## Revised interpretation

- A C-versus-S direct response shows that the registered loaded protocol and contemporaneous sham differ in recorder-experienced latency; compilation-specific attribution remains qualified.
- A morphology response without `POSITIVE_COMPRESSION_SUPPORT` is a transform-output response, not an ecology.
- A negative C-versus-S result is strong evidence against sensitivity under this exact host, workload corpus, manager, recorder, cadence, encoding, and hour pair—not proof that “nothing will” move scheduler latency.
- The historical passive arm remains necessary to describe ordinary exposure already observed but cannot serve as the causal control.
