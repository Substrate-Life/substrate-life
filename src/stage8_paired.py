"""Stage 8 paired-arm configuration: mutation-on/off factories (repair).

Additive implementation layer of the SUPERSEDING repair registration
``docs/stage-8-alpha-evolution-repair-preregistration.md`` (§8(1)).  Per
pair ``i``:

- **Arm M** — the registered dedicated-locus kernel carried verbatim:
  ``registered_m_population(s_i)`` builds exactly what
  ``registered_stage8_population`` built (same founders, ecology, window,
  kernel stream derivation).
- **Arm R0** — the kernel absent: ``registered_r0_population(s_i)`` builds
  the byte-frozen ``Stage7B2Population`` at the identical configuration
  (founders, ecology, ``W = 2400``).  No ``mutation_rng``, no
  ``mutation_draws``, no Stage-M substitution ever exist on this path, so
  the arm contrast is exactly the kernel.

Both factories consume the same ``hazard_seed``; the hazard-stream
derivation is unchanged, so exogenous draws coincide wherever trajectories
coincide.  Fresh registered tables (disjoint from every prior population
table, including the retired-unexecuted ``{20284617+i}`` /
``{20293311+j}``): confirmatory/pairing ``20310529 + i`` (``k = 24``
pairs) and shakedown ``20421301 + j`` (``k = 12`` pairs).

No fitness, selection, direction, or evolutionary claim is made here;
this module constructs populations, it does not interpret them.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from stage7b1_mechanics import REGISTERED_PACKET_RATE
from stage7b2_population import Stage7B2Population
from stage7b2r_population import (
    REGISTERED_BUFFER_DEPTH,
    REGISTERED_CENSUS_CAPACITY,
    REGISTERED_CORPSE_TTL,
    REGISTERED_FOUNDER_S,
    REGISTERED_GENOTYPES,
    REGISTERED_HAZARD_RATE,
    REGISTERED_MEMORY_POOL,
    REGISTERED_PACKET_ENERGY,
)
from stage8_population import (
    FROZEN_D,
    FROZEN_T,
    REGISTERED_WINDOW_TICKS_STAGE8,
    stage8_founder_genomes,
)

PROTOCOL = "stage-8-alpha-evolution-repair-preregistration"
PREREG_DOCUMENT = "docs/stage-8-alpha-evolution-repair-preregistration.md"

PAIR_REPLICATES = 24
"""Registered confirmatory pair count ``k`` (repair registration §3)."""

CONFIRMATORY_PAIR_SEED_BASE = 20310529
"""Confirmatory table: ``20310529 + i``, i in 0..23; fresh and disjoint
from every prior table including the retired-unexecuted pair."""

SHAKEDOWN_PAIR_SEED_BASE = 20421301
SHAKEDOWN_PAIR_COUNT = 12
"""Shakedown table: ``20421301 + j``, j in 0..11; fixed before any run."""

DIRECTION_FLOOR_PAIRED = Fraction(4, 255)
"""``Δ_pair_floor``: equals the max kernel step magnitude (no single
event can manufacture a classified pair) and sits at >= 2 sigma of the
null mutational-cloud mean deviation (repair registration §3, §6)."""

RETIRED_TABLES = (
    ("stage-7b2", 20260822, 32),
    ("stage-7b2r", 20261822, 32),
    ("stage-7b2r-shakedown", 20270000, 24),
    ("stage-8-cancelled-confirmatory", 20284617, 24),
    ("stage-8-cancelled-shakedown", 20293311, 12),
)
"""Every prior population table, retained here as a disjointness witness;
the last two are retired UNEXECUTED and must never be reused."""


def confirmatory_pair_seed(index: int) -> int:
    if not 0 <= index < PAIR_REPLICATES:
        raise ValueError(
            f"pair index must be in [0,{PAIR_REPLICATES})")
    return CONFIRMATORY_PAIR_SEED_BASE + index


def shakedown_pair_seed(index: int) -> int:
    if not 0 <= index < SHAKEDOWN_PAIR_COUNT:
        raise ValueError(
            f"shakedown pair index must be in [0,{SHAKEDOWN_PAIR_COUNT})")
    return SHAKEDOWN_PAIR_SEED_BASE + index


def shakedown_pair_seeds() -> tuple[int, ...]:
    return tuple(shakedown_pair_seed(i) for i in range(SHAKEDOWN_PAIR_COUNT))


def _configuration_founders() -> list[tuple[int, int, int]]:
    """Carried founder blocks: 3 x (102,128,255) + 3 x (204,128,255)."""
    return stage8_founder_genomes()


def registered_m_population(hazard_seed: int,
                            window_ticks: int | None = None):
    """Arm M: the registered kernel path, configuration carried verbatim.

    ``window_ticks`` exists solely for implementation-window plumbing
    checks; every registered execution uses the fixed ``W = 2400``.
    """
    from stage8_population import registered_stage8_population

    return registered_stage8_population(
        hazard_seed,
        window_ticks=(REGISTERED_WINDOW_TICKS_STAGE8
                      if window_ticks is None else window_ticks))


def registered_r0_population(hazard_seed: int,
                             window_ticks: int | None = None) \
        -> Stage7B2Population:
    """Arm R0: the byte-frozen stack at the identical configuration.

    Constructs the frozen ``Stage7B2Population`` -- no kernel, no mutation
    site -- with the same founders, ecology, and window as Arm M.  Any
    attempt to pass non-frozen loci fails in the same way it always did.
    ``window_ticks`` exists solely for plumbing checks; registered
    executions use the fixed ``W = 2400``.
    """
    return Stage7B2Population(
        founder_genomes=_configuration_founders(),
        capacity=REGISTERED_CENSUS_CAPACITY,
        founder_s=REGISTERED_FOUNDER_S,
        memory_pool=REGISTERED_MEMORY_POOL,
        hazard_seed=hazard_seed,
        hazard_rate=REGISTERED_HAZARD_RATE,
        corpse_ttl=REGISTERED_CORPSE_TTL,
        packet_rate=REGISTERED_PACKET_RATE,
        buffer_depth=REGISTERED_BUFFER_DEPTH,
        packet_energy=REGISTERED_PACKET_ENERGY,
        window_ticks=(REGISTERED_WINDOW_TICKS_STAGE8
                      if window_ticks is None else window_ticks),
    )


def assert_kernel_absent(population: Stage7B2Population) -> None:
    """Structural G4 witness: the R0 path carries no kernel machinery."""
    if hasattr(population, "mutation_rng") or \
            hasattr(population, "mutation_draws"):
        raise AssertionError(
            "Arm R0 population carries kernel machinery; "
            "the arm contrast would not be exactly the kernel")


def registered_configuration() -> dict[str, Any]:
    """Echo of the binding values embedded in every paired artifact."""

    def fmt(value: Fraction) -> str:
        return f"{value.numerator}/{value.denominator}"

    return {
        "protocol": PROTOCOL,
        "prereg_document": PREREG_DOCUMENT,
        "arms": {
            "M": "dedicated-locus kernel p_mu=1/2, delta in "
                 "{±1..±4} clamped, T=128/D=255 frozen",
            "R0": "byte-frozen Stage7B2Population; kernel absent",
        },
        "pairing": "both arms of a pair run the identical hazard_seed; "
                   "hazard-stream derivation unchanged",
        "window_ticks_W": REGISTERED_WINDOW_TICKS_STAGE8,
        "expected_lifespans_per_window": 20,
        "census_capacity_N": REGISTERED_CENSUS_CAPACITY,
        "buffer_depth_d": REGISTERED_BUFFER_DEPTH,
        "packet_rate_r": REGISTERED_PACKET_RATE,
        "packet_energy_E": fmt(REGISTERED_PACKET_ENERGY),
        "hazard_rate_h": fmt(REGISTERED_HAZARD_RATE),
        "pairs_k": PAIR_REPLICATES,
        "runs_total": 2 * PAIR_REPLICATES,
        "confirmatory_seed_derivation":
            f"hazard_seed = {CONFIRMATORY_PAIR_SEED_BASE} + i, i in 0..23",
        "shakedown_seed_derivation":
            f"hazard_seed = {SHAKEDOWN_PAIR_SEED_BASE} + j, j in 0..11",
        "genotypes_ATD": [list(g) for g in REGISTERED_GENOTYPES],
        "founders_per_genotype": 3,
        "founder_S": fmt(REGISTERED_FOUNDER_S),
        "frozen_loci": {"T": FROZEN_T, "D": FROZEN_D},
        "direction_floor_paired": fmt(DIRECTION_FLOOR_PAIRED),
        "decision_thresholds": {"minimum_eligible_k_eff": 16,
                                "concordance": 18},
        "retired_tables_never_reused": [
            {"lineage": lineage, "base": base, "count": count}
            for lineage, base, count in RETIRED_TABLES],
    }
