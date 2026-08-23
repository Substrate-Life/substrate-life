"""Stage 7B signed-bracket solver: full-line certified Euler-Lotka roots.

Implements the registered Section 3 "Solver domain" replacement of
``docs/stage-7b-signed-bracket-preregistration.md`` (the SUPERSEDING
preregistration that closes the complete-pair availability defect).  It
completes, rather than replaces, the estimand of
``docs/stage-7b2-preregistration.md`` Section 4: the certified rational
bracket of the unique real root of ``L(r) = sum_x c_x * e^{-r x} = 1``. The
domain is extended from ``r >= 0`` to the full real line, because
``L`` is continuous and strictly decreasing whenever some age ``x >= 1``
carries positive coefficient mass, with ``lim_{r -> -inf} L(r) = +inf`` and
``lim_{r -> +inf} L(r) = c_0``.

Everything here is ADDITIVE.  The frozen positive-half-line machinery of
``stage7b2_solver.py`` -- ``exp_neg_enclosure``, ``lotka_interval``,
``certified_bracket``, ``median_lower_middle`` -- is reused by import,
never edited in place (Authorisation section of the signed-bracket
preregistration).  This module supplies exactly what is new: a rigorous
enclosure of ``e^{+t}`` for ``t > 0`` (positive-term Taylor partial sums
are exact-rational lower bounds; the geometric remainder bound
``<= term_K * t / (K + 1 - t)`` once ``K + 1 > t`` gives the certified
upper bound), the negative-branch Lotka enclosure built from it via the
same exact-rational interval-squaring already used for the positive
branch, and the full-line classification/decision-rule wrapper (registered
Section 3 table).

All arithmetic here is analysis-side only; approximations never feed back
into any ledger.  No fitness, selection, optimum, or ESS claim is made or
implemented here.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from stage7b2_solver import (  # frozen; imported, never edited in place
    MIN_CONTRAST_DELTA_R,
    MIN_COMPLETE_PAIRS,
    SOLVER_RESOLUTION_RHO,
    _interval_pow,
    certified_bracket,
    fmt_rat,
    lotka_interval,
    median_lower_middle,
)

_BASE_GUARD_BITS = 48

FINITE_ROOT_STATUSES = ("SUPERCRITICAL", "CRITICAL", "SUBCRITICAL")
"""Statuses that carry a certified finite-root bracket (Section 3 table)."""


def exp_pos_enclosure(t: Fraction, guard_bits: int = _BASE_GUARD_BITS
                      ) -> tuple[Fraction, Fraction]:
    """Rigorous enclosure ``(lo, hi)`` of ``e^{+t}`` for ``t > 0``.

    ``S_K = sum_{k=0}^{K} t^k / k!`` is an exact-rational LOWER bound of
    ``e^t`` for every ``K`` (every term is non-negative).  Once
    ``K + 1 > t`` the geometric-tail bound
    ``e^t - S_K <= term_K * t / (K + 1 - t)`` (``term_K = t^K / K!``)
    gives a certified UPPER bound; iterate until that bound is at most
    ``2^-guard_bits``.
    """
    t = Fraction(t)
    if t <= 0:
        raise ValueError("enclosure requires t > 0")
    tol = Fraction(1, 2 ** guard_bits)
    term = Fraction(1)   # t^k / k!, k = 0 initially
    total = Fraction(1)  # S_k
    k = 0
    while True:
        k += 1
        term *= t / k
        total += term
        if k + 1 > t:
            remainder_bound = term * t / (k + 1 - t)
            if remainder_bound <= tol:
                return total, total + remainder_bound
        if k > 2_000_000:
            raise RuntimeError("exp(+t) enclosure failed to converge")


def lotka_interval_signed(c_x: dict[int, Fraction], r: Fraction,
                          guard_bits: int = _BASE_GUARD_BITS
                          ) -> tuple[Fraction, Fraction]:
    """Certified enclosure of ``L(r) = sum c_x e^{-r x}`` for any real ``r``.

    Dispatches to the frozen positive-half-line enclosure for ``r >= 0``
    (byte-identical reuse); implements the additive negative branch for
    ``r < 0`` using ``exp_pos_enclosure`` and the unchanged exact-rational
    interval-squaring machinery (``e^{-r x} = (e^{|r|})^x`` for ``r < 0``).
    """
    if r >= 0:
        return lotka_interval(c_x, r, guard_bits)
    enclosure = exp_pos_enclosure(-r, guard_bits)
    acc_lo = Fraction(0)
    acc_hi = Fraction(0)
    for x, cx in sorted(c_x.items()):
        powered = _interval_pow(enclosure, x)
        acc_lo += cx * powered[0]
        acc_hi += cx * powered[1]
    if acc_hi < acc_lo:
        raise AssertionError("Lotka enclosure inverted (negative branch)")
    return acc_lo, acc_hi


def full_line_certified_bracket(c_x: dict[int, Fraction],
                                rho: Fraction = SOLVER_RESOLUTION_RHO,
                                ) -> dict[str, Any]:
    """Registered Section 3 full-line solver contract.

    Classification (verbatim from the registered repair table):

    (i)   ``L(0) > 1``            -> ``SUPERCRITICAL``, bracket in [0, inf);
    (ii)  ``L(0) == 1`` (exact)   -> ``CRITICAL``, bracket exactly [0, 0];
    (iii) ``L(0) < 1`` and
          ``S_+ := sum_{x>=1} c_x > 0`` -> ``SUBCRITICAL`` with a certified
          NEGATIVE bracket;
    (iv)  ``S_+ == 0`` (with ``c_0 != 1``), or ``c_0 >= 1`` with
          ``S_+ > 0`` -> loud ``NO_FINITE_ROOT`` (rootless; excluded from
          pairing and counted against the Section 5 G1 gate condition).
    """
    l0_exact = sum(c_x.values(), Fraction(0))
    c0 = c_x.get(0, Fraction(0))
    s_plus = l0_exact - c0
    certificate: dict[str, Any] = {
        "L0_exact": l0_exact,
        "rho": rho,
        "support": {str(x): fmt_rat(cx) for x, cx in sorted(c_x.items())},
    }

    # (iv) rootless cases -- checked first; orthogonal to the L(0) vs 1
    # comparison.  Mechanically impossible while c_0 == 0 always holds
    # (no age-0 fecundity), but classified loudly if it ever occurs.
    if s_plus == 0 or (c0 >= 1 and s_plus > 0):
        certificate["status"] = "NO_FINITE_ROOT"
        certificate["reason"] = (
            f"rootless: S_plus={fmt_rat(s_plus)}, c_0={fmt_rat(c0)} "
            "(Section 3 item iv)")
        return certificate

    # From here: s_plus > 0 and c0 < 1, so L is continuous, strictly
    # decreasing, and ranges over (c0, +inf) as r ranges over (+inf, -inf);
    # a unique real root of L(r) = 1 is guaranteed.
    if l0_exact > 1:
        positive = certified_bracket(c_x, rho)  # frozen, byte-identical
        certificate.update(positive)
        certificate["status"] = "SUPERCRITICAL"
        return certificate

    if l0_exact == 1:
        certificate.update({
            "status": "CRITICAL",
            "r_lo": Fraction(0),
            "r_hi": Fraction(0),
            "width": Fraction(0),
            "iterations": 0,
            "certified": "L(0) == 1 exactly (Fraction equality)",
        })
        return certificate

    # l0_exact < 1 and s_plus > 0: certified negative bracket.
    guard_bits = _BASE_GUARD_BITS

    def sign_test(r: Fraction) -> str:
        nonlocal guard_bits
        bits = guard_bits
        for _ in range(10):
            lo_val, hi_val = lotka_interval_signed(c_x, r, bits)
            if lo_val >= 1:
                return "above"
            if hi_val < 1:
                return "below"
            bits += 32
        raise RuntimeError(f"could not certify sign of L at r={r}")

    if sign_test(Fraction(0)) != "below":
        raise AssertionError(
            "L(0) < 1 must be certifiable when subcritical")

    lo = -rho
    for _ in range(512):
        if sign_test(lo) == "above":
            break
        lo *= 2
    else:
        raise RuntimeError("no certified negative lower bracket found")

    hi = Fraction(0)
    iterations = 0
    while hi - lo > rho:
        mid = (lo + hi) / 2
        if sign_test(mid) == "above":
            lo = mid
        else:
            hi = mid
        iterations += 1
        if iterations > 4096:
            raise RuntimeError("bisection failed to converge")
    certificate.update({
        "status": "SUBCRITICAL",
        "r_lo": lo,
        "r_hi": hi,
        "width": hi - lo,
        "iterations": iterations,
        "guard_bits": guard_bits,
        "certified": (
            "L(r_lo) >= 1 > L(r_hi) under directed enclosures "
            "(negative branch)"),
    })
    return certificate


def full_line_bracket_midpoint(certificate: dict[str, Any]) -> Fraction | None:
    """Midpoint of any certified finite-root bracket; ``None`` if rootless."""
    if certificate["status"] not in FINITE_ROOT_STATUSES:
        return None
    return (certificate["r_lo"] + certificate["r_hi"]) / 2


def apply_full_line_decision_rule(
        replicate_outcomes: list[dict[int, dict[str, Any]]],
        delta_min: Fraction = MIN_CONTRAST_DELTA_R,
        min_complete_pairs: int = MIN_COMPLETE_PAIRS,
        ) -> dict[str, Any]:
    """Registered Section 3 decision-rule replacement, applied exactly once.

    Complete pairs are replicates where BOTH genotypes emit a certified
    finite-root bracket (any of SUPERCRITICAL/CRITICAL/SUBCRITICAL) rather
    than requiring joint supercriticality.  Class names, thresholds, and
    single-application discipline are carried unchanged from
    ``stage7b2_solver.apply_decision_rule``.
    """
    genotypes = sorted({g for outcome in replicate_outcomes
                        for g in outcome})
    if len(genotypes) != 2:
        raise ValueError("decision rule expects exactly two genotypes")

    per_genotype: dict[int, dict[str, Any]] = {}
    for g in genotypes:
        certs = [outcome[g] for outcome in replicate_outcomes]
        supers = [c for c in certs if c["status"] == "SUPERCRITICAL"]
        subs = [c for c in certs if c["status"] == "SUBCRITICAL"]
        crits = [c for c in certs if c["status"] == "CRITICAL"]
        rootless = [c for c in certs if c["status"] == "NO_FINITE_ROOT"]
        per_genotype[g] = {
            "supercritical_replicates": len(supers),
            "critical_replicates": len(crits),
            "subcritical_replicates": len(subs),
            "no_finite_root_replicates": len(rootless),
            "subcritical_at_this_ecology": len(subs) >= min_complete_pairs,
        }

    complete_pairs: list[tuple[Fraction, Fraction]] = []
    for outcome in replicate_outcomes:
        mids = []
        for g in genotypes:
            mid = full_line_bracket_midpoint(outcome[g])
            if mid is None:
                mids = None
                break
            mids.append(mid)
        if mids is not None:
            complete_pairs.append((mids[0], mids[1]))

    differences = [mid_b - mid_a for mid_a, mid_b in complete_pairs]
    median_difference = median_lower_middle(differences)
    positive_diffs = sum(1 for d in differences if d > 0)
    negative_diffs = sum(1 for d in differences if d < 0)
    zero_diffs = len(differences) - positive_diffs - negative_diffs
    details: dict[str, Any] = {
        "rule": "stage-7b-signed-bracket-preregistration section 3",
        "delta_min": delta_min,
        "min_complete_pairs": min_complete_pairs,
        "complete_pairs": len(complete_pairs),
        "median_paired_difference": median_difference,
        "sign_split": {
            "positive": positive_diffs,
            "negative": negative_diffs,
            "zero": zero_diffs,
        },
        "per_genotype": {
            str(g): stats for g, stats in per_genotype.items()},
    }
    if len(complete_pairs) < min_complete_pairs:
        pair_class = "DEGENERATE_REPLICATION"
    else:
        assert median_difference is not None
        pair_class = ("ESTABLISHED_CONTRAST"
                      if abs(median_difference) >= delta_min
                      else "NO_ESTABLISHED_CONTRAST")
    subcritical_class = None
    flags = [per_genotype[g]["subcritical_at_this_ecology"]
             for g in genotypes]
    if all(flags):
        subcritical_class = "BOTH_SUBCRITICAL"
    elif any(flags):
        subcritical_class = "ONE_ARM_SUBCRITICAL"
    details["pair_contrast_class"] = pair_class
    details["subcritical_report"] = subcritical_class
    return details
