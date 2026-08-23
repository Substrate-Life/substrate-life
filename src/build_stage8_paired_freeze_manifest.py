#!/usr/bin/env python3
"""Build the Stage 8 paired-arm pre-execution freeze manifest.

Run only AFTER the section 7 feasibility gate of
``docs/stage-8-alpha-evolution-repair-preregistration.md`` has passed on
the fixed 12-pair shakedown table.  Emits
``results/stage8-alpha-evolution-paired/pre-execution-manifest.json``
binding SHA-256 + byte size for every frozen file, embedding the factual
gate summary required by section 8(3) (df7b1f5 / e2f580b / 7d21153 /
27f5700 precedent).

Usage:
    python3 build_stage8_paired_freeze_manifest.py GATE_SUMMARY_JSON \
        [--out PATH]

``--out`` exists solely as a test hook; production freezes always use
the default registered path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

FILES = [
    "docs/stage-8-alpha-evolution-preregistration.md",
    "docs/stage-8-alpha-evolution-repair-preregistration.md",
    "docs/stage-8-debate-log.md",
    "docs/stage8-alpha-output-schema.md",
    "docs/stage8-paired-output-schema-addendum.md",
    "src/consts.py",
    "src/datastream.py",
    "src/transforms.py",
    "src/stage7_slice1.py",
    "src/stage7_slice2.py",
    "src/stage7b1_mechanics.py",
    "src/stage7b2_population.py",
    "src/stage7b2_measure.py",
    "src/stage7b2r_population.py",
    "src/stage8_population.py",
    "src/stage8_alpha_measure.py",
    "src/stage8_paired.py",
    "src/run_stage8_alpha.py",
    "src/run_stage8_paired.py",
    "src/reduce_stage8_alpha.py",
    "src/reduce_stage8_paired.py",
    "src/stage8_gate.py",
    "src/stage8_paired_gate.py",
    "src/test_stage8_kernel.py",
    "src/test_stage8_fault_matrix.py",
    "src/test_stage8_measure.py",
    "src/test_stage8_gate.py",
    "src/test_reduce_stage8_alpha.py",
    "src/test_reduce_stage8_paired.py",
    "src/test_stage8_paired.py",
]


def sha256_of(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prior_pins() -> dict[str, tuple[str, str]]:
    """(sha256, provenance) pins from the retained prior freeze manifests."""
    pins: dict[str, tuple[str, str]] = {}
    sources = [
        ("results/stage7b1/pre-execution-manifest.json",
         "retained Stage 7B1 freeze manifest"),
        ("results/stage7b2/pre-execution-manifest.json",
         "retained Stage 7B2 freeze manifest"),
        ("results/stage7b2-repair/pre-execution-manifest.json",
         "retained Stage 7B2-R freeze manifest"),
    ]
    for rel, provenance in sources:
        path = REPO / rel
        if not path.exists():
            continue
        manifest = json.loads(path.read_text())
        for filename, entry in manifest.get("files", {}).items():
            key = filename if filename.startswith("src/") \
                else f"src/{filename}"
            pins.setdefault(key, (entry["sha256"], provenance))
    return pins


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Stage 8 paired-arm pre-execution freeze "
                    "manifest (registered default output path; --out is a "
                    "test hook only).")
    parser.add_argument("gate_summary_json")
    parser.add_argument("--out", default=None,
                        help="override output path (test hook; the "
                             "registered path is results/"
                             "stage8-alpha-evolution-paired/"
                             "pre-execution-manifest.json)")
    args = parser.parse_args(argv[1:])
    gate = json.loads(pathlib.Path(args.gate_summary_json).read_text())
    if not gate.get("gate_passed"):
        print("REFUSING: the section 7 gate did not pass; no freeze may be "
              "committed (section 7).", file=sys.stderr)
        return 1
    for condition in ("G1_evolution_operates", "G2_implementation_integrity",
                      "G3_kernel_audit", "G4_reference_arm_integrity"):
        if not gate.get(condition, {}).get(f"passes_{condition[:2]}"):
            print(f"REFUSING: {condition} not passed.", file=sys.stderr)
            return 1

    pins = prior_pins()
    files = {}
    identity_notes = {}
    for rel in FILES:
        path = REPO / rel
        digest = sha256_of(path)
        files[rel] = {"bytes": path.stat().st_size, "sha256": digest}
        if rel in pins:
            expected, provenance = pins[rel]
            identity_notes[rel] = (
                f"byte-identical to the {provenance}" if digest == expected
                else f"HASH DRIFT versus {provenance}: {digest} != "
                     f"{expected} -- must be justified")
    drifted = {k: v for k, v in identity_notes.items() if "DRIFT" in v}

    g1 = gate["G1_evolution_operates"]
    g2 = gate["G2_implementation_integrity"]
    g3 = gate["G3_kernel_audit"]
    g4 = gate["G4_reference_arm_integrity"]
    replay = g3.get("stream_replay") or {}
    context = gate.get("factual_shakedown_context")
    gate_note = (
        "Section 7 factual gate summary. Seed list used: "
        f"{gate['pairs_used']} ({gate['pair_count']} shakedown pairs "
        "20421301+j, j=0..11, fixed before any execution at this ecology "
        "and disjoint from every retained or retired table). Pairs with "
        f"both arms COMPLETE: {gate['pairs_both_arms_complete']}/"
        f"{gate['pair_count']} (two-thirds threshold "
        f"{gate['two_thirds_threshold']}). "
        f"G1 (evolution operates, Arm M): passing pairs "
        f"{len(g1['passing_pairs'])}/{gate['two_thirds_threshold']} "
        f"required; genome-freeze violations: "
        f"{len(g1['genome_freeze_violations'])}; passes_G1="
        f"{g1['passes_G1']}. G2 (implementation integrity): invalid runs "
        f"{len(gate['invalid_runs'])}, buffer overflows "
        f"{len(g2['buffer_overflows'])}, checkpoint failures "
        f"{len(g2['checkpoint_failures'])}; passes_G2={g2['passes_G2']}. "
        "G3 (kernel audit, Arm M): kernel audit failures "
        f"{len(g3['kernel_audit_failures'])}; stream replay of seed "
        f"{replay.get('reexecuted_seed')} bit-exact="
        f"{replay.get('reexecution_identical')}; passes_G3="
        f"{g3['passes_G3']}. G4 (reference-arm integrity): failures "
        f"{len(g4['failures'])}, seed mismatches "
        f"{len(g4['seed_mismatches'])}; passes_G4={g4['passes_G4']}. "
        f"Gate passed: {gate['gate_passed']}. "
        "Factual shakedown context (threshold-free, non-binding): "
        + (json.dumps(context, sort_keys=True) if context else
           "NOT EMITTED by the gate tooling version that executed this "
           "shakedown (aggregate mutation-count / terminal-spread block "
           "was added to stage8_paired_gate.evaluate_gate only after the "
           "shakedown ran, discovered during the duplicate-session "
           "handoff; per-condition counts above are complete). "
           "Disclosed tooling amendment: the added block is stdout-only, "
           "computed from the same in-memory pair records, changes no "
           "condition and no execution semantics; stage8_paired_gate.py "
           "is outside the retained execution path (not in "
           "run_stage8_paired.FROZEN_SOURCES) and is pinned here as "
           "amended.")
    )

    manifest = {
        "protocol": "stage-8-alpha-evolution-repair-preregistration",
        "purpose": (
            "Stage 8 paired-arm pre-execution freeze (repair "
            "preregistration section 8): implementation, arm plumbing, "
            "runner, tests, output schema addendum, reducers, and gate "
            "tooling frozen together before any retained run, after the "
            "binding section 7 feasibility gate passed on the fixed "
            "12-pair shakedown table; df7b1f5/e2f580b/7d21153/27f5700 "
            "precedent."),
        "files": files,
        "shared_source_byte_identity": identity_notes,
        "feasibility_gate_summary": gate_note,
        "execution_disclosure": (
            "The retained suite may be executed with the frozen runner's "
            "--workers option: pairs are isolated seeded populations and "
            "pool.map preserves registered index order, so output is "
            "bit-identical to sequential execution; each arm's "
            "event_digest and kernel_draw_chain bind its exact streams."),
        "frozen_sources_embed_their_hashes_in_runner_output": True,
        "first_retained_outputs": {
            "raw": ("results/stage8-alpha-evolution-paired/"
                    "confirmatory-paired-20310529.json"),
            "reduced": ("results/stage8-alpha-evolution-paired/"
                        "confirmatory-paired-20310529-reduced.json"),
        },
        "authorised_execution_class": (
            "one seeded confirmatory pair suite: k = 24 pairs (48 runs), "
            "seeds 20310529 + i with Arm M and Arm R0 at each seed, "
            "W = 2400, executed once and reduced exactly once under the "
            "section 5 paired rule by the source-frozen reducer (repair "
            "preregistration sections 8(4)-8(5)); the retired tables "
            "20284617+i / 20293311+j remain unexecuted and never reused"),
        "hash_drift_versus_prior_manifests": drifted,
    }
    out_dir = (pathlib.Path(args.out).resolve()
               if args.out else REPO / "results" /
               "stage8-alpha-evolution-paired")
    out_path = out_dir / "pre-execution-manifest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out_path}")
    if drifted:
        print("DRIFT DETECTED versus prior retained manifests:", drifted,
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
