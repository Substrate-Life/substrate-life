#!/usr/bin/env python3
"""Build the Stage 7B2-R pre-execution freeze manifest from the gate summary.

Run only AFTER the section 6 feasibility gate has passed.  Emits
``results/stage7b2-repair/pre-execution-manifest.json`` binding SHA-256 +
byte size for every frozen file, embedding the factual gate summary
required by repair preregistration section 6.4.

Usage:
    python3 build_stage7b2r_freeze_manifest.py GATE_SUMMARY_JSON
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

FILES = [
    "docs/stage-7b2-repair-preregistration.md",
    "docs/stage7b2r-output-schema.md",
    "src/stage7b1_mechanics.py",
    "src/stage7_slice1.py",
    "src/stage7_slice2.py",
    "src/datastream.py",
    "src/transforms.py",
    "src/consts.py",
    "src/stage7b2_population.py",
    "src/stage7b2_measure.py",
    "src/stage7b2_solver.py",
    "src/stage7b2r_population.py",
    "src/run_stage7b2r.py",
    "src/reduce_stage7b2r.py",
    "src/stage7b2r_gate.py",
    "src/test_stage7b2_mechanics.py",
    "src/test_stage7b2r_mechanics.py",
]

# Files whose hashes are pinned by the retained Stage 7B2 freeze manifest;
# repair preregistration section 7.2 requires any drift to be justified.
SEVEN_B2_PINS = {
    "src/stage7b2_measure.py": "5664bcecdd0f87c0f1650a93ad95ef90728daa3b5236e652bf4866a909b054fd",
    "src/stage7b2_solver.py": "43756a830b565add8284ccdc0852141a91c1550b73cc63f7780f64714e28c5e5",
    "src/stage7b2_population.py": "86e1b67031bfa68778f7690f645ec94a9047f6cd2141fb27baa5b4e31f3503cb",
    "src/test_stage7b2_mechanics.py": "86a5343e2bd60aaa3157e0149a88ab565dee5f97575ea6d1b550abe543f47cf2",
}
STAGE7B1_PIN = {
    # Disclosed byte-identity expectation (commit 62f2672) from section 7.2.
    "src/stage7b1_mechanics.py": "615726900a1d3d3a36af1807ad0dc7c30ce76c09596c1d2f1fab44870d904cde",
}


def sha256_of(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    gate = json.loads(pathlib.Path(argv[1]).read_text())
    if not gate.get("gate_passed"):
        print("REFUSING: the section 6 gate did not pass; no freeze may be "
              "committed (section 6.3).", file=sys.stderr)
        return 1

    files = {}
    identity_notes = {}
    for rel in FILES:
        path = REPO / rel
        digest = sha256_of(path)
        files[rel] = {"bytes": path.stat().st_size, "sha256": digest}
        for pins, unchanged_text in (
                (SEVEN_B2_PINS,
                 "byte-identical to the retained Stage 7B2 freeze manifest"),
                (STAGE7B1_PIN,
                 "byte-identical to commit 62f2672 as disclosed at the "
                 "Stage 7B2 freeze")):
            if rel in pins:
                expected = pins[rel]
                identity_notes[rel] = (
                    unchanged_text if digest == expected else
                    f"HASH DRIFT versus registered pin: {digest} != "
                    f"{expected} -- must be justified against repair "
                    f"preregistration section 7.2")

    g1 = gate["G1_per_genotype"]
    g2 = gate["G2_joint_supercritical"]
    g3 = gate["G3_no_overflow_no_invalid"]
    g4 = gate["G4_all_checkpoints_closed"]
    gate_note = (
        "Section 6.4 factual gate summary. Seed list used: "
        f"{gate['seeds_used']} ({gate['seed_count']} distinct shakedown "
        "seeds 20270000+j, j=0..23, fixed before any execution at this "
        "ecology and disjoint from the confirmatory table "
        "{20261822..20261853}). Complete replicates: "
        f"{gate['complete_replicates']}/{gate['seed_count']}. "
        "G1 genotype A=102 supercritical in "
        f"{g1['102']['supercritical_replicates']}/{g1['102']['of']}; "
        "genotype A=204 supercritical in "
        f"{g1['204']['supercritical_replicates']}/{g1['204']['of']}; "
        f"G2 jointly supercritical in {g2['replicates']}/{g2['of']} "
        f"(two-thirds threshold {gate['two_thirds_threshold']}); "
        "G3 zero BUFFER_OVERFLOW="
        f"{g3['zero_buffer_overflow']}, zero INVALID_IMPLEMENTATION="
        f"{g3['zero_invalid_implementations']}; G4 checkpoint failures="
        f"{g4['checkpoint_failures']}. Gate passed: "
        + str(gate["gate_passed"]) + ". "
        "Implementation-window disclosures: (i) three short-window timing/"
        "plumbing probes on seed 20270000 (windows 100, 300, 150 ticks) and "
        "40-tick unit-test integration windows preceded the gate; all were "
        "exploratory and unretained; (ii) no runner or reducer execution at "
        "the registered ecology occurred during the window, per section 9; "
        "(iii) the confirmatory seed table was untouched until this freeze."
    )

    manifest = {
        "protocol": "stage-7b2r-preregistration",
        "purpose": (
            "Stage 7B2-R pre-execution freeze (repair preregistration "
            "section 7): implementation, configuration layer, runner, "
            "tests, output schema, reducer, and gate tooling frozen "
            "together before any retained run, after the binding section 6 "
            "feasibility gate passed; df7b1f5/e2f580b/62f2672/27f5700 "
            "precedent."),
        "files": files,
        "shared_source_byte_identity": identity_notes,
        "feasibility_gate_summary": gate_note,
        "execution_disclosure": (
            "The retained suite may be executed with the frozen runner's "
            "--workers option: replicates are isolated seeded populations "
            "and pool.map preserves registered index order, so output is "
            "bit-identical to sequential execution; each replicate's "
            "event_digest binds its exact stream."),
        "frozen_sources_embed_their_hashes_in_runner_output": True,
        "first_retained_outputs": {
            "raw": "results/stage7b2-repair/stage7b2r-result.json",
            "reduced": "results/stage7b2-repair/stage7b2r-reduced.json",
        },
        "authorised_execution_class": (
            "one seeded, mutation-disabled confirmatory suite: k = 32 "
            "replicate populations under section 3, reduced exactly once "
            "under the carried section 5 rule (repair preregistration "
            "sections 7.3-7.4); mutation remains unauthorised in every "
            "form"),
    }
    out_dir = REPO / "results" / "stage7b2-repair"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "pre-execution-manifest.json"
    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
