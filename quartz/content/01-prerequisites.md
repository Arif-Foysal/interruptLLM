# Module 01 — Prerequisites

> This module covers the bare minimum you need before studying LLM inference: computer systems basics, Python for research, and math foundations.

## Why this module matters

The InterruptLLM paper touches on GPUs, memory hierarchies, scheduling, and statistics. Without these foundations, the paper will feel like a wall of jargon. This module gives you the vocabulary and tools to read the paper with confidence.

## Notes in this module

1. [[01-computer-systems-basics]] — CPU, RAM, GPU, memory hierarchy, latency vs. throughput
2. [[02-python-for-research]] — Reading CSVs, NumPy, JSON, random seeds
3. [[03-math-foundations]] — Percentiles, mean/std, ratios, log scale, big-O

## Prerequisite self-check

Before moving to Module 2, make sure you can:

- [ ] Explain why HBM is faster than CPU DRAM.
- [ ] Read a CSV and compute an average in Python.
- [ ] Compute P50, P90, and P99 of a small dataset.
- [ ] Interpret $56.5 \pm 1.1$ ms.
- [ ] Explain what $O(n \log n)$ means.

## Time estimate

- 2–3 hours for a beginner
- 1 hour if you already know Python and basic systems

## Next module

After this, go to [[02-llm-fundamentals]] to learn what LLMs are and how they generate tokens.

> [!tip]
> Do not skip this module even if you think you know it. The specific vocabulary (HBM, P99, throughput) is used constantly in the paper.
