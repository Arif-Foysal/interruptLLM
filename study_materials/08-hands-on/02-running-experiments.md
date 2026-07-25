# 02 — Running Experiments

> This note explains how to run the InterruptLLM simulations locally and reproduce the paper results.

## Setup

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Common dependencies include:

- `numpy`
- `pandas`
- `matplotlib` (for plotting)
- `pyyaml` (for config)

> [!tip]
> If you are on a machine without a GPU, that is fine. The simulator is CPU-only. Only the phase5a GPU benchmark needs a GPU.

### 2. Download the dataset

The Kaggle dataset is already in `data/llm_inference_logs.csv` if the project is fully set up.

If you need to download it:

```bash
kaggle datasets download bektursyn/llm-inference-logs-and-performance-metrics
```

### 3. Run the local multi-run script

The easiest way to reproduce the main results is:

```bash
python scripts/run_local_multirun.py
```

This script will:

- Load the trace
- Run phase2a (scheduler comparison) 20 times with jitter
- Run phase4a (load sweep) 20 times with jitter
- Save results to `results/local_multirun/`

## What to expect

The script will print progress like:

```
[RUN] phase2a seed=0
[RESULT] p0_p99_ms = 55.3
[RUN] phase2a seed=1
...
[SUMMARY] phase2a p0_p99_ms: 56.5 ± 1.1
```

Results are saved as JSON files:

```
results/local_multirun/
├── phase2a/
│   └── phase2a_results.json
└── phase4a/
    └── phase4a_results.json
```

## Running a single experiment

You can also run a small experiment manually:

```python
import csv
import numpy as np
from src.interruptllm_core import (
    load_llm_trace,
    build_requests_from_trace,
    simulate_mlfq,
    compute_metrics,
)

# Load first 1000 rows
trace = load_llm_trace("data/llm_inference_logs.csv", max_rows=1000)

# Build requests
requests = build_requests_from_trace(
    trace,
    gpu_capacity_tok_ms=300,
    scale_factor=0.2,
    target_load_factor=0.76,
    seed=42,
)

# Run MLFQ
metrics = simulate_mlfq(requests, batch_capacity=16, swap_penalty_ms=0.5)

# Print results
print(f"P0 P99: {metrics['p0_p99_ms']:.1f} ms")
print(f"Throughput: {metrics['throughput_tok_s']:.0f} tok/s")
```

## Running the ablation study

```bash
python scripts/generate_paper_extras.py
```

This generates synthetic results for Table IV (ablation). It does not require the Kaggle trace.

## Running the GPU benchmark

The GPU benchmark requires a GPU with PyTorch installed:

```bash
python templates/phase5a.py
```

On Kaggle, the notebook handles PyTorch installation automatically.

> [!warning]
> The phase5a benchmark will fail on a CPU-only machine because it tries to allocate tensors on GPU.

## Running on Kaggle

If you have Kaggle credentials:

```bash
python pipeline.py upload-src
python pipeline.py generate
python pipeline.py push
python pipeline.py wait
python pipeline.py fetch
python pipeline.py results
```

> [!tip]
> For local learning, `run_local_multirun.py` is sufficient. The Kaggle pipeline is needed only if you want to run the exact GPU benchmark on P100.

## Check your understanding

- [ ] I can install the project dependencies.
- [ ] I can run the local multi-run script.
- [ ] I know where results are saved.
- [ ] I can run a single experiment manually.

## Exercises

1. Run `python scripts/run_local_multirun.py` and check the output in `results/local_multirun/`.
2. Modify the manual script to run FCFS instead of MLFQ. How do P0 P99 and throughput change?
3. Try changing the load factor from 0.76 to 0.93. What happens to P0 P99 under FCFS and MLFQ?

> [!important]
> Reproducing results is one of the best ways to understand a paper. Numbers that looked abstract in the paper become concrete when you compute them yourself.

> [!question]
> After running the experiments, compare your results to the paper. Are they close? If not, why might they differ? (Hint: small differences in trace preprocessing or random seeds can shift numbers.)
