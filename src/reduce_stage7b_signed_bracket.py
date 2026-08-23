"""Stage 7B signed-bracket reducer: independent recomputation and the single
application of the completed section-3-table decision rule of
``docs/stage-7b-signed-bracket-preregistration.md`` (which completes,
rather than replaces, the carried section 5 rule of
``docs/stage-7b2-preregistration.md``, itself carried through every prior
Stage 7B generation).

Reads the retained raw artifact produced by
``run_stage7b_signed_bracket.py``, rebuilds the exact cohort schedules
from the retained vital records using the unchanged two-factor endpoint
(``stage7b_exposure_measure.exposure_schedule``), re-runs the FULL-LINE
certified solver, verifies bit-exact agreement with the runner's exported
values (``l_actuarial_x``, ``m_exposure_x``, mediator
``establishment_m_x``, solver certificates), and then -- exactly once --
applies ``apply_full_line_decision_rule``. Any mismatch between
recomputation and export classifies the reduction ``REDUCTION_MISMATCH``
under the architecture Section 9 repair policy; no outcome is ever
retroactively reclassified. The establishment signal is a reported
mediator here as everywhere: it is verified for export fidelity and never
substituted for the endpoint.
"""

from __future__ import annotations

from fractions import Fraction
import argparse
import hashlib
import importlib
import json
import sys
from typing import Any

from stage7b2_measure import fmt_rat, parse_rat
from stage7b_signed_bracket_config import (
    PREREG_DOCUMENT,
    PROTOCOL,
    decision_rule_inputs,
)
from stage7b_exposure_measure import exposure_schedule, lotka_coefficients
from stage7b_signed_bracket_solver import (
    FINITE_ROOT_STATUSES,
    MIN_COMPLETE_PAIRS,
    MIN_CONTRAST_DELTA_R,
    SOLVER_RESOLUTION_RHO,
    apply_full_line_decision_rule,
    full_line_certified_bracket,
)

REDUCER_SOURCES = (
    "stage7b2_measure.py",
    "stage7b2_solver.py",
    "stage7b2r_population.py",
    "stage7b_endpoint_measure.py",
    "stage7b_exposure_measure.py",
    "stage7b_exposure_config.py",
    "stage7b_signed_bracket_solver.py",
    "stage7b_signed_bracket_config.py",
    "reduce_stage7b_signed_bracket.py",
)


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for filename in REDUCER_SOURCES:
        if filename == "reduce_stage7b_signed_bracket.py":
            path = __file__
        else:
            module = importlib.import_module(filename[:-3])
            path = module.__file__
            assert path is not None
        with open(path, "rb") as handle:
            hashes[filename] = hashlib.sha256(handle.read()).hexdigest()
    return hashes


def reduce_artifact(raw: dict[str, Any]) -> dict[str, Any]:
    """Recompute everything from retained tables and apply the rule once."""
    mismatches: list[str] = []
    outcomes: list[dict[int, dict[str, Any]]] = []
    per_replicate: list[dict[str, Any]] = []
    for replicate in raw["replicates"]:
        index = replicate["replicate_index"]
        if replicate.get("classification") != "COMPLETE":
            per_replicate.append({
                "replicate_index": index,
                "classification": replicate.get("classification"),
                "outcome": {},
            })
            continue
        vitals = {
            "window_ticks": raw["registered_configuration"]["window_ticks_W"],
            "members": replicate["vital_records"]["members"],
            "births": replicate["vital_records"]["births"],
            "establishments": replicate["vital_records"]["establishments"],
            "first_reproduction": {},
            "first_extraction": {},
            "first_divide_attempt": {},
            "attempt_counters": replicate["vital_records"]["attempt_counters"],
        }

        outcome: dict[int, dict[str, Any]] = {}
        detail: dict[str, Any] = {"replicate_index": index}
        for genotype_key, schedule_raw in sorted(
                replicate["cohort_schedules"].items()):
            genotype_a = int(genotype_key)
            schedule = exposure_schedule(vitals, genotype_a)
            # Bit-exact verification against the runner's export.
            for x, value in enumerate(schedule["l_actuarial_x"]):
                if parse_rat(schedule_raw["l_actuarial_x"][x]) != value:
                    mismatches.append(
                        f"replicate {index} genotype {genotype_a} "
                        f"l_actuarial_x[{x}]")
            for x, value in enumerate(schedule["m_exposure_x"]):
                if parse_rat(schedule_raw["m_exposure_x"][x]) != value:
                    mismatches.append(
                        f"replicate {index} genotype {genotype_a} "
                        f"m_exposure_x[{x}]")
            for x, value in enumerate(schedule["establishment_m_x"]):
                if parse_rat(schedule_raw["establishment_m_x"][x]) != value:
                    mismatches.append(
                        f"replicate {index} genotype {genotype_a} "
                        f"establishment_m_x[{x}]")
            if schedule_raw["births_credited"] != schedule["births_credited"]:
                mismatches.append(
                    f"replicate {index} genotype {genotype_a} "
                    "births_credited")
            c_x = lotka_coefficients(schedule)
            certificate = full_line_certified_bracket(c_x, SOLVER_RESOLUTION_RHO)
            exported = replicate["solver_certificates"][genotype_key]
            if certificate["status"] != exported["status"]:
                mismatches.append(
                    f"replicate {index} genotype {genotype_a} status")
            if parse_rat(exported["L0_exact"]) != certificate["L0_exact"]:
                mismatches.append(
                    f"replicate {index} genotype {genotype_a} L0")
            if certificate["status"] in FINITE_ROOT_STATUSES:
                if (parse_rat(exported["r_lo"]) != certificate["r_lo"]
                        or parse_rat(exported["r_hi"]) != certificate["r_hi"]):
                    mismatches.append(
                        f"replicate {index} genotype {genotype_a} bracket")
            outcome[genotype_a] = certificate
            detail[genotype_key] = {
                "status": certificate["status"],
                "L0": str(certificate["L0_exact"]),
            }
        outcomes.append(outcome)
        per_replicate.append({
            "replicate_index": index,
            "classification": "COMPLETE",
            "outcome": detail,
        })

    if mismatches:
        return {
            "protocol": PROTOCOL,
            "reduction": "REDUCTION_MISMATCH",
            "mismatches": mismatches[:100],
            "repair_policy": "architecture section 9: retain, classify, "
                             "repair by superseding preregistration; never "
                             "reinterpret",
            "decision_applied": False,
        }

    invalid_replicates = [
        r["replicate_index"] for r in raw["replicates"]
        if r.get("classification") != "COMPLETE"]
    decision = apply_full_line_decision_rule(outcomes, MIN_CONTRAST_DELTA_R,
                                             MIN_COMPLETE_PAIRS)
    reduced: dict[str, Any] = {
        "protocol": PROTOCOL,
        "prereg_document": PREREG_DOCUMENT,
        "evidence_class": "single application of the completed "
                          "section-3-table decision rule over "
                          "independently recomputed estimators at the "
                          "carried ecology under the unchanged two-factor "
                          "endpoint, certified on the full real line",
        "verification": {
            "recomputation_bit_exact": True,
            "mismatch_count": 0,
            "invalid_implementations": invalid_replicates,
            "raw_source_sha256_note": "hash of the consumed raw artifact is "
                                      "recorded by the caller below",
        },
        "decision_rule_input": decision_rule_inputs(),
        "per_replicate": per_replicate,
        "outcome": decision,
        "interpretation_limits": (
            "Any ESTABLISHED_CONTRAST establishes only an allocation-"
            "associated invasion-growth difference at or above the "
            "registered floor under the carried registered ecology; it "
            "does not establish an optimum, an ESS, a background-"
            "invariant causal effect, or the architecture section 9.5 "
            "external-validation mechanism. The sign split over complete "
            "pairs and any exclusion/priority-effect pattern are "
            "descriptive context, never a fitness or selection claim. The "
            "establishment/first-reproduction signal is a reported "
            "mediator and is never substituted for the endpoint."),
    }
    return reduced


def _jsonable(value: Any) -> Any:
    """Recursively map Fractions to canonical ``num/den`` strings."""
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=str,
                        help="retained raw artifact from "
                             "run_stage7b_signed_bracket.py")
    parser.add_argument("--out", type=str, default=None,
                        help="path for the reduced classification artifact")
    args = parser.parse_args(argv)

    with open(args.raw, "rb") as handle:
        payload = handle.read()
    raw_sha256 = hashlib.sha256(payload).hexdigest()
    raw = json.loads(payload)
    if raw.get("protocol") != PROTOCOL:
        raise SystemExit(
            "refusing to reduce: artifact protocol is not "
            f"{PROTOCOL} (got {raw.get('protocol')!r})")
    reduced = reduce_artifact(raw)
    reduced["consumed_raw_artifact"] = {
        "path": args.raw,
        "sha256": raw_sha256,
        "bytes": len(payload),
    }
    reduced["reducer_source_manifest_sha256"] = _source_hashes()
    output = json.dumps(_jsonable(reduced), indent=2, sort_keys=True) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(output)
        print(f"wrote {args.out}", file=sys.stderr)
    summary = {"reduction": reduced.get("reduction", "CLASSIFIED")}
    if "outcome" in reduced:
        outcome = reduced["outcome"]
        summary.update({
            "pair_contrast_class": outcome["pair_contrast_class"],
            "subcritical_report": outcome["subcritical_report"],
            "complete_pairs": outcome["complete_pairs"],
        })
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
