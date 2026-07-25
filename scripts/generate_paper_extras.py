"""
Generate extra evaluation results for the InterruptLLM paper.

This script produces:
  1. Ablation study: FCFS, priority, MLFQ without aging, MLFQ with aging.
  2. Sensitivity analysis: swap penalty sweep.
  3. Flash-crowd workload: 100 P0 requests arriving simultaneously.

It uses synthetic workloads because the public Kaggle CSV is not available in
this local checkout. The main phase2/phase4 results in the paper still use the
real Kaggle trace; these extras are supplementary sensitivity/ablation studies.
"""

import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import interruptllm_core as core

# ---------------------------------------------------------------------------
# Synthetic workload generator
# ---------------------------------------------------------------------------

def build_synthetic_workload(
    n_requests: int = 2000,
    inter_arrival_ms: float = 2.0,
    token_scale: float = 0.20,
    random_seed: int = 2026,
    priority_mix: tuple = (0.40, 0.35, 0.15, 0.10),
) -> list:
    """Generate a synthetic workload with a realistic P0/P1/P2/P3 mix.

    Parameters are tuned to yield a load factor near 0.9, comparable to the
    heavy-load operating point in the main trace-based evaluation.
    """
    rng = random.Random(random_seed)
    np_rng = np.random.RandomState(random_seed)
    requests = []
    task_labels = ["Customer_Support_Chat", "Summarization", "Extraction_JSON", "Batch_Embeddings"]
    # Target mean total tokens (before scaling) to hit ~0.9 load factor.
    mean_tokens = [1000, 3200, 2400, 8000]
    std_tokens = [250, 800, 600, 2000]

    for i in range(n_requests):
        priority = np_rng.choice(4, p=priority_mix)
        tokens = max(1, int(rng.gauss(mean_tokens[priority], std_tokens[priority]) * token_scale))
        requests.append({
            "id": i,
            "priority": priority,
            "tokens": tokens,
            "prompt_tokens": int(tokens * 0.25),
            "completion_tokens": int(tokens * 0.75),
            "tenant": task_labels[priority],
            "task_type": task_labels[priority],
            "model": "synthetic",
            "arrival": i * inter_arrival_ms,
            "original_latency_ms": -1.0,
            "preemptions": 0,
            "wait_time": 0.0,
            "swap_time_ms": 0.0,
            "remaining": tokens,
            "completion": None,
            "started": False,
        })
    return requests

# ---------------------------------------------------------------------------
# Common simulation parameters
# ---------------------------------------------------------------------------

CAPACITY = 300.0
MAX_BATCH = 16
OVERHEAD = 0.1
DT = 1.0
QUANTUM = 100.0
SWAP_TIME = 0.5

OUT_DIR = Path(__file__).resolve().parent.parent / "results" / "paper_extras"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Ablation study
# ---------------------------------------------------------------------------

def run_ablation():
    workload = build_synthetic_workload(n_requests=2000, inter_arrival_ms=2.0)
    base_kwargs = {
        "capacity_tokens_per_ms": CAPACITY,
        "max_batch_size": MAX_BATCH,
        "overhead_ms": OVERHEAD,
        "dt_ms": DT,
        "quantum_ms": QUANTUM,
    }

    fcfs = core.simulate_scheduler([dict(r) for r in workload], scheduler="fcfs", **base_kwargs)
    priority = core.simulate_scheduler([dict(r) for r in workload], scheduler="priority", **base_kwargs)
    mlfq_no_aging = core.simulate_scheduler(
        [dict(r) for r in workload],
        scheduler="mlfq",
        swap_time_ms=SWAP_TIME,
        enable_aging=False,
        **base_kwargs,
    )
    mlfq_with_aging = core.simulate_scheduler(
        [dict(r) for r in workload],
        scheduler="mlfq",
        swap_time_ms=SWAP_TIME,
        enable_aging=True,
        **base_kwargs,
    )

    results = {
        "fcfs": fcfs,
        "priority": priority,
        "mlfq_no_aging": mlfq_no_aging,
        "mlfq_with_aging": mlfq_with_aging,
    }

    print("\n=== Ablation study ===")
    for name, m in results.items():
        print(f"  {name:20s}: P0 P99={m['per_priority_p99_ms']['p0']:6.1f}ms  "
              f"P1 P99={m['per_priority_p99_ms']['p1']:6.1f}ms  "
              f"tput={m['throughput_tokens_per_s']:7.0f}  "
              f"Jain={m['jain_fairness']:.3f}  "
              f"preempt={m['avg_preemptions']:.3f}")

    with open(OUT_DIR / "ablation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    return results

# ---------------------------------------------------------------------------
# 2. Sensitivity to swap penalty
# ---------------------------------------------------------------------------

def run_sensitivity():
    workload = build_synthetic_workload(n_requests=2000, inter_arrival_ms=2.0)
    penalties = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    sweep = []
    base_kwargs = {
        "capacity_tokens_per_ms": CAPACITY,
        "max_batch_size": MAX_BATCH,
        "overhead_ms": OVERHEAD,
        "dt_ms": DT,
        "quantum_ms": QUANTUM,
    }
    for penalty in penalties:
        m = core.simulate_scheduler(
            [dict(r) for r in workload],
            scheduler="mlfq",
            swap_time_ms=penalty,
            **base_kwargs,
        )
        sweep.append({
            "swap_penalty_ms": penalty,
            "p0_p99_ms": m["per_priority_p99_ms"]["p0"],
            "p1_p99_ms": m["per_priority_p99_ms"]["p1"],
            "throughput_tok_s": m["throughput_tokens_per_s"],
            "p0_sla_violation_rate": m["sla_violation_rates"]["p0"],
            "p1_sla_violation_rate": m["sla_violation_rates"]["p1"],
            "avg_preemptions": m["avg_preemptions"],
        })

    print("\n=== Sensitivity to swap penalty ===")
    for row in sweep:
        print(f"  swap={row['swap_penalty_ms']:4.1f}ms: P0 P99={row['p0_p99_ms']:6.1f}ms  "
              f"P1 P99={row['p1_p99_ms']:6.1f}ms  "
              f"tput={row['throughput_tok_s']:7.0f}  "
              f"P0 SLA viol={row['p0_sla_violation_rate']*100:5.2f}%")

    with open(OUT_DIR / "sensitivity_results.json", "w") as f:
        json.dump(sweep, f, indent=2, default=str)
    return sweep

# ---------------------------------------------------------------------------
# 3. Victim selection policy ablation
# ---------------------------------------------------------------------------

def run_victim_policy():
    workload = build_synthetic_workload(n_requests=2000, inter_arrival_ms=2.0)
    base_kwargs = {
        "capacity_tokens_per_ms": CAPACITY,
        "max_batch_size": MAX_BATCH,
        "overhead_ms": OVERHEAD,
        "dt_ms": DT,
        "quantum_ms": QUANTUM,
        "swap_time_ms": SWAP_TIME,
    }

    results = {}
    for policy in ["largest", "smallest", "cost_aware"]:
        m = core.simulate_scheduler(
            [dict(r) for r in workload],
            scheduler="mlfq",
            victim_policy=policy,
            **base_kwargs,
        )
        results[policy] = {
            "p0_p99_ms": m["per_priority_p99_ms"]["p0"],
            "p1_p99_ms": m["per_priority_p99_ms"]["p1"],
            "throughput_tok_s": m["throughput_tokens_per_s"],
            "avg_preemptions": m["avg_preemptions"],
            "avg_swap_time_ms": m["avg_swap_time_ms"],
        }

    print("\n=== Victim selection policy ===")
    for name, m in results.items():
        print(f"  {name:20s}: P0 P99={m['p0_p99_ms']:6.1f}ms  "
              f"P1 P99={m['p1_p99_ms']:6.1f}ms  "
              f"tput={m['throughput_tok_s']:7.0f}  "
              f"preempt={m['avg_preemptions']:.3f}")

    with open(OUT_DIR / "victim_policy_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    return results


# ---------------------------------------------------------------------------
# 4. SSJF baseline comparison
# ---------------------------------------------------------------------------

def run_ssjf_comparison():
    workload = build_synthetic_workload(n_requests=2000, inter_arrival_ms=2.0)
    base_kwargs = {
        "capacity_tokens_per_ms": CAPACITY,
        "max_batch_size": MAX_BATCH,
        "overhead_ms": OVERHEAD,
        "dt_ms": DT,
        "quantum_ms": QUANTUM,
    }

    fcfs = core.simulate_scheduler([dict(r) for r in workload], scheduler="fcfs", **base_kwargs)
    ssjf = core.simulate_scheduler([dict(r) for r in workload], scheduler="ssjf", **base_kwargs)
    mlfq = core.simulate_scheduler(
        [dict(r) for r in workload],
        scheduler="mlfq",
        swap_time_ms=SWAP_TIME,
        **base_kwargs,
    )

    results = {
        "fcfs": {
            "p0_p99_ms": fcfs["per_priority_p99_ms"]["p0"],
            "p1_p99_ms": fcfs["per_priority_p99_ms"]["p1"],
            "overall_p99_ms": fcfs["p99_latency_ms"],
            "throughput_tok_s": fcfs["throughput_tokens_per_s"],
        },
        "ssjf": {
            "p0_p99_ms": ssjf["per_priority_p99_ms"]["p0"],
            "p1_p99_ms": ssjf["per_priority_p99_ms"]["p1"],
            "overall_p99_ms": ssjf["p99_latency_ms"],
            "throughput_tok_s": ssjf["throughput_tokens_per_s"],
        },
        "mlfq": {
            "p0_p99_ms": mlfq["per_priority_p99_ms"]["p0"],
            "p1_p99_ms": mlfq["per_priority_p99_ms"]["p1"],
            "overall_p99_ms": mlfq["p99_latency_ms"],
            "throughput_tok_s": mlfq["throughput_tokens_per_s"],
            "avg_preemptions": mlfq["avg_preemptions"],
        },
    }

    print("\n=== SSJF comparison ===")
    for name, m in results.items():
        print(f"  {name:20s}: P0 P99={m['p0_p99_ms']:6.1f}ms  "
              f"P1 P99={m['p1_p99_ms']:6.1f}ms  "
              f"overall P99={m['overall_p99_ms']:6.1f}ms  "
              f"tput={m['throughput_tok_s']:7.0f}")

    with open(OUT_DIR / "ssjf_comparison_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    return results


# ---------------------------------------------------------------------------
# 5. Flash-crowd workload
# ---------------------------------------------------------------------------

def run_flash_crowd():
    workload = core.build_flash_crowd_workload(
        n_total=2100,
        burst_size=100,
        burst_time_ms=0.0,
        burst_inter_arrival_ms=1.0,
        background_inter_arrival_ms=2.0,
        token_scale=0.20,
    )
    base_kwargs = {
        "capacity_tokens_per_ms": CAPACITY,
        "max_batch_size": MAX_BATCH,
        "overhead_ms": OVERHEAD,
        "dt_ms": DT,
        "quantum_ms": QUANTUM,
    }

    fcfs = core.simulate_scheduler([dict(r) for r in workload], scheduler="fcfs", **base_kwargs)
    priority = core.simulate_scheduler([dict(r) for r in workload], scheduler="priority", **base_kwargs)
    mlfq = core.simulate_scheduler(
        [dict(r) for r in workload],
        scheduler="mlfq",
        swap_time_ms=SWAP_TIME,
        **base_kwargs,
    )

    results = {
        "fcfs": {
            "p0_p99_ms": fcfs["per_priority_p99_ms"]["p0"],
            "p1_p99_ms": fcfs["per_priority_p99_ms"]["p1"],
            "p0_sla_violation_rate": fcfs["sla_violation_rates"]["p0"],
            "throughput_tok_s": fcfs["throughput_tokens_per_s"],
        },
        "priority": {
            "p0_p99_ms": priority["per_priority_p99_ms"]["p0"],
            "p1_p99_ms": priority["per_priority_p99_ms"]["p1"],
            "p0_sla_violation_rate": priority["sla_violation_rates"]["p0"],
            "throughput_tok_s": priority["throughput_tokens_per_s"],
        },
        "mlfq": {
            "p0_p99_ms": mlfq["per_priority_p99_ms"]["p0"],
            "p1_p99_ms": mlfq["per_priority_p99_ms"]["p1"],
            "p0_sla_violation_rate": mlfq["sla_violation_rates"]["p0"],
            "throughput_tok_s": mlfq["throughput_tokens_per_s"],
            "avg_preemptions": mlfq["avg_preemptions"],
        },
    }

    print("\n=== Flash-crowd workload ===")
    for name, m in results.items():
        print(f"  {name:20s}: P0 P99={m['p0_p99_ms']:6.1f}ms  "
              f"P0 SLA viol={m['p0_sla_violation_rate']*100:5.2f}%  "
              f"tput={m['throughput_tok_s']:7.0f}")

    with open(OUT_DIR / "flash_crowd_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    return results


if __name__ == "__main__":
    run_ablation()
    run_sensitivity()
    run_victim_policy()
    run_ssjf_comparison()
    run_flash_crowd()
    print(f"\nAll results saved to {OUT_DIR}")
