"""Executable-path regression for the stochastic calibration runner."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class StochasticRunnerSmokeTests(unittest.TestCase):
    def test_main_uses_instantiation_rate_schema(self):
        script = Path(__file__).with_name("derive_stochastic_efficiency.py")
        with tempfile.TemporaryDirectory() as output_dir:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--isolated-trials", "2",
                    "--mono-seeds", "2",
                    "--cycles", "1",
                    "--burn-cycles", "0",
                    "--output-prefix", "runner-schema-smoke",
                    "--output-dir", output_dir,
                ],
                cwd=script.parent,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            summary_path = Path(output_dir) / "runner-schema-smoke-summary.json"
            result = json.loads(summary_path.read_text())
            heuristic = result["heuristic"]
            self.assertIn("delta_instantiation_rate", heuristic)
            self.assertNotIn("delta_birth_rate", heuristic)
            for row in result["summaries"]:
                self.assertIn("instantiations_per_organism_tick", row)


if __name__ == "__main__":
    unittest.main()
