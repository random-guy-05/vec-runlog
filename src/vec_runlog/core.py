from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_git_sha(cwd: Path | None = None) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def build_entry(
    board: str,
    artifact: Path,
    command: str,
    *,
    notes: str = "",
    metrics: dict[str, Any] | None = None,
    git_sha: str | None = None,
) -> dict[str, Any]:
    resolved = artifact.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "board": board,
        "artifact": str(resolved),
        "sha256": sha256_file(resolved),
        "size_bytes": resolved.stat().st_size,
        "command": command,
        "git_sha": git_sha or current_git_sha(),
        "metrics": metrics,
        "notes": notes,
    }


def append_entry(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(serialized + "\n")
        handle.flush()


def load_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
    return entries


def verify_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for entry in entries:
        path = Path(entry["artifact"])
        expected = str(entry["sha256"])
        if not path.is_file():
            output.append(
                {
                    "artifact": str(path),
                    "status": "MISSING",
                    "expected": expected,
                    "actual": None,
                }
            )
            continue
        actual = sha256_file(path)
        output.append(
            {
                "artifact": str(path),
                "status": "OK" if actual == expected else "CHANGED",
                "expected": expected,
                "actual": actual,
            }
        )
    return output


def markdown(entries: list[dict[str, Any]]) -> str:
    lines = [
        "# VEC RunLog",
        "",
        "| time (UTC) | board | artifact | SHA256 | git | notes |",
        "|---|---|---|---|---|---|",
    ]
    for entry in entries:
        artifact = Path(entry["artifact"]).name
        notes = str(entry.get("notes", "")).replace("|", "/").replace("\n", " ")
        git_sha = str(entry.get("git_sha") or "")
        lines.append(
            f"| {entry['timestamp_utc']} | {entry['board']} | `{artifact}` | "
            f"`{entry['sha256'][:12]}` | `{git_sha[:12]}` | {notes} |"
        )
    return "\n".join(lines) + "\n"
