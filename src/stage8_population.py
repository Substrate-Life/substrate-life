"""Stage 8 alpha-evolution population: dedicated-locus kernel at Stage M.

Additive implementation layer required by the SUPERSEDING preregistration
``docs/stage-8-alpha-evolution-preregistration.md`` (rung 2).  Per its
section 7(1), the frozen mechanics are reused byte-identically by import;
the frozen files are never edited.  The single behavioural change is the
registered substitution of Stage M inside one method:

- ``Stage8Population.divide_publish`` is a verbatim copy of the frozen
  ``Stage7B1Population.divide_publish`` body with ONLY the structural
  zero-draw M-stage replaced by the registered kernel: Bernoulli
  ``p_mu = 1/2``, then uniform ``delta`` on ``{±1, ±2, ±3, ±4}``; child
  ``A' = clamp(A + delta, 0, 255)``; ``T = 128`` and ``D = 255`` are never
  drawn.  Every other line -- G/V/R/P/C staging, rollback rule, shadow
  outcomes, telemetry payloads, ledger assertions -- is carried verbatim.
- Kernel draws come exclusively from the dedicated deterministic stream
  ``random.Random(hazard_seed * 1000003 + 7)``, disjoint from the hazard
  stream, so hazard realisations at a given seed remain identical to
  prior-generation runs.  Rolled-back transactions retain consumed draws
  (registered section 3 stream row); the fault checkpoints ``mid_M`` /
  ``post_M`` still fire after the kernel decision, preserving the carried
  fault-injection semantics exactly.
- Every Stage-M decision emits a ``mutation_decision`` telemetry record
  (parent A, delta or no-mutation flag, child A', stream position,
  draws consumed) so the reducer can reconcile records against admitted
  births without any tuning freedom (preregistration section 3).

No fitness, selection, invasion-growth, optimum, ESS, causal, or
external-validation claim is made here; this module runs populations
under the registered kernel, it does not interpret them.
"""

from __future__ import annotations

from fractions import Fraction
import random
from typing import Any

from stage7_slice1 import Child, MIN_WORKING_MEMORY, SliceOrganism
from stage7_slice2 import PopulationMember
from stage7b1_mechanics import (
    DivideTxn,
    FaultInjector,
    InjectedFault,
    REGISTERED_PACKET_RATE,
)
from stage7b2r_population import (
    REGISTERED_BUFFER_DEPTH,
    REGISTERED_CENSUS_CAPACITY,
    REGISTERED_CORPSE_TTL,
    REGISTERED_FOUNDER_S,
    REGISTERED_GENOTYPES,
    REGISTERED_HAZARD_RATE,
    REGISTERED_MEMORY_POOL,
    REGISTERED_PACKET_ENERGY,
    REGISTERED_WINDOW_TICKS,
)
from stage7b2_population import Stage7B2Population

# ---------------------------------------------------------------------------
# Registered kernel constants (preregistration section 3 -- binding values)
# ---------------------------------------------------------------------------

PROTOCOL = "stage-8-alpha-evolution-preregistration"
PREREG_DOCUMENT = "docs/stage-8-alpha-evolution-preregistration.md"

REGISTERED_MUTATION_PROB = Fraction(1, 2)
"""Per-published-birth-candidate probability that a step is drawn."""

REGISTERED_STEP_SUPPORT: tuple[int, ...] = (-4, -3, -2, -1, 1, 2, 3, 4)
"""Uniform step support; zero excluded; max |delta| = 4 < floor 8 lattice
units, so no single event can cross the registered direction floor."""

LATTICE_MAX = 255
FROZEN_T = 128
FROZEN_D = 255

MUTATION_STREAM_MULTIPLIER = 1000003
MUTATION_STREAM_OFFSET = 7


def mutation_seed(hazard_seed: int) -> int:
    """Registered stream derivation: disjoint from the hazard stream."""
    return int(hazard_seed) * MUTATION_STREAM_MULTIPLIER + MUTATION_STREAM_OFFSET


# ---------------------------------------------------------------------------
# Population subclass
# ---------------------------------------------------------------------------


class Stage8Population(Stage7B2Population):
    """Frozen 7B1/7B2 mechanics carrying the registered A-locus kernel."""

    def __init__(
        self,
        founder_genomes,
        *,
        capacity: int,
        founder_s: Fraction,
        memory_pool: int,
        hazard_seed: int,
        hazard_rate: Fraction = REGISTERED_HAZARD_RATE,
        corpse_ttl: int = REGISTERED_CORPSE_TTL,
        packet_rate: int = REGISTERED_PACKET_RATE,
        buffer_depth: int = REGISTERED_BUFFER_DEPTH,
        packet_energy: Fraction = REGISTERED_PACKET_ENERGY,
        window_ticks: int = REGISTERED_WINDOW_TICKS,
    ) -> None:
        super().__init__(
            founder_genomes=founder_genomes,
            capacity=capacity,
            founder_s=founder_s,
            memory_pool=memory_pool,
            hazard_seed=hazard_seed,
            hazard_rate=hazard_rate,
            corpse_ttl=corpse_ttl,
            packet_rate=packet_rate,
            buffer_depth=buffer_depth,
            packet_energy=packet_energy,
            window_ticks=window_ticks,
        )
        for a, t, d in founder_genomes:
            if t != FROZEN_T or d != FROZEN_D:
                raise ValueError(
                    "Stage 8 founders must carry the frozen T/D pair "
                    f"(128, 255); got ({t}, {d})")
        self.mutation_rng = random.Random(mutation_seed(hazard_seed))
        self.mutation_draws = 0
        self.mutation_decisions = 0

    def divide_publish(self, member: PopulationMember,
                       injector: FaultInjector | None = None) -> str | None:
        """Publish one child through the registered G/V/M/R/P/C stages.

        Verbatim copy of the frozen ``Stage7B1Population.divide_publish``
        body; ONLY Stage M differs (see module docstring).  Returns the
        child id on success and ``None`` on a registered non-fault failure
        (NO_VACANCY, CHILD_MEMORY_UNAVAILABLE).  Injected faults roll back
        per the registered rollback rule and re-raise ``InjectedFault``.
        """
        organism = member.organism
        parent_id = organism.organism_id
        # Stage G: validate the registered complete-gestation condition.
        if parent_id not in self.memory.gestation:
            raise RuntimeError("DIVIDE requires parent-owned complete gestation")
        child_id = self._new_id()
        txn = DivideTxn(parent_id=parent_id, child_id=child_id,
                        rng_at_start=self.rng_draws)
        try:
            # Stage V: atomically reserve one census vacancy.
            if self.would_admit_now():
                would_admit = True
            else:
                would_admit = False
            self._record_shadow_outcome(would_admit)
            if not would_admit:
                # Registered NO_VACANCY: no provisioning is computed; the
                # completed bout is discarded (architecture §7 step 2/4);
                # a failed attempt is never retried from stale gestation.
                # No kernel draw occurs: mutation supply ties to realised
                # births only (preregistration section 3, mutation site).
                self.memory.release_gestation(parent_id)
                txn.gestation_discarded = True
                self._emit({
                    "tick": self.tick, "phase": "admission",
                    "event": "divide_failed", "organism_id": parent_id,
                    "stage": "V", "reason": "NO_VACANCY",
                })
                self.next_id -= 1
                self.assert_all_ledgers(f"divide_no_vacancy:{parent_id}")
                return None
            self.vacancy_reserved += 1
            txn.vacancy_held = True
            self.observe("post_V", txn)
            if injector is not None:
                injector.checkpoint("post_V")

            # Stage M: THE registered substitution.  Dedicated-locus
            # kernel per docs/stage-8-alpha-evolution-preregistration.md
            # section 3: Bernoulli p_mu = 1/2, then uniform delta on
            # {±1..±4}, clamped to the legal lattice {0..255}; T = 128 and
            # D = 255 are never drawn.  Draws come only from the dedicated
            # mutation stream; rolled-back transactions retain consumed
            # draws.  The carried fault checkpoints mid_M / post_M fire
            # after the decision, exactly as in the frozen body.
            stream_position = self.mutation_draws
            mutated = self.mutation_rng.random() < float(
                REGISTERED_MUTATION_PROB)
            delta: int | None = None
            if mutated:
                delta = REGISTERED_STEP_SUPPORT[
                    self.mutation_rng.randrange(len(REGISTERED_STEP_SUPPORT))]
                candidate_a = min(LATTICE_MAX, max(0, organism.a + delta))
            else:
                candidate_a = organism.a
            candidate_t = organism.t
            candidate_d = organism.d
            self.mutation_draws += 2 if mutated else 1
            self.mutation_decisions += 1
            self._emit({
                "tick": self.tick, "phase": "mutation",
                "event": "mutation_decision",
                "parent_id": parent_id, "child_id": child_id,
                "parent_a": organism.a,
                "mutated": mutated,
                "delta": delta,
                "child_a": candidate_a,
                "stream_position": stream_position,
                "draws_consumed": 2 if mutated else 1,
                "kernel": f"p_mu={REGISTERED_MUTATION_PROB.numerator}/"
                          f"{REGISTERED_MUTATION_PROB.denominator};"
                          f"delta_uniform_on{list(REGISTERED_STEP_SUPPORT)}",
            })
            if not (candidate_d > 0 and 0 <= candidate_t <= candidate_d
                    and 0 <= candidate_a <= candidate_d):
                raise ValueError("post-indel candidate violates trait bounds")
            self.observe("mid_M", txn)
            if injector is not None:
                injector.checkpoint("mid_M")
            txn.candidate_basis = MIN_WORKING_MEMORY
            self.observe("post_M", txn)
            if injector is not None:
                injector.checkpoint("post_M")

            # Stage R: release the parent gestation, then atomically reserve
            # the child's full memory obligation from the candidate basis.
            self.memory.release_gestation(parent_id)
            txn.gestation_discarded = True
            if injector is not None:
                injector.checkpoint("mid_R")
            try:
                self.memory.reserve_child_memory(child_id, txn.candidate_basis)
            except MemoryError:
                self.vacancy_reserved -= 1
                txn.vacancy_held = False
                self._emit({
                    "tick": self.tick, "phase": "admission",
                    "event": "divide_failed", "organism_id": parent_id,
                    "stage": "R", "reason": "CHILD_MEMORY_UNAVAILABLE",
                })
                self.assert_all_ledgers(
                    f"divide_child_memory_unavailable:{parent_id}")
                return None
            txn.child_reserved = True
            self.observe("post_R", txn)
            if injector is not None:
                injector.checkpoint("post_R")

            # Stage P: exact provisional provisioning P=(T/D)R_w.
            txn.r_w = organism.r
            p_value = organism.tau_r * txn.r_w
            organism.r -= p_value
            txn.p_value = p_value
            if injector is not None:
                injector.checkpoint("mid_P")
            provisional_child = Child(
                child_id, s=p_value, a=candidate_a, t=candidate_t,
                d=candidate_d,
            )
            if injector is not None:
                injector.checkpoint("pre_C")

            # Stage C: single commit point.  No injector boundary, no event
            # emission, and no fallible operation exists inside this block;
            # trait bounds were validated in stage M.
            self.memory.convert_child_reservation(child_id)
            txn.child_reserved = False
            child = SliceOrganism(
                child_id, self.memory, provisional_child.s, Fraction(0),
                a=provisional_child.a, t=provisional_child.t,
                d=provisional_child.d,
                initial_memory_already_committed=True,
            )
            self.members[child_id] = PopulationMember(
                organism=child, born_tick=self.tick)
            self.all_organisms[child_id] = child
            self.ancestry[child_id] = self.ancestry.get(parent_id, parent_id)
            self.vacancy_reserved -= 1
            txn.vacancy_held = False
            self.admitted_births += 1
            txn.committed = True
            self.observe("post_C", txn)
            self._emit({
                "tick": self.tick, "phase": "admission",
                "event": "provision_committed", "organism_id": parent_id,
                "child_id": child_id,
                "provision": p_value,
                "r_w": txn.r_w,
                "p_equation": "P=(T/D)*R_w",
                "inherited_a_over_d": f"{candidate_a}/{candidate_d}",
                "inherited_t_over_d": f"{candidate_t}/{candidate_d}",
                "ancestry_id": self.ancestry[child_id],
                "genotype_hash": self.genotype_hash(
                    candidate_a, candidate_t, candidate_d),
                "realised_y_parent": organism.gross_income,
                "parent_s_pre": self.rat(Fraction(organism.s)),
                "parent_r_pre": self.rat(Fraction(organism.r) + p_value),
                "parent_s_post": self.rat(Fraction(organism.s)),
                "parent_r_post": self.rat(Fraction(organism.r)),
                "c_s_cumulative": organism.c_s,
                "c_r_cumulative": organism.c_r,
                "child_initial_s": provisional_child.s,
                "child_initial_r": Fraction(0),
                "candidate_memory_basis": txn.candidate_basis,
                "child_memory_reserved": txn.candidate_basis,
                "gestation_bytes_released": txn.candidate_basis,
                "vacancy_reserved_after": self.vacancy_reserved,
                "copy_stage_rng_consumed": False,
                "divide_stage_rng_consumed": False,
                "rng_draws_total": self.rng_draws,
                "committed_flag": True,
            })
            self._emit({
                "tick": self.tick, "phase": "admission",
                "event": "birth_admitted", "parent_id": parent_id,
                "child_id": child_id,
                "provision": p_value,
                "ancestry_id": self.ancestry[child_id],
                "genotype_hash": self.genotype_hash(
                    candidate_a, candidate_t, candidate_d),
                "shadow_would_admit": True,
            })
            self.assert_all_ledgers(f"birth_admitted:{child_id}")
            return child_id
        except InjectedFault as fault:
            self._rollback_divide(txn, fault.boundary)
            raise
        except Exception:
            # Architecture §7 step 7: ANY exception after vacancy reservation
            # and before commit rolls back identically.  Unexpected (non-
            # injected) exceptions carry no registered failure record -- they
            # indicate an implementation bug and classify the run invalid --
            # but they must never leave a reservation or partial child.
            if not txn.committed:
                self._rollback_divide(txn, None)
            raise


# ---------------------------------------------------------------------------
# Registered configuration echo (preregistration sections 2-3)
# ---------------------------------------------------------------------------

CONFIRMATORY_SEED_BASE = 20284617
"""Confirmatory table: ``20284617 + i``, i in 0..23; fresh, disjoint from
every prior population table by construction."""
SHAKEDOWN_SEED_BASE = 20293311
"""Shakedown table: ``20293311 + j``, j in 0..11; fixed before any run."""
SHAKEDOWN_SEED_COUNT = 12
STAGE8_REPLICATES = 24
"""Registered confirmatory replicate count ``k`` (preregistration §3);
distinct from the carried 7B2-R constant REGISTERED_REPLICATES = 32."""
REGISTERED_WINDOW_TICKS_STAGE8 = 2400
"""20 expected lifespans at h = 1/120; ~960 realised births per replicate."""
DIRECTION_FLOOR_ALPHA = Fraction(8, 255)
ALPHA_REF = Fraction(153, 255)


def confirmatory_seed(index: int) -> int:
    if not 0 <= index < STAGE8_REPLICATES:
        raise ValueError(
            f"confirmatory index must be in [0,{STAGE8_REPLICATES})")
    return CONFIRMATORY_SEED_BASE + index


def shakedown_seed(index: int) -> int:
    if not 0 <= index < SHAKEDOWN_SEED_COUNT:
        raise ValueError(
            f"shakedown index must be in [0,{SHAKEDOWN_SEED_COUNT})")
    return SHAKEDOWN_SEED_BASE + index


def shakedown_seeds() -> tuple[int, ...]:
    return tuple(shakedown_seed(i) for i in range(SHAKEDOWN_SEED_COUNT))


def stage8_founder_genomes() -> list[tuple[int, int, int]]:
    """Carried founder blocks: 3 x (102,128,255) + 3 x (204,128,255)."""
    genomes: list[tuple[int, int, int]] = []
    for genotype in REGISTERED_GENOTYPES:
        genomes.extend([genotype] * 3)
    return genomes


def registered_stage8_population(hazard_seed: int,
                                 window_ticks: int | None = None) -> (
                                 Stage8Population):
    """The registered section 3 confirmatory configuration, verbatim."""
    return Stage8Population(
        founder_genomes=stage8_founder_genomes(),
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


def registered_configuration() -> dict[str, Any]:
    """Echo of the binding values embedded in every artifact."""
    def fmt(value: Fraction) -> str:
        return f"{value.numerator}/{value.denominator}"

    return {
        "protocol": PROTOCOL,
        "prereg_document": PREREG_DOCUMENT,
        "window_ticks_W": REGISTERED_WINDOW_TICKS_STAGE8,
        "expected_lifespans_per_window": 20,
        "census_capacity_N": REGISTERED_CENSUS_CAPACITY,
        "buffer_depth_d": REGISTERED_BUFFER_DEPTH,
        "packet_rate_r": REGISTERED_PACKET_RATE,
        "packet_energy_E": fmt(REGISTERED_PACKET_ENERGY),
        "hazard_rate_h": fmt(REGISTERED_HAZARD_RATE),
        "replicates_k": STAGE8_REPLICATES,
        "confirmatory_seed_derivation":
            f"hazard_seed = {CONFIRMATORY_SEED_BASE} + i, i in 0..23",
        "shakedown_seed_derivation":
            f"hazard_seed = {SHAKEDOWN_SEED_BASE} + j, j in 0..11",
        "genotypes_ATD": [list(g) for g in REGISTERED_GENOTYPES],
        "founders_per_genotype": 3,
        "founder_S": fmt(REGISTERED_FOUNDER_S),
        "founder_R": "0/1",
        "corpse_ttl": REGISTERED_CORPSE_TTL,
        "memory_pool_bytes": REGISTERED_MEMORY_POOL,
        "alpha_ref": fmt(ALPHA_REF),
        "direction_floor_alpha": fmt(DIRECTION_FLOOR_ALPHA),
        "mutation_probability": fmt(REGISTERED_MUTATION_PROB),
        "step_support": list(REGISTERED_STEP_SUPPORT),
        "frozen_loci": {"T": FROZEN_T, "D": FROZEN_D},
        "lattice": f"A in 0..{LATTICE_MAX}, clamped",
        "mutation_stream": (
            "random.Random(hazard_seed * "
            f"{MUTATION_STREAM_MULTIPLIER} + {MUTATION_STREAM_OFFSET}); "
            "disjoint from the hazard stream"),
    }
