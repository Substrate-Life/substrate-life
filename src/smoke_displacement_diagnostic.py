"""Non-inferential smoke exercise for displacement-outcome telemetry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from derive_stochastic_efficiency import (
    aggregate,
    disable_mutation,
    monomorphic_trial,
)

ROOT = Path("/opt/data/avida-life")
OUT = ROOT / "doomed-displacement-diagnostic-smoke.json"
SEEDS = (730001, 730002)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    disable_mutation()
    rows = [
        monomorphic_trial(
            "FULL", seed=seed, cycles=1, burn_cycles=0,
            maturation_delay=0)
        for seed in SEEDS
    ]
    summary = aggregate(rows, "monomorphic_cap", "FULL")
    fields = [
        "live_displacements",
        "vacancy_fills",
        "parent_victim_displacements",
        "doomed_offspring_live_displacements",
        "doomed_offspring_fraction_of_live_displacements",
        "unresolved_causing_offspring_live_displacements",
    ]
    sources = [
        ROOT / "src" / "smoke_displacement_diagnostic.py",
        ROOT / "src" / "derive_stochastic_efficiency.py",
        ROOT / "src" / "engine.py",
        ROOT / "src" / "organism.py",
        ROOT / "src" / "consts.py",
    ]
    result = {
        "classification": "telemetry_smoke_not_tau_assay",
        "scientific_inference_authorized": False,
        "lineage": "FULL",
        "seeds": list(SEEDS),
        "cycles_per_seed": 1,
        "endpoint_censoring_note": (
            "unresolved causing offspring prevent completed-cohort interpretation"
        ),
        "trials": [{key: row[key] for key in fields} for row in rows],
        "aggregate": {key: summary[key] for key in fields},
        "source_manifest": {
            str(path.relative_to(ROOT)): {
                "sha256": sha256(path),
                "mtime_ns": path.stat().st_mtime_ns,
                "size": path.stat().st_size,
            }
            for path in sources
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps({
        "output": str(OUT),
        "sha256": sha256(OUT),
        "aggregate": result["aggregate"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
