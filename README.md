# VEC RunLog

A small, append-only provenance ledger for VEC experiments and submission artifacts.

The useful question after a promising local score is often not "what model was this?" but:

- which exact file was scored?
- what command produced it?
- which Git commit was checked out?
- what was the artifact SHA-256?
- did the file change after it was logged?

RunLog records those facts in JSONL and can render a human-readable Markdown table or re-hash every artifact later.

## Usage

```bash
pip install -e .

vec-runlog add \
  --ledger runs.jsonl \
  --board T2:heart:val_extrap \
  --artifact predictions/model17.h5ad \
  --command "python export.py --checkpoint ckpt17" \
  --metrics local_score.json \
  --notes "seed 4; best extrap candidate"

vec-runlog render --ledger runs.jsonl --out RUNS.md
vec-runlog verify --ledger runs.jsonl
```

If `--git-sha` is omitted, RunLog records the current repository HEAD when available.

RunLog never reads Challenge data and never modifies logged artifacts.
