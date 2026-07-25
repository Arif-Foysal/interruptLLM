# 05 — Evaluation Walkthrough

> This note guides you through Section V of the paper: implementation, simulation assumptions, workload, and metrics.

## Section V structure

| Subsection | Title | What it covers |
|---|---|---|
| V-A | Research Prototype | Kaggle pipeline, core library, notebooks |
| V-B | Discrete-Event Simulator | GPU abstraction, batch model, scheduling quantum |
| V-C | Simulation Assumptions | Parameters, justifications, swap penalty calibration |
| V-D | Workload and Dataset | Kaggle trace, task type mapping |
| V-E | Scheduling Policies | The 7 policies compared |
| V-F | Metrics | P99, throughput, SLA, fairness |

## V-A: Research Prototype

The paper implements InterruptLLM as a Kaggle-driven research prototype.

Key components:

- `interruptllm_core.py`: core library with request model, scheduler policies, and swap cost model.
- `pipeline.py`: CLI to push notebooks to Kaggle, wait for completion, and parse results.
- Notebooks: Kaggle kernels that import the library and run experiments.

> [!important]
> The prototype validates scheduling logic and calibration assumptions; it does not integrate with a production inference engine like vLLM.

## V-B: Discrete-Event Simulator

The simulator models:

- A GPU with a configurable token-generation rate (300 tok/ms)
- A batch of up to 16 requests
- A scheduling quantum (100 ms)
- Capacity allocated equally among batch members

It abstracts away:

- CUDA kernel launch
- CUDA graphs
- Memory allocator overhead
- GPU microarchitecture effects

This abstraction lets the paper isolate scheduler behavior from GPU-level timing.

## V-C: Simulation Assumptions

Table I in the paper lists the parameters:

| Parameter | Value | Justification |
|---|---|---|
| GPU abstraction | 300 tok/ms | Dominates scheduling behavior |
| Batch capacity | 16 requests | vLLM default for 80 GB GPU |
| Scheduling quantum | 100 ms | Balances responsiveness and stability |
| Swap penalty | 0.5 ms | Calibrated vs. measured P100 memcpy |
| Token scaling | 0.2× | Preserves relative sizes, tractable simulation |
| KV block size | 16 tokens | vLLM PagedAttention default |
| CPU DRAM buffer | 320 GB | 4× GPU memory capacity |

> [!important]
> The 0.5 ms swap penalty is the most critical assumption. It is calibrated to the measured P100 effective bandwidth (~5 GB/s) applied to a small hot footprint (~2.5 MB).

## V-D: Workload and Dataset

The dataset is:

- **Source:** Kaggle `bektursyn/llm-inference-logs-and-performance-metrics`
- **Size:** 30,000 records
- **Fields:** timestamp, model, task type, prompt tokens, completion tokens, TTFT, TPOT, total latency, status code

Task type mapping to priority classes:

| Task Type | Priority Class |
|---|---|
| Customer_Support_Chat | P0 |
| Code_Generation | P0 |
| Summarization | P1 |
| Extraction_JSON | P1 |

Token scaling: 0.2×

Reason: keeps CPU simulation tractable while preserving relative request sizes.

Mean scaled request size: ~1,000 tokens.

## V-E: Scheduling Policies

The paper compares 7 policies:

1. **FCFS:** continuous batching, no eviction
2. **Priority:** non-preemptive, reorders admission at 100 ms quanta
3. **SSJF:** shortest remaining tokens first
4. **Lottery:** weighted random selection
5. **WFQ:** proportional capacity share
6. **EDF:** earliest deadline first
7. **InterruptLLM MLFQ:** preemptive MLFQ with block-granular swap

> [!important]
> These policies are carefully chosen to show that preemption, not just priority, is the key improvement.

## V-F: Metrics

The paper reports:

- P99 latency per class
- Throughput (tok/s)
- SLA violation rates
- Average preemption overhead
- Service-share Jain index
- Priority-weighted Jain index
- P1/P0 P99 ratio

SLA targets:

- P0: < 200 ms
- P1: < 1 s

## Connections to background modules

| Concept | Module |
|---|---|
| Discrete-event simulation | [[03-simulation-and-ablation]] |
| GPU memory hierarchy | [[01-gpu-memory-hierarchy]] |
| Swap penalty calibration | [[03-measuring-swap-latency]] |
| Performance metrics | [[01-performance-metrics]] |
| Confidence intervals | [[02-confidence-intervals]] |
| MLFQ | [[03-mlfq-deep-dive]] |

## Check your understanding

- [ ] I can explain the simulator's main abstractions.
- [ ] I know the key simulation parameters and their justifications.
- [ ] I understand the Kaggle dataset and task type mapping.
- [ ] I can list all 7 scheduling policies.
- [ ] I know all the metrics reported.

## Exercises

1. Why does the simulator abstract GPU execution as a token-generation rate?
2. How is the 0.5 ms swap penalty derived?
3. Why are tokens scaled by 0.2×?
4. What is the purpose of comparing 7 policies instead of just 2?

> [!warning]
> The simulator is not the real system. Every result depends on the assumptions. The most important assumption is the 0.5 ms swap penalty, which is calibrated to a real benchmark but not a full end-to-end measurement.
