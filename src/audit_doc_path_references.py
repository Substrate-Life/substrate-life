"""audit_doc_path_references.py -- read-only documentation path-reference auditor.

Answers one question mechanically: does every repository-rooted path that the
current-facing documentation cites actually exist on disk -- and where it does
not, is that absence a REGISTERED lawful absence with live evidence rather than
silent rot?

Scope (deliberate):
  - Scanned surfaces: README.md and docs/*.md (the current-facing documents).
    superseded/ and the documents inside results/ and failed-designs/ are
    archival surfaces; they are neither scanned nor required to resolve.
  - Citations recognised: repository-rooted paths under results/,
    failed-designs/, superseded/, src/, docs/ appearing inside backtick code
    spans, plus relative markdown link targets on those same prefixes.
  - External URLs, fragments, mailto, and prefix-less relative links
    (e.g. bare filenames) are out of scope by construction.

Checks:
  R1 registry strict parse (schema, types, non-empty fields)
  R2 citation-coverage floor (regex/scope rot tripwire)
  R3 every absent citation registered (unregistered absences fail loudly)
  R4 registered-absent paths must STILL be absent (a permanently-unused path
     coming into existence is a loud stop condition, never a quiet pass)
  R5 every registry evidence file exists (directories: exist and non-empty)
  R6 every registry entry anchored by >=1 live citation from its cited_by
     documents (registry rot fails loudly)

Exit code 0 iff every check passes. Read-only over the whole tree: this audit
never writes, never executes programme mechanics, and respects the Part V
item-3 hold (no evolutionary execution anywhere).
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

REGISTRY_PATH = "docs/doc-path-reference-registry.json"

SCAN_FILES = ("README.md",)
SCAN_DIR = "docs"

PATH_PREFIXES = ("results/", "failed-designs/", "superseded/", "src/", "docs/")

BACKTICK_PATH = re.compile(
    r"`((?:results|failed-designs|superseded|src|docs)/[A-Za-z0-9_./-]+)`"
)
MD_LINK = re.compile(r"\]\(([^)\s]+)\)")
EXTERNAL = re.compile(r"^[a-z]+://|^#|^mailto:")

# Coverage floor: the registration sweep measured 300 unique (file, citation)
# pairs across README.md + docs/*.md. A large silent drop would mean the
# citation regexes or the scanned-surface set rotted; fail loudly well before
# that. Lawful doc growth moves the number UP, which never trips this.
MIN_CITATIONS = 280

ALLOWED_REASON_CLASSES = frozenset(
    {
        "large-file-history-migration",
        "failed-feasibility-gate",
        "superseded-by-repair-registration",
        "uncommitted-source-citation",
    }
)


def _strip_trailing_punct(s: str) -> str:
    return s.rstrip(".,;:")


def collect_citations(root: pathlib.Path) -> dict[str, set[str]]:
    """Return {citation -> {files citing it}} over the scanned surfaces."""
    found: dict[str, set[str]] = {}
    files: list[pathlib.Path] = []
    for name in SCAN_FILES:
        p = root / name
        if p.is_file():
            files.append(p)
    docs = root / SCAN_DIR
    if docs.is_dir():
        files.extend(sorted(docs.glob("*.md")))
    for f in files:
        try:
            text = f.read_text()
        except OSError:
            continue
        rel = f.relative_to(root).as_posix()
        hits: set[str] = set()
        for m in BACKTICK_PATH.finditer(text):
            hits.add(_strip_trailing_punct(m.group(1)))
        for m in MD_LINK.finditer(text):
            t = m.group(1)
            if EXTERNAL.match(t):
                continue
            t = _strip_trailing_punct(t.split("#", 1)[0]).rstrip("/")
            if not t:
                continue
            if not t.startswith(PATH_PREFIXES):
                continue
            hits.add(t)
        for h in hits:
            found.setdefault(h, set()).add(rel)
    return found


def load_registry(root: pathlib.Path) -> tuple[dict | None, str]:
    lp = root / REGISTRY_PATH
    if not lp.is_file():
        return None, f"{REGISTRY_PATH}: missing (cannot classify absent citations)"
    try:
        reg = json.loads(lp.read_text())
    except (ValueError, OSError) as exc:
        return None, f"{REGISTRY_PATH}: unreadable ({exc})"
    if not isinstance(reg, dict) or reg.get("schema") != 1:
        return None, f"{REGISTRY_PATH}: schema must be 1"
    entries = reg.get("registered_absences")
    if not isinstance(entries, list) or not entries:
        return None, f"{REGISTRY_PATH}: 'registered_absences' must be a non-empty list"
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            return None, f"{REGISTRY_PATH}: entry #{i} not an object"
        for key in ("path", "reason_class", "reason"):
            v = e.get(key)
            if not isinstance(v, str) or not v.strip():
                return None, f"{REGISTRY_PATH}: entry #{i} field {key!r} empty/missing"
        if e["reason_class"] not in ALLOWED_REASON_CLASSES:
            return (
                None,
                f"{REGISTRY_PATH}: entry #{i} unknown reason_class "
                f"{e['reason_class']!r}",
            )
        ev = e.get("evidence_files")
        cb = e.get("cited_by")
        if not isinstance(ev, list) or not ev or not all(
            isinstance(x, str) and x.strip() for x in ev
        ):
            return (
                None,
                f"{REGISTRY_PATH}: entry #{i} 'evidence_files' must be a "
                "non-empty list of paths",
            )
        if not isinstance(cb, list) or not cb or not all(
            isinstance(x, str) and x.strip() for x in cb
        ):
            return (
                None,
                f"{REGISTRY_PATH}: entry #{i} 'cited_by' must be a non-empty "
                "list of document paths",
            )
    return reg, ""


def _covered(entry_path: str, citation: str) -> bool:
    """Directory registrations (trailing slash) cover everything under them."""
    base = entry_path.rstrip("/")
    return citation == base or citation.startswith(base + "/")


def audit(
    root: pathlib.Path, min_citations: int | None = None
) -> tuple[bool, list[str]]:
    lines: list[str] = []
    failures = 0
    n_checks = 0

    def record(ok: bool, label: str, detail: str) -> None:
        nonlocal failures, n_checks
        if not ok:
            failures += 1
        n_checks += 1
        lines.append(f"[{'PASS' if ok else 'FAIL'}] {label}: {detail}")

    floor = MIN_CITATIONS if min_citations is None else min_citations

    citations = collect_citations(root)
    total_pairs = sum(len(v) for v in citations.values())

    # R2 coverage floor.
    record(
        total_pairs >= floor,
        "R2 coverage",
        f"{total_pairs} unique (document, citation) pairs across scanned "
        f"surfaces (floor {floor})",
    )

    # R1 registry parse.
    reg, err = load_registry(root)
    if reg is None:
        record(False, "R1 registry", err)
    else:
        record(True, "R1 registry", _registry_summary(reg))
    if reg is None:
        record(False, "R3 coverage of absent citations", "not evaluable (R1 failed)")
        record(False, "R4 registered paths still absent", "not evaluable (R1 failed)")
        record(False, "R5 evidence binding", "not evaluable (R1 failed)")
        record(False, "R6 citation anchoring", "not evaluable (R1 failed)")
        lines.append(
            f"DOC-PATH-REFERENCES AUDIT: FAILURES={failures}/{n_checks} checks"
        )
        return failures == 0, lines

    entries = reg["registered_absences"]

    # R3 every absent citation must be covered by a registration.
    uncovered: list[tuple[str, list[str]]] = []
    resolved = 0
    for cite in sorted(citations):
        if (root / cite).exists():
            resolved += 1
            continue
        if any(_covered(e["path"], cite) for e in entries):
            continue
        uncovered.append((cite, sorted(citations[cite])))

    absent_total = len(uncovered) + sum(
        1
        for c in citations
        if not (root / c).exists()
        and any(_covered(e["path"], c) for e in entries)
    )
    if uncovered:
        preview = "; ".join(f"{c} (cited by {fs[0]})" for c, fs in uncovered[:5])
        record(
            False,
            "R3 coverage of absent citations",
            f"{len(uncovered)} ABSENT citation(s) not registered in "
            f"{REGISTRY_PATH}, e.g. {preview}",
        )
    else:
        record(
            True,
            "R3 coverage of absent citations",
            f"all {absent_total} absent citation(s) resolve to registered "
            f"lawful absences; other {resolved} citation(s) exist on disk",
        )

    # R4 registered paths must still be absent (tripwire).
    materialised = [e["path"] for e in entries if (root / e["path"].rstrip("/")).exists()]
    if materialised:
        record(
            False,
            "R4 registered paths still absent",
            f"{len(materialised)} registered permanently-unused path(s) now "
            f"EXIST on disk: {', '.join(materialised[:5])} -- diagnose before "
            "anything else",
        )
    else:
        record(
            True,
            "R4 registered paths still absent",
            f"all {len(entries)} registered absence path(s) still absent",
        )

    # R5 evidence binding.
    lost: list[str] = []
    for e in entries:
        for ev in e["evidence_files"]:
            p = root / ev
            if p.is_dir():
                if not any(p.iterdir()):
                    lost.append(f"{ev} (empty directory)")
            elif not p.is_file():
                lost.append(ev)
    if lost:
        record(
            False,
            "R5 evidence binding",
            f"{len(lost)} evidence path(s) missing/empty: "
            f"{'; '.join(lost[:5])}",
        )
    else:
        record(
            True,
            "R5 evidence binding",
            f"all evidence paths across {len(entries)} registration(s) exist",
        )

    # R6 every entry anchored by a live citation from a cited_by document.
    unanchored: list[str] = []
    for e in entries:
        anchoring = [
            cite
            for cite in citations
            if _covered(e["path"], cite) and citations[cite] & set(e["cited_by"])
        ]
        if not anchoring:
            unanchored.append(e["path"])
    if unanchored:
        record(
            False,
            "R6 citation anchoring",
            f"{len(unanchored)} registered entr(ies) no longer cited by any "
            f"cited_by document: {', '.join(unanchored[:5])} -- update the "
            "registry in the same commit as the citing-document change",
        )
    else:
        record(
            True,
            "R6 citation anchoring",
            f"all {len(entries)} registration(s) anchored by live citations",
        )

    status = "ALL CHECKS PASS" if failures == 0 else "FAILURES"
    lines.append(
        f"DOC-PATH-REFERENCES AUDIT: {status} ({n_checks - failures}/{n_checks})"
        if failures == 0
        else f"DOC-PATH-REFERENCES AUDIT: {status}={failures}/{n_checks} checks"
    )
    return failures == 0, lines


def _registry_summary(reg: dict) -> str:
    entries = reg["registered_absences"]
    classes = sorted({e["reason_class"] for e in entries})
    return (
        f"{REGISTRY_PATH}: {len(entries)} lawful-absence registration(s), "
        f"classes {','.join(classes)}"
    )


def main(argv: list[str] | None = None) -> int:
    ok, lines = audit(REPO_ROOT)
    for ln in lines:
        print(ln)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
