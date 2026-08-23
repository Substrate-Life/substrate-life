"""Stage 7B signed-bracket configuration: carried ecology and endpoint.

Thin configuration layer required by the SUPERSEDING preregistration
``docs/stage-7b-signed-bracket-preregistration.md``.  It registers the
protocol label and retained-output paths only; the ecology, the two-factor
endpoint coefficient assembly, and the decision-rule constants are carried
**verbatim** by re-export from the unchanged ``stage7b_exposure_config.py``
/ ``stage7b2r_population.py`` (never edited in place).  No mechanics,
estimator, or solver code lives here -- only the solver DOMAIN changes,
implemented additively in ``stage7b_signed_bracket_solver.py``.

Carried verbatim (denominator-repair prereg section 3, itself carried
through this document's section 3 table): census capacity ``N = 48``,
packet energy ``E = 900``, window ``W = 1200``, seed base ``20261822``,
genotypes ``(102,128,255)`` / ``(204,128,255)``, founders 3 per genotype,
founder ``S = 100`` / ``R = 0``, hazard arm ``h = 1/120``, corpse TTL 2,
buffer depth 64, shared memory pool 65,536 B, replicates ``k = 32``,
minimum complete pairs 16, solver resolution ``rho_r = 1/256``, minimum
contrast ``delta_r_min = 1/100``, mutation disabled, and the two-factor
coefficients ``c_x = l^A_x * m^E_x``.  The pre-freeze feasibility-gate
shakedown table is the same fixed 24 seeds ``20270000 + j`` reused a
fourth time (section 5.2 of this document) -- the underlying ledgers,
coefficient vectors, and ``L(0)`` values are bit-identical across all four
generations because population runs are deterministic in the hazard seed;
only the solver DOMAIN is new.

No fitness, selection, invasion-growth, or evolutionary claim is made
here; this module configures and labels, it does not interpret.
"""

from __future__ import annotations

from typing import Any

from stage7b2_solver import MIN_CONTRAST_DELTA_R, SOLVER_RESOLUTION_RHO
from stage7b2r_population import (
    MIN_COMPLETE_PAIRS,
    REGISTERED_BUFFER_DEPTH,
    REGISTERED_CENSUS_CAPACITY,
    REGISTERED_CORPSE_TTL,
    REGISTERED_FOUNDER_S,
    REGISTERED_GENOTYPES,
    REGISTERED_HAZARD_RATE,
    REGISTERED_MEMORY_POOL,
    REGISTERED_PACKET_ENERGY,
    REGISTERED_REPLICATE_SEED_BASE,
    REGISTERED_REPLICATES,
    REGISTERED_WINDOW_TICKS,
    SHAKEDOWN_SEED_BASE,
    SHAKEDOWN_SEED_COUNT,
    registered_founder_genomes,
    registered_population,
    registered_seed,
    shakedown_seed,
    shakedown_seeds,
)
from stage7b1_mechanics import REGISTERED_PACKET_RATE
from stage7b_exposure_config import endpoint_configuration as _exposure_configuration

PROTOCOL = "stage-7b-signed-bracket-preregistration"
"""Protocol label embedded in every artifact; the reducer refuses any other."""

PREREG_DOCUMENT = "docs/stage-7b-signed-bracket-preregistration.md"

RESULTS_DIR = "results/stage7b-signed-bracket/"
"""Retained-output directory (signed-bracket prereg section 3, output-path
row); a fresh path with no collision with, or implication about, any
earlier retained path."""

RAW_RESULT_PATH = RESULTS_DIR + "stage7b-signed-bracket-result.json"
REDUCED_RESULT_PATH = RESULTS_DIR + "stage7b-signed-bracket-reduced.json"
PRE_EXECUTION_MANIFEST_PATH = RESULTS_DIR + "pre-execution-manifest.json"

# Regression-identity reference: the archived generation-3 (denominator-
# repair) shakedown gate summary.  Read-only evidence, never modified;
# used solely to certify that reusing the same fixed 24-seed table through
# the new solver domain reproduces the same L(0) values bit-exactly
# (signed-bracket prereg section 5.2).
GENERATION_3_GATE_SUMMARY_PATH = (
    "failed-designs/2026-08-23-stage7b-denominator-feasibility-gate-no-go/"
    "gate-summary.json")


def endpoint_configuration() -> dict[str, Any]:
    """Echo of the binding values embedded in every artifact.

    Carries the denominator-repair endpoint configuration verbatim and
    overlays only the protocol label, prereg document, and the registered
    solver-domain extension.
    """
    carried = dict(_exposure_configuration())
    carried.update({
        "protocol": PROTOCOL,
        "prereg_document": PREREG_DOCUMENT,
        "solver_domain": (
            "full real line: L(0) > 1 -> SUPERCRITICAL (bracket >= 0); "
            "L(0) == 1 exact -> CRITICAL (bracket [0,0]); L(0) < 1 with "
            "S_plus > 0 -> SUBCRITICAL (certified negative bracket); "
            "S_plus == 0, or c_0 >= 1 with S_plus > 0 -> NO_FINITE_ROOT"),
        "solver_domain_supersedes": (
            "the L(0) <= 1 => SUBCRITICAL/no-numeric-r_g rule of "
            "docs/stage-7b2-preregistration.md section 4 steps 1-2, as "
            "carried through every prior Stage 7B generation"),
        "shakedown_table": (
            f"{SHAKEDOWN_SEED_COUNT} fixed seeds {SHAKEDOWN_SEED_BASE} + j, "
            "j in 0..23, reused verbatim a fourth time across all gate "
            "generations (signed-bracket prereg section 5.2)"),
        "generation_3_regression_reference": GENERATION_3_GATE_SUMMARY_PATH,
    })
    return carried


def decision_rule_inputs() -> dict[str, Any]:
    """Carried section-3-table rule constants embedded in every artifact."""
    def fmt(value: Any) -> str:
        return f"{value.numerator}/{value.denominator}"

    return {
        "solver_resolution_rho_r": fmt(SOLVER_RESOLUTION_RHO),
        "minimum_contrast_delta_r_min": fmt(MIN_CONTRAST_DELTA_R),
        "minimum_complete_pairs": MIN_COMPLETE_PAIRS,
    }
