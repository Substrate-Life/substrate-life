"""Run the registered continuous-compile scheduler-latency capture arm."""

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

from host_compressibility_probe import build_artifact


def compile_command(source_dir: Path) -> list[str]:
    return [sys.executable, "-m", "compileall", "-q", "-f", "-j", "1", str(source_dir)]


class Journal:
    def __init__(self, path: Path):
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        self._stream = os.fdopen(descriptor, "w", encoding="utf-8", buffering=1)
        self._lock = threading.Lock()

    def write(self, event: dict[str, object]) -> None:
        record = {"monotonic_ns": time.monotonic_ns(), **event}
        with self._lock:
            self._stream.write(json.dumps(record, sort_keys=True) + "\n")
            self._stream.flush()
            os.fsync(self._stream.fileno())

    def close(self) -> None:
        with self._lock:
            self._stream.close()


def _worker(
    worker_id: int,
    source_dir: Path,
    cache_dir: Path,
    stop: threading.Event,
    started: threading.Event,
    state: dict[str, object],
    state_lock: threading.Lock,
) -> None:
    environment = os.environ.copy()
    environment["PYTHONPYCACHEPREFIX"] = str(cache_dir)
    command = compile_command(source_dir)
    started.set()
    while not stop.is_set():
        start = time.monotonic_ns()
        completed = subprocess.run(
            command,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        end = time.monotonic_ns()
        with state_lock:
            state["invocations"] += 1
            state["last_start_monotonic_ns"] = start
            state["last_end_monotonic_ns"] = end
            if completed.returncode == 0:
                state["completed_compiles"] += 1
            else:
                state["nonzero_exits"] += 1
                state["last_nonzero_exit"] = completed.returncode
    with state_lock:
        state["thread_exited_monotonic_ns"] = time.monotonic_ns()


def run_loaded_capture(
    output: Path,
    journal_path: Path,
    source_dir: Path,
    sample_count: int,
    cadence_ns: int,
    worker_count: int,
    warmup_seconds: float,
    heartbeat_seconds: float = 10.0,
) -> dict[str, object]:
    if worker_count != 2:
        raise ValueError("registered loaded arm requires exactly two workers")
    if sample_count < 11 or (sample_count - 1) % 10:
        raise ValueError("sample count must be at least 11 and 1 modulo 10")
    if cadence_ns <= 0 or warmup_seconds < 0 or heartbeat_seconds <= 0:
        raise ValueError("invalid timing parameter")
    if output.exists():
        raise FileExistsError(output)

    journal = Journal(journal_path)
    stop = threading.Event()
    state_lock = threading.Lock()
    states = [
        {
            "worker_id": index,
            "invocations": 0,
            "completed_compiles": 0,
            "nonzero_exits": 0,
            "last_nonzero_exit": None,
            "last_start_monotonic_ns": None,
            "last_end_monotonic_ns": None,
            "thread_exited_monotonic_ns": None,
        }
        for index in range(worker_count)
    ]
    workers: list[threading.Thread] = []
    started_events = [threading.Event() for _ in range(worker_count)]
    heartbeat_stop = threading.Event()

    with tempfile.TemporaryDirectory(prefix="substrate-compile-load-") as temporary:
        temporary_root = Path(temporary)
        for index in range(worker_count):
            thread = threading.Thread(
                target=_worker,
                args=(
                    index,
                    source_dir,
                    temporary_root / f"worker-{index}",
                    stop,
                    started_events[index],
                    states[index],
                    state_lock,
                ),
                name=f"compile-worker-{index}",
            )
            thread.start()
            workers.append(thread)
        for event in started_events:
            if not event.wait(timeout=30):
                raise RuntimeError("compile worker failed to start")

        journal.write({
            "event": "workload_started",
            "worker_count": worker_count,
            "source_dir": str(source_dir),
            "command": compile_command(source_dir)[1:],
            "cache_policy": "worker-specific temporary PYTHONPYCACHEPREFIX",
        })

        def heartbeat() -> None:
            while not heartbeat_stop.is_set():
                with state_lock:
                    snapshot = [dict(state) for state in states]
                journal.write({
                    "event": "heartbeat",
                    "live_workers": sum(thread.is_alive() for thread in workers),
                    "workers": snapshot,
                })
                heartbeat_stop.wait(heartbeat_seconds)

        heartbeat_thread = threading.Thread(target=heartbeat, name="workload-heartbeat")
        heartbeat_thread.start()
        artifact_bytes = None
        failure = None
        try:
            time.sleep(warmup_seconds)
            journal.write({
                "event": "capture_started",
                "sample_count": sample_count,
                "cadence_ns": cadence_ns,
                "warmup_seconds": warmup_seconds,
                "live_workers": sum(thread.is_alive() for thread in workers),
            })
            artifact = build_artifact(sample_count, cadence_ns)
            artifact_bytes = (json.dumps(artifact, indent=2, sort_keys=True) + "\n").encode()
            descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(artifact_bytes)
            journal.write({
                "event": "capture_completed",
                "artifact_path": str(output),
                "artifact_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
                "artifact_bytes": len(artifact_bytes),
                "live_workers": sum(thread.is_alive() for thread in workers),
            })
        except BaseException as error:
            failure = error
            journal.write({"event": "capture_failed", "error": repr(error)})
        finally:
            alive_during_capture = [thread.is_alive() for thread in workers]
            stop.set()
            for thread in workers:
                thread.join(timeout=120)
            heartbeat_stop.set()
            heartbeat_thread.join(timeout=30)
            with state_lock:
                terminal_states = [
                    {**dict(state), "alive_during_capture": alive_during_capture[index]}
                    for index, state in enumerate(states)
                ]
            journal.write({
                "event": "workload_stopped",
                "worker_count": worker_count,
                "live_workers_after_join": sum(thread.is_alive() for thread in workers),
                "workers": terminal_states,
            })
            journal.close()
        if failure is not None:
            raise failure
        if artifact_bytes is None:
            raise RuntimeError("capture produced no artifact")
        return {
            "output": str(output),
            "output_sha256": hashlib.sha256(artifact_bytes).hexdigest(),
            "output_bytes": len(artifact_bytes),
            "journal": str(journal_path),
            "workers": terminal_states,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("journal", type=Path)
    parser.add_argument("--source-dir", type=Path, default=Path("src"))
    parser.add_argument("--sample-count", type=int, default=360_001)
    parser.add_argument("--cadence-ms", type=int, default=10)
    parser.add_argument("--worker-count", type=int, default=2)
    parser.add_argument("--warmup-seconds", type=float, default=30.0)
    args = parser.parse_args()
    result = run_loaded_capture(
        args.output,
        args.journal,
        args.source_dir,
        args.sample_count,
        args.cadence_ms * 1_000_000,
        args.worker_count,
        args.warmup_seconds,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
