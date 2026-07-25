# 06 — Results and Analysis

> This note guides you through Section VI of the paper: the results tables and figures.

## Section VI overview

| Subsection | Content |
|---|---|
| VI-A | Scheduler comparison at fixed load (ρ=0.76) |
| VI-B | End-to-end evaluation across load factors |
| VI-C | Context-swap latency: analytical and measured |
| VI-D | Ablation and sensitivity |

## VI-A: Scheduler Comparison at ρ=0.76

Table II in the paper compares FCFS, Priority, and InterruptLLM at load factor 0.76.

Key numbers from the paper:

| Metric | FCFS | Priority | InterruptLLM |
|---|---:|---:|---:|
| Overall P99 | 274.7 ± 5.9 ms | 307.2 ± 5.9 ms | 300.9 ± 5.7 ms |
| P0 P99 | 263.4 ± 9.0 ms | 111.7 ± 2.1 ms | **51.4 ± 1.4 ms** |
| P1 P99 | 285.0 ± 5.2 ms | 332.1 ± 8.1 ms | 737.3 ± 5.6 ms |
| Throughput | 228,911 ± 247 tok/s | 228,911 ± 247 tok/s | 228,911 ± 247 tok/s |
| Service-share Jain | 1.00 | 1.00 | 1.00 |
| P1/P0 P99 ratio | 1.08 | 2.97 | 14.3 |
| P0 SLA violation | 6.1% | 0.0% | 0.0% |
| Avg preemptions | 0.00 | 0.00 | 0.20 |

### What the table shows

- **P0 P99 drops from 263 ms to 51 ms:** 5.1× improvement over FCFS.
- **P1 P99 rises to 737 ms:** the trade-off for protecting P0.
- **Throughput is unchanged:** preemption overhead is small.
- **Service-share Jain stays 1.0:** no tenant is starved.
- **P1/P0 ratio rises to 14.3:** intentional priority separation.

> [!important]
> The overall P99 is similar across all three policies, but the *class-level* P99 differs dramatically. This is why class-level P99 matters.

## VI-B: End-to-End Evaluation Across Load Factors

Figure 3 in the paper shows P0 P99 vs. load factor for FCFS, Priority, and InterruptLLM.

Key observations:

- At low load (ρ=0.56), all policies are fast because the GPU is not saturated.
- Around ρ ≈ 0.7, FCFS starts to degrade due to head-of-line blocking.
- At high load (ρ=0.93), InterruptLLM keeps P0 P99 below 60 ms while FCFS reaches 499 ms.
- At overload (ρ=1.11), FCFS reaches 878 ms, Priority stays at 117 ms, InterruptLLM stays at 55 ms.

Key numbers at ρ=0.93:

- FCFS P0 P99: 499.2 ± 3.7 ms
- Priority P0 P99: 116.7 ± 1.5 ms
- InterruptLLM P0 P99: 56.5 ± 1.1 ms
- Throughput loss: 2.2%
- Average preemption overhead: 0.07 ± 0.001 ms

> [!important]
> The crossover at ρ ≈ 0.7 is where preemption becomes clearly beneficial. Below that, there is little blocking.

## VI-C: Context-Swap Latency

Table III and Figure 4 compare measured, analytical, and LZ4-compressed swap latencies.

Measured P100 bandwidth: ~5 GB/s effective.

For 1 GB block:

- Measured (P100 Gen3): 208.0 ms
- Analytical (Gen4): 32.0 ms
- Modeled + LZ4: 69.9 ms

> [!important]
> The measured latency is 6–7× higher than the analytical model. This gap reflects real-world overhead, not just hardware generation.

The 0.5 ms simulator penalty corresponds to a small hot footprint (~2.5 MB), not a full block.

## VI-D: Ablation and Sensitivity

Table IV isolates the contribution of preemption on a synthetic high-load workload.

Key results:

| Policy | P0 P99 | P1 P99 | Throughput | Preemptions |
|---|---:|---:|---:|---:|
| FCFS | 100 ± 33 ms | 114 ± 33 ms | 264,142 | 0.00 |
| Priority | 54.2 ± 4.8 ms | 69.0 ± 5.9 ms | 264,117 | 0.00 |
| SSJF | 57.1 ± 5.8 ms | 96.3 ± 12.0 ms | 264,373 | 0.00 |
| Lottery | 64.7 ± 13.8 ms | 104 ± 31 ms | 264,177 | 0.00 |
| WFQ | 54.2 ± 4.8 ms | 69.0 ± 5.9 ms | 264,117 | 0.00 |
| EDF | 57.1 ± 5.8 ms | 96.3 ± 12.0 ms | 264,373 | 0.00 |
| MLFQ | **27.7 ± 0.5** ms | 62.9 ± 1.3 ms | 255,614 | 0.16 |

### What the ablation shows

- Non-preemptive policies (Priority, SSJF, WFQ, EDF) reduce FCFS latency by ~2×.
- Preemptive MLFQ reduces it further by ~3.6×.
- The extra gain comes entirely from mid-quantum preemption.
- Lottery and WFQ have higher variance because they are probabilistic.

Sensitivity analysis:

- P0 P99 stays below 35 ms for swap penalties up to 2 ms.
- At 10 ms swap penalty, P0 P99 degrades to 61 ms, throughput drops to 121,000 tok/s, P1 violations hit 42.3%.

> [!important]
> The sub-10 ms swap target is validated: above that, the system degrades.

## Connections to background modules

| Result | Module |
|---|---|
| Class-level P99 | [[01-performance-metrics]] |
| Confidence intervals | [[02-confidence-intervals]] |
| Swap latency gap | [[03-measuring-swap-latency]] |
| Ablation | [[03-simulation-and-ablation]] |
| Load factor | [[01-performance-metrics]] |

## Check your understanding

- [ ] I can explain Table II in my own words.
- [ ] I can explain the shape of Figure 3.
- [ ] I understand why the measured swap latency differs from the analytical model.
- [ ] I can explain the ablation conclusion: preemption is the dominant factor.

## Exercises

1. Why is the overall P99 similar across FCFS, Priority, and InterruptLLM in Table II?
2. At what load factor does InterruptLLM start to show clear benefit over FCFS?
3. What does the 6–7× gap between measured and analytical swap latency imply for real systems?
4. How much does non-preemptive priority reduce FCFS latency? How much does preemptive MLFQ reduce it further?

> [!question]
> The P1 P99 increases significantly under InterruptLLM. Is this acceptable? What assumptions does the paper make about P1's tolerance for delay?
