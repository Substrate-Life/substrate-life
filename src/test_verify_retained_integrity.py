"""Tests for src/verify_retained_integrity.py.

Pure-logic coverage uses synthetic tmp-tree fixtures; one smoke test runs the
real verifier against the live repo in read-only mode. No mechanic import, no
execution of anything evolutionary.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import tempfile
import unittest

import verify_retained_integrity as vri


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class ClassifyPinTests(unittest.TestCase):
    def _meta(self, data: bytes) -> dict:
        return {"bytes": len(data), "sha256": digest(data)}

    def test_exact(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            data = b"retained bytes"
            (root / "a.bin").write_bytes(data)
            verdict, detail = vri.classify_pin(root, "a.bin", self._meta(data))
            self.assertEqual(verdict, "EXACT")
            self.assertIn("byte-exact", detail)

    def test_missing(self):
        with tempfile.TemporaryDirectory() as td:
            verdict, _ = vri.classify_pin(
                pathlib.Path(td), "gone.bin", {"bytes": 3, "sha256": "00"}
            )
            self.assertEqual(verdict, "MISSING")

    def test_drift_on_plain_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            (root / "a.bin").write_bytes(b"changed content")
            verdict, detail = vri.classify_pin(
                root, "a.bin", self._meta(b"original content")
            )
            self.assertEqual(verdict, "DRIFT")
            self.assertIn("sha mismatch", detail)

    def test_pure_append_accepted_for_debate_log_only(self):
        prefix = b"frozen debate-log prefix\n"
        meta = {"bytes": len(prefix), "sha256": digest(prefix)}
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            rel = "docs/stage-8-debate-log.md"
            (root / rel).parent.mkdir(parents=True)
            (root / rel).write_bytes(prefix + b"\n## Round 9 appendix\n")
            verdict, detail = vri.classify_pin(root, rel, meta)
            self.assertEqual(verdict, "PURE_APPEND")
            self.assertIn("lawfully appended", detail)

    def test_pure_append_rule_survives_absolute_path_input(self):
        """Defensive: the same file addressed by absolute path must still be
        recognised under the pure-append rule."""
        prefix = b"frozen debate-log prefix\n"
        meta = {"bytes": len(prefix), "sha256": digest(prefix)}
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            abs_target = root / "docs" / "stage-8-debate-log.md"
            abs_target.parent.mkdir(parents=True)
            abs_target.write_bytes(prefix + b"\n## Round 9 appendix\n")
            verdict, _ = vri.classify_pin(root, str(abs_target), meta)
            self.assertEqual(verdict, "PURE_APPEND")

    def test_prefix_alteration_rejected_even_for_debate_log(self):
        prefix = b"frozen debate-log prefix\n"
        meta = {"bytes": len(prefix), "sha256": digest(prefix)}
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            rel = "docs/stage-8-debate-log.md"
            (root / rel).parent.mkdir(parents=True)
            tampered_head = b"TAMPERED debate-log prefix\n"
            tampered = tampered_head + b"x" * (len(prefix) - len(tampered_head))
            (root / rel).write_bytes(tampered + b"\n## Round 9 appendix\n")
            verdict, detail = vri.classify_pin(root, rel, meta)
            self.assertEqual(verdict, "DRIFT")
            self.assertIn("alteration, not append", detail)

    def test_append_rule_not_extended_to_other_paths(self):
        """Negative control: a drifted non-debate-log file must never be
        excused by the pure-append rule."""
        data = b"schema text v1"
        meta = {"bytes": len(data), "sha256": digest(data)}
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            (root / "schema.md").write_bytes(data + b"\nextra line\n")
            verdict, _ = vri.classify_pin(root, "schema.md", meta)
            self.assertEqual(verdict, "DRIFT")


class InventoryCloseTests(unittest.TestCase):
    def test_close_detects_extra_and_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            mdir_rel = "results/ret"
            mdir = root / mdir_rel
            mdir.mkdir(parents=True)
            mp_rel = f"{mdir_rel}/pre-execution-manifest.json"
            mp = root / mp_rel
            pinned_rel = f"{mdir_rel}/raw.json"
            out_rel = f"{mdir_rel}/reduced.json"
            for rel in (mp_rel, pinned_rel, out_rel):
                (root / rel).write_bytes(b"x")
            manifest = {
                "files": {pinned_rel: {"bytes": 1, "sha256": digest(b"x")}},
                "first_retained_outputs": {"raw": None, "reduced": out_rel},
            }
            extra, missing = vri.inventory_close(root, mp_rel, manifest)
            self.assertEqual(extra, [])
            self.assertEqual(missing, [])

            # an undeclared file appears -> extra
            (mdir / "smuggled.json").write_bytes(b"y")
            # a declared file disappears -> missing
            (root / out_rel).unlink()
            extra, missing = vri.inventory_close(root, mp_rel, manifest)
            self.assertEqual(extra, [f"{mdir_rel}/smuggled.json"])
            self.assertEqual(missing, [out_rel])

    def test_known_outputs_count_as_expected_members(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            mp_rel = "results/ret/pre-execution-manifest.json"
            (root / mp_rel).parent.mkdir(parents=True)
            (root / mp_rel).write_bytes(b"x")
            (root / "results/ret/legacy-output.json").write_bytes(b"o")
            manifest = {"files": {}, "first_retained_outputs": {}}
            # without declaring the legacy output it is EXTRA
            extra, _ = vri.inventory_close(root, mp_rel, manifest)
            self.assertEqual(extra, ["results/ret/legacy-output.json"])
            # declared via known_outputs -> closed
            extra, missing = vri.inventory_close(
                root, mp_rel, manifest, known_outputs=("legacy-output.json",)
            )
            self.assertEqual((extra, missing), ([], []))

    def test_declared_outputs_outside_retained_dir_are_not_local_pins(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            mp_rel = "results/ret/pre-execution-manifest.json"
            (root / mp_rel).parent.mkdir(parents=True)
            (root / mp_rel).write_bytes(b"x")
            manifest = {
                "files": {},
                "first_retained_outputs": {
                    "raw": "docs/somewhere-else.json",
                    "reduced": None,
                },
            }
            extra, missing = vri.inventory_close(root, mp_rel, manifest)
            self.assertEqual((extra, missing), ([], []))


class GitDoorTests(unittest.TestCase):
    def test_doors_report_moved_paths_and_count(self):
        """Synthetic git-free check: doors() on a repo without the base commit
        must FAIL (never silently pass)."""
        with tempfile.TemporaryDirectory() as td:
            ok, detail = vri.doors(pathlib.Path(td), "deadbeef", 8)
            self.assertFalse(ok)
            self.assertIn("not found", detail)


class SyncTests(unittest.TestCase):
    """S1 sync-check coverage: fail-loud on unknown refs, pass only on
    genuine equality, report behind/ahead counts on mismatch."""

    @staticmethod
    def _init_repo(root: pathlib.Path):
        def g(*args: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                ["git", "-C", str(root), *args], capture_output=True, text=True
            )

        r = g("init", "-q")
        assert r.returncode == 0, r.stderr
        g("config", "user.email", "t@example.invalid")
        g("config", "user.name", "t")
        r = g("commit", "--allow-empty", "-m", "c0")
        assert r.returncode == 0, r.stderr
        return g

    def test_unknown_refs_fail_loudly(self):
        """Git-free tmp dir: sync must FAIL, never silently pass."""
        with tempfile.TemporaryDirectory() as td:
            ok, detail = vri.sync(pathlib.Path(td))
            self.assertFalse(ok)
            self.assertIn("unknown", detail)

    def test_equal_refs_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            g = self._init_repo(root)
            r = g("update-ref", "refs/remotes/origin/main", "HEAD")
            self.assertEqual(r.returncode, 0, r.stderr)
            ok, detail = vri.sync(root)
            self.assertTrue(ok, detail)
            self.assertIn("==", detail)

    def test_mismatch_fails_with_behind_ahead_counts(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            g = self._init_repo(root)
            g("update-ref", "refs/remotes/origin/main", "HEAD")
            r = g("commit", "--allow-empty", "-m", "c1-unpushed")
            self.assertEqual(r.returncode, 0, r.stderr)
            ok, detail = vri.sync(root)
            self.assertFalse(ok)
            self.assertIn("!=", detail)
            self.assertIn("0/1", detail)


class RealRepoSmoke(unittest.TestCase):
    def test_live_repo_passes_all_mechanical_checks(self):
        # T1 excluded: this suite may run before the verifier's own commit,
        # when its files are legitimately untracked; the tracked-file
        # invariant is asserted separately below.
        ok, lines = vri.verify(with_auditors=False, include_tree_check=False)
        self.assertTrue(ok, "\n".join(lines))
        self.assertTrue(
            lines[-1].startswith("VERIFY_RETAINED_INTEGRITY: ALL CHECKS PASS")
        )
        # The summary fraction must count only PASS/FAIL check lines --
        # never detail/info emissions interleaved in the output.
        n_flagged = sum(
            1
            for ln in lines
            if ln.startswith("[PASS]") or ln.startswith("[FAIL]")
        )
        self.assertIn(f"({n_flagged}/{n_flagged})", lines[-1])
        joined = "\n".join(lines)
        self.assertIn("P2 pins [stage7b-signed-bracket]", joined)
        self.assertIn("P2 pins [stage8-alpha-evolution-paired]", joined)
        # S1 runs outside the T1 guard so this smoke covers it.
        self.assertIn("S1 sync", joined)
        # The pure-append info line must carry the debate log's current size.
        self.assertRegex(joined, r"info: docs/stage-8-debate-log\.md: current size \d+ B")

    def test_live_repo_has_no_tracked_file_modifications(self):
        ok, detail = vri.tree_clean(vri.REPO_ROOT, strict=False)
        self.assertTrue(ok, detail)


if __name__ == "__main__":
    unittest.main()
