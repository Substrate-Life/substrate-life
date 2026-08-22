"""Stage 7B1 deterministic runner: executes the registered §§2-5/§6.2 test
matrix frozen in ``test_stage7b1_mechanics.py`` and produces one lossless
JSON artifact under ``results/stage7b1/`` per preregistration §9.3.  This is
the single authorised execution class: a deterministic, mutation-disabled
mechanics verification.  It makes no fitness, selection, or evolutionary
claim and runs no stochastic assay.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
import unittest
from typing import Any

import test_stage7b1_mechanics as matrix

#: Every source file this run depends on; hashed into the artifact so the
#: retained output is bound to an exact, inspectable implementation state.
FROZEN_SOURCES = (
    "stage7b1_mechanics.py",
    "stage7_slice1.py",
    "stage7_slice2.py",
    "datastream.py",
    "transforms.py",
    "consts.py",
    "test_stage7b1_mechanics.py",
    "run_stage7b1.py",
)

#: Registered test classes -- one per preregistration blocker plus §6.2.
REGISTERED_TEST_CLASSES = (
    matrix.Stage7B1RollbackMatrixTests,      # Blocker A, §2 (7 boundaries)
    matrix.Stage7B1CommitSemanticsTests,     # Blocker A, §2 (commit/RNG/lock)
    matrix.Stage7B1RetirementTests,          # Blocker B, §3
    matrix.Stage7B1NoEvictionTests,          # Blocker C, §4
    matrix.Stage7B1HazardDeathTests,         # Blocker D, §5
    matrix.Stage7B1ShadowTelemetryTests,     # Blocker F, §6.2
)


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for filename in FROZEN_SOURCES:
        module_name = filename[:-3]
        if module_name == "run_stage7b1":
            path = __file__
        else:
            module = importlib.import_module(module_name)
            path = module.__file__
            assert path is not None
        with open(path, "rb") as handle:
            hashes[filename] = hashlib.sha256(handle.read()).hexdigest()
    return hashes


class _RecordingResult(unittest.TestResult):
    """Collects a JSON-serialisable outcome per registered test."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[dict[str, Any]] = []

    def addSuccess(self, test: Any) -> None:
        super().addSuccess(test)
        self.records.append({"test": str(test), "outcome": "PASS"})

    def addFailure(self, test: Any, err: Any) -> None:
        super().addFailure(test, err)
        self.records.append({
            "test": str(test), "outcome": "FAIL",
            "detail": self._exc_info_to_string(err, test),
        })

    def addError(self, test: Any, err: Any) -> None:
        super().addError(test, err)
        self.records.append({
            "test": str(test), "outcome": "ERROR",
            "detail": self._exc_info_to_string(err, test),
        })


def run_registered_matrix() -> dict[str, Any]:
    """Run every registered test method and report a structured outcome."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for test_class in REGISTERED_TEST_CLASSES:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    result = _RecordingResult()
    suite.run(result)
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "passed": result.wasSuccessful(),
        "records": result.records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=str, default=None,
        help="optional path for the lossless JSON artifact")
    args = parser.parse_args()

    matrix_result = run_registered_matrix()
    raw: dict[str, Any] = {
        "protocol": "stage-7b1-preregistration",
        "protocol_sha256_note": "hash of the protocol document is recorded "
                                "in the pre-execution manifest, not "
                                "recomputed here",
        "evidence_class": "deterministic, mutation-disabled mechanics "
                          "verification of preregistration sections 2-5 "
                          "and 6.2; no fitness endpoint",
        "selection_assay_run": False,
        "mutation_enabled": False,
        "source_manifest_sha256": _source_hashes(),
        "registered_test_classes": [
            test_class.__name__ for test_class in REGISTERED_TEST_CLASSES],
        "matrix_result": matrix_result,
    }
    raw["decision"] = "PASS" if matrix_result["passed"] else "FAIL"
    raw["decision_scope"] = (
        "Permits only the mechanism-verification conclusion of "
        "preregistration section 9.3 for the registered fault-injection, "
        "retirement, death/corpse, no-eviction, and shadow-telemetry tests; "
        "establishes nothing about generality, fitness, selection, "
        "invasion growth, reproductive value, mutation accessibility, "
        "plasticity, optimum, or ESS."
        if raw["decision"] == "PASS" else
        "One or more registered tests failed under this source manifest; "
        "raw output is retained and classified under the architecture "
        "section 9 repair policy."
    )

    payload = json.dumps(raw, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
        print(f"wrote {args.out}", file=sys.stderr)
    print(json.dumps({
        "decision": raw["decision"],
        "tests_run": matrix_result["tests_run"],
        "failures": matrix_result["failures"],
        "errors": matrix_result["errors"],
    }, indent=2))
    return 0 if raw["decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
