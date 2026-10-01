import json

import pytest

from vec_runlog.core import (
    append_entry,
    build_entry,
    load_entries,
    markdown,
    verify_entries,
)


def test_roundtrip_and_change_detection(tmp_path):
    artifact = tmp_path / "prediction.h5ad"
    artifact.write_bytes(b"hello")
    entry = build_entry(
        "T1:val",
        artifact,
        "python export.py",
        git_sha="abc123",
    )
    ledger = tmp_path / "runs.jsonl"
    append_entry(ledger, entry)
    rows = load_entries(ledger)
    assert rows[0]["sha256"] == entry["sha256"]
    assert verify_entries(rows)[0]["status"] == "OK"

    artifact.write_bytes(b"changed")
    assert verify_entries(rows)[0]["status"] == "CHANGED"


def test_invalid_jsonl_reports_line(tmp_path):
    ledger = tmp_path / "bad.jsonl"
    ledger.write_text('{"ok": 1}\nnot-json\n')
    with pytest.raises(ValueError, match="line 2"):
        load_entries(ledger)


def test_markdown_escapes_table_separator(tmp_path):
    artifact = tmp_path / "x"
    artifact.write_text("x")
    entry = build_entry(
        "T3:gata4",
        artifact,
        "cmd",
        notes="a|b",
        git_sha="1234567890abcdef",
    )
    text = markdown([entry])
    assert "a/b" in text


def test_metrics_can_be_serialized(tmp_path):
    artifact = tmp_path / "x"
    artifact.write_bytes(b"x")
    entry = build_entry(
        "T1:val",
        artifact,
        "cmd",
        metrics={"score": 0.5},
        git_sha="abc",
    )
    assert json.loads(json.dumps(entry))["metrics"]["score"] == 0.5
