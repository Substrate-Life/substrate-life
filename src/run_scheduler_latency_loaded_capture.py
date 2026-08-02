"""Run one registered scheduler-latency compile or sham arm."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time

from host_compressibility_probe import build_artifact


def compile_command(source_dir: Path) -> list[str]:
    return [sys.executable, "-m", "compileall", "-q", "-f", "-j", "1", str(source_dir)]


class Journal:
    def __init__(self, path: Path):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        self._stream = os.fdopen(fd, "w", encoding="utf-8", buffering=1)
        self._lock = threading.Lock()
        self.failed = threading.Event()

    def write(self, event: dict[str, object], fsync: bool = False) -> None:
        record = {"monotonic_ns": time.monotonic_ns(), **event}
        try:
            with self._lock:
                self._stream.write(json.dumps(record, sort_keys=True) + "\n")
                self._stream.flush()
                if fsync:
                    os.fsync(self._stream.fileno())
        except BaseException:
            self.failed.set()
            raise

    def close(self) -> None:
        with self._lock:
            self._stream.close()


def _worker(
    worker_id: int, mode: str, source_dir: Path | None, cache_dir: Path,
    journal: Journal, stop: threading.Event, ready: threading.Event,
    state: dict[str, object], lock: threading.Lock, failures: list[BaseException],
) -> None:
    try:
        journal.write({"event": "worker_ready", "worker": worker_id})
        ready.set()
        if mode == "sham":
            stop.wait()
            return
        assert source_dir is not None
        env = os.environ.copy()
        env["PYTHONPYCACHEPREFIX"] = str(cache_dir)
        command = compile_command(source_dir)
        ordinal = 0
        while not stop.is_set() and not journal.failed.is_set():
            ordinal += 1
            started = time.monotonic_ns()
            with lock:
                state["active"] = True
                state["last_start_ns"] = started
                state["invocations"] = ordinal
            journal.write({"event": "invocation_started", "worker": worker_id,
                           "invocation": ordinal})
            result = subprocess.run(command, env=env, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, check=False)
            ended = time.monotonic_ns()
            with lock:
                state["active"] = False
                state["last_end_ns"] = ended
                if result.returncode == 0:
                    state["completed"] += 1
                else:
                    state["nonzero"] += 1
            journal.write({"event": "invocation_ended", "worker": worker_id,
                           "invocation": ordinal, "exit_status": result.returncode,
                           "duration_ns": ended - started})
    except BaseException as error:
        failures.append(error)
        stop.set()
    finally:
        ready.set()


def run_loaded_capture(
    output: Path, journal_path: Path, source_dir: Path | None,
    sample_count: int, cadence_ns: int, worker_count: int,
    warmup_seconds: float, arm: str = "C", mode: str = "compile",
    heartbeat_seconds: float = 10.0,
) -> dict[str, object]:
    if arm not in {"C", "S"} or mode not in {"compile", "sham"}:
        raise ValueError("invalid registered arm or mode")
    if (arm, mode) not in {("C", "compile"), ("S", "sham")}:
        raise ValueError("arm/mode mismatch")
    if worker_count != 2:
        raise ValueError("registered arms require two supervisor workers")
    if mode == "compile" and (source_dir is None or not source_dir.is_dir()):
        raise ValueError("compile arm requires immutable source directory")
    if sample_count < 11 or (sample_count - 1) % 10:
        raise ValueError("sample count must be at least 11 and 1 modulo 10")
    if cadence_ns <= 0 or warmup_seconds < 0 or heartbeat_seconds <= 0:
        raise ValueError("invalid timing parameter")
    if output.exists():
        raise FileExistsError(output)

    journal = Journal(journal_path)
    journal.write({"event": "manager_started", "arm": arm, "mode": mode,
                   "worker_count": worker_count}, fsync=True)
    stop = threading.Event()
    heartbeat_stop = threading.Event()
    lock = threading.Lock()
    failures: list[BaseException] = []
    states = [{"worker": i, "active": False, "invocations": 0,
               "completed": 0, "nonzero": 0, "last_start_ns": None,
               "last_end_ns": None} for i in range(worker_count)]
    ready = [threading.Event() for _ in range(worker_count)]
    workers: list[threading.Thread] = []
    temp_root = Path(tempfile.mkdtemp(prefix="substrate-compile-load-"))
    os.chmod(temp_root, 0o700)
    cleanup_success = False
    artifact_bytes: bytes | None = None
    failure: BaseException | None = None

    try:
        for i in range(worker_count):
            cache = temp_root / f"w{i}"
            cache.mkdir(mode=0o700)
            thread = threading.Thread(target=_worker,
                args=(i, mode, source_dir, cache, journal, stop, ready[i],
                      states[i], lock, failures), name=f"registered-worker-{i}")
            thread.start(); workers.append(thread)
        for event in ready:
            if not event.wait(30):
                raise RuntimeError("worker readiness timeout")
        if failures:
            raise RuntimeError("worker failed during readiness") from failures[0]
        journal.write({"event": "workload_started", "arm": arm, "mode": mode,
                       "worker_count": worker_count}, fsync=True)

        def heartbeat() -> None:
            try:
                while not heartbeat_stop.is_set():
                    with lock:
                        snapshot = [{"worker": s["worker"], "active": s["active"],
                                     "completed": s["completed"], "nonzero": s["nonzero"]}
                                    for s in states]
                    journal.write({"event": "heartbeat", "arm": arm, "mode": mode,
                                   "live_workers": sum(t.is_alive() for t in workers),
                                   "workers": snapshot}, fsync=True)
                    heartbeat_stop.wait(heartbeat_seconds)
            except BaseException as error:
                failures.append(error); stop.set()

        hb = threading.Thread(target=heartbeat, name="registered-heartbeat")
        hb.start()
        try:
            time.sleep(warmup_seconds)
            if failures or journal.failed.is_set() or sum(t.is_alive() for t in workers) != 2:
                raise RuntimeError("workload failed during warmup")
            journal.write({"event": "capture_started", "arm": arm,
                           "sample_count": sample_count, "cadence_ns": cadence_ns,
                           "warmup_seconds": warmup_seconds}, fsync=True)
            artifact = build_artifact(sample_count, cadence_ns)
            artifact_bytes = (json.dumps(artifact, indent=2, sort_keys=True) + "\n").encode()
            fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(artifact_bytes); stream.flush(); os.fsync(stream.fileno())
            journal.write({"event": "capture_completed", "arm": arm,
                           "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
                           "artifact_bytes": len(artifact_bytes)}, fsync=True)
        finally:
            stop.set()
            for thread in workers: thread.join(120)
            heartbeat_stop.set(); hb.join(30)
    except BaseException as error:
        failure = error
        try:
            journal.write({"event": "capture_failed", "arm": arm,
                           "error_type": type(error).__name__}, fsync=True)
        except BaseException:
            pass
    finally:
        try:
            shutil.rmtree(temp_root); cleanup_success = not temp_root.exists()
        except BaseException:
            cleanup_success = False
        with lock: terminal_states = [dict(s) for s in states]
        try:
            journal.write({"event": "workload_stopped", "arm": arm, "mode": mode,
                           "worker_count": worker_count,
                           "live_workers_after_join": sum(t.is_alive() for t in workers),
                           "workers": terminal_states,
                           "cleanup_success": cleanup_success}, fsync=True)
        finally:
            journal.close()
    if failure is not None: raise failure
    if failures: raise RuntimeError("worker or journal failure") from failures[0]
    if mode == "compile" and any(
        state["nonzero"] != 0 or state["completed"] <= 0 for state in terminal_states
    ):
        raise RuntimeError("compile workload integrity failure")
    if mode == "sham" and any(state["invocations"] != 0 for state in terminal_states):
        raise RuntimeError("sham invocation integrity failure")
    if not cleanup_success:
        raise RuntimeError("temporary cache cleanup failure")
    if artifact_bytes is None: raise RuntimeError("capture produced no artifact")
    return {"arm": arm, "mode": mode, "output_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
            "output_bytes": len(artifact_bytes), "workers": terminal_states,
            "cleanup_success": cleanup_success}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("output", type=Path); p.add_argument("journal", type=Path)
    p.add_argument("--arm", choices=["C", "S"], required=True)
    p.add_argument("--mode", choices=["compile", "sham"], required=True)
    p.add_argument("--source-dir", type=Path)
    p.add_argument("--sample-count", type=int, default=360_001)
    p.add_argument("--cadence-ms", type=int, default=10)
    p.add_argument("--worker-count", type=int, default=2)
    p.add_argument("--warmup-seconds", type=float, default=30.0)
    args = p.parse_args()
    print(json.dumps(run_loaded_capture(args.output, args.journal, args.source_dir,
        args.sample_count, args.cadence_ms * 1_000_000, args.worker_count,
        args.warmup_seconds, args.arm, args.mode), indent=2, sort_keys=True))


if __name__ == "__main__": main()
