"""Tests for the continuous-compile loaded capture manager."""

from __future__ import annotations

from pathlib import Path
import unittest

from run_scheduler_latency_loaded_capture import compile_command


class LoadedCaptureManagerTests(unittest.TestCase):
    def test_compile_command_is_single_threaded_for_each_worker(self):
        command = compile_command(Path("src"))
        self.assertEqual(
            command[1:],
            ["-m", "compileall", "-q", "-f", "-j", "1", "src"],
        )


if __name__ == "__main__":
    unittest.main()
