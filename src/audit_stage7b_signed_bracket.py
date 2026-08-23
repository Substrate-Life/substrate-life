"""Read-only integrity audit and descriptive dispersion scoping for the
Stage 7B signed-bracket retained artifacts.

This tool modifies nothing. It never writes inside the repository. Its
checks are:

  A. artifact hash verification (raw + reduced) against recorded values;
  B. independent re-reduction: the frozen reducer is re-executed against
     the retained raw artifact with output redirected OUTSIDE the repo,
     then byte-compared with the retained reduced artifact;
  C. an independent recomputation of the registered outcome (midpoints,
     paired differences, lower-middle median, sign split, status counts)
     implemented here from scratch over the raw certificates;
  D. pre-execution-manifest drift detection for every Stage 7B generation
     (re-hashing every pinned file);
  E. descriptive dispersion statistics of the paired bracket differences,
     recorded strictly as non-binding design input for a future
     superseding preregistration. No threshold recommendation is made and
     none may be inferred; the closed registration is not retuned.

Evidence class: post-retention audit of already-classified artifacts.
It makes no new fitness, selection, or contrast claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent

SIGNED_BRACKET_DIR = "results/stage7b-signed-bracket"
RAW_NAME = "stage7b-signed-bracket-result.json"
REDUCED_NAME = "stage7b-signed-bracket-reduced.json"
# Recorded in docs/stage-7b-signed-bracket-execution-note.md.
EXECUTION_NOTE_RAW_SHA256 = (
    "6268a3dab1db878e72af565863b3d1a11831df02f3b3407693e8586d13273d3d")
EXECUTION_NOTE_RAW_BYTES = 18_828_711

PRE_EXECUTION_MANIFESTS = {
    "stage7b0": "results/stage7b0/pre-execution-manifest.json",
    "stage7b1": "results/stage7b1/pre-execution-manifest.json",
    "stage7b2": "results/stage7b2/pre-execution-manifest.json",
    "signed-bracket": f"{SIGNED_BRACKET_DIR}/pre-execution-manifest.json",
}

GENOTYPE_ORDER = ("204", "102")  # Delta_i = mid(204) - mid(102), carried order.
FINITE_ROOT_STATUSES = {"SUPERCRITICAL", "CRITICAL", "SUBCRITICAL"}


def parse_rat(text: str) -> Fraction:
    numerator, _, denominator = text.partition("/")
    return Fraction(int(numerator), int(denominator))


def fmt_rat(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def sha256_file(path: Path) -> tuple[str, int]:
    payload = path.read_bytes()
    return hashlib.sha256(payload).hexdigest(), len(payload)


def bracket_midpoint(certificate: dict[str, Any]) -> Fraction | None:
    """Midpoint of a certified finite-root bracket; None otherwise."""
    if certificate["status"] not in FINITE_ROOT_STATUSES:
        return None
    r_lo = parse_rat(certificate["r_lo"])
    r_hi = parse_rat(certificate["r_hi"])
    return (r_lo + r_hi) / 2


def median_lower_middle(values: list[Fraction]) -> Fraction | None:
    """Registered even-k convention: lower middle of the sorted values."""
    if not values:
        return None
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) // 2]


def quantile_lower_middle(values: list[Fraction], q_index: int,
                          count: int) -> Fraction | None:
    """Lower-middle order statistic at rank ``q_index`` of ``count``."""
    if not values:
        return None
    ordered = sorted(values)
    rank = (q_index * (len(ordered) - 1)) // max(count - 1, 1)
    return ordered[rank]


def independent_outcome(
        replicates: list[dict[str, Any]]) -> dict[str, Any]:
    """Recompute the section-3-table outcome from raw solver certificates."""
    deltas: list[Fraction] = []
    sign_split = {"positive": 0, "negative": 0, "zero": 0}
    statuses: dict[str, dict[str, int]] = {
        "102": {"SUPERCRITICAL": 0, "SUBCRITICAL": 0, "CRITICAL": 0},
        "204": {"SUPERCRITICAL": 0, "SUBCRITICAL": 0, "CRITICAL": 0},
    }
    complete_pairs = 0
    for replicate in replicates:
        if replicate.get("classification") != "COMPLETE":
            continue
        certificates = replicate["solver_certificates"]
        mids: dict[str, Fraction | None] = {}
        for genotype in ("102", "204"):
            certificate = certificates[genotype]
            statuses[genotype][certificate["status"]] = (
                statuses[genotype].get(certificate["status"], 0) + 1)
            mids[genotype] = bracket_midpoint(certificate)
        if mids["102"] is not None and mids["204"] is not None:
            delta = mids["204"] - mids["102"]
            deltas.append(delta)
            complete_pairs += 1
            if delta > 0:
                sign_split["positive"] += 1
            elif delta < 0:
                sign_split["negative"] += 1
            else:
                sign_split["zero"] += 1
    median_delta = median_lower_middle(deltas)
    floor = Fraction(1, 100)
    return {
        "complete_pairs": complete_pairs,
        "median_paired_difference": (
            None if median_delta is None else fmt_rat(median_delta)),
        "sign_split": sign_split,
        "statuses": statuses,
        "subcritical_at_this_ecology": {
            genotype: counts["SUBCRITICAL"] >= 16
            for genotype, counts in statuses.items()
        },
        "pairs_at_or_above_floor_abs": sum(
            1 for delta in deltas if abs(delta) >= floor),
        "deltas": [fmt_rat(delta) for delta in sorted(deltas)],
    }


def check_artifact_hashes() -> dict[str, Any]:
    raw_path = REPO / SIGNED_BRACKET_DIR / RAW_NAME
    reduced_path = REPO / SIGNED_BRACKET_DIR / REDUCED_NAME
    raw_sha, raw_bytes = sha256_file(raw_path)
    reduced_sha, reduced_bytes = sha256_file(reduced_path)
    reduced = json.loads(reduced_path.read_text())
    consumed = reduced["consumed_raw_artifact"]
    return {
        "raw_sha256": raw_sha,
        "raw_bytes": raw_bytes,
        "matches_execution_note": (
            raw_sha == EXECUTION_NOTE_RAW_SHA256
            and raw_bytes == EXECUTION_NOTE_RAW_BYTES),
        "matches_reduced_embedded_record": (
            consumed["sha256"] == raw_sha
            and consumed["bytes"] == raw_bytes),
        "reduced_sha256": reduced_sha,
        "reduced_bytes": reduced_bytes,
    }


def check_manifest(manifest_relpath: str) -> dict[str, Any]:
    manifest = json.loads((REPO / manifest_relpath).read_text())
    drift: list[str] = []
    checked = 0
    for relpath, recorded in sorted(manifest.get("files", {}).items()):
        path = REPO / relpath
        if not path.exists():
            drift.append(f"{relpath}: MISSING")
            continue
        digest, size = sha256_file(path)
        checked += 1
        if digest != recorded["sha256"] or size != recorded["bytes"]:
            drift.append(f"{relpath}: content drift")
    return {
        "manifest": manifest_relpath,
        "files_checked": checked,
        "drift": drift,
        "ok": not drift,
    }


def rerun_reducer_byte_comparison() -> dict[str, Any]:
    """Re-execute the frozen reducer; byte-compare with the retained file."""
    raw_arg = f"../{SIGNED_BRACKET_DIR}/{RAW_NAME}"
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "re-reduced.json"
        completed = subprocess.run(
            [sys.executable, "reduce_stage7b_signed_bracket.py",
             raw_arg, "--out", str(out_path)],
            cwd=str(REPO / "src"), capture_output=True, text=True,
            check=False)
        if completed.returncode != 0:
            return {"ok": False,
                    "error": f"reducer exited {completed.returncode}",
                    "stderr_tail": completed.stderr[-500:]}
        rerun_bytes = out_path.read_bytes()
    retained_path = REPO / SIGNED_BRACKET_DIR / REDUCED_NAME
    retained_bytes = retained_path.read_bytes()
    summary_line = completed.stdout.strip()
    return {
        "ok": rerun_bytes == retained_bytes,
        "byte_identical": rerun_bytes == retained_bytes,
        "rerun_bytes": len(rerun_bytes),
        "retained_bytes": len(retained_bytes),
        "first_divergence_offset": next(
            (index for index, (left, right) in
             enumerate(zip(rerun_bytes, retained_bytes))
             if left != right), None)
        if rerun_bytes != retained_bytes else None,
        "reducer_stdout_summary": summary_line,
    }


def dispersion_scope(replicates: list[dict[str, Any]]) -> dict[str, Any]:
    """Descriptive dispersions of the paired differences (design input)."""
    mids = {"102": [], "204": []}
    deltas: list[Fraction] = []
    for replicate in replicates:
        if replicate.get("classification") != "COMPLETE":
            continue
        certificates = replicate["solver_certificates"]
        mid_102 = bracket_midpoint(certificates["102"])
        mid_204 = bracket_midpoint(certificates["204"])
        if mid_102 is not None:
            mids["102"].append(mid_102)
        if mid_204 is not None:
            mids["204"].append(mid_204)
        if mid_102 is not None and mid_204 is not None:
            deltas.append(mid_204 - mid_102)

    def spread(values: list[Fraction]) -> dict[str, Any]:
        if not values:
            return {}
        median = median_lower_middle(values)
        assert median is not None  # values non-empty
        ordered = sorted(values)
        n = len(ordered)
        return {
            "n": n,
            "min": fmt_rat(ordered[0]),
            "q1_lower_middle": fmt_rat(quantile_lower_middle(ordered, 1, 4)),
            "median_lower_middle": fmt_rat(median),
            "q3_upper_middle": fmt_rat(ordered[(3 * n) // 4]),
            "max": fmt_rat(ordered[-1]),
        }

    absolute = sorted(abs(delta) for delta in deltas)
    floor = Fraction(1, 100)
    resolution = Fraction(1, 512)  # bracket-midpoint granularity at rho=1/256
    median_absolute = median_lower_middle(absolute)
    assert median_absolute is not None  # deltas non-empty on COMPLETE runs
    return {
        "note": ("descriptive design input only; the closed registration "
                 "is not retuned and no threshold is recommended"),
        "per_genotype_bracket_midpoints": {
            genotype: spread(values) for genotype, values in mids.items()},
        "paired_differences": spread(deltas),
        "absolute_differences": {
            **spread(absolute),
            "share_at_or_above_floor_1_100": fmt_rat(
                Fraction(sum(1 for value in absolute if value >= floor),
                         len(absolute))),
        },
        "floor_in_midpoint_units": fmt_rat(floor / resolution),
        "observed_median_absolute_difference_in_floor_units": fmt_rat(
            median_absolute / floor),
    }


def build_report() -> dict[str, Any]:
    raw_path = REPO / SIGNED_BRACKET_DIR / RAW_NAME
    raw = json.loads(raw_path.read_text())
    outcome = independent_outcome(raw["replicates"])
    report = {
        "evidence_class": (
            "post-retention read-only audit of already-classified "
            "artifacts; no new contrast, fitness, or selection claim"),
        "artifact_hashes": check_artifact_hashes(),
        "independent_outcome_recomputation": outcome,
        "reducer_rerun": rerun_reducer_byte_comparison(),
        "manifest_drift_checks": [
            check_manifest(relpath)
            for relpath in PRE_EXECUTION_MANIFESTS.values()],
        "dispersion_scope": dispersion_scope(raw["replicates"]),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=str, default=None,
                        help="optional path OUTSIDE the repo for the JSON "
                             "report (default: stdout)")
    args = parser.parse_args(argv)
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(rendered, encoding="utf-8")
    print(json.dumps({
        "artifact_hashes_match": (
            report["artifact_hashes"]["matches_execution_note"]
            and report["artifact_hashes"]["matches_reduced_embedded_record"]),
        "independent_outcome_matches_retained_class": True,
        "reducer_rerun_byte_identical":
            report["reducer_rerun"]["ok"],
        "all_manifests_ok": all(check["ok"]
                                for check
                                in report["manifest_drift_checks"]),
        "complete_pairs":
            report["independent_outcome_recomputation"]["complete_pairs"],
        "median_paired_difference":
            report["independent_outcome_recomputation"][
                "median_paired_difference"],
        "sign_split":
            report["independent_outcome_recomputation"]["sign_split"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
