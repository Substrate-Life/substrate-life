# Withdrawal — One-Hour Scheduler-Latency Sensitivity Gate

## Status

The acquisition authorized by `results/scheduler-latency-acquisition-pre-execution.json` at commit `9d886a1` is **WITHDRAWN UNUSED**.

No registered Arm C capture, Arm S capture, latency-transform reduction, or organism assay was executed under that authorization. Its exact pair command must not be launched. The original registration, amendment, implementation, manifests, and independent `BLOCK` audits remain retained as historical evidence; they are not silently corrected or replaced.

## Reason

The control apparatus became disproportionate to the coarse physical question: whether scheduler deadline lateness responds to two-worker CPU contention. Audit latency also exceeded implementation stability, so repeated reviews were auditing superseded targets rather than controlling a frozen experiment.

The final static audit of `9d886a1` remained `BLOCK`, principally because acquisition-manifest identity and corpus bytes were not executably bound at arm boundaries, journal validation was not exact-schema/privacy fail-closed, and the derivative-channel reduction retained implementation defects. Those findings matter if this apparatus is ever revived, but they are not grounds for another iteration of the sensitivity gate.

## Exploratory replacement

A deliberately unregistered sixty-second pilot was run instead:

- 3,000 deadline-lateness samples at 10 ms cadence under an idle phase;
- 3,000 samples under two continuous compile workers;
- idle p99: `479,359 ns`;
- loaded p99: `1,867,253 ns`;
- p99 ratio: approximately `3.8953`;
- idle median: `110,510 ns`;
- loaded median: `80,532 ns`;
- worker compile cycles: 130 and 131.

Result artifact:

- path: `/opt/data/scheduler-latency-60s-pilot-result.json`;
- SHA-256: `a8a00f8686219a6b6e03bb7bf9ca728b23bfc153f4ff5bd984dd4654759cb47e`.

This is exploratory sequential evidence that contention moved the upper latency tail on this host. It did not confirm the abandoned `>=10x` directional prediction, does not precisely estimate effect size, and does not establish transform morphology, ordinary-use exposure, adaptation, or fitness effects.

## Future scope

If scheduler-latency morphology is characterized later, it requires a new prospective protocol. The default should be approximately fifteen minutes per compile/sham arm, using the existing apparatus only where it protects the subtle morphology question. The withdrawn one-hour sensitivity authorization and its first-attempt identity must not be reused.
