"""Minimal raw acquisition for the registered 15-minute latency morphology arms."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time


def _compile_worker(worker, source, cache, stop, ready, counts, failures):
    env = os.environ.copy(); env["PYTHONPYCACHEPREFIX"] = str(cache / f"w{worker}")
    command = [sys.executable, "-m", "compileall", "-q", "-f", "-j", "1", str(source)]
    ready.set()
    try:
        while not stop.is_set():
            result = subprocess.run(command, env=env, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, check=False)
            if result.returncode:
                raise RuntimeError(f"compile worker {worker} exit {result.returncode}")
            counts[worker] += 1
    except BaseException as error:
        failures.append(error); stop.set()


def _waiting_worker(stop, ready):
    ready.set(); stop.wait()


def capture(arm: str, sample_count: int, cadence_ns: int, warmup_seconds: float,
            source: Path) -> dict:
    if arm not in {"S", "C"}: raise ValueError("arm must be S or C")
    stop = threading.Event(); ready = [threading.Event(), threading.Event()]
    counts = [0, 0]; failures = []; threads = []
    with tempfile.TemporaryDirectory(prefix="latency-morphology-") as temporary:
        root = Path(temporary)
        for worker in range(2):
            if arm == "C":
                target = _compile_worker; args = (worker, source, root, stop, ready[worker], counts, failures)
            else:
                target = _waiting_worker; args = (stop, ready[worker])
            thread = threading.Thread(target=target, args=args); thread.start(); threads.append(thread)
        for event in ready:
            if not event.wait(10): raise RuntimeError("worker readiness timeout")
        time.sleep(warmup_seconds)
        first_deadline = time.monotonic_ns() + cadence_ns
        records = []
        for sequence in range(sample_count):
            deadline = first_deadline + sequence * cadence_ns
            remaining = deadline - time.monotonic_ns()
            if remaining > 0: time.sleep(remaining / 1_000_000_000)
            wake = time.monotonic_ns()
            records.append([sequence, deadline, wake])
            if failures: raise RuntimeError("compile worker failure") from failures[0]
        stop.set()
        for thread in threads: thread.join(30)
        if any(thread.is_alive() for thread in threads): raise RuntimeError("worker stop failure")
        if failures: raise RuntimeError("compile worker failure") from failures[0]
    return {"artifact_version": 1, "status": "RAW_ONLY", "arm": arm,
            "sample_count": sample_count, "cadence_ns": cadence_ns,
            "warmup_seconds": warmup_seconds, "records": records,
            "compile_cycles": counts,
            "privacy": "sequence, monotonic deadline, monotonic wake, arm provenance only"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arm", choices=["S", "C"]); parser.add_argument("output", type=Path)
    parser.add_argument("--sample-count", type=int, default=90_001)
    parser.add_argument("--cadence-ms", type=int, default=10)
    parser.add_argument("--warmup-seconds", type=float, default=30)
    parser.add_argument("--source", type=Path, default=Path("src"))
    args = parser.parse_args()
    artifact = capture(args.arm, args.sample_count, args.cadence_ms * 1_000_000,
                       args.warmup_seconds, args.source)
    encoded = (json.dumps(artifact, separators=(",", ":"), sort_keys=True) + "\n").encode()
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream: stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({"arm": args.arm, "output": str(args.output), "bytes": len(encoded),
                      "sha256": hashlib.sha256(encoded).hexdigest(),
                      "compile_cycles": artifact["compile_cycles"]}, sort_keys=True))


if __name__ == "__main__": main()
