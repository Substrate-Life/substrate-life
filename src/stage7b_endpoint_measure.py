"""Stage 7B endpoint-repair measurement: the corrected raw-fecundity m_x.

Implements the registered section 3 replacement of
``docs/stage-7b-endpoint-repair-preregistration.md`` (committed 17b6aed):
the endpoint ``m_x(g)`` is **raw age-specific fecundity** -- every admitted
birth counts exactly once, credited to its immediate parent at the
parent's attained age at the birth tick, with no requirement that the
offspring itself reproduce -- restoring the textbook Euler-Lotka
correspondence cited by the equation this endpoint solves.  The former
endpoint numerator (establishment credit through an offspring's first
reproduction, ``stage-7b1-preregistration.md`` section 6.1) is retained,
unchanged in every other respect, as a **reported mediator** and is never
substituted for the endpoint.

Everything here is additive.  The event-ledger extraction
(``stage7b2_measure.extract_vital_records``), survivorship ``l_x`` and the
establishment schedule (``stage7b2_measure.cohort_schedule``), Lotka
coefficient assembly (``stage7b2_measure.build_c_vector``), the certified
solver (``stage7b2_solver``), and the population machinery are reused
byte-identically from the retained freezes; per sections 5.1 and 8 of the
endpoint-repair preregistration the frozen modules
``stage7b2_measure.py``, ``stage7b2_population.py``, ``stage7b2_solver.py``
and ``stage7b2r_population.py`` are never edited in place.  Every quantity
is an exact ``Fraction`` or integer; no imputation or approximation of any
kind exists in this module.

Registered definitions implemented here (endpoint-repair prereg section 3):

- ``m_x(g) = |{births to a genotype-g parent of age exactly x}| / |C_g|``
  -- the ENDPOINT; credited to the immediate parent at the parent's age at
  the birth tick; founders' births count exactly like non-founders' births;
- ``l_x(g)`` -- unchanged, taken bit-exactly from the frozen
  ``cohort_schedule``;
- establishment / first-reproduction credit -- unchanged as a quantity,
  reported as the mediator ``establishment_m_x``; it earns nothing on its
  own;
- ``c_x = l_x * m_x`` and ``L(0) = sum(c_x)`` -- assembled with the frozen
  ``build_c_vector`` and certified by the frozen solver contract.

No fitness, selection, optimum, or ESS claim is made or implemented here;
this module measures registered quantities, nothing more.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from stage7b2_measure import cohort_schedule

RAW_FECUNDITY_M_X = (
    "raw age-specific fecundity: every admitted birth credited exactly "
    "once to its immediate parent at the parent's age at the birth tick "
    "(endpoint-repair prereg section 3)")
ESTABLISHMENT_MEDIATOR = (
    "offspring's first reproduction credits its parent; reported mediator "
    "only, never substituted for the endpoint (endpoint-repair prereg "
    "section 3)")


def raw_fecundity_counts(vitals: dict[str, Any],
                         genotype_a: int) -> list[int]:
    """Per-age birth counts credited to genotype-``g`` parents.

    The endpoint numerator before cohort normalisation: ``counts[x]`` is
    the number of admitted births whose immediate parent is a genotype-
    ``g`` member that attained age exactly ``x`` at the birth tick.  Every
    admitted birth is counted exactly once (births conservation); the
    offspring's own reproductive history is never consulted.
    """
    window = vitals["window_ticks"]
    members = vitals["members"]
    counts = [0] * (window + 1)
    for birth in vitals["births"]:
        parent = members.get(birth["parent_id"])
        # A genuine parent is always a founder or a previously admitted
        # child, both carrying an integer genotype.  The frozen extraction
        # fabricates genotype-less stub records for first-reproduction
        # keys without membership; crediting such a stub would mean a
        # corrupted ledger, which must fail loudly here.
        if parent is None or parent["genotype_a"] is None:
            raise AssertionError(
                f"birth {birth['child_id']!r} credits parent "
                f"{birth['parent_id']!r} with no registered genotype")
        if parent["genotype_a"] != genotype_a:
            continue
        child = members.get(birth["child_id"])
        if child is None:
            raise AssertionError(
                f"admitted birth {birth['child_id']!r} absent from the "
                "member table")
        if child["genotype_a"] != genotype_a:
            raise AssertionError(
                "mutation-disabled genotype invariance violated: child of "
                f"A={parent['genotype_a']} parent recorded as "
                f"A={child['genotype_a']}")
        age = int(birth["tick"]) - parent["born_tick"]
        if not 0 <= age <= window:
            raise AssertionError(f"birth age {age} outside window")
        counts[age] += 1
    return counts


def establishment_counts(vitals: dict[str, Any],
                         genotype_a: int) -> list[int]:
    """Per-age establishment counts (the mediator numerator, unnormalised).

    Exact integer counterpart of the frozen ``cohort_schedule`` ``m_x``
    numerators: an establishment is an offspring's first reproduction,
    crediting its parent at the parent's age at that tick; founders' first
    reproductions confer no credit.  Reported as a mediator only.
    """
    window = vitals["window_ticks"]
    members = vitals["members"]
    counts = [0] * (window + 1)
    for event in vitals["establishments"]:
        parent = members.get(event["parent_id"])
        if parent is None or parent["genotype_a"] != genotype_a:
            continue
        age = int(event["parent_age"])
        if not 0 <= age <= window:
            raise AssertionError(f"establishment age {age} outside window")
        counts[age] += 1
    return counts


def endpoint_schedule(vitals: dict[str, Any],
                      genotype_a: int) -> dict[str, Any]:
    """Exact ``C_g``, ``l_x``, corrected raw-fecundity ``m_x``, mediator.

    ``l_x`` and the descriptive cohort fields are taken bit-exactly from
    the frozen ``stage7b2_measure.cohort_schedule``; only the ``m_x``
    numerator is replaced, per the registered section 3 decision.  The
    returned ``m_x`` is the ENDPOINT; ``establishment_m_x`` is the
    former endpoint retained as a reported mediator.
    """
    legacy = cohort_schedule(vitals, genotype_a)
    cohort_size = legacy["cohort_size"]
    births_by_age = raw_fecundity_counts(vitals, genotype_a)
    establishments_by_age = establishment_counts(vitals, genotype_a)
    return {
        "genotype_a": genotype_a,
        "cohort_size": cohort_size,
        "died": legacy["died"],
        "censored": legacy["censored"],
        "exposure_member_ticks": legacy["exposure_member_ticks"],
        "l_x": legacy["l_x"],
        "m_x": [Fraction(count, cohort_size)
                for count in births_by_age],
        "establishment_m_x": [Fraction(count, cohort_size)
                              for count in establishments_by_age],
        "births_credited": sum(births_by_age),
        "establishments_credited": sum(establishments_by_age),
    }
