"""Stage 7B two-factor endpoint measurement: risk-set survivorship x
person-tick fecundity.

Implements the registered section 3 replacement of
``docs/stage-7b-denominator-repair-preregistration.md``: the endpoint
coefficient assembly is repaired to the standard demographic pair

- ``m^E_x(g) = n_x(g) / E_x(g)`` -- per-capita fecundity conditional on
  being alive at age ``x`` (raw admitted-birth counts over person-ticks
  lived at exact age x), and
- ``l^A_x(g)`` -- window-actuarial survivorship conditioned on risk sets:
  ``l^A_0 = 1``, ``l^A_{x+1} = l^A_x * (E_x - d_x) / E_x`` with ``d_x``
  the deaths at exact attained age x; right-censored members contribute
  exposure but no death,

so that ``c_x = l^A_x * m^E_x`` and ``L(0) = sum(c_x)`` is the standard
net reproductive rate ``R_0``, unbounded above 1 exactly when the
population genuinely grows.

Why both factors must change (denominator-repair prereg section 2,
Lemma C): the frozen survivorship ``l_x = l_counts[x] / |C_g|`` shares its
denominator set with the exposure ``E_x = l_counts[x]`` (both equal the
number attaining age x), so any two-factor form ``l_x * (n_x / E_x)``
collapses algebraically to ``n_x / |C_g|`` term-by-term -- i.e. to the
scalar-cohort endpoint whose ceiling ``L(0) = B_g / |C_g| < 1`` Theorem B
proved unsatisfiable.  The repair therefore replaces the survivorship
FACTOR of the endpoint with the risk-set-conditioned curve (the reported
descriptive ``l_x`` itself is unchanged and continues to be reported).

Everything here is additive.  The event-ledger extraction
(``stage7b2_measure.extract_vital_records``), the descriptive cohort
schedule (``stage7b2_measure.cohort_schedule``), Lotka coefficient
assembly (``stage7b2_measure.build_c_vector`` -- it accepts any exact
survivorship vector), the certified solver, and the raw-fecundity
numerator counting (``stage7b_endpoint_measure.raw_fecundity_counts`` /
``establishment_counts``) are reused byte-identically from the retained
freezes / committed windows; per the Authorisation section and section 8
of the denominator-repair preregistration no existing module is edited in
place.  Every quantity is an exact ``Fraction`` or integer; no imputation
or approximation of any kind exists in this module.

Binding identities enforced here (denominator-repair prereg section 3):

- (i)   ``sum_x E_x(g) = exposure_member_ticks(g)`` (frozen total);
- (ii)  ``sum_x n_x(g) = |C_g| - F_g`` (verified where founder counts are
        known by construction: tests, gate, runner metadata);
- (iii) ``n_x(g) <= E_x(g)`` for every x (births require live parents);
- (iv)  ``sum_x d_x(g) + censored_g = |C_g|`` (every member either dies
        in-window at some attained age or is right-censored at W);
- (v)   ``l^A_0(g) = 1``; ``l^A`` non-increasing; ``0 <= l^A_x <= 1``.

No fitness, selection, optimum, or ESS claim is made or implemented here;
this module measures registered quantities, nothing more.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from stage7b2_measure import build_c_vector, cohort_schedule
from stage7b_endpoint_measure import establishment_counts, raw_fecundity_counts

EXPOSURE_FECUNDITY_M_X = (
    "per-capita age-specific fecundity: raw birth counts divided by "
    "person-ticks lived at exact age x (denominator-repair prereg "
    "section 3)")
ACTUARIAL_SURVIVORSHIP = (
    "window-actuarial risk-set survivorship l^A: l^A_0 = 1, "
    "l^A_{x+1} = l^A_x * (E_x - d_x)/E_x; right-censored members "
    "contribute exposure but no death (denominator-repair prereg "
    "section 3)")
ZERO_EXPOSURE_CONVENTION = (
    "where E_x(g) = 0 the coefficient contribution is defined as exactly 0 "
    "(m^E_x = 0 and l^A vanishes beyond the last attained age)")


def exposure_denominators(vitals: dict[str, Any],
                          genotype_a: int,
                          legacy: dict[str, Any] | None = None) -> list[int]:
    """Exact per-age person-ticks ``E_x(g)`` recovered from frozen integers.

    ``E_x(g)`` equals the number of genotype-``g`` members attaining age
    ``x`` -- precisely the frozen survivorship count ``l_counts[x]`` --
    recovered bit-exactly as ``l_x[x] * |C_g|``.  A non-integer product is
    impossible for any schedule produced by the frozen loop and fails
    loudly here if it ever occurs.
    """
    if legacy is None:
        legacy = cohort_schedule(vitals, genotype_a)
    cohort_size = legacy["cohort_size"]
    e_x: list[int] = []
    for lx in legacy["l_x"]:
        value = lx * cohort_size
        if not isinstance(value, Fraction) or value.denominator != 1:
            raise AssertionError(
                f"non-integer exposure count {value} at some age for "
                f"A={genotype_a}; frozen l_x inconsistent with |C_g|")
        e_x.append(value.numerator)
    # Binding identity (i): person-ticks partition matches the frozen
    # descriptive exposure total exactly.
    if sum(e_x) != legacy["exposure_member_ticks"]:
        raise AssertionError(
            f"exposure partition mismatch for A={genotype_a}: sum(E_x)="
            f"{sum(e_x)} != exposure_member_ticks="
            f"{legacy['exposure_member_ticks']}")
    return e_x


def deaths_by_age(vitals: dict[str, Any],
                  genotype_a: int) -> tuple[list[int], int]:
    """Exact ``d_x(g)`` (deaths at exact attained age x) and censor count.

    A member dying at tick ``u`` after birth at ``t`` attains ages
    ``0..u-t`` (the carried exposure convention includes the death tick)
    and contributes one death at exact attained age ``u - t``.  Members
    alive through the window are right-censored: they contribute exposure
    through ``W`` and no death anywhere.
    """
    window = vitals["window_ticks"]
    d_x = [0] * (window + 1)
    censored = 0
    seen = 0
    for record in vitals["members"].values():
        if record["genotype_a"] != genotype_a:
            continue
        seen += 1
        born = record["born_tick"]
        death = record["death_tick"]
        if death is None:
            censored += 1
            continue
        last_age = int(death) - int(born)
        if not 0 <= last_age <= window:
            raise AssertionError(
                f"death attained age {last_age} outside window for "
                f"A={genotype_a}")
        d_x[last_age] += 1
    # Binding identity (iv): every member either dies in-window at some
    # attained age or is right-censored at W.
    if sum(d_x) + censored != seen:
        raise AssertionError(
            f"death/censor partition mismatch for A={genotype_a}: "
            f"{sum(d_x)} + {censored} != {seen}")
    return d_x, censored


def actuarial_survivorship(e_x: list[int], d_x: list[int]) -> list[Fraction]:
    """Exact risk-set survivorship ``l^A_x`` (denominator-repair prereg s3).

    ``l^A_0 = 1``; ``l^A_{x+1} = l^A_x * (E_x - d_x)/E_x`` wherever
    ``E_x > 0``; beyond the last attained age (``E_x = 0``) the curve is
    exactly zero.  Non-increasing and confined to ``[0, 1]`` by
    construction; violations fail loudly.
    """
    if len(e_x) != len(d_x):
        raise AssertionError(
            f"exposure/death length mismatch: {len(e_x)} vs {len(d_x)}")
    curve: list[Fraction] = [Fraction(1)]
    for x, (e, d) in enumerate(zip(e_x, d_x)):
        if d > e:
            raise AssertionError(
                f"deaths exceed person-ticks at age {x}: d_x={d} > E_x={e}")
        if e == 0:
            curve.append(Fraction(0))
        else:
            curve.append(curve[-1] * Fraction(e - d, e))
    curve = curve[:len(e_x)]
    value: Fraction
    for value in curve:
        if not 0 <= value <= 1:
            raise AssertionError(f"survivorship {value} outside [0, 1]")
    for earlier, later in zip(curve, curve[1:]):
        if later > earlier:
            raise AssertionError("actuarial survivorship increased")
    return curve


def exposure_schedule(vitals: dict[str, Any],
                      genotype_a: int) -> dict[str, Any]:
    """Exact two-factor endpoint schedule for one genotype.

    Returns the frozen descriptive quantities (``l_x``, exposure totals),
    the new estimator components (``e_x``, ``d_x``, ``l_actuarial_x``,
    ``m_exposure_x``), the assembled ENDPOINT coefficients under
    ``c_x = l^A_x * m^E_x``, and the establishment quantity retained as a
    reported mediator, unchanged.
    """
    legacy = cohort_schedule(vitals, genotype_a)
    cohort_size = legacy["cohort_size"]
    e_x = exposure_denominators(vitals, genotype_a, legacy)
    d_x, censored = deaths_by_age(vitals, genotype_a)
    if censored != legacy["censored"] or sum(d_x) != legacy["died"]:
        raise AssertionError(
            f"death/censor counts disagree with frozen schedule for "
            f"A={genotype_a}")
    l_actuarial_x = actuarial_survivorship(e_x, d_x)
    births_by_age = raw_fecundity_counts(vitals, genotype_a)
    establishments_by_age = establishment_counts(vitals, genotype_a)
    if len(births_by_age) != len(e_x):
        raise AssertionError(
            f"numerator/denominator length mismatch for A={genotype_a}: "
            f"{len(births_by_age)} vs {len(e_x)}")
    # Binding identity (iii): births require live parents at that age.
    for age, (n, e) in enumerate(zip(births_by_age, e_x)):
        if n > e:
            raise AssertionError(
                f"births exceed person-ticks for A={genotype_a} at age "
                f"{age}: n_x={n} > E_x={e}")
    m_exposure_x = [
        Fraction(n, e) if e > 0 else Fraction(0)
        for n, e in zip(births_by_age, e_x)]
    return {
        "genotype_a": genotype_a,
        "cohort_size": cohort_size,
        "died": legacy["died"],
        "censored": legacy["censored"],
        "exposure_member_ticks": legacy["exposure_member_ticks"],
        "l_x": legacy["l_x"],
        "d_x": d_x,
        "e_x": e_x,
        "l_actuarial_x": l_actuarial_x,
        "m_exposure_x": m_exposure_x,
        "c_x": build_c_vector(l_actuarial_x, m_exposure_x),
        "establishment_m_x": [Fraction(count, cohort_size)
                              for count in establishments_by_age],
        "births_credited": sum(births_by_age),
        "establishments_credited": sum(establishments_by_age),
        "person_ticks_credited": sum(e_x),
    }


def lotka_coefficients(schedule: dict[str, Any]) -> dict[int, Fraction]:
    """Exact endpoint coefficients ``c_x = l^A_x * m^E_x`` (frozen assembly)."""
    return schedule["c_x"]
