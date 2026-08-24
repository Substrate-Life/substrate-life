"""Tests for src/audit_doc_path_references.py.

Pure-logic coverage builds synthetic repository trees in tmp directories and
exercises every check (R1-R6) plus the directory-prefix coverage semantics.
One live smoke runs the real auditor against this repository, read-only, via
the same subprocess entrypoint the verifier's --auditors wiring uses. The
suite never touches the network and never executes programme mechanics.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _make_registry(entries: list[dict]) -> str:
    return json.dumps(
        {"schema": 1, "registered_absences": entries}, indent=2
    )


class DocPathReferenceAuditTestBase(unittest.TestCase):
    """Build a synthetic repo tree; return (root, audit_fn)."""

    def setUp(self):
        import audit_doc_path_references as adpr

        self.adpr = adpr
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = pathlib.Path(self._tmp.name)
        (self.root / "docs").mkdir()

    def write(self, rel: str, text: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def good_entry(self, **over) -> dict:
        entry = {
            "path": "results/never-created/",
            "reason_class": "failed-feasibility-gate",
            "reason": "gate failed 0/24; archived with evidence",
            "evidence_files": ["failed-designs/gate-no-go"],
            "cited_by": ["docs/prereg.md"],
        }
        entry.update(over)
        return entry

    def standard_tree(self) -> None:
        # A document citing one existing path and one registered-absent path.
        self.write(
            "docs/prereg.md",
            "Raw output retained under `results/never-created/sub/result.json` "
            "per plan; see also `results/real-dir/real.txt`.\n",
        )
        self.write("README.md", "Repo map: `src/engine.py`.\n")
        self.write("results/real-dir/real.txt", "retained\n")
        self.write("src/engine.py", "print('x')\n")
        (self.root / "failed-designs" / "gate-no-go").mkdir(parents=True)
        (self.root / "failed-designs" / "gate-no-go" / "evidence.txt").write_text(
            "no-go\n"
        )
        self.write("docs/doc-path-reference-registry.json", _make_registry([self.good_entry()]))

    def run_audit(self, min_citations: int = 3):
        return self.adpr.audit(self.root, min_citations=min_citations)


class HappyPaths(DocPathReferenceAuditTestBase):
    def test_standard_tree_passes_all_checks(self):
        self.standard_tree()
        ok, lines = self.run_audit()
        self.assertTrue(ok, "\n".join(lines))
        self.assertTrue(lines[-1].startswith("DOC-PATH-REFERENCES AUDIT: ALL CHECKS PASS"))
        joined = "\n".join(lines)
        for label in ("R1 registry", "R2 coverage", "R3 coverage", "R4 registered", "R5 evidence", "R6 citation"):
            self.assertIn(label, joined)

    def test_prefix_registration_covers_inner_paths(self):
        # The citation points at a file UNDER the registered absent directory;
        # the directory registration must cover it (this is the exact shape of
        # the real stage7b-endpoint-repair/stage7b2-repair families).
        self.standard_tree()
        ok, lines = self.run_audit()
        self.assertTrue(ok, "\n".join(lines))
        joined = "\n".join(lines)
        self.assertIn("all 1 absent citation(s)", joined)

    def test_markdown_link_citations_recognised(self):
        self.standard_tree()
        self.write(
            "docs/other.md",
            "Repo-rooted links are recognised: [the archive](failed-designs/gate-no-go), "
            "[results](results/never-created/), [doc](docs/prereg.md). "
            "A parent-relative link is out of scope by construction and must not "
            "be counted either way: [up](../failed-designs/gate-no-go).\n",
        )
        ok, lines = self.run_audit(min_citations=6)
        self.assertTrue(ok, "\n".join(lines))


class LoudFailures(DocPathReferenceAuditTestBase):
    def test_unregistered_absence_fails_naming_the_path(self):
        self.standard_tree()
        self.write("docs/newdoc.md", "planned output `results/brand-new/out.json`.\n")
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        joined = "\n".join(lines)
        self.assertIn("R3 coverage of absent citations", joined)
        self.assertIn("results/brand-new/out.json", joined)
        self.assertIn("not registered", joined)

    def test_registered_path_coming_into_existence_fails(self):
        # Tripwire: a permanently-unused registered path must never quietly
        # start existing (e.g. an execution writing into a superseded path).
        self.standard_tree()
        (self.root / "results" / "never-created").mkdir(parents=True)
        (self.root / "results" / "never-created" / "surprise.txt").write_text("x")
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        joined = "\n".join(lines)
        self.assertIn("R4 registered paths still absent", joined)
        self.assertIn("now EXIST", joined)

    def test_missing_evidence_file_fails(self):
        self.standard_tree()
        self.write(
            "docs/doc-path-reference-registry.json",
            _make_registry([self.good_entry(evidence_files=["failed-designs/gone"])]),
        )
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        joined = "\n".join(lines)
        self.assertIn("R5 evidence binding", joined)
        self.assertIn("failed-designs/gone", joined)

    def test_empty_evidence_directory_fails(self):
        self.standard_tree()
        (self.root / "failed-designs" / "hollow").mkdir()
        self.write(
            "docs/doc-path-reference-registry.json",
            _make_registry([self.good_entry(evidence_files=["failed-designs/hollow"])]),
        )
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        self.assertIn("empty directory", "\n".join(lines))

    def test_stale_entry_without_live_citation_fails(self):
        # If the citing sentence disappears from the docs, the registry entry
        # must be updated in the same commit -- otherwise it fails loudly here.
        self.standard_tree()
        self.write(
            "docs/doc-path-reference-registry.json",
            _make_registry([self.good_entry(cited_by=["docs/renamed-away.md"])]),
        )
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        joined = "\n".join(lines)
        self.assertIn("R6 citation anchoring", joined)
        self.assertIn("results/never-created/", joined)


class RegistryStrictness(DocPathReferenceAuditTestBase):
    def setUp(self):
        super().setUp()
        self.standard_tree()

    def test_missing_registry_fails(self):
        (self.root / "docs/doc-path-reference-registry.json").unlink()
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        joined = "\n".join(lines)
        self.assertIn("R1 registry", joined)
        self.assertIn("missing", joined)
        self.assertIn("not evaluable", joined)

    def test_malformed_json_fails(self):
        self.write("docs/doc-path-reference-registry.json", "{not json")
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        self.assertIn("unreadable", "\n".join(lines))

    def test_wrong_schema_fails(self):
        reg = json.loads(_make_registry([self.good_entry()]))
        reg["schema"] = 99
        self.write(
            "docs/doc-path-reference-registry.json", json.dumps(reg, indent=2)
        )
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        self.assertIn("schema must be 1", "\n".join(lines))

    def test_empty_entries_list_fails(self):
        self.write(
            "docs/doc-path-reference-registry.json",
            json.dumps({"schema": 1, "registered_absences": []}),
        )
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        self.assertIn("non-empty list", "\n".join(lines))

    def test_unknown_reason_class_fails(self):
        self.write(
            "docs/doc-path-reference-registry.json",
            _make_registry([self.good_entry(reason_class="because-i-said-so")]),
        )
        ok, lines = self.run_audit()
        self.assertFalse(ok)
        self.assertIn("unknown reason_class", "\n".join(lines))

    def test_empty_required_fields_fail(self):
        for field in ("path", "reason"):
            entry = self.good_entry()
            entry[field] = "   "
            self.write(
                "docs/doc-path-reference-registry.json",
                _make_registry([entry]),
            )
            ok, lines = self.run_audit()
            self.assertFalse(ok, f"{field} blank should fail")
            self.assertIn(f"field '{field}' empty/missing", "\n".join(lines))


class CoverageFloor(DocPathReferenceAuditTestBase):
    def test_floor_failure_is_loud(self):
        # A near-empty scanned surface means the citation regexes or the
        # scanned-surface set rotted; even a passing registry must fail.
        self.write("README.md", "# Empty\n")
        self.write("docs/only.md", "nothing cited\n")
        self.write(
            "docs/doc-path-reference-registry.json", _make_registry([self.good_entry()])
        )
        ok, lines = self.adpr.audit(self.root, min_citations=None)  # module floor
        self.assertFalse(ok)
        joined = "\n".join(lines)
        self.assertIn("R2 coverage", joined)
        self.assertIn("(floor 280)", joined)


class LiveSmoke(unittest.TestCase):
    def test_live_repo_audit_passes_via_subprocess_entrypoint(self):
        r = subprocess.run(
            [
                sys.executable,
                "-B",
                str(REPO_ROOT / "src" / "audit_doc_path_references.py"),
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            check=False,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        last = (r.stdout or "").strip().splitlines()[-1]
        self.assertIn("ALL CHECKS PASS", last)


if __name__ == "__main__":
    unittest.main()
