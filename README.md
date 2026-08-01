# Substrate

Substrate is an experimental digital-evolution system for studying what a computational substrate must provide before selection can express a difference. Organisms execute genomes, transform resource packets, pay energy and memory costs, reproduce, and compete under explicit population rules.

The project belongs to the research tradition established by Tierra and Avida, but shares no code or instruction set with either platform.

## Status

Stages 1–6 produced five scientific findings. Stage 7 implementation and deterministic verification then produced four methodological results. Stage 7 mutation, stochastic allocation assays, evolutionary runs, and fitness inference remain untested; verified mechanics are not an evolutionary result.

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
- [Audited findings synthesis](docs/stages1-6-findings-synthesis.md) — the evidentiary source, with measured/inferred boundaries and superseded claims.
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
