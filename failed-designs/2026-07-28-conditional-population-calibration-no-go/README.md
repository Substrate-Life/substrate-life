# Conditional p=1 capped-population calibration — NO-GO archive

Date: 2026-07-28

## Classification

This design was invalidated before the planned standalone ten-seed run. It must not be used as confirmatory or calibration evidence for a clean population-level fecundity contrast.

The isolated-parent conditional genome remains valid capacity evidence: FULL produced 3 versus HALF 2 live births per equal 17-tick cycle with no parent death or stillbirth. That claim is separate from population selection.

## Failure discovered during independent protocol review

The independent reviewer ran exploratory one-seed-per-treatment diagnostics while reviewing the preregistration:

- FULL seed 61001: 401 reserve-exhaustion deaths over 2,040 ticks.
- HALF seed 62001: 6,387 reserve-exhaustion deaths, 12,040 stillbirths, endpoint N=150.
- Packet capture remained f=1.

The reviewer did not preserve standalone raw artifacts. The complete available review is preserved as `independent-review.txt`; its live transcript remains in the delegation cache but is not assumed project-persistent.

Seeds 61001 and 62001 are therefore consumed and must never be reused as blind preregistered seeds.

## Mechanistic reason

A population-born offspring is created after the scheduler's active-ID snapshot, so it cannot execute on its birth tick, but it still pays upkeep at that tick's end. Its first successful bouts occur at ages 10/13/16 (FULL) or 10/13 (HALF), not the founder-trace ages 9/12/15 or 9/12. Under cap turnover, reserve and provisioning histories vary. Even at f=1 this creates pre-first-READ reserve death and, especially for HALF, under-endowed DIVIDEs/stillbirths.

Therefore the proposed gates of N=155 at every endpoint tick, zero non-displacement death, and zero stillbirth are not satisfied by the current population process. Relaxing those gates post hoc would change the question from pure fecundity to coupled recruitment/viability and is forbidden.

## Later threshold audit

A deterministic normal-scheduler ledger subsequently showed that `OFFSPRING_TROUGH=18` understates the reserve required to reach first extraction. Exact spend through READ is 20.0 and exact arithmetic therefore requires initial reserve >20; literal 20.0 survives only in the current float implementation because of a tiny positive residue. In the conditional isolated artifact, 195/400 HALF instantiations were below 20, including every second bout in cycles 6–200, while all 600 FULL transfers exceeded 20. The earlier clean 600/600-versus-400/400 viable-fecundity interpretation is withdrawn. This strengthens the NO-GO: the p=1 isolated trace itself counted under-endowed HALF offspring as live because they were removed before execution. See project `src/trace_offspring_first_extraction_threshold.py` and `offspring-first-extraction-threshold-summary.json`.

The clean-fecundity assay program is terminated under the current reserve/transfer/cap semantics. No retuning of threshold, τ, supply, cap, or mixed ecology is authorized within this design lineage.

## Additional protocol defects found

- Mutation-off was runner monkey-patched rather than a first-class runtime/readback parameter.
- End-of-tick memory snapshots can miss within-tick low-water marks.
- End-of-tick census ticks are not execution-opportunity denominators.
- `155/(1+V_k/mean(k))` is an ad hoc variance-discount index, not a defensible overlapping-generation Ne.
- Per-seed, not merely pooled, cohort completeness is required.
- Parent draw rejections are not logged; only the eventual protected outcome is observable.
- Queue overflow arrivals/discards are not instrumented.

## Preserved files

- `run_conditional_population_calibration.py`: unexecuted standalone runner draft; short smoke-tested only with nonregistered seed 99991.
- `test_population_calibration_runner.py`: reducer tests.
- `preregistration-before-no-go.md`: protocol state at invalidation.
- `independent-review.txt`: complete reviewer findings.
- `independent-review-live-transcript.log`: preserved reviewer tool transcript and exploratory command outputs.

No mixed population run was performed.
