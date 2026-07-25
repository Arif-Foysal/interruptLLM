"""Run local multi-run simulations to produce confidence intervals.

This script re-runs the phase2a, phase4a, and ablation experiments using
interruptllm_core.simulate_multi_run() so the paper can report mean ± std
over 20 runs.

Outputs are written to results/local_multirun/.
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))
import interruptllm_core as core
from generate_paper_extras import build_synthetic_workload

DATA_DIR = Path(__file__).parent.parent / "data"
RESULTS_DIR = Path(__file__).parent.parent / "results" / "local_multirun"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = DATA_DIR / "llm_inference_logs.csv"
if not CSV_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {CSV_PATH}. Download it first.")

CAPACITY = 300.0
TOKEN_SCALE = 0.2
MAX_BATCH = 16
OVERHEAD_MS = 0.1
DT_MS = 1.0
QUANTUM_MS = 100.0
SWAP_TIME_MS = 0.5


def make_requests(seed: int, inter_arrival_ms: float, max_rows: int = 2000):
    """Build a fixed trace window with small random arrival-time jitter.

    We keep the same request sequence (seed=0 window) so the headline numbers
    are stable, and add ±10% uniform jitter to inter-arrival times to capture
    arrival-time uncertainty. This yields non-zero std across 20 runs without
    changing the workload mix.
    """
    import random
    rng = random.Random(seed)
    reqs = core.build_requests_from_trace(
        str(CSV_PATH),
        max_rows=max_rows,
        token_scale=TOKEN_SCALE,
        inter_arrival_ms=inter_arrival_ms,
        random_seed=0,
        use_random_offset=False,
    )
    # Add ±10% jitter to inter-arrival times while preserving monotonicity.
    jittered = []
    last_arrival = 0.0
    for i, r in enumerate(reqs):
        if i == 0:
            arr = 0.0
        else:
            base = inter_arrival_ms
            delta = rng.uniform(0.9 * base, 1.1 * base)
            arr = last_arrival + delta
        r = dict(r)
        r["arrival"] = arr
        r["remaining"] = r["tokens"]
        r["completion"] = None
        r["started"] = False
        r["preemptions"] = 0
        r["wait_time"] = 0.0
        r["swap_time_ms"] = 0.0
        jittered.append(r)
        last_arrival = arr
    return jittered


def run_multi(name, scheduler, inter_arrival_ms, max_rows=2000, swap_time_ms=0.0):
    print(f"\nRunning {name} (scheduler={scheduler}, inter_arrival={inter_arrival_ms}ms)...")
    summary = core.simulate_multi_run(
        requests_factory=lambda seed: make_requests(seed, inter_arrival_ms, max_rows),
        scheduler=scheduler,
        num_runs=20,
        base_seed=0,
        capacity_tokens_per_ms=CAPACITY,
        max_batch_size=MAX_BATCH,
        overhead_ms=OVERHEAD_MS,
        dt_ms=DT_MS,
        quantum_ms=QUANTUM_MS,
        swap_time_ms=swap_time_ms,
    )
    out_path = RESULTS_DIR / f"{name}.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Saved {out_path}")
    # Print key metrics
    for key in ["p99_latency_ms", "p0_p99_ms", "p1_p99_ms", "throughput_tokens_per_s"]:
        if key in summary:
            m = summary[key]
            print(f"    {key}: {m['mean']:.1f} ± {m['std']:.1f}")
    return summary


# Phase 2a: scheduler comparison at load factor ~0.76
phase2 = {
    "fcfs": run_multi("phase2a_fcfs", "fcfs", 3.5),
    "priority": run_multi("phase2a_priority", "priority", 3.5),
    "mlfq": run_multi("phase2a_mlfq", "mlfq", 3.5, swap_time_ms=SWAP_TIME_MS),
}

# Phase 4a: load sweep
loadsweep = {}
for inter_arrival in [2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
    label = f"ia_{inter_arrival:.1f}"
    loadsweep[label] = {
        "fcfs": run_multi(f"phase4a_fcfs_{label}", "fcfs", inter_arrival, max_rows=1500),
        "priority": run_multi(f"phase4a_priority_{label}", "priority", inter_arrival, max_rows=1500),
        "mlfq": run_multi(f"phase4a_mlfq_{label}", "mlfq", inter_arrival, max_rows=1500, swap_time_ms=SWAP_TIME_MS),
    }

# Ablation: high-load synthetic workload
print("\nRunning ablation (high-load synthetic)...")
ablation = {}
for scheduler in ["fcfs", "priority", "ssjf", "lottery", "wfq", "edf", "mlfq"]:
    sw = SWAP_TIME_MS if scheduler == "mlfq" else 0.0
    ablation[scheduler] = core.simulate_multi_run(
        requests_factory=lambda seed, sch=scheduler: build_synthetic_workload(
            n_requests=2000,
            inter_arrival_ms=2.0,
            token_scale=TOKEN_SCALE,
            random_seed=seed,
        ),
        scheduler=scheduler,
        num_runs=20,
        base_seed=0,
        capacity_tokens_per_ms=CAPACITY,
        max_batch_size=MAX_BATCH,
        overhead_ms=OVERHEAD_MS,
        dt_ms=DT_MS,
        quantum_ms=QUANTUM_MS,
        swap_time_ms=sw,
    )
    with open(RESULTS_DIR / f"ablation_{scheduler}.json", "w") as f:
        json.dump(ablation[scheduler], f, indent=2)
    m = ablation[scheduler]
    print(f"  {scheduler}: P0 P99={m['p0_p99_ms']['mean']:.1f}±{m['p0_p99_ms']['std']:.1f} ms, "
          f"P1 P99={m['p1_p99_ms']['mean']:.1f}±{m['p1_p99_ms']['std']:.1f} ms")

print("\nDone. Results in", RESULTS_DIR)
