---
title: InterruptLLM Study Curriculum
author: Md Arif Faysal Nayem
affiliation: Department of Computer Science and Engineering, United International University, Bangladesh
email: mnayem201194@bscse.uiu.ac.bd
orcid: 0009-0003-8576-7197
paper_title: "InterruptLLM: A Preemptive Scheduling Framework for Low-Latency Multi-Tenant LLM Inference"
venue: ICCIT 2026 / IEEE Access (proposed)
repository: https://github.com/mdzero591/ICCIT
dataset: bektursyn/llm-inference-logs-and-performance-metrics
---

# InterruptLLM Study Curriculum

> A beginner-friendly, step-by-step path to understand the paper **"InterruptLLM: A Preemptive Scheduling Framework for Low-Latency Multi-Tenant LLM Inference"**.

## About this curriculum

| | |
|---|---|
| **Paper** | InterruptLLM: A Preemptive Scheduling Framework for Low-Latency Multi-Tenant LLM Inference |
| **Author** | Md Arif Faysal Nayem |
| **Affiliation** | Department of Computer Science and Engineering, United International University, Bangladesh |
| **Email** | mnayem201194@bscse.uiu.ac.bd |
| **ORCID** | 0009-0003-8576-7197 |
| **Repository** | https://github.com/mdzero591/ICCIT |
| **Dataset** | Kaggle: `bektursyn/llm-inference-logs-and-performance-metrics` |
| **Intended audience** | Undergraduate CS students, systems beginners, anyone curious about LLM serving |

> [!tip]
> Use the search box and the graph view on the right to explore the curriculum. Click any `[[wiki-link]]` to jump between notes.

## Paper summary

Modern LLM serving systems (vLLM, SGLang, TensorRT-LLM, Triton) use **continuous batching** to keep GPUs busy. This works well for throughput, but it is **non-preemptive**: once a request starts decoding, it cannot be evicted until it finishes. A single long summarization request can therefore block short, latency-sensitive interactive requests for seconds, causing head-of-line blocking and SLA violations in multi-tenant deployments.

**InterruptLLM** adds **decode-stage, block-granular preemption** to LLM inference. It combines:

- A **multi-level feedback queue (MLFQ)** scheduler with four priority classes.
- A **hierarchical context swapper** that moves KV blocks from GPU HBM → CPU DRAM → NVMe SSD.
- A **lightweight checkpoint engine** that saves request metadata so preempted requests can resume.

**Key results** (from a discrete-event simulator and a real NVIDIA P100 swap benchmark):

- **8.8×** reduction in interactive (P0) P99 latency over FCFS.
- **2.1×** reduction in P0 P99 latency over a non-preemptive priority queue.
- **2.2%** throughput loss.
- **0.07 ms** average preemption overhead.
- **Zero** P0 SLA violations at load factor 0.93.

## What this curriculum gives you

By the end of this curriculum, you will be able to:

1. **Explain** what LLM inference is, why it is non-preemptive today, and why that creates latency problems.
2. **Describe** the key components of InterruptLLM: the MLFQ scheduler, context swapper, and checkpoint engine.
3. **Read** the paper section by section and understand every table, figure, and claim.
4. **Evaluate** the paper critically: know what is solid, what is simulated, and what remains future work.
5. **Run** the project's simulator and reproduce the main plots locally.

## Who this is for

- Undergraduate CS students (2nd–4th year)
- Comfortable with basic Python and algebra
- No prior experience with GPU programming, LLM internals, or systems research papers needed
- Curious about machine learning systems, scheduling, and vLLM

## Table of contents

### Foundational modules

1. [[01-prerequisites]] — Computer systems basics, Python for research, and math foundations
   - [[01-computer-systems-basics]]
   - [[02-python-for-research]]
   - [[03-math-foundations]]
2. [[02-llm-fundamentals]] — What LLMs are, how transformers work, autoregressive generation, and the KV cache
   - [[01-what-are-llms]]
   - [[02-transformer-and-attention]]
   - [[03-autoregressive-generation]]
   - [[04-kv-cache-explained]]
3. [[03-gpu-and-memory]] — GPU memory hierarchy, CUDA, bandwidth, and measuring swap latency
   - [[01-gpu-memory-hierarchy]]
   - [[02-cuda-and-bandwidth]]
   - [[03-measuring-swap-latency]]
4. [[04-operating-systems-concepts]] — Scheduling, virtual memory, paging, and MLFQ
   - [[01-scheduling-fundamentals]]
   - [[02-scheduling-algorithms]]
   - [[03-mlfq-deep-dive]]
   - [[04-virtual-memory-and-paging]]

### Applied modules

5. [[05-llm-serving-systems]] — vLLM, PagedAttention, continuous batching, and the priority-inversion problem
   - [[01-vllm-and-pagedattention]]
   - [[02-continuous-batching]]
   - [[03-priority-inversion-problem]]
6. [[06-evaluation-methodology]] — Metrics, confidence intervals, simulation, and ablation studies
   - [[01-performance-metrics]]
   - [[02-confidence-intervals]]
   - [[03-simulation-and-ablation]]

### Paper and hands-on

7. [[07-reading-the-paper]] — Section-by-section guided reading and critical analysis
   - [[01-overview-and-structure]]
   - [[02-problem-and-motivation]]
   - [[03-system-design-deep-dive]]
   - [[04-algorithm-and-complexity]]
   - [[05-evaluation-walkthrough]]
   - [[06-results-and-analysis]]
   - [[07-discussion-and-limitations]]
   - [[08-critical-analysis]]
8. [[08-hands-on]] — Codebase walkthrough, running experiments, and plotting results
   - [[01-codebase-walkthrough]]
   - [[02-running-experiments]]
   - [[03-plotting-and-analysis]]

### Reference

- [[glossary]] — All key terms in alphabetical order
- [[references]] — Papers, videos, articles, and further reading

## How the curriculum is organized

```mermaid
flowchart LR
    A[01 Prerequisites] --> B[02 LLM Fundamentals]
    B --> C[03 GPU & Memory]
    C --> D[04 OS Concepts]
    D --> E[05 LLM Serving Systems]
    E --> F[06 Evaluation Methodology]
    F --> G[07 Reading the Paper]
    G --> H[08 Hands-On]
```

| Module | What you learn | Files |
|---|---|---|
| **01 Prerequisites** | Computer systems basics, Python for research, math foundations | [[01-computer-systems-basics]] \| [[02-python-for-research]] \| [[03-math-foundations]] |
| **02 LLM Fundamentals** | What LLMs are, transformers, autoregressive generation, KV cache | [[01-what-are-llms]] \| [[02-transformer-and-attention]] \| [[03-autoregressive-generation]] \| [[04-kv-cache-explained]] |
| **03 GPU & Memory** | GPU memory hierarchy, CUDA concepts, bandwidth, measuring swap | [[01-gpu-memory-hierarchy]] \| [[02-cuda-and-bandwidth]] \| [[03-measuring-swap-latency]] |
| **04 OS Concepts** | Scheduling, virtual memory, paging, MLFQ | [[01-scheduling-fundamentals]] \| [[02-scheduling-algorithms]] \| [[03-mlfq-deep-dive]] \| [[04-virtual-memory-and-paging]] |
| **05 LLM Serving** | vLLM, PagedAttention, continuous batching, priority inversion | [[01-vllm-and-pagedattention]] \| [[02-continuous-batching]] \| [[03-priority-inversion-problem]] |
| **06 Evaluation** | Metrics, confidence intervals, simulation, ablation | [[01-performance-metrics]] \| [[02-confidence-intervals]] \| [[03-simulation-and-ablation]] |
| **07 The Paper** | Section-by-section guided reading and critique | [[01-overview-and-structure]] \| [[02-problem-and-motivation]] \| [[03-system-design-deep-dive]] \| [[04-algorithm-and-complexity]] \| [[05-evaluation-walkthrough]] \| [[06-results-and-analysis]] \| [[07-discussion-and-limitations]] \| [[08-critical-analysis]] |
| **08 Hands-On** | Code walkthrough, run experiments, plot results | [[01-codebase-walkthrough]] \| [[02-running-experiments]] \| [[03-plotting-and-analysis]] |

## The paper at a glance

| Question | Answer |
|---|---|
| **What problem does it solve?** | LLM serving is non-preemptive; long batch jobs block short interactive requests. |
| **Core idea** | Add preemption at decode iteration boundaries and swap KV blocks to CPU/SSD. |
| **Main result** | 8.8× P99 latency reduction for interactive requests, with 2.2% throughput loss. |
| **Key technique** | MLFQ scheduler + hierarchical KV cache swapper + lightweight checkpoint engine. |
| **Evaluation** | Discrete-event simulator + real P100 GPU swap benchmark + Kaggle inference trace. |

## Week-by-week study plan

### Week 1: Build the foundations

- Read [[01-computer-systems-basics]]
- Read [[02-python-for-research]]
- Read [[03-math-foundations]]
- Read [[01-what-are-llms]]
- Read [[02-transformer-and-attention]]

**Goal:** Be comfortable with memory hierarchy, Python/NumPy, and the transformer architecture.

### Week 2: How LLMs generate and where memory goes

- Read [[03-autoregressive-generation]]
- Read [[04-kv-cache-explained]]
- Read [[01-gpu-memory-hierarchy]]
- Read [[02-cuda-and-bandwidth]]

**Goal:** Understand prefill vs. decode, KV cache size, and GPU memory bandwidth.

### Week 3: Scheduling and memory management

- Read [[01-scheduling-fundamentals]]
- Read [[02-scheduling-algorithms]]
- Read [[03-mlfq-deep-dive]]
- Read [[04-virtual-memory-and-paging]]

**Goal:** Connect OS scheduling and virtual memory to the GPU KV cache problem.

### Week 4: LLM serving and evaluation

- Read [[01-vllm-and-pagedattention]]
- Read [[02-continuous-batching]]
- Read [[03-priority-inversion-problem]]
- Read [[01-performance-metrics]]
- Read [[02-confidence-intervals]]
- Read [[03-simulation-and-ablation]]

**Goal:** Understand how vLLM works, why continuous batching is non-preemptive, and how to read performance metrics.

### Week 5: Read the paper deeply

- Read [[01-overview-and-structure]]
- Read [[02-problem-and-motivation]]
- Read [[03-system-design-deep-dive]]
- Read [[04-algorithm-and-complexity]]
- Read [[05-evaluation-walkthrough]]
- Read [[06-results-and-analysis]]
- Read [[07-discussion-and-limitations]]
- Read [[08-critical-analysis]]

**Goal:** Understand every section of the paper and form your own critique.

### Week 6: Run the code

- Read [[01-codebase-walkthrough]]
- Read [[02-running-experiments]]
- Read [[03-plotting-and-analysis]]
- Run the local multi-run simulation
- Recreate a figure from the paper results

**Goal:** Connect the paper to the codebase and data.

## Prerequisites self-check

Before starting, make sure you can answer these questions:

- [ ] I can write a Python function that reads a CSV file and computes an average.
- [ ] I understand what RAM and CPU are.
- [ ] I know what a percentile is (e.g., P99).
- [ ] I understand what $O(n \log n)$ means at a high level.

If any are unchecked, start with the [[01-prerequisites]] module.

## How to use Obsidian with this curriculum

1. Open the `study_materials/` folder as an Obsidian vault.
2. Start at this file (`00-curriculum-overview.md`).
3. Click `[[wiki-links]]` to move between notes.
4. Use the graph view to see connections between concepts.
5. Tick off the checkboxes in the "Check your understanding" sections.

## Key symbols used in the notes

| Symbol | Meaning |
|---|---|
| > [!important] | A key insight you must remember |
| > [!tip] | A practical tip or study hint |
| > [!warning] | A common misconception to avoid |
| > [!question] | A reflection question |
| `[[link]]` | Link to another note in this vault |
| `$$...$$` | Math equation (Obsidian renders this) |
| ✅ / ⬜ | Exercise or check-off item |

## Navigating the curriculum

Use this map of content (MOC) to jump anywhere:

- **Foundations:** [[01-prerequisites]] → [[02-llm-fundamentals]]
- **Hardware:** [[03-gpu-and-memory]]
- **Systems concepts:** [[04-operating-systems-concepts]]
- **Inference systems:** [[05-llm-serving-systems]]
- **Evaluation:** [[06-evaluation-methodology]]
- **Paper reading:** [[07-reading-the-paper]]
- **Code:** [[08-hands-on]]
- **Reference:** [[glossary]] \| [[references]]

## Check your understanding

- [ ] I can explain the non-preemptive problem in one sentence.
- [ ] I can name the three main components of InterruptLLM.
- [ ] I understand the difference between a simulator and a real-system prototype.
- [ ] I know how to navigate this curriculum using Obsidian links.

> [!question]
> Before moving on, ask yourself: *why do we need a new scheduler for LLM inference? What is wrong with just running requests in arrival order?*
