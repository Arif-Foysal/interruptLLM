# Module 06 — Evaluation Methodology

> This module explains the metrics, confidence intervals, simulation approach, and ablation studies used in the paper.

## Why this module matters

A result like "8.8× improvement" only means something if you understand how it was measured. This module teaches you to read experimental results critically.

## Notes in this module

1. [[01-performance-metrics]] — Latency, P99, throughput, SLA, Jain fairness, load factor
2. [[02-confidence-intervals]] — Mean ± std, standard error, arrival-time jitter, 20 runs
3. [[03-simulation-and-ablation]] — Discrete-event simulation, ablation, threats to validity

## Key takeaways

- P99 latency captures tail behavior.
- Throughput measures tokens per second.
- Mean ± std over 20 runs shows reproducibility.
- Ablation isolates the contribution of preemption.
- Simulation is powerful but depends on assumptions.

## Check your understanding

- [ ] I can compute P50, P90, P99.
- [ ] I can compute the Jain index.
- [ ] I understand why 20 runs with jitter are used.
- [ ] I can explain internal, external, and construct validity.

## Time estimate

- 3–4 hours for a beginner
- 1.5 hours if you already know experimental methodology

## Connections to the paper

These concepts directly support:

- Section V: Implementation and Evaluation Methodology
- Section VI: Results
- Section VII: Discussion and Limitations

## Previous / next

- Previous: [[05-llm-serving-systems]]
- Next: [[07-reading-the-paper]]

> [!tip]
> When reading the paper's tables, return to these notes to remind yourself what each column means.
