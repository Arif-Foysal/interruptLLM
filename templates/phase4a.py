"""
interruptllm phase4a — end-to-end latency and fairness evaluation.

Runs the full InterruptLLM system against baselines using the real Kaggle trace
across multiple load factors. Reports P99 latency, SLA violation rates,
throughput, Jain fairness, and creates paper-ready comparison figures.
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
# Locate and load trace.
# ---------------------------------------------------------------------------
csv_path = core.find_dataset_file("llm_inference_logs", "/kaggle/input")
if csv_path is None:
    raise FileNotFoundError("llm_inference_logs CSV not found")
print(f"Using trace: {csv_path}")

# ---------------------------------------------------------------------------
# Configuration.
# ---------------------------------------------------------------------------
CAPACITY_TOKENS_PER_MS = 300.0
MAX_BATCH_SIZE = 16
OVERHEAD_MS = 0.1
DT_MS = 1.0
QUANTUM_MS = 100.0
SWAP_TIME_MS = 0.5
TOKEN_SCALE = 0.20
MAX_ROWS = 1500
INTER_ARRIVAL_MS_VALUES = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

# ---------------------------------------------------------------------------
# Sweep load factors (20 runs per point with arrival-time jitter).
# ---------------------------------------------------------------------------
def _make_requests(ia: float, seed: int):
    """Build a fixed trace window with small arrival-time jitter."""
    import random
    rng = random.Random(seed)
    reqs = core.build_requests_from_trace(
        csv_path,
        max_rows=MAX_ROWS,
        token_scale=TOKEN_SCALE,
        inter_arrival_ms=ia,
    )
    jittered = []
    last_arrival = 0.0
    for i, r in enumerate(reqs):
        if i == 0:
            arr = 0.0
        else:
            delta = rng.uniform(0.9 * ia, 1.1 * ia)
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


base_kwargs = {
    "capacity_tokens_per_ms": CAPACITY_TOKENS_PER_MS,
    "max_batch_size": MAX_BATCH_SIZE,
    "overhead_ms": OVERHEAD_MS,
    "dt_ms": DT_MS,
    "quantum_ms": QUANTUM_MS,
}

sweep = []
for ia in INTER_ARRIVAL_MS_VALUES:
    _sample = core.build_requests_from_trace(
        csv_path,
        max_rows=MAX_ROWS,
        token_scale=TOKEN_SCALE,
        inter_arrival_ms=ia,
    )
    load_factor = (len(_sample) / max(1, (len(_sample) - 1) * ia)) * (np.mean([r["tokens"] for r in _sample])) / CAPACITY_TOKENS_PER_MS
    print(f"\n--- inter-arrival={ia}ms, load={load_factor:.2f}, n={len(_sample)} ---")

    fcfs_summary = core.simulate_multi_run(
        requests_factory=lambda seed, ia=ia: _make_requests(ia, seed),
        scheduler="fcfs",
        num_runs=20,
        base_seed=0,
        **base_kwargs,
    )
    npp_summary = core.simulate_multi_run(
        requests_factory=lambda seed, ia=ia: _make_requests(ia, seed),
        scheduler="priority",
        num_runs=20,
        base_seed=0,
        **base_kwargs,
    )
    mlfq_summary = core.simulate_multi_run(
        requests_factory=lambda seed, ia=ia: _make_requests(ia, seed),
        scheduler="mlfq",
        num_runs=20,
        base_seed=0,
        swap_time_ms=SWAP_TIME_MS,
        **base_kwargs,
    )

    def _extract(summary):
        out = {k: v["mean"] if isinstance(v, dict) and "mean" in v else v for k, v in summary.items()}
        out["per_priority_p99_ms"] = {p: summary[f"{p}_p99_ms"]["mean"] for p in ["p0", "p1", "p2", "p3"]}
        out["sla_violation_rates"] = {p: summary[f"{p}_sla_violation_rate"]["mean"] for p in ["p0", "p1", "p2", "p3"]}
        return out

    fcfs = _extract(fcfs_summary)
    npp = _extract(npp_summary)
    mlfq = _extract(mlfq_summary)

    print(f"  FCFS:  P0={fcfs['per_priority_p99_ms']['p0']:.0f}ms P99={fcfs['p99_latency_ms']:.0f}ms tput={fcfs['throughput_tokens_per_s']:.0f}")
    print(f"  Prior: P0={npp['per_priority_p99_ms']['p0']:.0f}ms P99={npp['p99_latency_ms']:.0f}ms tput={npp['throughput_tokens_per_s']:.0f}")
    print(f"  MLFQ:  P0={mlfq['per_priority_p99_ms']['p0']:.0f}ms P99={mlfq['p99_latency_ms']:.0f}ms tput={mlfq['throughput_tokens_per_s']:.0f} preempt={mlfq['avg_preemptions']:.2f}")

    sweep.append({
        "inter_arrival_ms": ia,
        "load_factor": float(load_factor),
        "n_requests": len(_sample),
        "fcfs_summary": fcfs_summary,
        "priority_summary": npp_summary,
        "mlfq_summary": mlfq_summary,
        "fcfs": fcfs,
        "non_preemptive_priority": npp,
        "mlfq_preemptive": mlfq,
    })

# ---------------------------------------------------------------------------
# Select a representative high-load point for detailed comparison.
# ---------------------------------------------------------------------------
best_idx = min(range(len(sweep)), key=lambda i: abs(sweep[i]["load_factor"] - 0.95))
point = sweep[best_idx]
print(f"\nSelected representative point: load={point['load_factor']:.2f}, ia={point['inter_arrival_ms']}ms")

fcfs = point["fcfs"]
npp = point["non_preemptive_priority"]
mlfq = point["mlfq_preemptive"]

# ---------------------------------------------------------------------------
# Paper-ready plots.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

loads = [s["load_factor"] for s in sweep]

# 1. P0 P99 vs load.
axes[0, 0].plot(loads, [s["fcfs"]["per_priority_p99_ms"]["p0"] for s in sweep], marker="o", color="#e74c3c", label="FCFS")
axes[0, 0].plot(loads, [s["non_preemptive_priority"]["per_priority_p99_ms"]["p0"] for s in sweep], marker="s", color="#f39c12", label="Priority")
axes[0, 0].plot(loads, [s["mlfq_preemptive"]["per_priority_p99_ms"]["p0"] for s in sweep], marker="^", color="#2ecc71", label="InterruptLLM")
axes[0, 0].axhline(200.0, color="gray", linestyle=":", label="P0 SLA target")
axes[0, 0].set_xlabel("Load factor")
axes[0, 0].set_ylabel("P0 P99 latency (ms)")
axes[0, 0].set_title("Interactive (P0) tail latency vs. load")
axes[0, 0].legend()
axes[0, 0].grid(linestyle="--", alpha=0.5)

# 2. Overall P99 vs load.
axes[0, 1].plot(loads, [s["fcfs"]["p99_latency_ms"] for s in sweep], marker="o", color="#e74c3c", label="FCFS")
axes[0, 1].plot(loads, [s["non_preemptive_priority"]["p99_latency_ms"] for s in sweep], marker="s", color="#f39c12", label="Priority")
axes[0, 1].plot(loads, [s["mlfq_preemptive"]["p99_latency_ms"] for s in sweep], marker="^", color="#2ecc71", label="InterruptLLM")
axes[0, 1].set_xlabel("Load factor")
axes[0, 1].set_ylabel("Overall P99 latency (ms)")
axes[0, 1].set_title("Overall tail latency vs. load")
axes[0, 1].legend()
axes[0, 1].grid(linestyle="--", alpha=0.5)

# 3. Throughput vs load.
axes[1, 0].plot(loads, [s["fcfs"]["throughput_tokens_per_s"] for s in sweep], marker="o", color="#e74c3c", label="FCFS")
axes[1, 0].plot(loads, [s["non_preemptive_priority"]["throughput_tokens_per_s"] for s in sweep], marker="s", color="#f39c12", label="Priority")
axes[1, 0].plot(loads, [s["mlfq_preemptive"]["throughput_tokens_per_s"] for s in sweep], marker="^", color="#2ecc71", label="InterruptLLM")
axes[1, 0].set_xlabel("Load factor")
axes[1, 0].set_ylabel("Throughput (tokens/s)")
axes[1, 0].set_title("Throughput vs. load")
axes[1, 0].legend()
axes[1, 0].grid(linestyle="--", alpha=0.5)

# 4. Detailed per-priority P99 at representative load.
priority_labels = ["P0 Interactive", "P1 Standard", "P2 Batch", "P3 Background"]
x = np.arange(len(priority_labels))
width = 0.25
fcfs_p99 = [fcfs["per_priority_p99_ms"][f"p{p}"] for p in range(4)]
npp_p99 = [npp["per_priority_p99_ms"][f"p{p}"] for p in range(4)]
mlfq_p99 = [mlfq["per_priority_p99_ms"][f"p{p}"] for p in range(4)]
axes[1, 1].bar(x - width, fcfs_p99, width, label="FCFS", color="#e74c3c")
axes[1, 1].bar(x, npp_p99, width, label="Priority", color="#f39c12")
axes[1, 1].bar(x + width, mlfq_p99, width, label="InterruptLLM", color="#2ecc71")
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(priority_labels, rotation=15, ha="right")
axes[1, 1].set_ylabel("P99 latency (ms)")
axes[1, 1].set_title(f"Per-priority P99 at load={point['load_factor']:.2f}")
axes[1, 1].legend()
axes[1, 1].grid(axis="y", linestyle="--", alpha=0.5)

fig.tight_layout()
fig.savefig("/kaggle/working/phase4a_evaluation.png", dpi=150)
print(" Saved phase4a_evaluation.png")

# ---------------------------------------------------------------------------
# Save results.
# ---------------------------------------------------------------------------
results = {
    "evaluation_complete": True,
    "capacity_tokens_per_ms": CAPACITY_TOKENS_PER_MS,
    "max_batch_size": MAX_BATCH_SIZE,
    "overhead_ms": OVERHEAD_MS,
    "quantum_ms": QUANTUM_MS,
    "swap_time_ms": SWAP_TIME_MS,
    "token_scale": TOKEN_SCALE,
    "max_rows": MAX_ROWS,
    "num_runs": 20,
    "sweep": sweep,
    "representative": point,
    "improvements": {
        "p0_vs_fcfs": f"{fcfs['per_priority_p99_ms']['p0'] / max(1e-9, mlfq['per_priority_p99_ms']['p0']):.2f}x",
        "p0_vs_priority": f"{npp['per_priority_p99_ms']['p0'] / max(1e-9, mlfq['per_priority_p99_ms']['p0']):.2f}x",
        "throughput_delta_vs_fcfs_pct": f"{((mlfq['throughput_tokens_per_s'] - fcfs['throughput_tokens_per_s']) / fcfs['throughput_tokens_per_s'] * 100):.2f}%",
        "throughput_delta_vs_priority_pct": f"{((mlfq['throughput_tokens_per_s'] - npp['throughput_tokens_per_s']) / npp['throughput_tokens_per_s'] * 100):.2f}%",
    },
}

core.save_results(results, "/kaggle/working/phase4a_results.json")

core.format_result("evaluation_complete", True)
core.format_result("representative_load", f"{point['load_factor']:.2f}")
core.format_result("fcfs_p0_p99_ms", f"{fcfs['per_priority_p99_ms']['p0']:.2f}")
core.format_result("priority_p0_p99_ms", f"{npp['per_priority_p99_ms']['p0']:.2f}")
core.format_result("mlfq_p0_p99_ms", f"{mlfq['per_priority_p99_ms']['p0']:.2f}")
core.format_result("p0_improvement_vs_fcfs", results["improvements"]["p0_vs_fcfs"])
core.format_result("p0_improvement_vs_priority", results["improvements"]["p0_vs_priority"])
core.format_result("fcfs_throughput_tok_s", f"{fcfs['throughput_tokens_per_s']:.0f}")
core.format_result("priority_throughput_tok_s", f"{npp['throughput_tokens_per_s']:.0f}")
core.format_result("mlfq_throughput_tok_s", f"{mlfq['throughput_tokens_per_s']:.0f}")
core.format_result("throughput_delta_vs_fcfs", results["improvements"]["throughput_delta_vs_fcfs_pct"])
core.format_result("mlfq_avg_preemptions", f"{mlfq['avg_preemptions']:.3f}")
core.format_result("mlfq_p0_sla_violation_rate", f"{mlfq['sla_violation_rates']['p0']*100:.2f}%")
core.format_result("mlfq_p1_sla_violation_rate", f"{mlfq['sla_violation_rates']['p1']*100:.2f}%")

print("\nDone.")
