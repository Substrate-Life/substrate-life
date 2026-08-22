# History Migration Note — 2026-08-22

## What happened

The first push of the accumulated 41-commit range was rejected by GitHub's
pre-receive hook: the registered raw artifact
`results/host-compressibility-long-window-360001x10ms.json` is 312,139,776
bytes, exceeding GitHub's hard 100 MB per-file limit. The file was committed
in `30753c9` ("Retain one-hour host compressibility result", 2026-08-01),
which lay inside the unpushed range — **no previously published commit ID
was affected**.

## What was done

Following the documented decision in the pre-migration `docs/push-status.md`
(option 2, "external storage" realised as same-repo split parts):

1. A full-history safety bundle was created:
   `/tmp/substrate-pre-migration.bundle`, 34,048,783 bytes,
   SHA-256 `78532a703e7ecb34f72467a55460982ec2c72210e25f1c9b8d094bf6ed250efb`.
2. The raw artifact was copied out and verified against its registered
   SHA-256 `623f59af1b6dd76a0f050337345881b93059981547ffe96a89eaa8b9a3a57c5f`.
3. `git filter-repo --invert-paths --path <that one path>` removed exactly
   that path from history. No other path was touched.
4. The raw bytes were re-added at the tip as eight ~40 MB parts under
   `results/host-compressibility-long-window-360001x10ms.parts/` with a
   binding `MANIFEST.json` (per-part offsets and SHA-256s; reassembly rule;
   original SHA-256 authoritative). Round-trip reassembly was verified
   byte-exact before commit.
5. This note records the mapping.

## Commit-ID consequences (verified)

- Fork point `3c34047` ("Add threat-matched verification finding") and every
  commit older than `30753c9` are **byte-identical, unchanged IDs** —
  including all Stage 1–6 history, both host-coupling registration commits,
  and their cited manifests (`e8d2f51`, `3dfb70c`, `0976239`).
- Exactly 36 commits changed ID: the artifact commit itself and its 35
  descendants (the Stage 7 line). Their subjects are unchanged. The full
  old→new map is embedded in `MANIFEST.json` under `migration_map`.

## Evidence-status consequences

- Raw-artifact SHA-256 values are unchanged and remain the authoritative
  identity of retained evidence; they never depended on Git object IDs.
- Audit documents written before this migration cite old IDs for the 36
  rewritten commits. Those citations now resolve through the map below.
  Per the publication guide, historical documents are not rewritten as if
  the new hashes were original; this note is the resolution record.
- The preregistration chronology (protocol freeze → manifest → capture) is
  preserved: relative order, dates, and content are untouched.

## Verification commands

```bash
git log --format='%H %s' origin/main..HEAD          # current IDs
cat results/host-compressibility-long-window-360001x10ms.parts/MANIFEST.json
# reassemble and check:
cat results/.../part-*.bin | sha256sum   # == 623f59af...
```
