"""
interruptllm phase1a — smoke test.

Validates the full pipeline: core dataset mounts, [RESULT] lines are
emitted, JSON results are saved. Replace the body with a real experiment
once the pipeline is verified.

Outputs to /kaggle/working/:
- phase1a_results.json
"""

import os
import sys

# Locate the core library inside Kaggle's input mount. Mount paths vary,
# so walk to find it rather than hardcoding.
def _find_core(name):
    for dirpath, _, filenames in os.walk("/kaggle/input"):
        if f"{name}.py" in filenames:
            return dirpath
    return None

_core_path = _find_core("interruptllm_core")
if _core_path is None:
    print("ERROR: interruptllm_core.py not found under /kaggle/input/")
    for dirpath, _, filenames in os.walk("/kaggle/input"):
        for f in filenames:
            print("  ", os.path.join(dirpath, f))
    raise ImportError("interruptllm_core.py not found")
sys.path.insert(0, _core_path)

import interruptllm_core as core

# ---------------------------------------------------------------------------
# Smoke-test experiment: replace with the real thing.
# ---------------------------------------------------------------------------

print("=" * 60)
print("PHASE 1A: smoke test")
print("=" * 60)

import numpy as np
rng = np.random.default_rng(42)
x = rng.standard_normal(1000)

# InterruptLLM-specific smoke: exercise the core helper functions.
req = core.mlfg_request(priority=2, tokens=512, tenant="tenant-a", arrival=0.0)
victim = core.select_victim([req], preemptor_priority=0)
latency = core.estimate_latency(prompt_len=256, history_avg=1.5e-3)

results = {
    "experiment_complete": True,
    "n_samples": int(x.size),
    "mean": float(x.mean()),
    "std": float(x.std()),
    "sample_request": req,
    "select_victim_ok": victim is not None or req["priority"] <= 0,
    "estimated_latency_ms": float(latency * 1000),
}

core.format_result("experiment_complete", results["experiment_complete"])
core.format_result("n_samples", results["n_samples"])
core.format_result("mean", f"{results['mean']:.4f}")
core.format_result("std", f"{results['std']:.4f}")
core.format_result("select_victim_ok", results["select_victim_ok"])
core.format_result("estimated_latency_ms", f"{results['estimated_latency_ms']:.4f}")

core.save_results(results, "/kaggle/working/phase1a_results.json")

print("\nDone.")
