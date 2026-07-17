"""Live model rebuild loop and optional QueryCAD web studio process."""

from __future__ import annotations

import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen

type Fingerprint = tuple[int, int]
type Snapshot = dict[Path, Fingerprint]


@dataclass(frozen=True)
class PreviewOptions:
    design: Path
    host: str = "127.0.0.1"
    port: int = 5173
    poll_interval: float = 0.25
    debounce: float = 0.35
    start_web: bool = True
    once: bool = False


@dataclass
class PreviewLock:
    path: Path
    descriptor: int

    def release(self) -> None:
        os.close(self.descriptor)
        try:
            owner = int(self.path.read_text(encoding="utf-8").strip())
        except (FileNotFoundError, ValueError):
            return
        if owner == os.getpid():
            self.path.unlink(missing_ok=True)


def _find_repo_root(start: Path) -> Path:
    candidates = (start.resolve(), Path(__file__).resolve())
    for candidate in candidates:
        for parent in (candidate, *candidate.parents):
            if (parent / "pyproject.toml").is_file() and (parent / "web/package.json").is_file():
                return parent
    raise ValueError("could not find the QueryCAD repository root")


def _fingerprint(path: Path) -> Fingerprint:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return (-1, -1)
    return (stat.st_mtime_ns, stat.st_size)


def watched_snapshot(source_root: Path, design: Path, pyproject: Path) -> Snapshot:
    """Return cheap change fingerprints for model code and the selected design."""
    paths = set(source_root.rglob("*.py"))
    paths.update((design, pyproject))
    return {path.resolve(): _fingerprint(path) for path in sorted(paths)}


def changed_files(previous: Snapshot, current: Snapshot) -> tuple[Path, ...]:
    return tuple(
        sorted(
            path
            for path in previous.keys() | current.keys()
            if previous.get(path) != current.get(path)
        )
    )


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def _process_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_preview_lock(build_root: Path, design: Path) -> PreviewLock:
    build_root.mkdir(parents=True, exist_ok=True)
    lock_path = build_root / f".preview-{design.stem}.lock"
    for _ in range(2):
        try:
            descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            try:
                owner = int(lock_path.read_text(encoding="utf-8").strip())
            except (OSError, ValueError):
                owner = -1
            if owner > 0 and _process_is_running(owner):
                raise ValueError(
                    f"another preview watcher is already running for {design.name} (PID {owner})"
                ) from None
            lock_path.unlink(missing_ok=True)
            continue
        os.write(descriptor, f"{os.getpid()}\n".encode())
        return PreviewLock(lock_path, descriptor)
    raise ValueError(f"could not acquire preview lock {lock_path}")


def _catalog_revision(repo_root: Path, design: Path) -> str | None:
    try:
        catalog = json.loads((repo_root / "build/catalog.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    for entry in catalog.get("designs", []):
        if isinstance(entry, dict) and entry.get("id") == design.stem:
            revision = entry.get("revision")
            return revision if isinstance(revision, str) else None
    return None


def _build_once(
    design: Path,
    repo_root: Path,
    changed: tuple[Path, ...] = (),
) -> int:
    previous_revision = _catalog_revision(repo_root, design)
    started = time.monotonic()
    print(f"\n[querycad] rebuilding {_display_path(design, repo_root)}", flush=True)
    result = subprocess.run(
        [sys.executable, "-m", "querycad", "build", str(design)],
        cwd=repo_root,
        check=False,
    )
    elapsed = time.monotonic() - started
    if result.returncode == 0:
        revision = _catalog_revision(repo_root, design)
        if changed and revision == previous_revision:
            print(
                f"[querycad] build ready in {elapsed:.2f}s, but GLB geometry is unchanged",
                flush=True,
            )
            if design.resolve() not in changed:
                print(
                    "[querycad] note: values explicitly set in the design JSON override "
                    "Python spec defaults",
                    flush=True,
                )
        else:
            suffix = f" · revision {revision}" if revision else ""
            print(f"[querycad] model ready in {elapsed:.2f}s{suffix}", flush=True)
    else:
        print(
            f"[querycad] build failed in {elapsed:.2f}s; fix the error and save again",
            file=sys.stderr,
            flush=True,
        )
    return result.returncode


def _studio_url(host: str, port: int) -> str:
    return f"http://{host}:{port}"


def _querycad_studio_is_running(host: str, port: int) -> bool:
    try:
        with urlopen(f"{_studio_url(host, port)}/catalog.json", timeout=0.4) as response:
            payload = json.load(response)
    except (OSError, TimeoutError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and payload.get("schemaVersion") == 1


def _port_is_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.3):
            return True
    except OSError:
        return False


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        os.killpg(process.pid, signal.SIGTERM)
    else:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait(timeout=5)


def _start_studio(repo_root: Path, host: str, port: int) -> subprocess.Popen[bytes] | None:
    url = _studio_url(host, port)
    if _querycad_studio_is_running(host, port):
        print(f"[querycad] reusing the running studio at {url}", flush=True)
        return None
    if _port_is_open(host, port):
        raise ValueError(f"port {port} is already used by a non-QueryCAD service")

    npm = shutil.which("npm")
    if npm is None:
        raise ValueError("npm is required to start the QueryCAD web studio")
    if not (repo_root / "web/node_modules/.bin/vite").exists():
        raise ValueError("web dependencies are missing; run 'cd web && npm install' first")

    print(f"[querycad] starting the studio at {url}", flush=True)
    process = subprocess.Popen(
        [npm, "run", "dev:ui", "--", "--host", host, "--port", str(port)],
        cwd=repo_root / "web",
        start_new_session=os.name == "posix",
    )
    deadline = time.monotonic() + 20
    ready = False
    try:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise ValueError(f"web studio exited with status {process.returncode}")
            if _querycad_studio_is_running(host, port):
                print(f"[querycad] studio ready: {url}", flush=True)
                ready = True
                return process
            time.sleep(0.15)
    finally:
        if not ready:
            _terminate_process(process)

    raise ValueError("web studio did not become ready within 20 seconds")


def _settle_changes(
    previous: Snapshot,
    current: Snapshot,
    source_root: Path,
    design: Path,
    pyproject: Path,
    poll_interval: float,
    debounce: float,
) -> tuple[Snapshot, tuple[Path, ...]]:
    pending = set(changed_files(previous, current))
    quiet_since = time.monotonic()
    settled = current
    while time.monotonic() - quiet_since < debounce:
        time.sleep(poll_interval)
        next_snapshot = watched_snapshot(source_root, design, pyproject)
        additional = changed_files(settled, next_snapshot)
        if additional:
            pending.update(additional)
            quiet_since = time.monotonic()
        settled = next_snapshot
    return settled, tuple(sorted(pending))


def run_preview(options: PreviewOptions) -> int:
    if options.port < 1 or options.port > 65535:
        raise ValueError("port must be between 1 and 65535")
    if options.poll_interval <= 0:
        raise ValueError("poll_interval must be greater than zero")
    if options.debounce < 0:
        raise ValueError("debounce cannot be negative")

    repo_root = _find_repo_root(Path.cwd())
    design = options.design.resolve()
    source_root = repo_root / "src/querycad"
    pyproject = repo_root / "pyproject.toml"
    preview_lock = acquire_preview_lock(repo_root / "build", design)
    studio: subprocess.Popen[bytes] | None = None
    studio_owned = False
    try:
        snapshot = watched_snapshot(source_root, design, pyproject)
        build_status = _build_once(design, repo_root)
        if options.once:
            return build_status

        if options.start_web:
            studio = _start_studio(repo_root, options.host, options.port)
            studio_owned = studio is not None

        print(
            "[querycad] watching the design JSON and src/querycad/**/*.py; press Ctrl-C to stop",
            flush=True,
        )
        while True:
            if studio is not None and studio.poll() is not None:
                print(
                    f"[querycad] web studio stopped with status {studio.returncode}",
                    file=sys.stderr,
                )
                return studio.returncode or 1

            time.sleep(options.poll_interval)
            current = watched_snapshot(source_root, design, pyproject)
            if not changed_files(snapshot, current):
                continue
            snapshot, pending = _settle_changes(
                snapshot,
                current,
                source_root,
                design,
                pyproject,
                options.poll_interval,
                options.debounce,
            )
            names = ", ".join(_display_path(path, repo_root) for path in pending)
            print(f"[querycad] change detected: {names}", flush=True)
            _build_once(design, repo_root, pending)
    except KeyboardInterrupt:
        print("\n[querycad] preview stopped", flush=True)
        return 0
    finally:
        if studio_owned and studio is not None:
            _terminate_process(studio)
        preview_lock.release()
