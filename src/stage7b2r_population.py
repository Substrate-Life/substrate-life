"""Stage 7B2-R population: the superseding ecology on the frozen stack.

Thin configuration layer required by the SUPERSEDING preregistration
``docs/stage-7b2-repair-preregistration.md`` (committed ``46c8ccb``).  It
registers the repaired Section 3 ecology constants and builds populations
through the *unchanged* ``Stage7B2Population`` machinery of the retained
Stage 7B2 freeze (manifest ``results/stage7b2/pre-execution-manifest.json``);
no mechanics, estimator, or solver code is modified here.  Per Section 7.2,
the frozen transaction mechanics are reused behind this configuration layer;
any hash drift in shared sources must be justified against that document.

Repaired values (Section 3): census capacity ``N`` 48 (was 12), packet
energy ``E`` 900 (was 300), window ``W`` 1200 (was 600), seed base 20261822
(was 20260822).  Carried verbatim: genotypes ``(102,128,255)`` /
``(204,128,255)``, founders 3 per genotype age 0 with ``S = 100``, ``R =
0``, single hazard arm ``h = 1/120``, corpse TTL 2, buffer depth 64, shared
memory pool 65,536 B, replicates ``k = 32``, minimum complete pairs 16,
solver resolution ``rho_r = 1/256``, minimum contrast ``delta_r_min =
1/100``.  Mutation stays disabled (structural zero-draw M stage).

Section 6 also fixes, before any execution, the exploratory shakedown seed
table used by the binding pre-freeze feasibility gate: 24 distinct hazard
seeds ``20270000 + j``, ``j`` in ``0..23``, disjoint from the registered
confirmatory table ``{20261822, ..., 20261853}`` (and from the retired
Stage 7B2 table), so no outcome-based seed selection is possible.

No fitness, selection, invasion-growth, or evolutionary claim is made here;
this module configures and runs populations, it does not interpret them.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from stage7b1_mechanics import REGISTERED_PACKET_RATE
from stage7b2_population import Stage7B2Population, run_window

# ---------------------------------------------------------------------------
# Registered configuration (repair preregistration section 3) -- binding values
# ---------------------------------------------------------------------------

REGISTERED_WINDOW_TICKS = 1200
"""Window ``W``: right-censoring boundary for every replicate."""

REGISTERED_CENSUS_CAPACITY = 48
"""Census capacity ``N``, identical across replicates and genotypes."""

REGISTERED_BUFFER_DEPTH = 64
"""Buffer depth ``d``: unchanged engineering bound; layers 1-2 of 7B1
section 4.1 remain armed and any trigger classifies the run
``INVALID_IMPLEMENTATION`` (section 3, row 4)."""

REGISTERED_HAZARD_RATE = Fraction(1, 120)
"""Single hazard arm: age-independent, phenotype-blind per live member."""

REGISTERED_REPLICATE_SEED_BASE = 20261822
"""Seed derivation: ``hazard_seed = 20261822 + i`` for replicate ``i``
(section 3, seed-table row; disjoint from every earlier table)."""

REGISTERED_REPLICATES = 32
"""Replicate count ``k``; carried unchanged."""

MIN_COMPLETE_PAIRS = 16
"""Carried evidential floor for the section 5 rule (applied once by the
source-frozen reducer)."""

REGISTERED_FOUNDERS_PER_GENOTYPE = 3
REGISTERED_GENOTYPES: tuple[tuple[int, int, int], ...] = (
    (102, 128, 255),
    (204, 128, 255),
)
"""Carried verbatim (repair preregistration section 3, carry-forward list)."""

REGISTERED_FOUNDER_S = Fraction(100)
"""Opening somatic reserve of every founder (carried)."""

REGISTERED_CORPSE_TTL = 2
"""Carried frozen constant."""

REGISTERED_PACKET_ENERGY = Fraction(900)
"""Packet energy ``E`` of the repaired programme family (section 3)."""

REGISTERED_MEMORY_POOL = 65536
"""Shared memory pool, unchanged (section 3): obligation bound
``N*(working+gestation) + corpse_ttl*128 <= 48*256 B << 65,536 B``."""

SHAKEDOWN_SEED_BASE = 20270000
"""Section 6 feasibility-gate seed derivation, fixed before any run."""

SHAKEDOWN_SEED_COUNT = 24
"""Minimum distinct shakedown seeds demanded by section 6.1."""


def registered_seed(index: int) -> int:
    """Registered confirmatory seed derivation for replicate ``index``."""
    if not 0 <= index < REGISTERED_REPLICATES:
        raise ValueError(
            f"replicate index must be in [0,{REGISTERED_REPLICATES})")
    return REGISTERED_REPLICATE_SEED_BASE + index


def shakedown_seed(index: int) -> int:
    """Section 6 exploratory seed derivation; disjoint from the confirmatory
    table by construction (fixed before any execution at this ecology)."""
    if not 0 <= index < SHAKEDOWN_SEED_COUNT:
        raise ValueError(
            f"shakedown index must be in [0,{SHAKEDOWN_SEED_COUNT})")
    return SHAKEDOWN_SEED_BASE + index


def shakedown_seeds() -> tuple[int, ...]:
    """The fixed shakedown seed table (section 6.1)."""
    return tuple(shakedown_seed(index) for index in range(SHAKEDOWN_SEED_COUNT))


def registered_founder_genomes() -> list[tuple[int, int, int]]:
    """Founder genome blocks: 3 per genotype, contiguous organisation IDs."""
    genomes: list[tuple[int, int, int]] = []
    for genotype in REGISTERED_GENOTYPES:
        genomes.extend([genotype] * REGISTERED_FOUNDERS_PER_GENOTYPE)
    return genomes


def registered_population(hazard_seed: int) -> Stage7B2Population:
    """The registered section 3 confirmatory configuration, verbatim.

    Built through the unchanged Stage 7B2 population class; every binding
    value is passed explicitly (nothing inherits a superseded default).
    """
    return Stage7B2Population(
        founder_genomes=registered_founder_genomes(),
        capacity=REGISTERED_CENSUS_CAPACITY,
        founder_s=REGISTERED_FOUNDER_S,
        memory_pool=REGISTERED_MEMORY_POOL,
        hazard_seed=hazard_seed,
        hazard_rate=REGISTERED_HAZARD_RATE,
        corpse_ttl=REGISTERED_CORPSE_TTL,
        packet_rate=REGISTERED_PACKET_RATE,
        buffer_depth=REGISTERED_BUFFER_DEPTH,
        packet_energy=REGISTERED_PACKET_ENERGY,
        window_ticks=REGISTERED_WINDOW_TICKS,
    )


def registered_configuration() -> dict[str, Any]:
    """Echo of the binding section 3 values embedded in every artifact."""
    return {
        "protocol": "stage-7b2r-preregistration",
        "window_ticks_W": REGISTERED_WINDOW_TICKS,
        "census_capacity_N": REGISTERED_CENSUS_CAPACITY,
        "buffer_depth_d": REGISTERED_BUFFER_DEPTH,
        "packet_rate_r": REGISTERED_PACKET_RATE,
        "hazard_arms": ["1/120 per live member per tick"],
        "replicates_k": REGISTERED_REPLICATES,
        "seed_derivation": "hazard_seed = 20261822 + i, i in 0..31",
        "genotypes_ATD": [list(g) for g in REGISTERED_GENOTYPES],
        "founders_per_genotype": REGISTERED_FOUNDERS_PER_GENOTYPE,
        "founder_S": f"{REGISTERED_FOUNDER_S.numerator}/"
                     f"{REGISTERED_FOUNDER_S.denominator}",
        "founder_R": "0/1",
        "corpse_ttl": REGISTERED_CORPSE_TTL,
        "packet_energy": f"{REGISTERED_PACKET_ENERGY.numerator}/"
                         f"{REGISTERED_PACKET_ENERGY.denominator}",
        "memory_pool_bytes": REGISTERED_MEMORY_POOL,
        "mutation": "disabled; structural zero-draw M stage",
        "supersedes": "ecology parameters of docs/stage-7b2-preregistration.md"
                      " per docs/stage-7b2-repair-preregistration.md section 3",
    }
