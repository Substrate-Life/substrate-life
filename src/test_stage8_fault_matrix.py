"""Stage 8 fault-injection matrix re-parameterised onto the kernel subclass.

Registered implementation-window work of
``docs/stage-8-alpha-evolution-preregistration.md`` section 7(1): the
carried Stage 7B1 section 2.4 fault-injection semantics are exercised
against ``Stage8Population.divide_publish`` — the verbatim-copied
transaction with the registered M-stage substitution — with the added
registered assertion that **consumed kernel draws stay consumed across
every rollback**.  The frozen ``test_stage7b1_mechanics`` module is not
edited and still covers the frozen class; this matrix proves the
subclass preserves every carried rollback property while adding the
kernel's stream behaviour.

For each injection boundary the post-rollback state must satisfy:

- vacancy reservation released to zero; no partial child in census,
  organism registry, or child-memory bucket; admitted-birth count
  unchanged;
- gestation released exactly once (bout discarded per architecture §7);
- provisional ``P`` refunded by the exact stored Fraction whenever it had
  been provisionally debited, so parent ``S`` and ``R`` are bit-identical
  to their pre-attempt values in every case;
- exactly one ``divide_failed`` record carrying the boundary's stage;
- reserve, census, memory, packet, and vacancy ledgers all closed (the
  rollback path itself asserts closure; the tests additionally verify
  the identities directly);
- kernel draws consumed: zero before the M decision point
  (``post_V``), one Bernoulli + one step from ``mid_M`` onward.

All arithmetic observed here is exact ``fractions.Fraction``.
"""

from __future__ import annotations

from fractions import Fraction
import unittest

from stage7b1_mechanics import FaultInjector, InjectedFault
from test_stage8_kernel import (
    ScriptedStream,
    events_by_name,
    prepare_bout,
    ready_population,
)

_BOUNDARIES = ("post_V", "mid_M", "post_M", "mid_R", "post_R", "mid_P",
               "pre_C")

_STAGE_OF_BOUNDARY = {
    "post_V": "V", "mid_M": "M", "post_M": "M", "mid_R": "R",
    "post_R": "R", "mid_P": "P", "pre_C": "P",
}


def _memory_totals(population) -> dict:
    return population.memory.totals()


class Stage8FaultMatrixTests(unittest.TestCase):

    def _attempt_with_fault(self, boundary: str):
        """Fresh fixture; scripted mutate(+3); inject at ``boundary``."""
        population, member = ready_population()
        parent = member.organism
        s_before = Fraction(parent.s)
        r_before = Fraction(parent.r)
        live_before = len(population.members)
        births_before = population.admitted_births
        population.mutation_rng = ScriptedStream([0.0], [2])
        injector = FaultInjector()
        injector.arm(boundary)
        with self.assertRaises(InjectedFault) as caught:
            population.divide_publish(member, injector)
        self.assertEqual(caught.exception.boundary, boundary)
        self.assertEqual(injector.fired_at, boundary)
        return (population, member, s_before, r_before, live_before,
                births_before)

    def _assert_rollback_state(self, population, member, s_before, r_before,
                               live_before, births_before, boundary):
        parent = member.organism
        # Exact refund / no-debit: parent reserves bit-identical.
        self.assertEqual(Fraction(parent.s), s_before)
        self.assertEqual(Fraction(parent.r), r_before)
        # No partial child anywhere; counters unchanged.
        attempted_child_id = f"org-{live_before + 1}"
        self.assertEqual(len(population.members), live_before)
        self.assertEqual(population.admitted_births, births_before)
        self.assertEqual(population.vacancy_reserved, 0)
        self.assertEqual(
            population.memory.child_reserved.get(attempted_child_id), None)
        self.assertNotIn(attempted_child_id, population.members)
        # Bout discarded exactly once: gestation bucket empty for parent.
        self.assertNotIn(parent.organism_id, population.memory.gestation)
        # Exactly one failure record with the boundary's stage.
        failures = events_by_name(population, "divide_failed")
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["stage"], _STAGE_OF_BOUNDARY[boundary])
        self.assertEqual(failures[0]["reason"], "FAULT_INJECTED")
        # No birth was admitted; no decision became a child genome change.
        self.assertEqual(events_by_name(population, "birth_admitted"), [])
        # Ledgers closed right now (the rollback already asserted closure
        # internally; verify the identities independently).
        self.assertTrue(population.reserve_closure()["closed"])
        self.assertTrue(population.census_closure()["closed"])
        self.assertEqual(
            sum(_memory_totals(population).values()),
            population.memory.initial_pool)
        # Kernel draws retained per boundary position.
        expected_draws = 0 if boundary == "post_V" else 2
        self.assertEqual(population.mutation_draws, expected_draws)

    def test_fault_post_v(self):
        self._assert_rollback_state(
            *self._attempt_with_fault("post_V"), boundary="post_V")

    def test_fault_mid_m(self):
        self._assert_rollback_state(
            *self._attempt_with_fault("mid_M"), boundary="mid_M")

    def test_fault_post_m(self):
        self._assert_rollback_state(
            *self._attempt_with_fault("post_M"), boundary="post_M")

    def test_fault_mid_r(self):
        self._assert_rollback_state(
            *self._attempt_with_fault("mid_R"), boundary="mid_R")

    def test_fault_post_r(self):
        self._assert_rollback_state(
            *self._attempt_with_fault("post_R"), boundary="post_R")

    def test_fault_mid_p_refunds_provisional_p(self):
        """P debited before mid_P must be refunded by the exact Fraction.

        The shared assertion helper already checks parent S/R are
        bit-identical to their pre-attempt values and that every ledger
        closes; for mid_P/pre_C that is only possible if the exact stored
        Fraction was restored, not recomputed from current alpha.
        """
        state = self._attempt_with_fault("mid_P")
        self._assert_rollback_state(*state, boundary="mid_P")

    def test_fault_pre_c_refunds_provisional_p(self):
        state = self._attempt_with_fault("pre_C")
        self._assert_rollback_state(*state, boundary="pre_C")


if __name__ == "__main__":
    unittest.main()
