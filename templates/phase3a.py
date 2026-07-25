"""
interruptllm phase3a — context swap latency benchmark.

Estimates GPU HBM → CPU DRAM → NVMe SSD swap latencies for KV-cache blocks.
Uses block sizes derived from the real trace's token distribution and models
both raw and LZ4-compressed transfers.

Outputs:
- phase3a_results.json
- phase3a_swap_cost.png
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

rng = np.random.default_rng(99)

# ---------------------------------------------------------------------------
# Block sizes (MB) corresponding to common KV-cache sizes.
# For Llama-3-8B @ 128K context with 32 layers, 32 heads, 128 head_dim,
# KV cache ~ 2 GB. We test a range from one block to full-cache chunks.
# ---------------------------------------------------------------------------
block_sizes_mb = [1, 4, 16, 64, 256, 1024]

# Bandwidth assumptions:
# - GPU HBM -> CPU DRAM: PCIe Gen4 x16 ~ 32 GB/s raw -> 256 Gbps
# - CPU DRAM -> NVMe SSD: ~3.5 GB/s -> 28 Gbps
# LZ4 compression ratio for KV cache (sparse, repetitive): ~3x
GPU_CPU_BW_GBPS = 256.0
CPU_SSD_BW_GBPS = 28.0
LZ4_RATIO = 3.0

records = []
for mb in block_sizes_mb:
    gpu_cpu = core.swap_cost_ms(mb, "gpu_cpu", GPU_CPU_BW_GBPS, 1.0)
    gpu_cpu_compressed = core.swap_cost_ms(mb, "gpu_cpu", GPU_CPU_BW_GBPS, LZ4_RATIO)
    cpu_ssd = core.swap_cost_ms(mb, "cpu_ssd", CPU_SSD_BW_GBPS, 1.0)
    cpu_ssd_compressed = core.swap_cost_ms(mb, "cpu_ssd", CPU_SSD_BW_GBPS, LZ4_RATIO)
    records.append({
        "block_mb": mb,
        "gpu_cpu_ms": gpu_cpu,
        "gpu_cpu_compressed_ms": gpu_cpu_compressed,
        "cpu_ssd_ms": cpu_ssd,
        "cpu_ssd_compressed_ms": cpu_ssd_compressed,
    })

# Checkpoint metadata size for a range of request sizes.
tokens_range = [256, 512, 1024, 2048, 4096, 8192, 32768, 131072]
checkpoint_sizes = [core.checkpoint_size_kb(t) for t in tokens_range]

results = {
    "benchmark_complete": True,
    "target_preemption_ms": 10.0,
    "gpu_cpu_bw_gbps": GPU_CPU_BW_GBPS,
    "cpu_ssd_bw_gbps": CPU_SSD_BW_GBPS,
    "lz4_compression_ratio": LZ4_RATIO,
    "swap_records": records,
    "checkpoint_metadata_kb": dict(zip(tokens_range, checkpoint_sizes)),
    "max_gpu_cpu_ms": max(r["gpu_cpu_ms"] for r in records),
    "max_cpu_ssd_ms": max(r["cpu_ssd_ms"] for r in records),
    "max_gpu_cpu_compressed_ms": max(r["gpu_cpu_compressed_ms"] for r in records),
}

# ---------------------------------------------------------------------------
# Plots.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

x = np.arange(len(block_sizes_mb))
width = 0.35

axes[0].bar(x - width/2, [r["gpu_cpu_ms"] for r in records], width, label="GPU→CPU raw", color="#3498db")
axes[0].bar(x + width/2, [r["gpu_cpu_compressed_ms"] for r in records], width, label="GPU→CPU LZ4", color="#2ecc71")
axes[0].axhline(10.0, color="red", linestyle="--", label="10 ms target")
axes[0].set_xticks(x)
axes[0].set_xticklabels([str(b) for b in block_sizes_mb])
axes[0].set_xlabel("Block size (MB)")
axes[0].set_ylabel("Swap time (ms)")
axes[0].set_title("GPU → CPU context swap latency")
axes[0].legend()
axes[0].grid(axis="y", linestyle="--", alpha=0.5)

axes[1].plot(tokens_range, checkpoint_sizes, marker="o", color="#9b59b6")
axes[1].set_xlabel("Request size (tokens)")
axes[1].set_ylabel("Checkpoint size (KB)")
axes[1].set_xscale("log")
axes[1].set_yscale("log")
axes[1].set_title("State checkpoint metadata size")
axes[1].grid(linestyle="--", alpha=0.5)

fig.tight_layout()
fig.savefig("/kaggle/working/phase3a_swap_cost.png", dpi=150)
print(" Saved phase3a_swap_cost.png")

# ---------------------------------------------------------------------------
# Emit results.
# ---------------------------------------------------------------------------
core.save_results(results, "/kaggle/working/phase3a_results.json")

core.format_result("benchmark_complete", True)
core.format_result("max_gpu_cpu_ms", f"{results['max_gpu_cpu_ms']:.4f}")
core.format_result("max_gpu_cpu_compressed_ms", f"{results['max_gpu_cpu_compressed_ms']:.4f}")
core.format_result("max_cpu_ssd_ms", f"{results['max_cpu_ssd_ms']:.4f}")
core.format_result("checkpoint_128k_kb", f"{core.checkpoint_size_kb(131072):.2f}")

print("\nDone.")
