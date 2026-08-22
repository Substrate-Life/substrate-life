# Push Status — Large-File Block and Storage Decision

*Date: 2026-08-22*

## Current state

`main` is 40 commits ahead of `origin/main` (fork point `3c34047`). The
push is **blocked by GitHub's hard 100 MB per-file limit**:

| File | Size | Introducing commit |
|------|------|--------------------|
| `results/host-compressibility-long-window-360001x10ms.json` | 297.68 MB | `30753c9` (2026-08-01) |
| `results/host-encoding-diagnostic-result.json` | 80.50 MB (warns, not blocking) | `9e0b94e` |

Both files are registered raw artifacts with SHA-256 values cited in
committed audit documents (`docs/host-compressibility-long-window-independent-audit.md`,
`docs/host-encoding-diagnostic-independent-audit.md`). The preregistration
chronology (protocol freeze `e8d2f51` → manifest `3dfb70c` → invalid
attempt `0976239` → retained capture) treats those commits' IDs as
evidence.

## Why we will not rewrite history to force the push

Per `scientific-repository-publication.md`, late LFS migration or history
filtering replaces blobs and rewrites every descendant commit ID. Audit
documents cite the current IDs. A filtered snapshot would be a different
publication product and must not silently replace the original.

## Options, in preference order

1. **Git LFS on the remote, configured prospectively** — but `git-lfs` is
   not installed locally and package installation requires root. Requires
   operator action: install git-lfs, then migrate only the two paths under
   a full-bundle safety net.
2. **External object storage for the two large raw files** with a
   committed binding manifest (path, byte size, SHA-256, retrieval URL),
   plus a normal-history push of everything else after removing the two
   blobs via a *documented, bundled, mapping-recorded* filter. This still
   rewrites IDs and requires a migration note per the publication guide.
3. **Push to an alternate remote without the limit** (any Git host or a
   bare repo on accessible storage). Preserves every commit ID exactly;
   zero scientific cost.

## Safety net already taken

A full bundle of all refs exists at `/tmp/substrate-full-history.bundle`
(34,046,576 bytes,
SHA-256 `1a78b5695bfd933687fb7fa573c651fc5b3975928d362a7a942fbdaad6a695a0`,
created via `git bundle create /tmp/substrate-full-history.bundle --all`)
before any migration decision. No history rewriting has occurred.

## What continues regardless

All Stage 7 work (B0 classified PASS + double-audited; B1 design) lives in
commits that contain no oversized objects. Only the push is blocked; the
research program proceeds locally and the recurring schedule remains
active.
