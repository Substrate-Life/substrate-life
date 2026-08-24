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


class AppendLedgerTests(unittest.TestCase):
    """L1 append-ledger coverage: the P2 pin proves only the debate log's
    frozen prefix, so ANY bytes behind it were previously unchecked -- even a
    same-length rewrite of the appended region passed every check. The ledger
    binds content: every recorded snapshot must stay a byte-exact prefix,
    snapshots must grow strictly monotonically, and the newest must equal the
    current file exactly."""

    @staticmethod
    def _write(
        root: pathlib.Path,
        log: bytes,
        snaps: list[dict] | None = None,
        raw_ledger: str | None = None,
    ) -> None:
        d = root / "docs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "stage-8-debate-log.md").write_bytes(log)
        lp = root / vri.APPEND_LEDGER_PATH
        if raw_ledger is not None:
            lp.write_text(raw_ledger)
        elif snaps is None:
            lp.write_text(
                json.dumps(
                    {"snapshots": [{"session": 26, "bytes": len(log),
                                    "sha256": digest(log)}]}
                )
            )
        else:
            lp.write_text(json.dumps({"snapshots": snaps}))

    def test_multi_snapshot_history_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            s1 = b"frozen prefix\n"
            s2 = s1 + b"## Round 9 appendix\n"
            s3 = s2 + b"## Round 10 appendix\n"
            self._write(
                root,
                s3,
                snaps=[
                    {"session": 24, "bytes": len(s1), "sha256": digest(s1)},
                    {"session": 25, "bytes": len(s2), "sha256": digest(s2)},
                    {"session": 26, "bytes": len(s3), "sha256": digest(s3)},
                ],
            )
            ok, detail = vri.append_ledger(root)
            self.assertTrue(ok, detail)
            self.assertIn("3 snapshots", detail)

    def test_same_length_mutation_of_appended_region_fails(self):
        """THE hole this check closes: frozen prefix intact, total size
        unchanged, suffix rewritten in place -- the prefix-only pin cannot
        see it, L1 must."""
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            good = b"frozen prefix\n## Round 9: closure survives\n"
            bad = bytearray(good)
            bad[-1] = ord("X")
            self._write(
                root,
                bytes(bad),
                snaps=[{"session": 26, "bytes": len(good),
                        "sha256": digest(good)}],
            )
            ok, detail = vri.append_ledger(root)
            self.assertFalse(ok)
            self.assertIn("!=", detail)

    def test_unregistered_lawful_append_fails_with_guidance(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            base = b"frozen prefix\n"
            self._write(root, base + b"\n## Round 10 appendix\n",
                        snaps=[{"session": 26, "bytes": len(base),
                                "sha256": digest(base)}])
            ok, detail = vri.append_ledger(root)
            self.assertFalse(ok)
            self.assertIn("register", detail)

    def test_truncation_below_recorded_state_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            big = b"frozen prefix\nlong appended history\n"
            self._write(root, b"frozen pre",
                        snaps=[{"session": 26, "bytes": len(big),
                                "sha256": digest(big)}])
            ok, detail = vri.append_ledger(root)
            self.assertFalse(ok)
            self.assertIn("truncated", detail.lower())

    def test_stale_older_snapshot_fails_even_if_newest_matches(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            cur = b"frozen prefix\nwhole appended region\n"
            self._write(
                root,
                cur,
                snaps=[
                    {"session": 25, "bytes": 10,
                     "sha256": digest(b"wrongwrong!")},
                    {"session": 26, "bytes": len(cur), "sha256": digest(cur)},
                ],
            )
            ok, detail = vri.append_ledger(root)
            self.assertFalse(ok)
            self.assertIn("alteration", detail)

    def test_missing_malformed_and_non_monotone_ledgers_fail(self):
        with tempfile.TemporaryDirectory() as td:
            ok, detail = vri.append_ledger(pathlib.Path(td))
            self.assertFalse(ok)
            self.assertIn("missing", detail.lower())
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, b"log bytes\n", raw_ledger="{not json")
            ok, detail = vri.append_ledger(root)
            self.assertFalse(ok)
            self.assertIn("unreadable", detail.lower())
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            cur = b"0123456789" * 2
            self._write(
                root,
                cur,
                snaps=[
                    {"session": 27, "bytes": 30,
                     "sha256": digest(b"x" * 30)},
                    {"session": 26, "bytes": len(cur),
                     "sha256": digest(cur)},
                ],
            )
            ok, detail = vri.append_ledger(root)
            self.assertFalse(ok)
            self.assertIn("strictly increasing", detail)


class CronBriefingTests(unittest.TestCase):
    """C1 cron-check coverage: SKIP (ok is None) on an absent config so the
    verifier stays portable, but strict validation whenever present -- stale
    briefing markers anywhere in the file, a disabled or missing v3 hold
    briefing, a resurrected legacy project briefing, and malformed configs
    all fail loudly; unrelated non-project jobs are ignored."""

    V3_PROMPT = (
        "continuing the Substrate digital-evolution project at ~/avida-life "
        "... closed-programme verification hold ..."
    )
    LEGACY_PROMPT = (
        "continuing the Substrate digital-evolution project at ~/avida-life "
        "... Stage 7B0 autonomous carry-on ..."
    )

    @staticmethod
    def _write(root: pathlib.Path, payload) -> pathlib.Path:
        p = root / "jobs.json"
        if isinstance(payload, str):
            p.write_text(payload)
        else:
            p.write_text(json.dumps({"jobs": payload}))
        return p

    def test_v3_only_enabled_passes(self):
        with tempfile.TemporaryDirectory() as td:
            p = self._write(
                pathlib.Path(td),
                [
                    {
                        "id": "b64708c35fa7",
                        "prompt": self.LEGACY_PROMPT,
                        "enabled": False,
                    },
                    {
                        "id": vri.CRON_V3_JOB_ID,
                        "prompt": self.V3_PROMPT,
                        "enabled": True,
                    },
                ],
            )
            ok, detail = vri.cron_jobs_ok(p)
            self.assertTrue(ok, detail)
            self.assertIn("v3 hold briefing", detail)

    def test_absent_config_skips_non_failing(self):
        with tempfile.TemporaryDirectory() as td:
            ok, detail = vri.cron_jobs_ok(pathlib.Path(td) / "jobs.json")
            self.assertIsNone(ok)
            self.assertIn("skipped", detail)

    def test_stale_marker_fails_anywhere_in_config(self):
        """Marker must be caught wherever it sits -- here inside an otherwise
        well-formed job prompt, i.e. past the parse stage."""
        with tempfile.TemporaryDirectory() as td:
            p = self._write(
                pathlib.Path(td),
                [
                    {
                        "id": "legacy-still-there",
                        "prompt": self.LEGACY_PROMPT
                        + " table f753894+i retired",
                        "enabled": False,
                    },
                ],
            )
            ok, detail = vri.cron_jobs_ok(p)
            self.assertFalse(ok)
            self.assertIn("1 stale 'f753894'", detail)
            self.assertIn("failsafe fixer", detail)

    def test_disabled_or_missing_v3_fails(self):
        disabled = [
            {"id": vri.CRON_V3_JOB_ID, "prompt": self.V3_PROMPT,
             "enabled": False},
        ]
        missing = [
            {"id": "b64708c35fa7", "prompt": self.LEGACY_PROMPT,
             "enabled": False},
        ]
        for payload in (disabled, missing):
            with tempfile.TemporaryDirectory() as td:
                p = self._write(pathlib.Path(td), payload)
                ok, detail = vri.cron_jobs_ok(p)
                self.assertFalse(ok)
                self.assertIn("disabled or missing", detail)

    def test_resurrected_legacy_job_alongside_v3_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p = self._write(
                pathlib.Path(td),
                [
                    {
                        "id": "b64708c35fa7",
                        "prompt": self.LEGACY_PROMPT,
                        "enabled": True,
                    },
                    {
                        "id": vri.CRON_V3_JOB_ID,
                        "prompt": self.V3_PROMPT,
                        "enabled": True,
                    },
                ],
            )
            ok, detail = vri.cron_jobs_ok(p)
            self.assertFalse(ok)
            self.assertIn("unexpected additional enabled project job(s)",
                          detail)
            self.assertIn("b64708c35fa7", detail)

    def test_unrelated_enabled_job_is_ignored(self):
        """A non-project job must never be flagged: lawful owner scheduling
        action outside this programme is not tampering."""
        with tempfile.TemporaryDirectory() as td:
            p = self._write(
                pathlib.Path(td),
                [
                    {"id": "other-job", "prompt": "water the plants",
                     "enabled": True},
                    {
                        "id": vri.CRON_V3_JOB_ID,
                        "prompt": self.V3_PROMPT,
                        "enabled": True,
                    },
                ],
            )
            ok, detail = vri.cron_jobs_ok(p)
            self.assertTrue(ok, detail)

    def test_malformed_config_fails_loudly(self):
        with tempfile.TemporaryDirectory() as td:
            p = self._write(pathlib.Path(td), "{not json at all")
            ok, detail = vri.cron_jobs_ok(p)
            self.assertFalse(ok)
            self.assertIn("unreadable/malformed", detail)


class FailedDesignsLedgerTests(unittest.TestCase):
    """F1 coverage: the append-only failed-designs archive was previously
    bound only by D1 -- a git diff against one fixed base commit plus an
    entry-directory count. Neither property proves a single byte of
    content, and both expire the moment a lawful door fires and the
    baseline rolls forward. The ledger binds every archived file by
    {bytes, sha256}: same-length rewrites, deletions, malformed ledgers,
    and unregistered lawful appends must all fail loudly."""

    ARCHIVE = {
        "failed-designs/e1/README.md": b"no-go rationale\n",
        "failed-designs/e1/gate-summary.json": b'{"verdict": "NO_GO"}\n',
        "failed-designs/e2/nested/diagnosis.md": b"why it failed\n",
    }

    @staticmethod
    def _ledger(files: dict[str, bytes]) -> str:
        return json.dumps(
            {
                "version": 1,
                "files": {
                    rel: {"bytes": len(d), "sha256": digest(d)}
                    for rel, d in sorted(files.items())
                },
            }
        )

    @classmethod
    def _write(
        cls,
        root: pathlib.Path,
        files: dict[str, bytes],
        raw_ledger: str | None = None,
    ) -> None:
        for rel, data in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        lp = root / vri.FAILED_DESIGNS_LEDGER_PATH
        lp.parent.mkdir(parents=True, exist_ok=True)
        lp.write_text(
            raw_ledger if raw_ledger is not None else cls._ledger(files)
        )

    def test_multi_entry_archive_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, dict(self.ARCHIVE))
            ok, detail = vri.failed_designs_ledger(root)
            self.assertTrue(ok, detail)
            self.assertIn("3 files", detail)
            self.assertIn("2 entries", detail)

    def test_same_length_in_place_edit_fails(self):
        """THE hole this check closes: a same-length rewrite of an archived
        file changes no count and -- once history moves past D1's fixed
        base commit -- no diff either; only content binding sees it."""
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            good = dict(self.ARCHIVE)
            bad = bytearray(good["failed-designs/e1/README.md"])
            bad[-2] = ord("X")
            edited = dict(good)
            edited["failed-designs/e1/README.md"] = bytes(bad)
            self._write(root, edited, raw_ledger=self._ledger(good))
            ok, detail = vri.failed_designs_ledger(root)
            self.assertFalse(ok)
            self.assertIn("altered", detail)
            self.assertIn("failed-designs/e1/README.md", detail)

    def test_deleted_registered_file_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, dict(self.ARCHIVE))
            (root / "failed-designs/e1/gate-summary.json").unlink()
            ok, detail = vri.failed_designs_ledger(root)
            self.assertFalse(ok)
            self.assertIn("deleted", detail)
            self.assertIn("gate-summary.json", detail)

    def test_unregistered_append_fails_with_registration_guidance(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, dict(self.ARCHIVE))
            newdir = root / "failed-designs/e3"
            newdir.mkdir()
            (newdir / "gate-summary.json").write_bytes(b'{"ok": false}\n')
            ok, detail = vri.failed_designs_ledger(root)
            self.assertFalse(ok)
            self.assertIn("unregistered", detail)
            self.assertIn("register", detail.lower())

    def test_missing_malformed_wrongtype_and_bad_digest_fail_loudly(self):
        with tempfile.TemporaryDirectory() as td:
            ok, detail = vri.failed_designs_ledger(pathlib.Path(td))
            self.assertFalse(ok)
            self.assertIn("missing", detail.lower())
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, dict(self.ARCHIVE), raw_ledger="{not json")
            ok, detail = vri.failed_designs_ledger(root)
            self.assertFalse(ok)
            self.assertIn("unreadable", detail.lower())
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, dict(self.ARCHIVE),
                        raw_ledger='{"version": 1, "files": []}')
            ok, detail = vri.failed_designs_ledger(root)
            self.assertFalse(ok)
            self.assertIn("malformed", detail.lower())
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            self._write(root, dict(self.ARCHIVE))
            lp = root / vri.FAILED_DESIGNS_LEDGER_PATH
            led = json.loads(lp.read_text())
            first = next(iter(led["files"]))
            led["files"][first]["sha256"] = "not-a-digest"
            lp.write_text(json.dumps(led))
            ok, detail = vri.failed_designs_ledger(root)
            self.assertFalse(ok)
            self.assertIn("malformed", detail.lower())
            self.assertIn(first, detail)


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
        # L1 content-binds the appended region via the ledger sidecar.
        self.assertIn("L1 append-ledger", joined)
        # C1 validates the out-of-repo scheduler config (or labels its
        # absence as a SKIP) without ever failing silently.
        self.assertIn("C1 cron", joined)
        # F1 content-binds the append-only failed-designs archive via the
        # ledger sidecar (D1's diff-vs-base + count prove no content).
        self.assertIn("F1 failed-designs", joined)

    def test_live_repo_has_no_tracked_file_modifications(self):
        ok, detail = vri.tree_clean(vri.REPO_ROOT, strict=False)
        self.assertTrue(ok, detail)


if __name__ == "__main__":
    unittest.main()
