"""Reproducible retained runner for the Stage 7 Slice 2A mechanics trace."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from stage7_slice2 import run_slice2_trace


SOURCE_NAMES = (
    "stage7_slice1.py",
    "stage7_slice2.py",
    "test_stage7_slice1.py",
    "test_stage7_slice2.py",
    "run_stage7_slice2_trace.py",
)


def _source_manifest() -> dict[str, dict[str, int | str]]:
    source_dir = Path(__file__).resolve().parent
    manifest: dict[str, dict[str, int | str]] = {}
    for name in SOURCE_NAMES:
        path = source_dir / name
        data = path.read_bytes()
        stat = path.stat()
        manifest[name] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
        }
    return manifest


def _exact_json(value: Any) -> str:
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return f"{value.numerator}/{value.denominator}"
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def write_trace_artifact(output: str | Path, ticks: int = 20) -> dict[str, Any]:
    """Execute the mechanics-only trace and atomically retain exact JSON."""
    artifact = run_slice2_trace(ticks=ticks)
    artifact["source_manifest"] = _source_manifest()
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(artifact, default=_exact_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output_path)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Stage 7 Slice 2A mechanics only; no scientific assay")
    parser.add_argument("--ticks", type=int, default=20)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "stage7-slice2-mechanics-trace.json",
    )
    args = parser.parse_args()
    artifact = write_trace_artifact(args.output, ticks=args.ticks)
    print(json.dumps({
        "output": str(args.output),
        "ticks": args.ticks,
        "assay_run": artifact["assay_run"],
        "reserve_closed": artifact["final_reserve"]["closed"],
        "packets_closed": artifact["final_packets_closed"],
        "memory_closed": artifact["final_memory_closed"],
        "closure_checkpoints": len(artifact["closure_history"]),
        "counts": artifact["counts"],
    }, default=_exact_json, sort_keys=True))


if __name__ == "__main__":
    main()
