# Module 04 — Operating Systems Concepts

> This module covers scheduling algorithms, virtual memory, and paging. These OS concepts are the direct analogy for what InterruptLLM does on a GPU.

## Why this module matters

InterruptLLM is essentially an operating system scheduler for LLM inference requests. The MLFQ scheduler, victim selection, and block-table swapping all borrow ideas from OS design.

## Notes in this module

1. [[01-scheduling-fundamentals]] — Cooperative vs. preemptive scheduling, context switching
2. [[02-scheduling-algorithms]] — FCFS, Priority, SSJF, Lottery, WFQ, EDF
3. [[03-mlfq-deep-dive]] — Multi-level feedback queues, aging, victim selection
4. [[04-virtual-memory-and-paging]] — Virtual memory, page tables, paging, OS → GPU analogy

## Key takeaways

- Preemptive scheduling lets urgent tasks interrupt long ones.
- MLFQ combines priority, round-robin, and aging.
- Virtual memory uses page tables to map non-contiguous physical frames.
- vLLM's block tables are the GPU analog of OS page tables.

## Check your understanding

- [ ] I can explain cooperative vs. preemptive scheduling.
- [ ] I can describe each baseline scheduling algorithm.
- [ ] I understand MLFQ: queues, aging, victim selection.
- [ ] I can map OS paging concepts to PagedAttention.

## Time estimate

- 4–6 hours for a beginner
- 2 hours if you already know OS scheduling

## Connections to the paper

These concepts directly support:

- Section II-C: Why Existing Schedulers Cannot Preempt
- Section IV-C/D/E: MLFQ, Swapper, Checkpoint Engine, Algorithm 1
- Section VI-E: Ablation baselines

## Previous / next

- Previous: [[03-gpu-and-memory]]
- Next: [[05-llm-serving-systems]]

> [!tip]
> If you are taking or have taken an OS course, this module will feel familiar. The key is translating those concepts to the LLM serving domain.
