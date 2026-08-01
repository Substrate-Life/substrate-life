"""Static and retained-artifact checks for frozen Stage 7B0.

Static tests never invoke registered blocks. Retained-artifact tests are skipped
unless STAGE7B0_ARTIFACT names the already-retained first attempt.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory

import stage7b0_channel as channel
from analyze_stage7b0_channel import (
    _validate_participant,
    _validate_reserve,
    _validate_state,
    analyze_artifact,
    validate_against_output_schema,
    validate_attempt_artifact,
)
from run_stage7b0_channel import AttemptJournal, attempt_path_for_digest
from stage7b0_channel import (
    BLOCK_IDS, BLOCK_CHECK_KEYS, CHECKPOINT_REQUIREMENTS, GATE_IDS,
    PROGRAM_SPEC_CANONICAL, PROGRAM_SPEC_SHA256, PROTOCOL_RELATIVE_PATH,
    PROTOCOL_SHA256, REQUIRED_FREEZE_FILES, load_execution_permit,
)

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PROTOCOL_SHA256 = "8ecabac15a8487724b09ab6dca1340e55e63de39c9717c580cd18dd52947c113"
EXPECTED_PROGRAM_SHA256 = "5ddbf276aa0a836672b1b3011e66974ce9ecd6fedb0758a111c95766f534c344"
ZERO_DIGEST = "0" * 64


def started_payload(digest: str = ZERO_DIGEST) -> dict:
    return {
        "artifact_version": 1,
        "run_status": "STARTED",
        "decision": None,
        "scope": "Stage 7B0 scripted fixed-state mechanism verification",
        "selection_assay_run": False,
        "mutation_enabled": False,
        "mutation_rng_draws": 0,
        "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
        "programme_specification_sha256": EXPECTED_PROGRAM_SHA256,
        "freeze_manifest_sha256": digest,
        "started_at_utc": "2026-08-01T00:00:00+00:00",
        "claimed_at_utc": None,
        "claim_sha256": None,
        "blocks_expected": list(BLOCK_IDS),
        "blocks": {},
        "analysis": None,
        "exception": None,
        "partial_progress": [],
    }


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
        self.assertEqual(PROTOCOL_RELATIVE_PATH, "docs/stage-7b-fixed-allocation-channel-preregistration.md")

    def test_block_gate_and_freeze_surfaces_are_closed(self):
        self.assertEqual(BLOCK_IDS, ("A", "B", "C", "D1", "D2", "E1", "E2"))
        self.assertEqual(GATE_IDS, ("realised_treatment", "programme_identity", "allocation_identity", "direct_debit_isolation", "reversal_provenance", "recovery", "lifecycle", "topology", "closure", "no_hidden_gate"))
        self.assertEqual(set(BLOCK_CHECK_KEYS), set(BLOCK_IDS))
        self.assertTrue(all(BLOCK_CHECK_KEYS[b] for b in BLOCK_IDS))
        self.assertEqual(set(REQUIRED_FREEZE_FILES), {
            "docs/stage-7b-fixed-allocation-channel-preregistration.md",
            "src/stage7b0_channel.py", "src/run_stage7b0_channel.py",
            "src/analyze_stage7b0_channel.py", "src/test_stage7b0_channel.py",
            "src/stage7b0-output-schema.json", "src/stage7_slice1.py",
            "src/stage7_slice2.py", "src/datastream.py", "src/transforms.py",
            "src/consts.py",
        })

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

    def test_execution_permit_requires_out_of_band_digests(self):
        with self.assertRaises(FileNotFoundError):
            load_execution_permit(
                ROOT / "results" / "does-not-exist.json",
                ROOT / "results" / "does-not-exist-permit.json",
                "a" * 64, "b" * 64,
            )

    def test_started_artifact_passes_dynamic_and_schema_validation(self):
        payload = started_payload()
        validate_attempt_artifact(payload, ZERO_DIGEST)
        validate_against_output_schema(payload, ZERO_DIGEST)

    def test_wrong_out_of_band_manifest_digest_is_rejected(self):
        payload = started_payload()
        with self.assertRaises(ValueError):
            validate_attempt_artifact(payload, "1" * 64)
        with self.assertRaises(ValueError):
            validate_against_output_schema(payload, "1" * 64)

    def test_prohibited_fields_are_rejected_recursively(self):
        payload = started_payload()
        payload["partial_progress"] = [{"fitness": 1}]
        with self.assertRaises(ValueError):
            validate_attempt_artifact(payload, ZERO_DIGEST)
        with self.assertRaises(ValueError):
            validate_against_output_schema(payload, ZERO_DIGEST)

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
            "role": "founder", "organism_id": "org-0", "treatment_label": "LOW",
            "A": 204, "T": 128, "D": 255,
            "heritable_state_sha256": hashlib.sha256(
                json.dumps({"A": 204, "D": 255, "T": 128}, sort_keys=True, separators=(",", ":")).encode()
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
            "executed_at_utc": "2026-08-01T00:00:00+00:00",
            "blocks": {b: {"checks": {k: True for k in BLOCK_CHECK_KEYS[b]}} for b in BLOCK_IDS},
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
                "participant": participant,
                "S": delta_s, "R": delta_r,
                "C_S": 0, "C_R": 0,
                "gross_income": 5, "reversed_income": 0,
                "committed": 0, "destroyed": 0, "child": None,
                "events": [{
                    "event": "draw", "packet_id": 1, "quantity": 5,
                    "delta_s": delta_s, "delta_r": delta_r,
                    "input_bytes": 1, "output_bytes": 1, "transform": "RLE",
                    "s": delta_s, "r": delta_r,
                }],
            }
            self.assertTrue(_validate_state(state, treatment.label)["allocation"])

    def test_producer_block_constructor_emits_raw_only(self):
        self.assertEqual(channel._finish_block({"LOW": {}}), {"raw": {"arms": {"LOW": {}}}})

    def test_registered_entry_points_require_execution_lease(self):
        self.assertFalse(hasattr(channel, "execute_registered_protocol"))
        for name in ("_block_a", "_block_b", "_block_c", "_block_e1", "_block_e2"):
            self.assertEqual(tuple(inspect.signature(getattr(channel, name)).parameters), ("lease",))
        self.assertEqual(tuple(inspect.signature(channel._block_d).parameters)[0], "lease")
        with self.assertRaises(PermissionError):
            channel._block_a(object())

    def test_execution_lease_has_no_callback_and_checks_full_prefix(self):
        self.assertEqual(
            tuple(inspect.signature(channel.issue_execution_lease).parameters),
            ("permit", "attempt_path"),
        )
        source = (ROOT / "src" / "stage7b0_channel.py").read_text()
        self.assertIn('retained.get("partial_progress") != state["progress_prefix"]', source)
        self.assertIn("_durable_attempt_replace(", source)

    def test_durable_claim_is_process_exclusive(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "claim"
            channel._exclusive_claim(path, {"claim": 1})
            with self.assertRaises(FileExistsError):
                channel._exclusive_claim(path, {"claim": 2})

    def test_failed_journal_write_does_not_mutate_last_good_payload(self):
        original = started_payload()
        with TemporaryDirectory() as directory:
            path = Path(directory) / "not-a-registered-attempt.json"
            path.write_text(json.dumps(original))
            journal = AttemptJournal(path, original, ZERO_DIGEST)
            with patch("run_stage7b0_channel._durable_replace", side_effect=OSError("disk")):
                with self.assertRaises(OSError):
                    journal.retain_invalid(RuntimeError("failure"))
            self.assertEqual(json.loads(path.read_text()), original)
            self.assertEqual(journal.payload, original)

    def test_attempt_path_is_deterministic_per_manifest_digest(self):
        digest = "a" * 64
        self.assertEqual(attempt_path_for_digest(digest), ROOT / "results" / f"stage7b0-attempt-{digest}.json")

    def test_isolated_child_identity_is_treatment_neutral(self):
        source = (ROOT / "src" / "stage7b0_channel.py").read_text()
        mechanics = (ROOT / "src" / "stage7_slice1.py").read_text()
        self.assertNotIn("child-{treatment.label}", source)
        self.assertNotIn("child-LOW", source)
        self.assertNotIn("child-HIGH", source)
        self.assertIn("a=self.a, t=self.t, d=self.d", mechanics)
        self.assertIn("child.a, child.t, child.d", source)


@unittest.skipUnless(os.environ.get("STAGE7B0_ARTIFACT"), "set STAGE7B0_ARTIFACT to inspect a retained registered execution")
class Stage7B0RetainedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(os.environ["STAGE7B0_ARTIFACT"]).resolve()
        cls.artifact = json.loads(cls.path.read_text())
        cls.digest = cls.artifact["freeze_manifest_sha256"]
        validate_attempt_artifact(cls.artifact, cls.digest)
        validate_against_output_schema(cls.artifact, cls.digest)
        cls.analysis = cls.artifact["analysis"]

    def test_artifact_is_not_a_selection_or_mutation_assay(self):
        self.assertFalse(self.artifact["selection_assay_run"])
        self.assertFalse(self.artifact["mutation_enabled"])
        self.assertNotIn("selection_coefficient", self.artifact)
        self.assertNotIn("p_value", self.artifact)
        self.assertNotIn("ess", self.artifact)

    def test_artifact_contains_every_registered_block_and_gate_once(self):
        self.assertEqual(tuple(self.artifact["blocks"]), BLOCK_IDS)
        self.assertEqual(tuple(self.analysis["gates"]), GATE_IDS)

    def test_analysis_decision_is_all_or_nothing(self):
        expected = "PASS" if all(g["passed"] for g in self.analysis["gates"].values()) else "FAIL"
        self.assertEqual(self.analysis["decision"], expected)
        self.assertEqual(self.artifact["decision"], expected)

    def test_artifact_matches_frozen_protocol_and_manifest(self):
        self.assertEqual(self.artifact["protocol_sha256"], PROTOCOL_SHA256)
        manifest = ROOT / "results" / "stage7b0-pre-execution-manifest.json"
        pin = ROOT / "results" / "stage7b0-detached-manifest-pin.json"
        permit = load_execution_permit(
            manifest, pin, hashlib.sha256(manifest.read_bytes()).hexdigest(),
            hashlib.sha256(pin.read_bytes()).hexdigest(),
        )
        self.assertEqual(self.digest, permit.manifest_sha256)


if __name__ == "__main__":
    unittest.main()
