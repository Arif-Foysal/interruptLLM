# InterruptLLM Kaggle Pipeline — Quickstart

This repo uses the OpenCode Kaggle ML-Ops harness described in `OPENCODE_REPLICATION_GUIDE.md`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` with your Kaggle API token:

```bash
KAGGLE_API_TOKEN=KGAT_your_token_here
```

## Edit before running

Kaggle username is already set to `mdzero591` in `config.yaml`.

## First run (smoke test)

```bash
python pipeline.py upload-src
# wait ~5 minutes
python pipeline.py generate phase1a
python pipeline.py push notebooks/phase1a.py
python pipeline.py wait phase1a
python pipeline.py fetch phase1a
python pipeline.py results phase1a
```

## Phases

| Phase | Template | Purpose |
|-------|----------|---------|
| phase1a | `templates/phase1a.py` | Smoke test and harness validation |
| phase2a | `templates/phase2a.py` | MLFQ scheduler simulation |
| phase3a | `templates/phase3a.py` | Context swap latency benchmark |
| phase4a | `templates/phase4a.py` | End-to-end latency/fairness evaluation |

## Next steps

1. Fill `src/interruptllm_core.py` with real simulation / math code.
2. Refine `templates/phase2a.py`, `phase3a.py`, and `phase4a.py` to match the paper experiments.
3. Use `python pipeline.py upload-results <phase>` to pass intermediate outputs between phases.
