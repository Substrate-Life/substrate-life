"""Freeze-manifest builder test matrix (gate-repair registration window).

Covers ``build_stage8_paired_freeze_manifest``: refusal to freeze on any
gate failure or missing condition, the registered default output path,
the ``--out`` test hook, manifest structure, and the integrity of the
embedded per-file SHA-256 + byte-size pins.  All tests write only to
temporary directories; the retained results tree is never touched.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import tempfile
import unittest

from build_stage8_paired_freeze_manifest import (
    FILES,
    REPO,
    main,
    prior_pins,
    sha256_of,
)

REPLAY_OK = {
    "reexecuted_seed": 20421301,
    "records_replayed": 900,
    "draws_replayed": 1800,
    "mismatches": [],
    "reexecution_identical": True,
    "passes": True,
}


def _passing_gate() -> dict:
    return {
        "gate": "stage-8-alpha-evolution-repair-preregistration section 7",
        "pairs_used": [20421301 + j for j in range(12)],
        "pair_count": 12,
        "two_thirds_threshold": 8,
        "pairs_both_arms_complete": 12,
        "invalid_runs": [],
        "G1_evolution_operates": {
            "passing_pairs": list(range(12)),
            "threshold": 8,
            "genome_freeze_violations": [],
            "passes_G1": True,
        },
        "G2_implementation_integrity": {
            "buffer_overflows": [],
            "checkpoint_failures": [],
            "passes_G2": True,
        },
        "G3_kernel_audit": {
            "kernel_audit_failures": [],
            "stream_replay": dict(REPLAY_OK),
            "passes_G3": True,
        },
        "G4_reference_arm_integrity": {
            "failures": [],
            "seed_mismatches": [],
            "passes_G4": True,
        },
        "factual_shakedown_context": {
            "note": "descriptive only; reported without thresholds per "
                    "section 7; may not resize anything",
            "total_m_mutation_decision_records": 5583,
            "total_m_kernel_draws": 11166,
            "complete_arms_terminal_live_min": 17,
            "complete_arms_terminal_live_max": 48,
            "m_terminal_distinct_A_min": 2,
            "m_terminal_distinct_A_max": 9,
            "extinct_complete_arms": 0,
        },
        "gate_passed": True,
    }


class FreezeManifestBuilderTests(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name)
        self.gate_path = self.tmp / "gate-summary.json"
        self.out_dir = self.tmp / "manifest-out"

    def _write_gate(self, gate: dict) -> pathlib.Path:
        self.gate_path.write_text(json.dumps(gate))
        return self.gate_path

    def test_every_pinned_file_exists_in_repo(self):
        missing = [rel for rel in FILES if not (REPO / rel).exists()]
        self.assertEqual(missing, [])

    def test_pinned_files_cover_both_registration_docs_and_addendum(self):
        for required in (
                "docs/stage-8-alpha-evolution-preregistration.md",
                "docs/stage-8-alpha-evolution-repair-preregistration.md",
                "docs/stage8-paired-output-schema-addendum.md",
                "src/run_stage8_paired.py",
                "src/reduce_stage8_paired.py",
                "src/stage7b1_mechanics.py",
                "src/test_stage8_fault_matrix.py"):
            self.assertIn(required, FILES)

    def test_refuses_when_gate_did_not_pass(self):
        gate = _passing_gate()
        gate["gate_passed"] = False
        result = main(["prog", str(self._write_gate(gate)),
                       "--out", str(self.out_dir)])
        self.assertEqual(result, 1)
        self.assertFalse(
            (self.out_dir / "pre-execution-manifest.json").exists())

    def test_refuses_when_any_condition_block_fails(self):
        for condition in ("G1_evolution_operates",
                          "G2_implementation_integrity",
                          "G3_kernel_audit", "G4_reference_arm_integrity"):
            with self.subTest(condition=condition):
                gate = _passing_gate()
                gate[condition]["passes_" + condition[:2]] = False
                result = main(["prog", str(self._write_gate(gate)),
                               "--out", str(self.out_dir)])
                self.assertEqual(result, 1)
                self.assertFalse(
                    (self.out_dir /
                     "pre-execution-manifest.json").exists())

    def test_happy_path_writes_structured_manifest_via_test_hook(self):
        gate_path = self._write_gate(_passing_gate())
        result = main(["prog", str(gate_path), "--out", str(self.out_dir)])
        self.assertEqual(result, 0)
        path = self.out_dir / "pre-execution-manifest.json"
        self.assertTrue(path.exists())
        manifest = json.loads(path.read_text())
        # Every pinned file carries sha256 + byte size, and the digests
        # match the current bytes.
        self.assertEqual(set(manifest["files"]), set(FILES))
        for rel, entry in manifest["files"].items():
            blob = (REPO / rel).read_bytes()
            self.assertEqual(entry["bytes"], len(blob))
            self.assertEqual(entry["sha256"],
                             hashlib.sha256(blob).hexdigest())
        # The embedded feasibility-gate note records the factual summary.
        note = manifest["feasibility_gate_summary"]
        self.assertIn("12 shakedown pairs", note)
        self.assertIn("both arms COMPLETE: 12/12", note)
        self.assertIn("passes_G1=True", note)
        self.assertIn("checkpoint failures 0", note)
        self.assertIn("bit-exact=True", note)
        self.assertIn("Gate passed: True", note)
        self.assertIn("Factual shakedown context (threshold-free,"
                      " non-binding)", note)
        self.assertIn("5583", note)  # factual aggregate carried through
        # Registered execution class and retained output names.
        self.assertEqual(
            manifest["first_retained_outputs"]["raw"],
            "results/stage8-alpha-evolution-paired/"
            "confirmatory-paired-20310529.json")
        self.assertEqual(
            manifest["first_retained_outputs"]["reduced"],
            "results/stage8-alpha-evolution-paired/"
            "confirmatory-paired-20310529-reduced.json")
        self.assertIn("k = 24 pairs (48 runs)",
                      manifest["authorised_execution_class"])
        self.assertIn("executed once and reduced exactly once",
                      manifest["authorised_execution_class"])
        self.assertIsInstance(
            manifest["hash_drift_versus_prior_manifests"], dict)

    def test_sha256_helper_matches_hashlib(self):
        probe = self.tmp / "probe.txt"
        probe.write_bytes(b"substrate")
        self.assertEqual(sha256_of(probe),
                         hashlib.sha256(b"substrate").hexdigest())

    def test_prior_pins_returns_sha_provenance_pairs(self):
        pins = prior_pins()
        for key, (digest, provenance) in pins.items():
            self.assertTrue(key.startswith("src/"))
            self.assertEqual(len(digest), 64)
            self.assertIn("freeze manifest", provenance)


if __name__ == "__main__":
    unittest.main()
