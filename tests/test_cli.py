import subprocess
import sys


def test_cli_add_render_verify(tmp_path):
    artifact = tmp_path / "prediction.h5ad"
    artifact.write_bytes(b"synthetic")
    ledger = tmp_path / "runs.jsonl"
    rendered = tmp_path / "RUNS.md"

    add = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_runlog.cli",
            "add",
            "--ledger",
            str(ledger),
            "--board",
            "T1:val",
            "--artifact",
            str(artifact),
            "--command",
            "synthetic-export",
            "--git-sha",
            "deadbeef",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert add.returncode == 0, add.stderr

    render = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_runlog.cli",
            "render",
            "--ledger",
            str(ledger),
            "--out",
            str(rendered),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert render.returncode == 0
    assert "T1:val" in rendered.read_text()

    verify = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_runlog.cli",
            "verify",
            "--ledger",
            str(ledger),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert verify.returncode == 0
    assert "OK" in verify.stdout
