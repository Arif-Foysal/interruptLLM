# Module 03 — GPU and Memory

> This module explains GPU memory hierarchy, CUDA concepts, and how the paper measures swap latency on a real GPU.

## Why this module matters

InterruptLLM moves data between GPU HBM, CPU DRAM, and NVMe SSD. To understand whether this is feasible, you need to know the bandwidths, latencies, and overheads involved.

## Notes in this module

1. [[01-gpu-memory-hierarchy]] — HBM, CPU DRAM, NVMe SSD, PCIe bandwidths
2. [[02-cuda-and-bandwidth]] — CUDA, host/device, cudaMemcpyAsync, pinned memory, streams
3. [[03-measuring-swap-latency]] — P100 benchmark, measured vs. analytical, 0.5 ms calibration

## Key takeaways

- HBM is fast and small; CPU DRAM is slower and larger; SSD is slowest and largest.
- PCIe bandwidth between GPU and CPU is much lower than HBM bandwidth.
- Measured effective bandwidth (~5 GB/s on P100) is lower than ideal bandwidth.
- The simulator's 0.5 ms penalty is calibrated to a small hot footprint, not a full swap.

## Check your understanding

- [ ] I can rank HBM, CPU DRAM, and SSD by capacity and speed.
- [ ] I know the approximate PCIe Gen3 and Gen4 bandwidths.
- [ ] I understand why `cudaMemcpyAsync` and pinned memory matter.
- [ ] I can derive the 0.5 ms simulator penalty from 2.5 MB at 5 GB/s.

## Time estimate

- 3–4 hours for a beginner
- 1.5 hours if you already know GPUs

## Connections to the paper

These concepts directly support:

- Section IV-C: Hierarchical Context Swapper
- Section VI-C: Context-Swap Latency
- Table III and Figure 4

## Previous / next

- Previous: [[02-llm-fundamentals]]
- Next: [[04-operating-systems-concepts]]

> [!warning]
> Do not confuse HBM bandwidth with PCIe bandwidth. Preemption cost depends on PCIe bandwidth.
