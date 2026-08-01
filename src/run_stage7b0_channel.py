"""Deterministic Stage 7B0 reproduction CLI.

No authorization or one-use machinery is needed: fixed inputs and mutation-off
execution make the scientific result exactly reproducible. Importing is inert.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from analyze_stage7b0_channel import analyze_artifact, validate_attempt_artifact
from stage7b0_channel import (
    PROGRAM_SPEC_SHA256,
    PROTOCOL_SHA256,
    REQUIRED_FREEZE_FILES,
    execute_deterministic_protocol,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "results" / "stage7b0-pre-execution-manifest.json"
DEFAULT_OUTPUT = ROOT / "results" / "stage7b0-channel-result.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_source_manifest(path: Path) -> tuple[dict[str, Any], str]:
    """Check the plain reproducibility manifest against current file bytes."""
    manifest = json.loads(path.read_text())
    files = manifest.get("files")
    if not isinstance(files, dict) or tuple(files) != REQUIRED_FREEZE_FILES:
        raise ValueError("manifest file set/order mismatch")
    if manifest.get("protocol_sha256") != PROTOCOL_SHA256:
        raise ValueError("protocol hash mismatch")
    if manifest.get("programme_specification_sha256") != PROGRAM_SPEC_SHA256:
        raise ValueError("programme hash mismatch")
    for relative_path, expected in files.items():
        target = ROOT / relative_path
        if not target.is_file():
            raise FileNotFoundError(target)
        if set(expected) != {"sha256", "bytes"}:
            raise ValueError(f"bad manifest entry: {relative_path}")
        if _sha256(target) != expected["sha256"] or target.stat().st_size != expected["bytes"]:
            raise ValueError(f"current bytes differ from manifest: {relative_path}")
    return manifest, _sha256(path)


def _encoded(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=False) + "\n").encode()


def run_deterministic(
    manifest_path: Path = DEFAULT_MANIFEST,
    output_path: Path = DEFAULT_OUTPUT,
    *,
    overwrite: bool = False,
) -> tuple[int, Path]:
    _, manifest_sha256 = load_source_manifest(manifest_path)
    evidence: list[dict[str, Any]] = []
    try:
        raw, evidence = execute_deterministic_protocol(manifest_sha256, evidence)
        analysis = analyze_artifact(raw, manifest_sha256)
        completed = {
            **raw,
            "artifact_version": 1,
            "run_status": "COMPLETED",
            "decision": analysis["decision"],
            "analysis": analysis,
        }
        validate_attempt_artifact(completed, manifest_sha256)
        payload = completed
        code = 0 if analysis["decision"] == "PASS" else 1
    except BaseException as exc:
        payload = {
            "artifact_version": 1,
            "run_status": "INVALID",
            "decision": "INVALID",
            "freeze_manifest_sha256": manifest_sha256,
            "exception": {"type": type(exc).__name__, "message": str(exc)},
            "partial_progress": evidence,
        }
        code = 2
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not overwrite:
        raise FileExistsError(output_path)
    output_path.write_bytes(_encoded(payload))
    return code, output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the deterministic Stage 7B0 mechanism trace",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        code, output = run_deterministic(
            args.manifest.resolve(), args.output.resolve(), overwrite=args.overwrite,
        )
        print(output)
        return code
    except (FileNotFoundError, ValueError) as exc:
        print(f"REFUSAL: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
