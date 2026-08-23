"""Stage 7B endpoint-repair configuration: the carried ecology, corrected
endpoint.

Thin configuration layer required by the SUPERSEDING preregistration
``docs/stage-7b-endpoint-repair-preregistration.md`` (committed ``17b6aed``).
It registers the protocol label, retained-output paths, and the endpoint
correction, and carries the binding section 3 ecology of
``docs/stage-7b2-repair-preregistration.md`` **verbatim** by re-export from
the unchanged ``stage7b2r_population.py`` (never edited in place; see the
endpoint-repair prereg sections 5.1 and 8).  No mechanics, estimator, or
solver code lives here.

Carried verbatim (repair prereg section 3): census capacity ``N = 48``,
packet energy ``E = 900``, window ``W = 1200``, seed base ``20261822``,
genotypes ``(102,128,255)`` / ``(204,128,255)``, founders 3 per genotype,
founder ``S = 100`` / ``R = 0``, hazard arm ``h = 1/120``, corpse TTL 2,
buffer depth 64, shared memory pool 65,536 B, replicates ``k = 32``,
minimum complete pairs 16, solver resolution ``rho_r = 1/256``, minimum
contrast ``delta_r_min = 1/100``, mutation disabled.  The pre-freeze
feasibility-gate shakedown table is likewise reused verbatim: the same
fixed 24 seeds ``20270000 + j`` already used and archived by the failed
gate (endpoint-repair prereg section 5.2 -- no new seed draw is needed or
permitted; reusing this table under the corrected estimator is the direct,
minimal test of whether the repair resolves the defect).

Corrected here: only the endpoint numerator -- raw age-specific fecundity
per endpoint-repair prereg section 3; the establishment signal stays a
reported mediator.  Mutation remains unauthorised in every form.

No fitness, selection, invasion-growth, or evolutionary claim is made
here; this module configures and labels, it does not interpret.
"""

from __future__ import annotations

from typing import Any

from stage7b1_mechanics import REGISTERED_PACKET_RATE
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

PROTOCOL = "stage-7b-endpoint-repair-preregistration"
"""Protocol label embedded in every artifact; the reducer refuses any other."""

PREREG_DOCUMENT = "docs/stage-7b-endpoint-repair-preregistration.md"

RESULTS_DIR = "results/stage7b-endpoint-repair/"
"""Retained-output directory (endpoint-repair prereg section 6.3); chosen
to avoid any collision with, or implication about, the retained
``stage7b2``/``stage7b2-repair`` paths."""

RAW_RESULT_PATH = RESULTS_DIR + "stage7b-endpoint-result.json"
REDUCED_RESULT_PATH = RESULTS_DIR + "stage7b-endpoint-reduced.json"
PRE_EXECUTION_MANIFEST_PATH = RESULTS_DIR + "pre-execution-manifest.json"


def endpoint_configuration() -> dict[str, Any]:
    """Echo of the binding values embedded in every artifact."""
    return {
        "protocol": PROTOCOL,
        "prereg_document": PREREG_DOCUMENT,
        "endpoint": (
            "raw age-specific fecundity m_x: every admitted birth credited "
            "exactly once to its immediate parent at the parent's age at "
            "the birth tick, divided by |C_g|"),
        "endpoint_supersedes": (
            "m_x definition of docs/stage-7b1-preregistration.md "
            "section 6.1 (establishment-filtered), per endpoint-repair "
            "prereg section 3"),
        "mediator_note": (
            "the establishment/first-reproduction quantity is reported as a "
            "mediator and is never substituted for the endpoint"),
        # Carried verbatim from stage7b2r_population (repair prereg s3):
        "window_ticks_W": REGISTERED_WINDOW_TICKS,
        "census_capacity_N": REGISTERED_CENSUS_CAPACITY,
        "buffer_depth_d": REGISTERED_BUFFER_DEPTH,
        "packet_rate_r": REGISTERED_PACKET_RATE,
        "hazard_arms": ["1/120 per live member per tick"],
        "replicates_k": REGISTERED_REPLICATES,
        "seed_derivation": f"hazard_seed = {REGISTERED_REPLICATE_SEED_BASE}"
                           " + i, i in 0..31",
        "genotypes_ATD": [list(g) for g in REGISTERED_GENOTYPES],
        "founders_per_genotype": 3,
        "founder_S": f"{REGISTERED_FOUNDER_S.numerator}/"
                     f"{REGISTERED_FOUNDER_S.denominator}",
        "founder_R": "0/1",
        "corpse_ttl": REGISTERED_CORPSE_TTL,
        "packet_energy": f"{REGISTERED_PACKET_ENERGY.numerator}/"
                         f"{REGISTERED_PACKET_ENERGY.denominator}",
        "memory_pool_bytes": REGISTERED_MEMORY_POOL,
        "mutation": "disabled; structural zero-draw M stage",
        "carried_from": (
            "docs/stage-7b2-repair-preregistration.md section 3 ecology, "
            "carried verbatim by endpoint-repair prereg header/section 3"),
        "shakedown_table": (
            f"{SHAKEDOWN_SEED_COUNT} fixed seeds {SHAKEDOWN_SEED_BASE} + j, "
            "j in 0..23, reused verbatim from the archived failed gate "
            "(endpoint-repair prereg section 5.2)"),
        "supersedes": (
            "m_x of docs/stage-7b1-preregistration.md section 6.1 as "
            "inherited by docs/stage-7b2-preregistration.md section 3 and "
            "docs/stage-7b2-repair-preregistration.md section 3"),
    }


def endpoint_decision_rule_inputs() -> dict[str, Any]:
    """Carried section 5 rule constants embedded in every artifact."""
    def fmt(value: Any) -> str:
        return f"{value.numerator}/{value.denominator}"

    return {
        "solver_resolution_rho_r": fmt(SOLVER_RESOLUTION_RHO),
        "minimum_contrast_delta_r_min": fmt(MIN_CONTRAST_DELTA_R),
        "minimum_complete_pairs": MIN_COMPLETE_PAIRS,
    }
