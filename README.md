# Substrate

Substrate is an experimental digital-evolution system for studying what a computational substrate must provide before selection can express a difference. Organisms execute genomes, transform resource packets, pay energy and memory costs, reproduce, and compete under explicit population rules.

The project belongs to the research tradition established by Tierra and Avida, but shares no code or instruction set with either platform.

## Status

Stages 1–6 produced five scientific findings. Stage 7 implementation and deterministic verification then produced four methodological results. Stage 7 mutation, stochastic allocation assays, evolutionary runs, and fitness inference remain untested; verified mechanics are not an evolutionary result.

### Status addendum (2026-08-24)

*Visible, dated addendum. The Status paragraph above is preserved
byte-for-byte and superseded only where the retained record below
contradicts it. Nothing here reopens, retunes, or reinterprets any
retained result.*

The untested tiers that paragraph names have since been tested,
executed, and audited. The Stage 7B split-reserve channels ran under
pre-registered feasibility gates: the 7B0 deterministic channel was
executed and independently audited; the host-coupling probes
(compressibility long window, scheduler-latency morphology, host
encoding diagnostic) were registered, run, and audited; the 7B2
feasibility gates returned registered no-gos, archived with evidence
under [`failed-designs/`](failed-designs/); the signed-bracket design
was frozen, registered, executed once, and audit-reproduced
(`results/stage7b-signed-bracket/`); and Stage 8 ran a single paired
confirmatory alpha-evolution execution whose reduced artifact is
retained and post-audited (`results/stage8-alpha-evolution-paired/`,
17/17 post-retention checks).

The programme is now CLOSED on computed grounds: the registered nulls
were forced at any instrument this architecture could afford. On the
measured dispersion (population sd(D) = 5.7061 lattice units), a true
shift equal to the entire registered pair floor yields 3.0% exact
power (13/24 crossings) on the frozen concordance rule; ≥50% power
needs 1.87× the floor; rule power falls with replicate count below
per-pair mover probability 0.75; and recruitment endpoints are
mechanically null at saturation (admitted births identical across
arms, phenotype-blind: 23,933 = 23,933). Full derivation:
[`docs/stage-8-followon-power-memo.md`](docs/stage-8-followon-power-memo.md)
(independently audited 21/21, zero exact-claim failures); narrative
closure: [`docs/final-report.md`](docs/final-report.md) §8 addendum.
Closure survived adversarial debate, Rounds 1–6
([`docs/stage-8-debate-log.md`](docs/stage-8-debate-log.md)).

Reopening doors R1–R3 (memo §9) are the only lawful paths back into
evolutionary work; until one fires, no evolutionary execution is
authorised anywhere in this programme. One-command integrity check
over the retained class:
`python3 src/verify_retained_integrity.py --auditors`.

## Findings

### Scientific findings

1. **Fitness currency follows the complete lifecycle.** Reserve, income, attempted births, and isolated reproductive capacity are not substitutes for growth in the regulated population.
2. **Serial copying constrains fecundity.** When copy time dominates reproduction, each additional offspring incurs nearly another full copy delay and may lose its growth-rate advantage.
3. **Reserve margin changes the selection regime.** A small cost can be lethal when pre-income runway is tight and merely disadvantageous when the margin is wider.
4. **Income has no automatic fitness meaning.** Surplus matters only through an implemented route to timing, persistence, reproduction, provisioning, establishment, or later contribution.
5. **One shared reserve couples fecundity and viability.** Reproductive work, parental persistence, offspring provisioning, and establishment compete through the same account.

### Methodological findings

6. **Control and evolutionary openness are in tension.** Freezing genomes, traits, schedules, or ecology improves identification while narrowing the evolutionary claim.
7. **Review and execution answer different questions.** Reviewed invariants made failures diagnosable, but the smallest complete execution exposed mechanism defects that further wording review had missed.
8. **Conservation does not establish ecological validity.** Exact reserve, packet, and memory closure can coexist with an implementation that deletes the resource interaction under study.
9. **Verification apparatus must match the experiment's threat model.** Deterministic fixed-input traces need transparent evidence and exact reproduction; one-use and seed-freeze ceremony earns its cost when stochastic or inferential degrees of freedom actually exist.

## Read first

- [Canonical public essay on Substack](https://substratelife.substack.com/p/conservation-is-not-an-ecology) — the public-facing argument in accessible form.
- [Archival Markdown copy](docs/public-technical-essay.md) — repository-preserved copy of the published argument.
- [Host-coupling essay](docs/the-host-varied-metabolism-couldnt-eat-it.md) — why measurable host variation remained outside the repetition metabolism's nutritional currency.
- [Audited findings synthesis](docs/stages1-6-findings-synthesis.md) — the evidentiary source, with measured/inferred boundaries and superseded claims. Its 2026-08-01 terminal state predates the Stage 7B/8 arc — read with the dated closure addendum at its top.
- [Final report](docs/final-report.md) — closure report for Stages 1 → 8 (2026-08-23); supersedes the project report bullet below, which remains the 2026-07-30 Stages 1–6 snapshot with a dated supersession notice at its top.
- [Project report](docs/project-report.md) — current model, retained results, failed assays, and open questions.
- [`failed-designs/`](failed-designs/) — byte-preserved dead ends, audit transcripts, and the reasoning for abandonment.

## Repository map

- [`src/`](src/) — implementation, runners, and tests.
- [`docs/`](docs/) — current models, report, synthesis, and essay.
- [`results/`](results/) — retained traces, calibrations, summaries, and raw outputs.
- [`superseded/`](superseded/) — historical documents replaced by the current model.
- [`failed-designs/`](failed-designs/) — abandoned designs with their evidence and audit trail intact.

## Try it

```bash
python3 src/engine.py
```

The deterministic seed-42 run prints its realised parameters and population checkpoints, reaches extinction at tick 1037, and finishes with `ticks=1038`, `max_pop=163`, `max_gen=45`, and `instantiated_offspring=8878`.

## Run the tests

```bash
cd src
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v
```

Stage 7 traces close reserve, packet-provenance, and shared-memory ledgers exactly. For the legacy Slice 1/2A artifacts, verify commit `23aa663` and recorded content hashes—not regenerated whole-artifact byte identity—because the Slice 2A manifest embeds Git-unstable `mtime_ns` and does not cover all transitive dependencies; see the [Stage 7B0 execution note](docs/stage-7b0-deterministic-execution-note.md).

## Archive policy

Failed designs and superseded claims are retained rather than rewritten away. Historical artifacts remain evidence only for the source semantics under which they were produced. The active report records when a claim was withdrawn, narrowed, or reclassified.

## License

MIT. See [LICENSE](LICENSE).
