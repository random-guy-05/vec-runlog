# Community Contribution submission text

## Title
VEC RunLog — append-only experiment and submission provenance ledger

## Description
VEC RunLog records the exact provenance of prediction artifacts in a simple append-only JSONL ledger: board, absolute artifact path, SHA-256, byte size, generation command, Git commit, optional local metric JSON, UTC timestamp and notes. It can render a readable run table and later re-hash every recorded file to detect overwritten or changed artifacts. The tool addresses a practical reproducibility failure mode during checkpoint/model selection and scarce final submissions: knowing exactly which immutable file produced a result and how to recreate it. It reads no Challenge data and has no external runtime dependencies.
