from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import append_entry, build_entry, load_entries, markdown, verify_entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VEC run provenance ledger.")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    add = subparsers.add_parser("add")
    add.add_argument("--ledger", type=Path, default=Path("runs.jsonl"))
    add.add_argument("--board", required=True)
    add.add_argument("--artifact", type=Path, required=True)
    add.add_argument("--command", required=True)
    add.add_argument("--metrics", type=Path)
    add.add_argument("--notes", default="")
    add.add_argument("--git-sha")

    render = subparsers.add_parser("render")
    render.add_argument("--ledger", type=Path, default=Path("runs.jsonl"))
    render.add_argument("--out", type=Path, default=Path("RUNS.md"))

    verify = subparsers.add_parser("verify")
    verify.add_argument("--ledger", type=Path, default=Path("runs.jsonl"))

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command_name == "add":
        metrics = None
        if args.metrics:
            metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
        entry = build_entry(
            args.board,
            args.artifact,
            args.command,
            notes=args.notes,
            metrics=metrics,
            git_sha=args.git_sha,
        )
        append_entry(args.ledger, entry)
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        return 0

    entries = load_entries(args.ledger)
    if args.command_name == "render":
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(markdown(entries), encoding="utf-8")
        print(args.out)
        return 0

    results = verify_entries(entries)
    for result in results:
        print(result["status"], result["artifact"])
    return 1 if any(result["status"] != "OK" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
