"""Guarded, deterministic, single-attempt CLI for frozen Stage 7B0.

Importing is inert. Every execution first claims one manifest-derived path,
then runs through a one-use core lease whose evidence must be durably visible.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

from analyze_stage7b0_channel import (
    analyze_artifact, validate_against_output_schema, validate_attempt_artifact,
)
from stage7b0_channel import (
    BLOCK_IDS, PROGRAM_SPEC_SHA256, PROTOCOL_SHA256,
    _execute_claimed_protocol, invalidate_execution_lease,
    issue_execution_lease, load_execution_permit,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "results" / "stage7b0-pre-execution-manifest.json"
DEFAULT_DETACHED_PERMIT = ROOT / "results" / "stage7b0-detached-manifest-pin.json"
PHRASE_PREFIX = "EXECUTE-FROZEN-STAGE7B0:"


def attempt_path_for_digest(manifest_sha256: str) -> Path:
    if len(manifest_sha256) != 64 or any(c not in "0123456789abcdef" for c in manifest_sha256):
        raise ValueError("manifest digest must be 64 lowercase hexadecimal characters")
    return ROOT / "results" / f"stage7b0-attempt-{manifest_sha256}.json"


def _encoded(payload: dict[str, Any], manifest_sha256: str) -> bytes:
    validate_attempt_artifact(payload, manifest_sha256)
    validate_against_output_schema(payload, manifest_sha256)
    return (json.dumps(payload, indent=2, sort_keys=False) + "\n").encode()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _exclusive_create(path: Path, payload: dict[str, Any], manifest_sha256: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _encoded(payload, manifest_sha256)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    _fsync_directory(path.parent)


def _durable_replace(path: Path, payload: dict[str, Any], manifest_sha256: str) -> None:
    data = _encoded(payload, manifest_sha256)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    except BaseException:
        try:
            temporary.unlink(missing_ok=True)
        finally:
            raise


class AttemptJournal:
    """Finalization helper that always starts from last durable core state."""

    def __init__(self, path: Path, started: dict[str, Any], manifest_sha256: str) -> None:
        self.path = path
        self.manifest_sha256 = manifest_sha256
        self.payload = deepcopy(started)

    def retain_invalid(self, exc: BaseException) -> None:
        candidate = json.loads(self.path.read_text())
        claim_path = Path(str(self.path) + ".claim")
        if candidate.get("claim_sha256") is None and claim_path.is_file():
            claim = json.loads(claim_path.read_text())
            import hashlib
            candidate["claimed_at_utc"] = claim["claimed_at_utc"]
            candidate["claim_sha256"] = hashlib.sha256(claim_path.read_bytes()).hexdigest()
        candidate.update({
            "run_status": "INVALID",
            "decision": "INVALID",
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "exception": {"type": type(exc).__name__, "message": str(exc)},
        })
        _durable_replace(self.path, candidate, self.manifest_sha256)
        self.payload = candidate


def run_once(
    manifest: Path,
    detached_permit: Path,
    phrase: str,
    expected_manifest_sha256: str,
    expected_detached_permit_sha256: str,
) -> tuple[int, Path]:
    expected_phrase = PHRASE_PREFIX + expected_manifest_sha256
    if phrase != expected_phrase:
        raise PermissionError(f"registered execution requires exact phrase {expected_phrase!r}")
    permit = load_execution_permit(
        manifest, detached_permit,
        expected_manifest_sha256, expected_detached_permit_sha256,
    )
    output = attempt_path_for_digest(permit.manifest_sha256)
    started = {
        "artifact_version": 1,
        "run_status": "STARTED",
        "decision": None,
        "scope": "Stage 7B0 scripted fixed-state mechanism verification",
        "selection_assay_run": False,
        "mutation_enabled": False,
        "mutation_rng_draws": 0,
        "protocol_sha256": PROTOCOL_SHA256,
        "programme_specification_sha256": PROGRAM_SPEC_SHA256,
        "freeze_manifest_sha256": permit.manifest_sha256,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "claimed_at_utc": None,
        "claim_sha256": None,
        "blocks_expected": list(BLOCK_IDS),
        "blocks": {},
        "analysis": None,
        "exception": None,
        "partial_progress": [],
    }
    _exclusive_create(output, started, permit.manifest_sha256)
    journal = AttemptJournal(output, started, permit.manifest_sha256)
    lease = None
    try:
        lease = issue_execution_lease(permit, output)
        artifact = _execute_claimed_protocol(lease)
        lease = None  # the core consumes a successfully completed lease
        analysis = analyze_artifact(artifact, permit.manifest_sha256)
        retained = json.loads(output.read_text())
        completed = {
            **artifact,
            "artifact_version": 1,
            "run_status": "COMPLETED",
            "decision": analysis["decision"],
            "started_at_utc": started["started_at_utc"],
            "claimed_at_utc": retained["claimed_at_utc"],
            "claim_sha256": retained["claim_sha256"],
            "blocks_expected": list(BLOCK_IDS),
            "analysis": analysis,
            "exception": None,
            "partial_progress": retained["partial_progress"],
        }
        _durable_replace(output, completed, permit.manifest_sha256)
        journal.payload = completed
        return (0 if analysis["decision"] == "PASS" else 1), output
    except BaseException as exc:
        if lease is not None:
            invalidate_execution_lease(lease)
        journal.retain_invalid(exc)
        return 2, output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Execute one published, hash-frozen Stage 7B0 attempt"
    )
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--expected-pin-sha256", required=True)
    parser.add_argument("--authorization-phrase", required=True)
    args = parser.parse_args(argv)
    try:
        code, output = run_once(
            DEFAULT_MANIFEST, DEFAULT_DETACHED_PERMIT,
            args.authorization_phrase, args.expected_manifest_sha256,
            args.expected_pin_sha256,
        )
        print(output)
        return code
    except (FileNotFoundError, FileExistsError, PermissionError, ValueError) as exc:
        print(f"PRE-EXECUTION REFUSAL: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
