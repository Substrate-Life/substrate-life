"""Stage 7B2 solver: certified rational Euler-Lotka brackets.

Implements the registered Section 4 solver contract of
``docs/stage-7b2-preregistration.md``.  For an exact coefficient vector
``c_x = l_x(g) * m_x(g)`` (finite support, non-negative, exact Fractions):

1. ``L(0) = sum(c_x)`` is computed exactly; ``L(0) <= 1`` classifies the
   genotype-replicate ``SUBCRITICAL`` and emits no numeric growth rate.
2. Otherwise the unique positive root of ``L(r) = sum(c_x * e^(-r x)) = 1``
   (strictly decreasing in ``r > 0`` by structural monotonicity) is located
   by monotone sign bisection on certified enclosures.
3. Exponential evaluation uses rigorous enclosures: a directed Taylor
   enclosure of ``e^(-t)`` with exact alternating-series remainder bounds,
   raised to integer powers by exponentiation-by-squaring under exact
   rational interval multiplication (products of rationals are exact, so
   containment is preserved with computable width growth).
4. Bracket endpoints are exact rationals with certified containment and
   width at most the registered resolution ``rho_r = 1/256``.

All arithmetic here is analysis-side only; approximations never feed back
into any ledger.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

SOLVER_RESOLUTION_RHO = Fraction(1, 256)
"""Registered solver resolution ``rho_r`` per tick."""

MIN_CONTRAST_DELTA_R = Fraction(1, 100)
"""Registered minimum contrast for the Section 5 decision rule."""

MIN_COMPLETE_PAIRS = 16
"""Registered minimum complete pairs (of k = 32) for a contrast decision."""

_BASE_GUARD_BITS = 48


def exp_neg_enclosure(t: Fraction, guard_bits: int = _BASE_GUARD_BITS
                      ) -> tuple[Fraction, Fraction]:
    """Rigorous enclosure ``(lo, hi)`` of ``e^(-t)`` for ``t >= 0``.

    Signed alternating-series partial sums bracket the true value once the
    terms are decreasing (guaranteed once ``k > t``); stopping after the
    latest term drops below ``2^-guard_bits`` bounds the tail by that term.
    """
    t = Fraction(t)
    if t < 0:
        raise ValueError("enclosure requires t >= 0")
    if t == 0:
        return Fraction(1), Fraction(1)
    tol = Fraction(1, 2 ** guard_bits)
    magnitude = Fraction(1)     # |t^k / k!|
    total = Fraction(1)         # signed partial sum, k = 0
    last_odd: Fraction | None = None
    last_even: Fraction | None = None   # includes the k = 0 term
    k = 0
    decreasing_from = int(t) + 1
    while True:
        k += 1
        magnitude *= t / k      # exactly t^k / k!
        total += -magnitude if k % 2 else magnitude
        if k % 2:
            last_odd = total
        else:
            last_even = total
        if magnitude <= tol and k >= decreasing_from:
            break
        if k > 1_000_000:
            raise RuntimeError("exp enclosure failed to converge")
    assert last_odd is not None and last_even is not None
    if last_odd > last_even:
        raise AssertionError("alternating bracket ordering violated")
    return last_odd, last_even


def _interval_mul(a: tuple[Fraction, Fraction],
                  b: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    """Exact outward interval product of positive rational intervals."""
    lo = a[0] * b[0]
    hi = a[1] * b[1]
    if hi < lo:
        raise AssertionError("interval product inverted")
    return lo, hi


def _interval_pow(base: tuple[Fraction, Fraction],
                  exponent: int) -> tuple[Fraction, Fraction]:
    """Interval power via exponentiation by squaring (exponent >= 0)."""
    result = (Fraction(1), Fraction(1))
    factor = base
    n = exponent
    while n:
        if n & 1:
            result = _interval_mul(result, factor)
        n >>= 1
        if n:
            factor = _interval_mul(factor, factor)
    return result


def lotka_interval(c_x: dict[int, Fraction], r: Fraction,
                   guard_bits: int = _BASE_GUARD_BITS
                   ) -> tuple[Fraction, Fraction]:
    """Certified enclosure of ``L(r) = sum c_x e^{-r x}`` for ``r >= 0``."""
    if r < 0:
        raise ValueError("lotka evaluation requires r >= 0")
    enclosure = exp_neg_enclosure(r, guard_bits)
    acc_lo = Fraction(0)
    acc_hi = Fraction(0)
    for x, cx in sorted(c_x.items()):
        powered = _interval_pow(enclosure, x)
        acc_lo += cx * powered[0]
        acc_hi += cx * powered[1]
    if acc_hi < acc_lo:
        raise AssertionError("Lotka enclosure inverted")
    return acc_lo, acc_hi


def certified_bracket(c_x: dict[int, Fraction],
                      rho: Fraction = SOLVER_RESOLUTION_RHO,
                      ) -> dict[str, Any]:
    """Registered Section 4 contract for one genotype-replicate schedule."""
    l0_exact = sum(c_x.values(), Fraction(0))
    certificate: dict[str, Any] = {
        "L0_exact": l0_exact,
        "rho": rho,
        "support": {str(x): fmt_rat(cx) for x, cx in sorted(c_x.items())},
    }
    if l0_exact <= 1:
        certificate["status"] = "SUBCRITICAL"
        return certificate

    guard_bits = _BASE_GUARD_BITS

    def evaluate(r: Fraction, bits: int) -> tuple[Fraction, Fraction]:
        return lotka_interval(c_x, r, bits)

    def sign_test(r: Fraction) -> str:
        """Certified classification of ``L(r)`` against 1.

        Returns ``"above"`` when the enclosure proves ``L(r) >= 1`` and
        ``"below"`` when it proves ``L(r) < 1``; escalates precision before
        conceding ambiguity, and raises only if the point sits within the
        enclosure width of the boundary at every escalation.
        """
        nonlocal guard_bits
        bits = guard_bits
        for _ in range(10):
            lo_val, hi_val = evaluate(r, bits)
            if lo_val >= 1:
                return "above"
            if hi_val < 1:
                return "below"
            bits += 32
        raise RuntimeError(
            f"could not certify sign of L at r={r}")

    # Locate a certified upper bound where L < 1 (monotone decreasing).
    upper = Fraction(1, 8)
    for _ in range(512):
        if sign_test(upper) == "below":
            break
        upper *= 2
    else:
        raise RuntimeError("no certified upper bracket found")

    lo = Fraction(0)
    if sign_test(lo) != "above":
        raise AssertionError("L(0) > 1 must be certifiable when supercritical")
    iterations = 0
    while upper - lo > rho:
        mid = (lo + upper) / 2
        if sign_test(mid) == "above":
            lo = mid
        else:
            upper = mid
        iterations += 1
        if iterations > 4096:
            raise RuntimeError("bisection failed to converge")
    certificate.update({
        "status": "SUPERCRITICAL",
        "r_lo": lo,
        "r_hi": upper,
        "width": upper - lo,
        "iterations": iterations,
        "guard_bits": guard_bits,
        "certified": "L(r_lo) >= 1 > L(r_hi) under directed enclosures",
    })
    return certificate


def bracket_midpoint(certificate: dict[str, Any]) -> Fraction | None:
    """Midpoint of a SUPERCRITICAL bracket; None when subcritical."""
    if certificate["status"] != "SUPERCRITICAL":
        return None
    return (certificate["r_lo"] + certificate["r_hi"]) / 2


def median_lower_middle(values: list[Fraction]) -> Fraction | None:
    """Registered even-k convention: lower middle of the sorted values."""
    if not values:
        return None
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) // 2]


def apply_decision_rule(replicate_outcomes: list[dict[int, dict[str, Any]]],
                        delta_min: Fraction = MIN_CONTRAST_DELTA_R,
                        min_complete_pairs: int = MIN_COMPLETE_PAIRS,
                        ) -> dict[str, Any]:
    """Registered Section 5 decision rule, applied exactly once.

    ``replicate_outcomes[i]`` maps genotype A value to its certificate dict
    (as produced by :func:`certified_bracket`).  Classes are exhaustive and
    mutually compatible exactly as registered: the pair-count/contrast class
    is one of ``DEGENERATE_REPLICATION``, ``ESTABLISHED_CONTRAST``,
    ``NO_ESTABLISHED_CONTRAST``; subcritical classes
    ``ONE_ARM_SUBCRITICAL`` / ``BOTH_SUBCRITICAL`` are reported alongside
    whenever at least 16 of a genotype's replicates are subcritical.
    """
    genotypes = sorted({g for outcome in replicate_outcomes
                        for g in outcome})
    if len(genotypes) != 2:
        raise ValueError("decision rule expects exactly two genotypes")

    per_genotype: dict[int, dict[str, Any]] = {}
    for g in genotypes:
        certs = [outcome[g] for outcome in replicate_outcomes]
        supers = [c for c in certs if c["status"] == "SUPERCRITICAL"]
        subs = len(certs) - len(supers)
        per_genotype[g] = {
            "subcritical_replicates": subs,
            "supercritical_replicates": len(supers),
            "subcritical_at_this_ecology": subs >= min_complete_pairs,
        }

    complete_pairs: list[tuple[Fraction, Fraction]] = []
    for outcome in replicate_outcomes:
        mids = []
        for g in genotypes:
            mid = bracket_midpoint(outcome[g])
            if mid is None:
                mids = None
                break
            mids.append(mid)
        if mids is not None:
            complete_pairs.append((mids[0], mids[1]))

    differences = [mid_b - mid_a for mid_a, mid_b in complete_pairs]
    median_difference = median_lower_middle(differences)
    details: dict[str, Any] = {
        "rule": "stage-7b2-preregistration section 5",
        "delta_min": delta_min,
        "min_complete_pairs": min_complete_pairs,
        "complete_pairs": len(complete_pairs),
        "median_paired_difference": median_difference,
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


def fmt_rat(value: Fraction) -> str:
    """Canonical exact serialisation of a rational."""
    return f"{value.numerator}/{value.denominator}"
