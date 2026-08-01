"""Static and retained-result checks for deterministic Stage 7B0.

Static tests never invoke Blocks A–E. Retained-result tests run only when
STAGE7B0_ARTIFACT names an already-produced deterministic artifact.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest

import stage7b0_channel as channel
from analyze_stage7b0_channel import (
    _validate_participant,
    _validate_reserve,
    _validate_state,
    analyze_artifact,
    validate_attempt_artifact,
)
from stage7b0_channel import (
    BLOCK_IDS, BLOCK_CHECK_KEYS, CHECKPOINT_REQUIREMENTS, GATE_IDS,
    PROGRAM_SPEC_CANONICAL, PROGRAM_SPEC_SHA256, PROTOCOL_RELATIVE_PATH,
    PROTOCOL_SHA256, REQUIRED_FREEZE_FILES,
)

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PROTOCOL_SHA256 = "8ecabac15a8487724b09ab6dca1340e55e63de39c9717c580cd18dd52947c113"
EXPECTED_PROGRAM_SHA256 = "5ddbf276aa0a836672b1b3011e66974ce9ecd6fedb0758a111c95766f534c344"
ZERO_DIGEST = "0" * 64


class Stage7B0StaticContractTests(unittest.TestCase):
    def test_frozen_protocol_and_programme_identifiers(self):
        self.assertEqual(PROTOCOL_SHA256, EXPECTED_PROTOCOL_SHA256)
        self.assertEqual(PROGRAM_SPEC_SHA256, EXPECTED_PROGRAM_SHA256)
        self.assertEqual(
            PROGRAM_SPEC_CANONICAL,
            '[{"extent":256,"op":"FORAGE_RLE"},'
            '{"op":"ALLOC_OFFSPRING","resolved_bytes":64},'
            '{"instructions":11,"op":"COPY_BLOCK"},{"op":"DIVIDE"}]',
        )
        self.assertEqual(
            PROTOCOL_RELATIVE_PATH,
            "docs/stage-7b-fixed-allocation-channel-preregistration.md",
        )

    def test_block_gate_and_source_surfaces_are_closed(self):
        self.assertEqual(BLOCK_IDS, ("A", "B", "C", "D1", "D2", "E1", "E2"))
        self.assertEqual(GATE_IDS, (
            "realised_treatment", "programme_identity", "allocation_identity",
            "direct_debit_isolation", "reversal_provenance", "recovery",
            "lifecycle", "topology", "closure", "no_hidden_gate",
        ))
        self.assertEqual(set(BLOCK_CHECK_KEYS), set(BLOCK_IDS))
        self.assertEqual(len(REQUIRED_FREEZE_FILES), 10)

    def test_named_checkpoint_contract_is_closed(self):
        self.assertEqual(CHECKPOINT_REQUIREMENTS, {
            "A": ("INITIAL", "POST_FORAGE", "POST_ALLOC", "POST_COPY", "POST_DIVIDE", "FINAL"),
            "B": ("INITIAL", "POST_PACKET_ARRIVAL", "POST_MEMBER", "POST_ADMISSION", "TICK_COMPLETE"),
            "C": ("INITIAL", "POST_FORAGE", "POST_ALLOC", "POST_COPY", "POST_DIVIDE", "FINAL"),
            "D1": ("INITIAL", "POST_PACKET_ARRIVAL", "POST_MEMBER", "POST_REJECTION", "TICK_COMPLETE"),
            "D2": ("INITIAL", "POST_PACKET_ARRIVAL", "POST_MEMBER", "POST_REJECTION", "TICK_COMPLETE"),
            "E1": ("INITIAL", "POST_FORAGE", "POST_REVERSAL", "FINAL"),
            "E2": ("INITIAL", "POST_FORAGE", "POST_ALLOC", "POST_COPY", "POST_DIVIDE", "POST_REVERSAL", "FINAL"),
        })

    def test_execution_path_has_no_authorization_ceremony(self):
        core = (ROOT / "src" / "stage7b0_channel.py").read_text()
        runner = (ROOT / "src" / "run_stage7b0_channel.py").read_text()
        for forbidden in (
            "ExecutionPermit", "ExecutionLease", "issue_execution_lease",
            "detached_permit", "authorization_phrase", ".claim",
        ):
            self.assertNotIn(forbidden, core + runner)
        self.assertTrue(callable(channel.execute_deterministic_protocol))

    def test_source_manifest_is_plain_and_self_checked(self):
        manifest = ROOT / "results" / "stage7b0-pre-execution-manifest.json"
        if manifest.exists():
            manifest_bytes = manifest.read_bytes()
            loaded = json.loads(manifest_bytes)
            digest = hashlib.sha256(manifest_bytes).hexdigest()
            self.assertEqual(len(digest), 64)
            self.assertEqual(tuple(loaded["files"]), REQUIRED_FREEZE_FILES)
            source_commit = loaded["source_commit"]
            for relative_path, expected in loaded["files"].items():
                result = subprocess.run(
                    ["git", "show", f"{source_commit}:{relative_path}"],
                    cwd=ROOT,
                    capture_output=True,
                    check=True,
                )
                self.assertEqual(len(result.stdout), expected["bytes"])
                self.assertEqual(
                    hashlib.sha256(result.stdout).hexdigest(),
                    expected["sha256"],
                )

    def test_forged_closed_boolean_cannot_override_reserve_equation(self):
        forged = {
            "kind": "isolated", "opening_S": 100, "opening_R": 0,
            "current_S": 100, "current_R": 0, "committed": 0,
            "destroyed": 0, "gross_income": 0, "reversed_income": 0,
            "C_S": 0, "C_R": 0, "lhs": 0, "rhs": 999, "closed": True,
        }
        with self.assertRaises(ValueError):
            _validate_reserve(forged, "synthetic.reserve")

    def test_wrong_label_to_trait_mapping_is_invalid(self):
        forged = {
            "role": "founder", "organism_id": "org-0",
            "treatment_label": "LOW", "A": 204, "T": 128, "D": 255,
            "heritable_state_sha256": hashlib.sha256(
                json.dumps(
                    {"A": 204, "D": 255, "T": 128},
                    sort_keys=True, separators=(",", ":"),
                ).encode()
            ).hexdigest(),
        }
        with self.assertRaises(ValueError):
            _validate_participant(forged, "synthetic.participant")

    def test_analyzer_rejects_producer_boolean_artifact(self):
        synthetic = {
            "scope": "Stage 7B0 scripted fixed-state mechanism verification",
            "selection_assay_run": False, "mutation_enabled": False,
            "mutation_rng_draws": 0,
            "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
            "programme_specification_sha256": EXPECTED_PROGRAM_SHA256,
            "freeze_manifest_sha256": ZERO_DIGEST,
            "blocks": {
                block: {"checks": {key: True for key in BLOCK_CHECK_KEYS[block]}}
                for block in BLOCK_IDS
            },
        }
        with self.assertRaises(ValueError):
            analyze_artifact(synthetic, ZERO_DIGEST)

    def test_registered_allocation_fraction_is_a_over_d(self):
        for treatment, delta_s, delta_r in (
            (channel.LOW, 3, 2), (channel.HIGH, 1, 4),
        ):
            participant = channel._participant_values(
                "parent", "parent", treatment.label,
                treatment.a, treatment.t, treatment.d,
            )
            state = {
                "participant": participant, "S": delta_s, "R": delta_r,
                "C_S": 0, "C_R": 0, "gross_income": 5,
                "reversed_income": 0, "committed": 0, "destroyed": 0,
                "child": None,
                "events": [{
                    "event": "draw", "packet_id": 1, "quantity": 5,
                    "delta_s": delta_s, "delta_r": delta_r,
                    "input_bytes": 1, "output_bytes": 1, "transform": "RLE",
                    "s": delta_s, "r": delta_r,
                }],
            }
            self.assertTrue(_validate_state(state, treatment.label)["allocation"])

    def test_somatic_read_and_compress_debits_are_direct(self):
        participant = channel._participant_values(
            "parent", "parent", "LOW", 102, 128, 255,
        )
        state = {
            "participant": participant, "S": 98, "R": 0,
            "C_S": 2, "C_R": 0, "gross_income": 0,
            "reversed_income": 0, "committed": 0, "destroyed": 0,
            "child": None,
            "events": [
                {"event": "charge_s", "s": 99, "r": 0,
                 "reason": "READ", "amount": 1},
                {"event": "charge_s", "s": 98, "r": 0,
                 "reason": "TRANSFORM_COMPRESS_256", "amount": 1},
            ],
        }
        self.assertTrue(_validate_state(state, "synthetic.direct")["direct"])

    def test_producer_block_constructor_emits_raw_only(self):
        self.assertEqual(
            channel._finish_block({"LOW": {}}),
            {"raw": {"arms": {"LOW": {}}}},
        )

    def test_checkpoint_account_events_are_snapshotted(self):
        source = (ROOT / "src" / "stage7b0_channel.py").read_text()
        self.assertIn('"events": _jsonable(organism.events)', source)
        self.assertNotIn('"events": organism.events', source)

    def test_isolated_child_identity_is_inherited_and_label_neutral(self):
        source = (ROOT / "src" / "stage7b0_channel.py").read_text()
        mechanics = (ROOT / "src" / "stage7_slice1.py").read_text()
        self.assertNotIn("child-{treatment.label}", source)
        self.assertIn("a=self.a, t=self.t, d=self.d", mechanics)
        self.assertIn("child.a, child.t, child.d", source)


@unittest.skipUnless(
    os.environ.get("STAGE7B0_ARTIFACT"),
    "set STAGE7B0_ARTIFACT to inspect a retained deterministic result",
)
class Stage7B0RetainedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(os.environ["STAGE7B0_ARTIFACT"]).resolve()
        cls.artifact = json.loads(cls.path.read_text())
        cls.digest = cls.artifact["freeze_manifest_sha256"]
        validate_attempt_artifact(cls.artifact, cls.digest)
        cls.analysis = cls.artifact["analysis"]

    def test_artifact_is_not_a_selection_or_mutation_assay(self):
        self.assertFalse(self.artifact["selection_assay_run"])
        self.assertFalse(self.artifact["mutation_enabled"])
        self.assertEqual(self.artifact["mutation_rng_draws"], 0)

    def test_artifact_contains_every_registered_block_and_gate_once(self):
        self.assertEqual(tuple(self.artifact["blocks"]), BLOCK_IDS)
        self.assertEqual(tuple(self.analysis["gates"]), GATE_IDS)

    def test_analysis_decision_is_all_or_nothing(self):
        expected = "PASS" if all(
            gate["passed"] for gate in self.analysis["gates"].values()
        ) else "FAIL"
        self.assertEqual(self.analysis["decision"], expected)
        self.assertEqual(self.artifact["decision"], expected)

    def test_artifact_matches_plain_source_manifest(self):
        manifest = ROOT / "results" / "stage7b0-pre-execution-manifest.json"
        _, digest = load_source_manifest(manifest)
        self.assertEqual(self.digest, digest)


if __name__ == "__main__":
    unittest.main()
