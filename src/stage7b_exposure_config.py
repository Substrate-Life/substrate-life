"""Stage 7B exposure-normalised configuration: carried ecology, new endpoint.

Thin configuration layer required by the SUPERSEDING preregistration
``docs/stage-7b-denominator-repair-preregistration.md``.  It registers the
protocol label, retained-output paths, and the normalisation repair, and
carries the binding section 3 ecology of
``docs/stage-7b2-repair-preregistration.md`` **verbatim** by re-export from
the unchanged ``stage7b2r_population.py`` (never edited in place).  No
mechanics, estimator, or solver code lives here.

Carried verbatim: census capacity ``N = 48``, packet energy ``E = 900``,
window ``W = 1200``, seed base ``20261822``, genotypes ``(102,128,255)`` /
``(204,128,255)``, founders 3 per genotype, founder ``S = 100`` / ``R = 0``,
hazard arm ``h = 1/120``, corpse TTL 2, buffer depth 64, shared memory pool
65,536 B, replicates ``k = 32``, minimum complete pairs 16, solver
resolution ``rho_r = 1/256``, minimum contrast ``delta_r_min = 1/100``,
mutation disabled.  The pre-freeze feasibility-gate shakedown table is the
same fixed 24 seeds ``20270000 + j`` used by both prior gate generations
(denominator-repair prereg section 5.2 -- no new seed draw is needed or
permitted; a third reuse on identical seeds isolates the repaired endpoint
layer).

Repaired here: only the endpoint COEFFICIENT ASSEMBLY -- the two Lotka
factors are re-grounded in independent denominator sets (risk-set
actuarial survivorship l^A times person-tick fecundity m^E = n_x/E_x),
replacing the collapsed product l_x * m_x whose factors shared one
cohort-size denominator set; the raw numerator, the reported descriptive
l_x, the mediator, solver contract, decision rule, and ecology are
untouched.  Mutation remains unauthorised in every form.

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

PROTOCOL = "stage-7b-denominator-repair-preregistration"
"""Protocol label embedded in every artifact; the reducer refuses any other."""

PREREG_DOCUMENT = "docs/stage-7b-denominator-repair-preregistration.md"

RESULTS_DIR = "results/stage7b-exposure-endpoint/"
"""Retained-output directory (denominator-repair prereg section 6.3); chosen
to avoid any collision with, or implication about, the retained
``stage7b2`` / ``stage7b2-repair`` paths and the never-frozen
``stage7b-endpoint-repair`` path."""

RAW_RESULT_PATH = RESULTS_DIR + "stage7b-exposure-result.json"
REDUCED_RESULT_PATH = RESULTS_DIR + "stage7b-exposure-reduced.json"
PRE_EXECUTION_MANIFEST_PATH = RESULTS_DIR + "pre-execution-manifest.json"


def endpoint_configuration() -> dict[str, Any]:
    """Echo of the binding values embedded in every artifact."""
    return {
        "protocol": PROTOCOL,
        "prereg_document": PREREG_DOCUMENT,
        "endpoint": (
            "two-factor Euler-Lotka coefficients c_x = l^A_x * m^E_x: "
            "risk-set window-actuarial survivorship l^A_{x+1} = "
            "l^A_x*(E_x-d_x)/E_x times per-capita person-tick fecundity "
            "m^E_x = n_x/E_x"),
        "endpoint_supersedes": (
            "the collapsed coefficient assembly c_x = l_x*m_x = n_x/|C_g| "
            "(shared cohort-size denominator set) of "
            "docs/stage-7b-endpoint-repair-preregistration.md section 3, "
            "per denominator-repair prereg sections 2-3"),
        "binding_identities": [
            "sum_x E_x(g) == exposure_member_ticks(g)",
            "sum_x n_x(g) == |C_g| - F_g",
            "n_x(g) <= E_x(g) for every x",
            "sum_x d_x(g) + censored_g == |C_g|",
            "l^A_0 == 1; l^A non-increasing; 0 <= l^A <= 1",
        ],
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
            "carried verbatim through the endpoint-repair and "
            "denominator-repair preregistrations"),
        "shakedown_table": (
            f"{SHAKEDOWN_SEED_COUNT} fixed seeds {SHAKEDOWN_SEED_BASE} + j, "
            "j in 0..23, reused verbatim across all three gate generations "
            "(denominator-repair prereg section 5.2)"),
        "supersedes": (
            "m_x normalisation of "
            "docs/stage-7b-endpoint-repair-preregistration.md section 3 as "
            "inherited from docs/stage-7b1-preregistration.md section 6.1"),
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
