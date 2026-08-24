#!/usr/bin/env python3
"""Retained-class integrity verifier: one-command mechanical re-verification battery.

Standalone, read-only, stdlib-only (house precedent: src/audit_*.py). Consolidates
the verification battery performed ad hoc in programme-review sessions 10-12 into
a single reproducible command so every future wake can re-establish the Part V
item-4 retained-class immutability invariant cheaply and without skipped steps.

What it checks (all mechanical, all read-only):

  P1  Both retained pre-execution manifests are themselves bit-intact against
      the digests recorded below (tamper-evident anchor: the manifests are
      retained-class objects and must never change).
  P2  Every pinned file of both manifests re-hashes byte-exactly to its pinned
      {bytes, sha256}. The single lawful exception is docs/stage-8-debate-log.md,
      which is append-only by Round-2/6 design: it passes iff its frozen prefix
      of exactly the pinned length hashes to the pinned digest (pure-append rule,
      proven in programme-review session 10 and reproduced in every later wake).
  P3  Inventory close: each retained directory contains exactly the manifest plus
      the pins/first-retained-outputs the manifest declares -- nothing added,
      nothing missing.
  L1  Append ledger: docs/stage-8-debate-log-append-ledger.json content-binds
      the lawfully-appended suffix of the sole pure-append path (the P2 pin
      proves only its frozen prefix). Every recorded {bytes, sha256} snapshot
      must remain a byte-exact prefix of the current file forever, snapshots
      must grow strictly monotonically, and the newest snapshot must equal
      the current file exactly -- so same-length rewrites of the appended
      region, truncations, malformed/non-monotone ledgers, and lawful appends
      not registered within the appending unit's own commit all FAIL loudly.
  T1  Working tree clean (git status --porcelain empty).
  S1  Sync: local HEAD equals origin/main by local rev-parse comparison
      (no network; compares the last-fetched remote ref). The wake
      procedure fetches first, so this mechanises briefing step 1's
      comparison half and turns any unpushed-commit or failed-push
      state into a loud stop condition instead of a manual discovery.
  D1  Doors: zero changed paths under results/ or failed-designs/ since the last
      artifact-producing commit d19d7c2 (the R1-R3 door check used by sessions
      10-12), and failed-designs/ still holds exactly its 8 archived entries.
  C1  Cron-briefing integrity: the out-of-repo scheduler config is validated
      strictly whenever present -- it must parse, carry ZERO stale f753894
      briefing markers, have exactly the v3 hold-briefing job enabled for
      this project, and NO other enabled project-targeting job (a resurrected
      legacy briefing would contradict the hold at every wake). An ABSENT
      config is a labelled non-failing SKIP so the verifier stays portable to
      environments without this scheduler. Unrelated non-project jobs are
      deliberately ignored: lawful owner scheduling action must never be
      flagged as tampering. This mechanises the manual disclosure every wake
      since session 19 has hand-run ("cron jobs.json checked directly").

P2 additionally emits a non-failing info line for each pure-append path
reporting the file's current byte size (= frozen prefix + lawfully
appended), replacing the per-session manual stat disclosure of the
debate log's size that every wake since session 10 has hand-transcribed.

With --auditors it additionally spawns the three standalone read-only auditors
(signed-bracket, post-retention, follow-on-memo) and requires exit 0 from each;
it never runs the test suite and never executes anything evolutionary (Part V
item-3 hold respected by construction).

Exit code 0 iff every check passes. Any FAIL line means: stop, do not treat the
wake as verified, diagnose before anything else.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Retained manifests (P1 anchors). These digests were recorded at session 13
# (2026-08-23) after reproducing the session 10-12 re-hash battery bit-for-bit;
# both manifests are retained-class and must match these forever.
RETAINED_MANIFESTS: tuple[tuple[str, str], ...] = (
    (
        "results/stage7b-signed-bracket/pre-execution-manifest.json",
        "a9e3d532299d2b111fc00d33d09c8e627aa737033f4e2ea738f2b8f379a737a7",
    ),
    (
        "results/stage8-alpha-evolution-paired/pre-execution-manifest.json",
        "c7cec747ab997a0fc9ede498d2e0f050498b24f77db93f6083a46bcb7c9054e7",
    ),
)

# Sole path for which the pure-append rule (P2 exception) is recognised. Any
# other pinned path must match exactly or the check fails.
PURE_APPEND_PATHS = frozenset({"docs/stage-8-debate-log.md"})

# Retained execution outputs that predate the manifest "first_retained_outputs"
# declaration convention: they live beside their manifest, are retained-class,
# and are named explicitly here so P3 can require exact directory membership
# without silently tolerating undeclared files.
KNOWN_DIR_OUTPUTS: dict[str, tuple[str, ...]] = {
    "results/stage7b-signed-bracket": (
        "stage7b-signed-bracket-result.json",
        "stage7b-signed-bracket-reduced.json",
    ),
}

# Last artifact-producing commit (programme-review sessions 10-12 door check).
LAST_ARTIFACT_COMMIT = "d19d7c2"

# Append-only archive directory must hold exactly this many entries.
FAILED_DESIGNS_COUNT = 8

# Content-binding ledger for the sole pure-append path (check L1): a monotone
# snapshot history proving the appended suffix byte-exact against every
# recorded state. Non-retained, unpinned, version-controlled; each lawful
# append registers a new snapshot in the appending unit's own commit.
APPEND_LEDGER_PATH = "docs/stage-8-debate-log-append-ledger.json"

# Scheduler state (check C1). Out-of-repo and environment-specific: the
# session-19 root-cause fix replaced the stale legacy briefing job with the
# v3 closed-programme hold briefing; every wake since has re-established by
# hand that the fix survived. Absent file => labelled SKIP (portability);
# present file => strict validation.
CRON_JOBS_PATH = pathlib.Path("/opt/data/cron/jobs.json")
CRON_V3_JOB_ID = "de939b52cc2b"
STALE_BRIEFING_MARKER = "f753894"
PROJECT_MARKERS = ("avida-life", "substrate-life")

AUDITORS: tuple[str, ...] = (
    "src/audit_stage7b_signed_bracket.py",
    "src/audit_stage8_post_retention.py",
    "src/audit_followon_power_memo.py",
)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def classify_pin(
    root: pathlib.Path, rel: str, meta: dict
) -> tuple[str, str]:
    """Return (verdict, detail) for one pinned path; verdict in
    {EXACT, PURE_APPEND, MISSING, DRIFT}."""
    p = root / rel
    if not p.is_file():
        return "MISSING", f"{rel}: absent from working tree"
    # Normalize to a repo-relative posix path so the PURE_APPEND_PATHS
    # membership test is robust to absolute vs relative input styles.
    norm_rel = _rel_to_root(p, root) or pathlib.PurePosixPath(rel).as_posix()
    data = p.read_bytes()
    if len(data) == meta["bytes"] and sha256_hex(data) == meta["sha256"]:
        return "EXACT", f"{rel}: byte-exact ({meta['bytes']} B)"
    if norm_rel in PURE_APPEND_PATHS:
        prefix = data[: meta["bytes"]]
        if sha256_hex(prefix) == meta["sha256"]:
            appended = len(data) - meta["bytes"]
            return (
                "PURE_APPEND",
                f"{rel}: frozen prefix ({meta['bytes']} B) bit-exact; "
                f"{appended} B lawfully appended (append-only debate log)",
            )
        return (
            "DRIFT",
            f"{rel}: frozen prefix no longer hashes to pinned digest "
            "(alteration, not append)",
        )
    return (
        "DRIFT",
        f"{rel}: len {len(data)} != {meta['bytes']} or sha mismatch",
    )


def _rel_to_root(p: pathlib.Path, root: pathlib.Path) -> str | None:
    try:
        return str(p.resolve().relative_to(root.resolve()))
    except ValueError:
        return None


def append_ledger(
    root: pathlib.Path,
    rel: str = "docs/stage-8-debate-log.md",
) -> tuple[bool, str]:
    """L1: content-bind the pure-append path beyond its frozen prefix.

    The P2 pin proves only the frozen prefix and accepts ANY bytes behind
    it, so a same-length in-place rewrite of the appended region would
    otherwise pass every mechanical check. The ledger at APPEND_LEDGER_PATH
    holds a monotone snapshot history: every recorded {bytes, sha256} must
    still be a byte-exact prefix of the current file, snapshots must grow
    strictly monotonically, and the newest must equal the current file
    exactly. Any alteration (same-size or not), truncation, stale historical
    snapshot, or lawful append not registered in the appending unit's own
    commit fails loudly.
    """
    lp = root / APPEND_LEDGER_PATH
    if not lp.is_file():
        return False, f"{APPEND_LEDGER_PATH}: missing (cannot content-bind {rel})"
    try:
        ledger = json.loads(lp.read_text())
        raw_snaps = ledger["snapshots"]
        if not isinstance(raw_snaps, list) or not raw_snaps:
            raise ValueError("snapshots must be a non-empty list")
        snaps = [(int(s["bytes"]), str(s["sha256"])) for s in raw_snaps]
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return False, f"{APPEND_LEDGER_PATH}: unreadable/malformed ({exc})"
    sizes = [b for b, _ in snaps]
    if any(next_b <= b for b, next_b in zip(sizes, sizes[1:])):
        return False, (
            f"{APPEND_LEDGER_PATH}: snapshots not strictly increasing in "
            f"bytes {sizes}"
        )
    target = root / rel
    if not target.is_file():
        return False, f"{rel}: absent from working tree"
    data = target.read_bytes()
    stale = [
        f"{b}B/{h[:12]}"
        for b, h in snaps[:-1]
        if not (len(data) >= b and sha256_hex(data[:b]) == h)
    ]
    if stale:
        return False, (
            f"{rel}: recorded history no longer a byte-exact prefix "
            f"(alteration, not append): {', '.join(stale)}"
        )
    lb, lh = snaps[-1]
    if len(data) < lb:
        return False, (
            f"{rel}: truncated below last recorded state ({len(data)} < {lb} B)"
        )
    cur = (len(data), sha256_hex(data))
    if cur != (lb, lh):
        return False, (
            f"{rel}: current state {cur[0]}B/{cur[1][:12]} != last recorded "
            f"{lb}B/{lh[:12]} -- register lawful appends in "
            f"{APPEND_LEDGER_PATH} within the appending unit's own commit"
        )
    return True, (
        f"{rel}: {len(data)} B matches ledger history ({len(snaps)} "
        f"snapshot{'s' if len(snaps) != 1 else ''}; frozen prefix + "
        f"appended suffix content-bound)"
    )


def inventory_close(
    root: pathlib.Path,
    manifest_path: str | pathlib.Path,
    manifest: dict,
    known_outputs: tuple[str, ...] = (),
) -> tuple[list[str], list[str]]:
    """Extra files present in the retained dir, and declared-but-missing files.

    All inputs and returns are repo-root-relative strings. Expected membership
    is exactly: the manifest itself, any pinned files located in this
    directory, any first_retained_outputs located here, plus `known_outputs`
    (pre-convention retained outputs named explicitly by the caller).
    """
    mdir = pathlib.PurePosixPath(manifest_path).parent
    declared = set(manifest.get("files", {}))
    for k in ("raw", "reduced"):
        out = manifest.get("first_retained_outputs", {}).get(k)
        if out:
            declared.add(out)
    declared.add(str(manifest_path))
    for out in known_outputs:
        declared.add(f"{mdir.as_posix()}/{out}")
    actual: set[str] = set()
    for q in (root / mdir).iterdir():
        if q.is_file():
            rel = _rel_to_root(q, root)
            if rel is not None:
                actual.add(rel)
    local_declared = {
        rel for rel in declared if (root / rel).parent == (root / mdir)
    }
    extra = sorted(actual - local_declared)
    missing = sorted(local_declared - actual)
    return extra, missing


def git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def tree_clean(root: pathlib.Path, strict: bool = True) -> tuple[bool, str]:
    args = ["status", "--porcelain"]
    if not strict:
        args.append("--untracked-files=no")
    r = git(root, *args)
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if r.returncode != 0:
        return False, f"git status failed: {r.stderr.strip()}"
    if lines:
        return False, "working tree dirty:\n      " + "\n      ".join(lines[:10])
    return True, (
        "working tree clean"
        if strict
        else "no modifications to tracked files (untracked ignored)"
    )


def doors(
    root: pathlib.Path, base: str, expected_failed_designs: int
) -> tuple[bool, str]:
    rb = git(root, "rev-parse", "--verify", base)
    if rb.returncode != 0:
        return False, f"base commit {base} not found"
    rd = git(root, "diff", "--name-only", f"{base}..HEAD", "--", "results/", "failed-designs/")
    moved = [ln for ln in rd.stdout.splitlines() if ln.strip()]
    fd = root / "failed-designs"
    n = len([q for q in fd.iterdir() if q.is_dir()]) if fd.is_dir() else -1
    ok = (rd.returncode == 0 and not moved and n == expected_failed_designs)
    return ok, (
        f"changed artifact paths since {base}: {len(moved)}; "
        f"failed-designs entries: {n} (expected {expected_failed_designs})"
        + ("" if not moved else "; moved=" + ",".join(moved[:5]))
    )


def sync(root: pathlib.Path) -> tuple[bool, str]:
    """S1: local HEAD must equal origin/main.

    Purely local (compares the last-fetched remote ref, no network); the
    wake procedure fetches first. Unknown refs fail loudly -- a verifier
    that cannot establish the sync state must never silently pass.
    """
    rh = git(root, "rev-parse", "--verify", "HEAD")
    rm = git(root, "rev-parse", "--verify", "origin/main")
    if rh.returncode != 0 or rm.returncode != 0:
        return False, (
            f"refs unknown: HEAD rc={rh.returncode}, "
            f"origin/main rc={rm.returncode} (not a git repo / fetch first?)"
        )
    head, main = rh.stdout.strip(), rm.stdout.strip()
    if head != main:
        rc = git(root, "rev-list", "--left-right", "--count", f"{main}...{head}")
        counts = (
            rc.stdout.strip().replace("\t", "/") if rc.returncode == 0 else "?/?"
        )
        return False, (
            f"HEAD {head[:12]} != origin/main {main[:12]} "
            f"(behind/ahead {counts}; resolve fetch/push before proceeding)"
        )
    return True, f"HEAD {head[:12]} == origin/main"


def cron_jobs_ok(
    path: pathlib.Path | None = None,
) -> tuple[bool | None, str]:
    """C1: the scheduler must run exactly the v3 hold briefing for this repo.

    Mechanises the per-wake manual disclosure performed since session 19
    ("enabled job = v3 only, zero f753894 markers"). Returns (ok, detail)
    where ok is None iff the check is skipped because the scheduler config
    does not exist in this environment (non-failing; recorded as a labelled
    PASS so portability never masks state). A PRESENT file must validate
    strictly:

      - parses as JSON with a list under "jobs";
      - zero occurrences of the stale-briefing marker f753894 anywhere;
      - the v3 hold-briefing job (CRON_V3_JOB_ID) exists and is enabled;
      - no OTHER enabled job targets this project (a resurrected legacy
        briefing would contradict the hold at every wake).

    Unrelated enabled jobs are ignored: they are outside this programme,
    and lawful owner scheduling action must never be flagged as tampering.
    """
    p = CRON_JOBS_PATH if path is None else pathlib.Path(path)
    if not p.is_file():
        return None, (
            f"{p}: scheduler config absent from this environment; "
            "skipped (non-failing)"
        )
    try:
        raw = p.read_text()
        cfg = json.loads(raw)
        jobs = cfg["jobs"]
        if not isinstance(jobs, list):
            raise ValueError('"jobs" must be a list')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return False, f"{p}: unreadable/malformed ({exc})"
    markers = raw.count(STALE_BRIEFING_MARKER)
    if markers:
        return False, (
            f"{p}: {markers} stale '{STALE_BRIEFING_MARKER}' briefing "
            "marker(s) present -- re-run the session-19 failsafe fixer "
            "(fails safe on unexpected content) before proceeding"
        )
    project_jobs = [
        j
        for j in jobs
        if any(m in str(j.get("prompt", "")) for m in PROJECT_MARKERS)
    ]
    enabled_project = {
        str(j.get("id")): j for j in project_jobs if j.get("enabled")
    }
    if CRON_V3_JOB_ID not in enabled_project:
        return False, (
            f"{p}: v3 hold-briefing job {CRON_V3_JOB_ID} disabled or "
            "missing -- wakes would stop or arrive on a stale briefing"
        )
    others = sorted(k for k in enabled_project if k != CRON_V3_JOB_ID)
    if others:
        return False, (
            f"{p}: unexpected additional enabled project job(s) {others} "
            f"besides {CRON_V3_JOB_ID} -- a resurrected legacy briefing "
            "would contradict the hold"
        )
    return True, (
        f"{p}: enabled project job = {CRON_V3_JOB_ID} (v3 hold briefing) "
        f"only; {markers} '{STALE_BRIEFING_MARKER}' markers"
    )


def run_auditors(root: pathlib.Path) -> tuple[bool, str]:
    outs = []
    ok = True
    for script in AUDITORS:
        r = subprocess.run(
            [sys.executable, "-B", str(root / script)],
            capture_output=True,
            text=True,
            cwd=str(root),
            check=False,
        )
        text = (r.stdout or r.stderr or "").strip()
        tail = text.splitlines()[-1:] or ["<no output>"]
        outs.append(f"{script}: exit {r.returncode}; {tail[0][:110]}")
        ok = ok and r.returncode == 0
    return ok, "; ".join(outs)


def verify(
    root: pathlib.Path = REPO_ROOT,
    with_auditors: bool = False,
    include_tree_check: bool = True,
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

    # P1 manifest self-integrity
    for rel, digest in RETAINED_MANIFESTS:
        p = root / rel
        ok = p.is_file() and sha256_hex(p.read_bytes()) == digest
        record(ok, "P1 manifest anchor", f"{rel}" if ok else f"{rel} missing or digest drifted")

    # P2/P3 pins and inventories
    for rel, _digest in RETAINED_MANIFESTS:
        mp = root / rel
        if not mp.is_file():
            record(False, "P2 pins", f"{rel}: unreadable")
            continue
        manifest = load_manifest(mp)
        pin_items = sorted(manifest["files"].items())
        verdicts = [classify_pin(root, r, m) for r, m in pin_items]
        exact = sum(1 for v, _ in verdicts if v == "EXACT")
        append = sum(1 for v, _ in verdicts if v == "PURE_APPEND")
        bad = [(v, d) for v, d in verdicts if v in ("MISSING", "DRIFT")]
        n = len(verdicts)
        record(
            not bad,
            f"P2 pins [{rel.rsplit('/', 2)[-2]}]",
            f"{exact}/{n} exact, {append} pure-append, {len(bad)} bad"
            + ("" if not bad else "; e.g. " + bad[0][1]),
        )
        for _v, d in bad:
            lines.append(f"       detail: {d}")
        # Non-failing size disclosure for pure-append paths (see module
        # docstring): makes the recurring manual debate-log byte report
        # mechanical.
        for (rel_i, meta_i), (v_i, _d_i) in zip(pin_items, verdicts):
            if v_i == "PURE_APPEND":
                total_b = (root / rel_i).stat().st_size
                lines.append(
                    f"       info: {rel_i}: current size {total_b} B "
                    f"(= {meta_i['bytes']} B frozen prefix + "
                    f"{total_b - meta_i['bytes']} B lawfully appended)"
                )
        extra, missing = inventory_close(
            root,
            rel,
            manifest,
            known_outputs=KNOWN_DIR_OUTPUTS.get(
                pathlib.PurePosixPath(rel).parent.as_posix(), ()
            ),
        )
        record(
            not extra and not missing,
            f"P3 inventory [{rel.rsplit('/', 2)[-2]}]",
            f"extra={extra or 'none'} missing={missing or 'none'}",
        )

    # L1 append ledger: content-binds the pure-append suffix (the P2 pin
    # proves only the frozen prefix; see module docstring).
    ok, detail = append_ledger(root)
    record(ok, "L1 append-ledger", detail)

    # T1 tree clean (strict: includes untracked). Skippable for in-suite
    # smoke runs where the verifier's own new files are legitimately
    # untracked until their commit lands.
    if include_tree_check:
        ok, detail = tree_clean(root, strict=True)
        record(ok, "T1 tree", detail)

    # S1 sync: runs regardless of include_tree_check so the live-repo
    # smoke covers it too. At suite time HEAD is the arrival HEAD (the
    # unit's own commit does not exist yet), which equals origin/main.
    ok, detail = sync(root)
    record(ok, "S1 sync", detail)

    # D1 doors
    ok, detail = doors(root, LAST_ARTIFACT_COMMIT, FAILED_DESIGNS_COUNT)
    record(ok, "D1 doors", detail)

    # C1 cron-briefing integrity: out-of-repo scheduler state. An absent
    # config is a labelled non-failing SKIP; a present one must validate
    # strictly. Runs regardless of include_tree_check so the live-repo
    # smoke covers it too.
    c1_ok, c1_detail = cron_jobs_ok()
    record(c1_ok is not False, "C1 cron", c1_detail)

    # Optional auditors
    if with_auditors:
        ok, detail = run_auditors(root)
        record(ok, "A1 auditors", detail)

    total = n_checks
    lines.append(
        f"VERIFY_RETAINED_INTEGRITY: {'ALL CHECKS PASS' if failures == 0 else 'FAILURES PRESENT'} "
        f"({total - failures}/{total})"
    )
    return failures == 0, lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--auditors",
        action="store_true",
        help="also run the three standalone read-only auditors (requires exit 0)",
    )
    args = ap.parse_args(argv)
    ok, lines = verify(with_auditors=args.auditors)
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
