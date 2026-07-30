# Substrate

Substrate is an experimental digital-evolution system for studying what a computational substrate must provide before selection can express a difference. Organisms execute genomes, transform resource packets, pay energy and memory costs, reproduce, and compete under explicit population rules.

The project belongs to the research tradition established by Tierra and Avida, but shares no code or instruction set with either platform.

## Status

Stages 1–6 produced five scientific findings. Two verified Stage 7 implementation slices then produced three methodological results. Stage 7 mutation, evolutionary runs, allocation contrasts, and fitness inference remain untested; verified mechanics are not an evolutionary result.

## Findings

1. **Fitness currency follows the complete lifecycle.** Reserve, income, attempted births, and isolated reproductive capacity are not substitutes for growth in the regulated population.
2. **Serial copying constrains fecundity.** When copy time dominates reproduction, each additional offspring incurs nearly another full copy delay and may lose its growth-rate advantage.
3. **Reserve margin changes the selection regime.** A small cost can be lethal when pre-income runway is tight and merely disadvantageous when the margin is wider.
4. **Income has no automatic fitness meaning.** Surplus matters only through an implemented route to timing, persistence, reproduction, provisioning, establishment, or later contribution.
5. **One shared reserve couples fecundity and viability.** Reproductive work, parental persistence, offspring provisioning, and establishment compete through the same account.
6. **Control and evolutionary openness are in tension.** Freezing genomes, traits, schedules, or ecology improves identification while narrowing the evolutionary claim.
7. **Review and execution answer different questions.** Reviewed invariants made failures diagnosable, but the smallest complete execution exposed mechanism defects that further wording review had missed.
8. **Conservation does not establish ecological validity.** Exact reserve, packet, and memory closure can coexist with an implementation that deletes the resource interaction under study.

## Read first

- [Public technical essay](docs/public-technical-essay.md) — the argument in accessible form; a canonical Substack link will be added after publication.
- [Audited findings synthesis](stages1-6-findings-synthesis.md) — the evidentiary source, with measured/inferred boundaries and superseded claims.
- [Project report](project-report.md) — current model, retained results, failed assays, and open questions.
- [`failed-designs/`](failed-designs/) — byte-preserved dead ends, audit transcripts, and the reasoning for abandonment.

## Run the tests

```bash
cd src
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v
```

The current suite contains 47 tests. Stage 7 traces additionally embed source manifests and close reserve, packet-provenance, and shared-memory ledgers exactly.

## Archive policy

Failed designs and superseded claims are retained rather than rewritten away. Historical artifacts remain evidence only for the source semantics under which they were produced. The active report records when a claim was withdrawn, narrowed, or reclassified.

## License

MIT. See [LICENSE](LICENSE).
