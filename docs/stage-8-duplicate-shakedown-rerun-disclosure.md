# Stage 8 duplicate corrected-gate rerun: disclosure of a second execution of shakedown table 20421301+j

*Recorded 2026-08-23 under the duplicate-session disclosure precedent
(3acd5fa / ee5c7ca / f1e6880 chain). This note changes no registered
quantity, re-authorises nothing, and touches no artifact. It corrects one
factual sentence in the f1e6880 freeze-commit disclosure and records a
procedural deviation against registration #3 §4.*

## 1. What happened

Registration #3 §4 authorised the corrected §7 gate to execute **once
more** on the fixed shakedown table `20421301 + j` (k = 12 pairs,
exploratory, stdout-only, unretained). Two complete executions occurred:

| # | Launch | Completion | Evidence |
|---|--------|------------|----------|
| A | ≈ 11:33 UTC by the session that committed 0a081ce ("the rerun [is] executing as this entry is committed"); that session was subsequently terminated | ≈ 12:54 UTC (mtime of `/tmp/stage8-gate-rerun-stdout.json`; wrapper stderr `/tmp/stage8-gate-rerun-stderr.log` ends `GATE_EXIT=0`) | Full gate summary JSON on disk in `/tmp`, all four conditions PASS |
| B | ≈ 13:25 UTC (header line mtime of `/tmp/stage8-corrected-gate-rerun-2026-08-23.log`) by the session that produced f1e6880, believing attempt A had emitted nothing | ≈ 15:3x UTC (≈ 2h05m wall per the f1e6880 message) | Summary captured at `/tmp/stage8-corrected-gate-summary.json`; embedded verbatim in the freeze manifest |

At 14:54:44 UTC the freeze commit f1e6880 disclosed: *"the preceding
session launched this same authorised rerun (~11:33 UTC) and was
terminated before the process emitted anything observable; **no output
existed on disk or in any transcript***" (emphasis added here). The
italicised clause is **factually incorrect as to disk**: execution A
completed at ≈ 12:54 and wrote its full summary to `/tmp` roughly two
hours *before* the freeze was committed. Attempt B's operator searched
repo paths and transcripts and missed the `/tmp` captures.

## 2. Why this had no integrity consequence

1. **Zero information difference.** Executions A and B are deterministic
   replays of the same fixed seeded table with the same frozen code. The
   two summary files were compared programmatically this session: the
   JSON documents are **identical in every key and value**. The second
   execution generated no observation that did not already exist.
2. **No endpoint exposure in either execution.** Both summaries contain
   only condition booleans and counts (pairs both-arms COMPLETE, audit /
   overflow / checkpoint / seed-mismatch lists, replay identity booleans)
   plus the registration §3 `factual_shakedown_context` block of
   threshold-free aggregates (mutation-decision totals, kernel-draw
   totals, terminal live census 48..48 across all 24 arms, Arm-M
   distinct-A range 8..15). No `ᾱ` value, no paired difference, no
   direction information exists in either capture.
3. **Nothing was tuned.** An independent hash audit performed this
   session confirms all 30 pins of
   `results/stage8-alpha-evolution-paired/pre-execution-manifest.json`
   byte-match the working tree at f1e6880 with an empty drift table
   versus every prior retained manifest. Kernel, floor, thresholds,
   window, endpoint, arm definitions, seed tables, and rule are exactly
   as registered before either execution.
4. **Confirmatory table untouched.** `20310529 + i` consumed zero runs
   through both shakedown executions; its single authorised retained
   launch occurred at 14:55 UTC from the f1e6880 tree and is the only
   retained act of registration #3 §6.

On the evidence available, no agent read either capture before the
freeze: session A died before its own process finished; session B never
found the files; this session's first read of capture A postdates
f1e6880. (A negative cannot be proven absolutely; the claim is recorded
at the strength the evidence supports.)

## 3. Disposition

- The deviation is **recorded, not repaired**: no third execution of the
  shakedown table is authorised or permitted, and none will occur.
- The registration #3 §6 sequence continues unaffected: the one retained
  confirmatory suite (launched 14:55 UTC) → reduction applied exactly
  once by the source-frozen reducer → execution note carrying the
  Round-2/3 obligations (empirical null spread of `D_i` reported
  descriptively whatever the class; leakage monitor `leakage_pairs` and
  ancestry-plurality read and reported).
- `failed-designs/` is not implicated: no gate condition failed in either
  execution; nothing is being deleted or rewritten. The superseded-
  tooling G2 failure archive remains the only gate-failure record.
- Future sessions: before asserting that a predecessor "emitted nothing",
  sweep volatile capture locations (`/tmp`) as well as repo paths and
  transcripts; this note exists because that sweep was missed once.
