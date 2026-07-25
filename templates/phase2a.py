"""
interruptllm phase2a — MLFQ scheduler simulation with real workload trace.

Loads the Kaggle LLM inference logs, maps Task_Type to InterruptLLM priorities,
and compares three schedulers:
  1. FCFS (vLLM-style continuous batching, non-preemptive)
  2. Non-preemptive priority queue
  3. InterruptLLM MLFQ with true preemption

Outputs metrics and a comparison plot to /kaggle/working/.
"""

import os
import sys

_core_path = next(
    (dirpath for dirpath, _, filenames in os.walk("/kaggle/input")
     if "interruptllm_core.py" in filenames),
    None,
)
if _core_path is None:
    raise ImportError("interruptllm_core.py not found under /kaggle/input")
sys.path.insert(0, _core_path)

import interruptllm_core as core

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Locate the public trace dataset.
# ---------------------------------------------------------------------------
csv_path = core.find_dataset_file("llm_inference_logs", "/kaggle/input")
if csv_path is None:
    print("ERROR: could not find llm_inference_logs CSV under /kaggle/input")
    for dirpath, _, filenames in os.walk("/kaggle/input"):
        for f in filenames:
            print("  ", os.path.join(dirpath, f))
    raise FileNotFoundError("llm_inference_logs CSV not found")
print(f"Using trace: {csv_path}")

# ---------------------------------------------------------------------------
# Load and prepare requests.
# ---------------------------------------------------------------------------
CAPACITY_TOKENS_PER_MS = 300.0
INTER_ARRIVAL_MS = 3.5
TOKEN_SCALE = 0.20
QUANTUM_MS = 100.0
SWAP_TIME_MS = 0.5
MAX_BATCH_SIZE = 16
OVERHEAD_MS = 0.1
DT_MS = 1.0

requests = core.build_requests_from_trace(
    csv_path,
    max_rows=2000,
    token_scale=TOKEN_SCALE,
    inter_arrival_ms=INTER_ARRIVAL_MS,
)

load_factor = (len(requests) / max(1, (len(requests) - 1) * INTER_ARRIVAL_MS)) * (np.mean([r["tokens"] for r in requests])) / CAPACITY_TOKENS_PER_MS
print(f"Loaded {len(requests)} requests")
print(f"Load factor: {load_factor:.2f}")
print(f"Priority distribution: P0={sum(1 for r in requests if r['priority']==0)}, "
      f"P1={sum(1 for r in requests if r['priority']==1)}, "
      f"P2={sum(1 for r in requests if r['priority']==2)}, "
      f"P3={sum(1 for r in requests if r['priority']==3)}")

# ---------------------------------------------------------------------------
# Run schedulers.
# ---------------------------------------------------------------------------
fcfs = core.simulate_scheduler(
    [dict(r) for r in requests],
    scheduler="fcfs",
    capacity_tokens_per_ms=CAPACITY_TOKENS_PER_MS,
    max_batch_size=MAX_BATCH_SIZE,
    overhead_ms=OVERHEAD_MS,
    dt_ms=DT_MS,
    quantum_ms=QUANTUM_MS,
)

npp = core.simulate_scheduler(
    [dict(r) for r in requests],
    scheduler="priority",
    capacity_tokens_per_ms=CAPACITY_TOKENS_PER_MS,
    max_batch_size=MAX_BATCH_SIZE,
    overhead_ms=OVERHEAD_MS,
    dt_ms=DT_MS,
    quantum_ms=QUANTUM_MS,
)

mlfq = core.simulate_scheduler(
    [dict(r) for r in requests],
    scheduler="mlfq",
    capacity_tokens_per_ms=CAPACITY_TOKENS_PER_MS,
    max_batch_size=MAX_BATCH_SIZE,
    overhead_ms=OVERHEAD_MS,
    swap_time_ms=SWAP_TIME_MS,
    dt_ms=DT_MS,
    quantum_ms=QUANTUM_MS,
)

print("\n--- FCFS ---")
print(f"  P99 latency: {fcfs['p99_latency_ms']:.2f} ms")
print(f"  P0 P99:      {fcfs['per_priority_p99_ms']['p0']:.2f} ms")
print(f"  P1 P99:      {fcfs['per_priority_p99_ms']['p1']:.2f} ms")
print(f"  Throughput:  {fcfs['throughput_tokens_per_s']:.0f} tok/s")
print(f"  Jain:        {fcfs['jain_fairness']:.3f}")

print("\n--- Non-preemptive priority ---")
print(f"  P99 latency: {npp['p99_latency_ms']:.2f} ms")
print(f"  P0 P99:      {npp['per_priority_p99_ms']['p0']:.2f} ms")
print(f"  P1 P99:      {npp['per_priority_p99_ms']['p1']:.2f} ms")
print(f"  Throughput:  {npp['throughput_tokens_per_s']:.0f} tok/s")
print(f"  Jain:        {npp['jain_fairness']:.3f}")

print("\n--- InterruptLLM MLFQ preemptive ---")
print(f"  P99 latency: {mlfq['p99_latency_ms']:.2f} ms")
print(f"  P0 P99:      {mlfq['per_priority_p99_ms']['p0']:.2f} ms")
print(f"  P1 P99:      {mlfq['per_priority_p99_ms']['p1']:.2f} ms")
print(f"  Throughput:  {mlfq['throughput_tokens_per_s']:.0f} tok/s")
print(f"  Jain:        {mlfq['jain_fairness']:.3f}")
print(f"  Avg preemptions: {mlfq['avg_preemptions']:.3f}")
print(f"  Avg swap time: {mlfq['avg_swap_time_ms']:.3f} ms")

# ---------------------------------------------------------------------------
# Results and plot.
# ---------------------------------------------------------------------------
results = {
    "simulation_complete": True,
    "n_requests": len(requests),
    "load_factor": float(load_factor),
    "capacity_tokens_per_ms": CAPACITY_TOKENS_PER_MS,
    "inter_arrival_ms": INTER_ARRIVAL_MS,
    "token_scale": TOKEN_SCALE,
    "max_batch_size": MAX_BATCH_SIZE,
    "overhead_ms": OVERHEAD_MS,
    "swap_time_ms": SWAP_TIME_MS,
    "quantum_ms": QUANTUM_MS,
    "fcfs": fcfs,
    "non_preemptive_priority": npp,
    "mlfq_preemptive": mlfq,
}

core.save_results(results, "/kaggle/working/phase2a_results.json")

# Bar chart comparing P99 latency and throughput.
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
labels = ["FCFS", "Priority", "InterruptLLM"]

p99_ms = [fcfs["p99_latency_ms"], npp["p99_latency_ms"], mlfq["p99_latency_ms"]]
p0_p99 = [fcfs["per_priority_p99_ms"]["p0"], npp["per_priority_p99_ms"]["p0"], mlfq["per_priority_p99_ms"]["p0"]]
p1_p99 = [fcfs["per_priority_p99_ms"]["p1"], npp["per_priority_p99_ms"]["p1"], mlfq["per_priority_p99_ms"]["p1"]]
tput = [fcfs["throughput_tokens_per_s"], npp["throughput_tokens_per_s"], mlfq["throughput_tokens_per_s"]]
fair = [fcfs["jain_fairness"], npp["jain_fairness"], mlfq["jain_fairness"]]

axes[0, 0].bar(labels, p99_ms, color=["#e74c3c", "#f39c12", "#2ecc71"])
axes[0, 0].set_ylabel("Overall P99 latency (ms)")
axes[0, 0].set_title("Overall tail latency")
axes[0, 0].grid(axis="y", linestyle="--", alpha=0.5)

axes[0, 1].bar(labels, p0_p99, color=["#e74c3c", "#f39c12", "#2ecc71"])
axes[0, 1].axhline(200.0, color="gray", linestyle=":", label="P0 SLA target")
axes[0, 1].set_ylabel("P0 P99 latency (ms)")
axes[0, 1].set_title("Interactive (P0) tail latency")
axes[0, 1].legend()
axes[0, 1].grid(axis="y", linestyle="--", alpha=0.5)

axes[1, 0].bar(labels, tput, color=["#e74c3c", "#f39c12", "#2ecc71"])
axes[1, 0].set_ylabel("Throughput (tokens/s)")
axes[1, 0].set_title("System throughput")
axes[1, 0].grid(axis="y", linestyle="--", alpha=0.5)

axes[1, 1].bar(labels, fair, color=["#e74c3c", "#f39c12", "#2ecc71"])
axes[1, 1].set_ylabel("Jain fairness index")
axes[1, 1].set_ylim(0, 1)
axes[1, 1].set_title("Fairness across tenants")
axes[1, 1].grid(axis="y", linestyle="--", alpha=0.5)

fig.tight_layout()
fig.savefig("/kaggle/working/phase2a_comparison.png", dpi=150)
print(" Saved phase2a_comparison.png")

# Emit greppable result lines.
p0_improvement = fcfs["per_priority_p99_ms"]["p0"] / max(1e-9, mlfq["per_priority_p99_ms"]["p0"])
core.format_result("simulation_complete", True)
core.format_result("n_requests", len(requests))
core.format_result("load_factor", f"{load_factor:.2f}")
core.format_result("fcfs_p99_ms", f"{p99_ms[0]:.2f}")
core.format_result("priority_p99_ms", f"{p99_ms[1]:.2f}")
core.format_result("mlfq_p99_ms", f"{p99_ms[2]:.2f}")
core.format_result("fcfs_p0_p99_ms", f"{p0_p99[0]:.2f}")
core.format_result("priority_p0_p99_ms", f"{p0_p99[1]:.2f}")
core.format_result("mlfq_p0_p99_ms", f"{p0_p99[2]:.2f}")
core.format_result("p0_improvement_vs_fcfs", f"{p0_improvement:.2f}x")
core.format_result("fcfs_throughput_tok_s", f"{tput[0]:.0f}")
core.format_result("priority_throughput_tok_s", f"{tput[1]:.0f}")
core.format_result("mlfq_throughput_tok_s", f"{tput[2]:.0f}")
core.format_result("fcfs_jain", f"{fair[0]:.3f}")
core.format_result("priority_jain", f"{fair[1]:.3f}")
core.format_result("mlfq_jain", f"{fair[2]:.3f}")
core.format_result("mlfq_avg_preemptions", f"{mlfq['avg_preemptions']:.3f}")
core.format_result("mlfq_avg_swap_ms", f"{mlfq['avg_swap_time_ms']:.3f}")

print("\nDone.")
