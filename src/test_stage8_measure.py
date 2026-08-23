"""Registered Stage 8 measurement-layer test matrix.

Covers ``stage8_alpha_measure``: exact census-snapshot arithmetic,
checkpoint-loop equivalence with the frozen ``run_window`` semantics
(snapshots observe, never mutate), direction-class boundaries, tercile
split rule, kernel reconciliation identities on synthetic ledgers,
bit-exact stream replay, and the genome-freeze audit.

All ledger arithmetic observed here is exact ``fractions.Fraction``.
"""

from __future__ import annotations

from fractions import Fraction
import json
import random

import unittest

from stage7b2_population import run_window
from stage8_alpha_measure import (
    CHECKPOINT_TICKS,
    alpha_terciles,
    births_by_ancestry,
    census_snapshot,
    direction_class,
    genome_freeze_audit,
    kernel_reconciliation,
    replay_stream,
    run_window_with_checkpoints,
)
from stage8_population import (
    FROZEN_D,
    FROZEN_T,
    REGISTERED_MUTATION_PROB,
    REGISTERED_STEP_SUPPORT,
    mutation_seed,
    registered_stage8_population,
)


def _short_population(seed: int = 20284617, window: int = 6):
    """Registered configuration scaled to a short window for speed."""
    return registered_stage8_population(seed, window_ticks=window)


def _decision(stream_position: int, mutated: bool, delta: int | None,
              child_id: str, parent_a: int = 153) -> dict:
    if mutated and delta is not None:
        child_a = min(255, max(0, parent_a + delta))
    else:
        child_a = parent_a
    return {
        "event": "mutation_decision",
        "tick": 1,
        "phase": "mutation",
        "parent_id": "org-0",
        "child_id": child_id,
        "parent_a": parent_a,
        "mutated": mutated,
        "delta": delta,
        "child_a": child_a,
        "stream_position": stream_position,
        "draws_consumed": 2 if mutated else 1,
    }


def _birth(child_id: str, a: int = 153) -> dict:
    return {
        "event": "birth_admitted", "tick": 1, "parent_id": "org-0",
        "child_id": child_id, "provision": "1/1",
        "ancestry_id": "F0",
        "genotype_hash": f"{a}-{FROZEN_T}-{FROZEN_D}",
        "shadow_would_admit": True,
        "inherited_a_over_d": f"{a}/{FROZEN_D}",
        "inherited_t_over_d": f"{FROZEN_T}/{FROZEN_D}",
    }


class CensusSnapshotTests(unittest.TestCase):

    def test_founder_alpha_is_exactly_three_fifths(self):
        population = _short_population()
        snapshot = census_snapshot(population, tick=0)
        # Carried founder block: 6 founders (3 per genotype) in a
        # capacity-48 census that grows through vacancy-capture births.
        self.assertEqual(snapshot["n_live"], 6)
        # mean A = (3*102 + 3*204)/6 = 153 => alpha_mean = 153/255 = 3/5.
        self.assertEqual(Fraction(snapshot["alpha_mean"]),
                         Fraction(153, 255))
        self.assertEqual(snapshot["distinct_A_values"], 2)
        self.assertEqual(snapshot["T_values_present"], [128])
        self.assertEqual(snapshot["D_values_present"], [255])
        self.assertEqual(sum(snapshot["histogram_A"].values()), 6)
        self.assertEqual(sorted(snapshot["live_by_ancestry"]),
                         ["F0", "F1", "F2", "F3", "F4", "F5"])

    def test_snapshot_reads_without_mutating(self):
        population = _short_population()
        before = json.dumps(population.event_log, sort_keys=True,
                            default=str)
        draws_before = population.mutation_draws
        rng_state = population.mutation_rng.getstate()
        census_snapshot(population, tick=0)
        self.assertEqual(
            json.dumps(population.event_log, sort_keys=True, default=str),
            before)
        self.assertEqual(population.mutation_draws, draws_before)
        self.assertEqual(population.mutation_rng.getstate(), rng_state)


class CheckpointLoopEquivalenceTests(unittest.TestCase):

    def test_matches_frozen_run_window_bit_exactly(self):
        """Snapshots observe only; execution stays bit-identical."""
        control = _short_population(seed=20293311)
        instrumented = _short_population(seed=20293311)
        control_result = run_window(control)
        instrumented_result = run_window_with_checkpoints(
            instrumented, tuple(range(1, control.window_ticks + 1)))
        self.assertEqual(control_result["classification"],
                         instrumented_result["classification"])
        self.assertEqual(control_result["ticks_completed"],
                         instrumented_result["ticks_completed"])
        self.assertEqual(len(instrumented_result["snapshots"]),
                         control.window_ticks)
        self.assertEqual(
            json.dumps(control.event_log, sort_keys=True, default=str),
            json.dumps(instrumented.event_log, sort_keys=True,
                       default=str))
        self.assertEqual(control.admitted_births,
                         instrumented.admitted_births)
        self.assertEqual(control.mutation_draws,
                         instrumented.mutation_draws)
        self.assertEqual(len(control.members), len(instrumented.members))

    def test_registered_checkpoint_schedule(self):
        self.assertEqual(CHECKPOINT_TICKS,
                         tuple(range(120, 2401, 120)))
        self.assertEqual(len(CHECKPOINT_TICKS), 20)


class DirectionClassTests(unittest.TestCase):

    def test_boundaries(self):
        self.assertEqual(direction_class("161/255"), "mover_up")
        self.assertEqual(direction_class("145/255"), "mover_down")
        self.assertEqual(direction_class("153/255"), "non_mover")
        # Exactly at the floor counts as a mover (registered >= / <=):
        # alpha_ref + 8/255 = 161/255, - 8/255 = 145/255.
        self.assertEqual(direction_class("161/255"), "mover_up")
        self.assertEqual(direction_class("145/255"), "mover_down")
        # One lattice unit inside the floor does not.
        self.assertEqual(direction_class("160/255"), "non_mover")
        self.assertEqual(direction_class("146/255"), "non_mover")


class TercileTests(unittest.TestCase):

    def test_exact_thirds(self):
        snapshot = {"histogram_A": {"1": 2, "2": 2, "3": 2}}
        result = alpha_terciles(snapshot)
        self.assertEqual(result["n_live"], 6)
        self.assertEqual(result["terciles"]["low"], {
            "size": 2, "min_A": 1, "max_A": 1, "mean_A": "1/1"})
        self.assertEqual(result["terciles"]["middle"]["mean_A"], "2/1")
        self.assertEqual(result["terciles"]["high"]["mean_A"], "3/1")

    def test_remainder_accrues_to_upper_terciles(self):
        snapshot = {"histogram_A": {"10": 3, "20": 3, "30": 1}}
        result = alpha_terciles(snapshot)
        sizes = [result["terciles"][k]["size"]
                 for k in ("low", "middle", "high")]
        self.assertEqual(sizes, [2, 2, 3])

    def test_empty_census(self):
        self.assertIsNone(alpha_terciles({"histogram_A": {}})["terciles"])


class KernelReconciliationTests(unittest.TestCase):

    def _clean_ledger(self) -> list[dict]:
        return [
            _decision(0, True, +3, "org-10"),
            _decision(2, False, None, "org-11"),
            _decision(3, True, -4, "org-12"),
            _birth("org-10", 156), _birth("org-11", 153),
            _birth("org-12", 149),
        ]

    def test_clean_chain_passes(self):
        report = kernel_reconciliation(self._clean_ledger())
        self.assertTrue(report["passes"])
        self.assertEqual(report["decision_records"], 3)
        self.assertEqual(report["admitted_births"], 3)
        self.assertEqual(report["draws_total"], 5)

    def test_missing_stage_m_record_detected(self):
        ledger = self._clean_ledger()
        ledger[3] = _birth("org-99", 153)  # admitted without a decision
        report = kernel_reconciliation(ledger)
        self.assertFalse(report["passes"])
        self.assertTrue(any("org-99" in p for p in report["problems"]))

    def test_bad_clamp_detected(self):
        record = _decision(0, True, +3, "org-10", parent_a=250)
        record["child_a"] = 254  # true clamp is 253
        ledger = [record, _birth("org-10", 254)]
        report = kernel_reconciliation(ledger)
        self.assertFalse(report["passes"])

    def test_off_support_delta_detected(self):
        record = _decision(0, True, +5, "org-10")
        ledger = [record, _birth("org-10", 158)]
        report = kernel_reconciliation(ledger)
        self.assertFalse(report["passes"])
        self.assertTrue(any("off-support" in p
                            for p in report["problems"]))

    def test_no_mutation_must_not_change_a(self):
        record = _decision(0, False, None, "org-10")
        record["child_a"] = 154
        ledger = [record, _birth("org-10", 154)]
        report = kernel_reconciliation(ledger)
        self.assertFalse(report["passes"])

    def test_supply_identity_with_memory_failures(self):
        ledger = self._clean_ledger()
        ledger.append({"event": "divide_failed", "tick": 2,
                       "organism_id": "org-1", "stage": "R",
                       "reason": "CHILD_MEMORY_UNAVAILABLE"})
        ledger.append(_decision(5, False, None, "org-15"))  # failed at R
        report = kernel_reconciliation(ledger)
        self.assertTrue(report["passes"])
        self.assertEqual(report["memory_unavailable_failures"], 1)


class ReplayStreamTests(unittest.TestCase):

    def test_derivation_replays_recorded_chain(self):
        seed = 20293311
        stream = random.Random(mutation_seed(seed))
        chain = []
        position = 0
        for _ in range(200):
            mutated = stream.random() < float(REGISTERED_MUTATION_PROB)
            delta = None
            if mutated:
                delta = REGISTERED_STEP_SUPPORT[
                    stream.randrange(len(REGISTERED_STEP_SUPPORT))]
            chain.append({"stream_position": position, "mutated": mutated,
                          "delta": delta,
                          "draws_consumed": 2 if mutated else 1})
            position += 2 if mutated else 1
        report = replay_stream(seed, chain)
        self.assertTrue(report["passes"])
        self.assertEqual(report["draws_replayed"], position)

    def test_tampered_chain_fails(self):
        seed = 20293311
        chain = [{"stream_position": 0, "mutated": True, "delta": +1,
                  "draws_consumed": 2}]
        report = replay_stream(seed, chain)
        if report["passes"]:
            # Only possible if the genuine first draw happens to mutate to
            # +1; force an inconsistency instead.
            chain[0]["delta"] = -chain[0]["delta"]
            report = replay_stream(seed, chain)
        self.assertFalse(report["passes"])


class GenomeFreezeAuditTests(unittest.TestCase):

    def test_frozen_genome_stream_passes(self):
        ledger = [
            {"event": "founder_registered", "tick": 0,
             "organism_id": "org-0", "ancestry_id": "F0",
             "a_over_d": "102/255", "t_over_d": "128/255"},
            _birth("org-10", 156),
        ]
        report = genome_freeze_audit(ledger)
        self.assertTrue(report["passes"])
        self.assertEqual(report["records_checked"], 2)

    def test_non_frozen_t_detected(self):
        ledger = [_birth("org-10", 153)]
        ledger[0]["inherited_t_over_d"] = "127/255"
        report = genome_freeze_audit(ledger)
        self.assertFalse(report["passes"])
        self.assertEqual(len(report["violations"]), 1)

    def test_out_of_lattice_a_detected(self):
        ledger = [_birth("org-10", 256)]
        report = genome_freeze_audit(ledger)
        self.assertFalse(report["passes"])


class BirthsByAncestryTests(unittest.TestCase):

    def test_counts_by_tag(self):
        ledger = [_birth("org-10"), _birth("org-11")]
        ledger[1]["ancestry_id"] = "F3"
        ledger.append({"event": "divide_failed", "reason": "NO_VACANCY"})
        self.assertEqual(births_by_ancestry(ledger), {"F0": 1, "F3": 1})


if __name__ == "__main__":
    unittest.main()
