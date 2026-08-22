"""Stage 7B2 measurement: exact estimators from event-ledger records.

Implements the registered Section 3 estimator definitions of
``docs/stage-7b2-preregistration.md`` (which binds the 7B1 Section 6.1
endpoint definitions) as pure functions over event-ledger records plus the
registered window.  Every quantity is an exact ``Fraction`` or integer; no
imputation of any kind exists; approximations never enter this module.

Registered definitions implemented here:

- genotype membership by exact ``(A, T, D)`` inheritance, read from the
  ``a_over_d`` field of ``founder_registered`` / ``birth_admitted`` events;
- attained age: a member admitted at measurement tick ``t`` attains age
  ``x`` at tick ``t + x`` if it is still alive entering that tick; hazard
  deaths at tick ``u`` therefore attain age ``u - t`` (exposure includes the
  death tick); right-censored members alive through tick ``W`` attain ages
  through ``W - t``; founders carry measurement birth tick ``0`` (their
  configuration-phase ``born_tick`` is ``-1``, shifted so they attain age
  ``x`` at tick ``x``);
- ``l_x(g) = |{members of g attaining age >= x}| / |C_g|`` with ``C_g`` the
  set of genotype-``g`` members ever alive in the replicate;
- establishment rule: an establishment is an offspring's *first*
  reproduction; credit goes to the offspring's parent at the parent's age
  ``x = tau - born_tick(child)`` where ``tau`` is the tick of that first
  reproduction; ``m_x(g) = (# establishments with a genotype-``g`` parent of
  age exactly x) / |C_g|``;
- censored members contribute exposure and survival counts but no ``m_x``
  events; nothing is projected beyond the window;
- mediators are reported separately and never substituted for the endpoint.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

ESTABLISHMENT_FIRST_REPRODUCTION = (
    "offspring's first reproduction credits its parent (prereg Section 3)")


def parse_rat(text: str) -> Fraction:
    """Parse a canonical ``num/den`` serialisation into an exact Fraction."""
    numerator, _, denominator = text.strip().partition("/")
    return Fraction(int(numerator), int(denominator))


def fmt_rat(value: Fraction) -> str:
    """Canonical exact serialisation of a rational."""
    return f"{value.numerator}/{value.denominator}"


def _measurement_birth_tick(raw_born_tick: int) -> int:
    """Founders (raw ``born_tick == -1``) enter the measurement clock at 0."""
    return max(raw_born_tick, 0)


def extract_vital_records(event_log: list[dict[str, Any]],
                          window_ticks: int) -> dict[str, Any]:
    """Derive the complete vital-record table from one replicate's events.

    Pure function of the event ledger and the window; the reducer reruns
    exactly this function over the retained tables and must reproduce the
    runner's schedules bit-exactly.
    """
    if window_ticks <= 0:
        raise ValueError("window must be positive")
    members: dict[str, dict[str, Any]] = {}
    births: list[dict[str, Any]] = []
    establishments: list[dict[str, Any]] = []
    first_reproduction: dict[str, int] = {}
    first_extraction: dict[str, int] = {}
    first_divide_attempt: dict[str, int] = {}
    pending_child_genotype: dict[str, int] = {}
    divide_attempts = 0
    no_vacancy_attempts = 0
    child_memory_unavailable_attempts = 0
    somatic_stalls = 0

    def ensure(organism_id: str) -> None:
        if organism_id not in members:
            members[organism_id] = {
                "genotype_a": None,
                "born_tick": None,
                "death_tick": None,
            }

    for event in event_log:
        kind = event.get("event")
        if kind == "founder_registered":
            organism_id = event["organism_id"]
            members[organism_id] = {
                "genotype_a": int(event["a_over_d"].split("/")[0]),
                "born_tick": _measurement_birth_tick(-1),
                "death_tick": None,
            }
        elif kind == "provision_committed":
            # Committed provisioning carries the exact inherited traits;
            # it precedes its birth_admitted event within the same tick.
            divide_attempts += 1
            first_divide_attempt.setdefault(
                event["organism_id"], int(event["tick"]))
            pending_child_genotype[event["child_id"]] = int(
                event["inherited_a_over_d"].split("/")[0])
        elif kind == "birth_admitted":
            tick = int(event["tick"])
            parent_id = event["parent_id"]
            child_id = event["child_id"]
            genotype_a = pending_child_genotype.pop(child_id)
            members[child_id] = {
                "genotype_a": genotype_a,
                "born_tick": tick,
                "death_tick": None,
            }
            births.append({
                "child_id": child_id,
                "parent_id": parent_id,
                "tick": tick,
                "genotype_a": genotype_a,
                "provision": event["provision"],
            })
            if parent_id not in first_reproduction:
                first_reproduction[parent_id] = tick
        elif kind == "hazard_death":
            organism_id = event["organism_id"]
            ensure(organism_id)
            members[organism_id]["death_tick"] = int(event["tick"])
        elif kind == "packet_draw":
            organism_id = event["organism_id"]
            first_extraction.setdefault(organism_id, int(event["tick"]))
        elif kind == "divide_failed":
            divide_attempts += 1
            reason = event.get("reason")
            if reason == "NO_VACANCY":
                no_vacancy_attempts += 1
            elif reason == "CHILD_MEMORY_UNAVAILABLE":
                child_memory_unavailable_attempts += 1
            first_divide_attempt.setdefault(
                event["organism_id"], int(event["tick"]))
        elif kind == "somatic_stall":
            somatic_stalls += 1

    # Establishment table: each offspring's FIRST reproduction credits its
    # parent.  first_reproduction already holds the earliest such tick per
    # parent because the log is append-ordered.
    for parent_id, tau in sorted(first_reproduction.items()):
        ensure(parent_id)
        # The reproducing individual is itself a born member whose own birth
        # record carries its parent; recover that parent from births.
        own_birth = next((b for b in births if b["child_id"] == parent_id),
                         None)
        if own_birth is None:
            continue  # a founder's first reproduction confers no credit
        grandparent_id = own_birth["parent_id"]
        ensure(grandparent_id)
        child_born = members[parent_id]["born_tick"]
        establishments.append({
            "parent_id": grandparent_id,
            "through_offspring": parent_id,
            "tick": tau,
            "parent_age": tau - child_born,
        })

    return {
        "window_ticks": window_ticks,
        "members": {oid: dict(record)
                    for oid, record in sorted(members.items())},
        "births": births,
        "establishments": establishments,
        "first_reproduction": dict(sorted(first_reproduction.items())),
        "first_extraction": dict(sorted(first_extraction.items())),
        "first_divide_attempt": dict(sorted(first_divide_attempt.items())),
        "attempt_counters": {
            "shadow_decisions_identity": divide_attempts,
            "no_vacancy_attempts": no_vacancy_attempts,
            "child_memory_unavailable_attempts":
                child_memory_unavailable_attempts,
            "somatic_stalls": somatic_stalls,
        },
    }


def cohort_genotypes(vitals: dict[str, Any]) -> list[int]:
    """Distinct genotype A values present in the vital records."""
    return sorted({record["genotype_a"]
                   for record in vitals["members"].values()
                   if record["genotype_a"] is not None})


def cohort_schedule(vitals: dict[str, Any],
                    genotype_a: int) -> dict[str, Any]:
    """Exact ``C_g``, ``l_x``, ``m_x``, and descriptive exposure totals."""
    window = vitals["window_ticks"]
    cohort = {
        oid: record for oid, record in vitals["members"].items()
        if record["genotype_a"] == genotype_a
    }
    cohort_size = len(cohort)
    if cohort_size == 0:
        raise ValueError(f"empty genotype cohort A={genotype_a}")
    l_counts = [0] * (window + 1)
    exposure_ticks = 0
    censored = 0
    died = 0
    for record in cohort.values():
        born = record["born_tick"]
        death = record["death_tick"]
        if death is None:
            last_age = window - born
            censored += 1
        else:
            last_age = death - born
            died += 1
        if last_age < 0:
            raise AssertionError(
                f"negative attained age for member born {born} "
                f"dead {death}")
        exposure_ticks += last_age + 1
        for x in range(0, min(last_age, window) + 1):
            l_counts[x] += 1
    l_x = [Fraction(count, cohort_size) for count in l_counts]

    m_counts = [0] * (window + 1)
    for event in vitals["establishments"]:
        parent = vitals["members"].get(event["parent_id"])
        if parent is None or parent["genotype_a"] != genotype_a:
            continue
        age = event["parent_age"]
        if not 0 <= age <= window:
            raise AssertionError(f"establishment age {age} outside window")
        m_counts[age] += 1
    m_x = [Fraction(count, cohort_size) for count in m_counts]

    return {
        "genotype_a": genotype_a,
        "cohort_size": cohort_size,
        "died": died,
        "censored": censored,
        "exposure_member_ticks": exposure_ticks,
        "l_x": l_x,
        "m_x": m_x,
    }


def build_c_vector(l_x: list[Fraction],
                   m_x: list[Fraction]) -> dict[int, Fraction]:
    """Exact Lotka coefficients ``c_x = l_x * m_x`` with trimmed support."""
    support: dict[int, Fraction] = {}
    for x, (lx, mx) in enumerate(zip(l_x, m_x)):
        value = lx * mx
        if value != 0:
            support[x] = value
    return support


def mediator_summary(vitals: dict[str, Any],
                     shadow_decisions: int,
                     shadow_would_admit: int,
                     admitted_births: int) -> dict[str, Any]:
    """Reported mediators; never substituted for the endpoint.

    Intrinsic bout completion, ecological vacancy availability, and realised
    recruitment are reported separately per the 7B1 Section 6.2 decision.
    ``shadow_decisions`` satisfies the exact identity
    ``shadow_decisions == provision_committed + divide_failed`` (every DIVIDE
    publication attempt records exactly one shadow outcome), cross-checked
    here against the event-ledger counters.
    """
    if admitted_births != len(vitals["births"]):
        raise AssertionError(
            "admitted-birth counter disagrees with the event ledger")
    if shadow_decisions != \
            vitals["attempt_counters"]["shadow_decisions_identity"]:
        raise AssertionError("shadow-decision identity violated")

    def _rate(numerator: int, denominator: int) -> str | None:
        return fmt_rat(Fraction(numerator, denominator)) if denominator else None

    first_success_ages = []
    for parent_id, tau in vitals["first_reproduction"].items():
        born = vitals["members"].get(parent_id, {}).get("born_tick")
        if born is not None:
            first_success_ages.append(tau - born)
    first_attempt_ages = []
    for organism_id, tick in vitals["first_divide_attempt"].items():
        born = vitals["members"].get(organism_id, {}).get("born_tick")
        if born is not None:
            first_attempt_ages.append(tick - born)
    return {
        "bout_completion_rate_intrinsic":
            _rate(admitted_births, shadow_decisions),
        "vacancy_availability_rate_ecological":
            _rate(shadow_would_admit, shadow_decisions),
        "realised_recruitment_per_attempt":
            _rate(admitted_births, shadow_decisions),
        "shadow_decisions": shadow_decisions,
        "shadow_would_admit": shadow_would_admit,
        "admitted_births": admitted_births,
        "no_vacancy_attempts":
            vitals["attempt_counters"]["no_vacancy_attempts"],
        "first_attempt_age_min": min(first_attempt_ages) if first_attempt_ages else None,
        "first_attempt_age_max": max(first_attempt_ages) if first_attempt_ages else None,
        "first_success_age_min": min(first_success_ages) if first_success_ages else None,
        "first_success_age_max": max(first_success_ages) if first_success_ages else None,
    }
