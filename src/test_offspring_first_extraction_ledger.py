"""Regression tests for the normal-scheduler first-extraction ledger."""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trace_offspring_first_extraction import trace


class OffspringFirstExtractionLedgerTests(unittest.TestCase):
    def test_below_twenty_reads_but_does_not_extract(self):
        for label, extent in (("FULL", 256), ("HALF", 128)):
            row = trace(label, extent, 19.9)
            self.assertTrue(row["valid_read"])
            self.assertFalse(row["reached_extraction"])
            self.assertEqual(row["death_cause"], "reserve exhausted")

    def test_literal_twenty_reaches_extraction_only_at_float_boundary(self):
        below = math.nextafter(20.0, -math.inf)
        above = math.nextafter(20.0, math.inf)
        for label, extent in (("FULL", 256), ("HALF", 128)):
            self.assertFalse(trace(label, extent, below)["reached_extraction"])
            at_boundary = trace(label, extent, 20.0)
            self.assertTrue(at_boundary["valid_read"])
            self.assertTrue(at_boundary["reached_extraction"])
            self.assertIsNone(at_boundary["death_cause"])
            self.assertTrue(trace(label, extent, above)["reached_extraction"])


if __name__ == "__main__":
    unittest.main()
