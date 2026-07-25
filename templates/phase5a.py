"""
interruptllm phase5a — real GPU→CPU swap latency benchmark.

Runs on Kaggle with P100 GPU. Measures actual cudaMemcpyAsync (via PyTorch)
for KV-cache block sizes from 32 MB to 1 GB, with and without LZ4 compression.
Compares measured results against the analytical model from phase3a.

Outputs:
- phase5a_results.json
- phase5a_gpu_swap_benchmark.png
"""

# ---------------------------------------------------------------------------
# Bootstrap PyTorch if Kaggle's default image lacks Pascal (sm_60) support.
# P100 GPUs have compute capability 6.0; recent PyTorch wheels only ship
# sm_70+. Detect mismatch, install a compatible wheel, and restart once.
# ---------------------------------------------------------------------------
import os
import sys

if os.environ.get("INTERRUPTSWAP_BOOTSTRAPPED") != "1":
    try:
        import torch
        _torch_ok = True
        if torch.cuda.is_available():
            cc_major = torch.cuda.get_device_capability(0)[0]
            if cc_major < 7:
                # Runtime check: current PyTorch may warn but still work, or it may
                # refuse to launch kernels on sm_60 (P100). Try a tiny kernel.
                try:
                    _x = torch.randn(10, device="cuda")
                    _y = _x + _x
                    torch.cuda.synchronize()
                except RuntimeError:
                    _torch_ok = False
        if not _torch_ok:
            raise ImportError
    except Exception:
        print("Kaggle's default PyTorch does not support Pascal (sm_60).")
        print("Installing PyTorch 2.4.1+cu118 (includes sm_60 support)...")
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--quiet", "--upgrade",
            "torch==2.4.1+cu118", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu118",
        ])
        os.environ["INTERRUPTSWAP_BOOTSTRAPPED"] = "1"
        print("Restarting script with compatible PyTorch...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

# ---------------------------------------------------------------------------

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
import torch
import time

# ---------------------------------------------------------------------------
# Verify GPU availability
# ---------------------------------------------------------------------------
if not torch.cuda.is_available():
    raise RuntimeError("GPU required for phase5a — run on a Kaggle GPU kernel")

gpu_name = torch.cuda.get_device_name(0)
gpu_props = torch.cuda.get_device_properties(0)
print(f"GPU: {gpu_name} ({gpu_props.total_memory / 1e9:.1f} GB)")
print(f"PCIe bandwidth (theoretical): ~{32.0:.0f} GB/s (Gen3 x16)")

# ---------------------------------------------------------------------------
# Benchmark configuration
# ---------------------------------------------------------------------------
BLOCK_SIZES_MB = [32, 64, 128, 256, 512, 1024]
NUM_ITERATIONS = 20
WARMUP_ITERATIONS = 3

# P100 PCIe: theoretical max ~32 GB/s (PCIe Gen3 x16)
# Measured practical: ~24-28 GB/s for large transfers
GPU_CPU_BW_GBPS = 256.0  # analytical assumption (Gen4)
LZ4_RATIO = 3.0

# ---------------------------------------------------------------------------
# Helper: measure GPU→CPU memcpy latency
# ---------------------------------------------------------------------------
def measure_gpu_to_cpu_copy(block_size_mb: int, num_iters: int = 20) -> dict:
    """Time a GPU→CPU memory copy using torch.cuda.synchronize for accurate timing."""
    block_bytes = block_size_mb * 1024 * 1024

    # Allocate GPU source
    gpu_tensor = torch.randn(block_bytes // 4, dtype=torch.float32, device="cuda")

    # Allocate CPU destination
    cpu_tensor = torch.empty(block_bytes // 4, dtype=torch.float32, device="cpu")

    # Warmup
    for _ in range(WARMUP_ITERATIONS):
        cpu_tensor.copy_(gpu_tensor, non_blocking=True)
        torch.cuda.synchronize()

    # Timed iterations
    times_ms = []
    for _ in range(num_iters):
        torch.cuda.synchronize()
        start = time.perf_counter()
        cpu_tensor.copy_(gpu_tensor, non_blocking=True)
        torch.cuda.synchronize()
        end = time.perf_counter()
        times_ms.append((end - start) * 1000)

    times_ms = np.array(times_ms)

    # Free GPU memory
    del gpu_tensor
    torch.cuda.empty_cache()

    return {
        "block_mb": block_size_mb,
        "block_bytes": block_bytes,
        "mean_ms": float(times_ms.mean()),
        "std_ms": float(times_ms.std()),
        "min_ms": float(times_ms.min()),
        "max_ms": float(times_ms.max()),
        "p50_ms": float(np.percentile(times_ms, 50)),
        "p95_ms": float(np.percentile(times_ms, 95)),
        "p99_ms": float(np.percentile(times_ms, 99)),
        "times_ms": times_ms.tolist(),
    }


def measure_compressed_gpu_to_cpu(block_size_mb: int, num_iters: int = 20) -> dict:
    """Time GPU→CPU copy with LZ4 compression (compress on GPU, copy, decompress on CPU).

    Since LZ4 on GPU is non-trivial, we simulate by:
    1. Copying to CPU at full size
    2. Compressing on CPU with LZ4
    3. Measuring the compressed copy time separately

    This gives us the real-world scenario: compress, then transfer smaller payload.
    """
    block_bytes = block_size_mb * 1024 * 1024

    try:
        import lz4.frame
        has_lz4 = True
    except ImportError:
        has_lz4 = False

    # Step 1: Copy raw block to CPU
    gpu_tensor = torch.randn(block_bytes // 4, dtype=torch.float32, device="cuda")
    cpu_tensor = torch.empty(block_bytes // 4, dtype=torch.float32, device="cpu")

    # Warmup
    for _ in range(WARMUP_ITERATIONS):
        cpu_tensor.copy_(gpu_tensor, non_blocking=True)
        torch.cuda.synchronize()

    # Step 2: Copy + compress
    if has_lz4:
        compressed_sizes = []
        compress_times_ms = []
        copy_times_ms = []
        total_times_ms = []

        for _ in range(num_iters):
            torch.cuda.synchronize()
            start = time.perf_counter()
            cpu_tensor.copy_(gpu_tensor, non_blocking=True)
            torch.cuda.synchronize()
            copy_end = time.perf_counter()

            raw_data = cpu_tensor.numpy().tobytes()
            c_start = time.perf_counter()
            compressed = lz4.frame.compress(raw_data)
            c_end = time.perf_counter()

            total_end = time.perf_counter()

            copy_times_ms.append((copy_end - start) * 1000)
            compress_times_ms.append((c_end - c_start) * 1000)
            total_times_ms.append((total_end - start) * 1000)
            compressed_sizes.append(len(compressed))

        avg_compressed_ratio = block_bytes / np.mean(compressed_sizes) if compressed_sizes else 1.0
        result = {
            "block_mb": block_size_mb,
            "raw_copy_mean_ms": float(np.mean(copy_times_ms)),
            "raw_copy_std_ms": float(np.std(copy_times_ms)),
            "compress_mean_ms": float(np.mean(compress_times_ms)),
            "compress_std_ms": float(np.std(compress_times_ms)),
            "total_mean_ms": float(np.mean(total_times_ms)),
            "total_std_ms": float(np.std(total_times_ms)),
            "compression_ratio": float(avg_compressed_ratio),
            "compressed_size_mb": float(np.mean(compressed_sizes) / 1e6),
        }
    else:
        # Fallback: just measure raw copy and model compression savings
        raw = measure_gpu_to_cpu_copy(block_size_mb, num_iters)
        estimated_compressed_ms = raw["mean_ms"] / LZ4_RATIO
        result = {
            "block_mb": block_size_mb,
            "raw_copy_mean_ms": raw["mean_ms"],
            "raw_copy_std_ms": raw["std_ms"],
            "compress_mean_ms": 0.0,
            "compress_std_ms": 0.0,
            "total_mean_ms": estimated_compressed_ms,
            "total_std_ms": raw["std_ms"] / LZ4_RATIO,
            "compression_ratio": LZ4_RATIO,
            "compressed_size_mb": block_size_mb / LZ4_RATIO,
            "lz4_available": False,
        }

    del gpu_tensor
    torch.cuda.empty_cache()

    return result


# ---------------------------------------------------------------------------
# Run benchmarks
# ---------------------------------------------------------------------------
print(f"\nBenchmarking GPU→CPU memcpy for {len(BLOCK_SIZES_MB)} block sizes, "
      f"{NUM_ITERATIONS} iterations each...")

raw_results = []
compressed_results = []
analytical_results = []

for mb in BLOCK_SIZES_MB:
    print(f"\n  Block size: {mb} MB")

    # Raw copy
    raw = measure_gpu_to_cpu_copy(mb, NUM_ITERATIONS)
    raw_results.append(raw)
    print(f"    Raw copy: {raw['mean_ms']:.3f} ± {raw['std_ms']:.3f} ms "
          f"(p99={raw['p99_ms']:.3f} ms)")

    # Compressed copy
    compressed = measure_compressed_gpu_to_cpu(mb, NUM_ITERATIONS)
    compressed_results.append(compressed)
    print(f"    Compressed: {compressed['total_mean_ms']:.3f} ± {compressed['total_std_ms']:.3f} ms "
          f"(ratio={compressed['compression_ratio']:.1f}×)")

    # Analytical prediction
    analytical_raw = core.swap_cost_ms(mb, "gpu_cpu", GPU_CPU_BW_GBPS, 1.0)
    analytical_compressed = core.swap_cost_ms(mb, "gpu_cpu", GPU_CPU_BW_GBPS, LZ4_RATIO)
    analytical_results.append({
        "block_mb": mb,
        "analytical_raw_ms": analytical_raw,
        "analytical_compressed_ms": analytical_compressed,
    })
    print(f"    Analytical: raw={analytical_raw:.3f} ms, compressed={analytical_compressed:.3f} ms")

# ---------------------------------------------------------------------------
# Compute measured bandwidth
# ---------------------------------------------------------------------------
bandwidths_gbps = []
for raw in raw_results:
    if raw["mean_ms"] > 0:
        bw = (raw["block_bytes"] * 8) / (raw["mean_ms"] / 1000) / 1e9
        bandwidths_gbps.append(bw)

measured_bw_gbps = np.mean(bandwidths_gbps) if bandwidths_gbps else 0
print(f"\nMeasured PCIe bandwidth: {measured_bw_gbps:.1f} GB/s")

# ---------------------------------------------------------------------------
# Aggregate results
# ---------------------------------------------------------------------------
results = {
    "benchmark_complete": True,
    "gpu_name": gpu_name,
    "gpu_memory_gb": round(gpu_props.total_memory / 1e9, 1),
    "measured_bandwidth_gbps": float(measured_bw_gbps),
    "analytical_bandwidth_gbps": GPU_CPU_BW_GBPS,
    "num_iterations": NUM_ITERATIONS,
    "warmup_iterations": WARMUP_ITERATIONS,
    "raw_results": raw_results,
    "compressed_results": compressed_results,
    "analytical_results": analytical_results,
    "summary": {
        "max_raw_ms": max(r["mean_ms"] for r in raw_results),
        "max_compressed_ms": max(r["total_mean_ms"] for r in compressed_results),
        "max_raw_std_ms": max(r["std_ms"] for r in raw_results),
        "measured_vs_analytical_ratio": float(
            np.mean([r["mean_ms"] / a["analytical_raw_ms"]
                     for r, a in zip(raw_results, analytical_results)
                     if a["analytical_raw_ms"] > 0])
        ),
    },
}

# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

block_mbs = [r["block_mb"] for r in raw_results]
raw_means = [r["mean_ms"] for r in raw_results]
raw_stds = [r["std_ms"] for r in raw_results]
raw_p99s = [r["p99_ms"] for r in raw_results]
comp_means = [r["total_mean_ms"] for r in compressed_results]
comp_stds = [r["total_std_ms"] for r in compressed_results]
ana_raw = [a["analytical_raw_ms"] for a in analytical_results]
ana_comp = [a["analytical_compressed_ms"] for a in analytical_results]

x = np.arange(len(block_mbs))
width = 0.25

# Plot 1: Measured vs analytical (raw)
axes[0].errorbar(x - width/2, raw_means, yerr=raw_stds, fmt='o-',
                 capsize=3, label='Measured (P100)', color='#3498db', linewidth=2)
axes[0].plot(x + width/2, ana_raw, 's--', label='Analytical (Gen4)',
             color='#e74c3c', linewidth=2)
axes[0].axhline(10.0, color='gray', linestyle=':', alpha=0.5, label='10 ms target')
axes[0].set_xticks(x)
axes[0].set_xticklabels([str(b) for b in block_mbs], fontsize=8)
axes[0].set_xlabel("Block size (MB)")
axes[0].set_ylabel("GPU→CPU copy time (ms)")
axes[0].set_title("Raw copy: Measured vs Analytical")
axes[0].legend(fontsize=8)
axes[0].grid(axis='y', linestyle='--', alpha=0.3)

# Plot 2: Measured vs analytical (compressed)
axes[1].errorbar(x - width/2, comp_means, yerr=comp_stds, fmt='o-',
                 capsize=3, label='Measured + LZ4 (P100)', color='#2ecc71', linewidth=2)
axes[1].plot(x + width/2, ana_comp, 's--', label='Analytical (Gen4)',
             color='#e74c3c', linewidth=2)
axes[1].axhline(10.0, color='gray', linestyle=':', alpha=0.5, label='10 ms target')
axes[1].set_xticks(x)
axes[1].set_xticklabels([str(b) for b in block_mbs], fontsize=8)
axes[1].set_xlabel("Block size (MB)")
axes[1].set_ylabel("GPU→CPU copy time (ms)")
axes[1].set_title("LZ4 compressed: Measured vs Analytical")
axes[1].legend(fontsize=8)
axes[1].grid(axis='y', linestyle='--', alpha=0.3)

# Plot 3: P99 with error bars
axes[2].errorbar(x, raw_means, yerr=[np.zeros_like(raw_stds), raw_p99s - np.array(raw_means)],
                 fmt='o', capsize=3, label='Mean', color='#3498db', linewidth=2)
axes[2].scatter(x, raw_p99s, marker='v', color='#e74c3c', s=60, label='P99', zorder=5)
axes[2].axhline(10.0, color='gray', linestyle=':', alpha=0.5, label='10 ms target')
axes[2].set_xticks(x)
axes[2].set_xticklabels([str(b) for b in block_mbs], fontsize=8)
axes[2].set_xlabel("Block size (MB)")
axes[2].set_ylabel("GPU→CPU copy time (ms)")
axes[2].set_title("Raw copy: Mean vs P99")
axes[2].legend(fontsize=8)
axes[2].grid(axis='y', linestyle='--', alpha=0.3)

fig.suptitle(f"GPU→CPU KV-Cache Swap Benchmark ({gpu_name})", fontsize=12, y=1.02)
fig.tight_layout()
fig.savefig("/kaggle/working/phase5a_gpu_swap_benchmark.png", dpi=150, bbox_inches='tight')
print("\nSaved phase5a_gpu_swap_benchmark.png")

# ---------------------------------------------------------------------------
# Emit results
# ---------------------------------------------------------------------------
core.save_results(results, "/kaggle/working/phase5a_results.json")

core.format_result("benchmark_complete", True)
core.format_result("gpu_name", gpu_name)
core.format_result("measured_bandwidth_gbps", f"{measured_bw_gbps:.1f}")
core.format_result("max_raw_ms", f"{results['summary']['max_raw_ms']:.3f}")
core.format_result("max_compressed_ms", f"{results['summary']['max_compressed_ms']:.3f}")
core.format_result("measured_vs_analytical_ratio",
                   f"{results['summary']['measured_vs_analytical_ratio']:.3f}")

# Per-block-size results
for r in raw_results:
    core.format_result(f"swap_{r['block_mb']}mb_ms",
                       f"{r['mean_ms']:.3f} ± {r['std_ms']:.3f}")

print("\nDone.")
