"""Stage 8 alpha-evolution measurement: exact estimators and kernel audits.

Pure functions implementing the registered endpoint/co-report definitions of
``docs/stage-8-alpha-evolution-preregistration.md`` (sections 3-4) and the
section 6 G1/G3 audit primitives, as deterministic functions of the event
ledger plus a live population snapshot.  Every allocation quantity is an
exact ``fractions.Fraction``; kernel draws are integer-lattice operations on
the dedicated stream and never feed approximations into any ledger.

Registered definitions implemented here:

- **Terminal mean allocation** ``ᾱ_end`` (primary per-replicate endpoint):
  equal weight ``mean(A/255)`` over live members at the tick-``W`` census
  close -- active and recoverable-depleted/stalled alike; state composition
  co-reported (section 4).
- **Trajectory checkpoints** ``ᾱ`` at ticks 120, 240, ..., 2400 (20 points),
  same estimator (co-report).
- **Direction classes** (applied by the source-frozen reducer, not here):
  mover-up iff ``ᾱ_end - α_ref >= Δα_floor``; mover-down iff
  ``<= -Δα_floor``; ``Δα_floor = 8/255``, ``α_ref = 153/255``.
- **Kernel audit primitives** (section 6 G3): every admitted birth carries
  exactly one Stage-M decision record; recorded children satisfy
  ``0 <= A <= 255`` with ``T = 128``, ``D = 255`` genome-wide; replaying the
  documented stream derivation ``random.Random(hazard_seed * 1000003 + 7)``
  reproduces the recorded draw sequence bit-exactly.
- **Recruitment telemetry** (co-report, mediator-labelled, section 4): the
  carried 7B1 §6.2 mediator definitions plus births by founder ancestry and
  terminal-census α-tercile composition.  These are descriptive context;
  nothing here promotes them to endpoints.

No fitness, selection, optimum, ESS, causal, or external-validation claim is
made anywhere in this module.
"""

from __future__ import annotations

from fractions import Fraction
import random
from typing import Any

from stage7b1_mechanics import BufferOverflowError
from stage7b2_measure import fmt_rat, parse_rat
from stage7b2_population import Stage7B2Population
from stage8_population import (
    ALPHA_REF,
    DIRECTION_FLOOR_ALPHA,
    FROZEN_D,
    FROZEN_T,
    LATTICE_MAX,
    REGISTERED_STEP_SUPPORT,
    REGISTERED_MUTATION_PROB,
    REGISTERED_WINDOW_TICKS_STAGE8,
    mutation_seed,
)

#: Registered trajectory checkpoints: ᾱ at ticks 120, 240, ..., 2400.
CHECKPOINT_TICKS: tuple[int, ...] = tuple(
    range(120, REGISTERED_WINDOW_TICKS_STAGE8 + 1, 120))
assert len(CHECKPOINT_TICKS) == 20
assert CHECKPOINT_TICKS[-1] == REGISTERED_WINDOW_TICKS_STAGE8


# ---------------------------------------------------------------------------
# Census snapshot estimator (exact)
# ---------------------------------------------------------------------------


def census_snapshot(population: Stage7B2Population, tick: int) -> dict[str, Any]:
    """Exact terminal/checkpoint statistics over the live members.

    The primary estimator: ``ᾱ = mean(A/255)`` with equal weight over live
    members (active and stalled alike), returned as an exact Fraction
    serialisation plus the co-reported composition fields.
    """
    alphas = [member.organism.a for member in population.members.values()]
    states: dict[str, int] = {}
    ancestries: dict[str, int] = {}
    histogram: dict[str, int] = {}
    for member in population.members.values():
        state = member.state
        states[state] = states.get(state, 0) + 1
        ancestry = population.ancestry.get(
            member.organism.organism_id, "UNKNOWN")
        ancestries[ancestry] = ancestries.get(ancestry, 0) + 1
        key = str(member.organism.a)
        histogram[key] = histogram.get(key, 0) + 1
    n_live = len(alphas)
    total_a = Fraction(sum(alphas))
    mean_alpha = Fraction(total_a, 255 * n_live) if n_live else None
    return {
        "tick": tick,
        "n_live": n_live,
        "sum_A": str(total_a.numerator),
        "alpha_mean": fmt_rat(mean_alpha) if mean_alpha is not None else None,
        "distinct_A_values": len(set(alphas)),
        "histogram_A": dict(sorted(
            histogram.items(), key=lambda kv: int(kv[0]))),
        "states": dict(sorted(states.items())),
        "live_by_ancestry": dict(sorted(ancestries.items())),
        "T_values_present": sorted({
            member.organism.t for member in population.members.values()}),
        "D_values_present": sorted({
            member.organism.d for member in population.members.values()}),
    }


def run_window_with_checkpoints(
    population: Stage7B2Population,
    checkpoint_ticks: tuple[int, ...] = CHECKPOINT_TICKS,
) -> dict[str, Any]:
    """Run the window stepping tick-by-tick with registered snapshots.

    Verbatim execution semantics of the frozen ``run_window``
    (``BufferOverflowError`` -> ``INVALID_IMPLEMENTATION``; any other
    exception is an implementation bug and propagates) with one addition:
    immediately after the step that completes each registered checkpoint
    tick, a census snapshot is taken.  Snapshots observe live state only;
    they perform no mutation and consume no draws.
    """
    wanted = set(checkpoint_ticks)
    snapshots: dict[str, dict[str, Any]] = {}
    ticks_completed = 0
    try:
        for _ in range(population.window_ticks):
            population.step()
            ticks_completed += 1
            if ticks_completed in wanted:
                snapshot = census_snapshot(population, ticks_completed)
                snapshots[str(ticks_completed)] = snapshot
    except BufferOverflowError as error:
        return {
            "classification": "INVALID_IMPLEMENTATION",
            "reason": "BUFFER_OVERFLOW",
            "detail": str(error),
            "ticks_completed": ticks_completed,
            "snapshots": snapshots,
        }
    return {
        "classification": "COMPLETE",
        "ticks_completed": ticks_completed,
        "snapshots": snapshots,
    }


def terminal_snapshot(snapshots: dict[str, dict[str, Any]],
                      window_ticks: int) -> dict[str, Any]:
    """The snapshot at the window close; requires it to exist."""
    snapshot = snapshots.get(str(window_ticks))
    if snapshot is None:
        raise AssertionError(
            f"missing terminal census snapshot at tick {window_ticks}")
    return snapshot


# ---------------------------------------------------------------------------
# Kernel audit primitives (preregistration sections 3 and 6 G3)
# ---------------------------------------------------------------------------

_FROZEN_TD = f"{FROZEN_T}/{FROZEN_D}"


def _decisions(event_log: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in event_log
            if event.get("event") == "mutation_decision"]


def _births(event_log: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in event_log
            if event.get("event") == "birth_admitted"]


def genome_freeze_audit(event_log: list[dict[str, Any]]) -> dict[str, Any]:
    """Zero non-frozen T/D anywhere in the event stream (G1/G3 primitive).

    Scans every genotype-bearing record class -- ``founder_registered``,
    ``provision_committed``, ``birth_admitted`` -- and asserts the frozen
    pair ``(T, D) = (128, 255)`` and the legal lattice on ``A``.  This is
    the trait-isolation gate evidence: only ``A`` ever changes.
    """
    violations: list[dict[str, Any]] = []
    checked = 0
    for event in event_log:
        kind = event.get("event")
        if kind == "founder_registered":
            a = int(event["a_over_d"].split("/")[0])
            td = event["t_over_d"]
            checked += 1
            if td != _FROZEN_TD or not 0 <= a <= LATTICE_MAX:
                violations.append({"event": kind, "tick": event.get("tick"),
                                   "organism_id": event["organism_id"],
                                   "t_over_d": td, "a": a})
        elif kind == "provision_committed":
            # The ONLY genotype-bearing admission record: carries the exact
            # inherited (A, T, D) triple.  The paired birth_admitted record
            # on the frozen 7B1 stack is deliberately telemetry-hash-only
            # and must not be scanned for these fields.
            a = int(event["inherited_a_over_d"].split("/")[0])
            td = event["inherited_t_over_d"]
            checked += 1
            if td != _FROZEN_TD or not 0 <= a <= LATTICE_MAX:
                violations.append({"event": kind, "tick": event.get("tick"),
                                   "child_id": event["child_id"],
                                   "t_over_d": td, "a": a})
    return {
        "records_checked": checked,
        "violations": violations,
        "frozen_td": _FROZEN_TD,
        "passes": not violations and checked > 0,
    }


def kernel_reconciliation(event_log: list[dict[str, Any]]) -> dict[str, Any]:
    """Every admitted birth carries exactly one Stage-M record (G3).

    Checks, over one replicate's event ledger:

    - every ``birth_admitted`` child id appears in exactly one
      ``mutation_decision`` record;
    - every decision record is kernel-valid: parent/child ``A`` inside the
      lattice; ``delta`` present iff ``mutated``; ``delta`` in the registered
      support when present; ``child_a == clamp(parent_a + delta, 0, 255)``
      when mutating and ``child_a == parent_a`` otherwise; declared draw
      consumption matches the kernel (two draws when mutated, one otherwise);
    - stream positions form the exact contiguous chain
      ``pos_{k+1} = pos_k + draws_k`` starting at 0 (draws are consumed once
      per published-birth candidate and retained across rollbacks);
    - the supply identity holds: ``#decisions ==
      #admitted_births + #CHILD_MEMORY_UNAVAILABLE failures`` (candidates
      failing at stage V consume no draws and emit no record).
    """
    decisions = _decisions(event_log)
    births = _births(event_log)
    memory_failures = sum(
        1 for event in event_log
        if event.get("event") == "divide_failed"
        and event.get("reason") == "CHILD_MEMORY_UNAVAILABLE")
    problems: list[str] = []

    decision_by_child: dict[str, list[dict[str, Any]]] = {}
    for record in decisions:
        decision_by_child.setdefault(record["child_id"], []).append(record)
    for birth in births:
        found = decision_by_child.get(birth["child_id"], [])
        if len(found) != 1:
            problems.append(
                f"birth {birth['child_id']}: {len(found)} Stage-M records")
    extra = sorted(
        set(decision_by_child) - {b["child_id"] for b in births})
    if len(extra) != memory_failures:
        problems.append(
            f"{len(extra)} decisions without admission vs "
            f"{memory_failures} CHILD_MEMORY_UNAVAILABLE failures")

    expected_position = 0
    support = set(REGISTERED_STEP_SUPPORT)
    for index, record in enumerate(decisions):
        parent_a = int(record["parent_a"])
        child_a = int(record["child_a"])
        mutated = bool(record["mutated"])
        delta = record["delta"]
        consumed = int(record["draws_consumed"])
        if not 0 <= parent_a <= LATTICE_MAX or not 0 <= child_a <= LATTICE_MAX:
            problems.append(f"decision {index}: lattice violation")
        if mutated:
            if delta not in support:
                problems.append(f"decision {index}: delta {delta} off-support")
            elif child_a != min(LATTICE_MAX,
                                max(0, parent_a + int(delta))):
                problems.append(f"decision {index}: child != clamped parent+delta")
            if consumed != 2:
                problems.append(f"decision {index}: mutated draw count {consumed}")
        else:
            if delta is not None:
                problems.append(f"decision {index}: no-mutation carries delta")
            if child_a != parent_a:
                problems.append(f"decision {index}: no-mutation changed A")
            if consumed != 1:
                problems.append(
                    f"decision {index}: unmutated draw count {consumed}")
        if int(record["stream_position"]) != expected_position:
            problems.append(
                f"decision {index}: position {record['stream_position']} "
                f"!= expected {expected_position}")
        expected_position += consumed

    return {
        "decision_records": len(decisions),
        "admitted_births": len(births),
        "memory_unavailable_failures": memory_failures,
        "draws_total": expected_position,
        "problems": problems,
        "passes": not problems,
    }


def replay_stream(hazard_seed: int,
                  decisions: list[dict[str, Any]]) -> dict[str, Any]:
    """Bit-exact replay of the documented stream derivation (G3).

    Reconstructs ``random.Random(hazard_seed * 1000003 + 7)`` and re-draws
    the Bernoulli/step sequence; every recorded decision must match the
    replayed draws exactly (float comparison of the same generator state,
    so 'bit-exact' here is literal).
    """
    stream = random.Random(mutation_seed(hazard_seed))
    mismatches: list[dict[str, Any]] = []
    position = 0
    p_mu = float(REGISTERED_MUTATION_PROB)
    support = REGISTERED_STEP_SUPPORT
    for index, record in enumerate(decisions):
        bernoulli = stream.random() < p_mu
        replayed_delta: int | None = None
        if bernoulli:
            replayed_delta = support[stream.randrange(len(support))]
        entry: dict[str, Any] = {"index": index}
        if bool(record["mutated"]) != bernoulli:
            entry["mutated"] = [record["mutated"], bernoulli]
        if record["delta"] != replayed_delta:
            entry["delta"] = [record["delta"], replayed_delta]
        if int(record["stream_position"]) != position:
            entry["stream_position"] = [record["stream_position"], position]
        consumed = 2 if bernoulli else 1
        if int(record["draws_consumed"]) != consumed:
            entry["draws_consumed"] = [record["draws_consumed"], consumed]
        if entry != {"index": index}:
            mismatches.append(entry)
        position += consumed
    return {
        "seed_derivation": f"random.Random({hazard_seed} * 1000003 + 7)",
        "records_replayed": len(decisions),
        "draws_replayed": position,
        "mismatches": mismatches,
        "passes": not mismatches,
    }


# ---------------------------------------------------------------------------
# Recruitment telemetry (co-report; mediator-labelled; never endpoints)
# ---------------------------------------------------------------------------


def births_by_ancestry(event_log: list[dict[str, Any]]) -> dict[str, int]:
    """Admitted births per immutable founder ancestry tag (descriptive)."""
    counts: dict[str, int] = {}
    for event in _births(event_log):
        ancestry = event["ancestry_id"]
        counts[ancestry] = counts.get(ancestry, 0) + 1
    return dict(sorted(counts.items()))


def alpha_terciles(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Terminal-census α-tercile composition (registered descriptive rule).

    Live members ordered by ascending ``A``; tercile boundaries at indices
    ``floor(n/3)`` and ``floor(2n/3)`` of the sorted vector (remainders
    accrue to upper terciles).  Per tercile: size, ``A`` range, exact mean
    ``A``.  Purely descriptive composition context.
    """
    histogram = {int(a): int(count) for a, count
                 in snapshot["histogram_A"].items()}
    sorted_alphas: list[int] = []
    for value in sorted(histogram):
        sorted_alphas.extend([value] * histogram[value])
    n = len(sorted_alphas)
    if n == 0:
        return {"rule": "boundaries at floor(n/3), floor(2n/3) ascending",
                "terciles": None}

    def _slice(low: int, high: int) -> dict[str, Any]:
        part = sorted_alphas[low:high]
        size = len(part)
        return {
            "size": size,
            "min_A": min(part),
            "max_A": max(part),
            "mean_A": fmt_rat(Fraction(sum(part), size)),
        }

    b1 = n // 3
    b2 = 2 * n // 3
    return {
        "rule": "boundaries at floor(n/3), floor(2n/3) ascending; "
                "remainders accrue to upper terciles",
        "n_live": n,
        "terciles": {
            "low": _slice(0, b1),
            "middle": _slice(b1, b2),
            "high": _slice(b2, n),
        },
    }


def direction_class(alpha_end_text: str) -> str:
    """Registered direction class of one eligible replicate (section 4).

    mover-up iff ``ᾱ_end - α_ref >= Δα_floor``; mover-down iff
    ``<= -Δα_floor``; otherwise ``non_mover``.  Classification only; the
    suite-level rule lives in the source-frozen reducer.
    """
    difference = parse_rat(alpha_end_text) - ALPHA_REF
    if difference >= DIRECTION_FLOOR_ALPHA:
        return "mover_up"
    if difference <= -DIRECTION_FLOOR_ALPHA:
        return "mover_down"
    return "non_mover"
