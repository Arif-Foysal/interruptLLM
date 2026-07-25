"""
interruptllm core library.

Uploaded as a Kaggle dataset by `pipeline.py upload-src`. All notebooks
import this module after locating it under /kaggle/input/.

Add project-specific functions below the helpers.
"""

import json
from pathlib import Path

def format_result(key, value, comment=None):
    """Print a greppable [RESULT] line and return the formatted string.

    Notebooks should call this for every metric so `pipeline.py fetch`
    can surface it without parsing free-form stdout.
    """
    line = f"[RESULT] {key} = {value}"
    if comment:
        line += f" # {comment}"
    print(line)
    return line

def save_results(data: dict, path):
    """Write a results dict as JSON. Use /kaggle/working/<phase>_results.json."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f" Saved: {p}")

# ---------------------------------------------------------------------------
# Project-specific code goes below.
# ---------------------------------------------------------------------------

# InterruptLLM: shared simulation utilities.
# These functions are intentionally framework-free (numpy + stdlib) so they run
# on CPU-only Kaggle kernels during early-phase experiments.

import csv
import os
import random
from typing import Dict, List, Tuple, Optional

import numpy as np

# -----------------------------------------------------------------------------
# Request model and trace loading
# -----------------------------------------------------------------------------

def load_llm_trace(csv_path: str, max_rows: Optional[int] = None) -> List[dict]:
    """Load the Kaggle LLM inference logs CSV into a list of request dicts.

    Columns expected:
      Timestamp, Model_Name, Task_Type, Provider, Prompt_Tokens,
      Completion_Tokens, Cache_Hit_Tokens, TTFT_ms, TPOT_ms,
      Total_Latency_ms, Estimated_Cost_USD, Status_Code
    """
    requests = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if max_rows is not None and i >= max_rows:
                break
            try:
                prompt = int(row["Prompt_Tokens"])
                completion = int(row["Completion_Tokens"])
                total_tokens = prompt + completion
                total_latency_ms = float(row["Total_Latency_ms"])
                tpot_ms = float(row["TPOT_ms"])
                ttft_ms = float(row["TTFT_ms"])
            except (ValueError, KeyError):
                continue
            requests.append({
                "timestamp": row.get("Timestamp", ""),
                "model": row.get("Model_Name", "unknown"),
                "task_type": row.get("Task_Type", "unknown"),
                "provider": row.get("Provider", "unknown"),
                "prompt_tokens": prompt,
                "completion_tokens": completion,
                "total_tokens": total_tokens,
                "ttft_ms": ttft_ms,
                "tpot_ms": tpot_ms,
                "total_latency_ms": total_latency_ms,
                "status_code": int(row.get("Status_Code", 200) or 200),
                "row": i,
            })
    return requests


def task_to_priority(task_type: str) -> int:
    """Map Task_Type to InterruptLLM priority class.

    P0 (interactive) < P1 (standard) < P2 (batch) < P3 (background).
    """
    task = str(task_type).lower().strip().replace("_", " ")
    # Interactive / latency-sensitive tasks.
    if any(k in task for k in {"chat", "support", "code", "coding", "qa", "question", "answer", "interactive", "conversational"}):
        return 0
    # Standard API tasks.
    if any(k in task for k in {"summarization", "summarize", "extraction", "extract", "translation", "classify", "classification", "standard"}):
        return 1
    # Batch analytics tasks.
    if any(k in task for k in {"embedding", "rerank", "analysis", "batch", "data"}):
        return 2
    # Default long-running / background tasks.
    return 3


def build_requests_from_trace(
    csv_path: str,
    max_rows: Optional[int] = None,
    token_scale: float = 1.0,
    random_seed: int = 42,
    inter_arrival_ms: float = 50.0,
) -> List[dict]:
    """Convert a CSV trace into InterruptLLM simulation requests."""
    rng = random.Random(random_seed)
    raw = load_llm_trace(csv_path, max_rows=max_rows)
    requests = []
    for i, r in enumerate(raw):
        if r["status_code"] != 200:
            continue
        tokens = max(1, int(r["total_tokens"] * token_scale))
        priority = task_to_priority(r["task_type"])
        arrival = i * inter_arrival_ms  # relative arrival in ms
        requests.append({
            "id": i,
            "priority": priority,
            "tokens": tokens,
            "prompt_tokens": r["prompt_tokens"],
            "completion_tokens": r["completion_tokens"],
            "tenant": r["task_type"],
            "task_type": r["task_type"],
            "model": r["model"],
            "arrival": arrival,  # ms
            "original_latency_ms": r["total_latency_ms"],
            "preemptions": 0,
            "wait_time": 0.0,
            "swap_time_ms": 0.0,
            "remaining": tokens,
            "completion": None,
            "started": False,
        })
    return requests


def build_flash_crowd_workload(
    n_total: int = 1200,
    burst_size: int = 100,
    burst_time_ms: float = 0.0,
    burst_inter_arrival_ms: float = 1.0,
    background_inter_arrival_ms: float = 5.0,
    token_scale: float = 1.0,
    random_seed: int = 42,
) -> List[dict]:
    """Generate a synthetic workload with a P0 flash crowd at the start.

    A burst of `burst_size` P0 interactive requests arrives close together at
    `burst_time_ms`, followed by lower-rate P1 background load. This models a
    sudden spike in interactive chat/code-completion traffic.
    """
    rng = random.Random(random_seed)
    requests = []
    next_id = 0

    # P0 burst.
    for i in range(burst_size):
        tokens = max(1, int(rng.gauss(800, 200) * token_scale))
        requests.append({
            "id": next_id,
            "priority": 0,
            "tokens": tokens,
            "prompt_tokens": int(tokens * 0.25),
            "completion_tokens": int(tokens * 0.75),
            "tenant": "flash_p0",
            "task_type": "Flash_Crowd_P0",
            "model": "synthetic",
            "arrival": burst_time_ms + i * burst_inter_arrival_ms,
            "original_latency_ms": -1.0,
            "preemptions": 0,
            "wait_time": 0.0,
            "swap_time_ms": 0.0,
            "remaining": tokens,
            "completion": None,
            "started": False,
        })
        next_id += 1

    # P1 background load.
    for i in range(n_total - burst_size):
        tokens = max(1, int(rng.gauss(2500, 600) * token_scale))
        requests.append({
            "id": next_id,
            "priority": 1,
            "tokens": tokens,
            "prompt_tokens": int(tokens * 0.2),
            "completion_tokens": int(tokens * 0.8),
            "tenant": "background_p1",
            "task_type": "Background_P1",
            "model": "synthetic",
            "arrival": burst_time_ms + i * background_inter_arrival_ms,
            "original_latency_ms": -1.0,
            "preemptions": 0,
            "wait_time": 0.0,
            "swap_time_ms": 0.0,
            "remaining": tokens,
            "completion": None,
            "started": False,
        })
        next_id += 1

    return requests


def find_dataset_file(name: str, root: str = "/kaggle/input") -> Optional[str]:
    """Walk the Kaggle input mount and return the first CSV matching *name*."""
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if name.lower() in fn.lower() and fn.lower().endswith(".csv"):
                return os.path.join(dirpath, fn)
    return None

# -----------------------------------------------------------------------------
# Capacity-shared discrete-event scheduler simulation
# -----------------------------------------------------------------------------

def _metrics_from_requests(requests: List[dict], scheduler: str = "fcfs") -> dict:
    """Compute aggregate metrics from completed request dicts."""
    completions = [r for r in requests if r["completion"] is not None]
    if not completions:
        return {"error": "no completions"}

    latencies_ms = [r["completion"] - r["arrival"] for r in completions]
    latencies_ms = [max(0, x) for x in latencies_ms]
    arr = np.array(latencies_ms)

    total_tokens = sum(r["tokens"] for r in requests)
    total_time_ms = max(1e-9, max(r["completion"] for r in completions) - min(r["arrival"] for r in completions))

    # SLA targets by priority (ms).
    sla_targets_ms = {0: 200.0, 1: 1000.0, 2: 5000.0, 3: 30000.0}
    sla_violations = {p: 0 for p in range(4)}
    counts = {p: 0 for p in range(4)}
    for r in completions:
        p = r["priority"]
        counts[p] += 1
        if (r["completion"] - r["arrival"]) > sla_targets_ms[p]:
            sla_violations[p] += 1

    # Jain fairness across tenants (task types). Use normalized service share:
    # each tenant's share = (tokens served for tenant) / (tenant's total demand)
    # divided by total time. This measures proportional fairness.
    tenant_demand = {}
    tenant_served = {}
    for r in requests:
        tenant = r["tenant"]
        tenant_demand.setdefault(tenant, 0)
        tenant_demand[tenant] += r["tokens"]
    for r in completions:
        tenant = r["tenant"]
        tenant_served.setdefault(tenant, 0)
        tenant_served[tenant] += r["tokens"]

    shares = []
    for tenant in tenant_demand:
        demand = max(1, tenant_demand[tenant])
        served = tenant_served.get(tenant, 0)
        shares.append(served / demand)
    if shares:
        jain = (sum(shares) ** 2) / (len(shares) * sum(s ** 2 for s in shares))
    else:
        jain = 0.0

    # Also compute priority-weighted fairness: lower priority should not be
    # starved relative to demand. Weighted by 1/(priority+1).
    weighted_shares = []
    for tenant in tenant_demand:
        # Use the first request's priority for this tenant as representative.
        p = next(r["priority"] for r in requests if r["tenant"] == tenant)
        demand = max(1, tenant_demand[tenant])
        served = tenant_served.get(tenant, 0)
        weighted_shares.append(served / demand / (p + 1))
    if weighted_shares:
        weighted_jain = (sum(weighted_shares) ** 2) / (len(weighted_shares) * sum(s ** 2 for s in weighted_shares))
    else:
        weighted_jain = 0.0

    per_priority = {}
    for p in range(4):
        subset = [r["completion"] - r["arrival"] for r in completions if r["priority"] == p]
        per_priority[f"p{p}"] = float(np.percentile(subset, 99)) if subset else 0.0

    return {
        "mean_latency_ms": float(np.mean(arr)),
        "p50_latency_ms": float(np.median(arr)),
        "p99_latency_ms": float(np.percentile(arr, 99)),
        "max_latency_ms": float(np.max(arr)),
        "throughput_tokens_per_s": float(total_tokens / (total_time_ms / 1000.0)),
        "throughput_requests_per_s": float(len(completions) / (total_time_ms / 1000.0)),
        "jain_fairness": float(jain),
        "weighted_jain_fairness": float(weighted_jain),
        "avg_preemptions": float(np.mean([r["preemptions"] for r in requests])),
        "avg_swap_time_ms": float(np.mean([r["swap_time_ms"] for r in requests])),
        "sla_violations": {f"p{p}": sla_violations[p] for p in range(4)},
        "sla_violation_rates": {f"p{p}": (sla_violations[p] / max(1, counts[p])) for p in range(4)},
        "per_priority_p99_ms": per_priority,
        "tenant_service_fraction": {tenant: tenant_served.get(tenant, 0) / max(1, tenant_demand[tenant]) for tenant in tenant_demand},
    }


def _select_batch(queue: List[dict], scheduler: str, max_batch: int, clock_ms: float) -> List[dict]:
    """Select up to max_batch requests to serve at this moment."""
    ready = [r for r in queue if r["arrival"] <= clock_ms and r["remaining"] > 0]
    if not ready:
        return []
    if scheduler == "fcfs":
        return sorted(ready, key=lambda r: r["arrival"])[:max_batch]
    if scheduler == "priority":
        return sorted(ready, key=lambda r: (r["priority"], r["arrival"]))[:max_batch]
    if scheduler == "mlfq":
        # Same as priority but caller handles preemption.
        return sorted(ready, key=lambda r: (r["priority"], r["arrival"]))[:max_batch]
    return ready[:max_batch]


def simulate_scheduler(
    requests: List[dict],
    scheduler: str = "fcfs",
    capacity_tokens_per_ms: float = 200.0,
    max_batch_size: int = 16,
    overhead_ms: float = 0.5,
    swap_time_ms: float = 2.0,
    dt_ms: float = 1.0,
    quantum_ms: float = 0.0,
    max_steps: int = 5_000_000,
    aging_threshold_ms: float = 1000.0,
    enable_aging: bool = True,
    victim_policy: str = "largest",
) -> dict:
    """Discrete-time capacity-shared scheduler simulation.

    scheduler: "fcfs", "priority", "mlfq", or "ssjf"
    capacity_tokens_per_ms: total GPU token generation capacity
    max_batch_size: maximum number of requests in a batch
    overhead_ms: per-iteration scheduling overhead
    swap_time_ms: context swap penalty on preemption (MLFQ only)
    dt_ms: simulation time step
    aging_threshold_ms: boost a waiting request's priority class if it has
                        waited this long without being served (MLFQ only)
    enable_aging: whether to apply priority boosting in MLFQ
    victim_policy: for MLFQ, "largest", "smallest", or "cost_aware"
    """
    for r in requests:
        r["remaining"] = r["tokens"]
        r["completion"] = None
        r["preemptions"] = 0
        r["swap_time_ms"] = 0.0
        r["started"] = False
        r["last_service_ms"] = r["arrival"]
        r["effective_priority"] = r["priority"]

    clock_ms = 0.0
    step = 0
    active: List[dict] = []

    # Pre-compute sorted arrivals.
    arrivals = sorted(requests, key=lambda r: r["arrival"])
    next_arrival_idx = 0
    n = len(requests)

    def _effective_priority(r):
        if scheduler != "mlfq" or not enable_aging:
            return r["priority"]
        # Priority boosting: if a request has waited long, lower its priority number by 1.
        wait = clock_ms - max(r["arrival"], r["last_service_ms"])
        boosted = max(0, r["priority"] - int(wait / aging_threshold_ms))
        return boosted

    def _select(keys):
        ready = [r for r in active if r["arrival"] <= clock_ms and r["remaining"] > 0]
        if not ready:
            return []
        if scheduler == "fcfs":
            return sorted(ready, key=lambda r: r["arrival"])[:max_batch_size]
        if scheduler == "ssjf":
            # Shortest-remaining-job-first: shortest remaining tokens first, then arrival.
            return sorted(ready, key=lambda r: (r["remaining"], r["arrival"]))[:max_batch_size]
        # priority or mlfq: use effective priority, then arrival time.
        return sorted(ready, key=lambda r: (_effective_priority(r), r["arrival"]))[:max_batch_size]

    def _pick_victim(eligible):
        """Select a victim from eligible batch members according to victim_policy."""
        if victim_policy == "largest":
            return max(eligible, key=lambda r: (_effective_priority(r), -r["remaining"]))
        if victim_policy == "smallest":
            return min(eligible, key=lambda r: (_effective_priority(r), r["remaining"]))
        # cost_aware: minimize swap_time per freed token. Since swap_time is a constant
        # per preemption in this model, this reduces to the smallest footprint.
        return min(eligible, key=lambda r: (_effective_priority(r), r["remaining"]))

    while True:
        step += 1
        if step > max_steps:
            break

        # Add newly arrived requests.
        while next_arrival_idx < n and arrivals[next_arrival_idx]["arrival"] <= clock_ms:
            new_req = arrivals[next_arrival_idx]
            new_req["started"] = True
            active.append(new_req)
            next_arrival_idx += 1

        # Remove completed requests.
        active = [r for r in active if r["remaining"] > 0]
        if not active and next_arrival_idx >= n:
            break
        # Select batch to serve.
        batch = _select(active)

        # For MLFQ, apply preemption only if a higher-priority ready request is being
        # excluded from the batch because the batch is full of lower-priority work.
        if scheduler == "mlfq" and batch and len(active) > max_batch_size:
            ready = [r for r in active if r["arrival"] <= clock_ms and r["remaining"] > 0]
            excluded = [r for r in ready if r not in batch]
            if excluded:
                best_excluded = min(excluded, key=lambda r: (_effective_priority(r), r["arrival"]))
                victim = _pick_victim(batch)
                if _effective_priority(best_excluded) < _effective_priority(victim):
                    victim["preemptions"] += 1
                    victim["swap_time_ms"] += swap_time_ms
                    victim["last_service_ms"] = clock_ms
                    clock_ms += swap_time_ms
                    batch = _select(active)

        if not batch:
            # Advance to next arrival.
            if next_arrival_idx < n:
                clock_ms = arrivals[next_arrival_idx]["arrival"]
            else:
                clock_ms += dt_ms
            continue

        # FCFS: run the current batch until all its members complete.
        # Priority/MLFQ: run for one quantum (iteration), then reselect.
        if scheduler == "fcfs":
            quantum_steps = max_steps
        else:
            quantum_steps = max(1, int(quantum_ms / dt_ms)) if quantum_ms else 1

        for _ in range(quantum_steps):
            # For MLFQ, check for higher-priority arrivals during the quantum
            # and preempt immediately if the current batch is holding a lower-priority
            # request while a higher-priority request is ready.
            if scheduler == "mlfq":
                while next_arrival_idx < n and arrivals[next_arrival_idx]["arrival"] <= clock_ms:
                    new_req = arrivals[next_arrival_idx]
                    new_req["started"] = True
                    active.append(new_req)
                    next_arrival_idx += 1
                ready = [r for r in active if r["arrival"] <= clock_ms and r["remaining"] > 0]
                if ready and batch:
                    highest_ready = min(ready, key=lambda r: (_effective_priority(r), r["arrival"]))
                    if highest_ready not in batch:
                        victim = _pick_victim(batch)
                        if _effective_priority(highest_ready) < _effective_priority(victim):
                            victim["preemptions"] += 1
                            victim["swap_time_ms"] += swap_time_ms
                            victim["last_service_ms"] = clock_ms
                            clock_ms += swap_time_ms
                            break  # exit quantum early, reselect next outer iteration

            # Allocate capacity equally among batch members.
            tokens_per_request = capacity_tokens_per_ms * dt_ms / len(batch)
            for r in batch:
                r["remaining"] = max(0, r["remaining"] - tokens_per_request)
                r["last_service_ms"] = clock_ms
                if r["remaining"] <= 0:
                    r["completion"] = clock_ms + dt_ms

            # Remove completed from batch so we don't serve them again this quantum.
            batch = [r for r in batch if r["remaining"] > 0]
            if not batch:
                break

            clock_ms += dt_ms + overhead_ms
            step += 1
            if step > max_steps:
                break

    return _metrics_from_requests(requests, scheduler)


# Backwards-compatible aliases used by early templates.
def simulate_fcfs(requests, **kwargs):
    return simulate_scheduler(requests, scheduler="fcfs", **kwargs)


def simulate_non_preemptive_priority(requests, **kwargs):
    return simulate_scheduler(requests, scheduler="priority", **kwargs)


def simulate_mlfq_preemptive(requests, **kwargs):
    return simulate_scheduler(requests, scheduler="mlfq", **kwargs)

# -----------------------------------------------------------------------------
# Context swap cost model
# -----------------------------------------------------------------------------

def swap_cost_ms(
    block_size_mb: float,
    tier: str = "gpu_cpu",
    bandwidth_gbps: float = 32.0,
    compression_ratio: float = 1.0,
) -> float:
    """Estimate context swap time for a KV-cache block.

    tier: "gpu_cpu" or "cpu_ssd"
    bandwidth_gbps: effective bandwidth in Gbps
    compression_ratio: 1.0 = no compression, >1 = compressed
    """
    bytes_ = block_size_mb * 1e6 / compression_ratio
    seconds = bytes_ * 8 / (bandwidth_gbps * 1e9)
    return seconds * 1000


def checkpoint_size_kb(tokens: int, layers: int = 32, heads: int = 32, head_dim: int = 128, dtype_bytes: int = 2) -> float:
    """Estimate the size of the lightweight state checkpoint (metadata only).

    This is the block-table + metadata, not the KV cache itself.
    """
    # Metadata per token: ~ 16 bytes (position id, mask, sampling state).
    metadata = tokens * 16
    return metadata / 1024.0

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def truncate(arr, n=3):
    """Return a string summary of a list/array for compact logging."""
    if len(arr) <= 2 * n:
        return str(list(arr))
    return f"{list(arr[:n])} ... {list(arr[-n:])} (len={len(arr)})"

